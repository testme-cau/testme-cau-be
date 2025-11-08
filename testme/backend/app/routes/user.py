"""
User routes for profile management
"""
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.models.requests import UserUpdateRequest
from app.models.responses import SuccessResponse
from app.utils.language_utils import get_supported_languages

router = APIRouter(tags=["user"])


@router.get("/languages")
async def get_languages():
    """
    Get list of supported languages
    
    Returns list of available languages with:
    - code: ISO 639-1 language code
    - name: English name
    - native_name: Name in native language
    - flag: Emoji flag
    
    No authentication required (public endpoint)
    """
    return {
        'success': True,
        'languages': get_supported_languages(),
        'count': len(get_supported_languages())
    }


@router.get("/profile")
async def get_user_profile(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user's profile information
    
    Returns user profile including language preference
    """
    try:
        user_uid = user['uid']
        
        # Get user from Firestore
        db = firestore.client()
        user_ref = db.collection('users').document(user_uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
        else:
            # Create default user document if doesn't exist
            user_data = {
                'uid': user_uid,
                'email': user.get('email'),
                'display_name': user.get('display_name'),
                'photo_url': user.get('photo_url'),
                'language_preference': 'ko',  # Default to Korean
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            user_ref.set(user_data)
        
        return {
            'success': True,
            'user': user_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/profile", response_model=SuccessResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update current user's profile
    
    - **display_name**: User display name (optional)
    - **language_preference**: Language code (ISO 639-1: ko, en, ja, zh, etc.)
    
    Requires authentication
    """
    try:
        user_uid = user['uid']
        
        # Build update data
        update_data = {}
        if request.display_name is not None:
            update_data['display_name'] = request.display_name
        if request.language_preference is not None:
            update_data['language_preference'] = request.language_preference
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No fields to update'
            )
        
        update_data['updated_at'] = datetime.utcnow()
        
        # Update user in Firestore
        db = firestore.client()
        user_ref = db.collection('users').document(user_uid)
        
        # Check if user document exists
        user_doc = user_ref.get()
        if not user_doc.exists:
            # Create new user document
            user_data = {
                'uid': user_uid,
                'email': user.get('email'),
                'display_name': request.display_name or user.get('display_name'),
                'photo_url': user.get('photo_url'),
                'language_preference': request.language_preference or 'ko',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            user_ref.set(user_data)
        else:
            # Update existing document
            user_ref.update(update_data)
        
        return {
            'success': True,
            'message': 'User profile updated successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

