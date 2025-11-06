"""
Pydantic models for request/response validation
"""
from app.models.domain import User, PDF, Exam, Question
from app.models.requests import (
    ExamGenerationRequest,
    ExamSubmissionRequest,
    AnswerSubmission
)
from app.models.responses import (
    PDFUploadResponse,
    PDFListResponse,
    ExamResponse,
    ExamListResponse,
    GradingResponse,
    ErrorResponse,
    SuccessResponse
)

__all__ = [
    # Domain models
    "User",
    "PDF",
    "Exam",
    "Question",
    # Request models
    "ExamGenerationRequest",
    "ExamSubmissionRequest",
    "AnswerSubmission",
    # Response models
    "PDFUploadResponse",
    "PDFListResponse",
    "ExamResponse",
    "ExamListResponse",
    "GradingResponse",
    "ErrorResponse",
    "SuccessResponse",
]

