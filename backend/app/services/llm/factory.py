import logging
from app.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.mock_provider import MockLLMProvider
from app.services.llm.openai_provider import OpenAILLMProvider
from app.services.llm.gemini_provider import GeminiLLMProvider

logger = logging.getLogger(__name__)

class LLMProviderFactory:
    """
    Factory to instantiate LLM providers based on environment configuration.
    Defaults to deterministic MockLLMProvider if no valid API key is present,
    ensuring 100% functionality without requiring paid credentials.
    """

    @classmethod
    def get_provider(cls, override_provider: str = None) -> BaseLLMProvider:
        provider_type = (override_provider or settings.llm_provider or "mock").lower()

        if provider_type == "openai":
            if settings.openai_api_key:
                logger.info("Initializing OpenAI LLM Provider")
                return OpenAILLMProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model
                )
            else:
                logger.warning("OPENAI_API_KEY not set. Falling back to MockLLMProvider.")
                return MockLLMProvider()

        elif provider_type == "gemini":
            if settings.gemini_api_key:
                logger.info("Initializing Gemini LLM Provider")
                return GeminiLLMProvider(
                    api_key=settings.gemini_api_key,
                    model=settings.gemini_model
                )
            else:
                logger.warning("GEMINI_API_KEY not set. Falling back to MockLLMProvider.")
                return MockLLMProvider()

        logger.info("Initializing deterministic MockLLMProvider")
        return MockLLMProvider()
