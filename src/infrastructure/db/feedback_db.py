import sqlite3
from typing import Dict, Any, List
from datetime import datetime
import uuid
from core.logger import logger

class FeedbackDB:
    """Persistent storage for worker/human feedback."""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    query TEXT,
                    response TEXT,
                    feedback_type TEXT,
                    reason TEXT,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_feedback(self, query: str, response: str, f_type: str, reason: str, confidence: float = 1.0) -> Dict[str, Any]:
        """
        Stores user feedback (LIKE/DISLIKE) and reason (OUTDATED/WRONG/MISMATCH).
        """
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO feedback (id, query, response, feedback_type, reason, confidence, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (feedback_id, query, response, f_type, reason, confidence, timestamp)
            )
            
        logger.info(f"Feedback stored: {f_type} - {reason}")
        
        return {
            "id": feedback_id,
            "query": query,
            "response": response,
            "feedback_type": f_type,
            "reason": reason,
            "confidence": confidence,
            "timestamp": timestamp
        }

    def get_feedbacks(self) -> List[Dict[str, Any]]:
        feedbacks = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, query, response, feedback_type, reason, confidence, timestamp FROM feedback")
            for row in cursor.fetchall():
                feedbacks.append({
                    "id": row[0],
                    "query": row[1],
                    "response": row[2],
                    "feedback_type": row[3],
                    "reason": row[4],
                    "confidence": row[5],
                    "timestamp": row[6]
                })
        return feedbacks
