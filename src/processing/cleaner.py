import re
from typing import List, Any
from core.logger import logger

class Cleaner:
    """Cleans document content (removes extra whitespace, bad chars)."""
    
    def clean(self, documents: List[Any]) -> List[Any]:
        logger.info("Cleaning documents...")
        for doc in documents:
            # Example cleaning: remove multiple spaces
            doc.page_content = re.sub(r'\s+', ' ', doc.page_content).strip()
        return documents
