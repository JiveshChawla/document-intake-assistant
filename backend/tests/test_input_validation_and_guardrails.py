import pytest
from app.services.validator import InputValidator
from app.services.llm.prompts import SYSTEM_PROMPT, get_last_question_topic, build_gemini_prompt
from app.services.llm.gemini_provider import GeminiLLMProvider
from app.services.llm.mock_provider import MockLLMProvider
from app.services.state_manager import StateManager
from app.models.state import PersonalWishesState, ExecutorInfo
from app.models.chat import ChatMessage


# =====================================================================
# 1. InputValidator Unit Tests
# =====================================================================

def test_is_gibberish_detection():
    # Keyboard mash / walks
    assert InputValidator.is_gibberish("asdfghjk")[0] is True
    assert InputValidator.is_gibberish("qwerty")[0] is True
    assert InputValidator.is_gibberish("zxcvbnm")[0] is True

    # Placeholders / refusals
    assert InputValidator.is_gibberish("idk")[0] is True
    assert InputValidator.is_gibberish("none")[0] is True
    assert InputValidator.is_gibberish("n/a")[0] is True
    assert InputValidator.is_gibberish("test")[0] is True
    assert InputValidator.is_gibberish("unknown")[0] is True

    # Repetitive characters
    assert InputValidator.is_gibberish("aaaaaa")[0] is True
    assert InputValidator.is_gibberish("zzzzz")[0] is True

    # Words without vowels
    assert InputValidator.is_gibberish("bcdfgh")[0] is True

    # Valid inputs should NOT be flagged as gibberish
    assert InputValidator.is_gibberish("Jane Doe")[0] is False
    assert InputValidator.is_gibberish("10 Downing Street, London")[0] is False
    assert InputValidator.is_gibberish("brother")[0] is False
    assert InputValidator.is_gibberish("Cremate and scatter ashes in the Pacific")[0] is False


def test_validate_name():
    # Invalid names
    assert InputValidator.validate_name("a")[0] is False  # Too short
    assert InputValidator.validate_name("John Doe 123")[0] is False  # Digits
    assert InputValidator.validate_name("asdfghjk")[0] is False  # Gibberish keyboard walk
    assert InputValidator.validate_name("idk")[0] is False  # Refusal
    assert InputValidator.validate_name("!!!@@@###")[0] is False  # Punctuation

    # Valid names worldwide
    assert InputValidator.validate_name("Jane Doe")[0] is True
    assert InputValidator.validate_name("Dr. Martin Luther King Jr.")[0] is True
    assert InputValidator.validate_name("Jean-Luc Picard")[0] is True
    assert InputValidator.validate_name("José María González")[0] is True
    assert InputValidator.validate_name("Søren Kierkegaard")[0] is True


def test_validate_address():
    # Invalid addresses
    assert InputValidator.validate_address("123")[0] is False  # Too short
    assert InputValidator.validate_address("987654321")[0] is False  # Pure numbers
    assert InputValidator.validate_address("asdfghjkl")[0] is False  # Gibberish
    assert InputValidator.validate_address("idk")[0] is False  # Refusal

    # Valid addresses worldwide
    assert InputValidator.validate_address("10 Downing Street, London, UK")[0] is True
    assert InputValidator.validate_address("Apartment 4B, 742 Evergreen Terrace, Springfield")[0] is True
    assert InputValidator.validate_address("1-1 Chiyoda, Chiyoda-ku, Tokyo")[0] is True
    assert InputValidator.validate_address("15 Rue de Rivoli, 75004 Paris, France")[0] is True


def test_validate_relationship():
    # Invalid relationships
    assert InputValidator.validate_relationship("123")[0] is False  # Digits
    assert InputValidator.validate_relationship("asdf")[0] is False  # Keyboard walk
    assert InputValidator.validate_relationship("none")[0] is False  # Placeholder

    # Valid relationships
    assert InputValidator.validate_relationship("brother")[0] is True
    assert InputValidator.validate_relationship("sister")[0] is True
    assert InputValidator.validate_relationship("trusted friend")[0] is True
    assert InputValidator.validate_relationship("family solicitor")[0] is True


