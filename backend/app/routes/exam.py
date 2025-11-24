"""
Exam routes (exam generation and management) - Subject-based structure
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, BackgroundTasks

from app.dependencies.auth import get_current_user
from app.dependencies.ai_service import get_ai_service_dependency
from app.dependencies.service import get_exam_service
from app.services.ai_service_interface import AIServiceInterface
from app.services.exam_service import ExamService
from app.models.requests import ExamGenerationRequest
from app.models.responses import (
    ExamResponse,
    ExamListResponse,
    ExamInfo,
    ExamJobResponse,
    ExamJobListResponse,
    GradingJobResponse,
    GradingJobListResponse,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["exam"])


def _get_ai_model_name(ai_service: AIServiceInterface) -> Optional[str]:
    """Best-effort extraction of the concrete model name from the AI service."""
    for attr in ("model_name", "model"):
        value = getattr(ai_service, attr, None)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
    return None


@router.post(
    "/subjects/{subject_id}/exams/generate",
    response_model=ExamJobResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def generate_exam(
    background_tasks: BackgroundTasks,
    subject_id: str = Path(..., description="Subject ID"),
    request: ExamGenerationRequest = ...,
    user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIServiceInterface = Depends(get_ai_service_dependency),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    Generate exam from PDF under a specific subject (Async)
    
    This endpoint immediately returns a placeholder exam with status='pending'.
    The actual exam generation happens in the background.
    
    - **subject_id**: Subject ID
    - **pdf_ids**: List of PDF UUIDs (1-10)
    - **num_questions**: Number of questions to generate (1-50)
    - **difficulty**: Difficulty level (easy, medium, hard)
    - **ai_provider**: AI provider to use (gpt or gemini) - optional query parameter
    
    Requires authentication
    
    Returns:
        ExamResponse with placeholder exam (status='pending')
        
    Poll GET /subjects/{subject_id}/exams/{exam_id} to check status:
        - pending: Initial state
        - processing: Generation in progress
        - completed: Exam ready
        - failed: Generation failed
    """
    logger.info(f"Received async exam generation request for subject {subject_id}")
    
    ai_model_name = _get_ai_model_name(ai_service)

    # Create exam generation job
    job = exam_service.enqueue_exam_generation_job(
        user['uid'],
        subject_id,
        request,
        ai_service.provider_name,
        ai_model_name
    )
    
    # Schedule background task for actual generation
    background_tasks.add_task(
        exam_service.process_exam_generation_job,
        user['uid'],
        subject_id,
        job['job_id'],
        request,
        ai_service.provider_name,
        job.get('language'),
        ai_model_name
    )
    
    logger.info(f"Exam generation job created with ID {job['job_id']}, background generation scheduled")
    
    return ExamJobResponse(success=True, job=job)


