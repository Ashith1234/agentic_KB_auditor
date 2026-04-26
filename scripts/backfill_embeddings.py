import sys
import os

# Scripts run from project root; add src/ to path so bare package names resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.logger import logger
from processing.ingestion import IngestionPipeline
from kb.embedder import Embedder
from kb.vector_store import VectorStoreManager

def main():
    logger.info("Starting Embedding Backfill Script...")

    pipeline = IngestionPipeline(kb_path="data/kb")
    chunks = pipeline.run()

    if not chunks:
        logger.warning("No chunks generated. Check data/kb directory.")
        return

    embedder = Embedder()
    embedding_func = embedder.get_embedding_function()

    vs_manager = VectorStoreManager(embedding_func)
    vs_manager.create_index(chunks)
    logger.info("Backfill complete.")

if __name__ == "__main__":
    main()
