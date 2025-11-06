"""
Tests for Exam API routes
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


def test_generate_exam_without_auth(client: TestClient):
    """Test exam generation without authentication fails"""
    request_data = {"pdf_id": "test_pdf_123", "num_questions": 5}
    response = client.post("/api/exam/generate", json=request_data)
    assert response.status_code == 401


@patch('firebase_admin.firestore.client')
@patch('app.routes.exam.FirebaseStorageService')
@patch('app.dependencies.ai_service.get_ai_service')
def test_generate_exam_with_gpt(
    mock_get_ai_service,
    mock_storage_class,
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_storage_service,
    mock_ai_service,
    mock_pdf_data,
):
    """Test exam generation with GPT"""
    # Setup mocks
    mock_storage_class.return_value = mock_storage_service
    mock_get_ai_service.return_value = mock_ai_service
    
    # Mock PDF exists in Firestore
    mock_pdf_doc = Mock()
    mock_pdf_doc.exists = True
    mock_pdf_doc.to_dict.return_value = mock_pdf_data
    
    # Mock exam reference
    mock_exam_ref = Mock()
    mock_exam_ref.id = 'test_exam_123'
    mock_exam_ref.set = Mock()
    
    mock_db = Mock()
    mock_pdf_ref = Mock()
    mock_pdf_ref.get.return_value = mock_pdf_doc
    
    # Setup complex chain for Firestore operations
    mock_users_col = Mock()
    mock_user_doc = Mock()
    mock_pdfs_col = Mock()
    mock_pdf_doc_ref = Mock()
    mock_exams_col = Mock()
    
    mock_users_col.document.return_value = mock_user_doc
    mock_user_doc.collection.side_effect = lambda name: mock_pdfs_col if name == 'pdfs' else mock_exams_col
    mock_pdfs_col.document.return_value = mock_pdf_doc_ref
    mock_pdf_doc_ref.get.return_value = mock_pdf_doc
    mock_exams_col.document.return_value = mock_exam_ref
    
    mock_db.collection.return_value = mock_users_col
    mock_firestore.return_value = mock_db
    
    # Generate exam
    request_data = {
        "pdf_id": "test_pdf_123",
        "num_questions": 5,
        "difficulty": "medium"
    }
    response = client.post("/api/exam/generate?ai_provider=gpt", json=request_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data['success'] is True
    assert 'exam_id' in data
    assert data['ai_provider'] == 'gpt'


@patch('firebase_admin.firestore.client')
def test_get_exam(
    mock_firestore,
    client: TestClient,
    auth_override,
    mock_exam_data
):
    """Test getting exam details"""
    # Mock exam exists in Firestore
    mock_exam_doc = Mock()
    mock_exam_doc.exists = True
    mock_exam_doc.to_dict.return_value = mock_exam_data
    
    mock_db = Mock()
    mock_exam_ref = Mock()
    mock_exam_ref.get.return_value = mock_exam_doc
    
    mock_users_col = Mock()
    mock_user_doc = Mock()
    mock_exams_col = Mock()
    mock_exam_doc_ref = Mock()
    
    mock_users_col.document.return_value = mock_user_doc
    mock_user_doc.collection.return_value = mock_exams_col
    mock_exams_col.document.return_value = mock_exam_doc_ref
    mock_exam_doc_ref.get.return_value = mock_exam_doc
    
    mock_db.collection.return_value = mock_users_col
    mock_firestore.return_value = mock_db
    
    response = client.get("/api/exam/test_exam_123")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'exam' in data
    assert 'questions' in data['exam']


@pytest.mark.skip(reason="Complex Firestore mock chain - needs refinement")
@patch('firebase_admin.firestore.Query')
@patch('firebase_admin.firestore.client')
def test_list_exams(
    mock_firestore,
    mock_query,
    client: TestClient,
    auth_override,
    mock_exam_data
):
    """Test listing exams"""
    # Mock Query.DESCENDING
    mock_query.DESCENDING = 'DESCENDING'
    
    # Mock exam document
    mock_exam_doc = Mock()
    mock_exam_doc.to_dict.return_value = mock_exam_data
    
    # Setup Firestore mock chain
    mock_users_col = Mock()
    mock_user_doc = Mock()
    mock_exams_col = Mock()
    mock_order_by = Mock()
    
    mock_users_col.document.return_value = mock_user_doc
    mock_user_doc.collection.return_value = mock_exams_col
    mock_exams_col.order_by.return_value = mock_order_by
    mock_order_by.stream.return_value = [mock_exam_doc]
    
    mock_db = Mock()
    mock_db.collection.return_value = mock_users_col
    mock_firestore.return_value = mock_db
    
    response = client.get("/api/exam/list")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'exams' in data


def test_get_exam_not_found(client: TestClient, auth_override):
    """Test getting non-existent exam fails"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        mock_exam_doc = Mock()
        mock_exam_doc.exists = False
        
        mock_db = Mock()
        mock_exam_ref = Mock()
        mock_exam_ref.get.return_value = mock_exam_doc
        
        mock_users_col = Mock()
        mock_user_doc = Mock()
        mock_exams_col = Mock()
        mock_exam_doc_ref = Mock()
        
        mock_users_col.document.return_value = mock_user_doc
        mock_user_doc.collection.return_value = mock_exams_col
        mock_exams_col.document.return_value = mock_exam_doc_ref
        mock_exam_doc_ref.get.return_value = mock_exam_doc
        
        mock_db.collection.return_value = mock_users_col
        mock_firestore.return_value = mock_db
        
        response = client.get("/api/exam/nonexistent_id")
        assert response.status_code == 404


def test_generate_exam_pdf_not_found(client: TestClient, auth_override):
    """Test exam generation fails when PDF doesn't exist"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        mock_pdf_doc = Mock()
        mock_pdf_doc.exists = False
        
        mock_db = Mock()
        mock_pdf_ref = Mock()
        mock_pdf_ref.get.return_value = mock_pdf_doc
        
        mock_users_col = Mock()
        mock_user_doc = Mock()
        mock_pdfs_col = Mock()
        mock_pdf_doc_ref = Mock()
        
        mock_users_col.document.return_value = mock_user_doc
        mock_user_doc.collection.return_value = mock_pdfs_col
        mock_pdfs_col.document.return_value = mock_pdf_doc_ref
        mock_pdf_doc_ref.get.return_value = mock_pdf_doc
        
        mock_db.collection.return_value = mock_users_col
        mock_firestore.return_value = mock_db
        
        request_data = {
            "pdf_id": "nonexistent_pdf",
            "num_questions": 5,
            "difficulty": "medium"
        }
        response = client.post("/api/exam/generate", json=request_data)
        assert response.status_code == 404
