import sys
from loguru import logger
import os

def setup_logger(log_level="INFO", log_format="json"):
    """
    Configures Loguru for structured logging.
    """
    logger.remove()
    
    # Standard output handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )

    # File handler for audit logs
    log_file = os.path.join("data", "logs", "system.log")
    logger.add(
        log_file,
        rotation="10 MB",
        retention="10 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )

    return logger

# Initialize default logger
setup_logger()
