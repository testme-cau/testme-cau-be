"""
Tests for Subject routes
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from firebase_admin import firestore


@pytest.fixture
def mock_subject_data():
    """Mock subject data"""
    return {
        'subject_id': 'test_subject_123',
        'user_id': 'test_user_123',
        'name': '데이터베이스',
        'description': '데이터베이스 설계 및 구현',
        'semester': '2025-1',
        'year': 2025,
        'color': '#FF5733',
        'created_at': datetime.utcnow(),
        'updated_at': None
    }


def test_create_subject_success(client, auth_override, mock_subject_data):
    """Test successful subject creation"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc_ref = Mock()
        mock_doc_ref.id = 'test_subject_123'
        mock_doc_ref.get.return_value = Mock(to_dict=Mock(return_value=mock_subject_data))
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_collection
        
        # Patch SERVER_TIMESTAMP
        with patch('firebase_admin.firestore.SERVER_TIMESTAMP', datetime.utcnow()):
            # Make request
            response = client.post(
                "/api/subjects",
                json={
                    "name": "데이터베이스",
                    "description": "데이터베이스 설계 및 구현",
                    "semester": "2025-1",
                    "year": 2025,
                    "color": "#FF5733"
                }
            )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert 'subject' in data
        assert data['subject']['name'] == '데이터베이스'


def test_create_subject_missing_name(client, auth_override):
    """Test subject creation without required name"""
    response = client.post(
        "/api/subjects",
        json={
            "description": "Test description"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_create_subject_invalid_color(client, auth_override):
    """Test subject creation with invalid color format"""
    response = client.post(
        "/api/subjects",
        json={
            "name": "Test Subject",
            "color": "invalid_color"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_list_subjects_success(client, auth_override, mock_subject_data):
    """Test successful subject listing"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = mock_subject_data
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_collection.order_by.return_value = mock_query
        
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_collection
        
        # Make request
        response = client.get("/api/subjects")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'subjects' in data
        assert data['count'] == 1
        assert data['subjects'][0]['name'] == '데이터베이스'


def test_list_subjects_empty(client, auth_override):
    """Test subject listing when no subjects exist"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_query = Mock()
        mock_query.stream.return_value = []
        
        mock_collection = Mock()
        mock_collection.order_by.return_value = mock_query
        
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_collection
        
        # Make request
        response = client.get("/api/subjects")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['count'] == 0
        assert len(data['subjects']) == 0


def test_get_subject_success(client, auth_override, mock_subject_data):
    """Test successful subject retrieval"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = mock_subject_data
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Make request
        response = client.get("/api/subjects/test_subject_123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['subject']['name'] == '데이터베이스'


def test_get_subject_not_found(client, auth_override):
    """Test subject retrieval when subject doesn't exist"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Make request
        response = client.get("/api/subjects/nonexistent_id")
        
        # Assertions
        assert response.status_code == 404


def test_update_subject_success(client, auth_override, mock_subject_data):
    """Test successful subject update"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        updated_data = mock_subject_data.copy()
        updated_data['name'] = '데이터베이스 시스템'
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = mock_subject_data
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.side_effect = [mock_doc, Mock(to_dict=Mock(return_value=updated_data))]
        mock_doc_ref.update = Mock()
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc_ref
        
        # Patch SERVER_TIMESTAMP
        with patch('firebase_admin.firestore.SERVER_TIMESTAMP', datetime.utcnow()):
            # Make request
            response = client.put(
                "/api/subjects/test_subject_123",
                json={"name": "데이터베이스 시스템"}
            )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['subject']['name'] == '데이터베이스 시스템'


def test_update_subject_not_found(client, auth_override):
    """Test subject update when subject doesn't exist"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Make request
        response = client.put(
            "/api/subjects/nonexistent_id",
            json={"name": "Updated Name"}
        )
        
        # Assertions
        assert response.status_code == 404


def test_delete_subject_success(client, auth_override, mock_subject_data):
    """Test successful subject deletion"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = mock_subject_data
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        mock_doc_ref.delete = Mock()
        
        # Mock pdfs and exams collections
        mock_doc_ref.collection.return_value.stream.return_value = []
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc_ref
        
        # Make request
        response = client.delete("/api/subjects/test_subject_123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'deleted successfully' in data['message']


def test_delete_subject_not_found(client, auth_override):
    """Test subject deletion when subject doesn't exist"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Make request
        response = client.delete("/api/subjects/nonexistent_id")
        
        # Assertions
        assert response.status_code == 404


def test_delete_subject_unauthorized(client, auth_override, mock_subject_data):
    """Test subject deletion with wrong user"""
    with patch('firebase_admin.firestore.client') as mock_firestore:
        # Setup mocks
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        # Different user_id
        unauthorized_data = mock_subject_data.copy()
        unauthorized_data['user_id'] = 'different_user'
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = unauthorized_data
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Make request
        response = client.delete("/api/subjects/test_subject_123")
        
        # Assertions
        assert response.status_code == 403

