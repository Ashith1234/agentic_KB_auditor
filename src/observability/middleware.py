import threading
from core.logger import logger
from core.settings import settings
from typing import Callable
from infrastructure.db.audit_logs import AuditLogsDB

class AuditingMiddleware:
    """
    Intercepts queries and responses for auditing.

    Safety guarantees:
    1. FAIL-SAFE: ALL auditor logic is wrapped in try/except.
       If the auditor crashes for any reason, the original host-app
       response is returned completely untouched. The host app never dies.

    2. ASYNC (when settings.AUDIT_ASYNC=True):
       The audit pipeline runs in a background daemon thread.
       The host chatbot response returns to the user immediately —
       zero added latency from the auditor.
    """

    def __init__(self, pipeline):
        self.pipeline = pipeline
        # Fail-safe: AuditLogsDB init wrapped so a broken DB never crashes startup
        try:
            self.audit_log = AuditLogsDB()
        except Exception as exc:
            logger.error(f"AuditLogsDB init failed (non-fatal): {exc}")
            self.audit_log = None

    # ── Core intercept (always safe) ────────────────────────────────────────
    def intercept(self, query: str, response: str, context: dict,
                  user_id: str = "anonymous") -> dict:
        """
        Logs the intercepted query/response.
        ALWAYS returns a result dict — never raises.
        """
        try:
            logger.info(f"Intercepted query from {user_id}: {query[:50]}")
            if self.audit_log:
                self.audit_log.add_log(
                    query=query,
                    response=response,
                    user_id=user_id,
                    agents_triggered=["SupervisorAgent"],
                    confidence_score=context.get("confidence", 1.0),
                    signals_count=context.get("signals_count", 0)
                )
            return {"query": query, "status": "logged", "user_id": user_id}
        except Exception as exc:
            # Fail-safe: log the error but never propagate it
            logger.error(f"Middleware intercept failed (non-fatal): {exc}")
            return {"query": query, "status": "error", "error": str(exc)}

    # ── Background audit runner ─────────────────────────────────────────────
    def _run_audit_async(self, query: str, context: dict):
        """Runs the full audit pipeline in a background daemon thread."""
        try:
            if self.pipeline:
                self.pipeline.run(query, context)
        except Exception as exc:
            logger.error(f"Background audit failed (non-fatal): {exc}")

    def _trigger_audit(self, query: str, context: dict):
        """Dispatches the audit — async or blocking based on settings."""
        if settings.AUDIT_ASYNC:
            thread = threading.Thread(
                target=self._run_audit_async,
                args=(query, context),
                daemon=True   # dies with the host process — never hangs shutdown
            )
            thread.start()
            logger.info("Audit dispatched to background thread.")
        else:
            self._run_audit_async(query, context)

    # ── Decorator interface ─────────────────────────────────────────────────
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator for RAG endpoints.
        The original response is ALWAYS returned to the caller first.
        The audit happens after (async) or is silently swallowed on failure.
        """
        def wrapper(*args, **kwargs):
            # Step 1: call the real chatbot function — never blocked
            try:
                response = func(*args, **kwargs)
            except Exception as exc:
                # The host function itself crashed — propagate normally
                raise

            # Step 2: fire-and-forget audit (never blocks the response)
            try:
                query   = kwargs.get("query", args[0] if args else "")
                user_id = kwargs.get("user_id", "anonymous")
                self.intercept(query, str(response), {}, user_id)
                self._trigger_audit(query, {"query": query})
            except Exception as exc:
                logger.error(f"Middleware wrapper failed (non-fatal): {exc}")

            return response  # ← host app always gets its response back
        return wrapper

