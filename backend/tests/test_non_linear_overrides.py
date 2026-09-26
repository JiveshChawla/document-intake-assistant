import pytest
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem
from app.models.chat import ChatMessage
from app.services.llm.mock_provider import MockLLMProvider

@pytest.fixture
def mock_llm():
    return MockLLMProvider()

@pytest.mark.asyncio
async def test_override_executor_during_address_question(mock_llm):
    """User changes executor while assistant is asking for home address."""
    history = [
        ChatMessage(role="assistant", content="Thank you, Alice Cooper. What is your current residential home address?")
    ]
    state = PersonalWishesState(
        full_name="Alice Cooper",
        home_address=None,
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Bob Cooper", relationship="brother")
    )

    # User overrides executor with name and relationship
    res = await mock_llm.process_turn("Actually, change my executor to Jane Doe, my friend", history, state)
    
    assert res.proposed_state_updates.get("executor") == {
        "name": "Jane Doe",
        "relationship": "friend"
    }
    # No false address ambiguity should be generated
    assert len(res.ambiguities) == 0
    # Assistant response acknowledges update and smoothly resumes address intake
    assert "updated" in res.assistant_message.lower()
    assert "jane doe" in res.assistant_message.lower()
    assert "address" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_override_address_during_executor_question(mock_llm):
    """User changes address while assistant is asking for executor."""
    history = [
        ChatMessage(
            role="assistant",
            content="Who would you like to appoint as your Executor (the person who will administer your estate and carry out your wishes), and what is their relationship to you?"
        )
    ]
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="10 Downing St, London",
        covers_worldwide_assets=True,
        has_children=False
    )

    res = await mock_llm.process_turn("Actually, change my address to 221B Baker St, London", history, state)

    assert res.proposed_state_updates.get("home_address") == "221B Baker St, London"
    # Never overwrite or invent executor
    assert "executor" not in res.proposed_state_updates
    assert len(res.ambiguities) == 0
    # Response acknowledges updated address and continues with executor prompt
    assert "updated" in res.assistant_message.lower()
    assert "221b baker st" in res.assistant_message.lower()
    assert "executor" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_override_name_during_executor_question(mock_llm):
    """User changes their own full name while assistant is asking for executor."""
    history = [
        ChatMessage(
            role="assistant",
            content="Who would you like to appoint as your Executor (the person who will administer your estate and carry out your wishes), and what is their relationship to you?"
        )
    ]
    state = PersonalWishesState(
        full_name="Peter Parker",
        home_address="20 Ingram St, New York",
        covers_worldwide_assets=True,
        has_children=False
    )

    res = await mock_llm.process_turn("Actually, change my name to Bruce Wayne", history, state)

    assert res.proposed_state_updates.get("full_name") == "Bruce Wayne"
    assert "executor" not in res.proposed_state_updates
    assert len(res.ambiguities) == 0
    assert "bruce wayne" in res.assistant_message.lower()
    assert "executor" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_override_asset_scope_during_children_question(mock_llm):
    """User changes asset scope while assistant asks about children."""
    history = [
        ChatMessage(role="assistant", content="Do you have any children?")
    ]
    state = PersonalWishesState(
        full_name="Clark Kent",
        home_address="344 Clinton St, Metropolis",
        covers_worldwide_assets=True
    )

    res = await mock_llm.process_turn("Actually, change asset scope to domestic only", history, state)

    assert res.proposed_state_updates.get("covers_worldwide_assets") is False
    assert len(res.ambiguities) == 0
    assert "domestic" in res.assistant_message.lower()
    assert "children" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_override_children_status_during_wishes_question(mock_llm):
    """User changes children to none while on wishes question."""
    history = [
        ChatMessage(role="assistant", content="Are there any additional personal wishes or directives you'd like to include?")
    ]
    state = PersonalWishesState(
        full_name="Diana Prince",
        home_address="Themyscira Embassy, London",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Lucas"],
        executor=ExecutorInfo(name="Steve Trevor", relationship="friend")
    )

    res = await mock_llm.process_turn("Actually, change to no children", history, state)

    assert res.proposed_state_updates.get("has_children") is False
    assert res.proposed_state_updates.get("children") == []
    assert len(res.ambiguities) == 0
    assert "updated" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_override_children_names_with_new_names(mock_llm):
    """User updates children names out of order."""
    history = [
        ChatMessage(role="assistant", content="Who would you like to appoint as your Executor?")
    ]
    state = PersonalWishesState(
        full_name="Diana Prince",
        home_address="Themyscira Embassy, London",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Lucas"]
    )

    res = await mock_llm.process_turn("Actually, change my children to Lucas and Emma", history, state)

    assert res.proposed_state_updates.get("has_children") is True
    assert res.proposed_state_updates.get("children") == ["Lucas", "Emma"]
    assert len(res.ambiguities) == 0
    assert "lucas" in res.assistant_message.lower()
    assert "emma" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_non_linear_add_and_clear_gifts(mock_llm):
    """User adds a gift out of order, then clears all gifts."""
    history = [
        ChatMessage(role="assistant", content="Are there any additional personal wishes or directives you'd like to include?")
    ]
    state = PersonalWishesState(
        full_name="Tony Stark",
        home_address="10880 Malibu Point, Malibu, CA",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Pepper Potts", relationship="partner"),
        specific_gifts=[]
    )

    # 1. Add gift out of order
    res1 = await mock_llm.process_turn("Actually, add a gift: my vintage watch to Lucas", history, state)
    assert "specific_gifts" in res1.proposed_state_updates
    gifts = res1.proposed_state_updates["specific_gifts"]
    assert len(gifts) == 1
    assert "watch" in gifts[0]["item"].lower()
    assert "lucas" in gifts[0]["recipient"].lower()

    # 2. Clear all gifts
    state.specific_gifts = [GiftItem(item="Vintage watch", recipient="Lucas")]
    res2 = await mock_llm.process_turn("Actually, remove all gifts", history, state)
    assert res2.proposed_state_updates.get("specific_gifts") == []
    assert "removed all specific gifts" in res2.assistant_message.lower()

