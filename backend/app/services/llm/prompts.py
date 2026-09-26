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

2. Context-Aware Field Mapping:
   - Check the recent conversation history to identify the specific field the assistant just asked for!
   - If the assistant just asked about the executor (e.g., "Who would you like to appoint as your Executor..."), any name or relationship provided MUST be mapped strictly to the "executor" object ("name" or "relationship") and MUST NEVER alter or overwrite "full_name".
   - If the assistant just asked for residential address, map it strictly to "home_address".
   - If the user provides multiple valid fields at once (e.g., "I am Jane Doe living at 10 Downing St, London"), extract all valid fields into their respective keys. Reject any sub-field that is nonsensical or ambiguous.

3. Handling Missing/Ambiguous Data:
   - Never invent facts or assume values. If a value is unknown or unconfirmed, omit it.
   - If the user specifies an executor relationship (e.g. "my brother") without a name, or a name without relationship, flag this ambiguity and ask for the missing detail.
   - Avoid repeatedly asking for information that has already been captured.

4. Optional Sections (Gifts & Wishes):
   - When asking if the user has specific gifts or additional wishes, if the user replies 'yes' (or gives an affirmative answer) without details, DO NOT skip or finalize. Prompt them warmly to specify what those gifts or directives are.
   - When the user describes gifts (e.g. 'my watch to my son Lucas' or 'donate my books'), extract them into specific_gifts with 'item' and 'recipient'.
   - When the user describes additional personal wishes (e.g. 'cremation and ashes scattered', 'play jazz at my funeral'), extract them into additional_wishes array.

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
        topic_hint = f"\nACTIVE INTAKE FOCUS: The assistant's latest question was specifically regarding: {last_topic}. Ensure answers to this prompt map contextually to that field unless explicit multi-field information or correction is stated."

    prompt_parts = [
        SYSTEM_PROMPT.strip(),
        state_context,
        history_context + topic_hint,
        f"CURRENT USER MESSAGE:\n{user_message}\n\nRespond with strict JSON."
    ]

    return "\n\n---\n\n".join(prompt_parts)
