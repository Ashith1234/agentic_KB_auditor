from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Version(BaseModel):
    version_id: str
    article_id: str
    content: str
    content_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: str = "system"
    is_active: bool = True
    previous_version_id: Optional[str] = None