@pytest.mark.asyncio
async def test_non_linear_add_and_clear_wishes(mock_llm):
    """User adds a wish out of order, then clears wishes."""
    history = [
        ChatMessage(role="assistant", content="Who would you like to appoint as your Executor?")
    ]
    state = PersonalWishesState(
        full_name="Steve Rogers",
        home_address="569 Leaman Place, Brooklyn, NY",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes=[]
    )

    # 1. Add wish out of order
    res1 = await mock_llm.process_turn("Actually, add a wish: I want to be cremated", history, state)
    assert "additional_wishes" in res1.proposed_state_updates
    assert any("cremated" in w.lower() for w in res1.proposed_state_updates["additional_wishes"])

    # 2. Clear all wishes
    state.additional_wishes = ["I want to be cremated"]
    res2 = await mock_llm.process_turn("Actually, remove all wishes", history, state)
    assert res2.proposed_state_updates.get("additional_wishes") == []
    assert "removed all additional wishes" in res2.assistant_message.lower()

@pytest.mark.asyncio
async def test_executor_override_with_name_only_prompts_for_relationship(mock_llm):
    """User overrides executor with only name, assistant records name and prompts for relationship."""
    history = [
        ChatMessage(role="assistant", content="What is your current residential home address?")
    ]
    state = PersonalWishesState(
        full_name="John Doe",
        home_address=None,
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Bob Doe", relationship="brother")
    )

    res = await mock_llm.process_turn("Actually, change my executor to Jane Doe", history, state)
    
    # State update should have name Jane Doe and relationship None
    assert res.proposed_state_updates.get("executor") == {
        "name": "Jane Doe",
        "relationship": None
    }
    # Ambiguity prompt should request relationship
    assert any("relationship is missing" in amb.lower() for amb in res.ambiguities)

@pytest.mark.asyncio
async def test_api_end_to_end_non_linear_override_flow():
    """Verify full end-to-end multi-turn conversation over API with non-linear override."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.services.state_manager import state_manager

    session_id = "test_non_linear_api_session"
    state_manager.clear_all()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: User provides name and address
        r1 = await client.post("/api/chat", json={
            "session_id": session_id,
            "message": "I am Hermione Granger living at 8 Heathgate, Hampstead Garden Suburb, London."
        })
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["state"]["full_name"] == "Hermione Granger"
        assert "Heathgate" in d1["state"]["home_address"]

        # Step 2: Assistant asks about worldwide assets; user overrides executor instead!
        r2 = await client.post("/api/chat", json={
            "session_id": session_id,
            "message": "Actually, change my executor to Harry Potter, my friend."
        })
        assert r2.status_code == 200
        d2 = r2.json()
        # Executor must be updated immediately
        assert d2["state"]["executor"]["name"] == "Harry Potter"
        assert d2["state"]["executor"]["relationship"] == "friend"
        # Full name and address preserved
        assert d2["state"]["full_name"] == "Hermione Granger"
        # Assistant acknowledges executor and resumes worldwide assets prompt
        bot_msg = d2["message"]["content"].lower()
        assert "harry potter" in bot_msg
        assert "worldwide" in bot_msg or "assets" in bot_msg

        # Step 3: User answers worldwide assets question
        r3 = await client.post("/api/chat", json={
            "session_id": session_id,
            "message": "Worldwide assets please."
        })
        assert r3.status_code == 200
        d3 = r3.json()
        assert d3["state"]["covers_worldwide_assets"] is True
        assert d3["state"]["executor"]["name"] == "Harry Potter"

