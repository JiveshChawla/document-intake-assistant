import json
from typing import List
from openai import AsyncOpenAI
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult

SYSTEM_PROMPT = """
You are the Document Intake Assistant for a fictional "Personal Wishes Document".
Your role is to conduct an empathetic, professional legal-intake interview to collect:
1. full_name: Full legal name
2. home_address: Primary residential address
3. covers_worldwide_assets: Boolean (true for worldwide, false for domestic only)
4. has_children: Boolean (true if user has children, false if none)
5. children: Array of children's legal names (if has_children is true; empty array if false)
6. executor: Object with "name" and "relationship" (both must be gathered)
7. specific_gifts: Array of objects with "item" and "recipient"
8. additional_wishes: Array of strings (funeral preferences, memorial directives, etc.)

CRITICAL GUIDELINES:
- Separate state from conversation: Provide extracted updates in structured JSON.
- Never invent facts. If a value is unknown, represent it as null or omit it.
- Ask sensible follow-up questions when information is missing, unclear, or contradictory.
- If the user specifies an executor relationship (e.g. "my brother") but no name, or a name without relationship, flag this ambiguity and ask for the missing detail.
- Handle multi-field answers in any order.
- Respect corrections cleanly (e.g. "Actually, my executor is Sarah").
- Avoid repeatedly asking for information that has already been captured.
- OPTIONAL SECTIONS (Gifts & Wishes):
  * When asking if the user has specific gifts or additional wishes, if the user replies 'yes' (or gives an affirmative answer) without details, DO NOT skip or finalize. Prompt them warmly to specify what those gifts or directives are.
  * When the user describes gifts (e.g. 'my watch to my son Lucas' or 'donate my books'), extract them into specific_gifts with 'item' and 'recipient'.
  * When the user describes additional personal wishes (e.g. 'cremation and ashes scattered', 'play jazz at my funeral'), extract them into additional_wishes array.

You MUST respond with a JSON object strictly matching this schema:
{
  "assistant_message": "Conversational message to user acknowledging what was recorded and asking the next question or clarifying ambiguities",
  "proposed_state_updates": {
    // Only include keys that were provided, clarified, or corrected in this turn!
    // Example: "full_name": "Jane Doe", "executor": {"name": "James", "relationship": "brother"}, "specific_gifts": [{"item": "watch", "recipient": "son Lucas"}]
  },
  "ambiguities": [
    // List of strings explaining any ambiguity or missing sub-fields requiring clarification
  ]
}
"""

class OpenAILLMProvider(BaseLLMProvider):
    provider_name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def process_turn(
        self,
        user_message: str,
        history: List[ChatMessage],
        current_state: PersonalWishesState,
    ) -> LLMExtractionResult:
        state_context = f"CURRENT CONFIRMED STATE:\n{current_state.model_dump_json(indent=2)}"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + state_context},
        ]
        
        # Include recent history
        for m in history[-6:]:
            messages.append({"role": m.role, "content": m.content})
            
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_text)
            
            return LLMExtractionResult(
                assistant_message=parsed.get("assistant_message", "Could you please elaborate?"),
                proposed_state_updates=parsed.get("proposed_state_updates", {}),
                ambiguities=parsed.get("ambiguities", []),
                confidence=0.95,
                raw_model_response=raw_text
            )
        except Exception as e:
            # Fallback handling
            return LLMExtractionResult(
                assistant_message=f"I encountered a temporary connection issue with the AI service. Could you please repeat that? (Error: {str(e)})",
                proposed_state_updates={},
                ambiguities=["Model API communication error"],
                confidence=0.0,
                raw_model_response=str(e)
            )
