"""
Main API routes (root and health endpoints)
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.admin import (
    BetaStatusResponse,
    WaitlistJoinRequest,
    WaitlistJoinResponse,
)
from app.services.admin_config_service import AdminConfigService
from app.services.admin_waitlist_service import AdminWaitlistService

router = APIRouter()
config_service = AdminConfigService()
waitlist_service = AdminWaitlistService()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str = "2.0.0"


class WelcomeResponse(BaseModel):
    """Welcome message response"""
    message: str
    version: str = "2.0.0"
    api_docs: str


@router.get("/", response_model=WelcomeResponse, tags=["main"])
async def root():
    """Root endpoint - welcome message"""
    return WelcomeResponse(
        message="Welcome to test.me API - AI-powered exam generation platform",
        version="2.0.0",
        api_docs="/docs"
    )


@router.get("/health", response_model=HealthResponse, tags=["main"])
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Service is running",
        version="2.0.0"
    )


@router.get("/api/health", response_model=HealthResponse, tags=["api"])
async def api_health():
    """API health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is running",
        version="2.0.0"
    )


@router.get(
    "/api/admin/config/status",
    response_model=BetaStatusResponse,
    tags=["api"],
)
async def beta_status():
    """Expose current beta configuration status to clients."""
    config = config_service.get_config()
    return BetaStatusResponse(
        status=config.status,
        allowed_emails=config.allowed_emails,
        updated_at=config.updated_at,
        updated_by=config.updated_by,
    )


@router.post(
    "/api/waitlist",
    response_model=WaitlistJoinResponse,
    tags=["api"],
)
async def join_waitlist(request: WaitlistJoinRequest):
    """Allow users to join the closed beta waitlist."""
    try:
        waitlist_service.add_entry(request.email, note=request.note)
        return WaitlistJoinResponse(
            success=True,
            message="승인 대기 목록에 등록되었습니다. 메일로 결과를 안내드릴게요.",
        )
    except ValueError as exc:
        code = str(exc)
        if code == "ALREADY_ALLOWED":
            return WaitlistJoinResponse(
                success=True,
                already_allowed=True,
                message="이미 클로즈베타에 초대된 이메일입니다. 기존 계정으로 로그인해주세요.",
            )
        if code == "ALREADY_PENDING":
            return WaitlistJoinResponse(
                success=True,
                already_pending=True,
                message="이미 승인 대기 중인 이메일입니다. 승인을 기다려주세요.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="대기열 등록에 실패했습니다.",
        ) from exc
