from datetime import datetime
from unittest.mock import Mock

import pytest

from app.services.exam_service import ExamService
from app.utils.exam_utils import compute_pdf_signature, normalize_pdf_ids
from config import settings


def test_compute_pdf_signature_order_invariant():
    pdf_ids_a = ["pdf-1", "pdf-2", "pdf-3"]
    pdf_ids_b = ["pdf-3", "pdf-2", "pdf-1", ""]
    
    signature_a = compute_pdf_signature(pdf_ids_a)
    signature_b = compute_pdf_signature(pdf_ids_b)
    
    assert signature_a == signature_b
    assert signature_a != ""


def test_normalize_pdf_ids_filters_empty():
    pdf_ids = ["pdf-1", None, "", " pdf-2 "]
    normalized = normalize_pdf_ids(pdf_ids)  # type: ignore[arg-type]
    
    assert normalized == ["pdf-1", "pdf-2"]


def test_build_previous_context_respects_limits(monkeypatch):
    service = ExamService(
        exam_repo=Mock(),
        subject_repo=Mock(),
        pdf_service=Mock(),
        exam_job_repo=Mock(),
        grading_job_repo=Mock(),
        submission_repo=Mock()
    )
    
    submissions = [
        {
            'exam_data': {
                'questions': [{'id': 1, 'question': 'Q1', 'topic': '네트워크', 'points': 10}]
            },
            'grading_result': {
                'question_results': [{'question_id': 1, 'score': 5, 'max_points': 10, 'feedback': 'Needs work'}]
            },
            'answers': [{'question_id': 1, 'answer': 'Answer 1'}],
            'submitted_at': datetime(2024, 1, 1, 10, 0, 0)
        },
        {
            'exam_data': {
                'questions': [{'id': 2, 'question': 'Q2', 'topic': '알고리즘', 'points': 10}]
            },
            'grading_result': {
                'question_results': [{'question_id': 2, 'score': 9, 'max_points': 10, 'feedback': 'Great job'}]
            },
            'answers': [{'question_id': 2, 'answer': 'Answer 2'}],
            'submitted_at': datetime(2024, 1, 2, 10, 0, 0)
        },
        {
            'exam_data': {
                'questions': [{'id': 3, 'question': 'Q3', 'topic': '네트워크', 'points': 10}]
            },
            'grading_result': {
                'question_results': [{'question_id': 3, 'score': 2, 'max_points': 10, 'feedback': 'Very weak'}]
            },
            'answers': [{'question_id': 3, 'answer': 'Answer 3'}],
            'submitted_at': datetime(2024, 1, 3, 10, 0, 0)
        },
    ]
    
    monkeypatch.setattr(settings, 'exam_history_limit', 2, raising=False)
    monkeypatch.setattr(settings, 'exam_history_per_topic', 1, raising=False)
    monkeypatch.setattr(settings, 'exam_history_feedback_max_chars', 5, raising=False)
    
    context = service._build_previous_context(submissions)  # noqa: SLF001 (intentional private use for test)
    
    assert len(context) == 2
    topics = {entry['topic'] for entry in context}
    assert topics == {'네트워크', '알고리즘'}
    assert context[0]['score'] <= context[1]['score']
    assert len(context[0]['feedback']) <= 5

