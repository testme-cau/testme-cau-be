"""
Service layer dependency injection
"""
from fastapi import Depends
from app.services.subject_service import SubjectService
from app.services.pdf_service import PDFService
from app.services.exam_service import ExamService


def get_subject_service() -> SubjectService:
    """Get SubjectService instance"""
    return SubjectService()


def get_pdf_service() -> PDFService:
    """Get PDFService instance"""
    return PDFService()


def get_exam_service() -> ExamService:
    """Get ExamService instance"""
    return ExamService()

