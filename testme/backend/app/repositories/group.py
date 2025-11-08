"""
Group repository for group-related data operations
"""
from typing import List, Dict, Any
from .base import BaseRepository
from app.models.domain import Group


class GroupRepository(BaseRepository[Group]):
    """Repository for Group entities"""
    
    def __init__(self):
        super().__init__(collection_name='groups', parent_collection='users')
    
    def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all groups for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of group data
        """
        return self.list_by_user(user_id, order_by='created_at', direction='DESCENDING')
    
    def get_by_id_with_ownership(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """
        Get group by ID and verify ownership.
        
        Args:
            user_id: User ID
            group_id: Group ID
            
        Returns:
            Group data
            
        Raises:
            HTTPException: If group not found or unauthorized
        """
        return super().get_by_id_with_ownership(group_id, user_id, owner_field='user_id')

