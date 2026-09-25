import json
from typing import List
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult
from app.services.llm.openai_provider import SYSTEM_PROMPT

class GeminiLLMProvider(BaseLLMProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            self.genai = None

    async def process_turn(
        self,
        user_message: str,
        history: List[ChatMessage],
        current_state: PersonalWishesState,
    ) -> LLMExtractionResult:
        if not self.genai:
            return LLMExtractionResult(
                assistant_message="Gemini SDK is not installed or configured.",
                proposed_state_updates={},
                ambiguities=["SDK Missing"],
                confidence=0.0
            )

        try:
            model = self.genai.GenerativeModel(
                model_name=self.model,
                generation_config={"response_mime_type": "application/json"}
            )
            state_ctx = f"CURRENT STATE: {current_state.model_dump_json()}"
            prompt = f"{SYSTEM_PROMPT}\n\n{state_ctx}\n\nUser Message: {user_message}"
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)
            
            return LLMExtractionResult(
                assistant_message=parsed.get("assistant_message", "Could you please clarify?"),
                proposed_state_updates=parsed.get("proposed_state_updates", {}),
                ambiguities=parsed.get("ambiguities", []),
                confidence=0.95,
                raw_model_response=raw_text
            )
        except Exception as e:
            return LLMExtractionResult(
                assistant_message=f"Gemini API error occurred: {str(e)}",
                proposed_state_updates={},
                ambiguities=["Gemini API error"],
                confidence=0.0,
                raw_model_response=str(e)
            )
