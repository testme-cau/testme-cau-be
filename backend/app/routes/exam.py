"""
Exam routes (exam generation and management) - Subject-based structure
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path

from app.dependencies.auth import get_current_user
from app.dependencies.ai_service import get_ai_service_dependency
from app.dependencies.service import get_exam_service
from app.services.ai_service_interface import AIServiceInterface
from app.services.exam_service import ExamService
from app.models.requests import ExamGenerationRequest
from app.models.responses import ExamResponse, ExamListResponse, ExamInfo

router = APIRouter(tags=["exam"])


@router.post("/subjects/{subject_id}/exams/generate", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def generate_exam(
    subject_id: str = Path(..., description="Subject ID"),
    request: ExamGenerationRequest = ...,
    user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIServiceInterface = Depends(get_ai_service_dependency),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    Generate exam from PDF under a specific subject
    
    - **subject_id**: Subject ID
    - **pdf_id**: UUID of the uploaded PDF
    - **num_questions**: Number of questions to generate (1-50)
    - **difficulty**: Difficulty level (easy, medium, hard)
    - **ai_provider**: AI provider to use (gpt or gemini) - optional query parameter
    
    Requires authentication
    
    Returns:
        ExamResponse with generated questions
    """
    result = exam_service.generate_exam(
        user['uid'],
        subject_id,
        request,
        ai_service,
        language='ko'
    )
    
    # Return exam object wrapped in ExamResponse
    return ExamResponse(
        success=True,
        exam=result
    )


@router.get("/subjects/{subject_id}/exams/{exam_id}", response_model=Dict[str, Any])
async def get_exam(
    subject_id: str = Path(..., description="Subject ID"),
    exam_id: str = Path(..., description="Exam ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    Get exam details
    
    - **subject_id**: Subject ID
    - **exam_id**: Exam ID
    
    Requires authentication
    
    Returns:
        Exam details
    """
    exam = exam_service.get_exam(user['uid'], subject_id, exam_id)
    return {
        'success': True,
        'exam': exam.dict()
    }


@router.get("/subjects/{subject_id}/exams", response_model=ExamListResponse)
async def list_exams(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    List all exams for a specific subject
    
    - **subject_id**: Subject ID
    
    Requires authentication
    
    Returns:
        ExamListResponse with list of exams
    """
    exams = exam_service.list_exams(user['uid'], subject_id)
    
    exam_list = [
        ExamInfo(
            exam_id=exam.exam_id,
            pdf_id=exam.pdf_id,
            num_questions=exam.num_questions,
            total_points=exam.total_points,
            difficulty=exam.difficulty,
            created_at=exam.created_at,
            status=exam.status,
            ai_provider=exam.ai_provider
        )
        for exam in exams
    ]
    
    return ExamListResponse(
        success=True,
        exams=exam_list,
        count=len(exam_list)
    )
