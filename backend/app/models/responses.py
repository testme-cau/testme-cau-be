"""
Response models for API endpoints
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.domain import Question, QuestionResult, Subject, Group


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }


class GroupResponse(BaseModel):
    """Response model for group operations"""
    success: bool = True
    group: Group
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "group": {
                    "group_id": "group_123",
                    "user_id": "user_456",
                    "name": "2025-1학기",
                    "description": "2025년 1학기 과목들",
                    "color": "#3B82F6",
                    "icon": "calendar",
                    "created_at": "2025-11-07T12:00:00",
                    "updated_at": None
                }
            }
        }


class GroupListResponse(BaseModel):
    """Response model for group list"""
    success: bool = True
    groups: List[Group]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "groups": [
                    {
                        "group_id": "group_123",
                        "user_id": "user_456",
                        "name": "2025-1학기",
                        "description": "2025년 1학기",
                        "color": "#3B82F6",
                        "icon": "calendar",
                        "created_at": "2025-11-07T12:00:00",
                        "updated_at": None
                    }
                ],
                "count": 1
            }
        }


class SubjectResponse(BaseModel):
    """Response model for subject operations"""
    success: bool = True
    subject: Subject
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "subject": {
                    "subject_id": "subj_123",
                    "user_id": "user_456",
                    "name": "데이터베이스",
                    "description": "데이터베이스 설계 및 구현",
                    "semester": "2025-1",
                    "year": 2025,
                    "color": "#FF5733",
                    "created_at": "2025-11-07T12:00:00",
                    "updated_at": None
                }
            }
        }


class SubjectListResponse(BaseModel):
    """Response model for subject list"""
    success: bool = True
    subjects: List[Subject]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "subjects": [
                    {
                        "subject_id": "subj_123",
                        "user_id": "user_456",
                        "name": "데이터베이스",
                        "description": "데이터베이스 설계",
                        "semester": "2025-1",
                        "year": 2025,
                        "color": "#FF5733",
                        "created_at": "2025-11-07T12:00:00",
                        "updated_at": None
                    }
                ],
                "count": 1
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid request",
                "details": "PDF ID not found"
            }
        }


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload"""
    success: bool = True
    file_id: str
    original_filename: str
    file_url: str
    uploaded_at: datetime
    size: int
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "original_filename": "lecture.pdf",
                "file_url": "/api/pdf/123e4567-e89b-12d3-a456-426614174000/download",
                "uploaded_at": "2025-11-06T12:00:00",
                "size": 1024000
            }
        }


class PDFInfo(BaseModel):
    """PDF information for list responses"""
    file_id: str
    original_filename: str
    file_url: str
    size: int
    uploaded_at: datetime
    status: str
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None


class PDFListResponse(BaseModel):
    """Response model for PDF list"""
    success: bool = True
    pdfs: List[PDFInfo]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "pdfs": [
                    {
                        "file_id": "123e4567-e89b-12d3-a456-426614174000",
                        "original_filename": "lecture.pdf",
                        "file_url": "/api/pdf/123e4567.../download",
                        "size": 1024000,
                        "uploaded_at": "2025-11-06T12:00:00",
                        "status": "uploaded"
                    }
                ],
                "count": 1
            }
        }


class ExamResponse(BaseModel):
    """Response model for exam generation/retrieval"""
    success: bool = True
    exam: Dict[str, Any]  # Exam object with all fields
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "exam": {
                    "exam_id": "exam_123",
                    "subject_id": "subj_123",
                    "user_id": "user_123",
                    "pdf_id": "pdf_456",
                    "questions": [
                        {
                            "id": 1,
                            "question": "What is the capital of France?",
                            "type": "multiple_choice",
                            "options": ["London", "Paris", "Berlin", "Madrid"],
                            "points": 10
                        }
                    ],
                    "total_points": 100,
                    "estimated_time": 60,
                    "difficulty": "medium",
                    "num_questions": 10,
                    "created_at": "2025-11-06T12:00:00",
                    "status": "active",
                    "ai_provider": "gpt"
                }
            }
        }


class ExamInfo(BaseModel):
    """Exam information for list responses"""
    exam_id: str
    title: Optional[str] = None  # AI-generated exam title
    pdf_id: Optional[str]
    num_questions: int
    total_points: int
    difficulty: str
    created_at: datetime
    status: str
    ai_provider: Optional[str]
    language: Optional[str] = None


class ExamListResponse(BaseModel):
    """Response model for exam list"""
    success: bool = True
    exams: List[ExamInfo]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "exams": [
                    {
                        "exam_id": "exam_123",
                        "pdf_id": "pdf_456",
                        "num_questions": 10,
                        "total_points": 100,
                        "difficulty": "medium",
                        "created_at": "2025-11-06T12:00:00",
                        "status": "active",
                        "ai_provider": "gpt"
                    }
                ],
                "count": 1
            }
        }


class ExamJobInfo(BaseModel):
    job_id: str
    subject_id: str
    status: str
    pdf_ids: List[str]
    num_questions: int
    difficulty: str
    ai_provider: Optional[str]
    ai_model: Optional[str] = None
    language: Optional[str] = None
    progress_percentage: float = 0.0
    estimated_duration_seconds: Optional[int]
    exam_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    cancelled_at: Optional[str] = None


class ExamJobResponse(BaseModel):
    success: bool = True
    job: ExamJobInfo


class ExamJobListResponse(BaseModel):
    success: bool = True
    jobs: List[ExamJobInfo]


class GradingJobInfo(BaseModel):
    job_id: str
    subject_id: str
    exam_id: str
    submission_id: str
    status: str
    total_questions: int
    ai_provider: Optional[str]
    progress_percentage: float = 0.0
    estimated_duration_seconds: Optional[int]
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    cancelled_at: Optional[str] = None


class GradingJobListResponse(BaseModel):
    success: bool = True
    jobs: List[GradingJobInfo]


class GradingJobResponse(BaseModel):
    success: bool = True
    submission_id: str
    job: GradingJobInfo


class GradingResponse(BaseModel):
    """Response model for exam grading"""
    success: bool = True
    total_score: float
    max_score: float
    percentage: float
    question_results: List[QuestionResult]
    ai_provider: Optional[str] = None
    
    # Overall assessment
    overall_feedback: Optional[str] = None  # 전체 총평
    strengths: Optional[List[str]] = None   # 잘한 점
    weaknesses: Optional[List[str]] = None  # 약점
    study_recommendations: Optional[List[str]] = None  # 학습 권장사항
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_score": 85.5,
                "max_score": 100,
                "percentage": 85.5,
                "question_results": [
                    {
                        "question_id": 1,
                        "score": 8.5,
                        "max_points": 10,
                        "feedback": "Good answer, but could be more detailed",
                        "is_correct": True
                    }
                ],
                "ai_provider": "gpt",
                "overall_feedback": "전반적으로 우수한 성적입니다.",
                "strengths": ["데이터베이스 설계 이해도가 높음"],
                "weaknesses": ["SQL 쿼리 최적화 부분 보완 필요"],
                "study_recommendations": ["인덱싱 전략 심화 학습 권장"]
            }
        }


class SubmissionResponse(BaseModel):
    """답안 제출 응답"""
    success: bool = True
    submission_id: str
    status: str
    grading_result: Optional[Dict[str, Any]] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    error_message: Optional[str] = None

