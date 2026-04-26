from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4-turbo-preview"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Path settings
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    KB_PATH: str = os.path.join(BASE_DIR, "data", "kb")
    VECTOR_STORE_PATH: str = os.path.join(BASE_DIR, "data", "vector_store")

settings = Settings()
