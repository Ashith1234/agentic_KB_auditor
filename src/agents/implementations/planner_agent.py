from typing import List, Dict, Any
from agents.base.base_agent import BaseAgent
from core.logger import logger
from infrastructure.llm.openai_client import OpenAIClient

class PlannerAgent(BaseAgent):
    """Decides which agents to run, priority, and frequency."""
    
    def __init__(self):
        super().__init__(name="PlannerAgent")
        self.llm = OpenAIClient()

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the incoming query and context to decide an execution plan.
        Returns a dict indicating which agents to activate and their priorities.
        """
        query = data.get("query", "")
        context_chunks = data.get("chunks", [])
        
        logger.info(f"PlannerAgent evaluating query: {query[:50]}")
        
        # In a real scenario, LLM decides this. Here we use a heuristic simulation.
        # But we'll try to structure it dynamically.
        plan = {
            "VersionAgent": {"run": True, "priority": "high"},
            "DuplicateAgent": {"run": False, "priority": "low"},
            "CoverageAgent": {"run": True, "priority": "medium"}
        }
        
        # Example logic: if query suggests looking for conflicts
        if "conflict" in query.lower() or "different" in query.lower():
            plan["DuplicateAgent"] = {"run": True, "priority": "high"}
            
        logger.info(f"Generated execution plan: {plan}")
        return plan
