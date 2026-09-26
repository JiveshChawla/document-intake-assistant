import json
import logging
from typing import List
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult
from app.services.llm.prompts import SYSTEM_PROMPT, build_gemini_prompt, get_last_question_topic
from app.services.validator import InputValidator

logger = logging.getLogger(__name__)

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
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            )
            
            # Detect context from recent history to enforce context-aware mapping
            last_topic = get_last_question_topic(history)
            
            # Build rich prompt with System prompt, State, Conversation History, and Current message
            prompt = build_gemini_prompt(
                user_message=user_message,
                history=history,
                current_state=current_state,
                last_topic=last_topic
            )
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)
            
            raw_proposed = parsed.get("proposed_state_updates", {})
            raw_ambiguities = parsed.get("ambiguities", [])
            assistant_msg = parsed.get("assistant_message", "Could you please elaborate?")

            # -----------------------------------------------------------------
            # Strict Schema & Input Validation Enforcement
            # -----------------------------------------------------------------
            # Even if the LLM proposed an invalid or gibberish input, filter it
            # out, record the rejection in ambiguities, and keep the field empty.
            validated_updates, rejection_warnings = InputValidator.validate_proposed_updates(
                raw_proposed,
                user_message=user_message
            )

            all_ambiguities = list(raw_ambiguities)
            if rejection_warnings:
                all_ambiguities.extend(rejection_warnings)
                logger.warning(f"Gemini proposed updates contained invalid entries that were rejected: {rejection_warnings}")
                
                # If assistant message didn't already reject or clarify, update it politely
                lower_msg = assistant_msg.lower()
                if not any(w in lower_msg for w in ["valid", "invalid", "clarify", "verify", "recognize", "re-enter", "please provide"]):
                    assistant_msg = (
                        f"I could not verify the provided response as a valid legal entry ({'; '.join(rejection_warnings)}). "
                        "Could you please provide a valid response?"
                    )

            # Context-Aware check: If asking for executor, ensure full_name was not accidentally updated
            if last_topic in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP"]:
                if "full_name" in validated_updates and "full_name" not in user_message.lower():
                    logger.warning("Prevented Gemini from assigning executor answer to full_name")
                    validated_updates.pop("full_name", None)

            return LLMExtractionResult(
                assistant_message=assistant_msg,
                proposed_state_updates=validated_updates,
                ambiguities=all_ambiguities,
                confidence=0.95 if not rejection_warnings else 0.7,
                raw_model_response=raw_text
            )
        except Exception as e:
            logger.error(f"Gemini API error during turn: {e}", exc_info=True)
            return LLMExtractionResult(
                assistant_message=f"I encountered an issue processing your response with the AI service. Could you please repeat that? (Error: {str(e)})",
                proposed_state_updates={},
                ambiguities=["Gemini API error"],
                confidence=0.0,
                raw_model_response=str(e)
            )
