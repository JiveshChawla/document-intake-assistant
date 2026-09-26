import pytest
from app.services.state_manager import StateManager
from app.models.state import PersonalWishesState, ExecutorInfo

@pytest.fixture
def fresh_manager():
    mgr = StateManager()
    mgr.clear_all()
    return mgr

def test_apply_multi_field_updates(fresh_manager):
    session_id = "test_multi"
    updates = {
        "full_name": "Alice Johnson",
        "home_address": "45 Park Avenue, Bristol",
        "covers_worldwide_assets": True,
        "has_children": False
    }
    state, delta, warnings = fresh_manager.apply_validated_updates(session_id, updates)
    assert state.full_name == "Alice Johnson"
    assert state.home_address == "45 Park Avenue, Bristol"
    assert state.covers_worldwide_assets is True
    assert state.has_children is False
    assert state.children == []
    assert len(warnings) == 0
    assert "full_name" in delta
    assert delta["full_name"] == "Alice Johnson"

def test_correction_overwrites_existing_field(fresh_manager):
    session_id = "test_correction"
    # Initial state
    fresh_manager.apply_validated_updates(session_id, {
        "full_name": "Bob Smith",
        "executor": {"name": "James Smith", "relationship": "brother"}
    })
    
    # User corrects executor to sister Sarah
    updated_state, delta, warnings = fresh_manager.apply_validated_updates(session_id, {
        "executor": {"name": "Sarah Smith", "relationship": "sister"}
    })
    
    assert updated_state.executor.name == "Sarah Smith"
    assert updated_state.executor.relationship == "sister"
    assert delta["executor"]["name"] == "Sarah Smith"
    assert len(warnings) == 0

def test_child_dependency_cleanup(fresh_manager):
    """When has_children becomes False, any prior children names must be cleared."""
    session_id = "test_child_cleanup"
    # First set children
    fresh_manager.apply_validated_updates(session_id, {
        "has_children": True,
        "children": ["Tom", "Jerry"]
    })
    # Later user says actually no children
    state, delta, _ = fresh_manager.apply_validated_updates(session_id, {
        "has_children": False
    })
    assert state.has_children is False
    assert state.children == []
    assert delta["children"] == []

def test_malformed_updates_prevented_without_crashing(fresh_manager):
    session_id = "test_malformed"
    # Establish valid baseline
    fresh_manager.apply_validated_updates(session_id, {"full_name": "Valid Name"})
    
    # Send malformed payload
    state, delta, warnings = fresh_manager.apply_validated_updates(session_id, {
        "covers_worldwide_assets": {"unexpected": "nested_dict"},
        "full_name": ""  # Blank name should not overwrite valid name
    })
    
    # Baseline must be preserved
    assert state.full_name == "Valid Name"
    assert len(warnings) > 0

def test_session_reset(fresh_manager):
    session_id = "test_reset"
    fresh_manager.apply_validated_updates(session_id, {"full_name": "Charles"})
    reset_session = fresh_manager.reset_session(session_id)
    assert reset_session.state.full_name is None
    assert reset_session.state.completion_percentage() == 0
    assert len(reset_session.messages) == 1  # Initial assistant greeting
