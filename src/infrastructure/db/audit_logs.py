import sqlite3
import json
from typing import Dict, Any, List
from datetime import datetime
import uuid
from core.logger import logger

class AuditLogsDB:
    """Persistent SQLite-backed audit log for real-time monitoring."""

    def __init__(self, db_path: str = "data/audit_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    query TEXT,
                    response TEXT,
                    user_id TEXT,
                    agents_triggered TEXT,
                    signals_count INTEGER DEFAULT 0,
                    confidence_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_log(self, query: str, response: str, user_id: str,
                agents_triggered: List[str], confidence_score: float,
                signals_count: int = 0) -> Dict[str, Any]:
        log_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO audit_logs
                   (id, query, response, user_id, agents_triggered, signals_count, confidence_score, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (log_id, query, response, user_id,
                 json.dumps(agents_triggered), signals_count, confidence_score, timestamp)
            )
        logger.info(f"Audit log stored: {log_id}")
        return {"id": log_id, "query": query, "timestamp": timestamp,
                "signals_count": signals_count, "confidence_score": confidence_score}

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        logs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT id, query, response, user_id, agents_triggered,
                          signals_count, confidence_score, timestamp
                   FROM audit_logs ORDER BY timestamp DESC LIMIT ?""",
                (limit,)
            )
            for row in cursor.fetchall():
                logs.append({
                    "id": row[0], "query": row[1], "response": row[2],
                    "user_id": row[3],
                    "agents_triggered": json.loads(row[4]) if row[4] else [],
                    "signals_count": row[5], "confidence_score": row[6],
                    "timestamp": row[7]
                })
        return logs

    def get_stats(self) -> Dict[str, Any]:
        """Returns aggregate stats for the manager dashboard."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
            total_signals = conn.execute(
                "SELECT COALESCE(SUM(signals_count), 0) FROM audit_logs"
            ).fetchone()[0]
            avg_conf = conn.execute(
                "SELECT COALESCE(AVG(confidence_score), 0) FROM audit_logs"
            ).fetchone()[0]
        return {"total_queries": total, "total_signals": int(total_signals),
                "avg_confidence": round(avg_conf, 2)}
