"""
Domain models for business entities
"""
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model"""
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    language_preference: str = "ko"  # ISO 639-1 code (ko, en, ja, zh, es, fr, etc.)
    
    class Config:
        from_attributes = True


class Group(BaseModel):
    """Subject group model"""
    group_id: str
    user_id: str
    name: str  # Required
    description: Optional[str] = None
    color: Optional[str] = None  # e.g., "#FF5733"
    icon: Optional[str] = None  # Optional icon identifier
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Subject(BaseModel):
    """Subject (course) model"""
    subject_id: str
    user_id: str
    name: str  # Required
    description: Optional[str] = None
    group_id: Optional[str] = None  # Reference to Group
    color: Optional[str] = None  # e.g., "#FF5733"
    language_preference: Optional[str] = None  # Override user's language (ko, en, ja, etc.)
    pdf_count: Optional[int] = 0  # Number of PDFs in this subject
    exam_count: Optional[int] = 0  # Number of exams in this subject
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PDF(BaseModel):
    """PDF document model"""
    file_id: str
    subject_id: str
    original_filename: str
    unique_filename: str
    storage_path: str
    size: int
    user_id: str
    uploaded_at: datetime
    status: str = "uploaded"
    
    class Config:
        from_attributes = True


class ScoringCriterion(BaseModel):
    """채점 기준 항목"""
    criterion: str  # 채점 항목 설명
    points: float   # 이 항목의 배점
    example: Optional[str] = None  # 예시 답변
    
    class Config:
        from_attributes = True


class Question(BaseModel):
    """Exam question model"""
    id: int
    question: str
    type: str  # "multiple_choice", "short_answer", "essay"
    options: Optional[List[str]] = None
    points: int
    topic: Optional[str] = None  # 문제가 다루는 주제
    
    # 정답 및 채점 관련 필드
    correct_answer: Optional[str] = None  # 객관식: 정답 선택지
    model_answer: Optional[str] = None    # 모범 답안 전체
    scoring_rubric: Optional[List[ScoringCriterion]] = None  # 채점 기준
    keywords: Optional[List[str]] = None  # 단답형용 핵심 키워드
    
    class Config:
        from_attributes = True


class Exam(BaseModel):
    """Exam model - supports multiple PDFs"""
    exam_id: str
    subject_id: str
    pdf_id: str  # Keep for backward compatibility (first PDF ID)
    pdf_ids: Optional[List[str]] = None  # New field for multiple PDFs
    user_id: str
    questions: List[Question]
    total_points: int
    estimated_time: int  # in minutes
    num_questions: int
    difficulty: str
    created_at: datetime
    status: str = "active"
    ai_provider: Optional[str] = "gpt"  # Which AI service was used
    
    class Config:
        from_attributes = True


class QuestionResult(BaseModel):
    """Result for a single question"""
    question_id: int
    score: float
    max_points: int
    feedback: str
    is_correct: Optional[bool] = None
    
    class Config:
        from_attributes = True


class GradingResult(BaseModel):
    """Complete grading result"""
    total_score: float
    max_score: float
    percentage: float
    question_results: List[QuestionResult]
    ai_provider: Optional[str] = None
    
    class Config:
        from_attributes = True

