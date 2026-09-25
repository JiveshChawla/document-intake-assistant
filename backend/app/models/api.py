from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's input text in conversation")
    session_id: Optional[str] = Field("default", description="Session identifier for multi-session support")

class ChatResponse(BaseModel):
    message: ChatMessage
    state: PersonalWishesState
    state_delta: Dict[str, Any] = Field(default_factory=dict, description="Fields modified in this turn")
    ambiguities: List[str] = Field(default_factory=list, description="Ambiguities or follow-up items flagged")
    document_markdown: str = Field(..., description="Draft legal document formatted in Markdown")
    document_html: str = Field(..., description="Draft legal document formatted in HTML")
    completion_percentage: int
    missing_fields: List[str]
    active_provider: str

class StateUpdateRequest(BaseModel):
    session_id: Optional[str] = Field("default", description="Session identifier")
    state: PersonalWishesState = Field(..., description="New structured state directly applied")

class SessionResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    state: PersonalWishesState
    document_markdown: str
    document_html: str
    completion_percentage: int
    missing_fields: List[str]
    active_provider: str

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    active_provider: str
