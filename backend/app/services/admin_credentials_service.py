"""
Credential storage and verification for admin gate login.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import bcrypt
from firebase_admin import firestore

from app.models.admin import AdminCredentials
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


class AdminCredentialService:
    """Stores hashed credentials in Firestore and verifies logins."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = firestore.client()
        return self._db

    @property
    def credentials_ref(self):
        return self.db.collection("admin").document("credentials")

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _check_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except ValueError:
            return False

    def _record_failure(self) -> None:
        self.credentials_ref.set(
            {
                "failed_attempts": firestore.Increment(1),  # type: ignore[attr-defined]
                "last_failed_at": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )

    def _reset_failures(self) -> None:
        self.credentials_ref.set(
            {"failed_attempts": 0, "last_failed_at": None}, merge=True
        )

    def _ensure_credentials(self) -> dict:
        """Ensure credential document exists with env defaults."""
        doc = self.credentials_ref.get()
        if doc.exists:
            return doc.to_dict() or {}

        initial_payload = {
            "admin_id": settings.admin_id,
            "password_hash": self._hash_password(settings.admin_pw),
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_by": "bootstrap",
            "failed_attempts": 0,
        }
        self.credentials_ref.set(initial_payload)
        doc = self.credentials_ref.get()
        return doc.to_dict() or initial_payload

    def verify_credentials(self, admin_id: str, password: str) -> bool:
        """Return True when provided credentials match stored hash."""
        record = self._ensure_credentials()
        stored_admin_id = record.get("admin_id")
        stored_hash = record.get("password_hash")

        if stored_admin_id != admin_id:
            self._record_failure()
            return False

        if not stored_hash or not self._check_password(password, stored_hash):
            self._record_failure()
            return False

        self._reset_failures()
        return True

    def update_credentials(
        self,
        current_password: str,
        new_admin_id: str,
        new_password: str,
        updated_by: Optional[str] = None,
    ) -> AdminCredentials:
        """Rotate admin id/password after verifying the current secret."""
        if not new_admin_id.strip():
            raise ValueError("새 관리자 ID를 입력해주세요.")
        if len(new_password) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        record = self._ensure_credentials()
        stored_hash = record.get("password_hash")
        if not stored_hash or not self._check_password(current_password, stored_hash):
            raise ValueError("현재 비밀번호가 일치하지 않습니다.")

        update_payload = {
            "admin_id": new_admin_id.strip(),
            "password_hash": self._hash_password(new_password),
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_by": updated_by,
            "failed_attempts": 0,
        }
        self.credentials_ref.set(update_payload, merge=True)
        return self.get_metadata()

    def get_metadata(self) -> AdminCredentials:
        """Expose metadata without revealing password hash."""
        record = self._ensure_credentials()
        return AdminCredentials(
            admin_id=record.get("admin_id", "admin"),
            updated_at=_to_datetime(record.get("updated_at")),
            updated_by=record.get("updated_by"),
        )

