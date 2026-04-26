from core.logger import logger
from infrastructure.db.version_registry import VersionRegistry

def run_version_agent():
    logger.info("Running version_agent...")

def run_retrieval_agent():
    logger.info("Running retrieval_agent...")

def handle_feedback_trigger(feedback_reason: str):
    if feedback_reason == "OUTDATED" or feedback_reason == "VERSION_MISMATCH":
        run_version_agent()
    elif feedback_reason == "WRONG":
        run_retrieval_agent()