def test_validate_proposed_updates_filtering():
    updates = {
        "full_name": "asdfghjk",  # Invalid gibberish
        "home_address": "10 Downing Street, London",  # Valid
        "covers_worldwide_assets": True,  # Valid
        "executor": {
            "name": "123456",  # Invalid name with digits
            "relationship": "brother"  # Valid relationship
        }
    }
    validated, rejections = InputValidator.validate_proposed_updates(updates)

    # full_name should be stripped
    assert "full_name" not in validated
    # home_address and assets scope should be preserved
    assert validated["home_address"] == "10 Downing Street, London"
    assert validated["covers_worldwide_assets"] is True
    # executor name stripped, relationship preserved
    assert validated["executor"]["name"] is None
    assert validated["executor"]["relationship"] == "brother"

    # Rejection reasons reported
    assert len(rejections) >= 2
    assert any("full_name" in r for r in rejections)
    assert any("executor name" in r for r in rejections)


# =====================================================================
# 2. LLM System Prompt & Guardrails Verification
# =====================================================================

def test_system_prompt_contains_exact_guardrails():
    """Verify that the verbatim required guardrail sentence is present in the prompt."""
    required_sentence = (
        "You are a precise legal document intake assistant. "
        "Validate all user inputs against the expected field type. "
        "If an input is invalid, nonsensical, or unclear, do not save it; politely ask the user to clarify."
    )
    # Check normalized whitespace
    normalized_prompt = " ".join(SYSTEM_PROMPT.split())
    assert required_sentence in normalized_prompt


def test_build_gemini_prompt_structure():
    state = PersonalWishesState(full_name="Jane Doe")
    history = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="What is your home address?")
    ]
    prompt = build_gemini_prompt(
        user_message="asdfghjk",
        history=history,
        current_state=state,
        last_topic="ADDRESS"
    )

    assert "CURRENT CONFIRMED STATE:" in prompt
    assert "Jane Doe" in prompt
    assert "RECENT CONVERSATION HISTORY:" in prompt
    assert "ACTIVE INTAKE FOCUS: The assistant's latest question was specifically regarding: ADDRESS" in prompt
    assert "CURRENT USER MESSAGE:\nasdfghjk" in prompt


# =====================================================================
# 3. Context-Aware Field Mapping & Executor Guard
# =====================================================================

def test_get_last_question_topic_accuracy():
    # Asking for principal name
    h1 = [ChatMessage(role="assistant", content="Could you please tell me your full legal name?")]
    assert get_last_question_topic(h1) == "NAME"

    # Asking for executor details
    h2 = [ChatMessage(role="assistant", content="Who would you like to appoint as your Executor, and what is their relationship to you?")]
    assert get_last_question_topic(h2) == "EXECUTOR_ALL"

    # Asking specifically for executor name (should NOT trigger principal NAME topic)
    h3 = [ChatMessage(role="assistant", content="What is the full legal name of your brother whom you wish to appoint as executor?")]
    assert get_last_question_topic(h3) == "EXECUTOR_NAME"

    # Asking for executor relationship
    h4 = [ChatMessage(role="assistant", content="What is James's relationship to you?")]
    assert get_last_question_topic(h4) == "EXECUTOR_RELATIONSHIP"


# =====================================================================
# 4. StateManager Invariant Validation
# =====================================================================

def test_state_manager_rejects_gibberish_full_name():
    sm = StateManager()
    session = sm.get_or_create_session("test_session_gibberish_name")

    proposed = {"full_name": "qwertyuiop"}
    updated_state, delta, warnings = sm.apply_validated_updates(session.session_id, proposed)

    assert updated_state.full_name is None
    assert "full_name" not in delta
    assert len(warnings) > 0
    assert any("full_name" in w for w in warnings)


def test_state_manager_rejects_pure_numeric_address():
    sm = StateManager()
    session = sm.get_or_create_session("test_session_numeric_address")

    proposed = {"home_address": "123456789"}
    updated_state, delta, warnings = sm.apply_validated_updates(session.session_id, proposed)

    assert updated_state.home_address is None
    assert "home_address" not in delta
    assert len(warnings) > 0
    assert any("home_address" in w for w in warnings)


