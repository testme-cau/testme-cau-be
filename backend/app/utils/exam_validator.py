"""
Exam validation utility for AI-generated exam responses
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def validate_exam_response(exam_data: dict, num_questions: int) -> dict:
    """
    AI 응답 검증 및 정제
    
    Args:
        exam_data: AI가 생성한 시험 데이터
        num_questions: 요청한 문제 개수
    
    Returns:
        검증되고 정제된 시험 데이터
    
    Raises:
        ValueError: 필수 필드가 없거나 검증 실패 시
    """
    issues = []
    
    # 1. 필수 최상위 필드 확인
    if 'questions' not in exam_data:
        raise ValueError("Missing required field: 'questions'")
    
    questions = exam_data['questions']
    
    if not isinstance(questions, list):
        raise ValueError("'questions' must be a list")
    
    # 2. 문제 개수 확인
    actual_count = len(questions)
    if actual_count != num_questions:
        issues.append(f"Expected {num_questions} questions, got {actual_count}")
        logger.warning(f"Question count mismatch: expected {num_questions}, got {actual_count}")
    
    # 3. 각 문제 검증
    validated_questions = []
    total_calculated_points = 0
    
    for i, q in enumerate(questions):
        q_num = i + 1
        
        # 필수 필드 확인
        required_base = ['id', 'question', 'type', 'points', 'model_answer']
        missing = [f for f in required_base if f not in q or q[f] is None]
        if missing:
            issues.append(f"Question {q_num} missing required fields: {missing}")
            continue
        
        q_type = q.get('type', '').lower()
        
        # 문제 유형별 검증
        if q_type == 'multiple_choice':
            # 객관식: options와 correct_answer 필수
            if not q.get('options') or not isinstance(q['options'], list):
                issues.append(f"Question {q_num}: multiple_choice must have 'options' list")
            elif len(q['options']) != 4:
                issues.append(f"Question {q_num}: multiple_choice must have exactly 4 options, got {len(q['options'])}")
            
            if not q.get('correct_answer'):
                issues.append(f"Question {q_num}: multiple_choice must have 'correct_answer'")
        
        elif q_type == 'short_answer':
            # 단답형: keywords와 scoring_rubric 권장
            if not q.get('keywords'):
                logger.warning(f"Question {q_num}: short_answer should have 'keywords'")
            
            if not q.get('scoring_rubric'):
                logger.warning(f"Question {q_num}: short_answer should have 'scoring_rubric'")
            else:
                # rubric 검증
                rubric_total = validate_scoring_rubric(q['scoring_rubric'], q['points'], q_num, issues)
        
        elif q_type == 'essay':
            # 서술형: scoring_rubric 필수
            if not q.get('scoring_rubric'):
                issues.append(f"Question {q_num}: essay must have 'scoring_rubric'")
            else:
                # rubric 검증
                rubric_total = validate_scoring_rubric(q['scoring_rubric'], q['points'], q_num, issues)
        
        else:
            issues.append(f"Question {q_num}: invalid type '{q_type}' (must be multiple_choice, short_answer, or essay)")
        
        # 점수 범위 확인
        points = q.get('points', 0)
        if not isinstance(points, (int, float)) or points <= 0:
            issues.append(f"Question {q_num}: points must be positive number, got {points}")
        elif points > 50:
            issues.append(f"Question {q_num}: points {points} seems too high (max recommended: 50)")
        
        total_calculated_points += points
        validated_questions.append(q)
    
    # 4. 총점 검증
    if 'total_points' in exam_data:
        stated_total = exam_data['total_points']
        if abs(total_calculated_points - stated_total) > 5:
            issues.append(
                f"Total points mismatch: calculated {total_calculated_points} vs stated {stated_total}"
            )
            logger.warning(f"Using calculated total: {total_calculated_points}")
    
    # 5. 예상 시간 검증
    estimated_time = exam_data.get('estimated_time', num_questions * 3)
    if not isinstance(estimated_time, (int, float)) or estimated_time <= 0:
        logger.warning(f"Invalid estimated_time, using default: {num_questions * 3} minutes")
        estimated_time = num_questions * 3
    
    # 검증 이슈 로깅
    if issues:
        logger.warning(f"Exam validation issues: {issues}")
    
    # 정제된 데이터 반환
    return {
        'questions': validated_questions,
        'total_points': total_calculated_points,
        'estimated_time': estimated_time,
        'validation_issues': issues
    }


def validate_scoring_rubric(
    rubric: List[Dict[str, Any]], 
    question_points: float, 
    question_num: int, 
    issues: List[str]
) -> float:
    """
    채점 기준(rubric) 검증
    
    Args:
        rubric: 채점 기준 리스트
        question_points: 문제의 총 배점
        question_num: 문제 번호 (에러 메시지용)
        issues: 이슈 리스트 (추가됨)
    
    Returns:
        rubric의 총점
    """
    if not isinstance(rubric, list):
        issues.append(f"Question {question_num}: scoring_rubric must be a list")
        return 0.0
    
    rubric_total = 0.0
    for i, criterion in enumerate(rubric):
        if not isinstance(criterion, dict):
            issues.append(f"Question {question_num}: rubric item {i+1} must be an object")
            continue
        
        if 'criterion' not in criterion:
            issues.append(f"Question {question_num}: rubric item {i+1} missing 'criterion'")
        
        if 'points' not in criterion:
            issues.append(f"Question {question_num}: rubric item {i+1} missing 'points'")
        else:
            try:
                points = float(criterion['points'])
                if points < 0:
                    issues.append(f"Question {question_num}: rubric item {i+1} has negative points")
                rubric_total += points
            except (ValueError, TypeError):
                issues.append(f"Question {question_num}: rubric item {i+1} has invalid points value")
    
    # rubric 총점이 문제 배점과 일치하는지 확인 (±1점 허용)
    if abs(rubric_total - question_points) > 1:
        issues.append(
            f"Question {question_num}: rubric total ({rubric_total}) doesn't match question points ({question_points})"
        )
        logger.warning(
            f"Question {question_num}: rubric points sum to {rubric_total}, but question is worth {question_points}"
        )
    
    return rubric_total



