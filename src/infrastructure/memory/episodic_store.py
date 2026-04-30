import sqlite3
import json
from typing import List, Dict, Any
from core.logger import logger

class EpisodicStore:
    """Stores past audit events to detect repeating failures."""
    
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT,
                    issue TEXT,
                    result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_event(self, doc_id: str, issue: str, result: str) -> None:
        """Saves a single episodic memory event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO episodic_memory (doc_id, issue, result) VALUES (?, ?, ?)",
                (doc_id, issue, result)
            )
        logger.info(f"Saved episodic memory for doc_id: {doc_id}")

    def get_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """Retrieves history of events for a given document."""
        history = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT issue, result, timestamp FROM episodic_memory WHERE doc_id = ? ORDER BY timestamp DESC", 
                (doc_id,)
            )
            for row in cursor.fetchall():
                history.append({
                    "issue": row[0],
                    "result": row[1],
                    "timestamp": row[2]
                })
        return history
