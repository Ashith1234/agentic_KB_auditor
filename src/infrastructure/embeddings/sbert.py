from langchain_community.embeddings import HuggingFaceEmbeddings
from core.logger import logger

class SBERTEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        logger.info(f"Initializing SBERT Embedder with model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    def get_embeddings(self):
        return self.embeddings
