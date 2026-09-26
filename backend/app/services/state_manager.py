import copy
import logging
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError
from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem
from app.models.chat import ChatMessage
from app.services.validator import InputValidator
from app.db.session import SessionLocal, init_db
from app.db.models import SessionModel, ChatMessageModel, StructuredStateModel

logger = logging.getLogger(__name__)

class MessageList(list):
    """
    Subclass of list that transparently mirrors message additions to SQLite persistence.
    Ensures that calling session.messages.append(msg) automatically saves to the database.
    """
    def __init__(self, session_id: str, state_mgr: Optional["StateManager"] = None, initial_items: Optional[List[ChatMessage]] = None):
        super().__init__(initial_items or [])
        self._session_id = session_id
        self._state_mgr = state_mgr

    def append(self, item: ChatMessage):
        super().append(item)
        if self._state_mgr and self._session_id:
            self._state_mgr.persist_message(self._session_id, item)

    def extend(self, items):
        for item in items:
            self.append(item)

class SessionData:
    def __init__(
        self,
        session_id: str,
        state: Optional[PersonalWishesState] = None,
        messages: Optional[List[ChatMessage]] = None,
        state_mgr: Optional["StateManager"] = None
    ):
        self.session_id = session_id
        self.state = state or PersonalWishesState()
        self.messages = MessageList(session_id, state_mgr, messages or [])
        self.state_history: List[Dict[str, Any]] = []

