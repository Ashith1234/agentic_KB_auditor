import os
from typing import List, Any
from langchain_community.vectorstores import FAISS
from core.logger import logger
from core.config import get_config

class VectorStoreManager:
    """
    Manages the FAISS vector database.
    """
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
        config = get_config()
        self.store_path = config['paths']['vector_store_dir']
        self.index_name = "index"

    def create_index(self, chunks: List[Any]) -> FAISS:
        """
        Creates a new FAISS index from document chunks.
        """
        logger.info(f"Creating new FAISS index at {self.store_path}")
        vector_store = FAISS.from_documents(chunks, self.embedding_function)
        self.save_index(vector_store)
        return vector_store

    def save_index(self, vector_store: FAISS):
        """
        Saves the FAISS index to disk.
        """
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)
        vector_store.save_local(self.store_path, index_name=self.index_name)
        logger.info(f"FAISS index saved to {self.store_path}")

    def load_index(self) -> FAISS:
        """
        Loads the FAISS index from disk.
        """
        if not os.path.exists(os.path.join(self.store_path, f"{self.index_name}.faiss")):
            logger.error("No FAISS index found on disk.")
            return None
        
        logger.info(f"Loading FAISS index from {self.store_path}")
        return FAISS.load_local(
            self.store_path, 
            self.embedding_function, 
            index_name=self.index_name,
            allow_dangerous_deserialization=True # Required for local loading
        )
