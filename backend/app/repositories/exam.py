"""
Exam repository for exam-related data operations
"""
from typing import List, Dict, Any
from firebase_admin import firestore
from .base import BaseRepository
from app.models.domain import Exam


class ExamRepository(BaseRepository[Exam]):
    """Repository for Exam entities (subcollection under subjects)"""
    
    def __init__(self):
        # Exams are stored as subcollection: users/{user_id}/subjects/{subject_id}/exams/{exam_id}
        super().__init__(collection_name='exams', parent_collection='users')
    
    def _get_exam_collection_ref(self, user_id: str, subject_id: str):
        """Get exam collection reference under a subject."""
        return (self.db.collection('users')
                .document(user_id)
                .collection('subjects')
                .document(subject_id)
                .collection('exams'))
    
    def get_by_subject(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        """
        Get all exams for a subject.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            List of exam data
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            docs = exams_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list exams: {str(e)}"
            )
    
    def get_by_id_with_ownership(self, user_id: str, subject_id: str, exam_id: str) -> Dict[str, Any]:
        """
        Get exam by ID and verify ownership.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID
            
        Returns:
            Exam data
            
        Raises:
            HTTPException: If exam not found or unauthorized
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            doc = exams_ref.document(exam_id).get()
            
            if not doc.exists:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exam not found"
                )
            
            exam_data = doc.to_dict()
            
            # Verify ownership
            if exam_data.get('user_id') != user_id:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access"
                )
            
            return exam_data
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get exam: {str(e)}"
            )
    
    def create_exam(self, user_id: str, subject_id: str, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new exam document.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_data: Exam data
            
        Returns:
            Created exam data with ID
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            exam_ref = exams_ref.document()
            
            exam_data['exam_id'] = exam_ref.id
            exam_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            exam_ref.set(exam_data)
            
            # Fetch created document
            created_doc = exam_ref.get()
            return created_doc.to_dict()
        except Exception as e:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create exam: {str(e)}"
            )
    
    def update_exam_status(self, user_id: str, subject_id: str, exam_id: str, status: str) -> None:
        """
        Update exam status.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID
            status: New status (pending, processing, completed, failed)
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            exam_ref = exams_ref.document(exam_id)
            exam_ref.update({'status': status})
        except Exception as e:
            from fastapi import HTTPException, status as http_status
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update exam status: {str(e)}"
            )
    
    def update_exam(self, user_id: str, subject_id: str, exam_id: str, update_data: Dict[str, Any]) -> None:
        """
        Update exam with given data.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID
            update_data: Data to update
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            exam_ref = exams_ref.document(exam_id)
            exam_ref.update(update_data)
        except Exception as e:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update exam: {str(e)}"
            )
    
    def delete_exam(self, user_id: str, subject_id: str, exam_id: str) -> None:
        """
        Delete an exam.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            exam_id: Exam ID
        """
        try:
            exams_ref = self._get_exam_collection_ref(user_id, subject_id)
            exam_ref = exams_ref.document(exam_id)
            exam_ref.delete()
        except Exception as e:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete exam: {str(e)}"
            )

