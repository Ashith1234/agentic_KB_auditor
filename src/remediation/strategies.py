from abc import ABC, abstractmethod
from core.logger import logger
from domain.entities.audit_signal import AuditSignal

class BaseStrategy(ABC):
    @abstractmethod
    def execute(self, signal: AuditSignal):
        pass

class AutoFixStrategy(BaseStrategy):
    def execute(self, signal: AuditSignal):
        logger.info(f"Auto-fixing issue: {signal.description}")
        # Update KB automatically

class SuggestionStrategy(BaseStrategy):
    def execute(self, signal: AuditSignal):
        logger.info(f"Creating suggestion for issue: {signal.description}")
        # Create a PR or dashboard notification

class EscalationStrategy(BaseStrategy):
    def execute(self, signal: AuditSignal):
        logger.warning(f"Escalating critical issue to human review: {signal.description}")
        # Add to HITL queue
