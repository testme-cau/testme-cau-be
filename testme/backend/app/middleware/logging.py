"""
Logging middleware for request/response logging
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger(__name__)


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
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
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
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"({process_time:.3f}s)"
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

