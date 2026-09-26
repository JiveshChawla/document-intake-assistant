import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.state_manager import state_manager

@pytest.fixture(autouse=True)
def clean_state():
    state_manager.clear_all()

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

@pytest.mark.asyncio
async def test_full_conversational_intake_with_executor_followup():
    """Test full multi-turn interview verifying that executor name does not overwrite user's full_name."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = "complete_flow_user"

        # Turn 1: Name
        r1 = await client.post("/api/chat", json={"session_id": sid, "message": "My name is Arthur Dent"})
        assert r1.json()["state"]["full_name"] == "Arthur Dent"

        # Turn 2: Address
        r2 = await client.post("/api/chat", json={"session_id": sid, "message": "15 Country Lane, Cottington, England"})
        assert r2.json()["state"]["full_name"] == "Arthur Dent"
        assert "Cottington" in r2.json()["state"]["home_address"]

        # Turn 3: Worldwide assets
        r3 = await client.post("/api/chat", json={"session_id": sid, "message": "Worldwide assets please"})
        assert r3.json()["state"]["covers_worldwide_assets"] is True

        # Turn 4: Children
        r4 = await client.post("/api/chat", json={"session_id": sid, "message": "No children"})
        assert r4.json()["state"]["has_children"] is False

        # Turn 5: Executor - Partial (relationship only)
        r5 = await client.post("/api/chat", json={"session_id": sid, "message": "My brother"})
        d5 = r5.json()
        assert d5["state"]["full_name"] == "Arthur Dent"  # Full name MUST NOT change
        assert d5["state"]["executor"]["relationship"] == "brother"
        assert d5["state"]["executor"]["name"] is None
        assert len(d5["ambiguities"]) > 0

        # Turn 6: Executor - Follow up name
        r6 = await client.post("/api/chat", json={"session_id": sid, "message": "Ford Prefect"})
        d6 = r6.json()
        # Full name MUST REMAIN Arthur Dent!
        assert d6["state"]["full_name"] == "Arthur Dent"
        assert d6["state"]["executor"]["name"] == "Ford Prefect"
        assert d6["state"]["executor"]["relationship"] == "brother"
        assert d6["completion_percentage"] == 100

        # Turn 7: Gifts - Bare 'Yes'
        r7 = await client.post("/api/chat", json={"session_id": sid, "message": "Yes"})
        d7 = r7.json()
        assert "describe the specific gifts" in d7["message"]["content"].lower()
        assert len(d7["state"]["specific_gifts"]) == 0

        # Turn 8: Gifts - Provide gift detail
        r8 = await client.post("/api/chat", json={"session_id": sid, "message": "My vintage watch to my son Lucas"})
        d8 = r8.json()
        assert len(d8["state"]["specific_gifts"]) == 1
        assert "watch" in d8["state"]["specific_gifts"][0]["item"].lower()
        assert "lucas" in d8["state"]["specific_gifts"][0]["recipient"].lower()
        # Verify gift is rendered in live document markdown
        assert "vintage watch" in d8["document_markdown"].lower()
        assert "lucas" in d8["document_markdown"].lower()

        # Turn 9: Gifts - Move on
        r9 = await client.post("/api/chat", json={"session_id": sid, "message": "No, move on"})
        d9 = r9.json()
        assert "additional personal wishes" in d9["message"]["content"].lower()

        # Turn 10: Wishes - Provide directive
        r10 = await client.post("/api/chat", json={"session_id": sid, "message": "Cremation and ashes scattered in Lake District"})
        d10 = r10.json()
        assert len(d10["state"]["additional_wishes"]) == 1
        assert "lake district" in d10["state"]["additional_wishes"][0].lower()
        # Verify wish is rendered in live document markdown
        assert "lake district" in d10["document_markdown"].lower()

        # Turn 11: Finalize
        r11 = await client.post("/api/chat", json={"session_id": sid, "message": "Ready to finalize"})
        d11 = r11.json()
        assert "captured" in d11["message"]["content"].lower() or "review" in d11["message"]["content"].lower()
        assert d11["completion_percentage"] == 100
        assert len(d11["state"]["specific_gifts"]) == 1
        assert len(d11["state"]["additional_wishes"]) == 1

