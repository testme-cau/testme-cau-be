"""
Subject service for business logic related to subjects
"""
from typing import List, Optional
from app.repositories.subject import SubjectRepository
from app.repositories.pdf import PDFRepository
from app.repositories.exam import ExamRepository
from app.models.domain import Subject
from app.models.requests import SubjectCreateRequest, SubjectUpdateRequest


class SubjectService:
    """Service for subject business logic"""
    
    def __init__(
        self, 
        subject_repo: Optional[SubjectRepository] = None,
        pdf_repo: Optional[PDFRepository] = None,
        exam_repo: Optional[ExamRepository] = None
    ):
        self.repo = subject_repo or SubjectRepository()
        self.pdf_repo = pdf_repo or PDFRepository()
        self.exam_repo = exam_repo or ExamRepository()
    
    def create_subject(self, user_id: str, request: SubjectCreateRequest) -> Subject:
        """
        Create a new subject.
        
        Args:
            user_id: User ID
            request: Subject creation data
            
        Returns:
            Created Subject
        """
        # Generate document ID first
        collection_ref = self.repo._get_collection_ref(user_id)
        doc_ref = collection_ref.document()
        subject_id = doc_ref.id
        
        subject_data = {
            'subject_id': subject_id,
            'user_id': user_id,
            'name': request.name,
            'description': request.description,
            'group_id': request.group_id,
            'color': request.color,
            'language_preference': request.language_preference,
        }
        
        # Create in repository with specific document ID
        created_data = self.repo.create(subject_data, user_id, doc_id=subject_id)
        
        # Ensure subject_id is in the returned data
        created_data['subject_id'] = subject_id
        
        return Subject(**created_data)
    
    def get_subject(self, user_id: str, subject_id: str) -> Subject:
        """
        Get a subject by ID with ownership verification.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            
        Returns:
            Subject
        """
        subject_data = self.repo.get_by_id_with_ownership(subject_id, user_id)
        return Subject(**subject_data)
    
    def list_subjects(self, user_id: str, group_id: Optional[str] = None) -> List[Subject]:
        """
        List all subjects for a user, optionally filtered by group.
        
        Args:
            user_id: User ID
            group_id: Optional group ID filter
            
        Returns:
            List of Subjects with pdf_count and exam_count
        """
        subjects_data = self.repo.get_by_user(user_id, group_id)
        
        # Handle "none" group filter (subjects without group)
        if group_id == "none":
            subjects_data = [s for s in self.repo.get_by_user(user_id) if s.get('group_id') is None]
        
        # Add PDF and Exam counts to each subject
        subjects = []
        for data in subjects_data:
            subject_id = data.get('subject_id')
            
            # Skip subjects with empty or invalid subject_id
            if not subject_id or not subject_id.strip():
                continue
            
            # Count PDFs (correct parameter order: user_id, subject_id)
            pdfs = self.pdf_repo.get_by_subject(user_id, subject_id)
            pdf_count = len(pdfs)
            
            # Count Exams (correct parameter order: user_id, subject_id)
            exams = self.exam_repo.get_by_subject(user_id, subject_id)
            exam_count = len(exams)
            
            # Add counts to subject data
            data['pdf_count'] = pdf_count
            data['exam_count'] = exam_count
            
            subjects.append(Subject(**data))
        
        return subjects
    
    def update_subject(self, user_id: str, subject_id: str, request: SubjectUpdateRequest) -> Subject:
        """
        Update a subject.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
            request: Update data
            
        Returns:
            Updated Subject
        """
        # Verify ownership first
        self.repo.get_by_id_with_ownership(subject_id, user_id)
        
        # Build update data (only include provided fields)
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.description is not None:
            update_data['description'] = request.description
        if request.group_id is not None:
            update_data['group_id'] = request.group_id
        if request.color is not None:
            update_data['color'] = request.color
        if request.language_preference is not None:
            update_data['language_preference'] = request.language_preference
        
        # Update in repository
        if update_data:
            updated_data = self.repo.update(subject_id, update_data, user_id)
            return Subject(**updated_data)
        
        # No updates, return current subject
        return self.get_subject(user_id, subject_id)
    
    def delete_subject(self, user_id: str, subject_id: str) -> None:
        """
        Delete a subject and all its related data.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
        """
        # Verify ownership first
        self.repo.get_by_id_with_ownership(subject_id, user_id)
        
        # Delete subject with subcollections
        self.repo.delete_with_subcollections(user_id, subject_id)

