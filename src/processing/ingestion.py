from core.logger import logger
from kb.loader import DocumentLoader
from kb.chunker import DocumentChunker
from processing.cleaner import Cleaner
from processing.normalizer import Normalizer

class IngestionPipeline:
    """Orchestrates the ingestion of documents into the KB."""
    def __init__(self, kb_path: str):
        self.loader = DocumentLoader(kb_path)
        self.chunker = DocumentChunker()
        self.cleaner = Cleaner()
        self.normalizer = Normalizer()

    def run(self):
        logger.info("Starting Ingestion Pipeline")
        docs = self.loader.load_documents()
        
        # Clean and normalize
        cleaned_docs = self.cleaner.clean(docs)
        normalized_docs = self.normalizer.normalize(cleaned_docs)
        
        # Chunk
        chunks = self.chunker.chunk_documents(normalized_docs)
        logger.info(f"Ingestion complete. Generated {len(chunks)} chunks.")
        return chunks
