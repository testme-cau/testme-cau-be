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
    
    class Config:
        from_attributes = True


class Subject(BaseModel):
    """Subject (course) model"""
    subject_id: str
    user_id: str
    name: str  # Required
    description: Optional[str] = None
    semester: Optional[str] = None  # e.g., "2025-1"
    year: Optional[int] = None
    color: Optional[str] = None  # e.g., "#FF5733"
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


class Question(BaseModel):
    """Exam question model"""
    id: int
    question: str
    type: str  # "multiple_choice", "short_answer", "essay"
    options: Optional[List[str]] = None
    points: int
    
    class Config:
        from_attributes = True


class Exam(BaseModel):
    """Exam model"""
    exam_id: str
    subject_id: str
    pdf_id: str
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

