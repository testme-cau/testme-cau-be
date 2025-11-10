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
        subject_data = self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
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
        
        # Check for previous submissions with same PDFs (for context)
        previous_context = None
        from app.repositories.submission import SubmissionRepository
        submission_repo = SubmissionRepository()
        
        try:
            recent_submissions = submission_repo.get_recent_submissions_for_pdfs(
                user_id, subject_id, request.pdf_ids, limit=3
            )
            
            if recent_submissions:
                # Build context from previous submissions
                previous_context = []
                for submission in recent_submissions:
                    exam_questions = submission.get('exam_data', {}).get('questions', [])
                    grading_result = submission.get('grading_result', {})
                    question_results = grading_result.get('question_results', [])
                    answers = submission.get('answers', [])
                    
                    # Match questions with answers and results
                    for question in exam_questions:
                        q_id = question.get('id')
                        
                        # Find corresponding answer and result
                        answer_obj = next((a for a in answers if a.get('question_id') == q_id), None)
                        result_obj = next((r for r in question_results if r.get('question_id') == q_id), None)
                        
                        if answer_obj and result_obj:
                            previous_context.append({
                                'question': question.get('question', ''),
                                'topic': question.get('topic', ''),
                                'answer': answer_obj.get('answer', ''),
                                'score': result_obj.get('score', 0),
                                'max_points': result_obj.get('max_points', question.get('points', 0)),
                                'feedback': result_obj.get('feedback', '')
                            })
                
                logger.info(f"Found {len(previous_context)} previous question attempts for context")
        except Exception as e:
            logger.warning(f"Failed to fetch previous context: {e}")
            previous_context = None
        
        # Generate exam using appropriate AI service method
        if len(pdf_bytes_list) == 1:
            # Single PDF - use original method
            generation_result = ai_service.generate_exam_from_pdf(
                pdf_bytes_list[0][0],  # pdf_bytes
                pdf_bytes_list[0][1],  # original_filename
                num_questions=request.num_questions,
                difficulty=request.difficulty,
                language=final_language,
                previous_context=previous_context
            )
        else:
            # Multiple PDFs - use new method
            generation_result = ai_service.generate_exam_from_multiple_pdfs(
                pdf_bytes_list,
                num_questions=request.num_questions,
                difficulty=request.difficulty,
                language=final_language,
                previous_context=previous_context
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
            'title': exam_data.get('title', 'Untitled Exam'),  # AI-generated title with fallback
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
        self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
        exams_data = self.exam_repo.get_by_subject(user_id, subject_id)
        return [Exam(**data) for data in exams_data]
    
    def submit_and_grade_exam(
        self,
        user_id: str,
        subject_id: str,
        exam_id: str,
        answers: List[Dict[str, Any]],
        ai_service: AIServiceInterface
    ) -> Dict[str, Any]:
        """
        답안 제출 및 자동 채점
        
        1. 시험 존재 확인
        2. 답안 먼저 저장 (status: pending)
        3. 채점 시도 (status: grading → graded/failed)
        
        Returns:
            제출 정보 (submission_id, status, grading_result 등)
        """
        from app.repositories.submission import SubmissionRepository
        submission_repo = SubmissionRepository()
        
        # 1. 시험 조회 및 검증
        exam_data = self.exam_repo.get_by_id_with_ownership(user_id, subject_id, exam_id)
        
        # 2. 답안 먼저 저장
        submission_data = {
            'exam_id': exam_id,
            'subject_id': subject_id,
            'user_id': user_id,
            'answers': answers,
            'ai_provider': ai_service.provider_name,
        }
        created_submission = submission_repo.create_submission(
            user_id, subject_id, exam_id, submission_data
        )
        
        # 3. 채점 시도
        try:
            # 상태 변경: pending → grading
            submission_repo.update_grading_result(
                user_id, subject_id, exam_id, 
                created_submission['submission_id'],
                {'status': 'grading'}
            )
            
            # PDF 다운로드
            pdf_bytes = self.pdf_service.download_pdf_bytes(
                user_id, subject_id, exam_data['pdf_id']
            )
            pdf_data = self.pdf_service.get_pdf(
                user_id, subject_id, exam_data['pdf_id']
            )
            
            # AI 채점
            grading_result = ai_service.grade_exam_with_pdf(
                pdf_bytes,
                pdf_data.original_filename,
                exam_data['questions'],
                answers
            )
            
            if grading_result['success']:
                # 채점 성공 → graded
                submission_repo.update_grading_result(
                    user_id, subject_id, exam_id,
                    created_submission['submission_id'],
                    {
                        'status': 'graded',
                        'grading_result': grading_result['result']
                    }
                )
                created_submission['status'] = 'graded'
                created_submission['grading_result'] = grading_result['result']
            else:
                # AI 서비스가 실패 반환 → failed
                error_msg = grading_result.get('error', 'Unknown error')
                submission_repo.update_grading_result(
                    user_id, subject_id, exam_id,
                    created_submission['submission_id'],
                    {
                        'status': 'failed',
                        'error_message': error_msg
                    }
                )
                created_submission['status'] = 'failed'
                created_submission['error_message'] = error_msg
        
        except Exception as e:
            # 예외 발생 (네트워크, 타임아웃 등) → failed
            logger.error(f"Grading exception: {e}")
            submission_repo.update_grading_result(
                user_id, subject_id, exam_id,
                created_submission['submission_id'],
                {
                    'status': 'failed',
                    'error_message': str(e)
                }
            )
            created_submission['status'] = 'failed'
            created_submission['error_message'] = str(e)
        
        return created_submission

