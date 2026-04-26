from core.logger import logger

class HealthScorer:
    """Calculates the overall health score of the Knowledge Base."""
    
    def __init__(self):
        self.base_score = 100.0

    def calculate_score(self, issues_count: int, total_docs: int) -> float:
        if total_docs == 0:
            return 0.0
        
        penalty = (issues_count / total_docs) * 100
        score = max(0.0, self.base_score - penalty)
        logger.info(f"Calculated KB Health Score: {score}")
        return score
