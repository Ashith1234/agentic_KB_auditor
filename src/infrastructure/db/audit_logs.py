from typing import Dict, Any, List
from datetime import datetime
import uuid

_audit_logs: List[Dict[str, Any]] = []

class AuditLogsDB:
    @staticmethod
    def add_log(query: str, response: str, user_id: str, agents_triggered: List[str], confidence_score: float):
        log_entry = {
            "id": str(uuid.uuid4()),
            "query": query,
            "response": response,
            "user_id": user_id,
            "agents_triggered": agents_triggered,
            "confidence_score": confidence_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        _audit_logs.append(log_entry)
        return log_entry

    @staticmethod
    def get_logs():
        return _audit_logs
