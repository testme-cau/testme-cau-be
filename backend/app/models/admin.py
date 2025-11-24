"""
Pydantic models for admin interface
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ServiceStatus(str, Enum):
    """Service lifecycle phases managed via admin console."""

    closed_beta = "closed_beta"
    open_beta = "open_beta"
    release = "release"


class AdminConfig(BaseModel):
    """Combined configuration for service status and runtime parameters."""

    status: ServiceStatus = ServiceStatus.closed_beta
    allowed_emails: List[str] = Field(default_factory=list)
    ai_provider: Optional[str] = None
    openai_model: Optional[str] = None
    gemini_model: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    """Request body for updating service status & allowlist."""

    status: ServiceStatus
    allowed_emails: Optional[List[str]] = None

    @validator("allowed_emails", each_item=True)
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ParametersUpdateRequest(BaseModel):
    """Request body for updating AI/runtime parameters."""

    ai_provider: Optional[str] = None
    openai_model: Optional[str] = None
    gemini_model: Optional[str] = None


class AdminConfigResponse(BaseModel):
    """Response containing admin config payload."""
    
    success: bool = True
    config: AdminConfig


class BetaStatusResponse(BaseModel):
    """Public status payload exposed to landing/login UI."""

    status: ServiceStatus
    allowed_emails: List[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class FirebaseUserPayload(BaseModel):
    """Subset of Firebase user object passed from OAuth popup."""

    uid: str
    email: Optional[str] = None
    displayName: Optional[str] = None
    photoURL: Optional[str] = None


class FirebaseLoginRequest(BaseModel):
    """Payload delivered after Firebase OAuth completes."""

    id_token: str = Field(alias="idToken")
    user: FirebaseUserPayload


class AdminLoginRequest(BaseModel):
    """Step 1 admin gate login request."""

    admin_id: str
    admin_pw: str


class AdminCredentials(BaseModel):
    """Credential metadata exposed to the dashboard."""

    admin_id: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class AdminCredentialsUpdateRequest(BaseModel):
    """Request body for rotating admin ID/password."""

    current_password: str
    new_admin_id: str
    new_password: str


class UserAnalytics(BaseModel):
    """Per-user aggregated statistics."""

    uid: str
    email: Optional[str] = None
    subject_count: int = 0
    exam_count: int = 0
    pdf_count: int = 0
    last_active: Optional[datetime] = None


class AnalyticsSummary(BaseModel):
    """High-level KPI numbers."""

    total_users: int = 0
    monthly_active_users: int = 0
    total_subjects: int = 0
    total_exams: int = 0
    total_pdfs: int = 0
    average_subjects_per_user: float = 0.0
    average_exams_per_user: float = 0.0


class AnalyticsSummaryResponse(BaseModel):
    """Response envelope for analytics endpoint."""

    success: bool = True
    summary: AnalyticsSummary
    users: List[UserAnalytics] = Field(default_factory=list)


class WaitlistEntry(BaseModel):
    """Waitlist entry for closed beta approvals."""

    entry_id: str
    email: str
    note: Optional[str] = None
    status: str = "pending"
    requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class WaitlistResponse(BaseModel):
    """Response containing waitlist entries."""

    success: bool = True
    entries: List[WaitlistEntry] = Field(default_factory=list)


class WaitlistActionRequest(BaseModel):
    """Request body for approving or rejecting waitlist entries."""

    entry_id: str


class WaitlistJoinRequest(BaseModel):
    """Public request to join the closed beta waitlist."""

    email: str
    note: Optional[str] = None

    @validator("email")
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("유효한 이메일 주소를 입력해주세요.")
        return normalized


class WaitlistJoinResponse(BaseModel):
    """Response for waitlist join attempts."""

    success: bool = True
    already_allowed: bool = False
    already_pending: bool = False
    message: str = ""


