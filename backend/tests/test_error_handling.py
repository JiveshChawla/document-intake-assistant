import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.state_manager import state_manager
from app.services.fixtures import FIXTURES

@pytest.fixture(autouse=True)
def clean_state():
    state_manager._sessions.clear()

@pytest.mark.asyncio
async def test_empty_chat_message_validation():
    """Verify that empty string payloads fail API validation with 422 Unprocessable Entity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/chat", json={
            "session_id": "err_user",
            "message": ""
        })
        assert resp.status_code == 422

@pytest.mark.asyncio
async def test_graceful_recovery_from_corrupted_model_fixture():
    """Verify that if model returns a malformed fixture, backend recovers gracefully without crashing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Trigger the malformed fixture
        resp = await client.post("/api/chat", json={
            "session_id": "malformed_test",
            "message": "[FIXTURE_MALFORMED]"
        })
        assert resp.status_code == 200
        data = resp.json()
        # Ensure state was not corrupted by integers for name or invalid booleans
        assert data["state"]["full_name"] is None
        assert data["state"]["covers_worldwide_assets"] is None
        assert len(data["ambiguities"]) > 0

@pytest.mark.asyncio
async def test_fixtures_catalog_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/fixtures")
        assert resp.status_code == 200
        data = resp.json()
        assert "valid_multi_field" in data
        assert "ambiguous_executor_missing_name" in data
