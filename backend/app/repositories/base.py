"""
Base repository with common Firestore operations
"""
from typing import List, Dict, Any, Optional, TypeVar, Generic
from datetime import datetime
from abc import ABC, abstractmethod
from firebase_admin import firestore
from fastapi import HTTPException, status

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common CRUD operations for Firestore.
    
    All domain-specific repositories should inherit from this class.
    """
    
    def __init__(self, collection_name: str, parent_collection: Optional[str] = None, db=None):
        """
        Initialize repository.
        
        Args:
            collection_name: Name of the Firestore collection
            parent_collection: Name of parent collection for subcollections (e.g., 'users')
            db: Optional Firestore client (for testing)
        """
        self.collection_name = collection_name
        self.parent_collection = parent_collection
        self._db = db
    
    @property
    def db(self):
        """Lazy-load Firestore client"""
        if self._db is None:
            self._db = firestore.client()
        return self._db
    
    def _get_collection_ref(self, user_id: Optional[str] = None):
        """
        Get Firestore collection reference.
        
        Args:
            user_id: User ID for user-scoped collections
            
        Returns:
            Firestore collection reference
        """
        if self.parent_collection and user_id:
            return self.db.collection(self.parent_collection).document(user_id).collection(self.collection_name)
        return self.db.collection(self.collection_name)
    
    def get_by_id(self, doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            doc_id: Document ID
            user_id: User ID for user-scoped collections
            
        Returns:
            Document data or None if not found
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            doc = collection_ref.document(doc_id).get()
            
            if not doc.exists:
                return None
            
            return doc.to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get document: {str(e)}"
            )
    
    def get_by_id_with_ownership(self, doc_id: str, user_id: str, owner_field: str = 'user_id') -> Dict[str, Any]:
        """
        Get document by ID and verify ownership.
        
        Args:
            doc_id: Document ID
            user_id: User ID
            owner_field: Field name containing owner ID
            
        Returns:
            Document data
            
        Raises:
            HTTPException: If document not found or unauthorized
        """
        doc_data = self.get_by_id(doc_id, user_id)
        
        if not doc_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.collection_name.capitalize()} not found"
            )
        
        if doc_data.get(owner_field) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access"
            )
        
        return doc_data
    
    def list_by_user(
        self, 
        user_id: str, 
        order_by: Optional[str] = 'created_at',
        direction: str = 'DESCENDING',
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List documents for a user.
        
        Args:
            user_id: User ID
            order_by: Field to order by
            direction: Sort direction (ASCENDING or DESCENDING)
            limit: Maximum number of results
            filters: Additional filters as dict {field: value}
            
        Returns:
            List of document data
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            query = collection_ref
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            
            # Apply ordering
            if order_by:
                direction_enum = firestore.Query.DESCENDING if direction == 'DESCENDING' else firestore.Query.ASCENDING
                query = query.order_by(order_by, direction=direction_enum)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list documents: {str(e)}"
            )
    
    def create(self, data: Dict[str, Any], user_id: Optional[str] = None, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new document.
        
        Args:
            data: Document data
            user_id: User ID for user-scoped collections
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Created document data with ID
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            
            if doc_id:
                doc_ref = collection_ref.document(doc_id)
            else:
                doc_ref = collection_ref.document()
            
            # Add server timestamp
            data['created_at'] = firestore.SERVER_TIMESTAMP
            data['updated_at'] = None
            
            doc_ref.set(data)
            
            # Fetch the created document to get server timestamps
            created_doc = doc_ref.get()
            return created_doc.to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create document: {str(e)}"
            )
    
    def update(self, doc_id: str, data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a document.
        
        Args:
            doc_id: Document ID
            data: Updated fields
            user_id: User ID for user-scoped collections
            
        Returns:
            Updated document data
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            doc_ref = collection_ref.document(doc_id)
            
            # Check if document exists
            if not doc_ref.get().exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.collection_name.capitalize()} not found"
                )
            
            # Add update timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref.update(data)
            
            # Fetch updated document
            updated_doc = doc_ref.get()
            return updated_doc.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update document: {str(e)}"
            )
    
    def delete(self, doc_id: str, user_id: Optional[str] = None) -> None:
        """
        Delete a document.
        
        Args:
            doc_id: Document ID
            user_id: User ID for user-scoped collections
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            doc_ref = collection_ref.document(doc_id)
            
            # Check if document exists
            if not doc_ref.get().exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.collection_name.capitalize()} not found"
                )
            
            doc_ref.delete()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document: {str(e)}"
            )
    
    def delete_subcollection(self, parent_doc_id: str, subcollection_name: str, user_id: Optional[str] = None) -> int:
        """
        Delete all documents in a subcollection.
        
        Args:
            parent_doc_id: Parent document ID
            subcollection_name: Name of subcollection
            user_id: User ID for user-scoped collections
            
        Returns:
            Number of documents deleted
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            parent_ref = collection_ref.document(parent_doc_id)
            subcollection_ref = parent_ref.collection(subcollection_name)
            
            docs = subcollection_ref.stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            
            return count
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete subcollection: {str(e)}"
            )
    
    def exists(self, doc_id: str, user_id: Optional[str] = None) -> bool:
        """
        Check if document exists.
        
        Args:
            doc_id: Document ID
            user_id: User ID for user-scoped collections
            
        Returns:
            True if document exists, False otherwise
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            doc = collection_ref.document(doc_id).get()
            return doc.exists
        except Exception:
            return False
    
    def count(self, user_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents.
        
        Args:
            user_id: User ID for user-scoped collections
            filters: Optional filters
            
        Returns:
            Number of documents
        """
        try:
            collection_ref = self._get_collection_ref(user_id)
            query = collection_ref
            
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            
            docs = query.stream()
            return sum(1 for _ in docs)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to count documents: {str(e)}"
            )

