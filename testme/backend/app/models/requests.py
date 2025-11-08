"""
Request models for API endpoints
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class UserUpdateRequest(BaseModel):
    """Request model for user profile update"""
    display_name: Optional[str] = Field(default=None, description="User display name")
    language_preference: Optional[str] = Field(default=None, description="Language preference (ISO 639-1 code)")
    
    @validator('language_preference')
    def validate_language(cls, v):
        if v is None:
            return v
        from app.utils.language_utils import is_valid_language_code, VALID_LANGUAGE_CODES
        if not is_valid_language_code(v):
            raise ValueError(f'Language must be ISO 639-1 code. Supported: {VALID_LANGUAGE_CODES}')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "display_name": "홍길동",
                "language_preference": "ko"
            }
        }


class GroupCreateRequest(BaseModel):
    """Request model for group creation"""
    name: str = Field(..., description="Group name (required)", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Group description", max_length=500)
    color: Optional[str] = Field(default=None, description="Color hex code (e.g., '#FF5733')", pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(default=None, description="Icon identifier", max_length=50)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "2025-1학기",
                "description": "2025년 1학기 과목들",
                "color": "#3B82F6",
                "icon": "calendar"
            }
        }


class GroupUpdateRequest(BaseModel):
    """Request model for group update - all fields optional"""
    name: Optional[str] = Field(default=None, description="Group name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Group description", max_length=500)
    color: Optional[str] = Field(default=None, description="Color hex code", pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(default=None, description="Icon identifier", max_length=50)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "2025-2학기",
                "description": "업데이트된 설명"
            }
        }


class SubjectCreateRequest(BaseModel):
    """Request model for subject creation"""
    name: str = Field(..., description="Subject name (required)", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Subject description", max_length=500)
    group_id: Optional[str] = Field(default=None, description="Group ID (optional)")
    color: Optional[str] = Field(default=None, description="Color hex code (e.g., '#FF5733')", pattern=r'^#[0-9A-Fa-f]{6}$')
    language_preference: Optional[str] = Field(default=None, description="Language preference (ISO 639-1 code: ko, en, ja, zh, etc.)")
    
    @validator('language_preference')
    def validate_language(cls, v):
        if v is None:
            return v
        from app.utils.language_utils import is_valid_language_code, VALID_LANGUAGE_CODES
        if not is_valid_language_code(v):
            raise ValueError(f'Language must be ISO 639-1 code. Supported: {VALID_LANGUAGE_CODES}')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "name": "데이터베이스",
                "description": "데이터베이스 설계 및 구현",
                "group_id": "group_123",
                "color": "#FF5733",
                "language_preference": "ko"
            }
        }


class SubjectUpdateRequest(BaseModel):
    """Request model for subject update - all fields optional"""
    name: Optional[str] = Field(default=None, description="Subject name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Subject description", max_length=500)
    group_id: Optional[str] = Field(default=None, description="Group ID")
    color: Optional[str] = Field(default=None, description="Color hex code", pattern=r'^#[0-9A-Fa-f]{6}$')
    language_preference: Optional[str] = Field(default=None, description="Language preference (ISO 639-1 code)")
    
    @validator('language_preference')
    def validate_language(cls, v):
        if v is None:
            return v
        from app.utils.language_utils import is_valid_language_code, VALID_LANGUAGE_CODES
        if not is_valid_language_code(v):
            raise ValueError(f'Language must be ISO 639-1 code. Supported: {VALID_LANGUAGE_CODES}')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "name": "데이터베이스 시스템",
                "description": "업데이트된 설명",
                "group_id": "group_456",
                "language_preference": "en"
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

