import sqlite3
import json
from typing import List, Dict, Any
from datetime import datetime
import uuid
from core.logger import logger

class ReviewQueue:
    """Persistent SQLite-backed approval queue for human-in-the-loop control."""

    def __init__(self, db_path: str = "data/review_queue.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS review_queue (
                    id TEXT PRIMARY KEY,
                    item_type TEXT,
                    payload TEXT,
                    reasoning TEXT,
                    status TEXT DEFAULT 'pending',
                    submitted_by TEXT,
                    reviewed_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at DATETIME
                )
            ''')

    def add_item(self, item_type: str, payload: dict, reasoning: str,
                 submitted_by: str = "system") -> str:
        item_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO review_queue (id, item_type, payload, reasoning, submitted_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (item_id, item_type, json.dumps(payload), reasoning, submitted_by)
            )
        logger.info(f"Added item {item_id} to review queue ({item_type})")
        return item_id

    def get_pending(self) -> List[Dict[str, Any]]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, item_type, payload, reasoning, submitted_by, created_at FROM review_queue WHERE status = 'pending' ORDER BY created_at DESC"
            )
            for row in cursor.fetchall():
                items.append({
                    "id": row[0], "item_type": row[1],
                    "payload": json.loads(row[2]) if row[2] else {},
                    "reasoning": row[3], "submitted_by": row[4],
                    "created_at": row[5], "status": "pending"
                })
        return items

    def get_all(self) -> List[Dict[str, Any]]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, item_type, payload, reasoning, status, submitted_by, reviewed_by, created_at, reviewed_at FROM review_queue ORDER BY created_at DESC"
            )
            for row in cursor.fetchall():
                items.append({
                    "id": row[0], "item_type": row[1],
                    "payload": json.loads(row[2]) if row[2] else {},
                    "reasoning": row[3], "status": row[4],
                    "submitted_by": row[5], "reviewed_by": row[6],
                    "created_at": row[7], "reviewed_at": row[8]
                })
        return items

    def approve(self, item_id: str, reviewed_by: str = "manager") -> bool:
        return self._update_status(item_id, "approved", reviewed_by)

    def reject(self, item_id: str, reviewed_by: str = "manager") -> bool:
        return self._update_status(item_id, "rejected", reviewed_by)

    def _update_status(self, item_id: str, status: str, reviewed_by: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "UPDATE review_queue SET status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?",
                (status, reviewed_by, datetime.utcnow().isoformat(), item_id)
            )
        logger.info(f"Review queue item {item_id} marked as {status} by {reviewed_by}")
        return result.rowcount > 0

