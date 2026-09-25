import pytest
from pydantic import ValidationError
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem

def test_initial_state_has_explicit_unknowns():
    """Verify that unknown/unconfirmed fields default explicitly to None or empty collections."""
    state = PersonalWishesState()
    assert state.full_name is None
    assert state.home_address is None
    assert state.covers_worldwide_assets is None
    assert state.has_children is None
    assert state.children is None
    assert state.executor is None
    assert state.specific_gifts == []
    assert state.additional_wishes == []
    assert state.completion_percentage() == 0
    assert not state.is_complete()

def test_missing_fields_reporting():
    """Verify that get_missing_fields correctly enumerates uncaptured core fields."""
    state = PersonalWishesState()
    missing = state.get_missing_fields()
    assert "Full Name" in missing
    assert "Home Address" in missing
    assert "Worldwide Assets Scope" in missing
    assert "Children Status" in missing
    assert "Executor Details" in missing

def test_executor_partial_completeness():
    """Verify missing field reports when executor has relationship but no name."""
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="123 High St",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorInfo(name=None, relationship="brother")
    )
    missing = state.get_missing_fields()
    assert "Executor Name" in missing
    assert "Executor Details" not in missing
    assert not state.is_complete()

def test_complete_state_evaluation():
    """Verify is_complete() is True only when all mandatory intake questions are satisfied."""
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="123 High St, London",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Emma Doe", "Lucas Doe"],
        executor=ExecutorInfo(name="James Smith", relationship="brother")
    )
    assert state.is_complete()
    assert state.completion_percentage() == 100
    assert len(state.get_missing_fields()) == 0

def test_children_consistency():
    """Verify children list logic for has_children=False."""
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="123 High St, London",
        covers_worldwide_assets=False,
        has_children=False,
        executor=ExecutorInfo(name="James Smith", relationship="brother")
    )
    assert state.is_complete()
    assert state.completion_percentage() == 100

def test_invalid_types_raise_validation_error():
    """Verify strict type enforcement for structured state."""
    with pytest.raises(ValidationError):
        PersonalWishesState(covers_worldwide_assets="NOT_A_BOOLEAN_VALUE")
