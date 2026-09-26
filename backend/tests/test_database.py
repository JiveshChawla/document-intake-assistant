import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem
from app.models.chat import ChatMessage
from app.services.state_manager import StateManager
from app.db.session import SessionLocal, init_db
from app.db.models import SessionModel, ChatMessageModel, StructuredStateModel


def test_sqlite_file_and_schema_initialization():
    """Verify that SQLite app.db is initialized and contains required tables and columns."""
    init_db()
    assert os.path.exists(settings.db_file_path)

    with SessionLocal() as db:
        # Check sessions table
        session_cols = [c.name for c in SessionModel.__table__.columns]
        assert "session_id" in session_cols
        assert "created_at" in session_cols
        assert "updated_at" in session_cols

        # Check chat_messages table
        msg_cols = [c.name for c in ChatMessageModel.__table__.columns]
        assert "session_id" in msg_cols
        assert "role" in msg_cols
        assert "content" in msg_cols
        assert "extracted_fields" in msg_cols
        assert "ambiguities" in msg_cols
        assert "timestamp" in msg_cols

        # Check structured_states table
        state_cols = [c.name for c in StructuredStateModel.__table__.columns]
        assert "session_id" in state_cols
        assert "full_name" in state_cols
        assert "home_address" in state_cols
        assert "covers_worldwide_assets" in state_cols
        assert "has_children" in state_cols
        assert "children" in state_cols
        assert "executor" in state_cols
        assert "specific_gifts" in state_cols
        assert "additional_wishes" in state_cols
        assert "completion_percentage" in state_cols
        assert "raw_state_json" in state_cols


def test_session_and_messages_persisted_across_restarts():
    """Simulate server restart by instantiating a fresh StateManager and verifying recovery."""
    session_id = "restart_test_session"
    mgr1 = StateManager()
    
    # 1. Initialize session and record turns
    s1 = mgr1.get_or_create_session(session_id)
    assert len(s1.messages) >= 1  # Welcome message
    
    user_msg = ChatMessage(role="user", content="Hello, my name is Eleanor Vance")
    s1.messages.append(user_msg)
    
    # Apply state update
    mgr1.apply_validated_updates(session_id, {"full_name": "Eleanor Vance", "covers_worldwide_assets": True})

    # 2. Verify persisted in SQLite directly
    with SessionLocal() as db:
        db_s = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert db_s is not None
        assert len(db_s.messages) == 2
        assert db_s.state is not None
        assert db_s.state.full_name == "Eleanor Vance"
        assert db_s.state.covers_worldwide_assets is True

    # 3. Simulate complete server restart (fresh StateManager with empty in-memory cache)
    mgr2 = StateManager()
    assert session_id not in mgr2._sessions
    
    recovered_session = mgr2.get_or_create_session(session_id)
    assert recovered_session.session_id == session_id
    assert len(recovered_session.messages) == 2
    assert recovered_session.messages[1].content == "Hello, my name is Eleanor Vance"
    assert recovered_session.state.full_name == "Eleanor Vance"
    assert recovered_session.state.covers_worldwide_assets is True


def test_structured_state_fields_persisted_in_columns():
    """Verify all legal intake fields persist accurately to both columns and json."""
    session_id = "columns_test_session"
    mgr = StateManager()
    
    proposed = {
        "full_name": "Marcus Aurelius",
        "home_address": "Palatine Hill, Rome, Italy",
        "covers_worldwide_assets": True,
        "has_children": True,
        "children": ["Commodus", "Lucilla"],
        "executor": {"name": "Quintus Junius", "relationship": "trusted adviser"},
        "specific_gifts": [{"item": "Gold Medallion", "recipient": "Lucilla"}],
        "additional_wishes": ["Scatter ashes on the Tiber", "Quiet private memorial"]
    }
    
    updated_state, delta, warnings = mgr.apply_validated_updates(session_id, proposed)
    assert len(warnings) == 0
    assert updated_state.is_complete()

    # Query SQLite directly
    with SessionLocal() as db:
        rec = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
        assert rec is not None
        assert rec.full_name == "Marcus Aurelius"
        assert rec.home_address == "Palatine Hill, Rome, Italy"
        assert rec.covers_worldwide_assets is True
        assert rec.has_children is True
        assert "Commodus" in rec.children
        assert "Quintus Junius" in rec.executor
        assert "Gold Medallion" in rec.specific_gifts
        assert "Scatter ashes on the Tiber" in rec.additional_wishes
        assert rec.completion_percentage == 100

        # Test to_pydantic conversion
        hydrated = rec.to_pydantic()
        assert hydrated.full_name == "Marcus Aurelius"
        assert hydrated.executor.name == "Quintus Junius"
        assert len(hydrated.specific_gifts) == 1
        assert len(hydrated.additional_wishes) == 2


