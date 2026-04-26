from typing import List, Any
from core.logger import logger

class Normalizer:
    """Normalizes document metadata and structure."""
    
    def normalize(self, documents: List[Any]) -> List[Any]:
        logger.info("Normalizing documents...")
        for doc in documents:
            # Ensure metadata has standard fields
            if 'source' not in doc.metadata:
                doc.metadata['source'] = 'unknown'
        return documents
