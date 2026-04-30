from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal
from core.logger import logger
from core.settings import settings
from infrastructure.memory.episodic_store import EpisodicStore
from infrastructure.memory.semantic_store import SemanticStore

class SupervisorAgent(BaseAgent):
    """
    Orchestrates all specialized agents with:
    - Concurrent execution (ThreadPoolExecutor)
    - Per-agent hard timeout (AGENT_TIMEOUT_SECONDS)
    - Memory integration (EpisodicStore + SemanticStore)
    - Adaptive planning (PlannerAgent)
    - LIGHT_MODE fast path (skips memory/planner overhead)
    """

    def __init__(self, agents: list, planner=None):
        super().__init__(name="SupervisorAgent")
        self.agents = agents
        self.planner = planner
        # Memory stores — only instantiated once; skipped in light mode
        if not settings.LIGHT_MODE:
            self.episodic = EpisodicStore()
            self.semantic  = SemanticStore()
        else:
            self.episodic = None
            self.semantic  = None

    # ── Planning ────────────────────────────────────────────────────────────
    def _get_execution_plan(self, data: dict) -> dict:
        """Ask PlannerAgent for the execution plan, or run all if no planner."""
        if self.planner and not settings.LIGHT_MODE:
            return self.planner.analyze(data)
        return {agent.__class__.__name__: {"run": True, "priority": "high"}
                for agent in self.agents}

    # ── Single-agent runner (called inside thread) ───────────────────────────
    def _run_agent(self, agent: BaseAgent, data: dict) -> list:
        """Runs one agent and returns its signals. Any exception is swallowed."""
        try:
            return agent.analyze(data)
        except Exception as exc:
            logger.error(f"{agent.__class__.__name__} raised an exception: {exc}")
            return []

    # ── Main orchestration ───────────────────────────────────────────────────
    def analyze(self, data: dict) -> list[AuditSignal]:
        mode_tag = "[LIGHT]" if settings.LIGHT_MODE else "[FULL]"
        logger.info(f"Supervisor {mode_tag} starting analysis cycle.")

        plan = self._get_execution_plan(data)
        agents_to_run = [
            a for a in self.agents
            if plan.get(a.__class__.__name__, {}).get("run", True)
        ]

        skipped = len(self.agents) - len(agents_to_run)
        if skipped:
            logger.info(f"Planner skipped {skipped} agent(s).")

        all_signals: list[AuditSignal] = []
        timeout = settings.AGENT_TIMEOUT_SECONDS

        # ── Run agents concurrently ────────────────────────────────────────
        with ThreadPoolExecutor(max_workers=len(agents_to_run) or 1) as executor:
            future_to_agent = {
                executor.submit(self._run_agent, agent, data): agent
                for agent in agents_to_run
            }

            for future in as_completed(future_to_agent, timeout=None):
                agent = future_to_agent[future]
                agent_name = agent.__class__.__name__
                try:
                    # Hard per-agent deadline
                    signals = future.result(timeout=timeout)
                    logger.info(f"{agent_name} returned {len(signals)} signal(s).")
                    all_signals.extend(signals)

                    # ── Memory writes (skipped in LIGHT_MODE) ──────────────
                    if not settings.LIGHT_MODE and self.episodic and self.semantic:
                        for signal in signals:
                            doc_id = str(
                                signal.metadata.get("source", {})
                                       .get("source", signal.id)
                            )
                            self.episodic.save_event(doc_id, signal.signal_type,
                                                     signal.description)
                            self.semantic.save_pattern(
                                f"{signal.signal_type}:{signal.source_agent}"
                            )

                except FuturesTimeoutError:
                    logger.warning(
                        f"{agent_name} exceeded timeout of {timeout}s — skipped."
                    )
                except Exception as exc:
                    logger.error(f"{agent_name} future raised: {exc}")

        # ── Chronic issue escalation (FULL mode only) ──────────────────────
        if not settings.LIGHT_MODE:
            self._flag_chronic_issues(all_signals)

        logger.info(f"Supervisor completed. Total signals: {len(all_signals)}")
        return all_signals

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _flag_chronic_issues(self, signals: list):
        """Escalates severity to 'critical' for documents flagged 3+ times."""
        if not self.episodic:
            return
        for signal in signals:
            doc_id = str(
                signal.metadata.get("source", {}).get("source", signal.id)
            )
            history = self.episodic.get_history(doc_id)
            if len(history) >= 3:
                logger.warning(
                    f"CHRONIC ISSUE: doc='{doc_id}' flagged {len(history)} times."
                    " Escalating to critical."
                )
                signal.severity = "critical"

