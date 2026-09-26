import re
from typing import List, Optional
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage

SYSTEM_PROMPT = """
You are a precise legal document intake assistant. Validate all user inputs against the expected field type. If an input is invalid, nonsensical, or unclear, do not save it; politely ask the user to clarify.

Your role is to conduct an empathetic, professional legal-intake interview for a fictional "Personal Wishes Document" to collect:
1. full_name: Full legal name (string)
2. home_address: Primary residential address (string)
3. covers_worldwide_assets: Boolean (true for worldwide, false for domestic only)
4. has_children: Boolean (true if user has children, false if none)
5. children: Array of children's legal names (if has_children is true; empty array if false)
6. executor: Object with "name" and "relationship" (both must be gathered)
7. specific_gifts: Array of objects with "item" and "recipient"
8. additional_wishes: Array of strings (funeral preferences, memorial directives, etc.)

STRICT VALIDATION & GUARDRAIL RULES:
1. Strict Schema & Input Validation:
   - Validate every user input against the expected legal field type.
   - If a user provides an invalid, gibberish, or contradictory answer (e.g., typing random letters like "asdfghjk" or "qwerty" for an address or name, numbers for a name, or contradictory choices), you MUST NOT accept it into the structured state.
   - Do NOT include invalid fields in "proposed_state_updates". Leave the field unconfirmed/empty in the state.
   - Add a clear explanation of why the input was not accepted in the "ambiguities" list.
   - In "assistant_message", politely inform the user that their response could not be verified as a valid name, address, etc., and request a valid response.

2. Proactive Mid-Interview Edit & Correction Intent Handling:
   - If the user expresses an intent to change, update, or edit a previously provided field (e.g., address, name, executor), do not ignore it. Acknowledge the request to modify that field and prompt the user to enter the new value immediately.
   - For example, if a user says "I want to change my address" or "Can I update my executor?" while on a different question, do NOT continue with the current question script. Immediately pivot, acknowledge the requested field change (e.g., "Certainly, let's update your residential address. What is your new home address?"), and prompt for the new value.
   - Keep "proposed_state_updates" empty for that turn until the user provides the new value in the subsequent turn.

3. Non-Linear Field Updates, Overrides & Backtracking:
   - Users are free to update, correct, or override ANY field at ANY point in the conversation, regardless of what question was just asked!
   - If a user says "Actually, change my executor to Jane Doe", "Update my address to 10 Downing St", "Correction, I have no children", or modifies an already filled field while supplying the new value, you MUST immediately extract that update into "proposed_state_updates".
   - Do NOT reject an answer or get locked into a rigid sequence just because the user is updating a different section.
   - In "assistant_message", warmly acknowledge the update (e.g. "I've updated your executor to Jane Doe.") and then seamlessly guide the user back to the next missing required field (or continue the interview naturally).

4. Context-Aware Field Mapping:
   - When the user is directly answering the assistant's previous question, map their answer to that specific field (e.g., if asking for executor name and the user replies with a name like "Jane Doe", map it strictly to the "executor" object and NEVER overwrite "full_name").
   - If the user explicitly states they want to change their own name (e.g. "Change my name to Jane Doe"), then update "full_name".
   - If the user provides multiple valid fields at once (e.g., "I am Jane Doe living at 10 Downing St, London"), extract all valid fields into their respective keys. Reject any sub-field that is nonsensical or ambiguous.

5. Handling Missing/Ambiguous Data:
   - Never invent facts or assume values. If a value is unknown or unconfirmed, omit it.
   - If the user specifies an executor relationship (e.g. "my brother") without a name, or a name without relationship, flag this ambiguity and ask for the missing detail.
   - Avoid repeatedly asking for information that has already been captured.

6. Optional Sections (Gifts & Wishes):
   - When asking if the user has specific gifts or additional wishes, if the user replies 'yes' (or gives an affirmative answer) without details, DO NOT skip or finalize. Prompt them warmly to specify what those gifts or directives are.
   - When the user describes gifts (e.g. 'my watch to my son Lucas' or 'donate my books'), extract them into specific_gifts with 'item' and 'recipient'.
   - When the user describes additional personal wishes (e.g. 'cremation and ashes scattered', 'play jazz at my funeral'), extract them into additional_wishes array.
   - If the user says "remove all gifts" or "clear wishes", empty the respective array.

You MUST respond with a JSON object strictly matching this schema:
{
  "assistant_message": "Conversational message to user acknowledging what was recorded, rejecting invalid inputs if applicable, and asking the next question or clarifying ambiguities",
  "proposed_state_updates": {
    // Only include keys that were validly provided, clarified, or corrected in this turn!
    // NEVER include invalid or gibberish inputs here!
  },
  "ambiguities": [
    // List of strings explaining any ambiguity, validation rejections, or missing sub-fields requiring clarification
  ]
}
"""

