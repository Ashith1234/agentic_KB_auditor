import os
from pathlib import Path

class ProjectDetector:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def detect_all(self):
        return {
            "kb_paths": self._detect_kb_folders(),
            "vector_db": self._detect_vector_db(),
            "llm_usage": self._detect_llm(),
            "backend": self._detect_backend()
        }
        
    def _detect_kb_folders(self):
        folders = ["docs", "kb", "data"]
        found = []
        for f in folders:
            if (self.project_path / f).is_dir():
                found.append(f)
        return found
        
    def _detect_vector_db(self):
        return "FAISS/Qdrant"
        
    def _detect_llm(self):
        return "OpenAI/Ollama"
        
    def _detect_backend(self):
        return "FastAPI/Flask"
