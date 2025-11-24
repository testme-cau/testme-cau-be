"""
Tests for exam validator utility
"""
from unittest.mock import MagicMock

import pytest

from app.services.exam_service import ExamService
from app.utils.exam_validator import validate_exam_response, validate_scoring_rubric
from app.utils.exam_utils import normalize_exam_points


def test_validate_exam_response_success():
    """Test successful validation of well-formed exam data"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'What is Python?',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 10,
                'topic': 'Programming',
                'correct_answer': 'A',
                'model_answer': 'Python is a programming language.',
                'keywords': None,
                'scoring_rubric': None
            },
            {
                'id': 2,
                'question': 'Explain OOP.',
                'type': 'short_answer',
                'options': None,
                'points': 15,
                'topic': 'OOP',
                'correct_answer': None,
                'model_answer': 'OOP is object-oriented programming.',
                'keywords': ['objects', 'classes'],
                'scoring_rubric': [
                    {'criterion': 'Definition', 'points': 7},
                    {'criterion': 'Examples', 'points': 8}
                ]
            }
        ],
        'total_points': 25,
        'estimated_time': 10
    }
    
    result = validate_exam_response(exam_data, 2)
    
    assert result['questions'] is not None
    assert len(result['questions']) == 2
    assert result['total_points'] == 25
    assert result['estimated_time'] == 10
    assert result['validation_issues'] == []


def test_validate_exam_response_missing_questions():
    """Test validation fails when questions field is missing"""
    exam_data = {
        'total_points': 100,
        'estimated_time': 60
    }
    
    with pytest.raises(ValueError, match="Missing required field: 'questions'"):
        validate_exam_response(exam_data, 10)


def test_validate_exam_response_wrong_question_count():
    """Test validation warns when question count doesn't match"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test question',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 10,
                'model_answer': 'Answer',
                'correct_answer': 'A'
            }
        ],
        'total_points': 10,
        'estimated_time': 5
    }
    
    result = validate_exam_response(exam_data, 5)  # Expected 5, got 1
    
    assert len(result['validation_issues']) > 0
    assert any('Expected 5 questions' in issue for issue in result['validation_issues'])


def test_validate_exam_response_multiple_choice_validation():
    """Test multiple choice question validation"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test',
                'type': 'multiple_choice',
                'options': ['A', 'B'],  # Should have 4 options
                'points': 10,
                'model_answer': 'Answer'
                # Missing correct_answer
            }
        ],
        'total_points': 10,
        'estimated_time': 5
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert len(issues) >= 2
    assert any('exactly 4 options' in issue for issue in issues)
    assert any('must have \'correct_answer\'' in issue for issue in issues)


def test_validate_exam_response_missing_required_fields():
    """Test validation catches missing required fields"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'type': 'essay',
                'points': 20
                # Missing: question, model_answer
            }
        ],
        'total_points': 20,
        'estimated_time': 10
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert len(issues) > 0
    assert any('missing required fields' in issue for issue in issues)


def test_validate_exam_response_essay_needs_rubric():
    """Test essay questions require scoring rubric"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Write an essay',
                'type': 'essay',
                'options': None,
                'points': 20,
                'model_answer': 'Model essay answer'
                # Missing scoring_rubric
            }
        ],
        'total_points': 20,
        'estimated_time': 15
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert any('must have \'scoring_rubric\'' in issue for issue in issues)


def test_validate_scoring_rubric_correct():
    """Test scoring rubric with correct total"""
    rubric = [
        {'criterion': 'Clarity', 'points': 5},
        {'criterion': 'Depth', 'points': 10},
        {'criterion': 'Examples', 'points': 5}
    ]
    issues = []
    
    total = validate_scoring_rubric(rubric, 20, 1, issues)
    
    assert total == 20
    assert len(issues) == 0


def test_validate_scoring_rubric_mismatch():
    """Test scoring rubric with mismatched total"""
    rubric = [
        {'criterion': 'Clarity', 'points': 5},
        {'criterion': 'Depth', 'points': 5}
    ]
    issues = []
    
    total = validate_scoring_rubric(rubric, 20, 1, issues)
    
    assert total == 10
    assert len(issues) > 0
    assert any('doesn\'t match question points' in issue for issue in issues)


def test_validate_scoring_rubric_missing_fields():
    """Test rubric items missing required fields"""
    rubric = [
        {'criterion': 'Clarity'},  # Missing points
        {'points': 10}  # Missing criterion
    ]
    issues = []
    
    validate_scoring_rubric(rubric, 10, 1, issues)
    
    assert len(issues) >= 2
    assert any('missing \'points\'' in issue for issue in issues)
    assert any('missing \'criterion\'' in issue for issue in issues)


def test_validate_exam_response_invalid_points():
    """Test validation catches invalid point values"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': -5,  # Negative points
                'correct_answer': 'A',
                'model_answer': 'Answer'
            }
        ],
        'total_points': -5,
        'estimated_time': 5
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert any('points must be positive' in issue for issue in issues)


def test_validate_exam_response_total_points_mismatch():
    """Test detection of mismatched total points"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 10,
                'correct_answer': 'A',
                'model_answer': 'Answer'
            }
        ],
        'total_points': 100,  # Should be 10
        'estimated_time': 5
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert any('Total points mismatch' in issue for issue in issues)


def test_validate_exam_response_invalid_question_type():
    """Test validation catches invalid question types"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test',
                'type': 'invalid_type',
                'options': None,
                'points': 10,
                'model_answer': 'Answer'
            }
        ],
        'total_points': 10,
        'estimated_time': 5
    }
    
    result = validate_exam_response(exam_data, 1)
    
    issues = result['validation_issues']
    assert any('invalid type' in issue for issue in issues)


