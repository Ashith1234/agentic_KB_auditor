from typing import List, Any
from core.logger import logger

class KBExplorer:
    """
    Search interface for the Knowledge Base.
    """
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def search(self, query: str, k: int = 4) -> List[Any]:
        """
        Performs a semantic search in the KB.
        """
        logger.info(f"Searching for: '{query}' (k={k})")
        if not self.vector_store:
            logger.error("Vector store not initialized.")
            return []
            
        results = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} relevant chunks.")
        return results
