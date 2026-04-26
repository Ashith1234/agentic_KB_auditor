from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal
from core.logger import logger

class SupervisorAgent(BaseAgent):
    """Monitors all agents and aggregates their signals."""
    
    def __init__(self, agents: list):
        super().__init__(name="SupervisorAgent")
        self.agents = agents

    def analyze(self, data: dict) -> list[AuditSignal]:
        logger.info("Supervisor starting analysis cycle.")
        all_signals = []
        for agent in self.agents:
            signals = agent.analyze(data)
            all_signals.extend(signals)
        return all_signals
