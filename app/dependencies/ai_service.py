"""
AI Service dependency for FastAPI
"""
from typing import Optional
from fastapi import Query, HTTPException, status

from app.services.ai_service_interface import AIServiceInterface
from app.services.ai_factory import get_ai_service, get_supported_providers


async def get_ai_service_dependency(
    ai_provider: Optional[str] = Query(
        default=None,
        description="AI provider to use (gpt or gemini). If not specified, uses default from settings."
    )
) -> AIServiceInterface:
    """
    FastAPI dependency to inject AI service
    
    Args:
        ai_provider: Optional AI provider from query parameter
    
    Returns:
        AIServiceInterface implementation
    
    Raises:
        HTTPException: If provider is not supported
    """
    try:
        return get_ai_service(ai_provider)
    except ValueError as e:
        supported = get_supported_providers()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid AI provider. Supported providers: {', '.join(supported)}"
        )