def detect_edit_intent(text: str) -> Optional[str]:
    """
    Detects if the user expresses an intent to change, update, or edit a specific field.
    Returns the field key (e.g. 'home_address', 'full_name', 'executor', etc.) or None.
    """
    t = text.lower().strip()

    # Check for change/update/edit verbs
    has_edit_verb = bool(re.search(
        r"\b(change|update|edit|modify|fix|correct|revise|replace|switch|adjust|re-do|redo)\b",
        t
    ))
    if not has_edit_verb:
        return None

    # 1. Address
    if re.search(r"\b(?:change|update|edit|modify|fix|correct|revise)\b.*\b(?:address|home\s+address|residence|where\s+i\s+live|street)\b", t):
        return "home_address"

    # 2. Executor (checked before name so 'executor name' maps to executor)
    if re.search(r"\b(?:change|update|edit|modify|fix|correct|replace|switch)\b.*\b(?:executor|personal\s+representative|representative)\b", t):
        return "executor"

    # 3. Children (checked before name so 'children names' maps to children)
    if re.search(r"\b(?:change|update|edit|modify|fix)\b.*\b(?:children|kids|child)\b", t):
        return "children"

    # 4. Asset Jurisdiction / Scope
    if re.search(r"\b(?:change|update|edit|modify|switch)\b.*\b(?:asset|assets|scope|jurisdiction|worldwide|domestic)\b", t):
        return "covers_worldwide_assets"

    # 5. Principal Full Name
    if re.search(r"\b(?:change|update|edit|modify|fix|correct|revise)\b.*\b(?:name|full\s+name|legal\s+name)\b", t):
        return "full_name"

    # 6. Specific Gifts
    if re.search(r"\b(?:change|update|edit|modify)\b.*\b(?:gifts?|bequests?)\b", t):
        return "specific_gifts"

    # 7. Additional Wishes
    if re.search(r"\b(?:change|update|edit|modify)\b.*\b(?:wishes|directives|funeral)\b", t):
        return "additional_wishes"

    # 8. General edit intent
    if re.search(r"\b(?:change|update|edit|modify|fix|correct)\s+(?:something|a\s+detail|information|my\s+details|my\s+answers|a\s+field)\b", t) or re.search(r"^(?:can\s+i\s+)?(?:make\s+a\s+change|change\s+something)\??$", t):
        return "general"

    return None

def get_field_pivot_prompt(field: str) -> str:
    """
    Returns the focused conversational follow-up prompt when a user expresses
    an intent to edit/update a field without providing the new value in the same turn.
    """
    prompts = {
        "home_address": "Certainly, let's update your residential address. What is your new home address?",
        "full_name": "Certainly, let's update your legal name. What is your full legal name?",
        "executor": "Certainly, let's update your appointed Executor. Who would you like to appoint as your Executor, and what is their relationship to you?",
        "covers_worldwide_assets": "Certainly, let's update your asset coverage. Should your Personal Wishes Document cover all worldwide assets, or strictly domestic assets in your country of residence?",
        "children": "Certainly, let's update your children details. Do you have any children, and if so, what are their full names?",
        "specific_gifts": "Certainly, let's update your specific gifts. Please describe the gifts or bequests you would like to include or change, and who should receive each one.",
        "additional_wishes": "Certainly, let's update your additional wishes. What personal directives, funeral arrangements, or memorial preferences would you like to include or change?",
        "general": "Certainly! Which detail would you like to update? (You can change your full name, home address, worldwide assets, children, executor, specific gifts, or additional wishes)."
    }
    return prompts.get(field, "Certainly, let's update that information. What new details would you like to provide?")

