"""
Tests for Exam API routes - Subject-based structure
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


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


def test_generate_exam_without_auth(client: TestClient):
    """Test exam generation without authentication fails"""
    request_data = {"pdf_id": "test_pdf_123", "num_questions": 5}
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/exams/generate", json=request_data)
    assert response.status_code == 401


@pytest.mark.skip(reason="Complex Firestore mock chain with subject verification - requires Firestore emulator for proper testing")
@patch('app.dependencies.auth.ensure_default_subject')
@patch('firebase_admin.firestore.client')
@patch('app.routes.exam.FirebaseStorageService')
@patch('app.dependencies.ai_service.get_ai_service')
def test_generate_exam_with_gpt(
    mock_get_ai_service,
    mock_storage_class,
    mock_firestore,
    mock_ensure_default,
    client: TestClient,
    auth_override,
    mock_storage_service,
    mock_ai_service,
    mock_pdf_data,
    mock_subject_data
):
    """Test exam generation with GPT"""
    # Setup mocks
    mock_storage_class.return_value = mock_storage_service
    mock_get_ai_service.return_value = mock_ai_service
    
    # Update mock_pdf_data with subject_id
    mock_pdf_data['subject_id'] = TEST_SUBJECT_ID
    
    # Mock subject exists in Firestore
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    # Mock PDF exists in Firestore
    mock_pdf_doc = Mock()
    mock_pdf_doc.exists = True
    mock_pdf_doc.to_dict.return_value = mock_pdf_data
    
    # Mock exam reference
    mock_exam_ref = Mock()
    mock_exam_ref.id = 'test_exam_123'
    mock_exam_ref.set = Mock()
    
    mock_db = Mock()
    
    # Create separate mocks for different collection chains
    # Chain 1: users/{uid}/subjects/{subject_id} - for subject verification
    mock_subject_chain = Mock()
    mock_subject_user_doc = Mock()
    mock_subjects_col = Mock()
    mock_subject_doc_ref = Mock()
    
    mock_subject_doc_ref.get.return_value = mock_subject_doc
    mock_subjects_col.document.return_value = mock_subject_doc_ref
    mock_subject_user_doc.collection.return_value = mock_subjects_col
    mock_subject_chain.document.return_value = mock_subject_user_doc
    
    # Chain 2: users/{uid}/pdfs/{pdf_id} - for PDF access
    mock_pdf_chain = Mock()
    mock_pdf_user_doc = Mock()
    mock_pdfs_col = Mock()
    mock_pdf_doc_ref = Mock()
    
    mock_pdf_doc_ref.get.return_value = mock_pdf_doc
    mock_pdfs_col.document.return_value = mock_pdf_doc_ref
    mock_pdf_user_doc.collection.return_value = mock_pdfs_col
    mock_pdf_chain.document.return_value = mock_pdf_user_doc
    
    # Chain 3: users/{uid}/exams - for exam creation
    mock_exam_chain = Mock()
    mock_exam_user_doc = Mock()
    mock_exams_col = Mock()
    
    mock_exams_col.document.return_value = mock_exam_ref
    mock_exam_user_doc.collection.return_value = mock_exams_col
    mock_exam_chain.document.return_value = mock_exam_user_doc
    
    # Setup db.collection() to return appropriate chain based on first call
    call_count = {'count': 0}
    def collection_side_effect(name):
        if name == 'users':
            call_count['count'] += 1
            if call_count['count'] == 1:
                return mock_subject_chain
            elif call_count['count'] == 2:
                return mock_pdf_chain
            else:
                return mock_exam_chain
        return Mock()
    
    mock_db.collection.side_effect = collection_side_effect
    mock_firestore.return_value = mock_db
    
    # Generate exam
    request_data = {
        "pdf_id": "test_pdf_123",
        "num_questions": 5,
        "difficulty": "medium"
    }
    response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/exams/generate?ai_provider=gpt", json=request_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data['success'] is True
    assert 'exam_id' in data
    assert data['ai_provider'] == 'gpt'


@pytest.mark.skip(reason="Complex Firestore mock chain with subject verification - requires Firestore emulator for proper testing")
@patch('app.dependencies.auth.ensure_default_subject')
@patch('firebase_admin.firestore.client')
def test_get_exam(
    mock_firestore,
    mock_ensure_default,
    client: TestClient,
    auth_override,
    mock_exam_data,
    mock_subject_data
):
    """Test getting exam details"""
    # Update mock_exam_data with subject_id
    mock_exam_data['subject_id'] = TEST_SUBJECT_ID
    
    # Mock subject exists in Firestore
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    # Mock exam exists in Firestore
    mock_exam_doc = Mock()
    mock_exam_doc.exists = True
    mock_exam_doc.to_dict.return_value = mock_exam_data
    
    mock_db = Mock()
    
    # Chain 1: users/{uid}/subjects/{subject_id} - for subject verification
    mock_subject_chain = Mock()
    mock_subject_user_doc = Mock()
    mock_subjects_col = Mock()
    mock_subject_doc_ref = Mock()
    
    mock_subject_doc_ref.get.return_value = mock_subject_doc
    mock_subjects_col.document.return_value = mock_subject_doc_ref
    mock_subject_user_doc.collection.return_value = mock_subjects_col
    mock_subject_chain.document.return_value = mock_subject_user_doc
    
    # Chain 2: users/{uid}/exams/{exam_id} - for exam access
    mock_exam_chain = Mock()
    mock_exam_user_doc = Mock()
    mock_exams_col = Mock()
    mock_exam_doc_ref = Mock()
    
    mock_exam_doc_ref.get.return_value = mock_exam_doc
    mock_exams_col.document.return_value = mock_exam_doc_ref
    mock_exam_user_doc.collection.return_value = mock_exams_col
    mock_exam_chain.document.return_value = mock_exam_user_doc
    
    # Setup db.collection() to return appropriate chain
    call_count = {'count': 0}
    def collection_side_effect(name):
        if name == 'users':
            call_count['count'] += 1
            if call_count['count'] == 1:
                return mock_subject_chain
            else:
                return mock_exam_chain
        return Mock()
    
    mock_db.collection.side_effect = collection_side_effect
    mock_firestore.return_value = mock_db
    
    response = client.get(f"/api/subjects/{TEST_SUBJECT_ID}/exams/test_exam_123")
    
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
    mock_exam_data,
    mock_subject_data
):
    """Test listing exams"""
    # Mock Query.DESCENDING
    mock_query.DESCENDING = 'DESCENDING'
    
    # Update mock_exam_data with subject_id
    mock_exam_data['subject_id'] = TEST_SUBJECT_ID
    
    # Mock subject exists
    mock_subject_doc = Mock()
    mock_subject_doc.exists = True
    mock_subject_doc.to_dict.return_value = mock_subject_data
    
    # Mock exam document
    mock_exam_doc = Mock()
    mock_exam_doc.to_dict.return_value = mock_exam_data
    
    # Setup Firestore mock chain
    mock_users_col = Mock()
    mock_user_doc = Mock()
    mock_subjects_col = Mock()
    mock_subject_doc_ref = Mock()
    mock_exams_col = Mock()
    mock_order_by = Mock()
    
    mock_users_col.document.return_value = mock_user_doc
    mock_user_doc.collection.side_effect = lambda name: {
        'subjects': mock_subjects_col,
        'exams': mock_exams_col
    }.get(name)
    
    mock_subjects_col.document.return_value = mock_subject_doc_ref
    mock_subject_doc_ref.get.return_value = mock_subject_doc
    
    mock_exams_col.order_by.return_value = mock_order_by
    mock_order_by.stream.return_value = [mock_exam_doc]
    
    mock_db = Mock()
    mock_db.collection.return_value = mock_users_col
    mock_firestore.return_value = mock_db
    
    response = client.get(f"/api/subjects/{TEST_SUBJECT_ID}/exams")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'exams' in data


@pytest.mark.skip(reason="Complex Firestore mock chain with subject verification - requires Firestore emulator for proper testing")
def test_get_exam_not_found(client: TestClient, auth_override, mock_subject_data):
    """Test getting non-existent exam fails"""
    with patch('app.dependencies.auth.ensure_default_subject'):
        with patch('firebase_admin.firestore.client') as mock_firestore:
            # Mock subject exists
            mock_subject_doc = Mock()
            mock_subject_doc.exists = True
            mock_subject_doc.to_dict.return_value = mock_subject_data
            
            # Mock exam doesn't exist
            mock_exam_doc = Mock()
            mock_exam_doc.exists = False
            
            mock_db = Mock()
            
            # Chain 1: users/{uid}/subjects/{subject_id} - for subject verification
            mock_subject_chain = Mock()
            mock_subject_user_doc = Mock()
            mock_subjects_col = Mock()
            mock_subject_doc_ref = Mock()
            
            mock_subject_doc_ref.get.return_value = mock_subject_doc
            mock_subjects_col.document.return_value = mock_subject_doc_ref
            mock_subject_user_doc.collection.return_value = mock_subjects_col
            mock_subject_chain.document.return_value = mock_subject_user_doc
            
            # Chain 2: users/{uid}/exams/{exam_id} - for exam access
            mock_exam_chain = Mock()
            mock_exam_user_doc = Mock()
            mock_exams_col = Mock()
            mock_exam_doc_ref = Mock()
            
            mock_exam_doc_ref.get.return_value = mock_exam_doc
            mock_exams_col.document.return_value = mock_exam_doc_ref
            mock_exam_user_doc.collection.return_value = mock_exams_col
            mock_exam_chain.document.return_value = mock_exam_user_doc
            
            # Setup db.collection() to return appropriate chain
            call_count = {'count': 0}
            def collection_side_effect(name):
                if name == 'users':
                    call_count['count'] += 1
                    if call_count['count'] == 1:
                        return mock_subject_chain
                    else:
                        return mock_exam_chain
                return Mock()
            
            mock_db.collection.side_effect = collection_side_effect
            mock_firestore.return_value = mock_db
            
            response = client.get(f"/api/subjects/{TEST_SUBJECT_ID}/exams/nonexistent_id")
            assert response.status_code == 404


@pytest.mark.skip(reason="Complex Firestore mock chain with subject verification - requires Firestore emulator for proper testing")
def test_generate_exam_pdf_not_found(client: TestClient, auth_override, mock_subject_data):
    """Test exam generation fails when PDF doesn't exist"""
    with patch('app.dependencies.auth.ensure_default_subject'):
        with patch('firebase_admin.firestore.client') as mock_firestore:
            # Mock subject exists
            mock_subject_doc = Mock()
            mock_subject_doc.exists = True
            mock_subject_doc.to_dict.return_value = mock_subject_data
            
            # Mock PDF doesn't exist
            mock_pdf_doc = Mock()
            mock_pdf_doc.exists = False
            
            mock_db = Mock()
            
            # Chain 1: users/{uid}/subjects/{subject_id} - for subject verification
            mock_subject_chain = Mock()
            mock_subject_user_doc = Mock()
            mock_subjects_col = Mock()
            mock_subject_doc_ref = Mock()
            
            mock_subject_doc_ref.get.return_value = mock_subject_doc
            mock_subjects_col.document.return_value = mock_subject_doc_ref
            mock_subject_user_doc.collection.return_value = mock_subjects_col
            mock_subject_chain.document.return_value = mock_subject_user_doc
            
            # Chain 2: users/{uid}/pdfs/{pdf_id} - for PDF access
            mock_pdf_chain = Mock()
            mock_pdf_user_doc = Mock()
            mock_pdfs_col = Mock()
            mock_pdf_doc_ref = Mock()
            
            mock_pdf_doc_ref.get.return_value = mock_pdf_doc
            mock_pdfs_col.document.return_value = mock_pdf_doc_ref
            mock_pdf_user_doc.collection.return_value = mock_pdfs_col
            mock_pdf_chain.document.return_value = mock_pdf_user_doc
            
            # Setup db.collection() to return appropriate chain
            call_count = {'count': 0}
            def collection_side_effect(name):
                if name == 'users':
                    call_count['count'] += 1
                    if call_count['count'] == 1:
                        return mock_subject_chain
                    else:
                        return mock_pdf_chain
                return Mock()
            
            mock_db.collection.side_effect = collection_side_effect
            mock_firestore.return_value = mock_db
            
            request_data = {
                "pdf_id": "nonexistent_pdf",
                "num_questions": 5,
                "difficulty": "medium"
            }
            response = client.post(f"/api/subjects/{TEST_SUBJECT_ID}/exams/generate", json=request_data)
            assert response.status_code == 404
