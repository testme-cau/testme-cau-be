"""
Group routes (group management)
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.models.requests import GroupCreateRequest, GroupUpdateRequest
from app.models.responses import GroupResponse, GroupListResponse, SuccessResponse
from app.models.domain import Group

router = APIRouter(tags=["groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: GroupCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new group
    
    - **name**: Group name (required)
    - **description**: Group description (optional)
    - **color**: Color hex code (optional, e.g., "#FF5733")
    - **icon**: Icon identifier (optional)
    
    Requires authentication
    
    Returns:
        GroupResponse with created group information
    """
    try:
        user_uid = user['uid']
        
        # Create group document in Firestore
        db = firestore.client()
        groups_ref = db.collection('users').document(user_uid).collection('groups')
        group_ref = groups_ref.document()
        group_id = group_ref.id
        
        group_data = {
            'group_id': group_id,
            'user_id': user_uid,
            'name': request.name,
            'description': request.description,
            'color': request.color,
            'icon': request.icon,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': None
        }
        
        group_ref.set(group_data)
        
        # Fetch the created group to get the server timestamp
        created_group = group_ref.get()
        group_dict = created_group.to_dict()
        
        return GroupResponse(
            success=True,
            group=Group(**group_dict)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create group: {str(e)}'
        )


@router.get("", response_model=GroupListResponse)
async def list_groups(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all groups for current user
    
    Requires authentication
    
    Returns:
        GroupListResponse with list of groups
    """
    try:
        user_uid = user['uid']
        
        # Get all groups for user
        db = firestore.client()
        groups_ref = db.collection('users').document(user_uid).collection('groups')
        groups = groups_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        
        group_list = []
        for group_doc in groups:
            group_data = group_doc.to_dict()
            group_list.append(Group(**group_data))
        
        return GroupListResponse(
            success=True,
            groups=group_list,
            count=len(group_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to list groups: {str(e)}'
        )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get group details
    
    - **group_id**: Group ID
    
    Requires authentication
    
    Returns:
        GroupResponse with group information
    """
    try:
        user_uid = user['uid']
        
        # Get group from Firestore
        db = firestore.client()
        group_ref = db.collection('users').document(user_uid).collection('groups').document(group_id)
        group_doc = group_ref.get()
        
        if not group_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found'
            )
        
        group_data = group_doc.to_dict()
        
        # Verify ownership
        if group_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        return GroupResponse(
            success=True,
            group=Group(**group_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get group: {str(e)}'
        )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    request: GroupUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update group
    
    - **group_id**: Group ID
    - **name**: Group name (optional)
    - **description**: Group description (optional)
    - **color**: Color hex code (optional)
    - **icon**: Icon identifier (optional)
    
    Requires authentication
    
    Returns:
        GroupResponse with updated group information
    """
    try:
        user_uid = user['uid']
        
        # Get group from Firestore
        db = firestore.client()
        group_ref = db.collection('users').document(user_uid).collection('groups').document(group_id)
        group_doc = group_ref.get()
        
        if not group_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found'
            )
        
        group_data = group_doc.to_dict()
        
        # Verify ownership
        if group_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        # Update only provided fields
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.description is not None:
            update_data['description'] = request.description
        if request.color is not None:
            update_data['color'] = request.color
        if request.icon is not None:
            update_data['icon'] = request.icon
        
        if update_data:
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            group_ref.update(update_data)
        
        # Fetch updated group
        updated_group = group_ref.get()
        group_dict = updated_group.to_dict()
        
        return GroupResponse(
            success=True,
            group=Group(**group_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update group: {str(e)}'
        )


@router.delete("/{group_id}", response_model=SuccessResponse)
async def delete_group(
    group_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete group
    
    - **group_id**: Group ID
    
    Note: This will set group_id to null for all subjects in this group.
    
    Requires authentication
    
    Returns:
        SuccessResponse
    """
    try:
        user_uid = user['uid']
        
        # Get group from Firestore
        db = firestore.client()
        group_ref = db.collection('users').document(user_uid).collection('groups').document(group_id)
        group_doc = group_ref.get()
        
        if not group_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found'
            )
        
        group_data = group_doc.to_dict()
        
        # Verify ownership
        if group_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        # Update all subjects with this group_id to set group_id to None
        subjects_ref = db.collection('users').document(user_uid).collection('subjects')
        subjects = subjects_ref.where('group_id', '==', group_id).stream()
        
        for subject_doc in subjects:
            subject_doc.reference.update({'group_id': None, 'updated_at': firestore.SERVER_TIMESTAMP})
        
        # Delete the group
        group_ref.delete()
        
        return SuccessResponse(
            success=True,
            message=f'Group {group_id} deleted successfully'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to delete group: {str(e)}'
        )