@router.get(
    "/subjects/{subject_id}/exam-jobs",
    response_model=ExamJobListResponse
)
async def list_exam_jobs(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    jobs = exam_service.list_exam_jobs(user['uid'], subject_id)
    return {"success": True, "jobs": jobs}


@router.get(
    "/subjects/{subject_id}/exam-jobs/{job_id}",
    response_model=ExamJobResponse
)
async def get_exam_job(
    subject_id: str = Path(..., description="Subject ID"),
    job_id: str = Path(..., description="Job ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    job = exam_service.get_exam_job(user['uid'], subject_id, job_id)
    return {"success": True, "job": job}


@router.delete(
    "/subjects/{subject_id}/exam-jobs/{job_id}",
    response_model=ExamJobResponse
)
async def cancel_exam_job(
    subject_id: str = Path(..., description="Subject ID"),
    job_id: str = Path(..., description="Job ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    job = exam_service.cancel_exam_job(user['uid'], subject_id, job_id)
    return {"success": True, "job": job}


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
        Exam details (includes error_message if status is 'failed')
    """
    exam_data = exam_service.exam_repo.get_by_id_with_ownership(user['uid'], subject_id, exam_id)
    return {
        'success': True,
        'exam': exam_data
    }


@router.get("/subjects/{subject_id}/exams")
async def list_exams(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    List all exams for a specific subject with submission status
    
    - **subject_id**: Subject ID
    
    Requires authentication
    
    Returns:
        ExamListResponse with list of exams including submission_status
    """
    exams = exam_service.list_exams(user['uid'], subject_id)
    
    return {
        'success': True,
        'exams': exams,
        'count': len(exams)
    }


@router.delete("/subjects/{subject_id}/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    subject_id: str = Path(..., description="Subject ID"),
    exam_id: str = Path(..., description="Exam ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    Delete an exam
    
    - **subject_id**: Subject ID
    - **exam_id**: Exam ID to delete
    
    Requires authentication
    
    Returns:
        204 No Content on success
    """
    exam_service.delete_exam(user['uid'], subject_id, exam_id)
    return None


@router.post(
    "/subjects/{subject_id}/exams/{exam_id}/submit",
    response_model=GradingJobResponse
)
async def submit_exam(
    background_tasks: BackgroundTasks,
    subject_id: str = Path(..., description="Subject ID"),
    exam_id: str = Path(..., description="Exam ID"),
    answers: List[Dict[str, Any]] = Body(..., description="List of answers"),
    user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIServiceInterface = Depends(get_ai_service_dependency),
    exam_service: ExamService = Depends(get_exam_service)
):
    """
    Submit exam answers and get automatic grading
    
    - **subject_id**: Subject ID
    - **exam_id**: Exam ID  
    - **answers**: [{"question_id": 1, "answer": "text"}, ...]
    
    Returns:
        Submission ID, status, and grading result (if completed)
    """
    result = exam_service.submit_exam_async(
        user['uid'],
        subject_id,
        exam_id,
        answers,
        ai_service
    )

    background_tasks.add_task(
        exam_service.process_grading_job,
        user['uid'],
        subject_id,
        result['job']['job_id'],
        exam_id,
        result['submission_id'],
        ai_service.provider_name
    )
    
    return GradingJobResponse(
        success=True,
        submission_id=result['submission_id'],
        job=result['job']
    )


@router.get(
    "/subjects/{subject_id}/grading-jobs",
    response_model=GradingJobListResponse
)
async def list_grading_jobs(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    jobs = exam_service.list_grading_jobs(user['uid'], subject_id)
    return {"success": True, "jobs": jobs}


@router.get(
    "/subjects/{subject_id}/grading-jobs/{job_id}",
    response_model=GradingJobResponse
)
async def get_grading_job(
    subject_id: str = Path(..., description="Subject ID"),
    job_id: str = Path(..., description="Job ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    job = exam_service.get_grading_job(user['uid'], subject_id, job_id)
    return {"success": True, "job": job, "submission_id": job.get('submission_id', '')}


@router.delete(
    "/subjects/{subject_id}/grading-jobs/{job_id}",
    response_model=GradingJobResponse
)
async def cancel_grading_job(
    subject_id: str = Path(..., description="Subject ID"),
    job_id: str = Path(..., description="Job ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    exam_service: ExamService = Depends(get_exam_service)
):
    job = exam_service.cancel_grading_job(user['uid'], subject_id, job_id)
    return {"success": True, "job": job, "submission_id": job.get('submission_id', '')}


@router.get("/subjects/{subject_id}/exams/{exam_id}/submission")
async def get_my_submission(
    subject_id: str = Path(..., description="Subject ID"),
    exam_id: str = Path(..., description="Exam ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get my submission and grading result for an exam
    
    Returns:
        Submission details with status and grading result
    """
    from app.repositories.submission import SubmissionRepository
    submission_repo = SubmissionRepository()
    
    submission = submission_repo.get_by_user_and_exam(
        user['uid'],
        subject_id,
        exam_id
    )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submission found for this exam"
        )
    
    return {
        'success': True,
        'submission': submission
    }

