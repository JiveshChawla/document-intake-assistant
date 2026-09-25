import re
from typing import List, Dict, Any, Optional, Tuple
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult
from app.services.fixtures import FIXTURES

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, high-fidelity mock LLM provider.
    Runs completely offline with zero API keys or external dependencies.
    Accurately handles multi-turn interviews, multi-field intake, corrections,
    ambiguity detection, and intelligent follow-ups.
    """
    provider_name = "mock"

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

        # 2. Parse state updates and ambiguity from user message
        updates: Dict[str, Any] = {}
        ambiguities: List[str] = []
        acknowledged_parts: List[str] = []

        # Parse Full Name
        name = self._extract_name(text, current_state)
        if name is not None:
            updates["full_name"] = name
            acknowledged_parts.append(f"name as {name}")

        # Parse Home Address
        address = self._extract_address(text, current_state)
        if address is not None:
            updates["home_address"] = address
            acknowledged_parts.append(f"address as '{address}'")

        # Parse Worldwide Assets
        scope, scope_ambiguity = self._extract_asset_scope(text)
        if scope_ambiguity:
            ambiguities.append(scope_ambiguity)
        elif scope is not None:
            updates["covers_worldwide_assets"] = scope
            scope_desc = "worldwide asset coverage" if scope else "domestic-only asset coverage"
            acknowledged_parts.append(scope_desc)

        # Parse Children
        has_children, children_names, children_ambiguity = self._extract_children(text)
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

        # If user only provides children names in response to "What are the names of your children?"
        if "has_children" not in updates and current_state.has_children is True:
            if not current_state.children or len(current_state.children) == 0:
                standalone_names = self._extract_standalone_children(text)
                if standalone_names:
                    updates["children"] = standalone_names
                    acknowledged_parts.append(f"children: {', '.join(standalone_names)}")

        # Parse Executor
        executor_update, exec_ambiguity = self._extract_executor(text, current_state)
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

        # Parse Specific Gifts
        gifts = self._extract_gifts(text)
        if gifts:
            existing_gifts = list(current_state.specific_gifts or [])
            # Combine or replace
            updated_gifts = existing_gifts + gifts
            updates["specific_gifts"] = [g.model_dump() for g in updated_gifts]
            for g in gifts:
                acknowledged_parts.append(f"gift of '{g.item}' to {g.recipient}")

        # Parse Additional Wishes
        wishes = self._extract_additional_wishes(text)
        if wishes:
            existing_wishes = list(current_state.additional_wishes or [])
            updated_wishes = existing_wishes + wishes
            updates["additional_wishes"] = updated_wishes
            acknowledged_parts.append(f"additional wish: '{wishes[0]}'")

        # 3. Simulate future state to decide the next intelligent follow-up question
        simulated_state = self._simulate_state(current_state, updates)

        # 4. Generate conversational assistant message
        assistant_message = self._compose_response(
            text=text,
            acknowledged_parts=acknowledged_parts,
            ambiguities=ambiguities,
            simulated_state=simulated_state,
            history=history
        )

        return LLMExtractionResult(
            assistant_message=assistant_message,
            proposed_state_updates=updates,
            ambiguities=ambiguities,
            confidence=0.95,
            raw_model_response=f"[MOCK_INFERENCE] Extracted {len(updates)} updates, {len(ambiguities)} ambiguities."
        )

    # -------------------------------------------------------------
    # Extraction Helpers
    # -------------------------------------------------------------
    def _extract_name(self, text: str, current_state: PersonalWishesState) -> Optional[str]:
        patterns = [
            r"(?:actually|please)?\s*(?:change my name to|update my name to)\s+([A-Za-z\s]+?)(?=\s+(?:living|residing|at|and|,|\.|$))",
            r"(?:my name is|i am|i'm)\s+([A-Za-z\s]+?)(?=\s+(?:living|residing|live|reside|from|at|and|,|\.|$))",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                # Stop at common connectives
                candidate = re.split(r"\s+(?:living|residing|live|reside|from|at|and)\b", candidate, flags=re.IGNORECASE)[0].strip()
                # Exclude relationship / status words
                if candidate and not re.search(r"\b(brother|sister|executor|father|mother|friend|yes|no|none)\b", candidate, re.IGNORECASE):
                    # Ensure at least first and last name or valid name string
                    if len(candidate.split()) >= 1 and len(candidate) >= 2:
                        return candidate
        return None

    def _extract_address(self, text: str, current_state: PersonalWishesState) -> Optional[str]:
        patterns = [
            r"(?:actually|please)?\s*(?:change my address to|update my address to)\s+([^.]+)",
            r"(?:living at|residing at|live at|address is|home address is)\s+([^,.\n]+(?:,[^,.\n]+)*)",
            r"\b(\d+\s+[A-Z][a-zA-Z0-9\s,]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Way|Lane|Ln|Boulevard|Blvd|London|New York|Paris)[^.\n]*)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                addr = m.group(1).strip().rstrip(".,")
                # Avoid capturing entire multi-field sentences
                if " and " in addr.lower():
                    addr = re.split(r"\s+and\s+", addr, flags=re.IGNORECASE)[0]
                if len(addr) > 5:
                    return addr
        return None

    def _extract_asset_scope(self, text: str) -> Tuple[Optional[bool], Optional[str]]:
        t = text.lower()
        if "worldwide" in t:
            if re.search(r"\b(not sure|maybe|perhaps|property abroad but|foreign)\b", t) and not re.search(r"\b(yes|cover worldwide|include worldwide)\b", t):
                return None, "Scope is ambiguous: You mentioned foreign assets or uncertainty. Please confirm if the document should cover worldwide assets or strictly domestic assets."
            return True, None
        if "domestic" in t or "only in the uk" in t or "only domestic" in t or "domestic only" in t or "local assets" in t:
            return False, None
        return None, None

    def _extract_children(self, text: str) -> Tuple[Optional[bool], Optional[List[str]], Optional[str]]:
        t = text.lower()
        # Check negative first
        if re.search(r"\b(no children|don't have (?:any )?children|do not have (?:any )?children|no kids|haven't got (?:any )?children|zero children|without children|not have (?:any )?children)\b", t):
            return False, [], None

        # Check positive (ensuring not negated)
        if re.search(r"\b(have children|have kids|have two children|have three children|have a son|have a daughter|my children|my son|my daughter)\b", t):
            if not re.search(r"\b(don't|not|never|no)\s+(?:have children|have kids)\b", t):
                names = []
                # Extract names if mentioned
                names_match = re.search(r"(?:named|called)\s+([A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+|,\s*[A-Z][a-z]+)*)", text)
                if names_match:
                    raw_names = names_match.group(1)
                    split_names = re.split(r",\s*|\s+and\s+", raw_names)
                    names = [n.strip() for n in split_names if n.strip()]
                return True, names, None

        return None, None, None

    def _extract_standalone_children(self, text: str) -> Optional[List[str]]:
        # e.g., "Emma and Lucas", "Lucas Smith, Emma Smith"
        if re.match(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:,\s*|\s+and\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$", text.strip()):
            parts = re.split(r",\s*|\s+and\s+", text.strip())
            return [p.strip() for p in parts if p.strip()]
        return None

    def _extract_executor(
        self, text: str, current_state: PersonalWishesState
    ) -> Tuple[Optional[Dict[str, Optional[str]]], Optional[str]]:
        t = text.lower()
        # Look for executor context
        is_executor_context = bool(
            re.search(r"\b(executor|appoint|personal representative)\b", t)
            or (current_state.executor is None and re.search(r"\b(brother|sister|spouse|wife|husband|friend|cousin|son|daughter)\b", t))
        )

        if not is_executor_context:
            return None, None

        # Check relationship keywords
        rel_match = re.search(r"\b(brother|sister|wife|husband|spouse|friend|cousin|son|daughter|partner|lawyer|solicitor|father|mother)\b", t)
        relationship = rel_match.group(1) if rel_match else None

        # Check name patterns
        # e.g., "My brother James Smith", "sister Sarah", "friend John Doe", "appoint James Smith as my executor"
        name = None
        patterns = [
            r"(?:brother|sister|wife|husband|spouse|friend|cousin|son|daughter|partner)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"(?:appoint|executor(?: is)?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:who is my|is my)\s+(?:brother|sister|friend|cousin)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                cand = m.group(1).strip()
                if cand.lower() not in ["my", "as", "the", "an", "is", "her", "his", "their"]:
                    name = cand
                    break

        # Check ambiguity cases
        # Case A: Relationship mentioned, but no name (e.g. "I want to appoint my brother as executor")
        if relationship and not name:
            return {
                "relationship": relationship,
                "name": current_state.executor.name if current_state.executor else None,
            }, f"Executor name is missing: You specified your {relationship}, but not their name."

        # Case B: Name mentioned as executor, but relationship missing (e.g. "James Smith is my executor")
        if name and not relationship:
            existing_rel = current_state.executor.relationship if current_state.executor else None
            if not existing_rel:
                return {
                    "name": name,
                    "relationship": None
                }, f"Executor relationship is missing: You designated {name} as executor, but did not specify their relationship to you."
            else:
                return {"name": name, "relationship": existing_rel}, None

        if name or relationship:
            return {
                "name": name or (current_state.executor.name if current_state.executor else None),
                "relationship": relationship or (current_state.executor.relationship if current_state.executor else None)
            }, None

        return None, None

    def _extract_gifts(self, text: str) -> List[Any]:
        from app.models.state import GiftItem
        gifts = []
        patterns = [
            r"(?:give|leave|bequeath)\s+(?:my\s+)?([^,]+?)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:gets|receives|should receive)\s+(?:my\s+)?([^.]+)",
        ]
        for pat in patterns:
            matches = re.finditer(pat, text, re.IGNORECASE)
            for m in matches:
                if pat.startswith(r"(?:give"):
                    item, recipient = m.group(1).strip(), m.group(2).strip()
                else:
                    recipient, item = m.group(1).strip(), m.group(2).strip()
                gifts.append(GiftItem(item=item, recipient=recipient))
        return gifts

    def _extract_additional_wishes(self, text: str) -> List[str]:
        wishes = []
        patterns = [
            r"(?:i wish to be|i want to be|cremated|ashes scattered|buried|funeral preferences?)\s*([^.]+)?",
            r"(?:additional wish(?:es)?|further wish(?:es)?):\s*([^.]+)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                full_match = m.group(0).strip().rstrip(".,")
                wishes.append(full_match)
                break
        return wishes

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
        history: List[ChatMessage]
    ) -> str:
        parts = []

        # Acknowledgment header
        if acknowledged_parts:
            ack_str = ", ".join(acknowledged_parts)
            parts.append(f"Got it, I've recorded {ack_str}.")
        elif not ambiguities and len(history) == 0:
            parts.append("Hello! I am your Document Intake Assistant. I will help you create your Personal Wishes Document step-by-step.")

        # Ambiguity resolution takes priority
        if ambiguities:
            parts.append("To ensure everything is accurate: " + " ".join(ambiguities))
            return "\n\n".join(parts)

        # Intelligent sequential follow-up question
        next_question = self._get_next_question(simulated_state)
        parts.append(next_question)

        return "\n\n".join(parts)

    def _get_next_question(self, state: PersonalWishesState) -> str:
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
                return f"What is the full name of your {state.executor.relationship} whom you wish to appoint as executor?"
            elif not state.executor.relationship:
                return f"What is {state.executor.name}'s relationship to you (e.g., brother, sister, spouse, friend)?"
        if not state.specific_gifts or len(state.specific_gifts) == 0:
            return "Do you have any specific gifts or bequests you would like to leave to particular individuals (e.g. family heirlooms, jewelry, or specific cash gifts)?"
        if not state.additional_wishes or len(state.additional_wishes) == 0:
            return "Are there any additional personal wishes or directives you'd like to include, such as funeral arrangements or memorial preferences?"

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
            # Emulates malformed output to test error resilience
            return LLMExtractionResult(
                assistant_message="I experienced a processing anomaly, but your session state remains secure.",
                proposed_state_updates={"full_name": 12345, "covers_worldwide_assets": "INVALID_TYPE"},
                ambiguities=["Schema validation triggered"],
                confidence=0.1,
                raw_model_response="Malformed output test payload"
            )
        return None
