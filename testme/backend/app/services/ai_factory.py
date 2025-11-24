"""
AI Service Factory - creates AI service instances based on provider
"""
from __future__ import annotations

import logging
import time
from typing import Optional, Tuple

from app.models.admin import AdminConfig
from app.services.admin_config_service import AdminConfigService
from app.services.ai_service_interface import AIServiceInterface
from app.services.gemini_service import GeminiService
from app.services.gpt_service import GPTService
from config import settings

logger = logging.getLogger(__name__)
_admin_config_service = AdminConfigService()
_CONFIG_CACHE_TTL = 30.0  # seconds
_admin_config_cache: dict[str, Tuple[Optional[AdminConfig], float]] = {
    "value": (None, 0.0)
}


def _get_cached_admin_config() -> Optional[AdminConfig]:
    """Fetch admin config with lightweight caching/fallback."""
    cached_config, cached_at = _admin_config_cache["value"]
    now = time.monotonic()
    if cached_config is not None and now - cached_at < _CONFIG_CACHE_TTL:
        return cached_config

    try:
        config = _admin_config_service.get_config()
        _admin_config_cache["value"] = (config, now)
        return config
    except Exception as exc:  # pragma: no cover - firestore/network errors
        logger.warning("Failed to fetch admin config, using previous/settings: %s", exc)
        return cached_config


def invalidate_admin_config_cache() -> None:
    """Clear admin configuration cache (called after dashboard updates)."""
    _admin_config_cache["value"] = (None, 0.0)


def _resolve_provider_and_models(
    provider: Optional[str],
) -> Tuple[str, str, str]:
    """
    Determine provider & model names using admin-configured values when present.

    Returns:
        Tuple[provider, openai_model, gemini_model]
    """
    admin_config = _get_cached_admin_config()
    default_provider = (
        admin_config.ai_provider
        if admin_config and admin_config.ai_provider
        else settings.default_ai_provider
    )

    raw_provider = provider or default_provider
    if not raw_provider:
        raise ValueError("AI provider not specified and no default configured")

    resolved_provider = raw_provider.lower().strip()
    openai_model = settings.openai_model
    gemini_model = settings.google_model

    if admin_config:
        openai_model = admin_config.openai_model or openai_model
        gemini_model = admin_config.gemini_model or gemini_model

    return resolved_provider, openai_model, gemini_model


def get_ai_service(provider: Optional[str] = None) -> AIServiceInterface:
    """
    Factory function to get AI service instance.

    If admin dashboard has configured provider/model overrides, they take
    precedence unless an explicit query parameter is provided.
    """
    resolved_provider, openai_model, gemini_model = _resolve_provider_and_models(
        provider
    )

    if resolved_provider == "gpt":
        return GPTService(
            api_key=settings.openai_api_key,
            model=openai_model,
        )
    if resolved_provider == "gemini":
        return GeminiService(
            api_key=settings.google_api_key,
            model=gemini_model,
        )
    raise ValueError(
        f"Unsupported AI provider: {resolved_provider}. Supported providers: gpt, gemini"
    )


def get_supported_providers() -> list[str]:
    """
    Get list of supported AI providers
    
    Returns:
        List of provider names
    """
    return ["gpt", "gemini"]

