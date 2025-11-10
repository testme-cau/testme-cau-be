"""
Exam service for business logic related to exam generation and grading
"""
from typing import List, Dict, Any
from app.repositories.exam import ExamRepository
from app.repositories.subject import SubjectRepository
from app.services.pdf_service import PDFService
from app.services.ai_service_interface import AIServiceInterface
from app.models.domain import Exam
from app.models.requests import ExamGenerationRequest
from app.utils.exam_validator import validate_exam_response
from fastapi import HTTPException, status
import logging


logger = logging.getLogger(__name__)


class ExamService:
    """Service for exam business logic"""
    
    def __init__(
        self,
        exam_repo: ExamRepository = None,
        subject_repo: SubjectRepository = None,
        pdf_service: PDFService = None
    ):
        self.exam_repo = exam_repo or ExamRepository()
        self.subject_repo = subject_repo or SubjectRepository()
        self.pdf_service = pdf_service or PDFService()
    
    def generate_exam(
        self,
        user_id: str,
        subject_id: str,
        request: ExamGenerationRequest,
        ai_service: AIServiceInterface,
        language: str = 'ko'
    ) -> Dict[str, Any]:
        """
        Generate exam from one or multiple PDFs.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            request: Exam generation request (with pdf_ids list)
            ai_service: AI service instance
            language: Language code
            
        Returns:
            Generated exam data
        """
        # Verify subject exists
        subject_data = self.subject_repo.get_by_id_with_ownership(user_id, subject_id)
        
        # Collect PDF bytes and filenames for all requested PDFs
        pdf_bytes_list = []
        for pdf_id in request.pdf_ids:
            # Get PDF and verify ownership
            pdf_data = self.pdf_service.get_pdf(user_id, subject_id, pdf_id)
            
            # Download PDF bytes
            pdf_bytes = self.pdf_service.download_pdf_bytes(user_id, subject_id, pdf_id)
            
            pdf_bytes_list.append((pdf_bytes, pdf_data.original_filename))
        
        # Determine language (subject > user > default)
        final_language = subject_data.get('language_preference', language)
        
        # Generate exam using appropriate AI service method
        if len(pdf_bytes_list) == 1:
            # Single PDF - use original method
            generation_result = ai_service.generate_exam_from_pdf(
                pdf_bytes_list[0][0],  # pdf_bytes
                pdf_bytes_list[0][1],  # original_filename
                num_questions=request.num_questions,
                difficulty=request.difficulty,
                language=final_language
            )
        else:
            # Multiple PDFs - use new method
            generation_result = ai_service.generate_exam_from_multiple_pdfs(
                pdf_bytes_list,
                num_questions=request.num_questions,
                difficulty=request.difficulty,
                language=final_language
            )
        
        if not generation_result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate exam: {generation_result.get('error', 'Unknown error')}"
            )
        
        raw_exam_data = generation_result['exam']
        
        # Validate and refine AI response
        try:
            exam_data = validate_exam_response(raw_exam_data, request.num_questions)
            if exam_data.get('validation_issues'):
                logger.warning(f"Exam validation issues: {exam_data['validation_issues']}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid exam data from AI: {str(e)}"
            )
        
        # Save exam to Firestore
        exam_record = {
            'subject_id': subject_id,
            'pdf_id': request.pdf_ids[0],  # First PDF for backward compatibility
            'pdf_ids': request.pdf_ids,  # New field: all PDFs
            'user_id': user_id,
            'questions': exam_data['questions'],
            'total_points': exam_data['total_points'],
            'estimated_time': exam_data['estimated_time'],
            'num_questions': request.num_questions,
            'difficulty': request.difficulty,
            'status': 'active',
            'ai_provider': ai_service.provider_name
        }
        
        created_exam = self.exam_repo.create_exam(user_id, subject_id, exam_record)
        
        return {
            'exam_id': created_exam['exam_id'],
            'questions': created_exam['questions'],
            'total_points': created_exam['total_points'],
            'estimated_time': created_exam['estimated_time'],
            'created_at': created_exam.get('created_at'),
            'ai_provider': created_exam['ai_provider']
        }
    
    def get_exam(self, user_id: str, subject_id: str, exam_id: str) -> Exam:
        """
        Get exam by ID with ownership verification.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID
            
        Returns:
            Exam
        """
        exam_data = self.exam_repo.get_by_id_with_ownership(user_id, subject_id, exam_id)
        return Exam(**exam_data)
    
    def list_exams(self, user_id: str, subject_id: str) -> List[Exam]:
        """
        List all exams for a subject.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            List of Exams
        """
        # Verify subject exists
        self.subject_repo.get_by_id_with_ownership(user_id, subject_id)
        
        exams_data = self.exam_repo.get_by_subject(user_id, subject_id)
        return [Exam(**data) for data in exams_data]

