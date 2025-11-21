"""
Service helpers for admin configuration and lifecycle management.
"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from firebase_admin import firestore

from app.models.admin import (
    AdminConfig,
    ParametersUpdateRequest,
    ServiceStatus,
    StatusUpdateRequest,
)
from config import settings


def _to_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return value.to_datetime()
    except AttributeError:
        return None


class AdminConfigService:
    """CRUD layer for admin configuration document in Firestore."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = firestore.client()
        return self._db

    @property
    def config_ref(self):
        return self.db.collection("admin").document("config")

    @staticmethod
    def _normalize_emails(emails: Optional[Iterable[str]]) -> List[str]:
        if not emails:
            return []
        return sorted(
            {
                email.strip().lower()
                for email in emails
                if email and email.strip()
            }
        )

    def _default_config_payload(self) -> dict:
        return {
            "status": ServiceStatus.closed_beta.value,
            "allowed_emails": [],
            "ai_provider": settings.default_ai_provider,
            "openai_model": settings.openai_model,
            "gemini_model": settings.google_model,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_by": "system",
        }

    def get_config(self) -> AdminConfig:
        """Fetch configuration document, creating defaults when missing."""
        doc = self.config_ref.get()
        if not doc.exists:
            payload = self._default_config_payload()
            self.config_ref.set(payload)
            doc = self.config_ref.get()

        data = doc.to_dict() or {}
        status_value = data.get("status", ServiceStatus.closed_beta.value)
        try:
            status = ServiceStatus(status_value)
        except ValueError:
            status = ServiceStatus.closed_beta

        allowed_emails = self._normalize_emails(data.get("allowed_emails", []))

        return AdminConfig(
            status=status,
            allowed_emails=allowed_emails,
            ai_provider=data.get("ai_provider") or settings.default_ai_provider,
            openai_model=data.get("openai_model") or settings.openai_model,
            gemini_model=data.get("gemini_model") or settings.google_model,
            updated_at=_to_datetime(data.get("updated_at")),
            updated_by=data.get("updated_by"),
        )

    def update_status(
        self,
        request: StatusUpdateRequest,
        updated_by: Optional[str] = None,
    ) -> AdminConfig:
        """Update lifecycle status and optional email allowlist."""
        update_data = {
            "status": request.status.value,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_by": updated_by,
        }
        if request.allowed_emails is not None:
            update_data["allowed_emails"] = self._normalize_emails(
                request.allowed_emails
            )

        self.config_ref.set(update_data, merge=True)
        return self.get_config()

    def update_parameters(
        self,
        request: ParametersUpdateRequest,
        updated_by: Optional[str] = None,
    ) -> AdminConfig:
        """Update AI/model parameters stored in config."""
        update_data = {
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_by": updated_by,
        }
        if request.ai_provider is not None:
            update_data["ai_provider"] = request.ai_provider
        if request.openai_model is not None:
            update_data["openai_model"] = request.openai_model
        if request.gemini_model is not None:
            update_data["gemini_model"] = request.gemini_model

        self.config_ref.set(update_data, merge=True)
        return self.get_config()

    def is_email_allowed(self, email: Optional[str]) -> bool:
        """Return True if email is allowed to access admin dashboard."""
        config = self.get_config()
        if config.status != ServiceStatus.closed_beta:
            return True
        if not email:
            return False
        normalized_email = email.strip().lower()
        return normalized_email in {item.lower() for item in config.allowed_emails}

