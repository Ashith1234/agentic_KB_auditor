from abc import ABC, abstractmethod
from typing import Any, Dict
from core.logger import logger

class BaseAgent(ABC):
    """Base class for all auditing agents."""
    
    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initializing Agent: {self.name}")

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Any:
        """Analyzes the given data and returns audit signals."""
        pass
