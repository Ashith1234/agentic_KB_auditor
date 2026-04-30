import os
from pathlib import Path
from core.logger import logger

MIDDLEWARE_IMPORT = "from observability.middleware import AuditingMiddleware"
MIDDLEWARE_INJECTION = "\n# --- Injected by RAG Auditor ---\n_auditor_middleware = AuditingMiddleware(pipeline=None)\napp.add_middleware(type(_auditor_middleware), pipeline=None)\n# --- End Injection ---\n"

FASTAPI_ENTRYPOINTS = ["main.py", "app.py", "server.py", "api.py"]

class MiddlewareInjector:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def _find_entrypoint(self) -> Path | None:
        """Scans for the most likely FastAPI/Flask entrypoint file."""
        for name in FASTAPI_ENTRYPOINTS:
            candidate = self.project_path / name
            if candidate.exists():
                return candidate
            # Check one level deeper (e.g. src/main.py)
            for child in self.project_path.iterdir():
                if child.is_dir():
                    deeper = child / name
                    if deeper.exists():
                        return deeper
        return None

    def inject(self) -> bool:
        """
        Finds the entrypoint and injects middleware if not already present.
        Returns True if injection was successful, False otherwise.
        """
        target = self._find_entrypoint()
        if not target:
            logger.error("Could not find a FastAPI/Flask entrypoint to inject middleware into.")
            return False

        content = target.read_text()

        # Guard: don't inject twice
        if MIDDLEWARE_IMPORT in content:
            logger.info(f"Middleware already injected in {target}. Skipping.")
            return True

        # Add import at the top (after existing imports block)
        lines = content.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1

        lines.insert(insert_at, MIDDLEWARE_IMPORT + "\n")
        lines.append(MIDDLEWARE_INJECTION)

        target.write_text("".join(lines))
        logger.info(f"✅ Middleware successfully injected into: {target}")
        return True