class StateManager:
    """
    Manages structured state as the application's single source of truth,
    backed by SQLite for persistent data storage across restarts.
    Strictly validates LLM proposed updates before mutating state to ensure
    invariants, prevent hallucinations, and protect against malformed payloads.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        # Ensure database tables exist in SQLite
        try:
            init_db()
        except Exception as e:
            logger.warning(f"Database initialization deferred or encountered: {e}")

    def get_or_create_session(self, session_id: str = "default") -> SessionData:
        """
        Retrieves an active session from memory cache or SQLite database.
        If it does not exist, initializes a new session with initial welcome
        greeting and empty structured state in SQLite.
        """
        if session_id in self._sessions:
            return self._sessions[session_id]

        try:
            with SessionLocal() as db:
                db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
                if db_session:
                    # Hydrate from SQLite
                    loaded_messages = [m.to_pydantic() for m in db_session.messages]
                    loaded_state = db_session.state.to_pydantic() if db_session.state else PersonalWishesState()
                    
                    session = SessionData(
                        session_id=session_id,
                        state=loaded_state,
                        messages=loaded_messages,
                        state_mgr=self
                    )
                    self._sessions[session_id] = session
                    return session

                # Create fresh session in SQLite
                new_db_session = SessionModel(session_id=session_id)
                db.add(new_db_session)
                db.flush()

                # Add initial assistant welcome greeting
                welcome_msg = ChatMessage(
                    role="assistant",
                    content=(
                        "Hello! I am your Document Intake Assistant. I will help you create your "
                        "formal Personal Wishes Document through a quick, guided conversation.\n\n"
                        "To begin, could you please tell me your full legal name?"
                    )
                )
                db_msg = ChatMessageModel.from_pydantic(session_id, welcome_msg)
                db.add(db_msg)

                # Initialize empty structured state
                initial_state = PersonalWishesState()
                db_state = StructuredStateModel(session_id=session_id)
                db_state.update_from_pydantic(initial_state)
                db.add(db_state)

                db.commit()

                session = SessionData(
                    session_id=session_id,
                    state=initial_state,
                    messages=[welcome_msg],
                    state_mgr=self
                )
                self._sessions[session_id] = session
                return session
        except Exception as e:
            logger.error(f"Error accessing SQLite in get_or_create_session: {e}", exc_info=True)
            # Resilient fallback if DB error occurs
            if session_id not in self._sessions:
                welcome_msg = ChatMessage(
                    role="assistant",
                    content=(
                        "Hello! I am your Document Intake Assistant. I will help you create your "
                        "formal Personal Wishes Document through a quick, guided conversation.\n\n"
                        "To begin, could you please tell me your full legal name?"
                    )
                )
                session = SessionData(
                    session_id=session_id,
                    state=PersonalWishesState(),
                    messages=[welcome_msg],
                    state_mgr=self
                )
                self._sessions[session_id] = session
            return self._sessions[session_id]

    def persist_message(self, session_id: str, message: ChatMessage) -> None:
        """Persists a single chat message to the SQLite database."""
        try:
            with SessionLocal() as db:
                db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
                if not db_session:
                    db_session = SessionModel(session_id=session_id)
                    db.add(db_session)
                    db.flush()

                db_msg = ChatMessageModel.from_pydantic(session_id, message)
                db.add(db_msg)
                db.commit()
        except Exception as e:
            logger.error(f"Error persisting message to SQLite for session {session_id}: {e}", exc_info=True)

    def persist_state(self, session_id: str, state: PersonalWishesState) -> None:
        """Persists structured state to the SQLite database."""
        try:
            with SessionLocal() as db:
                db_state = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
                if not db_state:
                    db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
                    if not db_session:
                        db_session = SessionModel(session_id=session_id)
                        db.add(db_session)
                        db.flush()
                    db_state = StructuredStateModel(session_id=session_id)
                    db.add(db_state)

                db_state.update_from_pydantic(state)
                db.commit()
        except Exception as e:
            logger.error(f"Error persisting structured state to SQLite for session {session_id}: {e}", exc_info=True)

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Convenience method to append and persist a message."""
        session = self.get_or_create_session(session_id)
        session.messages.append(message)

    def reset_session(self, session_id: str = "default") -> SessionData:
        """Resets the conversation and structured state in SQLite and in-memory cache."""
        try:
            with SessionLocal() as db:
                db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
                if db_session:
                    db.delete(db_session)
                    db.commit()
        except Exception as e:
            logger.error(f"Error resetting session {session_id} in SQLite: {e}", exc_info=True)

        self._sessions.pop(session_id, None)
        return self.get_or_create_session(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Returns metadata for all persisted sessions in SQLite."""
        try:
            with SessionLocal() as db:
                sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
                result = []
                for s in sessions:
                    result.append({
                        "session_id": s.session_id,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                        "message_count": len(s.messages),
                        "completion_percentage": s.state.completion_percentage if s.state else 0,
                        "full_name": s.state.full_name if s.state else None,
                    })
                return result
        except Exception as e:
            logger.error(f"Error listing sessions from SQLite: {e}", exc_info=True)
            return []

    def clear_all(self) -> None:
        """Clears all sessions, messages, and state from both SQLite and memory cache."""
        try:
            with SessionLocal() as db:
                db.query(ChatMessageModel).delete()
                db.query(StructuredStateModel).delete()
                db.query(SessionModel).delete()
                db.commit()
        except Exception as e:
            logger.error(f"Error clearing database: {e}", exc_info=True)
        self._sessions.clear()

    def apply_validated_updates(
        self,
        session_id: str,
        proposed_updates: Dict[str, Any]
    ) -> Tuple[PersonalWishesState, Dict[str, Any], List[str]]:
        """
        Validates proposed updates against schema invariants and applies them.
        Persists the resulting state into SQLite.
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
                    is_valid, reason = InputValidator.validate_name(str(value) if value is not None else "")
                    if is_valid:
                        working_data["full_name"] = str(value).strip()
                        actual_delta["full_name"] = str(value).strip()
                    else:
                        validation_warnings.append(f"Rejected invalid full_name: {reason}")

                elif field == "home_address":
                    is_valid, reason = InputValidator.validate_address(str(value) if value is not None else "")
                    if is_valid:
                        working_data["home_address"] = str(value).strip()
                        actual_delta["home_address"] = str(value).strip()
                    else:
                        validation_warnings.append(f"Rejected invalid home_address: {reason}")

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
                        clean_children = []
                        for c in value:
                            c_str = str(c).strip()
                            c_valid, c_reason = InputValidator.validate_name(c_str)
                            if c_valid:
                                clean_children.append(c_str)
                            else:
                                validation_warnings.append(f"Rejected invalid child name '{c_str}': {c_reason}")
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
                            n_str = str(value["name"]).strip()
                            n_valid, n_reason = InputValidator.validate_name(n_str)
                            if n_valid:
                                new_exec_data["name"] = n_str
                            else:
                                validation_warnings.append(f"Rejected invalid executor name '{n_str}': {n_reason}")
                        if "relationship" in value and value["relationship"]:
                            r_str = str(value["relationship"]).strip()
                            r_valid, r_reason = InputValidator.validate_relationship(r_str)
                            if r_valid:
                                new_exec_data["relationship"] = r_str
                            else:
                                validation_warnings.append(f"Rejected invalid executor relationship '{r_str}': {r_reason}")
                        
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
                                item_str = str(g["item"]).strip()
                                recip_str = str(g["recipient"]).strip()
                                item_gib, _ = InputValidator.is_gibberish(item_str)
                                recip_gib, _ = InputValidator.is_gibberish(recip_str)
                                if not item_gib and not recip_gib and len(item_str) >= 2 and len(recip_str) >= 2:
                                    validated_gifts.append(GiftItem(item=item_str, recipient=recip_str).model_dump())
                                else:
                                    validation_warnings.append(f"Rejected invalid gift '{item_str}' to '{recip_str}'")
                        working_data["specific_gifts"] = validated_gifts
                        actual_delta["specific_gifts"] = validated_gifts

                elif field == "additional_wishes":
                    if isinstance(value, list):
                        clean_wishes = []
                        for w in value:
                            w_str = str(w).strip()
                            w_gib, _ = InputValidator.is_gibberish(w_str)
                            if not w_gib and len(w_str) >= 3:
                                clean_wishes.append(w_str)
                            else:
                                validation_warnings.append(f"Rejected invalid wish '{w_str}'")
                        working_data["additional_wishes"] = clean_wishes
                        actual_delta["additional_wishes"] = clean_wishes
                    elif isinstance(value, str) and value.strip():
                        w_str = value.strip()
                        w_gib, _ = InputValidator.is_gibberish(w_str)
                        if not w_gib and len(w_str) >= 3:
                            current_wishes = working_data.get("additional_wishes") or []
                            if w_str not in current_wishes:
                                current_wishes.append(w_str)
                            working_data["additional_wishes"] = current_wishes
                            actual_delta["additional_wishes"] = current_wishes
                        else:
                            validation_warnings.append(f"Rejected invalid wish '{w_str}'")

            except (ValidationError, TypeError, ValueError) as err:
                logger.error(f"Validation error for field {field}: {err}")
                validation_warnings.append(f"Rejected update for '{field}': {str(err)}")

        # Validate complete state object
        try:
            new_state = PersonalWishesState(**working_data)
            session.state = new_state
            if actual_delta:
                session.state_history.append(actual_delta)
            
            # Persist updated state to SQLite
            self.persist_state(session_id, new_state)

            return new_state, actual_delta, validation_warnings
        except ValidationError as e:
            logger.critical(f"State integrity violation prevented: {e}")
            validation_warnings.append(f"State mutation rejected: {str(e)}")
            return current_state, {}, validation_warnings

    def set_direct_state(self, session_id: str, new_state: PersonalWishesState) -> PersonalWishesState:
        """Directly overrides state from user manual edit and saves to SQLite."""
        session = self.get_or_create_session(session_id)
        session.state = new_state
        session.state_history.append({"direct_override": new_state.model_dump()})
        self.persist_state(session_id, new_state)
        return session.state

# Global singleton state manager
state_manager = StateManager()
