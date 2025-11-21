"""
Exam service for business logic related to exam generation and grading
"""
from collections import defaultdict
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.repositories.exam import ExamRepository
from app.repositories.exam_job import ExamJobRepository
from app.repositories.grading_job import GradingJobRepository
from app.repositories.subject import SubjectRepository
from app.repositories.submission import SubmissionRepository
from app.services.pdf_service import PDFService
from app.services.ai_service_interface import AIServiceInterface
from app.models.domain import Exam
from app.models.requests import ExamGenerationRequest
from app.utils.exam_validator import validate_exam_response

from config import settings
from app.utils.exam_utils import compute_pdf_signature, normalize_pdf_ids


logger = logging.getLogger(__name__)


GENERATION_SECONDS_PER_QUESTION = 6
MIN_GENERATION_SECONDS = 45
GRADING_SECONDS_PER_QUESTION = 5
MIN_GRADING_SECONDS = 25


class ExamService:
    """Service for exam business logic"""
    
    def __init__(
        self,
        exam_repo: ExamRepository = None,
        subject_repo: SubjectRepository = None,
        pdf_service: PDFService = None,
        exam_job_repo: ExamJobRepository = None,
        grading_job_repo: GradingJobRepository = None,
        submission_repo: SubmissionRepository = None
    ):
        self.exam_repo = exam_repo or ExamRepository()
        self.subject_repo = subject_repo or SubjectRepository()
        self.pdf_service = pdf_service or PDFService()
        self.exam_job_repo = exam_job_repo or ExamJobRepository()
        self.grading_job_repo = grading_job_repo or GradingJobRepository()
        self.submission_repo = submission_repo or SubmissionRepository()

    # ----------------------------
    # Helpers
    # ----------------------------
    def _estimate_generation_duration(self, pdf_count: int, num_questions: int) -> int:
        base = num_questions * GENERATION_SECONDS_PER_QUESTION
        multiplier = max(1, pdf_count)
        return max(MIN_GENERATION_SECONDS, base * multiplier)

    def _estimate_grading_duration(self, num_questions: int) -> int:
        base = num_questions * GRADING_SECONDS_PER_QUESTION
        return max(MIN_GRADING_SECONDS, base)

    @staticmethod
    def _serialize_timestamp(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        try:
            # Firestore Timestamp has to_datetime()
            return value.to_datetime().isoformat()  # type: ignore
        except AttributeError:
            return str(value)

    def _calculate_time_progress(self, job: Dict[str, Any]) -> float:
        status_value = job.get('status', 'pending')
        if status_value == 'completed':
            return 100.0
        if status_value in {'failed', 'cancelled'}:
            return 0.0
        estimated = job.get('estimated_duration_seconds') or 60
        started_at = job.get('started_at')
        if not started_at:
            return 5.0
        if not isinstance(started_at, datetime):
            try:
                started_at = started_at.to_datetime()  # type: ignore
            except AttributeError:
                started_at = datetime.utcnow()
        elapsed = (datetime.utcnow() - started_at).total_seconds()
        progress = (elapsed / estimated) * 100
        return max(5.0, min(progress, 95.0))

    def _format_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        job_copy = dict(job)
        job_copy['created_at'] = self._serialize_timestamp(job_copy.get('created_at'))
        job_copy['updated_at'] = self._serialize_timestamp(job_copy.get('updated_at'))
        job_copy['started_at'] = self._serialize_timestamp(job_copy.get('started_at'))
        job_copy['completed_at'] = self._serialize_timestamp(job_copy.get('completed_at'))
        job_copy['failed_at'] = self._serialize_timestamp(job_copy.get('failed_at'))
        job_copy['progress_percentage'] = round(
            job_copy.get('progress_percentage', self._calculate_time_progress(job_copy)), 2
        )
        return job_copy
    
    @staticmethod
    def _ensure_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        try:
            return value.to_datetime()  # type: ignore[attr-defined]
        except AttributeError:
            return datetime.min
    
    def _fetch_previous_context(
        self,
        user_id: str,
        subject_id: str,
        pdf_ids: List[str]
    ) -> Optional[List[Dict[str, Any]]]:
        limit = max(0, settings.exam_history_limit)
        if limit <= 0:
            return None
        
        try:
            recent_submissions = self.submission_repo.get_recent_submissions_for_pdfs(
                user_id,
                subject_id,
                pdf_ids,
                limit=limit,
                per_exam_limit=settings.exam_history_per_exam_limit
            )
            
            if not recent_submissions:
                return None
            
            previous_context = self._build_previous_context(recent_submissions)
            if previous_context:
                logger.info(f"Found {len(previous_context)} previous question attempts for context")
            return previous_context or None
        except Exception as exc:
            logger.warning(f"Failed to fetch previous context: {exc}")
            return None
    
    def _build_previous_context(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        max_entries = max(0, settings.exam_history_limit)
        if max_entries == 0:
            return []
        
        per_topic_limit = max(1, settings.exam_history_per_topic)
        feedback_max_chars = max(0, settings.exam_history_feedback_max_chars)
        
        candidates: List[Dict[str, Any]] = []
        for submission in submissions:
            exam_questions = submission.get('exam_data', {}).get('questions', [])
            grading_result = submission.get('grading_result', {})
            question_results = grading_result.get('question_results', [])
            answers = submission.get('answers', [])
            
            if not exam_questions or not question_results or not answers:
                continue
            
            submitted_at = self._ensure_datetime(submission.get('submitted_at'))
            result_map = {
                result.get('question_id'): result
                for result in question_results
                if result.get('question_id') is not None
            }
            answer_map = {
                answer.get('question_id'): answer
                for answer in answers
                if answer.get('question_id') is not None
            }
            
            for question in exam_questions:
                question_id = question.get('id')
                if question_id is None:
                    continue
                
                answer_obj = answer_map.get(question_id)
                result_obj = result_map.get(question_id)
                if not answer_obj or not result_obj:
                    continue
                
                score = result_obj.get('score', 0) or 0
                max_points = result_obj.get('max_points', question.get('points', 0)) or 0
                score_pct = (score / max_points * 100) if max_points > 0 else 0
                
                candidates.append({
                    'question': question.get('question', ''),
                    'topic': question.get('topic', '') or '기타',
                    'answer': answer_obj.get('answer', ''),
                    'score': score,
                    'max_points': max_points,
                    'feedback': result_obj.get('feedback', '') or '',
                    'score_pct': score_pct,
                    'submitted_at': submitted_at
                })
        
        candidates.sort(
            key=lambda item: (
                item['score_pct'],
                -item['submitted_at'].timestamp()
            )
        )
        
        topic_counts: Dict[str, int] = defaultdict(int)
        previous_context: List[Dict[str, Any]] = []
        
        for candidate in candidates:
            topic_key = candidate['topic'] or '기타'
            if topic_counts[topic_key] >= per_topic_limit:
                continue
            
            feedback_text = candidate['feedback']
            if feedback_max_chars and len(feedback_text) > feedback_max_chars:
                feedback_text = feedback_text[:feedback_max_chars].rstrip()
            
            topic_counts[topic_key] += 1
            previous_context.append({
                'question': candidate['question'],
                'topic': topic_key,
                'answer': candidate['answer'],
                'score': candidate['score'],
                'max_points': candidate['max_points'],
                'feedback': feedback_text
            })
            
            if len(previous_context) >= max_entries:
                break
        
        return previous_context

    # ----------------------------
    # Exam generation jobs
    # ----------------------------
    def enqueue_exam_generation_job(
        self,
        user_id: str,
        subject_id: str,
        request: ExamGenerationRequest,
        ai_provider_name: str
    ) -> Dict[str, Any]:
        """Create a generation job document."""
        self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        job_data = {
            'user_id': user_id,
            'subject_id': subject_id,
            'pdf_ids': request.pdf_ids,
            'num_questions': request.num_questions,
            'difficulty': request.difficulty,
            'ai_provider': ai_provider_name,
            'status': 'pending',
            'progress_percentage': 0.0,
            'estimated_duration_seconds': self._estimate_generation_duration(len(request.pdf_ids), request.num_questions)
        }
        job = self.exam_job_repo.create_job(user_id, subject_id, job_data)
        return self._format_job(job)

    def process_exam_generation_job(
        self,
        user_id: str,
        subject_id: str,
        job_id: str,
        request: ExamGenerationRequest,
        ai_provider_name: str,
        language: str = 'ko'
    ) -> None:
        """Background worker that generates the exam and updates job status."""
        try:
            self.exam_job_repo.update_job(
                user_id, subject_id, job_id,
                {'status': 'processing', 'started_at': datetime.utcnow(), 'progress_percentage': 10.0}
            )
            subject_data = self.subject_repo.get_by_id_with_ownership(subject_id, user_id)

            pdf_bytes_list = []
            for pdf_id in request.pdf_ids:
                pdf_data = self.pdf_service.get_pdf(user_id, subject_id, pdf_id)
                pdf_bytes = self.pdf_service.download_pdf_bytes(user_id, subject_id, pdf_id)
                pdf_bytes_list.append((pdf_bytes, pdf_data.original_filename))

            final_language = subject_data.get('language_preference', language)

            previous_context = self._fetch_previous_context(user_id, subject_id, request.pdf_ids)

            from app.services.ai_factory import get_ai_service
            ai_service = get_ai_service(ai_provider_name)

            if len(pdf_bytes_list) == 1:
                generation_result = ai_service.generate_exam_from_pdf(
                    pdf_bytes_list[0][0],
                    pdf_bytes_list[0][1],
                    num_questions=request.num_questions,
                    difficulty=request.difficulty,
                    language=final_language,
                    previous_context=previous_context
                )
            else:
                generation_result = ai_service.generate_exam_from_multiple_pdfs(
                    pdf_bytes_list,
                    num_questions=request.num_questions,
                    difficulty=request.difficulty,
                    language=final_language,
                    previous_context=previous_context
                )

            if not generation_result['success']:
                raise Exception(generation_result.get('error', 'Unknown error during generation'))

            raw_exam_data = generation_result['exam']
            exam_data = validate_exam_response(raw_exam_data, request.num_questions)

            title = exam_data.get('title') or 'Untitled Exam'
            if title == 'Untitled Exam':
                topics = []
                for question in exam_data.get('questions', [])[:3]:
                    topic = question.get('topic')
                    if topic and topic not in topics:
                        topics.append(topic)
                if topics:
                    title = ' 및 '.join(topics)[:50]

            exam_record = {
                'subject_id': subject_id,
                'title': title,
                'pdf_id': request.pdf_ids[0],
                'pdf_ids': request.pdf_ids,
                'user_id': user_id,
                'questions': exam_data['questions'],
                'total_points': exam_data['total_points'],
                'estimated_time': exam_data['estimated_time'],
                'num_questions': request.num_questions,
                'difficulty': request.difficulty,
                'status': 'active',
                'ai_provider': ai_provider_name
            }

            created_exam = self.exam_repo.create_exam(user_id, subject_id, exam_record)

            self.exam_job_repo.update_job(
                user_id,
                subject_id,
                job_id,
                {
                    'status': 'completed',
                    'completed_at': datetime.utcnow(),
                    'progress_percentage': 100.0,
                    'exam_id': created_exam['exam_id']
                }
            )
        except Exception as e:
            logger.error(f"Exam generation job {job_id} failed: {e}")
            self.exam_job_repo.update_job(
                user_id,
                subject_id,
                job_id,
                {
                    'status': 'failed',
                    'failed_at': datetime.utcnow(),
                    'progress_percentage': 0.0,
                    'error_message': str(e)
                }
            )

    def list_exam_jobs(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        jobs = self.exam_job_repo.list_jobs(user_id, subject_id)
        formatted = []
        for job in jobs:
            if job.get('status') in {'pending', 'processing'}:
                job['progress_percentage'] = self._calculate_time_progress(job)
            elif job.get('status') == 'completed':
                job['progress_percentage'] = 100.0
            else:
                job['progress_percentage'] = job.get('progress_percentage', 0.0)
            formatted.append(self._format_job(job))
        return formatted

    def get_exam_job(self, user_id: str, subject_id: str, job_id: str) -> Dict[str, Any]:
        job = self.exam_job_repo.get_job(user_id, subject_id, job_id)
        if job.get('status') in {'pending', 'processing'}:
            job['progress_percentage'] = self._calculate_time_progress(job)
        elif job.get('status') == 'completed':
            job['progress_percentage'] = 100.0
        return self._format_job(job)

    def cancel_exam_job(self, user_id: str, subject_id: str, job_id: str) -> Dict[str, Any]:
        job = self.exam_job_repo.get_job(user_id, subject_id, job_id)
        if job.get('status') not in {'pending', 'processing'}:
            return self._format_job(job)
        self.exam_job_repo.update_job(
            user_id,
            subject_id,
            job_id,
            {
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow(),
                'progress_percentage': 0.0
            }
        )
        job = self.exam_job_repo.get_job(user_id, subject_id, job_id)
        return self._format_job(job)

    # ----------------------------
    # Grading jobs
    # ----------------------------
    def _prepare_grading_job(
        self,
        user_id: str,
        subject_id: str,
        exam_id: str,
        submission_id: str,
        num_questions: int,
        ai_provider_name: str
    ) -> Dict[str, Any]:
        job_data = {
            'user_id': user_id,
            'subject_id': subject_id,
            'exam_id': exam_id,
            'submission_id': submission_id,
            'status': 'pending',
            'total_questions': num_questions,
            'ai_provider': ai_provider_name,
            'progress_percentage': 0.0,
            'estimated_duration_seconds': self._estimate_grading_duration(num_questions)
        }
        job = self.grading_job_repo.create_job(user_id, subject_id, job_data)
        return self._format_job(job)

    def process_grading_job(
        self,
        user_id: str,
        subject_id: str,
        job_id: str,
        exam_id: str,
        submission_id: str,
        ai_provider_name: str
    ) -> None:
        try:
            job = self.grading_job_repo.get_job(user_id, subject_id, job_id)
            if job.get('status') == 'cancelled':
                logger.info(f"Grading job {job_id} cancelled before start")
                return

            self.grading_job_repo.update_job(
                user_id,
                subject_id,
                job_id,
                {'status': 'processing', 'started_at': datetime.utcnow(), 'progress_percentage': 15.0}
            )

            exam_data = self.exam_repo.get_by_id_with_ownership(user_id, subject_id, exam_id)
            submission_repo = self.submission_repo
            submission = submission_repo.get_submission_by_id(user_id, subject_id, exam_id, submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found for grading job {job_id}")
            answers = submission.get('answers', [])

            pdf_bytes = self.pdf_service.download_pdf_bytes(user_id, subject_id, exam_data['pdf_id'])
            pdf_data = self.pdf_service.get_pdf(user_id, subject_id, exam_data['pdf_id'])

            from app.services.ai_factory import get_ai_service
            ai_service = get_ai_service(ai_provider_name)

            grading_result = ai_service.grade_exam_with_pdf(
                pdf_bytes,
                pdf_data.original_filename,
                exam_data['questions'],
                answers
            )

            if grading_result['success']:
                submission_repo.update_grading_result(
                    user_id,
                    subject_id,
                    exam_id,
                    submission_id,
                    {
                        'status': 'graded',
                        'grading_result': grading_result['result']
                    }
                )
                self.grading_job_repo.update_job(
                    user_id,
                    subject_id,
                    job_id,
                    {
                        'status': 'completed',
                        'completed_at': datetime.utcnow(),
                        'progress_percentage': 100.0
                    }
                )
            else:
                error_msg = grading_result.get('error', 'Unknown error')
                submission_repo.update_grading_result(
                    user_id,
                    subject_id,
                    exam_id,
                    submission_id,
                    {'status': 'failed', 'error_message': error_msg}
                )
                self.grading_job_repo.update_job(
                    user_id,
                    subject_id,
                    job_id,
                    {
                        'status': 'failed',
                        'failed_at': datetime.utcnow(),
                        'error_message': error_msg,
                        'progress_percentage': 0.0
                    }
                )
        except Exception as e:
            logger.error(f"Grading job {job_id} failed: {e}")
            self.grading_job_repo.update_job(
                user_id,
                subject_id,
                job_id,
                {
                    'status': 'failed',
                    'failed_at': datetime.utcnow(),
                    'error_message': str(e),
                    'progress_percentage': 0.0
                }
            )
            self.submission_repo.update_grading_result(
                user_id,
                subject_id,
                exam_id,
                submission_id,
                {'status': 'failed', 'error_message': str(e)}
            )

    def list_grading_jobs(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        jobs = self.grading_job_repo.list_jobs(user_id, subject_id)
        formatted = []
        for job in jobs:
            if job.get('status') in {'pending', 'processing'}:
                job['progress_percentage'] = self._calculate_time_progress(job)
            elif job.get('status') == 'completed':
                job['progress_percentage'] = 100.0
            formatted.append(self._format_job(job))
        return formatted

    def get_grading_job(self, user_id: str, subject_id: str, job_id: str) -> Dict[str, Any]:
        job = self.grading_job_repo.get_job(user_id, subject_id, job_id)
        if job.get('status') in {'pending', 'processing'}:
            job['progress_percentage'] = self._calculate_time_progress(job)
        elif job.get('status') == 'completed':
            job['progress_percentage'] = 100.0
        return self._format_job(job)

    def cancel_grading_job(self, user_id: str, subject_id: str, job_id: str) -> Dict[str, Any]:
        job = self.grading_job_repo.get_job(user_id, subject_id, job_id)
        if job.get('status') not in {'pending', 'processing'}:
            return self._format_job(job)
        self.grading_job_repo.update_job(
            user_id,
            subject_id,
            job_id,
            {'status': 'cancelled', 'cancelled_at': datetime.utcnow(), 'progress_percentage': 0.0}
        )
        job = self.grading_job_repo.get_job(user_id, subject_id, job_id)
        return self._format_job(job)

    
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
        
        previous_context = self._fetch_previous_context(user_id, subject_id, request.pdf_ids)
        
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
        
        pdf_signature = compute_pdf_signature(request.pdf_ids)
        pdf_count = len(normalize_pdf_ids(request.pdf_ids))
        
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
            'ai_provider': ai_service.provider_name,
            'pdf_signature': pdf_signature,
            'pdf_count': pdf_count
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
    
    def list_exams(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        """
        List all exams for a subject with submission status.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            List of exam dictionaries with submission_status
        """
        # Verify subject exists
        self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
        # Get all exams
        exams_data = self.exam_repo.get_by_subject(user_id, subject_id)
        
        # Get all submissions for this subject
        from app.repositories.submission import SubmissionRepository
        submission_repo = SubmissionRepository()
        submissions_map = submission_repo.get_submissions_by_subject(user_id, subject_id)
        
        # Enrich exam data with submission status
        enriched_exams = []
        for exam_data in exams_data:
            exam_id = exam_data.get('exam_id')
            submission = submissions_map.get(exam_id)
            
            if submission:
                exam_data['submission_status'] = submission.get('status')
                exam_data['submission_id'] = submission.get('submission_id')
                if submission.get('status') == 'graded':
                    # Include score info for graded exams
                    grading_result = submission.get('grading_result', {})
                    exam_data['score'] = grading_result.get('total_score')
                    exam_data['max_score'] = grading_result.get('max_score')
            else:
                exam_data['submission_status'] = None  # Not submitted
            
            enriched_exams.append(exam_data)
        
        return enriched_exams
    
    def submit_exam_async(
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
        # 1. 시험 조회 및 검증
        exam_data = self.exam_repo.get_by_id_with_ownership(user_id, subject_id, exam_id)
        
        # 2. 답안 먼저 저장
        exam_pdf_ids = exam_data.get('pdf_ids') or ([exam_data.get('pdf_id')] if exam_data.get('pdf_id') else [])
        submission_data = {
            'exam_id': exam_id,
            'subject_id': subject_id,
            'user_id': user_id,
            'answers': answers,
            'ai_provider': ai_service.provider_name,
            'pdf_signature': exam_data.get('pdf_signature') or compute_pdf_signature(exam_pdf_ids),
            'pdf_count': len(normalize_pdf_ids(exam_pdf_ids)),
        }
        created_submission = self.submission_repo.create_submission(
            user_id, subject_id, exam_id, submission_data
        )
        
        # 3. 상태 변경: pending → grading
        self.submission_repo.update_grading_result(
            user_id, subject_id, exam_id,
            created_submission['submission_id'],
            {'status': 'grading'}
        )

        grading_job = self._prepare_grading_job(
            user_id,
            subject_id,
            exam_id,
            created_submission['submission_id'],
            len(exam_data['questions']),
            ai_service.provider_name
        )
        
        return {
            'submission_id': created_submission['submission_id'],
            'job': grading_job
        }
    
    
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

