import sqlite3
import json
from core.logger import logger
from domain.entities.version import Version
from typing import Dict, List, Optional

class VersionRegistry:
    """Manages document versions and rollbacks via persistent SQLite storage."""
    
    def __init__(self, db_path: str = "data/versions.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS versions (
                    version_id TEXT PRIMARY KEY,
                    article_id TEXT,
                    is_active INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    content TEXT
                )
            ''')

    def register_version(self, version: Version):
        """Adds a new version to the article's history."""
        logger.info(f"Registering version: {version.version_id} for article: {version.article_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            # Deactivate previous versions
            conn.execute(
                "UPDATE versions SET is_active = 0 WHERE article_id = ?",
                (version.article_id,)
            )
            # Insert new active version
            # (Assuming Version has 'content' or we serialize it if needed. 
            # If not, we just save what we need. For this mock we store empty content if not present)
            content = getattr(version, 'content', '') 
            conn.execute(
                "INSERT INTO versions (version_id, article_id, is_active, content) VALUES (?, ?, 1, ?)",
                (version.version_id, version.article_id, content)
            )

    def get_latest_version(self, article_id: str) -> Optional[Version]:
        """Returns the most recent active version of an article."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT version_id, article_id, is_active FROM versions WHERE article_id = ? AND is_active = 1",
                (article_id,)
            )
            row = cursor.fetchone()
            if row:
                v = Version(version_id=row[0], article_id=row[1])
                v.is_active = bool(row[2])
                return v
        return None

    def rollback(self, article_id: str) -> Optional[Version]:
        """
        Reverts to the previous version and returns it.
        The current version is deactivated, previous is activated.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT version_id FROM versions WHERE article_id = ? ORDER BY created_at DESC LIMIT 2",
                (article_id,)
            )
            rows = cursor.fetchall()
            if len(rows) < 2:
                logger.warning(f"No previous version to rollback to for article: {article_id}")
                return None
                
            current_version_id = rows[0][0]
            previous_version_id = rows[1][0]
            
            logger.warning(f"Rolling back from {current_version_id} to {previous_version_id} for article: {article_id}")
            
            # Deactivate current
            conn.execute("UPDATE versions SET is_active = 0 WHERE version_id = ?", (current_version_id,))
            # Activate previous
            conn.execute("UPDATE versions SET is_active = 1 WHERE version_id = ?", (previous_version_id,))
            
            return self.get_latest_version(article_id)

    def handle_version_mismatch(self, article_id: str):
        """
        Flow for Dislike (VERSION_MISMATCH):
        Check last update -> Rollback -> Re-run retrieval (stubbed)
        """
        logger.info(f"Handling VERSION_MISMATCH for article: {article_id}")
        latest = self.get_latest_version(article_id)
        if latest:
            logger.info(f"Last update for {article_id}: {latest.version_id}")
            rolled_back = self.rollback(article_id)
            if rolled_back:
                logger.info("Rollback successful. Triggering re-run retrieval...")
                return rolled_back
        return None
