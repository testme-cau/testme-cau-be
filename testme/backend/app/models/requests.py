"""
Request models for API endpoints
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class SubjectCreateRequest(BaseModel):
    """Request model for subject creation"""
    name: str = Field(..., description="Subject name (required)", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Subject description", max_length=500)
    semester: Optional[str] = Field(default=None, description="Semester (e.g., '2025-1')", max_length=20)
    year: Optional[int] = Field(default=None, description="Year", ge=2000, le=2100)
    color: Optional[str] = Field(default=None, description="Color hex code (e.g., '#FF5733')", pattern=r'^#[0-9A-Fa-f]{6}$')
    
    class Config:
        schema_extra = {
            "example": {
                "name": "데이터베이스",
                "description": "데이터베이스 설계 및 구현",
                "semester": "2025-1",
                "year": 2025,
                "color": "#FF5733"
            }
        }


class SubjectUpdateRequest(BaseModel):
    """Request model for subject update - all fields optional"""
    name: Optional[str] = Field(default=None, description="Subject name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Subject description", max_length=500)
    semester: Optional[str] = Field(default=None, description="Semester", max_length=20)
    year: Optional[int] = Field(default=None, description="Year", ge=2000, le=2100)
    color: Optional[str] = Field(default=None, description="Color hex code", pattern=r'^#[0-9A-Fa-f]{6}$')
    
    class Config:
        schema_extra = {
            "example": {
                "name": "데이터베이스 시스템",
                "description": "업데이트된 설명"
            }
        }


class ExamGenerationRequest(BaseModel):
    """Request model for exam generation"""
    pdf_id: str = Field(..., description="UUID of the uploaded PDF")
    num_questions: int = Field(default=10, ge=1, le=50, description="Number of questions to generate")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    ai_provider: Optional[str] = Field(default=None, description="AI provider to use: gpt or gemini")
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed = ['easy', 'medium', 'hard']
        if v.lower() not in allowed:
            raise ValueError(f'Difficulty must be one of {allowed}')
        return v.lower()
    
    @validator('ai_provider')
    def validate_ai_provider(cls, v):
        if v is None:
            return v
        allowed = ['gpt', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'AI provider must be one of {allowed}')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "pdf_id": "123e4567-e89b-12d3-a456-426614174000",
                "num_questions": 10,
                "difficulty": "medium",
                "ai_provider": "gpt"
            }
        }


class AnswerSubmission(BaseModel):
    """Single answer submission"""
    question_id: int
    answer: str
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": 1,
                "answer": "The answer is 42"
            }
        }


class ExamSubmissionRequest(BaseModel):
    """Request model for exam submission and grading"""
    exam_id: str = Field(..., description="Exam ID")
    answers: List[AnswerSubmission] = Field(..., description="List of student answers")
    ai_provider: Optional[str] = Field(default=None, description="AI provider to use for grading")
    
    @validator('ai_provider')
    def validate_ai_provider(cls, v):
        if v is None:
            return v
        allowed = ['gpt', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'AI provider must be one of {allowed}')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "exam_id": "exam_123",
                "answers": [
                    {"question_id": 1, "answer": "The answer is 42"},
                    {"question_id": 2, "answer": "Paris"}
                ],
                "ai_provider": "gpt"
            }
        }

