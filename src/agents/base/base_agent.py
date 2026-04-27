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

    def analyze_with_reflection(self, current_prompt: str, system_prompt: str, llm_client, max_retries: int = 3) -> dict:
        """
        Executes a do-while reflection loop for any agent.
        Evaluates JSON, checks 'confidence_score', and retries if the score is low.
        """
        attempt = 0
        best_result = None
        highest_score = 0
        
        while True:
            # --- DO BLOCK ---
            result = llm_client.evaluate_json(
                current_prompt, 
                system_prompt=system_prompt
            )
            
            score = result.get("confidence_score", 0) 
            
            if score > highest_score:
                highest_score = score
                best_result = result
            
            # 1. Break if perfect score achieved
            if score >= 9:
                logger.info(f"{self.name} - Perfect score achieved ({score}/10) on attempt {attempt + 1}")
                return result 
                
            attempt += 1
            
            # --- WHILE (Check) BLOCK ---
            # 2. Break if max retries reached
            if attempt >= max_retries:
                break
                
            # If we get here, it means score < 9 AND attempt < max_retries, so we loop again
            logger.warning(f"{self.name} - Low score ({score}/10) on attempt {attempt}. Retrying...")
            current_prompt += f"\n\n[SYSTEM FEEDBACK]: Your previous attempt scored {score}/10. Explanation given: '{result.get('explanation', result.get('gap_description', 'None'))}'. Please reflect deeper, fix the errors, and try again to achieve a higher confidence score."
            
        logger.warning(f"{self.name} - Max retries reached. Returning best attempt with score {highest_score}/10.")
        return best_result or {}
