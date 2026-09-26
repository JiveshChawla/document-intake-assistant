from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.models.api import (
    ChatRequest, 
    ChatResponse, 
    SessionResponse, 
    StateUpdateRequest, 
    HealthResponse
)
from app.models.chat import ChatMessage
from app.services.state_manager import state_manager
from app.services.llm.factory import LLMProviderFactory
from app.services.document_generator import DocumentGenerator
from app.services.fixtures import FIXTURES

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    provider = LLMProviderFactory.get_provider()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        active_provider=provider.provider_name
    )

@router.get("/session", response_model=SessionResponse)
async def get_session(session_id: str = Query("default")):
    session = state_manager.get_or_create_session(session_id)
    doc_md, doc_html = DocumentGenerator.generate(session.state)
    provider = LLMProviderFactory.get_provider()
    
    return SessionResponse(
        session_id=session.session_id,
        messages=session.messages,
        state=session.state,
        document_markdown=doc_md,
        document_html=doc_html,
        completion_percentage=session.state.completion_percentage(),
        missing_fields=session.state.get_missing_fields(),
        active_provider=provider.provider_name
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_turn(payload: ChatRequest):
    session = state_manager.get_or_create_session(payload.session_id)
    
    # 1. Record user message
    user_msg = ChatMessage(role="user", content=payload.message)
    session.messages.append(user_msg)

    # 2. Query LLM provider with user input, history, and current confirmed state
    provider = LLMProviderFactory.get_provider()
    try:
        extraction_result = await provider.process_turn(
            user_message=payload.message,
            history=session.messages[:-1],  # prior history
            current_state=session.state
        )
    except Exception as exc:
        # Graceful fallback on unexpected LLM failure
        extraction_result = await LLMProviderFactory.get_provider("mock").process_turn(
            user_message=payload.message,
            history=session.messages[:-1],
            current_state=session.state
        )

    # 3. Validate and apply proposed updates to structured state
    updated_state, state_delta, validation_warnings = state_manager.apply_validated_updates(
        session_id=payload.session_id,
        proposed_updates=extraction_result.proposed_state_updates
    )

    # 4. Generate refreshed document draft from new confirmed state
    doc_md, doc_html = DocumentGenerator.generate(updated_state)

    # 5. Record and return assistant response
    all_ambiguities = list(extraction_result.ambiguities)
    if validation_warnings:
        all_ambiguities.extend(validation_warnings)

    assistant_msg = ChatMessage(
        role="assistant",
        content=extraction_result.assistant_message,
        extracted_fields=list(state_delta.keys()),
        ambiguities=all_ambiguities
    )
    session.messages.append(assistant_msg)

    return ChatResponse(
        message=assistant_msg,
        state=updated_state,
        state_delta=state_delta,
        ambiguities=all_ambiguities,
        document_markdown=doc_md,
        document_html=doc_html,
        completion_percentage=updated_state.completion_percentage(),
        missing_fields=updated_state.get_missing_fields(),
        active_provider=provider.provider_name
    )

@router.post("/session/reset", response_model=SessionResponse)
async def reset_session(session_id: str = Query("default")):
    session = state_manager.reset_session(session_id)
    doc_md, doc_html = DocumentGenerator.generate(session.state)
    provider = LLMProviderFactory.get_provider()
    
    return SessionResponse(
        session_id=session.session_id,
        messages=session.messages,
        state=session.state,
        document_markdown=doc_md,
        document_html=doc_html,
        completion_percentage=session.state.completion_percentage(),
        missing_fields=session.state.get_missing_fields(),
        active_provider=provider.provider_name
    )

@router.post("/state/manual-edit", response_model=SessionResponse)
async def manual_state_edit(payload: StateUpdateRequest):
    session = state_manager.get_or_create_session(payload.session_id)
    updated_state = state_manager.set_direct_state(payload.session_id, payload.state)
    doc_md, doc_html = DocumentGenerator.generate(updated_state)
    provider = LLMProviderFactory.get_provider()

    # Add a system note in transcript to maintain transparency
    note = ChatMessage(
        role="system",
        content="Structured state was updated directly via manual override."
    )
    session.messages.append(note)

    return SessionResponse(
        session_id=session.session_id,
        messages=session.messages,
        state=updated_state,
        document_markdown=doc_md,
        document_html=doc_html,
        completion_percentage=updated_state.completion_percentage(),
        missing_fields=updated_state.get_missing_fields(),
        active_provider=provider.provider_name
    )

@router.get("/sessions")
async def list_persisted_sessions():
    """Returns a list of all intake sessions stored in the SQLite database."""
    sessions = state_manager.list_sessions()
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

@router.get("/fixtures")
async def list_fixtures():
    """Returns sample test fixtures for demonstration and automated testing."""
    return FIXTURES
