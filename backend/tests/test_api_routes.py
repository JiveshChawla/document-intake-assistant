import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.state_manager import state_manager

@pytest.fixture(autouse=True)
def clean_state():
    state_manager._sessions.clear()

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "active_provider" in data

@pytest.mark.asyncio
async def test_get_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/session?session_id=user_1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "user_1"
        assert len(data["messages"]) == 1  # Initial greeting
        assert data["completion_percentage"] == 0
        assert "document_markdown" in data

@pytest.mark.asyncio
async def test_chat_interaction_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User provides name and address
        resp = await client.post("/api/chat", json={
            "session_id": "flow_user",
            "message": "I am Robert Langdon living at Harvard Yard, Cambridge."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["state"]["full_name"] == "Robert Langdon"
        assert "Harvard Yard" in data["state"]["home_address"]
        assert len(data["message"]["extracted_fields"]) >= 2
        assert data["completion_percentage"] > 0

@pytest.mark.asyncio
async def test_session_reset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Populate session first
        await client.post("/api/chat", json={
            "session_id": "reset_user",
            "message": "My name is John Doe."
        })
        
        # Reset session
        resp = await client.post("/api/session/reset?session_id=reset_user")
        assert resp.status_code == 200
        data = resp.json()
        assert data["state"]["full_name"] is None
        assert data["completion_percentage"] == 0

@pytest.mark.asyncio
async def test_manual_state_edit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "manual_user",
            "state": {
                "full_name": "Dr. Watson",
                "home_address": "221B Baker St",
                "covers_worldwide_assets": True,
                "has_children": False,
                "executor": {"name": "Sherlock Holmes", "relationship": "friend"}
            }
        }
        resp = await client.post("/api/state/manual-edit", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["state"]["full_name"] == "Dr. Watson"
        assert data["completion_percentage"] == 100
        assert "Sherlock Holmes" in data["document_markdown"]
