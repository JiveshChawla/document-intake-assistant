import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    extracted_fields: Optional[List[str]] = Field(default_factory=list, description="Fields updated in this turn")
    ambiguities: Optional[List[str]] = Field(default_factory=list, description="Any ambiguities identified in this turn")
