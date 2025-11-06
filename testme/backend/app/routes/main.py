"""
Main API routes (root and health endpoints)
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


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
