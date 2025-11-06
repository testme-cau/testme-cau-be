"""
Pytest fixtures and configuration
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from main import create_app
from datetime import datetime


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_firebase_user():
    """Mock Firebase user data"""
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "display_name": "Test User"
    }


@pytest.fixture
def auth_override(app, mock_firebase_user):
    """Override authentication dependency for testing"""
    from app.dependencies.auth import get_current_user
    
    async def mock_get_current_user():
        return mock_firebase_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_firestore_client():
    """Mock Firestore client"""
    return Mock()


@pytest.fixture
def mock_pdf_data():
    """Mock PDF data"""
    return {
        'file_id': 'test_pdf_123',
        'original_filename': 'test.pdf',
        'unique_filename': 'test_pdf_123.pdf',
        'storage_path': 'pdfs/test_user_123/test_pdf_123.pdf',
        'size': 1024,
        'user_id': 'test_user_123',
        'uploaded_at': datetime.utcnow(),
        'status': 'uploaded'
    }


@pytest.fixture
def mock_exam_data():
    """Mock exam data"""
    return {
        'exam_id': 'test_exam_123',
        'pdf_id': 'test_pdf_123',
        'user_id': 'test_user_123',
        'questions': [
            {
                'id': 1,
                'question': 'What is 2+2?',
                'type': 'multiple_choice',
                'options': ['2', '3', '4', '5'],
                'points': 10
            },
            {
                'id': 2,
                'question': 'Explain Python.',
                'type': 'essay',
                'options': None,
                'points': 20
            }
        ],
        'total_points': 30,
        'estimated_time': 15,
        'num_questions': 2,
        'difficulty': 'medium',
        'created_at': datetime.utcnow(),
        'status': 'active',
        'ai_provider': 'gpt'
    }


@pytest.fixture
def mock_storage_service():
    """Mock Firebase Storage Service"""
    mock = Mock()
    mock.upload_file = Mock(return_value={
        'file_id': 'test_pdf_123',
        'unique_filename': 'test_pdf_123.pdf',
        'storage_path': 'pdfs/test_user_123/test_pdf_123.pdf',
        'original_filename': 'test.pdf'
    })
    mock.get_file_size = Mock(return_value=1024)
    mock.get_download_url = Mock(return_value='https://mock-download-url.com/test.pdf')
    mock.delete_file = Mock(return_value=True)
    mock.download_file = Mock(return_value=b'%PDF-1.4 mock content')
    return mock


@pytest.fixture
def mock_ai_service():
    """Mock AI Service"""
    mock = Mock()
    mock.provider_name = 'gpt'
    mock.generate_exam_from_pdf = Mock(return_value={
        'success': True,
        'exam': {
            'questions': [
                {
                    'id': 1,
                    'question': 'What is 2+2?',
                    'type': 'multiple_choice',
                    'options': ['2', '3', '4', '5'],
                    'points': 10
                }
            ],
            'total_points': 10,
            'estimated_time': 5
        }
    })
    mock.grade_exam_with_pdf = Mock(return_value={
        'success': True,
        'result': {
            'total_score': 85.0,
            'max_score': 100.0,
            'percentage': 85.0,
            'question_results': []
        }
    })
    return mock
