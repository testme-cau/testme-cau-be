"""
Service helpers for managing closed beta waitlist entries.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from firebase_admin import firestore

from app.models.admin import WaitlistEntry
from app.services.admin_config_service import AdminConfigService


def _to_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return value.to_datetime()
    except AttributeError:
        return None


class AdminWaitlistService:
    """CRUD utilities for the closed-beta waitlist."""

    def __init__(self):
        self._db = None
        self._config_service = AdminConfigService()

    @property
    def db(self):
        if self._db is None:
            self._db = firestore.client()
        return self._db

    @property
    def collection(self):
        return (
            self.db.collection("admin")
            .document("waitlist")
            .collection("entries")
        )

    def _doc_to_entry(self, doc) -> WaitlistEntry:
        data = doc.to_dict() or {}
        return WaitlistEntry(
            entry_id=doc.id,
            email=data.get("email", ""),
            note=data.get("note"),
            status=data.get("status", "pending"),
            requested_at=_to_datetime(data.get("requested_at")),
            approved_at=_to_datetime(data.get("approved_at")),
            updated_by=data.get("updated_by"),
        )

    def list_entries(self) -> List[WaitlistEntry]:
        """Return waitlist entries ordered by request date desc."""
        docs = (
            self.collection.order_by(
                "requested_at", direction=firestore.Query.DESCENDING
            )
            .stream()
        )
        return [self._doc_to_entry(doc) for doc in docs]

    def add_entry(self, email: str, note: Optional[str] = None) -> WaitlistEntry:
        """Add a new waitlist entry if not already present/allowed."""
        normalized = email.strip().lower()
        config = self._config_service.get_config()
        if normalized in {addr.lower() for addr in config.allowed_emails}:
            raise ValueError("ALREADY_ALLOWED")

        existing = (
            self.collection.where("email", "==", normalized)
            .where("status", "==", "pending")
            .limit(1)
            .stream()
        )
        if list(existing):
            raise ValueError("ALREADY_PENDING")

        doc_ref = self.collection.document()
        payload = {
            "email": normalized,
            "note": note,
            "status": "pending",
            "requested_at": firestore.SERVER_TIMESTAMP,
        }
        doc_ref.set(payload)
        created = doc_ref.get()
        return self._doc_to_entry(created)

    def remove_entry(self, entry_id: str) -> None:
        """Remove an entry (used for rejection)."""
        doc_ref = self.collection.document(entry_id)
        if not doc_ref.get().exists:
            raise ValueError("WAITLIST_NOT_FOUND")
        doc_ref.delete()

    def approve_entry(self, entry_id: str, updated_by: Optional[str] = None):
        """Approve entry by moving email into allowed_emails and marking approved."""
        doc_ref = self.collection.document(entry_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise ValueError("WAITLIST_NOT_FOUND")

        entry = doc.to_dict() or {}
        email = entry.get("email")
        if not email:
            raise ValueError("INVALID_ENTRY")

        # Append to allowlist
        self._config_service.add_allowed_email(email, updated_by=updated_by)

        # Update entry metadata & mark as approved
        doc_ref.update(
            {
                "status": "approved",
                "approved_at": firestore.SERVER_TIMESTAMP,
                "updated_by": updated_by,
            }
        )
        return email

