import pytest
from app.models.state import PersonalWishesState, ExecutorInfo
from app.models.chat import ChatMessage
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
async def test_universal_international_addresses(mock_llm):
    """Test custom free-text addresses from various countries worldwide."""
    history_asking_address = [
        ChatMessage(role="assistant", content="What is your current residential home address?")
    ]
    state = PersonalWishesState(full_name="Carlos Martinez")

    test_addresses = [
        "14 Rue de la Paix, 75002 Paris, France",
        "Flat 302, Green Valley Apartments, Bangalore, India 560001",
        "Apartment 4B, Shibuya 1-chome, Tokyo 150-0002, Japan",
        "42 Wallaby Way, Sydney NSW 2000, Australia",
        "Av. Paulista 1000, Bela Vista, São Paulo, Brazil",
        "Calle 85 # 11-53, Bogotá, Colombia",
    ]

    for addr in test_addresses:
        res = await mock_llm.process_turn(addr, history_asking_address, state)
        assert res.proposed_state_updates.get("home_address") == addr, f"Failed for address: {addr}"

@pytest.mark.asyncio
async def test_children_yes_handling(mock_llm):
    """Test answering 'yes' to children status question."""
    history = [
        ChatMessage(role="assistant", content="Do you have any children?")
    ]
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="123 High St",
        covers_worldwide_assets=True
    )

    # Simple "Yes"
    res1 = await mock_llm.process_turn("Yes", history, state)
    assert res1.proposed_state_updates.get("has_children") is True
    # Should ask for names of children next
    assert "names of your children" in res1.assistant_message.lower()

    # "Yes" with names in same sentence
    res2 = await mock_llm.process_turn("Yes, two children: Lucas and Emma", history, state)
    assert res2.proposed_state_updates.get("has_children") is True
    assert "Lucas" in res2.proposed_state_updates.get("children", [])
    assert "Emma" in res2.proposed_state_updates.get("children", [])

@pytest.mark.asyncio
async def test_standalone_children_names(mock_llm):
    """Test providing children names in follow-up."""
    history = [
        ChatMessage(role="assistant", content="Could you provide the full names of your children?")
    ]
    state = PersonalWishesState(
        full_name="Jane Doe",
        has_children=True
    )

    res = await mock_llm.process_turn("Pierre, Sophie, and Lucas", history, state)
    children = res.proposed_state_updates.get("children", [])
    assert "Pierre" in children
    assert "Sophie" in children
    assert "Lucas" in children

@pytest.mark.asyncio
async def test_decline_optional_sections_no_loop(mock_llm):
    """Test that answering 'no' or 'none' to optional gifts/wishes smoothly progresses without looping."""
    history_gifts = [
        ChatMessage(role="assistant", content="Do you have any specific gifts or bequests you would like to leave?")
    ]
    state_complete_core = PersonalWishesState(
        full_name="Jane Doe",
        home_address="123 High St",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="James Smith", relationship="brother")
    )

    # Say "No" to gifts
    res_gifts = await mock_llm.process_turn("No, none at this time", history_gifts, state_complete_core)
    # Should advance to additional wishes
    assert "additional personal wishes" in res_gifts.assistant_message.lower()

    history_wishes = [
        ChatMessage(role="assistant", content="Are there any additional personal wishes or directives you'd like to include?")
    ]
    # Say "No" to wishes
    res_wishes = await mock_llm.process_turn("No, that is all", history_wishes, state_complete_core)
    # Should complete without getting stuck
    assert "captured" in res_wishes.assistant_message.lower() or "draft" in res_wishes.assistant_message.lower()

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
    state = PersonalWishesState(full_name="Arthur Dent")
    result = await mock_llm.process_turn("Hello again", [], state)
    assert "address" in result.assistant_message.lower()

@pytest.mark.asyncio
async def test_executor_turn_strictly_maps_to_executor_not_full_name(mock_llm):
    """Verify that providing an executor name/relationship never overwrites full_name."""
    history = [
        ChatMessage(
            role="assistant",
            content="Who would you like to appoint as your Executor (the person who will administer your estate and carry out your wishes), and what is their relationship to you?"
        )
    ]
    state = PersonalWishesState(
        full_name="Alice Cooper",
        home_address="10 Downing St",
        covers_worldwide_assets=True,
        has_children=False
    )

    # User enters "My brother James"
    res = await mock_llm.process_turn("My brother James", history, state)
    assert "full_name" not in res.proposed_state_updates
    assert res.proposed_state_updates.get("executor", {}).get("name") == "James"
    assert res.proposed_state_updates.get("executor", {}).get("relationship") == "brother"

@pytest.mark.asyncio
async def test_executor_name_followup_preserves_principal_name(mock_llm):
    """When assistant asks 'What is the full legal name of your brother...', answer must map to executor.name and NOT full_name."""
    history = [
        ChatMessage(
            role="assistant",
            content="What is the full legal name of your brother whom you wish to appoint as executor?"
        )
    ]
    state = PersonalWishesState(
        full_name="Alice Cooper",
        home_address="10 Downing St",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name=None, relationship="brother")
    )

    # User answers just the name
    res = await mock_llm.process_turn("James Smith", history, state)
    assert "full_name" not in res.proposed_state_updates
    assert res.proposed_state_updates.get("executor", {}).get("name") == "James Smith"
    assert res.proposed_state_updates.get("executor", {}).get("relationship") == "brother"

