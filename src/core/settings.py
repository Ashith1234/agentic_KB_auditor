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

    # ── Performance & Safety ──────────────────────────────────────
    # Max seconds a single agent is allowed to run before it is cancelled.
    # Set via AGENT_TIMEOUT_SECONDS env var.  Default: 10s.
    AGENT_TIMEOUT_SECONDS: int = 10

    # When True: skip Planner, EpisodicStore, SemanticStore writes.
    # Trades intelligence for speed. Enable via LIGHT_MODE=true env var.
    LIGHT_MODE: bool = False

    # When True: audit pipeline runs in a background thread so the host
    # chatbot response is never blocked.  Enable via AUDIT_ASYNC=true.
    AUDIT_ASYNC: bool = True

settings = Settings()
