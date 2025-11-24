"""
Tests for Submission API routes
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime


# Test constants
TEST_SUBJECT_ID = "test_subject_123"
TEST_EXAM_ID = "test_exam_123"
TEST_SUBMISSION_ID = "test_submission_123"


def test_submit_exam_without_auth(client: TestClient):
    """Test exam submission without authentication fails"""
    answers = [
        {"question_id": 1, "answer": "4"},
        {"question_id": 2, "answer": "Python is a programming language"}
    ]
    response = client.post(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submit",
        json=answers
    )
    assert response.status_code == 401


def test_get_submission_without_auth(client: TestClient):
    """Test getting submission without authentication fails"""
    response = client.get(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submission"
    )
    assert response.status_code == 401


@patch('app.services.exam_service.ExamService.submit_exam_async')
def test_submit_exam_success(
    mock_submit_async,
    client: TestClient,
    auth_override,
    mock_submission_data
):
    """Test successful exam submission and grading"""
    mock_job = {
        'job_id': 'grading_job_123',
        'subject_id': TEST_SUBJECT_ID,
        'exam_id': TEST_EXAM_ID,
        'submission_id': TEST_SUBMISSION_ID,
        'status': 'processing',
        'total_questions': 5,
        'ai_provider': 'gpt',
        'progress_percentage': 25.0,
        'estimated_duration_seconds': 60,
        'created_at': datetime.utcnow().isoformat()
    }
    mock_submit_async.return_value = {
        'submission_id': TEST_SUBMISSION_ID,
        'job': mock_job
    }
    
    answers = [
        {"question_id": 1, "answer": "4"},
        {"question_id": 2, "answer": "Python is a programming language"}
    ]
    
    response = client.post(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submit",
        json=answers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True
    assert data['submission_id'] == TEST_SUBMISSION_ID
    assert 'job' in data
    assert data['job']['job_id'] == mock_job['job_id']
    assert data['job']['status'] == 'processing'
    assert data['job']['progress_percentage'] == mock_job['progress_percentage']
    mock_submit_async.assert_called_once()


@patch('app.services.exam_service.ExamService.submit_exam_async')
def test_submit_exam_grading_failed(
    mock_submit_async,
    client: TestClient,
    auth_override
):
    """Test exam submission when grading fails"""
    failed_job = {
        'job_id': 'grading_job_456',
        'subject_id': TEST_SUBJECT_ID,
        'exam_id': TEST_EXAM_ID,
        'submission_id': TEST_SUBMISSION_ID,
        'status': 'failed',
        'total_questions': 5,
        'ai_provider': 'gpt',
        'progress_percentage': 0.0,
        'error_message': 'AI service timeout',
        'created_at': datetime.utcnow().isoformat(),
        'failed_at': datetime.utcnow().isoformat()
    }
    mock_submit_async.return_value = {
        'submission_id': TEST_SUBMISSION_ID,
        'job': failed_job
    }
    
    answers = [{"question_id": 1, "answer": "test"}]
    
    response = client.post(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submit",
        json=answers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True
    assert data['submission_id'] == TEST_SUBMISSION_ID
    assert data['job']['status'] == 'failed'
    assert data['job']['error_message'] == 'AI service timeout'
    mock_submit_async.assert_called_once()


@pytest.mark.skip(reason="Requires Firestore emulator - integration test")
@patch('app.repositories.submission.SubmissionRepository.get_by_user_and_exam')
def test_get_submission_success(
    mock_get_submission,
    client: TestClient,
    auth_override,
    mock_submission_data
):
    """Test successful submission retrieval"""
    # Mock repository method
    mock_get_submission.return_value = mock_submission_data
    
    response = client.get(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submission"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True
    assert 'submission' in data
    assert data['submission']['submission_id'] == TEST_SUBMISSION_ID
    assert data['submission']['status'] == 'graded'


@pytest.mark.skip(reason="Requires Firestore emulator - integration test")
@patch('app.repositories.submission.SubmissionRepository.get_by_user_and_exam')
def test_get_submission_not_found(
    mock_get_submission,
    client: TestClient,
    auth_override
):
    """Test getting submission that doesn't exist"""
    # Mock no submission found
    mock_get_submission.return_value = None
    
    response = client.get(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submission"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "No submission found" in data['detail']


def test_submit_exam_invalid_answers_format(
    client: TestClient,
    auth_override
):
    """Test exam submission with invalid answers format"""
    # Invalid format - not a list
    invalid_answers = {"question_id": 1, "answer": "test"}
    
    response = client.post(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submit",
        json=invalid_answers
    )
    
    # Should fail validation
    assert response.status_code == 422


@pytest.mark.skip(reason="Requires Firestore emulator - integration test")
def test_submit_exam_empty_answers(
    client: TestClient,
    auth_override
):
    """Test exam submission with empty answers"""
    response = client.post(
        f"/api/subjects/{TEST_SUBJECT_ID}/exams/{TEST_EXAM_ID}/submit",
        json=[]
    )
    
    # Empty list should be accepted (even if it results in 0 score)
    # The service layer or repository should handle this
    assert response.status_code in [200, 400, 422]


@pytest.mark.skip(reason="Requires Firestore emulator - integration test")
@pytest.mark.asyncio
async def test_submission_repository_create():
    """Test SubmissionRepository.create_submission"""
    from app.repositories.submission import SubmissionRepository
    
    # This test would need Firestore emulator or more complex mocking
    # For now, we'll just verify the class can be imported and instantiated
    repo = SubmissionRepository()
    assert repo is not None
    assert hasattr(repo, 'create_submission')
    assert hasattr(repo, 'update_grading_result')
    assert hasattr(repo, 'get_by_user_and_exam')


def test_submission_model():
    """Test Submission domain model"""
    from app.models.domain import Submission, GradingResult
    from datetime import datetime
    
    grading_result = GradingResult(
        total_score=85.0,
        max_score=100.0,
        percentage=85.0,
        question_results=[],
        ai_provider='gpt'
    )
    
    submission = Submission(
        submission_id='test_123',
        exam_id='exam_123',
        subject_id='subject_123',
        user_id='user_123',
        answers=[{'question_id': 1, 'answer': 'test'}],
        grading_result=grading_result,
        ai_provider='gpt',
        submitted_at=datetime.utcnow(),
        graded_at=datetime.utcnow(),
        status='graded',
        error_message=None
    )
    
    assert submission.submission_id == 'test_123'
    assert submission.status == 'graded'
    assert submission.grading_result.total_score == 85.0


def test_submission_response_model():
    """Test SubmissionResponse model"""
    from app.models.responses import SubmissionResponse
    from datetime import datetime
    
    response = SubmissionResponse(
        success=True,
        submission_id='test_123',
        status='graded',
        grading_result={'total_score': 85.0},
        submitted_at=datetime.utcnow(),
        graded_at=datetime.utcnow(),
        error_message=None
    )
    
    assert response.success is True
    assert response.submission_id == 'test_123'
    assert response.status == 'graded'

