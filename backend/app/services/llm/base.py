from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.state import PersonalWishesState
from app.models.chat import ChatMessage

class LLMExtractionResult(BaseModel):
    """
    Structured response contract from any LLM provider (mock or live).
    Strictly separates model reasoning & proposed updates from state persistence.
    """
    assistant_message: str = Field(..., description="Conversational reply to the user")
    proposed_state_updates: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Key-value pairs of extracted or updated fields"
    )
    ambiguities: List[str] = Field(
        default_factory=list, 
        description="List of ambiguities or conflicts detected requiring follow-up"
    )
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    raw_model_response: Optional[str] = Field(None, description="Raw text/JSON returned by provider")

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Both deterministic mock providers and live API providers (OpenAI, Gemini) implement this contract.
    """
    provider_name: str = "base"

    @abstractmethod
    async def process_turn(
        self,
        user_message: str,
        history: List[ChatMessage],
        current_state: PersonalWishesState,
    ) -> LLMExtractionResult:
        """
        Processes a single conversational turn.
        Inputs:
            - user_message: latest user input text
            - history: prior chat messages
            - current_state: current confirmed structured state (source of truth)
        Outputs:
            - LLMExtractionResult with assistant_message, proposed updates, and ambiguity flags
        """
        pass
