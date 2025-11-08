"""
Tests for exam validator utility
"""
import pytest
from app.utils.exam_validator import validate_exam_response, validate_scoring_rubric


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



