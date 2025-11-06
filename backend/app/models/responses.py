"""
Response models for API endpoints
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.domain import Question, QuestionResult


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
    exam_id: str
    questions: List[Question]
    total_points: int
    estimated_time: int
    created_at: datetime
    ai_provider: Optional[str] = "gpt"
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "exam_id": "exam_123",
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
                "created_at": "2025-11-06T12:00:00",
                "ai_provider": "gpt"
            }
        }


class ExamInfo(BaseModel):
    """Exam information for list responses"""
    exam_id: str
    pdf_id: Optional[str]
    num_questions: int
    total_points: int
    difficulty: str
    created_at: datetime
    status: str
    ai_provider: Optional[str]


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


class GradingResponse(BaseModel):
    """Response model for exam grading"""
    success: bool = True
    total_score: float
    max_score: float
    percentage: float
    question_results: List[QuestionResult]
    ai_provider: Optional[str] = None
    
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
                "ai_provider": "gpt"
            }
        }

