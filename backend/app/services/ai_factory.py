"""
AI Service Factory - creates AI service instances based on provider
"""
from typing import Optional
from app.services.ai_service_interface import AIServiceInterface
from app.services.gpt_service import GPTService
from app.services.gemini_service import GeminiService
from config import settings


def get_ai_service(provider: Optional[str] = None) -> AIServiceInterface:
    """
    Factory function to get AI service instance
    
    Args:
        provider: AI provider name ("gpt" or "gemini").
                 If None, uses default from settings.
    
    Returns:
        AIServiceInterface implementation
    
    Raises:
        ValueError: If provider is not supported
    """
    # Use default provider if not specified
    if provider is None:
        provider = settings.default_ai_provider
    
    provider = provider.lower().strip()
    
    if provider == "gpt":
        return GPTService(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
    elif provider == "gemini":
        return GeminiService(
            api_key=settings.google_api_key,
            model=settings.google_model
        )
    else:
        raise ValueError(
            f"Unsupported AI provider: {provider}. "
            f"Supported providers: gpt, gemini"
        )


def get_supported_providers() -> list[str]:
    """
    Get list of supported AI providers
    
    Returns:
        List of provider names
    """
    return ["gpt", "gemini"]