def test_session_reset_updates_sqlite():
    """Verify reset_session cleans messages and resets state in SQLite."""
    session_id = "reset_sqlite_test"
    mgr = StateManager()
    s = mgr.get_or_create_session(session_id)
    s.messages.append(ChatMessage(role="user", content="Test reset"))
    mgr.apply_validated_updates(session_id, {"full_name": "Reset Me"})

    # Reset
    reset_session = mgr.reset_session(session_id)
    assert reset_session.state.full_name is None
    assert len(reset_session.messages) == 1  # Only initial greeting

    # Verify SQLite reflects the reset
    with SessionLocal() as db:
        db_s = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert db_s is not None
        assert len(db_s.messages) == 1
        assert db_s.state.full_name is None


def test_manual_state_edit_persists_to_sqlite():
    """Verify set_direct_state immediately writes to SQLite."""
    session_id = "manual_edit_sqlite_test"
    mgr = StateManager()
    mgr.get_or_create_session(session_id)

    new_state = PersonalWishesState(
        full_name="Direct Edit Name",
        home_address="Direct Edit Address",
        covers_worldwide_assets=False,
        has_children=False,
        executor=ExecutorInfo(name="Direct Executor", relationship="friend")
    )
    mgr.set_direct_state(session_id, new_state)

    with SessionLocal() as db:
        rec = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
        assert rec is not None
        assert rec.full_name == "Direct Edit Name"
        assert rec.home_address == "Direct Edit Address"
        assert rec.covers_worldwide_assets is False
        assert rec.has_children is False


@pytest.mark.asyncio
async def test_api_chat_and_sessions_endpoint_integration():
    """Verify HTTP API turns automatically persist to SQLite and list_sessions retrieves them."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = "api_persistence_test"

        # 1. Turn 1 via API
        r1 = await client.post("/api/chat", json={"session_id": sid, "message": "My name is Luke Skywalker"})
        assert r1.status_code == 200
        data1 = r1.json()
        assert data1["state"]["full_name"] == "Luke Skywalker"

        # 2. Turn 2 via API
        r2 = await client.post("/api/chat", json={"session_id": sid, "message": "I live at Lars Moisture Farm, Tatooine"})
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["state"]["home_address"] == "Lars Moisture Farm, Tatooine"

        # 3. Check SQLite directly
        with SessionLocal() as db:
            db_s = db.query(SessionModel).filter(SessionModel.session_id == sid).first()
            assert db_s is not None
            # Initial greeting + Turn 1 user + Turn 1 assistant + Turn 2 user + Turn 2 assistant = 5 messages
            assert len(db_s.messages) == 5
            assert db_s.state.full_name == "Luke Skywalker"
            assert db_s.state.home_address == "Lars Moisture Farm, Tatooine"

        # 4. Check GET /api/sessions endpoint
        r_list = await client.get("/api/sessions")
        assert r_list.status_code == 200
        sessions_data = r_list.json()
        assert "sessions" in sessions_data
        matching = [s for s in sessions_data["sessions"] if s["session_id"] == sid]
        assert len(matching) == 1
        assert matching[0]["full_name"] == "Luke Skywalker"
        assert matching[0]["message_count"] == 5
