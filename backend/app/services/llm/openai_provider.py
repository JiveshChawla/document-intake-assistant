import json
import logging
from typing import List
from openai import AsyncOpenAI
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage
from app.services.llm.base import BaseLLMProvider, LLMExtractionResult
from app.services.llm.prompts import SYSTEM_PROMPT, get_last_question_topic
from app.services.validator import InputValidator

logger = logging.getLogger(__name__)

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
        last_topic = get_last_question_topic(history)
        
        system_content = SYSTEM_PROMPT.strip() + f"\n\n{state_context}"
        if last_topic:
            system_content += f"\n\nACTIVE INTAKE FOCUS: Latest question asked was regarding {last_topic}."

        messages = [
            {"role": "system", "content": system_content},
        ]
        
        # Include recent history
        for m in history[-8:]:
            messages.append({"role": m.role, "content": m.content})
            
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_text = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_text)
            
            raw_proposed = parsed.get("proposed_state_updates", {})
            raw_ambiguities = parsed.get("ambiguities", [])
            assistant_msg = parsed.get("assistant_message", "Could you please elaborate?")

            # Strict backend validation of proposed updates against gibberish/nonsense
            validated_updates, rejection_warnings = InputValidator.validate_proposed_updates(
                raw_proposed,
                user_message=user_message
            )

            all_ambiguities = list(raw_ambiguities)
            if rejection_warnings:
                all_ambiguities.extend(rejection_warnings)
                lower_msg = assistant_msg.lower()
                if not any(w in lower_msg for w in ["valid", "invalid", "clarify", "verify", "recognize", "re-enter", "please provide"]):
                    assistant_msg = (
                        f"I could not verify the provided response as a valid legal entry ({'; '.join(rejection_warnings)}). "
                        "Could you please provide a valid response?"
                    )

            # Context-Aware check: Prevent executor answer from altering full_name
            if last_topic in ["EXECUTOR_ALL", "EXECUTOR_NAME", "EXECUTOR_RELATIONSHIP"]:
                if "full_name" in validated_updates and "full_name" not in user_message.lower():
                    validated_updates.pop("full_name", None)
            
            return LLMExtractionResult(
                assistant_message=assistant_msg,
                proposed_state_updates=validated_updates,
                ambiguities=all_ambiguities,
                confidence=0.95 if not rejection_warnings else 0.7,
                raw_model_response=raw_text
            )
        except Exception as e:
            logger.error(f"OpenAI API error during turn: {e}", exc_info=True)
            return LLMExtractionResult(
                assistant_message=f"I encountered a temporary connection issue with the AI service. Could you please repeat that? (Error: {str(e)})",
                proposed_state_updates={},
                ambiguities=["Model API communication error"],
                confidence=0.0,
                raw_model_response=str(e)
            )
