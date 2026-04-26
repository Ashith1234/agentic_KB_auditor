from typing import Dict, Any, List
import uuid

_sessions: Dict[str, Dict[str, Any]] = {}

class SessionManager:
    @staticmethod
    def create_session(user_id: str) -> str:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "user": user_id,
            "queries": [],
            "feedback": []
        }
        return session_id
        
    @staticmethod
    def get_session(session_id: str):
        return _sessions.get(session_id)
        
    @staticmethod
    def add_query(session_id: str, query: str):
        if session_id in _sessions:
            _sessions[session_id]["queries"].append(query)
            
    @staticmethod
    def add_feedback(session_id: str, feedback_id: str):
        if session_id in _sessions:
            _sessions[session_id]["feedback"].append(feedback_id)
