"""
Subject repository for subject-related data operations
"""
from typing import List, Dict, Any, Optional
from .base import BaseRepository
from app.models.domain import Subject


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject entities"""
    
    def __init__(self):
        super().__init__(collection_name='subjects', parent_collection='users')
    
    def get_by_user(self, user_id: str, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all subjects for a user, optionally filtered by group.
        
        Args:
            user_id: User ID
            group_id: Optional group ID filter (use "none" for subjects without group)
            
        Returns:
            List of subject data
        """
        filters = {}
        if group_id is not None:
            if group_id == "none":
                # Firestore doesn't support querying for None/null directly in some cases
                # We'll handle this in the service layer
                filters = None
            else:
                filters = {'group_id': group_id}
        
        return self.list_by_user(user_id, order_by='created_at', direction='DESCENDING', filters=filters)
    
    def get_by_id_with_ownership(self, subject_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get subject by ID and verify ownership.
        
        Args:
            subject_id: Subject ID
            user_id: User ID
            
        Returns:
            Subject data
            
        Raises:
            HTTPException: If subject not found or unauthorized
        """
        return super().get_by_id_with_ownership(subject_id, user_id, owner_field='user_id')
    
    def delete_with_subcollections(self, user_id: str, subject_id: str) -> None:
        """
        Delete subject and all its subcollections (PDFs, exams).
        
        Args:
            user_id: User ID
            subject_id: Subject ID
        """
        # Delete PDFs subcollection
        self.delete_subcollection(subject_id, 'pdfs', user_id)
        
        # Delete exams subcollection
        self.delete_subcollection(subject_id, 'exams', user_id)
        
        # Delete the subject itself
        self.delete(subject_id, user_id)