def test_validate_exam_response_uses_calculated_total():
    """Test that validator uses calculated total when stated total is wrong"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test 1',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 10,
                'correct_answer': 'A',
                'model_answer': 'Answer 1'
            },
            {
                'id': 2,
                'question': 'Test 2',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 15,
                'correct_answer': 'B',
                'model_answer': 'Answer 2'
            }
        ],
        'total_points': 100,  # Wrong, should be 25
        'estimated_time': 10
    }
    
    result = validate_exam_response(exam_data, 2)
    
    # Validator should use calculated total (25), not stated total (100)
    assert result['total_points'] == 25


def test_validate_exam_response_default_estimated_time():
    """Test that validator provides default estimated time if invalid"""
    exam_data = {
        'questions': [
            {
                'id': 1,
                'question': 'Test',
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'points': 10,
                'correct_answer': 'A',
                'model_answer': 'Answer'
            }
        ],
        'total_points': 10,
        'estimated_time': -5  # Invalid
    }
    
    result = validate_exam_response(exam_data, 1)
    
    # Should provide default (num_questions * 3)
    assert result['estimated_time'] == 3


def test_normalize_exam_points_scales_total_to_target():
    """정규화 헬퍼가 총점을 100점으로 맞추는지 검증"""
    exam_payload = {
        'questions': [
            {
                'id': 1,
                'question': 'Q1',
                'type': 'multiple_choice',
                'points': 20,
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 'A',
                'model_answer': 'A'
            },
            {
                'id': 2,
                'question': 'Q2',
                'type': 'essay',
                'points': 55,
                'model_answer': 'Essay',
                'scoring_rubric': [
                    {'criterion': 'Logic', 'points': 30},
                    {'criterion': 'Examples', 'points': 25}
                ]
            }
        ],
        'total_points': 75,
        'estimated_time': 20
    }

    normalized = normalize_exam_points(exam_payload, target_total=100)

    assert normalized['total_points'] == pytest.approx(100)
    assert sum(q['points'] for q in normalized['questions']) == pytest.approx(100)
    essay_question = normalized['questions'][1]
    assert sum(item['points'] for item in essay_question['scoring_rubric']) == pytest.approx(
        essay_question['points']
    )


def test_normalize_exam_points_handles_zero_rubric_entries():
    """배점 0 또는 rubric 없는 항목이 있어도 안정적으로 동작"""
    exam_payload = {
        'questions': [
            {
                'id': 1,
                'question': 'Q1',
                'type': 'short_answer',
                'points': 30,
                'model_answer': 'Ans',
                'scoring_rubric': [
                    {'criterion': 'Core', 'points': 20},
                    {'criterion': 'Examples', 'points': 10}
                ]
            },
            {
                'id': 2,
                'question': 'Q2',
                'type': 'short_answer',
                'points': 0,
                'model_answer': 'Zero question',
                'scoring_rubric': []
            },
            {
                'id': 3,
                'question': 'Q3',
                'type': 'essay',
                'points': 45,
                'model_answer': 'Essay',
                'scoring_rubric': [
                    {'criterion': 'Depth', 'points': 25},
                    {'criterion': 'Clarity', 'points': 20}
                ]
            }
        ],
        'total_points': 75,
        'estimated_time': 30
    }

    normalized = normalize_exam_points(exam_payload, target_total=100)

    assert normalized['total_points'] == pytest.approx(100)
    assert normalized['questions'][1]['points'] == 0  # 0점 문제는 그대로 유지
    for question in normalized['questions']:
        rubric = question.get('scoring_rubric') or []
        if rubric:
            assert sum(item['points'] for item in rubric) == pytest.approx(question['points'])


def _create_exam_service() -> ExamService:
    """Helper to build ExamService with mocked dependencies for normalization tests."""
    mock_repo = MagicMock()
    return ExamService(
        exam_repo=mock_repo,
        subject_repo=mock_repo,
        pdf_service=mock_repo,
        exam_job_repo=mock_repo,
        grading_job_repo=mock_repo,
        submission_repo=mock_repo,
    )


def test_normalize_grading_result_uses_exam_total_points():
    service = _create_exam_service()
    exam_data = {
        'questions': [
            {'id': 'q1', 'points': 20, 'type': 'short_answer'},
            {'id': 'q2', 'points': 55, 'type': 'essay', 'scoring_rubric': []},
        ],
        'total_points': 75,
    }
    grading_result = {
        'question_results': [
            {'question_id': 'q1', 'score': 12, 'max_points': 40},
            {'question_id': 'q2', 'score': 30, 'max_points': 60},
        ],
        'total_score': 42,
        'max_score': 100,
    }

    normalized = service._normalize_grading_result(exam_data, grading_result, answers=[])

    assert normalized['max_score'] == pytest.approx(75)
    assert sum(result['max_points'] for result in normalized['question_results']) == pytest.approx(75)


def test_normalize_grading_result_falls_back_to_question_sum_when_total_missing():
    service = _create_exam_service()
    exam_data = {
        'questions': [
            {'id': 'q1', 'points': 10, 'type': 'short_answer'},
            {'id': 'q2', 'points': 15, 'type': 'short_answer'},
        ],
    }
    grading_result = {
        'question_results': [
            {'question_id': 'q1', 'score': 8, 'max_points': 20},
            {'question_id': 'q2', 'score': 10, 'max_points': 30},
        ],
        'total_score': 18,
        'max_score': 100,
    }

    normalized = service._normalize_grading_result(exam_data, grading_result, answers=[])

    assert normalized['max_score'] == pytest.approx(25)
    assert sum(result['max_points'] for result in normalized['question_results']) == pytest.approx(25)




