from core.logger import logger
from typing import Callable, Any

class AuditingMiddleware:
    """Intercepts queries and responses for auditing."""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def intercept(self, query: str, response: str, context: dict) -> dict:
        logger.info(f"Intercepted query: {query[:30]}")
        # Capture data for observability and trigger pipeline asynchronously
        # self.pipeline.run(query, context)
        return {"query": query, "status": "logged"}

    def __call__(self, func: Callable) -> Callable:
        """Decorator for RAG endpoints."""
        def wrapper(*args, **kwargs):
            query = kwargs.get('query', args[0] if args else "")
            response = func(*args, **kwargs)
            # Log and trigger async audit
            self.intercept(query, str(response), {})
            return response
        return wrapper
