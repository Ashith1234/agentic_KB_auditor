from langchain_openai import OpenAIEmbeddings
from core.logger import logger
from core.settings import settings

class OpenAIEmbedder:
    def __init__(self, model_name: str = "text-embedding-3-small"):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        logger.info(f"Initializing OpenAI Embedder with model: {model_name}")
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=model_name
        )
    
    def get_embeddings(self):
        return self.embeddings
