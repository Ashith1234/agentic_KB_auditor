from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class SignalType(str, Enum):
    OUTDATED = "outdated"
    DUPLICATE = "duplicate"
    CONTRADICTION = "contradiction"
    GAP = "gap"
    UNKNOWN = "unknown"

class AuditSignal(BaseModel):
    id: str
    signal_type: SignalType
    description: str
    severity: str = "medium" # low, medium, high, critical
    source_agent: str
    metadata: Dict[str, Any] = {}
