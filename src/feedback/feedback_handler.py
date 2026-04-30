from infrastructure.db.feedback_db import FeedbackDB
from core.logger import logger
from agents.trigger import handle_feedback_trigger
from agents.meta.prompt_optimizer import PromptOptimizer

# Maps feedback reason -> the agent most responsible
REASON_TO_AGENT = {
    "OUTDATED": "VersionAgent",
    "VERSION_MISMATCH": "VersionAgent",
    "WRONG": "DuplicateAgent",
    "MISMATCH": "CoverageAgent",
}

class FeedbackHandler:
    def __init__(self):
        self.db = FeedbackDB()
        self.optimizer = PromptOptimizer()

    def handle_feedback(self, query: str, response: str, f_type: str, reason: str, confidence: float = 1.0):
        """
        Stores feedback and triggers adaptive self-improvement if feedback is negative.
        """
        self.db.add_feedback(query, response, f_type, reason, confidence)
        logger.info(f"Feedback received: {f_type} - {reason}")

        if f_type == "BAD":
            self.on_dislike(reason)

    def on_dislike(self, reason: str):
        """
        On bad feedback:
        1. Triggers the appropriate agent to re-run (existing behaviour).
        2. Calls PromptOptimizer to improve that agent's system prompt.
        """
        logger.info(f"Processing dislike reason: {reason}")
        handle_feedback_trigger(reason)

        # Self-improvement: update the responsible agent's prompt
        responsible_agent = REASON_TO_AGENT.get(reason)
        if responsible_agent:
            self.optimizer.track_outcome(
                agent_name=responsible_agent,
                outcome="REJECTED",
                feedback=f"User marked response as bad due to: {reason}"
            )
            logger.info(f"PromptOptimizer updated {responsible_agent} based on feedback reason: {reason}")
