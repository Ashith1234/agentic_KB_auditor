import os
from typing import List, Any
from langchain_community.vectorstores import FAISS
from core.logger import logger

class FAISSAdapter:
    """Infrastructure adapter for FAISS vector database."""
    def __init__(self, embedding_function, store_path: str):
        self.embedding_function = embedding_function
        self.store_path = store_path
        self.index_name = "index"

    def create_or_load(self, chunks: List[Any] = None) -> FAISS:
        if os.path.exists(os.path.join(self.store_path, f"{self.index_name}.faiss")):
            logger.info("Loading existing FAISS index")
            return FAISS.load_local(
                self.store_path, 
                self.embedding_function, 
                index_name=self.index_name,
                allow_dangerous_deserialization=True
            )
        elif chunks:
            logger.info("Creating new FAISS index")
            vs = FAISS.from_documents(chunks, self.embedding_function)
            self._save(vs)
            return vs
        else:
            raise ValueError("No index found and no chunks provided to create one.")

    def _save(self, vector_store: FAISS):
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)
        vector_store.save_local(self.store_path, index_name=self.index_name)
