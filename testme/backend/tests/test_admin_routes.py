"""
Tests for admin FastAPI routes
"""
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.models.admin import AdminConfig, ServiceStatus


def _dummy_config() -> AdminConfig:
    return AdminConfig(
        status=ServiceStatus.open_beta,
        allowed_emails=["beta@test.me"],
        ai_provider="gpt",
        openai_model="gpt-4o",
        gemini_model="gemini-1.5-pro",
    )


def _authenticate_admin(client: TestClient, monkeypatch) -> None:
    """Helper to perform admin gate + firebase login."""
    monkeypatch.setattr(
        "app.routes.admin.credential_service.verify_credentials",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "app.routes.admin.config_service.get_config",
        lambda: _dummy_config(),
    )
    monkeypatch.setattr(
        "app.routes.admin.firebase_auth.verify_id_token",
        lambda *_: {"uid": "admin-uid", "email": "admin@test.me"},
    )

    login_response = client.post(
        "/admin/login",
        json={"admin_id": "admin", "admin_pw": "pw"},
    )
    assert login_response.status_code == 200

    firebase_response = client.post(
        "/admin/firebase-login",
        json={
            "idToken": "token",
            "user": {
                "uid": "admin-uid",
                "email": "admin@test.me",
                "displayName": "Admin",
                "photoURL": None,
            },
        },
    )
    assert firebase_response.status_code == 200


def test_admin_login_success(client: TestClient, monkeypatch):
    monkeypatch.setattr(
        "app.routes.admin.credential_service.verify_credentials",
        lambda *_: True,
    )
    response = client.post(
        "/admin/login",
        json={"admin_id": "admin", "admin_pw": "pw"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_admin_login_failure(client: TestClient, monkeypatch):
    monkeypatch.setattr(
        "app.routes.admin.credential_service.verify_credentials",
        lambda *_: False,
    )
    response = client.post(
        "/admin/login",
        json={"admin_id": "admin", "admin_pw": "wrong"},
    )
    assert response.status_code == 401


def test_session_endpoint_requires_full_auth(client: TestClient, monkeypatch):
    _authenticate_admin(client, monkeypatch)

    response = client.get("/admin/api/session")
    assert response.status_code == 200
    payload = response.json()
    assert payload["authenticated"] is True
    assert payload["user"]["email"] == "admin@test.me"


def test_update_service_status_calls_service(client: TestClient, monkeypatch):
    _authenticate_admin(client, monkeypatch)

    updated_config = AdminConfig(
        status=ServiceStatus.release,
        allowed_emails=[],
        ai_provider="gpt",
        openai_model="gpt-4o-mini",
        gemini_model="gemini-1.5-pro",
    )

    mock_update = MagicMock(return_value=updated_config)
    monkeypatch.setattr(
        "app.routes.admin.config_service.update_status",
        mock_update,
    )

    response = client.put(
        "/admin/api/config/status",
        json={"status": "release", "allowed_emails": []},
    )
    assert response.status_code == 200
    assert response.json()["config"]["status"] == "release"
    mock_update.assert_called_once()


def test_analytics_endpoint_returns_mock_data(client: TestClient, monkeypatch):
    _authenticate_admin(client, monkeypatch)

    mock_summary = {
        "success": True,
        "summary": {
            "total_users": 1,
            "monthly_active_users": 1,
            "total_subjects": 2,
            "total_exams": 3,
            "total_pdfs": 4,
            "average_subjects_per_user": 2.0,
            "average_exams_per_user": 3.0,
        },
        "users": [
            {
                "uid": "user-1",
                "email": "user1@test.me",
                "subject_count": 2,
                "exam_count": 3,
                "pdf_count": 4,
                "last_active": "2024-01-01T00:00:00",
            }
        ],
    }

    monkeypatch.setattr(
        "app.routes.admin.analytics_service.get_summary",
        lambda: mock_summary,
    )

    response = client.get("/admin/api/analytics/summary")
    assert response.status_code == 200
    assert response.json()["summary"]["total_users"] == 1

