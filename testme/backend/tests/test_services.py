"""
Tests for Service layer
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from app.services.subject_service import SubjectService
from app.services.pdf_service import PDFService
from app.services.exam_service import ExamService
from app.models.domain import Subject, PDF, Exam
from app.models.requests import SubjectCreateRequest, SubjectUpdateRequest, ExamGenerationRequest


class TestSubjectService:
    """Test SubjectService business logic"""
    
    def test_create_subject_success(self):
        """Test successful subject creation"""
        # Mock repository
        mock_subject_repo = Mock()
        
        # Setup mock return
        created_data = {
            'subject_id': 'test_123',
            'name': 'Test Subject',
            'user_id': 'user_123',
            'created_at': datetime.utcnow()
        }
        mock_subject_repo.create.return_value = created_data
        mock_subject_repo._get_collection_ref.return_value.document.return_value.id = 'test_123'
        
        # Create service
        service = SubjectService(mock_subject_repo)
        
        # Create request
        request = SubjectCreateRequest(name='Test Subject')
        
        # Execute
        result = service.create_subject('user_123', request)
        
        # Assert
        assert result.name == 'Test Subject'
        mock_subject_repo.create.assert_called_once()
    
    def test_get_subject_success(self):
        """Test getting subject"""
        mock_subject_repo = Mock()
        
        subject_data = {
            'subject_id': 'test_123',
            'name': 'Test Subject',
            'user_id': 'user_123',
            'created_at': datetime.utcnow()
        }
        mock_subject_repo.get_by_id_with_ownership.return_value = subject_data
        
        service = SubjectService(mock_subject_repo)
        result = service.get_subject('user_123', 'test_123')
        
        assert result.name == 'Test Subject'
        mock_subject_repo.get_by_id_with_ownership.assert_called_once_with('test_123', 'user_123')
    
    def test_update_subject_success(self):
        """Test subject update"""
        mock_subject_repo = Mock()
        
        # Mock get for ownership check
        existing_data = {
            'subject_id': 'test_123',
            'name': 'Old Name',
            'user_id': 'user_123',
            'created_at': datetime.utcnow()
        }
        mock_subject_repo.get_by_id_with_ownership.return_value = existing_data
        
        # Mock update
        updated_data = {
            'subject_id': 'test_123',
            'name': 'New Name',
            'user_id': 'user_123',
            'created_at': datetime.utcnow()
        }
        mock_subject_repo.update.return_value = updated_data
        
        service = SubjectService(mock_subject_repo)
        request = SubjectUpdateRequest(name='New Name')
        
        result = service.update_subject('user_123', 'test_123', request)
        
        assert result.name == 'New Name'
        mock_subject_repo.update.assert_called_once()
    
    @pytest.mark.skip(reason="Cascading delete logic needs integration test")
    def test_delete_subject_with_cascading(self):
        """Test subject deletion with cascading delete of PDFs and exams"""
        mock_subject_repo = Mock()
        
        # Mock subject exists
        subject_data = {
            'subject_id': 'test_123',
            'name': 'Test Subject',
            'user_id': 'user_123'
        }
        mock_subject_repo.get_by_id_with_ownership.return_value = subject_data
        
        service = SubjectService(mock_subject_repo)
        service.delete_subject('user_123', 'test_123')
        
        mock_subject_repo.delete.assert_called_once()


class TestPDFService:
    """Test PDFService business logic"""
    
    def test_upload_pdf_success(self):
        """Test successful PDF upload"""
        mock_subject_repo = Mock()
        mock_pdf_repo = Mock()
        mock_storage_service = Mock()
        
        # Mock subject exists
        subject_data = {
            'subject_id': 'subject_123',
            'user_id': 'user_123',
            'name': 'Test Subject'
        }
        mock_subject_repo.get_by_id_with_ownership.return_value = subject_data
        
        # Mock storage upload
        upload_result = {
            'file_id': 'pdf_123',
            'original_filename': 'test.pdf',
            'unique_filename': 'test_pdf_123.pdf',
            'storage_path': 'path/to/test.pdf'
        }
        mock_storage_service.upload_file.return_value = upload_result
        mock_storage_service.get_file_size.return_value = 1024
        
        # Mock PDF creation
        pdf_data = {
            'file_id': 'pdf_123',
            'original_filename': 'test.pdf',
            'size': 1024,
            'uploaded_at': datetime.utcnow()
        }
        mock_pdf_repo.create_pdf.return_value = pdf_data
        
        service = PDFService(mock_pdf_repo, mock_subject_repo, mock_storage_service)
        
        # Mock file object
        mock_file = Mock()
        
        result = service.upload_pdf('user_123', 'subject_123', mock_file, 'test.pdf', 1024)
        
        assert result['file_id'] == 'pdf_123'
        assert result['original_filename'] == 'test.pdf'
        mock_storage_service.upload_file.assert_called_once()
        mock_pdf_repo.create_pdf.assert_called_once()
    
    def test_upload_pdf_invalid_extension(self):
        """Test PDF upload with invalid file extension"""
        mock_subject_repo = Mock()
        mock_pdf_repo = Mock()
        mock_storage_service = Mock()
        
        # Mock subject exists
        subject_data = {
            'subject_id': 'subject_123',
            'user_id': 'user_123'
        }
        mock_subject_repo.get_by_id_with_ownership.return_value = subject_data
        
        service = PDFService(mock_pdf_repo, mock_subject_repo, mock_storage_service)
        
        mock_file = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            service.upload_pdf('user_123', 'subject_123', mock_file, 'test.txt', 1024)
        
        assert exc_info.value.status_code == 400
    
    def test_get_download_url(self):
        """Test getting PDF download URL"""
        mock_subject_repo = Mock()
        mock_pdf_repo = Mock()
        mock_storage_service = Mock()
        
        # Mock PDF data
        pdf_data = {
            'file_id': 'pdf_123',
            'storage_path': 'path/to/test.pdf',
            'original_filename': 'test.pdf'
        }
        mock_pdf_repo.get_by_id_with_ownership.return_value = pdf_data
        
        # Mock signed URL
        mock_storage_service.get_download_url.return_value = 'https://signed-url.com/test.pdf'
        
        service = PDFService(mock_pdf_repo, mock_subject_repo, mock_storage_service)
        
        result = service.get_download_url('user_123', 'subject_123', 'pdf_123')
        
        assert result['download_url'] == 'https://signed-url.com/test.pdf'
        assert result['filename'] == 'test.pdf'


class TestExamService:
    """Test ExamService business logic"""
    
    @pytest.mark.skip(reason="Complex AI service mocking - needs integration test")
    def test_generate_exam_success(self):
        """Test successful exam generation"""
        pass
    
    @pytest.mark.skip(reason="Complex service dependencies - needs integration test")
    def test_get_exam_success(self):
        """Test getting exam"""
        pass

