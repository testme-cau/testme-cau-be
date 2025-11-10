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
    """Mock exam data with enhanced fields"""
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
                'points': 10,
                'topic': 'Basic Arithmetic',
                'correct_answer': '4',
                'model_answer': 'The correct answer is 4 because 2+2 equals 4 in basic arithmetic.',
                'keywords': None,
                'scoring_rubric': None
            },
            {
                'id': 2,
                'question': 'Explain Python.',
                'type': 'essay',
                'options': None,
                'points': 20,
                'topic': 'Programming Languages',
                'correct_answer': None,
                'model_answer': 'Python is a high-level, interpreted programming language known for its simplicity and readability.',
                'keywords': None,
                'scoring_rubric': [
                    {'criterion': 'Definition clarity', 'points': 8, 'example': None},
                    {'criterion': 'Key features mentioned', 'points': 7, 'example': None},
                    {'criterion': 'Examples provided', 'points': 5, 'example': None}
                ]
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
    """Mock AI Service with enhanced response"""
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
                    'points': 10,
                    'topic': 'Basic Arithmetic',
                    'correct_answer': '4',
                    'model_answer': 'The correct answer is 4 because 2+2 equals 4 in basic arithmetic.',
                    'keywords': None,
                    'scoring_rubric': None
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
            'question_results': [
                {
                    'question_id': 1,
                    'score': 8.5,
                    'max_points': 10,
                    'feedback': 'Good answer',
                    'is_correct': True
                }
            ]
        }
    })
    return mock


@pytest.fixture
def mock_submission_data():
    """Mock submission data"""
    return {
        'submission_id': 'test_submission_123',
        'exam_id': 'test_exam_123',
        'subject_id': 'test_subject_123',
        'user_id': 'test_user_123',
        'answers': [
            {'question_id': 1, 'answer': '4'},
            {'question_id': 2, 'answer': 'Python is a programming language'}
        ],
        'grading_result': {
            'total_score': 85.0,
            'max_score': 100.0,
            'percentage': 85.0,
            'question_results': [
                {
                    'question_id': 1,
                    'score': 10.0,
                    'max_points': 10,
                    'feedback': 'Correct!',
                    'is_correct': True
                },
                {
                    'question_id': 2,
                    'score': 15.0,
                    'max_points': 20,
                    'feedback': 'Good answer but could be more detailed',
                    'is_correct': False
                }
            ],
            'overall_feedback': 'You demonstrated solid understanding of the core concepts.',
            'strengths': ['Clear explanation of basic concepts', 'Good use of examples'],
            'weaknesses': ['Could be more detailed in explanations', 'Missing some advanced concepts'],
            'study_recommendations': ['Review chapter 3 on advanced topics', 'Practice more problems on data structures']
        },
        'ai_provider': 'gpt',
        'submitted_at': datetime.utcnow(),
        'graded_at': datetime.utcnow(),
        'status': 'graded',
        'error_message': None
    }


@pytest.fixture
def mock_subject_data():
    """Mock subject data"""
    return {
        'subject_id': 'test_subject_123',
        'user_id': 'test_user_123',
        'name': '테스트 과목',
        'description': 'Test subject description',
        'group_id': None,
        'color': '#FF5733',
        'language_preference': 'ko',
        'pdf_count': 0,
        'exam_count': 0,
        'created_at': datetime.utcnow(),
        'updated_at': None
    }
