"""
Exam service for business logic related to exam generation and grading
"""
from typing import List, Dict, Any, Optional
from app.repositories.exam import ExamRepository
from app.repositories.subject import SubjectRepository
from app.services.pdf_service import PDFService
from app.services.ai_service_interface import AIServiceInterface
from app.models.domain import Exam
from app.models.requests import ExamGenerationRequest
from app.utils.exam_validator import validate_exam_response
from fastapi import HTTPException, status
import logging
from datetime import datetime


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
    
    def create_exam_placeholder(
        self,
        user_id: str,
        subject_id: str,
        request: ExamGenerationRequest,
        ai_provider_name: str
    ) -> Dict[str, Any]:
        """
        Create a placeholder exam with 'pending' status for async generation.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            request: Exam generation request
            ai_provider_name: Name of AI provider to use
            
        Returns:
            Placeholder exam data with exam_id and status='pending'
        """
        # Verify subject exists
        subject_data = self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
        # Create placeholder exam
        exam_record = {
            'subject_id': subject_id,
            'title': 'Generating...',
            'pdf_id': request.pdf_ids[0],
            'pdf_ids': request.pdf_ids,
            'user_id': user_id,
            'questions': [],
            'total_points': 0,
            'estimated_time': 0,
            'num_questions': request.num_questions,
            'difficulty': request.difficulty,
            'status': 'pending',  # Status: pending
            'ai_provider': ai_provider_name,
            'generation_started_at': datetime.utcnow().isoformat()
        }
        
        created_exam = self.exam_repo.create_exam(user_id, subject_id, exam_record)
        
        return created_exam
    
    def generate_exam_background(
        self,
        user_id: str,
        subject_id: str,
        exam_id: str,
        request: ExamGenerationRequest,
        ai_provider_name: str,
        language: str = 'ko'
    ) -> None:
        """
        Background task to generate exam and update the placeholder.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Placeholder exam ID
            request: Exam generation request
            ai_provider_name: AI provider name (gpt, gemini)
            language: Language code
        """
        try:
            logger.info(f"Starting background exam generation for exam_id={exam_id}")
            
            # Create AI service instance (cannot reuse request-scoped service)
            from app.services.ai_factory import get_ai_service
            ai_service = get_ai_service(ai_provider_name)
            
            # Update status to 'processing'
            self.exam_repo.update_exam_status(user_id, subject_id, exam_id, 'processing')
            
            # Get subject data
            subject_data = self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
            
            # Collect PDF bytes
            pdf_bytes_list = []
            for pdf_id in request.pdf_ids:
                logger.info(f"Fetching PDF: {pdf_id}")
                pdf_data = self.pdf_service.get_pdf(user_id, subject_id, pdf_id)
                logger.info(f"PDF data: file_id={pdf_data.file_id}, original_filename={pdf_data.original_filename}")
                pdf_bytes = self.pdf_service.download_pdf_bytes(user_id, subject_id, pdf_id)
                logger.info(f"Downloaded PDF bytes: {len(pdf_bytes)} bytes")
                pdf_bytes_list.append((pdf_bytes, pdf_data.original_filename))
                logger.info(f"Added to pdf_bytes_list: ({len(pdf_bytes)} bytes, {pdf_data.original_filename})")
            
            # Determine language
            final_language = subject_data.get('language_preference', language)
            
            # Check for previous context
            previous_context = None
            from app.repositories.submission import SubmissionRepository
            submission_repo = SubmissionRepository()
            
            try:
                recent_submissions = submission_repo.get_recent_submissions_for_pdfs(
                    user_id, subject_id, request.pdf_ids, limit=3
                )
                
                if recent_submissions:
                    previous_context = []
                    for submission in recent_submissions:
                        exam_questions = submission.get('exam_data', {}).get('questions', [])
                        grading_result = submission.get('grading_result', {})
                        question_results = grading_result.get('question_results', [])
                        answers = submission.get('answers', [])
                        
                        for question in exam_questions:
                            q_id = question.get('id')
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
            except Exception as e:
                logger.warning(f"Failed to fetch previous context: {e}")
            
            # Generate exam
            logger.info(f"Calling AI service with {len(pdf_bytes_list)} PDF(s)")
            if len(pdf_bytes_list) == 1:
                logger.info(f"Single PDF mode: filename={pdf_bytes_list[0][1]}")
                generation_result = ai_service.generate_exam_from_pdf(
                    pdf_bytes_list[0][0],
                    pdf_bytes_list[0][1],
                    num_questions=request.num_questions,
                    difficulty=request.difficulty,
                    language=final_language,
                    previous_context=previous_context
                )
            else:
                logger.info(f"Multiple PDF mode: {[filename for _, filename in pdf_bytes_list]}")
                generation_result = ai_service.generate_exam_from_multiple_pdfs(
                    pdf_bytes_list,
                    num_questions=request.num_questions,
                    difficulty=request.difficulty,
                    language=final_language,
                    previous_context=previous_context
                )
            
            if not generation_result['success']:
                raise Exception(f"AI generation failed: {generation_result.get('error', 'Unknown error')}")
            
            raw_exam_data = generation_result['exam']
            exam_data = validate_exam_response(raw_exam_data, request.num_questions)
            
            # Generate title if not provided by AI
            title = exam_data.get('title', '')
            if not title or title == 'Untitled Exam':
                # Extract topics from questions to create a meaningful title
                topics = []
                for q in exam_data.get('questions', [])[:3]:  # Use first 3 questions
                    topic = q.get('topic', '')
                    if topic and topic not in topics:
                        topics.append(topic)
                
                if topics:
                    title = ' 및 '.join(topics)
                    if len(title) > 50:
                        title = title[:47] + '...'
                else:
                    # Use PDF filename as fallback
                    pdf_id = request.pdf_ids[0]
                    pdf_data = self.pdf_service.get_pdf(user_id, subject_id, pdf_id)
                    title = pdf_data.original_filename.replace('.pdf', '').replace('_', ' ')
                    if len(title) > 50:
                        title = title[:47] + '...'
            
            # Update exam with generated content
            update_data = {
                'title': title,
                'questions': exam_data['questions'],
                'total_points': exam_data['total_points'],
                'estimated_time': exam_data['estimated_time'],
                'status': 'completed',
                'generation_completed_at': datetime.utcnow().isoformat()
            }
            
            self.exam_repo.update_exam(user_id, subject_id, exam_id, update_data)
            
            logger.info(f"Background exam generation completed for exam_id={exam_id}")
            
        except Exception as e:
            logger.error(f"Background exam generation failed for exam_id={exam_id}: {e}")
            # Update status to 'failed'
            try:
                self.exam_repo.update_exam(user_id, subject_id, exam_id, {
                    'status': 'failed',
                    'error_message': str(e),
                    'generation_failed_at': datetime.utcnow().isoformat()
                })
            except Exception as update_error:
                logger.error(f"Failed to update exam status to failed: {update_error}")
    
    def delete_exam(self, user_id: str, subject_id: str, exam_id: str) -> None:
        """
        Delete an exam.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID to delete
        """
        # Verify ownership before deletion
        self.exam_repo.get_by_id_with_ownership(user_id, subject_id, exam_id)
        
        # Delete the exam
        self.exam_repo.delete_exam(user_id, subject_id, exam_id)
        logger.info(f"Deleted exam {exam_id} for user {user_id}")

