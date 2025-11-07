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


@patch('firebase_admin.firestore.client')
@patch('app.routes.pdf.FirebaseStorageService')
def test_upload_pdf_success(
    mock_storage_class,
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_storage_service,
    mock_pdf_data,
    mock_subject_data
):
    """Test successful PDF upload"""
    # Setup mocks
    mock_storage_class.return_value = mock_storage_service
    
    # Mock subject exists check
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    mock_db = Mock()
    
    # Mock subject reference
    mock_subject_ref = Mock()
    mock_subject_ref.get.return_value = mock_subject_doc
    
    # Mock PDF reference
    mock_pdf_ref = Mock()
    mock_pdf_ref.set = Mock()
    mock_subject_ref.collection.return_value.document.return_value = mock_pdf_ref
    
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
    mock_firestore.return_value = mock_db
    
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


@patch('firebase_admin.firestore.client')
@patch('app.routes.pdf.FirebaseStorageService')
def test_get_pdf_download_url(
    mock_storage_class,
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_storage_service,
    mock_pdf_data
):
    """Test getting PDF download URL"""
    # Setup mocks
    mock_storage_class.return_value = mock_storage_service
    
    mock_pdf_data['subject_id'] = TEST_SUBJECT_ID
    
    mock_pdf_doc = Mock()
    mock_pdf_doc.exists = True
    mock_pdf_doc.to_dict.return_value = mock_pdf_data
    
    mock_db = Mock()
    mock_subject_ref = Mock()
    mock_pdf_ref = Mock()
    mock_pdf_ref.get.return_value = mock_pdf_doc
    mock_subject_ref.collection.return_value.document.return_value = mock_pdf_ref
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
    mock_firestore.return_value = mock_db
    
    # Get download URL
    response = client.get(
        f"/api/subjects/{TEST_SUBJECT_ID}/pdfs/test_pdf_123/download",
        follow_redirects=False
    )
    
    assert response.status_code == 307  # Redirect
    assert 'location' in response.headers


@patch('firebase_admin.firestore.client')
@patch('app.routes.pdf.FirebaseStorageService')
def test_delete_pdf(
    mock_storage_class,
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_storage_service,
    mock_pdf_data
):
    """Test deleting PDF"""
    # Setup mocks
    mock_storage_class.return_value = mock_storage_service
    
    mock_pdf_data['subject_id'] = TEST_SUBJECT_ID
    
    mock_pdf_doc = Mock()
    mock_pdf_doc.exists = True
    mock_pdf_doc.to_dict.return_value = mock_pdf_data
    
    mock_db = Mock()
    mock_subject_ref = Mock()
    mock_pdf_ref = Mock()
    mock_pdf_ref.get.return_value = mock_pdf_doc
    mock_pdf_ref.delete = Mock()
    mock_subject_ref.collection.return_value.document.return_value = mock_pdf_ref
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_subject_ref
    mock_firestore.return_value = mock_db
    
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
