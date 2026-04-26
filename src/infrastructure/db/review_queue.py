from typing import List, Any
from core.logger import logger

class ReviewQueue:
    """Manages tasks that require human-in-the-loop approval."""
    
    def __init__(self):
        self.queue = []
        
    def add_item(self, item: Any):
        logger.info("Adding item to Review Queue")
        self.queue.append(item)
        
    def get_pending(self) -> List[Any]:
        return [item for item in self.queue if item.get("status") == "pending"]

