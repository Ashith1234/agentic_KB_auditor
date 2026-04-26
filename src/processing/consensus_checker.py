from typing import List, Dict, Any
from core.logger import logger
from infrastructure.llm.openai_client import OpenAIClient

class ConsensusChecker:
    """Checks for consensus across multiple sources to validate facts."""
    
    def __init__(self):
        self.llm = OpenAIClient()

    def check_consensus(self, fact: str, sources: List[str]) -> Dict[str, Any]:
        """
        Uses LLM to determine if a fact is supported by the majority of sources.
        """
        logger.info(f"Checking consensus for fact: {fact[:50]}...")
        
        sources_text = "\n---\n".join([f"Source {i+1}: {s}" for i, s in enumerate(sources)])
        
        system_prompt = "You are a factual verification agent. Compare a 'Proposed Fact' against multiple 'Sources'."
        user_prompt = f"""
        Proposed Fact: {fact}
        
        Sources:
        {sources_text}
        
        Determine if there is a consensus among the sources regarding the proposed fact.
        Return JSON with:
        - "has_consensus": boolean
        - "confidence": float (0.0 to 1.0)
        - "reasoning": string explanation
        """
        
        result = self.llm.evaluate_json(user_prompt, system_prompt=system_prompt)
        return result

