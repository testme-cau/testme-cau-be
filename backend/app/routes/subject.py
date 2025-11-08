"""
Subject routes (subject/course management)
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.dependencies.service import get_subject_service
from app.services.subject_service import SubjectService
from app.models.requests import SubjectCreateRequest, SubjectUpdateRequest
from app.models.responses import SubjectResponse, SubjectListResponse, SuccessResponse

router = APIRouter(tags=["subjects"])


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: SubjectCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """
    Create a new subject
    
    - **name**: Subject name (required)
    - **description**: Subject description (optional)
    - **group_id**: Group ID (optional)
    - **color**: Color hex code (optional, e.g., "#FF5733")
    - **language_preference**: Language preference (optional, ISO 639-1 code)
    
    Requires authentication
    
    Returns:
        SubjectResponse with created subject information
    """
    subject = subject_service.create_subject(user['uid'], request)
    return SubjectResponse(success=True, subject=subject)


@router.get("", response_model=SubjectListResponse)
async def list_subjects(
    user: Dict[str, Any] = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """
    List all subjects for current user
    
    Requires authentication
    
    Returns:
        SubjectListResponse with list of subjects
    """
    subjects = subject_service.list_subjects(user['uid'])
    return SubjectListResponse(
        success=True,
        subjects=subjects,
        count=len(subjects)
    )


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """
    Get subject details
    
    - **subject_id**: Subject ID
    
    Requires authentication
    
    Returns:
        SubjectResponse with subject information
    """
    subject = subject_service.get_subject(user['uid'], subject_id)
    return SubjectResponse(success=True, subject=subject)


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    request: SubjectUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """
    Update subject
    
    - **subject_id**: Subject ID
    - **name**: Subject name (optional)
    - **description**: Subject description (optional)
    - **group_id**: Group ID (optional)
    - **color**: Color hex code (optional)
    - **language_preference**: Language preference (optional, ISO 639-1 code)
    
    Requires authentication
    
    Returns:
        SubjectResponse with updated subject information
    """
    subject = subject_service.update_subject(user['uid'], subject_id, request)
    return SubjectResponse(success=True, subject=subject)


@router.delete("/{subject_id}", response_model=SuccessResponse)
async def delete_subject(
    subject_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """
    Delete subject
    
    - **subject_id**: Subject ID
    
    Note: This will also delete all PDFs and exams under this subject.
    
    Requires authentication
    
    Returns:
        SuccessResponse
    """
    subject_service.delete_subject(user['uid'], subject_id)
    return SuccessResponse(
        success=True,
        message=f'Subject {subject_id} deleted successfully'
    )

