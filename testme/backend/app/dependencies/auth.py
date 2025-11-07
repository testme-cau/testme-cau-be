"""
Authentication dependencies for FastAPI
"""
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from firebase_admin import auth, firestore
import logging

logger = logging.getLogger(__name__)


def ensure_default_subject(user_uid: str) -> str:
    """
    Ensure user has a default subject. If not, create one.
    
    Args:
        user_uid: User's Firebase UID
    
    Returns:
        str: Default subject ID
    """
    try:
        db = firestore.client()
        subjects_ref = db.collection('users').document(user_uid).collection('subjects')
        
        # Check if user has any subjects
        subjects = list(subjects_ref.limit(1).stream())
        
        if not subjects:
            # Create default subject
            default_subject_ref = subjects_ref.document()
            subject_id = default_subject_ref.id
            
            default_subject_data = {
                'subject_id': subject_id,
                'user_id': user_uid,
                'name': '기본',
                'description': '기본 과목',
                'semester': None,
                'year': None,
                'color': '#6B7280',  # Gray color
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': None
            }
            
            default_subject_ref.set(default_subject_data)
            logger.info(f'Created default subject for user {user_uid}')
            return subject_id
        
        # Return first subject ID if exists
        return subjects[0].id
        
    except Exception as e:
        logger.error(f'Failed to ensure default subject: {e}')
        # Don't raise exception, just log it
        return None


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
                    user_uid = decoded_token['uid']
                    
                    # Ensure user has a default subject
                    ensure_default_subject(user_uid)
                    
                    return {
                        'uid': user_uid,
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
        
        user_uid = decoded_token['uid']
        
        # Ensure user has a default subject
        ensure_default_subject(user_uid)
        
        # Return user info
        return {
            'uid': user_uid,
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

