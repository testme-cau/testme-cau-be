"""
FastAPI admin routes (templates + JSON APIs)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import auth as firebase_auth

from app.models.admin import (
    AdminConfigResponse,
    AdminCredentialsUpdateRequest,
    AdminLoginRequest,
    AnalyticsSummaryResponse,
    FirebaseLoginRequest,
    ParametersUpdateRequest,
    StatusUpdateRequest,
)
from app.services.admin_analytics_service import AdminAnalyticsService
from app.services.admin_config_service import AdminConfigService
from app.services.admin_credentials_service import AdminCredentialService
from config import settings


router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

config_service = AdminConfigService()
credential_service = AdminCredentialService()
analytics_service = AdminAnalyticsService()


def _require_admin_gate(request: Request):
    if not request.session.get("admin_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 로그인 이후 이용해주세요.",
        )
    return True


def _require_full_admin(request: Request):
    session = request.session
    if not session.get("admin_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 로그인 이후 이용해주세요.",
        )
    if not session.get("firebase_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase OAuth 인증이 필요합니다.",
        )
    return session


@router.get("/", include_in_schema=False)
async def admin_root(request: Request):
    """Redirect users to the correct stage."""
    if request.session.get("firebase_authenticated"):
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    if request.session.get("admin_authenticated"):
        return RedirectResponse(url="/admin/oauth", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def admin_login_page(request: Request):
    if request.session.get("firebase_authenticated"):
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def admin_login(payload: AdminLoginRequest, request: Request):
    if credential_service.verify_credentials(payload.admin_id, payload.admin_pw):
        request.session["admin_authenticated"] = True
        request.session["admin_gate_user"] = payload.admin_id
        return {"success": True, "message": "관리자 인증이 완료되었습니다."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="잘못된 관리자 ID 또는 비밀번호입니다.",
    )


@router.get("/oauth", response_class=HTMLResponse, include_in_schema=False)
async def oauth_page(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    if request.session.get("firebase_authenticated"):
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin/oauth.html", {"request": request})


@router.post("/firebase-login")
async def firebase_login(request: Request, payload: FirebaseLoginRequest):
    _require_admin_gate(request)

    try:
        decoded = firebase_auth.verify_id_token(payload.id_token)
    except Exception as exc:  # pragma: no cover - firebase admin raises many subclasses
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase 토큰 검증에 실패했습니다: {exc}",
        ) from exc

    email = decoded.get("email") or payload.user.email
    config = config_service.get_config()
    if config.status.value == "closed_beta":
        normalized = (email or "").strip().lower()
        allowed = {item.lower() for item in config.allowed_emails}
        if normalized not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="클로즈베타 허용 이메일만 접근할 수 있습니다.",
            )

    request.session["firebase_authenticated"] = True
    request.session["firebase_token"] = payload.id_token
    request.session["firebase_user"] = {
        "uid": decoded.get("uid"),
        "email": email,
        "displayName": decoded.get("name") or payload.user.displayName,
        "photoURL": decoded.get("picture") or payload.user.photoURL,
    }
    request.session["firebase_authenticated_at"] = datetime.utcnow().isoformat()

    return {
        "success": True,
        "message": "Firebase 로그인에 성공했습니다.",
        "config": config.model_dump(),
    }


@router.post("/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return {"success": True, "message": "로그아웃 되었습니다."}


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard_page(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    if not request.session.get("firebase_authenticated"):
        return RedirectResponse(url="/admin/oauth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/api/session")
async def session_info(session=Depends(_require_full_admin)):
    config = config_service.get_config()
    return {
        "authenticated": True,
        "user": session.get("firebase_user", {}),
        "admin_gate_user": session.get("admin_gate_user"),
        "has_token": bool(session.get("firebase_token")),
        "config": config.model_dump(),
    }


@router.get("/api/firebase-config")
async def firebase_config(_: bool = Depends(_require_admin_gate)):
    return {
        "apiKey": settings.firebase_api_key,
        "authDomain": settings.firebase_auth_domain,
        "projectId": settings.firebase_project_id,
    }


@router.get("/api/config", response_model=AdminConfigResponse)
async def get_admin_config(_: dict = Depends(_require_full_admin)):
    return AdminConfigResponse(config=config_service.get_config())


@router.put("/api/config/status", response_model=AdminConfigResponse)
async def update_service_status(
    payload: StatusUpdateRequest,
    session=Depends(_require_full_admin),
):
    config = config_service.update_status(
        payload, updated_by=session.get("firebase_user", {}).get("email")
    )
    return AdminConfigResponse(config=config)


@router.put("/api/config/parameters", response_model=AdminConfigResponse)
async def update_parameters(
    payload: ParametersUpdateRequest,
    session=Depends(_require_full_admin),
):
    config = config_service.update_parameters(
        payload, updated_by=session.get("firebase_user", {}).get("email")
    )
    return AdminConfigResponse(config=config)


@router.get("/api/credentials")
async def get_credentials(_: dict = Depends(_require_full_admin)):
    metadata = credential_service.get_metadata()
    return {
        "success": True,
        "credentials": {
            "admin_id": metadata.admin_id,
            "updated_at": metadata.updated_at.isoformat()
            if metadata.updated_at
            else None,
            "updated_by": metadata.updated_by,
        },
    }


@router.put("/api/credentials")
async def rotate_credentials(
    payload: AdminCredentialsUpdateRequest,
    session=Depends(_require_full_admin),
):
    try:
        metadata = credential_service.update_credentials(
            current_password=payload.current_password,
            new_admin_id=payload.new_admin_id,
            new_password=payload.new_password,
            updated_by=session.get("firebase_user", {}).get("email"),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        "message": "관리자 계정 정보가 갱신되었습니다.",
        "credentials": {
            "admin_id": metadata.admin_id,
            "updated_at": metadata.updated_at.isoformat()
            if metadata.updated_at
            else None,
            "updated_by": metadata.updated_by,
        },
    }


@router.get("/api/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(_: dict = Depends(_require_full_admin)):
    return analytics_service.get_summary()
