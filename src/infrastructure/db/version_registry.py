from core.logger import logger
from domain.entities.version import Version
from typing import Dict, List, Optional

class VersionRegistry:
    """Manages document versions and rollbacks."""
    
    def __init__(self):
        # Maps article_id -> List of Version objects (ordered by creation)
        self._history: Dict[str, List[Version]] = {} 
    
    def register_version(self, version: Version):
        """Adds a new version to the article's history."""
        logger.info(f"Registering version: {version.version_id} for article: {version.article_id}")
        
        if version.article_id not in self._history:
            self._history[version.article_id] = []
            
        # Deactivate previous versions
        for v in self._history[version.article_id]:
            v.is_active = False
            
        self._history[version.article_id].append(version)
        
    def get_latest_version(self, article_id: str) -> Optional[Version]:
        """Returns the most recent version of an article."""
        history = self._history.get(article_id, [])
        return history[-1] if history else None

    def rollback(self, article_id: str) -> Optional[Version]:
        """
        Reverts to the previous version and returns it.
        The current version is removed from history.
        """
        history = self._history.get(article_id, [])
        if len(history) < 2:
            logger.warning(f"No previous version to rollback to for article: {article_id}")
            return None
            
        # Remove current active version
        removed_version = history.pop()
        logger.warning(f"Rolling back from {removed_version.version_id} for article: {article_id}")
        
        # Activate the new latest version
        new_latest = history[-1]
        new_latest.is_active = True
        
        return new_latest

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
                # trigger re-run retrieval stub
                return rolled_back
        return None
