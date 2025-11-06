"""
Authentication dependencies for FastAPI
"""
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from firebase_admin import auth
import logging

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    
    Supports two authentication methods:
    1. Firebase ID token from Authorization header (for mobile app)
    2. Session-based auth from admin web interface (for testing)
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Dict with user information (uid, email, firebase_user)
    
    Raises:
        HTTPException: If authentication fails
    """
    # Check if user is authenticated via admin session (if SessionMiddleware is installed)
    try:
        if hasattr(request.state, '_session'):  # Check if session is available
            session = request.session
            if session.get('firebase_authenticated') and session.get('firebase_token'):
                # Admin session authentication
                id_token = session.get('firebase_token')
                
                # Verify the session token is still valid
                try:
                    decoded_token = auth.verify_id_token(id_token)
                    return {
                        'uid': decoded_token['uid'],
                        'email': decoded_token.get('email'),
                        'firebase_user': decoded_token
                    }
                except Exception as e:
                    logger.error(f'Session token verification failed: {e}')
                    # Clear invalid session
                    session.pop('firebase_authenticated', None)
                    session.pop('firebase_token', None)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Session expired, please login again'
                    )
    except (AttributeError, AssertionError):
        # SessionMiddleware not installed, skip session authentication
        pass
    
    # Standard Firebase token authentication (from Authorization header)
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No token provided'
        )
    
    # Extract token
    id_token = auth_header.split('Bearer ')[1]
    
    try:
        # Verify token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        
        # Return user info
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'firebase_user': decoded_token
        }
        
    except Exception as e:
        logger.error(f'Token verification failed: {e}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )


async def get_optional_user(request: Request) -> Dict[str, Any] | None:
    """
    Optional authentication dependency
    Returns user if authenticated, None otherwise
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