@pytest.mark.asyncio
async def test_short_single_word_executor_name(mock_llm):
    """When user enters a single word name like 'Pierre' for executor."""
    history = [
        ChatMessage(
            role="assistant",
            content="What is the full legal name of your friend whom you wish to appoint as executor?"
        )
    ]
    state = PersonalWishesState(
        full_name="Alice Cooper",
        executor=ExecutorInfo(name=None, relationship="friend")
    )

    res = await mock_llm.process_turn("Pierre", history, state)
    assert "full_name" not in res.proposed_state_updates
    assert res.proposed_state_updates.get("executor", {}).get("name") == "Pierre"
    assert res.proposed_state_updates.get("executor", {}).get("relationship") == "friend"

@pytest.mark.asyncio
async def test_optional_gifts_bare_yes_prompts_for_details(mock_llm):
    """When user replies 'Yes' to gifts question, assistant prompts for details and does not skip."""
    history = [
        ChatMessage(
            role="assistant",
            content="Do you have any specific gifts or bequests you would like to leave to particular individuals (e.g. family heirlooms, jewelry, or cash gifts)? You can also reply 'no' to skip."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("Yes", history, state)
    assert "specific_gifts" not in res.proposed_state_updates
    # Must prompt to describe gifts and not prematurely jump to wishes or finalize
    assert "describe the specific gifts" in res.assistant_message.lower()
    assert "personal wishes" not in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_optional_gifts_affirmative_with_details_extracted(mock_llm):
    """When user replies 'Yes, my vintage watch to my son' or similar, gift is extracted correctly."""
    history = [
        ChatMessage(
            role="assistant",
            content="Do you have any specific gifts or bequests you would like to leave to particular individuals (e.g. family heirlooms, jewelry, or cash gifts)? You can also reply 'no' to skip."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("Yes, my vintage watch to my son", history, state)
    assert "specific_gifts" in res.proposed_state_updates
    gifts = res.proposed_state_updates["specific_gifts"]
    assert len(gifts) == 1
    assert "watch" in gifts[0]["item"].lower()
    assert "son" in gifts[0]["recipient"].lower()
    # Must ask if there are other gifts or ready to move on
    assert "other specific gifts" in res.assistant_message.lower() or "move on" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_optional_gifts_donate_books(mock_llm):
    """When user replies 'I want to donate my books' under gifts question."""
    history = [
        ChatMessage(
            role="assistant",
            content="Do you have any specific gifts or bequests you would like to leave to particular individuals (e.g. family heirlooms, jewelry, or cash gifts)? You can also reply 'no' to skip."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("I want to donate my books", history, state)
    assert "specific_gifts" in res.proposed_state_updates
    gifts = res.proposed_state_updates["specific_gifts"]
    assert len(gifts) == 1
    assert "books" in gifts[0]["item"].lower()
    assert "charity" in gifts[0]["recipient"].lower() or "donation" in gifts[0]["recipient"].lower()

@pytest.mark.asyncio
async def test_optional_wishes_bare_yes_prompts_for_details(mock_llm):
    """When user replies 'Yes' to additional wishes question, assistant prompts for details and does not finalize."""
    history = [
        ChatMessage(
            role="assistant",
            content="Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences? You can also reply 'no' if you are ready to finalize."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("Yes", history, state)
    assert "additional_wishes" not in res.proposed_state_updates
    # Must prompt to describe additional wishes and not finalize
    assert "describe your additional wishes" in res.assistant_message.lower()
    assert "captured" not in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_optional_wishes_affirmative_with_details_extracted(mock_llm):
    """When user replies 'Yes, cremation and ashes scattered in Lake District', wish is extracted."""
    history = [
        ChatMessage(
            role="assistant",
            content="Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences? You can also reply 'no' if you are ready to finalize."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("Yes, cremation and ashes scattered in Lake District", history, state)
    assert "additional_wishes" in res.proposed_state_updates
    wishes = res.proposed_state_updates["additional_wishes"]
    assert len(wishes) == 1
    assert "cremation" in wishes[0].lower()
    assert "lake district" in wishes[0].lower()
    # Must ask if other directives or ready to finalize
    assert "ready to finalize" in res.assistant_message.lower() or "other personal wishes" in res.assistant_message.lower()

@pytest.mark.asyncio
async def test_optional_wishes_donate_books(mock_llm):
    """When user replies 'I want to donate my books' under wishes question."""
    history = [
        ChatMessage(
            role="assistant",
            content="Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences? You can also reply 'no' if you are ready to finalize."
        )
    ]
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name="Theodora", relationship="sister")
    )

    res = await mock_llm.process_turn("I want to donate my books", history, state)
    assert "additional_wishes" in res.proposed_state_updates
    wishes = res.proposed_state_updates["additional_wishes"]
    assert len(wishes) == 1
    assert "donate my books" in wishes[0].lower()

