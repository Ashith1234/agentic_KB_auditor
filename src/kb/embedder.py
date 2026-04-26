from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from core.config import get_config
from core.settings import settings
from core.logger import logger

class Embedder:
    """
    Wrapper for different embedding models.
    """
    def __init__(self, provider: str = None, model_name: str = None):
        config = get_config()
        self.provider = provider or config['llm']['provider']
        self.model_name = model_name or config['kb']['embedding_model']

    def get_embedding_function(self):
        """
        Returns the embedding function based on the provider.
        """
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not found. Falling back to SBERT.")
                return self._get_sbert_embeddings()
            logger.info("Using OpenAI Embeddings")
            return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            return self._get_sbert_embeddings()

    def _get_sbert_embeddings(self):
        logger.info(f"Using SBERT Embeddings ({self.model_name})")
        return HuggingFaceEmbeddings(model_name=self.model_name)
