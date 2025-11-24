"""
Tests for AI factory configuration resolution (admin-driven)
"""
from app.models.admin import AdminConfig, ServiceStatus
from app.services import ai_factory
from config import settings


class DummyGeminiService:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model


class DummyGPTService:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model


def _set_admin_config(monkeypatch, **overrides):
    config = AdminConfig(
        status=overrides.get("status", ServiceStatus.release),
        allowed_emails=overrides.get("allowed_emails", []),
        ai_provider=overrides.get("ai_provider"),
        openai_model=overrides.get("openai_model"),
        gemini_model=overrides.get("gemini_model"),
    )
    monkeypatch.setattr(
        ai_factory._admin_config_service,
        "get_config",
        lambda: config,
    )
    ai_factory.invalidate_admin_config_cache()
    return config


def _patch_services(monkeypatch):
    monkeypatch.setattr(ai_factory, "GeminiService", DummyGeminiService)
    monkeypatch.setattr(ai_factory, "GPTService", DummyGPTService)


def _set_dummy_api_keys(monkeypatch):
    monkeypatch.setattr(settings, "google_api_key", "dummy-google", raising=False)
    monkeypatch.setattr(settings, "openai_api_key", "dummy-openai", raising=False)


def test_ai_factory_uses_admin_default_provider(monkeypatch):
    _patch_services(monkeypatch)
    _set_dummy_api_keys(monkeypatch)
    _set_admin_config(
        monkeypatch,
        ai_provider="gemini",
        openai_model="gpt-5",
        gemini_model="gemini-2.5-pro-admin",
    )

    service = ai_factory.get_ai_service()
    assert isinstance(service, DummyGeminiService)
    assert service.model == "gemini-2.5-pro-admin"


def test_ai_factory_respects_query_provider_but_uses_admin_model(monkeypatch):
    _patch_services(monkeypatch)
    _set_dummy_api_keys(monkeypatch)
    _set_admin_config(
        monkeypatch,
        ai_provider="gemini",
        openai_model="gpt-5o-mini",
        gemini_model="gemini-2.5-flash",
    )

    service = ai_factory.get_ai_service("gpt")
    assert isinstance(service, DummyGPTService)
    assert service.model == "gpt-5o-mini"


def test_ai_factory_falls_back_when_admin_config_unavailable(monkeypatch):
    _patch_services(monkeypatch)
    _set_dummy_api_keys(monkeypatch)

    def _raise():
        raise RuntimeError("firestore unavailable")

    monkeypatch.setattr(
        ai_factory._admin_config_service,
        "get_config",
        _raise,
    )
    ai_factory.invalidate_admin_config_cache()
    monkeypatch.setattr(settings, "default_ai_provider", "gpt", raising=False)
    monkeypatch.setattr(settings, "openai_model", "gpt-from-settings", raising=False)

    service = ai_factory.get_ai_service()
    assert isinstance(service, DummyGPTService)
    assert service.model == "gpt-from-settings"