def test_state_manager_accepts_valid_updates():
    sm = StateManager()
    session = sm.get_or_create_session("test_session_valid")

    proposed = {
        "full_name": "Jane Doe",
        "home_address": "10 Downing Street, London",
        "covers_worldwide_assets": True,
        "has_children": True,
        "children": ["Lucas Doe", "Emma Doe"],
        "executor": {"name": "James Smith", "relationship": "brother"}
    }
    updated_state, delta, warnings = sm.apply_validated_updates(session.session_id, proposed)

    assert len(warnings) == 0
    assert updated_state.full_name == "Jane Doe"
    assert updated_state.home_address == "10 Downing Street, London"
    assert updated_state.covers_worldwide_assets is True
    assert updated_state.has_children is True
    assert updated_state.children == ["Lucas Doe", "Emma Doe"]
    assert updated_state.executor.name == "James Smith"
    assert updated_state.executor.relationship == "brother"
    assert updated_state.is_complete()


# =====================================================================
# 5. Conversational Mock Provider End-to-End Validation
# =====================================================================

@pytest.mark.asyncio
async def test_mock_provider_rejects_gibberish_name():
    provider = MockLLMProvider()
    initial_state = PersonalWishesState()
    history = [
        ChatMessage(role="assistant", content="Hello! Could you please tell me your full legal name?")
    ]

    # User inputs keyboard mash
    result = await provider.process_turn("asdfghjkl", history, initial_state)

    # State update must NOT contain the gibberish name
    assert "full_name" not in result.proposed_state_updates
    # Ambiguities must record the validation failure
    assert len(result.ambiguities) > 0
    # Assistant message must politely ask for legal full name
    assert "legal name" in result.assistant_message.lower() or "accuracy" in result.assistant_message.lower()


@pytest.mark.asyncio
async def test_mock_provider_rejects_gibberish_address():
    provider = MockLLMProvider()
    state_with_name = PersonalWishesState(full_name="Jane Doe")
    history = [
        ChatMessage(role="user", content="My name is Jane Doe"),
        ChatMessage(role="assistant", content="Thank you, Jane Doe. What is your current residential home address?")
    ]

    # User inputs numbers only for address
    result = await provider.process_turn("12345", history, state_with_name)

    # State update must NOT contain the invalid address
    assert "home_address" not in result.proposed_state_updates
    assert len(result.ambiguities) > 0
    assert "residential address" in result.assistant_message.lower() or "accuracy" in result.assistant_message.lower()


@pytest.mark.asyncio
async def test_mock_provider_never_overwrites_name_on_executor_turn():
    provider = MockLLMProvider()
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="10 Downing St, London",
        covers_worldwide_assets=True,
        has_children=False
    )
    history = [
        ChatMessage(
            role="assistant",
            content="Who would you like to appoint as your Executor (the person who will administer your estate and carry out your wishes), and what is their relationship to you?"
        )
    ]

    # User provides only an executor name
    result = await provider.process_turn("Pierre Dubois", history, state)

    # Must NOT overwrite full_name!
    assert "full_name" not in result.proposed_state_updates
    # Must map to executor
    assert "executor" in result.proposed_state_updates
    assert result.proposed_state_updates["executor"]["name"] == "Pierre Dubois"


@pytest.mark.asyncio
async def test_mock_provider_multi_field_with_one_invalid():
    """If user provides valid address but gibberish name, accept valid address, reject gibberish name."""
    provider = MockLLMProvider()
    state = PersonalWishesState()
    history = [
        ChatMessage(role="assistant", content="Please provide your full legal name and residential address.")
    ]

    # Valid address with keyboard mash name
    result = await provider.process_turn("asdfghjk living at 10 Downing Street, London", history, state)

    # Should NOT have full_name
    assert "full_name" not in result.proposed_state_updates
    # Should have extracted home_address
    assert result.proposed_state_updates.get("home_address") == "10 Downing Street, London"
    # Should report ambiguity regarding name
    assert len(result.ambiguities) > 0
