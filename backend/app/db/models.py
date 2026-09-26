import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.chat import ChatMessage
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem

class SessionModel(Base):
    """
    SQLAlchemy model representing a user interview session or conversation.
    """
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = relationship(
        "ChatMessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessageModel.id"
    )
    state = relationship(
        "StructuredStateModel",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan"
    )

class ChatMessageModel(Base):
    """
    SQLAlchemy model storing individual chat turns per session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(64), index=True, nullable=True)
    session_id = Column(String(128), ForeignKey("sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    extracted_fields = Column(Text, nullable=True)  # JSON string list
    ambiguities = Column(Text, nullable=True)  # JSON string list
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="messages")

    def to_pydantic(self) -> ChatMessage:
        fields = []
        if self.extracted_fields:
            try:
                fields = json.loads(self.extracted_fields)
            except Exception:
                fields = []
        ambigs = []
        if self.ambiguities:
            try:
                ambigs = json.loads(self.ambiguities)
            except Exception:
                ambigs = []
        
        ts_str = self.timestamp.isoformat() if self.timestamp else datetime.now(timezone.utc).isoformat()

        return ChatMessage(
            id=self.message_id or str(self.id),
            role=self.role,  # type: ignore
            content=self.content,
            timestamp=ts_str,
            extracted_fields=fields,
            ambiguities=ambigs
        )

    @classmethod
    def from_pydantic(cls, session_id: str, msg: ChatMessage) -> "ChatMessageModel":
        extracted_json = json.dumps(msg.extracted_fields or [])
        ambiguities_json = json.dumps(msg.ambiguities or [])
        
        ts = None
        if msg.timestamp:
            try:
                ts = datetime.fromisoformat(msg.timestamp.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.now(timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        return cls(
            session_id=session_id,
            message_id=msg.id,
            role=msg.role,
            content=msg.content,
            extracted_fields=extracted_json,
            ambiguities=ambiguities_json,
            timestamp=ts
        )

class StructuredStateModel(Base):
    """
    SQLAlchemy model storing the extracted structured legal data per session.
    Provides explicit individual columns for direct querying as well as
    lossless JSON serialization.
    """
    __tablename__ = "structured_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), ForeignKey("sessions.session_id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Core structured legal fields
    full_name = Column(String(255), nullable=True)
    home_address = Column(Text, nullable=True)
    covers_worldwide_assets = Column(Boolean, nullable=True)
    has_children = Column(Boolean, nullable=True)
    children = Column(Text, nullable=True)  # JSON-serialized list of strings
    executor = Column(Text, nullable=True)  # JSON-serialized dict: {"name": ..., "relationship": ...}
    specific_gifts = Column(Text, nullable=True)  # JSON-serialized list of dicts
    additional_wishes = Column(Text, nullable=True)  # JSON-serialized list of strings
    
    completion_percentage = Column(Integer, default=0)
    raw_state_json = Column(Text, nullable=True)  # Complete JSON representation
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="state")

    def to_pydantic(self) -> PersonalWishesState:
        if self.raw_state_json:
            try:
                return PersonalWishesState.model_validate_json(self.raw_state_json)
            except Exception:
                pass
        
        # Fallback from individual columns
        kids = None
        if self.children:
            try:
                kids = json.loads(self.children)
            except Exception:
                kids = None
        
        exec_info = None
        if self.executor:
            try:
                e_data = json.loads(self.executor)
                if isinstance(e_data, dict):
                    exec_info = ExecutorInfo(**e_data)
            except Exception:
                exec_info = None

        gifts = []
        if self.specific_gifts:
            try:
                g_list = json.loads(self.specific_gifts)
                if isinstance(g_list, list):
                    gifts = [GiftItem(**g) for g in g_list if isinstance(g, dict)]
            except Exception:
                gifts = []

        wishes = []
        if self.additional_wishes:
            try:
                w_list = json.loads(self.additional_wishes)
                if isinstance(w_list, list):
                    wishes = [str(w) for w in w_list]
            except Exception:
                wishes = []

        return PersonalWishesState(
            full_name=self.full_name,
            home_address=self.home_address,
            covers_worldwide_assets=self.covers_worldwide_assets,
            has_children=self.has_children,
            children=kids,
            executor=exec_info,
            specific_gifts=gifts,
            additional_wishes=wishes
        )

    def update_from_pydantic(self, state: PersonalWishesState):
        self.full_name = state.full_name
        self.home_address = state.home_address
        self.covers_worldwide_assets = state.covers_worldwide_assets
        self.has_children = state.has_children
        self.children = json.dumps(state.children) if state.children is not None else None
        self.executor = json.dumps(state.executor.model_dump()) if state.executor is not None else None
        self.specific_gifts = json.dumps([g.model_dump() for g in state.specific_gifts]) if state.specific_gifts else json.dumps([])
        self.additional_wishes = json.dumps(state.additional_wishes) if state.additional_wishes else json.dumps([])
        self.completion_percentage = state.completion_percentage()
        self.raw_state_json = state.model_dump_json()
        self.updated_at = datetime.now(timezone.utc)
