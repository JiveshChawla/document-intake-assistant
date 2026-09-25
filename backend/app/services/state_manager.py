import copy
import logging
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem
from app.models.chat import ChatMessage

logger = logging.getLogger(__name__)

class SessionData:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = PersonalWishesState()
        self.messages: List[ChatMessage] = []
        self.state_history: List[Dict[str, Any]] = []

class StateManager:
    """
    Manages structured state as the application's single source of truth.
    Strictly validates LLM proposed updates before mutating state to ensure
    invariants, prevent hallucinations, and protect against malformed payloads.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def get_or_create_session(self, session_id: str = "default") -> SessionData:
        if session_id not in self._sessions:
            session = SessionData(session_id)
            # Add initial welcome message
            welcome_msg = ChatMessage(
                role="assistant",
                content=(
                    "Hello! I am your Document Intake Assistant. I will help you create your "
                    "formal Personal Wishes Document through a quick, guided conversation.\n\n"
                    "To begin, could you please tell me your full legal name?"
                )
            )
            session.messages.append(welcome_msg)
            self._sessions[session_id] = session
        return self._sessions[session_id]

    def reset_session(self, session_id: str = "default") -> SessionData:
        """Resets the conversation and structured state to initial clean state."""
        self._sessions.pop(session_id, None)
        return self.get_or_create_session(session_id)

    def apply_validated_updates(
        self,
        session_id: str,
        proposed_updates: Dict[str, Any]
    ) -> Tuple[PersonalWishesState, Dict[str, Any], List[str]]:
        """
        Validates proposed updates against schema invariants and applies them.
        Returns:
            - updated PersonalWishesState
            - state_delta (only the actual changes)
            - list of validation errors or warnings if any
        """
        session = self.get_or_create_session(session_id)
        current_state = session.state
        validation_warnings: List[str] = []
        actual_delta: Dict[str, Any] = {}

        if not proposed_updates:
            return current_state, {}, []

        # Create working copy of current data dictionary
        working_data = current_state.model_dump()

        for field, value in proposed_updates.items():
            if value is None:
                continue

            try:
                if field == "full_name":
                    if isinstance(value, str) and value.strip():
                        working_data["full_name"] = value.strip()
                        actual_delta["full_name"] = value.strip()
                    else:
                        validation_warnings.append(f"Invalid full_name format: {value}")

                elif field == "home_address":
                    if isinstance(value, str) and value.strip():
                        working_data["home_address"] = value.strip()
                        actual_delta["home_address"] = value.strip()
                    else:
                        validation_warnings.append(f"Invalid home_address format: {value}")

                elif field == "covers_worldwide_assets":
                    if isinstance(value, bool):
                        working_data["covers_worldwide_assets"] = value
                        actual_delta["covers_worldwide_assets"] = value
                    elif isinstance(value, str):
                        v_lower = value.strip().lower()
                        if v_lower in ["true", "yes", "worldwide"]:
                            working_data["covers_worldwide_assets"] = True
                            actual_delta["covers_worldwide_assets"] = True
                        elif v_lower in ["false", "no", "domestic", "domestic only"]:
                            working_data["covers_worldwide_assets"] = False
                            actual_delta["covers_worldwide_assets"] = False
                        else:
                            validation_warnings.append(f"Invalid covers_worldwide_assets value: {value}")
                    else:
                        validation_warnings.append(f"Invalid covers_worldwide_assets value: {value}")

                elif field == "has_children":
                    bool_val = bool(value) if not isinstance(value, str) else value.lower() in ["true", "yes"]
                    working_data["has_children"] = bool_val
                    actual_delta["has_children"] = bool_val
                    # Consistency check: If user has no children, clear any leftover children array
                    if not bool_val:
                        working_data["children"] = []
                        actual_delta["children"] = []

                elif field == "children":
                    if isinstance(value, list):
                        clean_children = [str(c).strip() for c in value if str(c).strip()]
                        working_data["children"] = clean_children
                        if clean_children:
                            working_data["has_children"] = True
                            actual_delta["has_children"] = True
                        actual_delta["children"] = clean_children
                    else:
                        validation_warnings.append(f"Invalid children list format: {value}")

                elif field == "executor":
                    # Partial or complete executor update
                    existing_exec = working_data.get("executor") or {}
                    if isinstance(value, dict):
                        new_exec_data = copy.deepcopy(existing_exec)
                        if "name" in value and value["name"]:
                            new_exec_data["name"] = str(value["name"]).strip()
                        if "relationship" in value and value["relationship"]:
                            new_exec_data["relationship"] = str(value["relationship"]).strip()
                        
                        # Validate through Pydantic ExecutorInfo model
                        validated_exec = ExecutorInfo(**new_exec_data)
                        working_data["executor"] = validated_exec.model_dump()
                        actual_delta["executor"] = validated_exec.model_dump()
                    else:
                        validation_warnings.append(f"Executor must be an object, received: {type(value)}")

                elif field == "specific_gifts":
                    if isinstance(value, list):
                        validated_gifts = []
                        for g in value:
                            if isinstance(g, dict) and "item" in g and "recipient" in g:
                                validated_gifts.append(GiftItem(item=str(g["item"]).strip(), recipient=str(g["recipient"]).strip()).model_dump())
                        working_data["specific_gifts"] = validated_gifts
                        actual_delta["specific_gifts"] = validated_gifts

                elif field == "additional_wishes":
                    if isinstance(value, list):
                        clean_wishes = [str(w).strip() for w in value if str(w).strip()]
                        working_data["additional_wishes"] = clean_wishes
                        actual_delta["additional_wishes"] = clean_wishes
                    elif isinstance(value, str) and value.strip():
                        current_wishes = working_data.get("additional_wishes") or []
                        if value.strip() not in current_wishes:
                            current_wishes.append(value.strip())
                        working_data["additional_wishes"] = current_wishes
                        actual_delta["additional_wishes"] = current_wishes

            except (ValidationError, TypeError, ValueError) as err:
                logger.error(f"Validation error for field {field}: {err}")
                validation_warnings.append(f"Rejected update for '{field}': {str(err)}")

        # Validate complete state object
        try:
            new_state = PersonalWishesState(**working_data)
            session.state = new_state
            if actual_delta:
                session.state_history.append(actual_delta)
            return new_state, actual_delta, validation_warnings
        except ValidationError as e:
            logger.critical(f"State integrity violation prevented: {e}")
            validation_warnings.append(f"State mutation rejected: {str(e)}")
            return current_state, {}, validation_warnings

    def set_direct_state(self, session_id: str, new_state: PersonalWishesState) -> PersonalWishesState:
        """Directly overrides state from user manual edit."""
        session = self.get_or_create_session(session_id)
        session.state = new_state
        session.state_history.append({"direct_override": new_state.model_dump()})
        return session.state

# Global singleton state manager
state_manager = StateManager()
