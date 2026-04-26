from core.logger import logger
from domain.entities.audit_signal import AuditSignal
from remediation.strategies import AutoFixStrategy, SuggestionStrategy, EscalationStrategy

class RemediationEngine:
    """Decides and executes the best corrective action for a signal."""
    
    def __init__(self):
        self.strategies = {
            "auto-fix": AutoFixStrategy(),
            "suggest": SuggestionStrategy(),
            "escalate": EscalationStrategy()
        }

    def process_signal(self, signal: AuditSignal):
        logger.info(f"Processing signal: {signal.signal_type} - Severity: {signal.severity}")
        
        # Determine strategy based on severity (stub logic)
        action_type = "suggest"
        if signal.severity == "low":
            action_type = "auto-fix"
        elif signal.severity == "critical":
            action_type = "escalate"
            
        strategy = self.strategies.get(action_type)
        if strategy:
            strategy.execute(signal)
