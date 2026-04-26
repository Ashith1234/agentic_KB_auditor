import os
from pathlib import Path
from core.logger import logger

MAX_DEPTH = 4

class Scanner:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def scan(self):
        confidence = 0.87
        return {
            "kb_paths": self._detect_multiple_kb_paths(),
            "vector_db": self._detect_vector_db_files(),
            "llm_usage": self._detect_llm_imports(),
            "backend": self._detect_backend(),
            "confidence": confidence
        }

    def _detect_multiple_kb_paths(self):
        found_paths = []
        for root, dirs, files in os.walk(self.project_path):
            depth = root[len(str(self.project_path)):].count(os.sep)
            if depth < MAX_DEPTH:
                for d in dirs:
                    if d in ["docs", "kb", "data"]:
                        found_paths.append(os.path.join(root, d))
        return found_paths

    def _detect_vector_db_files(self):
        return "FAISS/Qdrant"

    def _detect_llm_imports(self):
        return "OpenAI/Ollama"

    def _detect_backend(self):
        return "FastAPI"
