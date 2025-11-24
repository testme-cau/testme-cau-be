"""
PDF repository for PDF-related data operations
"""
from typing import List, Dict, Any
from firebase_admin import firestore
from fastapi import HTTPException, status
from .base import BaseRepository
from app.models.domain import PDF


class PDFRepository(BaseRepository[PDF]):
    """Repository for PDF entities (subcollection under subjects)"""
    
    def __init__(self):
        # PDFs are stored as subcollection: users/{user_id}/subjects/{subject_id}/pdfs/{pdf_id}
        super().__init__(collection_name='pdfs', parent_collection='users')
    
    def _get_pdf_collection_ref(self, user_id: str, subject_id: str):
        """Get PDF collection reference under a subject."""
        return (self.db.collection('users')
                .document(user_id)
                .collection('subjects')
                .document(subject_id)
                .collection('pdfs'))
    
    def get_by_subject(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        """
        Get all PDFs for a subject.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            List of PDF data
        """
        try:
            pdfs_ref = self._get_pdf_collection_ref(user_id, subject_id)
            docs = pdfs_ref.order_by('uploaded_at', direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list PDFs: {str(e)}"
            )

    def list_all_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all PDFs for a user across every subject.

        Args:
            user_id: User ID

        Returns:
            List of PDF data
        """
        try:
            query = (
                self.db.collection_group('pdfs')
                .where('user_id', '==', user_id)
                .order_by('uploaded_at', direction=firestore.Query.DESCENDING)
            )
            return [doc.to_dict() for doc in query.stream()]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list PDFs: {str(e)}"
            )

    def get_by_file_id(self, user_id: str, pdf_id: str) -> Dict[str, Any]:
        """
        Fetch a single PDF by file_id across all subjects.

        Args:
            user_id: User ID
            pdf_id: PDF ID

        Returns:
            PDF data
        """
        try:
            query = (
                self.db.collection_group('pdfs')
                .where('user_id', '==', user_id)
                .where('file_id', '==', pdf_id)
                .limit(1)
            )
            docs = list(query.stream())
            if not docs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="PDF not found"
                )
            return docs[0].to_dict()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch PDF: {str(e)}"
            )
    
    def get_by_id_with_ownership(self, user_id: str, subject_id: str, pdf_id: str) -> Dict[str, Any]:
        """
        Get PDF by ID and verify ownership.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
            
        Returns:
            PDF data
            
        Raises:
            HTTPException: If PDF not found or unauthorized
        """
        try:
            pdfs_ref = self._get_pdf_collection_ref(user_id, subject_id)
            doc = pdfs_ref.document(pdf_id).get()
            
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="PDF not found"
                )
            
            pdf_data = doc.to_dict()
            
            # Verify ownership
            if pdf_data.get('user_id') != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access"
                )
            
            return pdf_data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get PDF: {str(e)}"
            )
    
    def create_pdf(self, user_id: str, subject_id: str, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new PDF document.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_data: PDF metadata
            
        Returns:
            Created PDF data
        """
        try:
            pdfs_ref = self._get_pdf_collection_ref(user_id, subject_id)
            pdf_ref = pdfs_ref.document(pdf_data['file_id'])
            
            pdf_data['uploaded_at'] = firestore.SERVER_TIMESTAMP
            pdf_ref.set(pdf_data)
            
            # Fetch created document
            created_doc = pdf_ref.get()
            return created_doc.to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create PDF: {str(e)}"
            )
    
    def delete_pdf(self, user_id: str, subject_id: str, pdf_id: str) -> None:
        """
        Delete a PDF document.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            pdf_id: PDF ID
        """
        try:
            pdfs_ref = self._get_pdf_collection_ref(user_id, subject_id)
            pdf_ref = pdfs_ref.document(pdf_id)
            
            if not pdf_ref.get().exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="PDF not found"
                )
            
            pdf_ref.delete()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete PDF: {str(e)}"
            )