def get_last_question_topic(history: List[ChatMessage]) -> Optional[str]:
    """Finds what question the assistant asked in the latest turn."""
    for msg in reversed(history):
        if msg.role == "assistant":
            # Look at the question portion (last paragraph) to avoid false matches on acknowledgment headers
            paragraphs = [p.strip() for p in msg.content.split("\n\n") if p.strip()]
            question_text = paragraphs[-1].lower() if paragraphs else msg.content.lower()

            # 1. GIFTS & WISHES SUB-TOPICS (Check specific follow-up sub-topics first)
            if "other personal wishes" in question_text or "ready to finalize" in question_text:
                return "WISHES_DETAILS"
            if "describe your additional wishes" in question_text or "additional wishes or directives" in question_text:
                return "WISHES_DETAILS"
            if "additional personal wishes" in question_text or "additional wishes" in question_text or "funeral arrangements" in question_text or "memorial preferences" in question_text:
                return "WISHES"

            if "any other specific gifts" in question_text or "move on to additional" in question_text:
                return "GIFTS_OR_WISHES"
            if "describe the specific gifts" in question_text or "who should receive each" in question_text or "specific gifts or bequests and who" in question_text:
                return "GIFTS_DETAILS"
            if "specific gifts" in question_text or "bequests" in question_text:
                return "GIFTS"

            # 2. EXECUTOR TOPICS (Must check FIRST before principal NAME so 'full legal name of your executor' maps to EXECUTOR_NAME)
            if "executor" in question_text or "administer your estate" in question_text:
                if "full legal name" in question_text or "full name" in question_text or "what is the name" in question_text or "what is the full" in question_text:
                    return "EXECUTOR_NAME"
                if "relationship" in question_text:
                    if not ("who would you like" in question_text or "appoint" in question_text):
                        return "EXECUTOR_RELATIONSHIP"
                return "EXECUTOR_ALL"
            if "relationship to you" in question_text:
                return "EXECUTOR_RELATIONSHIP"

            # 3. PRINCIPAL FULL NAME
            if "legal name" in question_text or "tell me your full name" in question_text or "what is your full name" in question_text or "your name" in question_text:
                return "NAME"

            # 4. RESIDENTIAL ADDRESS
            if "residential" in question_text or "home address" in question_text or "where do you live" in question_text:
                return "ADDRESS"

            # 5. ASSET JURISDICTION
            if "worldwide assets" in question_text or "strictly domestic" in question_text or "country of residence" in question_text:
                return "WORLDWIDE"

            # 6. CHILDREN
            if "names of your children" in question_text or "names of your child" in question_text:
                return "CHILDREN_NAMES"
            if "have any children" in question_text or "do you have children" in question_text:
                return "CHILDREN_STATUS"
    return None

def build_gemini_prompt(
    user_message: str,
    history: List[ChatMessage],
    current_state: PersonalWishesState,
    last_topic: Optional[str] = None
) -> str:
    """
    Constructs a rich, context-aware prompt for the Gemini model including
    system instructions, current confirmed state, recent conversation history,
    and the current user message.
    """
    state_context = f"CURRENT CONFIRMED STATE:\n{current_state.model_dump_json(indent=2)}"

    history_lines = []
    # Include up to the last 8 messages for context
    for msg in history[-8:]:
        role_label = "Assistant" if msg.role == "assistant" else "User"
        history_lines.append(f"{role_label}: {msg.content}")

    history_context = "RECENT CONVERSATION HISTORY:\n" + ("\n".join(history_lines) if history_lines else "(Beginning of intake conversation)")

    topic_hint = ""
    if last_topic:
        topic_hint = (
            f"\nACTIVE INTAKE FOCUS: The assistant's latest question was specifically regarding: {last_topic}. "
            "Ensure direct answers to this question map contextually to that field. "
            "IMPORTANT: If the user expresses an intent to change, update, or edit a previously provided field "
            "(e.g., 'I want to change my address', 'update my name', 'edit my executor') without providing the value yet, "
            "do not ignore it. Acknowledge the request to modify that field and prompt the user to enter the new value immediately. "
            "If the user provided the new value directly (e.g., 'Actually change my executor to Jane Doe'), "
            "prioritize and extract that override immediately into proposed_state_updates."
        )

    prompt_parts = [
        SYSTEM_PROMPT.strip(),
        state_context,
        history_context + topic_hint,
        f"CURRENT USER MESSAGE:\n{user_message}\n\nRespond with strict JSON."
    ]

    return "\n\n---\n\n".join(prompt_parts)
