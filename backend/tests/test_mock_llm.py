import pytest
from app.models.state import PersonalWishesState, ExecutorInfo
from app.services.llm.mock_provider import MockLLMProvider

@pytest.fixture
def mock_llm():
    return MockLLMProvider()

@pytest.mark.asyncio
async def test_extract_multi_field_input(mock_llm):
    user_input = "I am Jane Doe living at 10 Downing St, London. I want worldwide coverage and I don't have children."
    state = PersonalWishesState()
    result = await mock_llm.process_turn(user_input, [], state)
    
    updates = result.proposed_state_updates
    assert updates.get("full_name") == "Jane Doe"
    assert "10 Downing St" in updates.get("home_address", "")
    assert updates.get("covers_worldwide_assets") is True
    assert updates.get("has_children") is False
    assert len(result.ambiguities) == 0

@pytest.mark.asyncio
async def test_ambiguous_executor_flags_warning(mock_llm):
    user_input = "I want to appoint my brother as executor."
    state = PersonalWishesState(full_name="Jane Doe")
    result = await mock_llm.process_turn(user_input, [], state)
    
    assert "executor" in result.proposed_state_updates
    assert result.proposed_state_updates["executor"]["relationship"] == "brother"
    assert result.proposed_state_updates["executor"]["name"] is None
    assert len(result.ambiguities) > 0
    assert any("name is missing" in amb.lower() for amb in result.ambiguities)
    # The follow-up question should specifically ask for the brother's name
    assert "name" in result.assistant_message.lower()

@pytest.mark.asyncio
async def test_correction_executor(mock_llm):
    user_input = "Actually, change my executor to my sister Sarah Jenkins."
    current_state = PersonalWishesState(
        full_name="Jane Doe",
        executor=ExecutorInfo(name="James Smith", relationship="brother")
    )
    result = await mock_llm.process_turn(user_input, [], current_state)
    updates = result.proposed_state_updates
    assert updates.get("executor", {}).get("name") == "Sarah Jenkins"
    assert updates.get("executor", {}).get("relationship") == "sister"

@pytest.mark.asyncio
async def test_triggered_fixture_valid(mock_llm):
    result = await mock_llm.process_turn("[FIXTURE_VALID]", [], PersonalWishesState())
    assert result.proposed_state_updates["full_name"] == "Jane Doe"
    assert result.proposed_state_updates["covers_worldwide_assets"] is True

@pytest.mark.asyncio
async def test_triggered_fixture_ambiguous(mock_llm):
    result = await mock_llm.process_turn("[FIXTURE_AMBIGUOUS]", [], PersonalWishesState())
    assert len(result.ambiguities) > 0

@pytest.mark.asyncio
async def test_intelligent_follow_up_progression(mock_llm):
    # When full_name is already provided, assistant asks for address
    state = PersonalWishesState(full_name="Arthur Dent")
    result = await mock_llm.process_turn("Hello again", [], state)
    assert "address" in result.assistant_message.lower()
