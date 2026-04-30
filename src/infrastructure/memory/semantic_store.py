import sqlite3
import json
from typing import List, Dict, Any
from core.logger import logger

class SemanticStore:
    """Stores learned patterns across the entire KB system."""
    
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT UNIQUE,
                    frequency INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_pattern(self, pattern: str) -> None:
        """Saves a learned pattern or increments its frequency if it exists."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert or update frequency
            conn.execute('''
                INSERT INTO semantic_memory (pattern, frequency) 
                VALUES (?, 1)
                ON CONFLICT(pattern) DO UPDATE SET frequency = frequency + 1, timestamp = CURRENT_TIMESTAMP
            ''', (pattern,))
        logger.info(f"Saved/Updated semantic pattern: {pattern}")

    def get_patterns(self) -> List[Dict[str, Any]]:
        """Retrieves all semantic patterns ordered by frequency."""
        patterns = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT pattern, frequency, timestamp FROM semantic_memory ORDER BY frequency DESC"
            )
            for row in cursor.fetchall():
                patterns.append({
                    "pattern": row[0],
                    "frequency": row[1],
                    "timestamp": row[2]
                })
        return patterns
