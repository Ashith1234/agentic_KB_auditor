from typing import Dict, Any, List
from datetime import datetime
import uuid

_feedbacks: List[Dict[str, Any]] = []

class FeedbackDB:
    @staticmethod
    def add_feedback(query: str, response: str, user_id: str, f_type: str, reason: str, confidence: float):
        feedback = {
            "id": str(uuid.uuid4()),
            "query": query,
            "response": response,
            "user_id": user_id,
            "type": f_type,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        _feedbacks.append(feedback)
        return feedback
        
    @staticmethod
    def get_feedbacks():
        return _feedbacks
