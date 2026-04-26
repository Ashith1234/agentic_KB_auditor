from typing import List, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.logger import logger
from core.config import get_config

class DocumentChunker:
    """
    Splits documents into smaller chunks for embedding.
    """
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        config = get_config()
        self.chunk_size = chunk_size or config['kb']['chunk_size']
        self.chunk_overlap = chunk_overlap or config['kb']['chunk_overlap']
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        """
        Splits a list of documents into chunks.
        """
        logger.info(f"Chunking {len(documents)} documents with size={self.chunk_size}")
        chunks = self.splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks.")
        return chunks
