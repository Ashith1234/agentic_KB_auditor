from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Article(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    source: str = "unknown"
