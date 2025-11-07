"""
Subject routes (subject/course management)
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.models.requests import SubjectCreateRequest, SubjectUpdateRequest
from app.models.responses import SubjectResponse, SubjectListResponse, SuccessResponse
from app.models.domain import Subject

router = APIRouter(tags=["subjects"])


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: SubjectCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new subject
    
    - **name**: Subject name (required)
    - **description**: Subject description (optional)
    - **semester**: Semester (optional, e.g., "2025-1")
    - **year**: Year (optional)
    - **color**: Color hex code (optional, e.g., "#FF5733")
    
    Requires authentication
    
    Returns:
        SubjectResponse with created subject information
    """
    try:
        user_uid = user['uid']
        
        # Create subject document in Firestore
        db = firestore.client()
        subjects_ref = db.collection('users').document(user_uid).collection('subjects')
        subject_ref = subjects_ref.document()
        subject_id = subject_ref.id
        
        subject_data = {
            'subject_id': subject_id,
            'user_id': user_uid,
            'name': request.name,
            'description': request.description,
            'semester': request.semester,
            'year': request.year,
            'color': request.color,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': None
        }
        
        subject_ref.set(subject_data)
        
        # Fetch the created subject to get the server timestamp
        created_subject = subject_ref.get()
        subject_dict = created_subject.to_dict()
        
        return SubjectResponse(
            success=True,
            subject=Subject(**subject_dict)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create subject: {str(e)}'
        )


@router.get("", response_model=SubjectListResponse)
async def list_subjects(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all subjects for current user
    
    Requires authentication
    
    Returns:
        SubjectListResponse with list of subjects
    """
    try:
        user_uid = user['uid']
        
        # Get all subjects for user
        db = firestore.client()
        subjects_ref = db.collection('users').document(user_uid).collection('subjects')
        subjects = subjects_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        
        subject_list = []
        for subject_doc in subjects:
            subject_data = subject_doc.to_dict()
            subject_list.append(Subject(**subject_data))
        
        return SubjectListResponse(
            success=True,
            subjects=subject_list,
            count=len(subject_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to list subjects: {str(e)}'
        )


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get subject details
    
    - **subject_id**: Subject ID
    
    Requires authentication
    
    Returns:
        SubjectResponse with subject information
    """
    try:
        user_uid = user['uid']
        
        # Get subject from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subject not found'
            )
        
        subject_data = subject_doc.to_dict()
        
        # Verify ownership
        if subject_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        return SubjectResponse(
            success=True,
            subject=Subject(**subject_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get subject: {str(e)}'
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    request: SubjectUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update subject
    
    - **subject_id**: Subject ID
    - **name**: Subject name (optional)
    - **description**: Subject description (optional)
    - **semester**: Semester (optional)
    - **year**: Year (optional)
    - **color**: Color hex code (optional)
    
    Requires authentication
    
    Returns:
        SubjectResponse with updated subject information
    """
    try:
        user_uid = user['uid']
        
        # Get subject from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subject not found'
            )
        
        subject_data = subject_doc.to_dict()
        
        # Verify ownership
        if subject_data.get('user_id') != user_uid:
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
        if request.semester is not None:
            update_data['semester'] = request.semester
        if request.year is not None:
            update_data['year'] = request.year
        if request.color is not None:
            update_data['color'] = request.color
        
        if update_data:
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            subject_ref.update(update_data)
        
        # Fetch updated subject
        updated_subject = subject_ref.get()
        subject_dict = updated_subject.to_dict()
        
        return SubjectResponse(
            success=True,
            subject=Subject(**subject_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update subject: {str(e)}'
        )


@router.delete("/{subject_id}", response_model=SuccessResponse)
async def delete_subject(
    subject_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete subject
    
    - **subject_id**: Subject ID
    
    Note: This will also delete all PDFs and exams under this subject.
    
    Requires authentication
    
    Returns:
        SuccessResponse
    """
    try:
        user_uid = user['uid']
        
        # Get subject from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subject not found'
            )
        
        subject_data = subject_doc.to_dict()
        
        # Verify ownership
        if subject_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        # Delete all pdfs under this subject
        pdfs_ref = subject_ref.collection('pdfs')
        pdfs = pdfs_ref.stream()
        for pdf_doc in pdfs:
            pdf_doc.reference.delete()
        
        # Delete all exams under this subject
        exams_ref = subject_ref.collection('exams')
        exams = exams_ref.stream()
        for exam_doc in exams:
            exam_doc.reference.delete()
        
        # Delete the subject
        subject_ref.delete()
        
        return SuccessResponse(
            success=True,
            message=f'Subject {subject_id} deleted successfully'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to delete subject: {str(e)}'
        )

