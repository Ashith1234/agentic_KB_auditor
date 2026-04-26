from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}

class FeedbackRequest(BaseModel):
    query: str
    response: str
    user_id: str
    type: str
    reason: str
    confidence: float

@router.post("/audit")
def trigger_audit(request: QueryRequest):
    # Stub: Trigger pipeline
    return {"status": "audit_triggered", "query": request.query}

@router.get("/signals")
def get_signals():
    # Stub: Return active audit signals
    return {"signals": []}

@router.post("/ask")
def ask_question(request: QueryRequest):
    return {"response": "Response from Ask Endpoint"}

@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    return {"status": "feedback_received", "reason": feedback.reason}

@router.get("/metrics")
def get_metrics():
    return {"status": "metrics_stub"}

@router.post("/rollback")
def trigger_rollback(article_id: str):
    return {"status": "rollback_triggered", "article": article_id}

@router.get("/integration-requests")
def get_integration_requests():
    return {"status": "ok", "requests": []}
