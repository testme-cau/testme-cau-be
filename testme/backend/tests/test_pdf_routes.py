"""
Tests for PDF API routes - Subject-based structure
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from io import BytesIO


# Test subject ID to use across tests
TEST_SUBJECT_ID = "test_subject_123"


@pytest.fixture
def mock_subject_data():
    """Mock subject data"""
    return {
        'subject_id': TEST_SUBJECT_ID,
        'user_id': 'test_user_123',
        'name': '테스트 과목',
        'description': None,
        'semester': None,
        'year': None,
        'color': None,
        'created_at': None,
        'updated_at': None
    }


def test_upload_pdf_without_auth(client: TestClient):
    """Test PDF upload without authentication fails"""
    files = {'file': ('test.pdf', BytesIO(b'%PDF-1.4 content'), 'application/pdf')}
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/upload", files=files)
    assert response.status_code == 401


def test_upload_pdf_success(
    client: TestClient,
    app,
    auth_override,
    mock_pdf_data
):
    """Test successful PDF upload"""
    from datetime import datetime
    from app.dependencies.service import get_pdf_service
    
    # Mock PDFService
    mock_pdf_service = Mock()
    mock_pdf_service.upload_pdf.return_value = {
        'file_id': 'test_pdf_123',
        'original_filename': 'test.pdf',
        'file_url': f'/api/subjects/{TEST_SUBJECT_ID}/pdfs/test_pdf_123/download',
        'size': 1024,
        'uploaded_at': datetime.utcnow()
    }
    
    # Override dependency
    app.dependency_overrides[get_pdf_service] = lambda: mock_pdf_service
    
    # Upload PDF
    pdf_content = b'%PDF-1.4\n%Mock PDF content\n%%EOF'
    files = {'file': ('test.pdf', BytesIO(pdf_content), 'application/pdf')}
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data['success'] is True
    assert data['file_id'] == 'test_pdf_123'
    assert data['original_filename'] == 'test.pdf'
    assert 'file_url' in data
    assert TEST_SUBJECT_ID in data['file_url']


def test_upload_pdf_no_file(client: TestClient, auth_override):
    """Test PDF upload without file fails"""
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/upload", files={})
    assert response.status_code == 422  # Validation error


@patch('firebase_admin.firestore.client')
def test_upload_pdf_invalid_extension(
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_subject_data
):
    """Test PDF upload with invalid file extension fails"""
    # Mock subject exists
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    mock_db = Mock()
    mock_subject_ref = Mock()
    mock_subject_ref.get.return_value = mock_subject_doc
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
    mock_firestore.return_value = mock_db
    
    files = {'file': ('test.txt', BytesIO(b'text content'), 'text/plain')}
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/upload", files=files)
    assert response.status_code == 400


@patch('firebase_admin.firestore.client')
def test_list_pdfs(
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_pdf_data,
    mock_subject_data
):
    """Test listing PDFs"""
    # Update mock_pdf_data with subject_id
    mock_pdf_data['subject_id'] = TEST_SUBJECT_ID
    
    # Mock subject exists
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    # Mock PDF documents
    mock_pdf_doc = Mock()
    mock_pdf_doc.to_dict.return_value = mock_pdf_data
    
    mock_db = Mock()
    mock_subject_ref = Mock()
    mock_subject_ref.get.return_value = mock_subject_doc
    
    # Mock PDFs collection
    mock_pdfs_collection = Mock()
    mock_pdfs_collection.order_by.return_value.stream.return_value = [mock_pdf_doc]
    mock_subject_ref.collection.return_value = mock_pdfs_collection
    
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
    mock_firestore.return_value = mock_db
    
    # List PDFs
    response = client.get(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'pdfs' in data
    assert data['count'] >= 0


def test_get_pdf_download_url(
    client: TestClient,
    app,
    auth_override
):
    """Test getting PDF download URL"""
    from app.dependencies.service import get_pdf_service
    
    # Mock PDFService
    mock_pdf_service = Mock()
    mock_pdf_service.get_download_url.return_value = {
        'download_url': 'https://storage.googleapis.com/test-bucket/test.pdf?signed=true',
        'filename': 'test.pdf'
    }
    
    # Override dependency
    app.dependency_overrides[get_pdf_service] = lambda: mock_pdf_service
    
    # Get download URL
    response = client.get(
        f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/test_pdf_123/download",
        follow_redirects=False
    )
    
    # Route returns JSON with download_url, not a redirect
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'download_url' in data
    assert 'filename' in data
    assert data['filename'] == 'test.pdf'


def test_delete_pdf(
    client: TestClient,
    app,
    auth_override
):
    """Test deleting PDF"""
    from app.dependencies.service import get_pdf_service
    
    # Mock PDFService
    mock_pdf_service = Mock()
    mock_pdf_service.delete_pdf.return_value = None  # delete returns None
    
    # Override dependency
    app.dependency_overrides[get_pdf_service] = lambda: mock_pdf_service
    
    # Delete PDF
    response = client.delete(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/test_pdf_123")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


def test_delete_pdf_not_found(client: TestClient, auth_override):
    """Test deleting non-existent PDF fails"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        mock_pdf_doc = Mock()
        mock_pdf_doc.exists = False
        
        mock_db = Mock()
        mock_subject_ref = Mock()
        mock_pdf_ref = Mock()
        mock_pdf_ref.get.return_value = mock_pdf_doc
        mock_subject_ref.collection.return_value.document.return_value = mock_pdf_ref
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
        mock_firestore.return_value = mock_db
        
        response = client.delete(f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/nonexistent_id")
        assert response.status_code == 404
