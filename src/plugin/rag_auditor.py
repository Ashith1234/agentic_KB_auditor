from core.logger import logger
from observability.middleware import AuditingMiddleware

TRACKED_ROUTES = ["/chat", "/ask", "/query"]

class RAGAuditorPlugin:
    """Plugin wrapper to integrate the auditor into existing RAG apps."""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.middleware = AuditingMiddleware(pipeline)

    def get_middleware(self):
        return self.middleware

    def intercept_request(self, request, route: str):
        if route in TRACKED_ROUTES:
            user_id = request.headers.get("X-User-ID", "anonymous")
            logger.info(f"Intercepted request from {user_id} on {route}")
            return {
                "status": "intercepted",
                "message": "Check Worker Dashboard"
            }
        return None
