from abc import ABC, abstractmethod
from typing import Dict, Any

class ILLMInterface(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        pass

    @abstractmethod
    def evaluate_json(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Returns structured JSON response"""
        pass
