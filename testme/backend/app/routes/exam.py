"""
Exam routes (exam generation and management) - Subject-based structure
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.dependencies.ai_service import get_ai_service_dependency
from app.services.ai_service_interface import AIServiceInterface
from app.services.firebase_storage import FirebaseStorageService
from app.models.requests import ExamGenerationRequest
from app.models.responses import ExamResponse, ExamListResponse, ExamInfo
from app.models.domain import Exam

router = APIRouter(tags=["exam"])


@router.post("/subjects/{subject_id}/exams/generate", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def generate_exam(
    subject_id: str = Path(..., description="Subject ID"),
    request: ExamGenerationRequest = ...,
    user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIServiceInterface = Depends(get_ai_service_dependency)
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
    try:
        user_uid = user['uid']
        pdf_id = request.pdf_id
        num_questions = request.num_questions
        difficulty = request.difficulty
        
        # Verify subject exists
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subject not found'
            )
        
        # Get PDF metadata from Firestore
        pdf_ref = subject_ref.collection('pdfs').document(pdf_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='PDF not found'
            )
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        # Download PDF from Firebase Storage
        storage_service = FirebaseStorageService()
        pdf_bytes = storage_service.download_file(pdf_data['storage_path'])
        
        # Generate exam using AI service
        generation_result = ai_service.generate_exam_from_pdf(
            pdf_bytes,
            pdf_data['original_filename'],
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        if not generation_result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate exam: {generation_result.get('error', 'Unknown error')}"
            )
        
        exam_data = generation_result['exam']
        
        # Save exam to Firestore under subject
        exams_ref = subject_ref.collection('exams')
        exam_ref = exams_ref.document()
        exam_id = exam_ref.id
        
        exam_record = {
            'exam_id': exam_id,
            'subject_id': subject_id,
            'pdf_id': pdf_id,
            'user_id': user_uid,
            'questions': exam_data['questions'],
            'total_points': exam_data['total_points'],
            'estimated_time': exam_data['estimated_time'],
            'num_questions': num_questions,
            'difficulty': difficulty,
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'active',
            'ai_provider': ai_service.provider_name
        }
        
        exam_ref.set(exam_record)
        
        return ExamResponse(
            success=True,
            exam_id=exam_id,
            questions=exam_data['questions'],
            total_points=exam_data['total_points'],
            estimated_time=exam_data['estimated_time'],
            created_at=datetime.utcnow(),
            ai_provider=ai_service.provider_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Exam generation failed: {str(e)}'
        )


@router.get("/subjects/{subject_id}/exams/{exam_id}", response_model=Dict[str, Any])
async def get_exam(
    subject_id: str = Path(..., description="Subject ID"),
    exam_id: str = Path(..., description="Exam ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get exam details
    
    - **subject_id**: Subject ID
    - **exam_id**: Exam ID
    
    Requires authentication
    
    Returns:
        Exam details
    """
    try:
        user_uid = user['uid']
        
        # Get exam from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        exam_ref = subject_ref.collection('exams').document(exam_id)
        exam_doc = exam_ref.get()
        
        if not exam_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Exam not found'
            )
        
        exam_data = exam_doc.to_dict()
        
        # Verify ownership
        if exam_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Unauthorized'
            )
        
        return {
            'success': True,
            'exam': exam_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get exam: {str(e)}'
        )


@router.get("/subjects/{subject_id}/exams", response_model=ExamListResponse)
async def list_exams(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all exams for a specific subject
    
    - **subject_id**: Subject ID
    
    Requires authentication
    
    Returns:
        ExamListResponse with list of exams
    """
    try:
        user_uid = user['uid']
        
        # Verify subject exists
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subject not found'
            )
        
        # Get all exams for subject
        exams_ref = subject_ref.collection('exams')
        exams = exams_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        
        exam_list = []
        for exam in exams:
            exam_data = exam.to_dict()
            exam_list.append(ExamInfo(
                exam_id=exam_data['exam_id'],
                pdf_id=exam_data.get('pdf_id'),
                num_questions=exam_data.get('num_questions', 0),
                total_points=exam_data.get('total_points', 0),
                difficulty=exam_data.get('difficulty', 'medium'),
                created_at=exam_data.get('created_at', datetime.utcnow()),
                status=exam_data.get('status', 'active'),
                ai_provider=exam_data.get('ai_provider')
            ))
        
        return ExamListResponse(
            success=True,
            exams=exam_list,
            count=len(exam_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to list exams: {str(e)}'
        )
