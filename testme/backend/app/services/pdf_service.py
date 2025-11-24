"""
PDF service for business logic related to PDF management
"""
from typing import List, BinaryIO
from datetime import timedelta
from app.repositories.pdf import PDFRepository
from app.repositories.subject import SubjectRepository
from app.services.firebase_storage import FirebaseStorageService
from app.models.domain import PDF
from app.utils.file_utils import allowed_file
from config import settings
from fastapi import HTTPException, status


class PDFService:
    """Service for PDF business logic"""
    
    def __init__(
        self,
        pdf_repo: PDFRepository = None,
        subject_repo: SubjectRepository = None,
        storage_service: FirebaseStorageService = None
    ):
        self.pdf_repo = pdf_repo or PDFRepository()
        self.subject_repo = subject_repo or SubjectRepository()
        self.storage_service = storage_service or FirebaseStorageService()
    
    def upload_pdf(
        self,
        user_id: str,
        subject_id: str,
        file: BinaryIO,
        filename: str,
        file_size: int
    ) -> dict:
        """
        Upload a PDF file.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            file: File object
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Upload result with file information
        """
        # Verify subject exists and user owns it
        self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
        # Validate file type
        if not allowed_file(filename, settings.allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Validate file size
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
            )
        
        # Upload to Firebase Storage
        upload_result = self.storage_service.upload_file(file, user_id, filename)
        
        # Get actual file size from storage
        actual_size = self.storage_service.get_file_size(upload_result['storage_path'])
        
        # Save metadata to Firestore
        pdf_data = {
            'file_id': upload_result['file_id'],
            'subject_id': subject_id,
            'original_filename': upload_result['original_filename'],
            'unique_filename': upload_result['unique_filename'],
            'storage_path': upload_result['storage_path'],
            'size': actual_size,
            'user_id': user_id,
            'status': 'uploaded'
        }
        
        created_pdf = self.pdf_repo.create_pdf(user_id, subject_id, pdf_data)
        
        return {
            'file_id': created_pdf['file_id'],
            'original_filename': created_pdf['original_filename'],
            'file_url': f"/api/subjects/{subject_id}/pdfs/{created_pdf['file_id']}/download",
            'size': created_pdf['size'],
            'uploaded_at': created_pdf.get('uploaded_at')
        }
    
    def get_pdf(self, user_id: str, subject_id: str, pdf_id: str) -> PDF:
        """
        Get PDF by ID with ownership verification.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
            
        Returns:
            PDF
        """
        pdf_data = self.pdf_repo.get_by_id_with_ownership(user_id, subject_id, pdf_id)
        return PDF(**pdf_data)
    
    def list_pdfs(self, user_id: str, subject_id: str) -> List[PDF]:
        """
        List all PDFs for a subject.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            List of PDFs
        """
        # Verify subject exists
        self.subject_repo.get_by_id_with_ownership(subject_id, user_id)
        
        pdfs_data = self.pdf_repo.get_by_subject(user_id, subject_id)
        return [PDF(**data) for data in pdfs_data]

    def list_all_pdfs(self, user_id: str) -> List[dict]:
        """
        List all PDFs for a user across every subject.

        Args:
            user_id: User ID

        Returns:
            List of PDF dictionaries including subject metadata
        """
        pdfs_data = self.pdf_repo.list_all_for_user(user_id)
        if not pdfs_data:
            return []

        subjects = self.subject_repo.get_by_user(user_id)
        subject_map = {
            subject.get('subject_id'): subject.get('name')
            for subject in subjects
            if subject.get('subject_id')
        }

        for pdf in pdfs_data:
            subject_id = pdf.get('subject_id')
            pdf['subject_name'] = subject_map.get(subject_id)

        return pdfs_data
    
    def get_download_url(self, user_id: str, subject_id: str, pdf_id: str) -> dict:
        """
        Get download URL for a PDF.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
            
        Returns:
            Dict with download URL and filename
        """
        pdf_data = self.pdf_repo.get_by_id_with_ownership(user_id, subject_id, pdf_id)
        
        # Generate signed URL
        signed_url = self.storage_service.get_download_url(
            pdf_data['storage_path'],
            expiration=timedelta(hours=1)
        )
        
        return {
            'download_url': signed_url,
            'filename': pdf_data['original_filename']
        }
    
    def download_pdf_bytes(self, user_id: str, subject_id: str, pdf_id: str) -> bytes:
        """
        Download PDF file as bytes (for AI processing).
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
            
        Returns:
            PDF file bytes
        """
        pdf_data = self.pdf_repo.get_by_id_with_ownership(user_id, subject_id, pdf_id)
        return self.storage_service.download_file(pdf_data['storage_path'])
    
    def delete_pdf(self, user_id: str, subject_id: str, pdf_id: str) -> None:
        """
        Delete a PDF file.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
        """
        pdf_data = self.pdf_repo.get_by_id_with_ownership(user_id, subject_id, pdf_id)
        
        # Delete from Firebase Storage
        self.storage_service.delete_file(pdf_data['storage_path'])
        
        # Delete metadata from Firestore
        self.pdf_repo.delete_pdf(user_id, subject_id, pdf_id)

    def delete_pdf_by_id(self, user_id: str, pdf_id: str) -> None:
        """
        Delete a PDF when only file_id is known.

        Args:
            user_id: User ID
            pdf_id: PDF ID
        """
        pdf_data = self.pdf_repo.get_by_file_id(user_id, pdf_id)
        subject_id = pdf_data.get('subject_id')
        if not subject_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF does not have an associated subject"
            )
        self.delete_pdf(user_id, subject_id, pdf_id)

