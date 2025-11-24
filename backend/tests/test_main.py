"""
Tests for main API endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.models.admin import AdminConfig, ServiceStatus


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test.me" in data["message"].lower()


def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_api_health_endpoint(client: TestClient):
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "API is running"


def test_beta_status_endpoint(client: TestClient, monkeypatch):
    """Beta status endpoint reflects admin config."""
    dummy_config = AdminConfig(
        status=ServiceStatus.closed_beta,
        allowed_emails=["beta@test.me"],
        ai_provider="gpt",
        openai_model="gpt-4o",
        gemini_model="gemini-2.5-pro",
    )

    monkeypatch.setattr(
        "app.routes.main.config_service.get_config",
        lambda: dummy_config,
    )

    response = client.get("/api/admin/config/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed_beta"
    assert data["allowed_emails"] == ["beta@test.me"]


def test_join_waitlist_endpoint(client: TestClient, monkeypatch):
    """Waitlist join endpoint delegates to service."""
    captured = {}

    def _add_entry(email, note=None):
        captured["email"] = email
        captured["note"] = note
        return None

    monkeypatch.setattr(
        "app.routes.main.waitlist_service.add_entry",
        _add_entry,
    )

    response = client.post(
        "/api/waitlist",
        json={"email": "user@example.com", "note": "invite me"},
    )
    assert response.status_code == 200
    assert captured["email"] == "user@example.com"
    assert response.json()["success"] is True

