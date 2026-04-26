from core.logger import logger
from agents.implementations.supervisor_agent import SupervisorAgent

class AuditPipeline:
    """Main pipeline for running the audit workflow."""
    
    def __init__(self, supervisor: SupervisorAgent):
        self.supervisor = supervisor

    def run(self, query: str, context: dict):
        logger.info(f"Starting audit pipeline for query: {query[:30]}...")
        
        data = {"query": query, "context": context}
        signals = self.supervisor.analyze(data)
        
        logger.info(f"Pipeline completed. Generated {len(signals)} signals.")
        return signals
