"""
Logging middleware for request/response logging
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from config import settings

logger = logging.getLogger(__name__)
ENV_LABEL = (settings.environment or "development").upper()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request details and response status.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint to call
            
        Returns:
            Response from the endpoint
        """
        # Start timer
        start_time = time.time()
        
        # Log request
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            "[%s] Request: %s %s from %s",
            ENV_LABEL,
            request.method,
            request.url.path,
            client_host,
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "[%s] Response: %s for %s %s (%.3fs)",
            ENV_LABEL,
            response.status_code,
            request.method,
            request.url.path,
            process_time,
        )
        
        # Add process time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def setup_logging_middleware(app):
    """
    Setup logging middleware for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(LoggingMiddleware)
    logger.info("Logging middleware configured")

