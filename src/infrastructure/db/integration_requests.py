import uuid
from typing import Dict, Any, List
from datetime import datetime

_requests: Dict[str, Any] = {}

class IntegrationRequestDB:
    @staticmethod
    def create_request(project_path: str, kb_path: str, vector_db: str, app_type: str, confidence_score: float) -> str:
        req_id = str(uuid.uuid4())
        _requests[req_id] = {
            "request_id": req_id,
            "project_path": project_path,
            "kb_path": kb_path,
            "vector_db": vector_db,
            "app_type": app_type,
            "confidence_score": confidence_score,
            "status": "PENDING",
            "timestamp": datetime.utcnow().isoformat()
        }
        return req_id

    @staticmethod
    def get_request(req_id: str):
        return _requests.get(req_id)
        
    @staticmethod
    def list_requests() -> List[Dict[str, Any]]:
        return list(_requests.values())
        
    @staticmethod
    def update_status(req_id: str, status: str):
        if req_id in _requests:
            _requests[req_id]["status"] = status
            return True
        return False
