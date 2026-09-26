import re
from typing import List, Dict, Any, Optional, Tuple
from app.models.state import PersonalWishesState, GiftItem
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult
from app.services.fixtures import FIXTURES
from app.services.validator import InputValidator
from app.services.llm.prompts import get_last_question_topic

class MockLLMProvider(BaseLLMProvider):
    """
    Intelligent, deterministic, conversational mock LLM provider.
    Runs completely offline with zero external dependencies.
    Accurately handles:
    - Universal free-text input for names and addresses from any country worldwide
    - Multi-field intake in any order
    - Direct conversational answers (e.g., answering 'Yes' to children)
    - Ambiguity detection and intelligent follow-ups without stuck loops
    - Non-destructive corrections
    """
    provider_name = "mock"

    RELATIONSHIPS = [
        "brother", "sister", "wife", "husband", "spouse", "partner", "friend",
        "cousin", "son", "daughter", "mother", "father", "uncle", "aunt",
        "nephew", "niece", "colleague", "lawyer", "solicitor", "attorney",
        "accountant", "neighbour", "neighbor", "step-brother", "step-sister"
    ]

    async def process_turn(
        self,
        user_message: str,
        history: List[ChatMessage],
        current_state: PersonalWishesState,
    ) -> LLMExtractionResult:
        text = user_message.strip()

        # 1. Check for explicit test fixture triggers
        fixture_result = self._check_fixture_triggers(text)
        if fixture_result:
            return fixture_result

        # 2. Determine conversational context from prior assistant question
        last_topic = self._get_last_question_topic(history)

        updates: Dict[str, Any] = {}
        ambiguities: List[str] = []
        acknowledged_parts: List[str] = []

        # 3. Detect and apply corrections (e.g., "Actually, my address is...", "Change executor to...")
        is_correction = bool(re.search(r"\b(actually|change|update|correction|instead of|replace)\b", text, re.IGNORECASE))

        # 4. Extract Full Name
        name = self._extract_name(text, current_state, last_topic)
        if name is not None and last_topic not in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP"]:
            updates["full_name"] = name
            acknowledged_parts.append(f"name as {name}")
        elif last_topic == "NAME" and name is None:
            ambiguities.append(f"The input '{text}' could not be verified as a valid legal name. Please provide your legal full name.")

        # 5. Extract Home Address (universal support for any country)
        address = self._extract_address(text, current_state, last_topic, has_name=(name is not None))
        if address is not None:
            updates["home_address"] = address
            acknowledged_parts.append(f"address as '{address}'")
        elif last_topic == "ADDRESS" and address is None:
            ambiguities.append(f"The input '{text}' does not appear to be a valid residential address. Please provide your physical street and city.")

        # 6. Extract Worldwide Assets Scope
        scope, scope_ambiguity = self._extract_asset_scope(text, last_topic)
        if scope_ambiguity:
            ambiguities.append(scope_ambiguity)
        elif scope is not None:
            updates["covers_worldwide_assets"] = scope
            scope_desc = "worldwide asset coverage" if scope else "domestic-only asset coverage"
            acknowledged_parts.append(scope_desc)

        # 7. Extract Children & Children Names
        has_children, children_names, children_ambiguity = self._extract_children(
            text, current_state, last_topic
        )
        if children_ambiguity:
            ambiguities.append(children_ambiguity)
        if has_children is not None:
            updates["has_children"] = has_children
            if not has_children:
                updates["children"] = []
                acknowledged_parts.append("that you do not have children")
            else:
                acknowledged_parts.append("that you have children")
                if children_names:
                    updates["children"] = children_names
                    acknowledged_parts.append(f"children: {', '.join(children_names)}")

        # Standalone children names if answering "What are the names of your children?"
        if "has_children" not in updates and (last_topic == "CHILDREN_NAMES" or (current_state.has_children is True and not current_state.children)):
            standalone_names = self._extract_standalone_children(text)
            if standalone_names:
                updates["children"] = standalone_names
                acknowledged_parts.append(f"children: {', '.join(standalone_names)}")

        # 8. Extract Executor details
        executor_update, exec_ambiguity = self._extract_executor(text, current_state, last_topic)
        if exec_ambiguity:
            ambiguities.append(exec_ambiguity)
        if executor_update:
            updates["executor"] = executor_update
            if executor_update.get("name") and executor_update.get("relationship"):
                acknowledged_parts.append(
                    f"executor as {executor_update['name']} ({executor_update['relationship']})"
                )
            elif executor_update.get("name"):
                acknowledged_parts.append(f"executor name as {executor_update['name']}")
            elif executor_update.get("relationship"):
                acknowledged_parts.append(f"executor relationship as {executor_update['relationship']}")

        # 9. Extract Specific Gifts
        gifts, gifts_declined, pending_gift_details = self._extract_gifts(text, last_topic)
        just_added_gift = False
        if gifts:
            existing_gifts = list(current_state.specific_gifts or [])
            updated_gifts = existing_gifts + gifts
            updates["specific_gifts"] = [g.model_dump() for g in updated_gifts]
            just_added_gift = True
            for g in gifts:
                acknowledged_parts.append(f"gift of '{g.item}' to {g.recipient}")
        elif gifts_declined:
            acknowledged_parts.append("that you have no specific gifts to designate at this time")

        # 10. Extract Additional Wishes
        wishes, wishes_declined, pending_wish_details = self._extract_additional_wishes(text, last_topic)
        just_added_wish = False
        if wishes:
            existing_wishes = list(current_state.additional_wishes or [])
            updated_wishes = existing_wishes + wishes
            updates["additional_wishes"] = updated_wishes
            just_added_wish = True
            for w in wishes:
                acknowledged_parts.append(f"additional wish: '{w}'")
        elif wishes_declined:
            acknowledged_parts.append("no additional personal wishes to add")

        # 10.5 Validate proposed updates against strict schema
        validated_updates, rejections = InputValidator.validate_proposed_updates(updates, text)
        if rejections:
            ambiguities.extend(rejections)
        updates = validated_updates

        # 11. Simulate future state to compute next question
        simulated_state = self._simulate_state(current_state, updates)

        # 12. Compose intelligent conversational assistant message
        assistant_message = self._compose_response(
            text=text,
            acknowledged_parts=acknowledged_parts,
            ambiguities=ambiguities,
            simulated_state=simulated_state,
            history=history,
            last_topic=last_topic,
            gifts_declined=gifts_declined,
            pending_gift_details=pending_gift_details,
            just_added_gift=just_added_gift,
            wishes_declined=wishes_declined,
            pending_wish_details=pending_wish_details,
            just_added_wish=just_added_wish,
        )

        return LLMExtractionResult(
            assistant_message=assistant_message,
            proposed_state_updates=updates,
            ambiguities=ambiguities,
            confidence=0.95,
            raw_model_response=f"[MOCK_INFERENCE] Extracted {len(updates)} updates, {len(ambiguities)} ambiguities."
        )

    # -------------------------------------------------------------
    # Context Topic Detection
    # -------------------------------------------------------------
    def _get_last_question_topic(self, history: List[ChatMessage]) -> Optional[str]:
        """Finds what question the assistant asked in the latest turn."""
        return get_last_question_topic(history)

    # -------------------------------------------------------------
    # Extraction Helpers
    # -------------------------------------------------------------
    def _extract_name(
        self, text: str, current_state: PersonalWishesState, last_topic: Optional[str]
    ) -> Optional[str]:
        # STRICT GUARD 1: If current turn is about EXECUTOR, GIFTS, or WISHES, NEVER extract principal full_name!
        if last_topic in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP", "GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES", "WISHES", "WISHES_DETAILS"]:
            if not re.search(r"\b(change my name to|update my name to)\b", text, re.IGNORECASE):
                return None

        # STRICT GUARD 2: If current_state.full_name is already confirmed, ONLY allow explicit corrections!
        if current_state.full_name is not None and len(current_state.full_name.strip()) > 0:
            match_correction = re.search(
                r"(?:actually|please)?\s*(?:change my name to|update my name to|my name is actually)\s+([A-Za-zÀ-ÿ\s\-\'\.]+?)(?=\s+(?:living|residing|live|reside|from|at|and|,|\.|$))",
                text,
                re.IGNORECASE
            )
            if match_correction:
                return self._clean_name(match_correction.group(1).strip())
            return None

        # Explicit name declaration patterns (for initial intake)
        patterns = [
            r"(?:actually|please)?\s*(?:change my name to|update my name to)\s+([A-Za-zÀ-ÿ\s\-\'\.]+?)(?=\s+(?:living|residing|live|reside|from|at|and|,|\.|$))",
            r"(?:my name is|i am|i'm|this is)\s+([A-Za-zÀ-ÿ\s\-\'\.]+?)(?=\s+(?:living|residing|live|reside|from|at|and|,|\.|$))",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                cand = m.group(1).strip()
                # Exclude verb phrases like "i am choosing...", "i am appointing..."
                if re.search(r"\b(choosing|appointing|leaving|giving|want|wishing)\b", cand, re.IGNORECASE):
                    continue
                cand = self._clean_name(cand)
                if cand:
                    return cand

        # Contextual: Assistant asked for user's full name
        if (last_topic == "NAME" or (not current_state.full_name and len(current_state.get_missing_fields()) >= 5)):
            clean_text = text.strip()
            clean_text = re.sub(r"^(?:hello|hi|hey|sure|it is|it's|my name is|i am|i'm)\s+", "", clean_text, flags=re.IGNORECASE).strip()
            if re.search(r"\s+(?:living|residing|live|at)\s+", clean_text, re.IGNORECASE):
                cand = re.split(r"\s+(?:living|residing|live|at)\b", clean_text, flags=re.IGNORECASE)[0].strip().rstrip(",")
            else:
                cand = clean_text.split(",")[0].strip().rstrip(".")
            
            cand = self._clean_name(cand)
            if cand and not re.search(r"\b(yes|no|worldwide|children|executor|brother|sister)\b", cand, re.IGNORECASE):
                return cand

        return None

    def _clean_name(self, name_str: str) -> Optional[str]:
        n = re.sub(r"^(?:mr\.|mrs\.|ms\.|dr\.|prof\.)\s*", "", name_str.strip(), flags=re.IGNORECASE)
        n = n.rstrip(".,")
        # Remove trailing connectors
        n = re.split(r"\s+(?:and|who|with)\b", n, flags=re.IGNORECASE)[0].strip()
        parts = n.split()
        if len(parts) >= 1 and len(n) >= 2:
            is_valid, _ = InputValidator.validate_name(n)
            if is_valid:
                return n
        return None

    def _extract_address(
        self, text: str, current_state: PersonalWishesState, last_topic: Optional[str], has_name: bool = False
    ) -> Optional[str]:
        # STRICT GUARD: If current turn is about EXECUTOR, GIFTS, or WISHES, NEVER extract address unless explicit correction!
        if last_topic in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP", "GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES", "WISHES", "WISHES_DETAILS"]:
            if not re.search(r"\b(change my address to|update my address to)\b", text, re.IGNORECASE):
                return None

        # Explicit patterns
        patterns = [
            r"(?:actually|please)?\s*(?:change my address to|update my address to)\s+([^.]+)",
            r"(?:living at|residing at|live at|reside at|residing in|address is|home address is|my address is)\s+([^,.\n]+(?:,[^,.\n]+)*)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                addr = m.group(1).strip().rstrip(".,")
                # Avoid capturing trailing multi-field statements
                addr = re.split(r"\s+(?:and\s+(?:i\s+want|i\s+don't|worldwide|no\s+children|my\s+executor)|worldwide|no\s+kids)\b", addr, flags=re.IGNORECASE)[0].strip()
                if len(addr) >= 4:
                    is_valid, _ = InputValidator.validate_address(addr)
                    if is_valid:
                        return addr

        # Contextual: Assistant asked for residential address
        if last_topic == "ADDRESS":
            # If user message contains address directly
            candidate = text.strip()
            # Strip phrases like "I live at", "My address is"
            candidate = re.sub(r"^(?:i live at|my address is|it's|it is|sure,|currently at)\s+", "", candidate, flags=re.IGNORECASE).strip()
            # Split off any subsequent clauses if user provided multi-field info
            candidate = re.split(r"\s+(?:and\s+(?:i\s+want|worldwide|i\s+have|no\s+kids|my\s+executor)|worldwide)\b", candidate, flags=re.IGNORECASE)[0].strip().rstrip(".,")
            if len(candidate) >= 4 and not re.search(r"\b(yes|no|none|cancel)\b", candidate, re.IGNORECASE):
                is_valid, _ = InputValidator.validate_address(candidate)
                if is_valid:
                    return candidate

        # Multi-field fallback: if text has "10 Downing St" or digits followed by text with comma
        if re.search(r"\b\d+\s+[^,]+(?:,[^,]+)+", text):
            m = re.search(r"\b\d+\s+[^,]+(?:,[^,]+)+", text)
            if m:
                cand = m.group(0).strip().rstrip(".,")
                cand = re.split(r"\s+(?:and|worldwide)\b", cand, flags=re.IGNORECASE)[0].strip()
                is_valid, _ = InputValidator.validate_address(cand)
                if is_valid:
                    return cand

        return None

    def _extract_asset_scope(self, text: str, last_topic: Optional[str]) -> Tuple[Optional[bool], Optional[str]]:
        t = text.lower()
        
        # Ambiguity check: user expresses hesitation / doubt regarding foreign property
        if re.search(r"\b(property abroad|foreign property|house in|condo in|property overseas|assets in [a-z]+)\b", t) and re.search(r"\b(not sure|maybe|perhaps|don't know|depends)\b", t):
            return None, "Asset scope is ambiguous: You mentioned foreign property with uncertainty. Please confirm whether the document should cover worldwide assets or domestic only."

        # Worldwide indicators
        if re.search(r"\b(worldwide|worldwide assets|cover worldwide|all assets|global|international|everywhere|both domestic and foreign|all of them|everything)\b", t):
            return True, None

        # Domestic indicators
        if re.search(r"\b(domestic|domestic only|only domestic|just domestic|local only|only local|home country only|only in (?:the )?[a-z]+)\b", t):
            return False, None

        # Contextual response when asked about worldwide assets
        if last_topic == "WORLDWIDE":
            if re.search(r"\b(yes|yeah|yep|sure|worldwide|all|everything)\b", t):
                return True, None
            if re.search(r"\b(no|nope|domestic|local|just domestic|only domestic)\b", t):
                return False, None

        return None, None

    def _extract_children(
        self, text: str, current_state: PersonalWishesState, last_topic: Optional[str]
    ) -> Tuple[Optional[bool], Optional[List[str]], Optional[str]]:
        t = text.lower()

        # STRICT GUARD 1: If current turn is about GIFTS, WISHES, or EXECUTOR, NEVER extract children status unless explicitly discussing children!
        if last_topic in ["GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES", "WISHES", "WISHES_DETAILS", "EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP"]:
            if not re.search(r"\b(children|child|kids)\b", t):
                return None, None, None

        # STRICT GUARD 2: If current_state.has_children is already set, do not alter it unless explicit correction!
        if current_state.has_children is not None:
            if not re.search(r"\b(actually|change|correction|update)\b", t):
                return None, None, None

        # Negative phrases (no children)
        if re.search(r"\b(no children|don't have (?:any )?children|do not have (?:any )?children|no kids|haven't got (?:any )?children|zero children|without children|not have (?:any )?children|have no children|no child)\b", t):
            return False, [], None

        # Contextual negative when asked "Do you have any children?"
        if last_topic == "CHILDREN_STATUS":
            if re.search(r"^(?:no|nope|nah|none|not yet|i don't|no i don't|zero)$", t) or re.search(r"\b(no,?\s+i\s+don't|no children)\b", t):
                return False, [], None

        # Positive indicators
        has_pos = bool(
            re.search(r"\b(have children|have kids|have a son|have a daughter|have two children|have three children|have \d+ children|my children|my son|my daughter|two children|three children)\b", t)
            or (last_topic == "CHILDREN_STATUS" and re.search(r"\b(yes|yeah|yep|yes i do|sure|i do|indeed|yes,?\s+\d+)\b", t))
        )

        if has_pos:
            # Check if names are also provided in this turn
            names = []
            # Look for names after "named", "called", ":", or "e.g."
            match_named = re.search(r"(?:named|called|children are|kids are|two:|three:)\s+([A-Za-zÀ-ÿ\s,\&and]+)", text, re.IGNORECASE)
            if match_named:
                raw = match_named.group(1).strip().rstrip(".,")
                names = self._parse_names_list(raw)
            elif last_topic == "CHILDREN_STATUS" and re.search(r"(?:yes,?\s+)(?:two|three|\d+)?\s*([A-Za-zÀ-ÿ\s,\&and]+)", text, re.IGNORECASE):
                # e.g., "Yes, John and Mary"
                after_yes = re.sub(r"^(?:yes|yeah|yep|i do),?\s*(?:two|three|\d+)?\s*(?:children|kids)?\s*(?:named|called|:)?\s*", "", text, flags=re.IGNORECASE).strip()
                if after_yes and len(after_yes) > 2 and not re.search(r"\b(worldwide|executor|address)\b", after_yes, re.IGNORECASE):
                    names = self._parse_names_list(after_yes)

            return True, names, None

        return None, None, None

    def _extract_standalone_children(self, text: str) -> Optional[List[str]]:
        """Parses children names from a direct response."""
        clean = re.sub(r"^(?:their names are|they are|they're called|named|my children are)\s+", "", text.strip(), flags=re.IGNORECASE).rstrip(".,")
        names = self._parse_names_list(clean)
        return names if names else None

    def _parse_names_list(self, raw_str: str) -> List[str]:
        raw = re.split(r",\s*|\s+and\s+|\s*\&\s*", raw_str)
        names = []
        for p in raw:
            cleaned = p.strip().rstrip(".,")
            # Remove descriptors like "my son", "my daughter" and connectives "and", "&"
            cleaned = re.sub(r"^(?:and|&)\s+", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"^(?:my\s+son|my\s+daughter|son|daughter)\s+", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"^(?:and|&)\s+", "", cleaned, flags=re.IGNORECASE).strip()
            if cleaned and len(cleaned) >= 2 and not re.search(r"\b(yes|no|children|none)\b", cleaned, re.IGNORECASE):
                is_valid, _ = InputValidator.validate_name(cleaned)
                if is_valid:
                    names.append(cleaned)
        return names

    def _extract_executor(
        self, text: str, current_state: PersonalWishesState, last_topic: Optional[str]
    ) -> Tuple[Optional[Dict[str, Optional[str]]], Optional[str]]:
        t = text.lower()
        # STRICT GUARD: If current turn is about GIFTS or WISHES, NEVER extract executor unless explicitly appointing executor!
        if last_topic in ["GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES", "WISHES", "WISHES_DETAILS"]:
            if not re.search(r"\b(executor|personal representative|appoint as executor)\b", t):
                return None, None

        is_executor_turn = (
            last_topic in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP"]
            or bool(re.search(r"\b(executor|appoint|personal representative)\b", t))
            or (current_state.executor is None and any(r in t for r in self.RELATIONSHIPS))
        )

        if not is_executor_turn:
            return None, None

        # 1. Check for relationship in text
        relationship = None
        for rel in self.RELATIONSHIPS:
            if re.search(rf"\b{rel}\b", t):
                relationship = rel
                break

        # 2. Extract name
        name = None
        # Patterns like: "My brother James Smith", "Pierre Dubois, my friend", "sister Sarah Jenkins"
        patterns = [
            r"(?:brother|sister|wife|husband|spouse|partner|friend|cousin|son|daughter|uncle|aunt|colleague|lawyer|solicitor|attorney|accountant|neighbour)\s+(?!as\b|to\b|who\b|is\b)([A-Za-zÀ-ÿ\s\-\'\.]+)",
            r"([A-Za-zÀ-ÿ\s\-\'\.]+)\s+(?:who is my|is my)\s+(?:brother|sister|friend|cousin|partner|wife|husband|colleague)",
            r"([A-Za-zÀ-ÿ\s\-\'\.]+)\s*,\s*my\s+(?:brother|sister|friend|cousin|partner|wife|husband|colleague)",
            r"([A-Za-zÀ-ÿ\s\-\'\.]+)\s*\((?:brother|sister|friend|cousin|partner|wife|husband|colleague)\)",
            r"(?:appoint|executor(?: is)?)\s+(?!my\b|the\b|a\b|an\b)([A-Za-zÀ-ÿ\s\-\'\.]+)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().rstrip(".,")
                cand = re.split(r"\s+(?:and|as|who|for)\b", cand, flags=re.IGNORECASE)[0].strip()
                cand_lower = cand.lower()
                if cand_lower.startswith("as ") or "executor" in cand_lower or cand_lower in ["my", "as", "the", "an", "is", "her", "his", "their", "him"]:
                    continue
                if re.search(r"\b(i want|want|appoint|nominate|would like|choose|have|wish|will)\b", cand_lower):
                    continue
                if len(cand) >= 2:
                    is_valid, _ = InputValidator.validate_name(cand)
                    if is_valid:
                        name = cand
                        break

        # If assistant previously asked specifically for the name ("What is the full name of your [relationship]?")
        if last_topic == "EXECUTOR_NAME":
            clean = re.sub(r"^(?:his name is|her name is|their name is|it is|it's|name is|i choose|appoint)\s+", "", text.strip(), flags=re.IGNORECASE).rstrip(".,")
            if len(clean) >= 2 and not re.search(r"\b(yes|no|none|cancel)\b", clean, re.IGNORECASE):
                is_valid, reason = InputValidator.validate_name(clean)
                if is_valid:
                    name = clean
                else:
                    return None, f"The executor name '{clean}' does not appear to be a valid legal name ({reason}). Please provide their full legal name."

        # If assistant previously asked specifically for relationship ("What is [name]'s relationship to you?")
        if last_topic == "EXECUTOR_RELATIONSHIP":
            clean_rel = text.strip().lower().rstrip(".,")
            clean_rel = re.sub(r"^(?:he is my|she is my|they are my|is my|my)\s+", "", clean_rel, flags=re.IGNORECASE).strip()
            for r in self.RELATIONSHIPS:
                if r in clean_rel:
                    relationship = r
                    break
            if not relationship and len(clean_rel) >= 3:
                is_valid, reason = InputValidator.validate_relationship(clean_rel)
                if is_valid:
                    relationship = clean_rel
                else:
                    return None, f"The relationship '{clean_rel}' is not recognized ({reason}). Please specify their relationship to you (e.g., brother, friend, solicitor)."

        # Contextual direct answer to "Who would you like to appoint as your Executor...?"
        if last_topic == "EXECUTOR_ALL" and not name and not relationship:
            clean = re.sub(r"^(?:i want to appoint|i want|i appoint|appoint|my executor is|it is|it's)\s+", "", text.strip(), flags=re.IGNORECASE).rstrip(".,")
            if len(clean) >= 2 and not re.search(r"\b(yes|no|none|cancel)\b", clean, re.IGNORECASE):
                is_valid, reason = InputValidator.validate_name(clean)
                if is_valid:
                    name = clean
                else:
                    return None, f"The executor name '{clean}' does not appear to be a valid legal name ({reason}). Please provide their full legal name."

        # Check existing executor values for merging
        existing_name = current_state.executor.name if current_state.executor else None
        existing_rel = current_state.executor.relationship if current_state.executor else None

        final_name = name or existing_name
        final_rel = relationship or existing_rel

        # Validate final_name and final_rel if present
        if final_name:
            is_valid_n, n_reason = InputValidator.validate_name(final_name)
            if not is_valid_n:
                return None, f"Executor name '{final_name}' is invalid ({n_reason}). Please provide their full legal name."

        if final_rel:
            is_valid_r, r_reason = InputValidator.validate_relationship(final_rel)
            if not is_valid_r:
                return None, f"Executor relationship '{final_rel}' is invalid ({r_reason}). Please specify their relationship."

        # Check ambiguity cases
        if final_rel and not final_name:
            return {
                "relationship": final_rel,
                "name": None
            }, f"Executor name is missing: You specified your {final_rel}, but not their full legal name."

        if final_name and not final_rel:
            return {
                "name": final_name,
                "relationship": None
            }, f"Executor relationship is missing: You designated {final_name}, but did not specify their relationship to you."

        if final_name or final_rel:
            return {
                "name": final_name,
                "relationship": final_rel
            }, None

        return None, None

    def _extract_gifts(
        self, text: str, last_topic: Optional[str]
    ) -> Tuple[List[GiftItem], bool, bool]:
        """
        Returns:
            - gifts: List of extracted GiftItem
            - gifts_declined: bool (True if user declined gifts)
            - pending_gift_details: bool (True if user answered yes without gift details)
        """
        t = text.strip()
        t_lower = t.lower()

        is_gift_topic = last_topic in ["GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES"]
        has_gift_keywords = bool(re.search(r"\b(gift|gifts|bequeath|bequest|leave my|give my|donate)\b", t_lower))

        if not is_gift_topic and not has_gift_keywords:
            return [], False, False

        # 1. Check if user declines
        if is_gift_topic:
            decline_phrases = r"\b(no gifts|not at this time|no specific gifts|none for now|leave everything to executor|no more gifts|no other gifts|move on|that's all|thats all|that is all|nothing else|skip)\b"
            is_start_no = bool(re.search(r"^(?:no|nope|nah|none|nothing|skip)(?:,.*)?$", t_lower))
            if re.search(decline_phrases, t_lower) or is_start_no:
                # Ensure user isn't actually specifying a gift
                if not re.search(r"\b(give|leave|bequeath|gift|donate|watch|ring|car|house|money|cash|fund|to\s+[a-z]+)\b", t_lower):
                    return [], True, False

        # 2. Check for bare affirmative (user says "Yes" without describing gifts)
        bare_yes = bool(re.search(
            r"^(?:yes|yeah|yep|sure|i do|yes please|yes i do|yes i have|i have some|certainly|definitely|yes i would|i would)$",
            t_lower
        ) or re.search(r"^(?:yes|yeah|yep|sure),?\s*(?:i have (?:some|a few)|i do|i would like to leave some gifts?)?$", t_lower))

        if bare_yes and is_gift_topic:
            return [], False, True

        # 3. Extract gift items
        gifts: List[GiftItem] = []

        # Remove leading affirmations / conversational filler
        cleaned_text = re.sub(
            r"^(?:yes|yeah|yep|sure|ok|okay),?\s*(?:i want to|i would like to|i'd like to|please)?\s*",
            "",
            t,
            flags=re.IGNORECASE
        ).strip()
        cleaned_text = re.sub(r"^(?:i want to|i'd like to|i wish to|please)\s+", "", cleaned_text, flags=re.IGNORECASE).strip()

        # Split into multiple gift clauses if separated by semicolon or ' and ' followed by gift keyword
        clauses = re.split(r";\s*|\s+and\s+(?=(?:give|leave|bequeath|donate|my\s+|to\s+))", cleaned_text, flags=re.IGNORECASE)

        for clause in clauses:
            clause = clause.strip().rstrip(".,")
            if not clause:
                continue

            gift_found = False

            # Pattern A: (give/leave/bequeath) [item] to [recipient]
            mA = re.search(r"(?:give|leave|bequeath|gift)\s+(?:my\s+)?(.+?)\s+to\s+(.+)", clause, re.IGNORECASE)
            if mA:
                item = self._clean_gift_item(mA.group(1).strip())
                recipient = self._clean_gift_recipient(mA.group(2).strip())
                if item and recipient:
                    gifts.append(GiftItem(item=item, recipient=recipient))
                    gift_found = True

            # Pattern B: [item] to [recipient] (e.g. "my vintage watch to my son", "vintage watch to Lucas")
            if not gift_found:
                mB = re.search(r"^(?:my\s+)?(.+?)\s+to\s+(.+)$", clause, re.IGNORECASE)
                if mB:
                    cand_item = self._clean_gift_item(mB.group(1).strip())
                    cand_recip = self._clean_gift_recipient(mB.group(2).strip())
                    if cand_item and cand_recip and len(cand_item) >= 2 and len(cand_recip) >= 2:
                        gifts.append(GiftItem(item=cand_item, recipient=cand_recip))
                        gift_found = True

            # Pattern C: [recipient] gets/receives/inherits [item]
            if not gift_found:
                mC = re.search(r"(.+?)\s+(?:gets|receives|should receive|inherits)\s+(?:my\s+)?(.+)", clause, re.IGNORECASE)
                if mC:
                    cand_recip = self._clean_gift_recipient(mC.group(1).strip())
                    cand_item = self._clean_gift_item(mC.group(2).strip())
                    if cand_recip and cand_item:
                        gifts.append(GiftItem(item=cand_item, recipient=cand_recip))
                        gift_found = True

            # Pattern D: donate [item] [to recipient (optional)]
            if not gift_found:
                mD = re.search(r"(?:donate|charity)\s+(?:my\s+)?(.+?)(?:\s+to\s+(.+))?$", clause, re.IGNORECASE)
                if mD:
                    cand_item = self._clean_gift_item(mD.group(1).strip())
                    cand_recip = self._clean_gift_recipient(mD.group(2).strip()) if mD.group(2) else "Charity / Donation"
                    if cand_item:
                        gifts.append(GiftItem(item=cand_item, recipient=cand_recip))
                        gift_found = True

            # Pattern E: to [recipient], [item]
            if not gift_found:
                mE = re.search(r"^to\s+([A-Za-zÀ-ÿ\s\-\'\.]+)[,:]\s+(?:my\s+)?(.+)$", clause, re.IGNORECASE)
                if mE:
                    cand_recip = self._clean_gift_recipient(mE.group(1).strip())
                    cand_item = self._clean_gift_item(mE.group(2).strip())
                    if cand_recip and cand_item:
                        gifts.append(GiftItem(item=cand_item, recipient=cand_recip))
                        gift_found = True

        if gifts:
            return gifts, False, False

        # Fallback if in gift topic and text has " to "
        if is_gift_topic and " to " in cleaned_text.lower():
            parts = re.split(r"\s+to\s+", cleaned_text, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                item = self._clean_gift_item(parts[0].strip())
                recip = self._clean_gift_recipient(parts[1].strip())
                if item and recip:
                    return [GiftItem(item=item, recipient=recip)], False, False

        return [], False, False

    def _clean_gift_item(self, item_str: str) -> str:
        s = item_str.strip().rstrip(".,")
        s = re.sub(r"^(?:my|the|a|an)\s+", "", s, flags=re.IGNORECASE).strip()
        if s:
            s = s[0].upper() + s[1:]
        return s

    def _clean_gift_recipient(self, recipient_str: str) -> str:
        s = recipient_str.strip().rstrip(".,")
        s = re.sub(r"^(?:to\s+)", "", s, flags=re.IGNORECASE).strip()
        if s:
            s = s[0].upper() + s[1:]
        return s

    def _extract_additional_wishes(
        self, text: str, last_topic: Optional[str]
    ) -> Tuple[List[str], bool, bool]:
        """
        Returns:
            - wishes: List of extracted wish strings
            - wishes_declined: bool (True if user declined additional wishes)
            - pending_wish_details: bool (True if user answered yes without wish details)
        """
        t = text.strip()
        t_lower = t.lower()

        is_wishes_topic = last_topic in ["WISHES", "WISHES_DETAILS"]
        has_wish_keywords = bool(re.search(
            r"\b(cremat|scatter|funeral|memorial|burial|buried|organ donor|donate organs|wishes|directive|service|plot|ceremony)\b",
            t_lower
        ))

        if not is_wishes_topic and not has_wish_keywords:
            return [], False, False

        # 1. Check if user declines
        if is_wishes_topic:
            decline_phrases = r"\b(no additional wishes|that's all|thats all|that is all|nothing else|no wishes|nothing more|ready to finalize|ready|all good|finalize|skip)\b"
            is_start_no = bool(re.search(r"^(?:no|nope|nah|none|nothing|skip)(?:,.*)?$", t_lower))
            if re.search(decline_phrases, t_lower) or is_start_no:
                if not re.search(r"\b(cremat|scatter|funeral|memorial|burial|buried|organ donor|donate|wishes|directive|service|plot|ceremony)\b", t_lower):
                    return [], True, False

        # 2. Check for bare affirmative (user says "Yes" without describing wishes)
        bare_yes = bool(re.search(
            r"^(?:yes|yeah|yep|sure|i do|yes please|yes i do|yes i have|i have some|certainly|definitely|yes i would|i would)$",
            t_lower
        ) or re.search(r"^(?:yes|yeah|yep|sure),?\s*(?:i have (?:some|a few)|i do|i have additional wishes?)?$", t_lower))

        if bare_yes and is_wishes_topic:
            return [], False, True

        # 3. Extract wishes
        cleaned_text = re.sub(
            r"^(?:yes|yeah|yep|sure|ok|okay),?\s*(?:i want|i wish|please|i would like)?\s*",
            "",
            t,
            flags=re.IGNORECASE
        ).strip()
        cleaned_text = re.sub(r"^(?:additional wish(?:es)?|directive(?:s)?):\s*", "", cleaned_text, flags=re.IGNORECASE).strip()

        # If in wishes topic and user provided substantive directive
        if is_wishes_topic and len(cleaned_text) >= 3:
            if not re.search(r"^(?:hello|hi|hey|thanks|thank you)$", cleaned_text.lower()):
                formatted_wish = cleaned_text.rstrip(".,")
                if formatted_wish:
                    formatted_wish = formatted_wish[0].upper() + formatted_wish[1:]
                    return [formatted_wish], False, False

        # Keyword-based fallback
        patterns = [
            r"(?:i wish to be|i want to be|cremated|ashes scattered|buried|funeral preferences?)\s*([^.]+)?",
            r"(?:additional wish(?:es)?|further wish(?:es)?):\s*([^.]+)",
            r"(?:organ donor|donate organs)\s*([^.]+)?",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                full_match = m.group(0).strip().rstrip(".,")
                return [full_match], False, False

        return [], False, False

    def _simulate_state(self, current: PersonalWishesState, updates: Dict[str, Any]) -> PersonalWishesState:
        data = current.model_dump()
        for k, v in updates.items():
            if k == "executor" and isinstance(v, dict):
                cur_exec = data.get("executor") or {}
                cur_exec.update({ek: ev for ek, ev in v.items() if ev is not None})
                data["executor"] = cur_exec
            else:
                data[k] = v
        return PersonalWishesState(**data)

    def _compose_response(
        self,
        text: str,
        acknowledged_parts: List[str],
        ambiguities: List[str],
        simulated_state: PersonalWishesState,
        history: List[ChatMessage],
        last_topic: Optional[str],
        gifts_declined: bool,
        pending_gift_details: bool,
        just_added_gift: bool,
        wishes_declined: bool,
        pending_wish_details: bool,
        just_added_wish: bool,
    ) -> str:
        parts = []

        # Acknowledgment header
        if acknowledged_parts:
            ack_str = ", ".join(acknowledged_parts)
            parts.append(f"Got it, I've recorded {ack_str}.")
        elif not ambiguities and len(history) == 0:
            parts.append("Hello! I am your Document Intake Assistant. I will help you create your Personal Wishes Document step-by-step.")

        # Ambiguity resolution takes immediate priority
        if ambiguities:
            parts.append("To ensure complete legal accuracy: " + " ".join(ambiguities))
            return "\n\n".join(parts)

        # Sequential follow-up question based on what's missing
        next_question = self._get_next_question(
            state=simulated_state,
            history=history,
            last_topic=last_topic,
            gifts_declined=gifts_declined,
            pending_gift_details=pending_gift_details,
            just_added_gift=just_added_gift,
            wishes_declined=wishes_declined,
            pending_wish_details=pending_wish_details,
            just_added_wish=just_added_wish,
        )
        parts.append(next_question)

        return "\n\n".join(parts)

    def _get_next_question(
        self,
        state: PersonalWishesState,
        history: List[ChatMessage],
        last_topic: Optional[str] = None,
        gifts_declined: bool = False,
        pending_gift_details: bool = False,
        just_added_gift: bool = False,
        wishes_declined: bool = False,
        pending_wish_details: bool = False,
        just_added_wish: bool = False,
    ) -> str:
        if not state.full_name:
            return "Could you please tell me your full legal name?"
        if not state.home_address:
            return f"Thank you, {state.full_name}. What is your current residential home address?"
        if state.covers_worldwide_assets is None:
            return "Should this Personal Wishes Document cover all your worldwide assets, or strictly domestic assets in your country of residence?"
        if state.has_children is None:
            return "Do you have any children?"
        if state.has_children is True and (not state.children or len(state.children) == 0):
            return "Could you provide the full names of your children?"
        if not state.executor or not state.executor.name or not state.executor.relationship:
            if not state.executor:
                return "Who would you like to appoint as your Executor (the person who will administer your estate and carry out your wishes), and what is their relationship to you?"
            elif not state.executor.name:
                return f"What is the full legal name of your {state.executor.relationship} whom you wish to appoint as executor?"
            elif not state.executor.relationship:
                return f"What is {state.executor.name}'s relationship to you (e.g., brother, sister, spouse, friend)?"

        # -------------------------------------------------------------
        # Optional sections: Gifts
        # -------------------------------------------------------------
        if pending_gift_details:
            return "Wonderful. Please describe the specific gifts or bequests and who should receive each one (for example: 'my vintage watch to my son Lucas' or '£5,000 to Cancer Research')."

        if just_added_gift:
            return "Do you have any other specific gifts you would like to add, or are you ready to move on to additional personal wishes? (You can describe another gift or reply 'no' / 'move on')."

        if last_topic == "GIFTS_DETAILS" and not gifts_declined:
            return "Please describe the specific gift item and recipient (for example: 'my vintage watch to my son'), or reply 'no' / 'skip' to move on."

        gifts_resolved = (
            gifts_declined
            or (last_topic == "GIFTS_OR_WISHES" and not just_added_gift)
            or last_topic in ["WISHES", "WISHES_DETAILS"]
            or wishes_declined
            or just_added_wish
            or pending_wish_details
            or (bool(state.specific_gifts and len(state.specific_gifts) > 0) and last_topic not in ["GIFTS", "GIFTS_DETAILS", "GIFTS_OR_WISHES"])
            or any("additional personal wishes" in m.content.lower() or "additional wishes" in m.content.lower() for m in history)
        )

        if not gifts_resolved:
            return "Do you have any specific gifts or bequests you would like to leave to particular individuals (e.g. family heirlooms, jewelry, or cash gifts)? You can also reply 'no' to skip."

        # -------------------------------------------------------------
        # Optional sections: Wishes
        # -------------------------------------------------------------
        if pending_wish_details:
            return "Please go ahead and describe your additional wishes or directives (such as funeral preferences, memorial services, or medical instructions)."

        if just_added_wish:
            return "Do you have any other personal wishes or directives to add, or are you ready to finalize? (Reply with another wish or 'ready' / 'finalize')."

        if last_topic == "WISHES_DETAILS" and not wishes_declined:
            return "Please describe any further directives you would like included, or reply 'ready' / 'finalize' when you are all done."

        wishes_resolved = (
            wishes_declined
            or (bool(state.additional_wishes and len(state.additional_wishes) > 0) and not just_added_wish and last_topic not in ["WISHES", "WISHES_DETAILS"])
        )

        wishes_already_asked = any(
            "additional personal wishes" in m.content.lower() or "additional wishes" in m.content.lower()
            for m in history
        ) or last_topic in ["WISHES", "WISHES_DETAILS"]

        if not wishes_already_asked and not wishes_resolved:
            return "Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences? You can also reply 'no' if you are ready to finalize."

        if not wishes_resolved and last_topic == "WISHES":
            return "Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences? You can also reply 'no' if you are ready to finalize."

        # -------------------------------------------------------------
        # Completed intake
        # -------------------------------------------------------------
        return "All necessary details for your Personal Wishes Document have been captured! Please review the live legal draft preview on the right. You can ask me to change any detail at any time."

    def _check_fixture_triggers(self, text: str) -> Optional[LLMExtractionResult]:
        t = text.upper()
        if "[FIXTURE_VALID]" in t:
            f = FIXTURES["valid_multi_field"]
            return LLMExtractionResult(
                assistant_message=f["response"],
                proposed_state_updates=f["expected_updates"],
                ambiguities=f["ambiguities"],
                confidence=1.0,
                raw_model_response="[FIXTURE_TRIGGERED] valid_multi_field"
            )
        if "[FIXTURE_AMBIGUOUS]" in t:
            f = FIXTURES["ambiguous_executor_missing_name"]
            return LLMExtractionResult(
                assistant_message=f["response"],
                proposed_state_updates=f["expected_updates"],
                ambiguities=f["ambiguities"],
                confidence=0.8,
                raw_model_response="[FIXTURE_TRIGGERED] ambiguous_executor_missing_name"
            )
        if "[FIXTURE_MALFORMED]" in t:
            return LLMExtractionResult(
                assistant_message="I experienced a processing anomaly, but your session state remains secure.",
                proposed_state_updates={"full_name": 12345, "covers_worldwide_assets": "INVALID_TYPE"},
                ambiguities=["Schema validation triggered"],
                confidence=0.1,
                raw_model_response="Malformed output test payload"
            )
        return None
