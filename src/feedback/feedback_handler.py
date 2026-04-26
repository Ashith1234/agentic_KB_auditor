from infrastructure.db.feedback_db import FeedbackDB
from core.logger import logger
from agents.trigger import handle_feedback_trigger

class FeedbackHandler:
    @staticmethod
    def handle_feedback(query: str, response: str, user_id: str, f_type: str, reason: str, confidence: float):
        FeedbackDB.add_feedback(query, response, user_id, f_type, reason, confidence)
        logger.info(f"Feedback received: {f_type} - {reason}")
        
        if f_type == "BAD":
            FeedbackHandler.on_dislike(reason)

    @staticmethod
    def on_dislike(reason: str):
        logger.info(f"Processing dislike reason: {reason}")
        handle_feedback_trigger(reason)
