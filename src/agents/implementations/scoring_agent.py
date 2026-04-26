from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal

class ScoringAgent(BaseAgent):
    """Evaluates the overall health and confidence score of the KB."""
    
    def __init__(self):
        super().__init__(name="ScoringAgent")

    def analyze(self, data: dict) -> list[AuditSignal]:
        # Stub logic returns a score instead of signals
        return []
