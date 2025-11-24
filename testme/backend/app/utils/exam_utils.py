"""
Utility helpers for exam-related operations.
"""
from __future__ import annotations

from hashlib import sha1
from typing import Any, Dict, Iterable, List


def normalize_pdf_ids(pdf_ids: Iterable[str]) -> List[str]:
    """
    Normalize PDF ID list by removing falsy values and trimming whitespace.
    """
    if not pdf_ids:
        return []
    return [pdf_id.strip() for pdf_id in pdf_ids if pdf_id]


def compute_pdf_signature(pdf_ids: Iterable[str]) -> str:
    """
    Generate a deterministic signature for a set of PDF IDs.
    
    Sorting ensures the signature stays the same regardless of request order.
    """
    normalized_ids = normalize_pdf_ids(pdf_ids)
    if not normalized_ids:
        return ""
    
    normalized_ids.sort()
    joined = "|".join(normalized_ids)
    return sha1(joined.encode("utf-8")).hexdigest()


def normalize_exam_points(
    exam_payload: Dict[str, Any],
    target_total: float = 100.0,
    precision: int = 2
) -> Dict[str, Any]:
    """
    Normalize question- and rubric-level points so the exam totals the target score.
    """
    if not exam_payload or target_total <= 0:
        return exam_payload

    questions = exam_payload.get("questions")
    if not isinstance(questions, list) or not questions:
        return exam_payload

    current_total = sum(_safe_points(q.get("points")) for q in questions)
    if current_total <= 0:
        return exam_payload

    scale = target_total / current_total
    positive_indices = [
        idx for idx, q in enumerate(questions) if _safe_points(q.get("points")) > 0
    ]
    if not positive_indices:
        return exam_payload
    last_positive_index = positive_indices[-1]

    normalized_questions: List[Dict[str, Any]] = []
    running_total = 0.0

    for idx, question in enumerate(questions):
        original_points = _safe_points(question.get("points"))
        normalized_question = dict(question)

        if original_points <= 0:
            normalized_question["points"] = round(0.0, precision)
            normalized_questions.append(normalized_question)
            continue

        scaled_points = original_points * scale
        if idx != last_positive_index:
            scaled_points = round(scaled_points, precision)
            running_total += scaled_points
        else:
            scaled_points = round(max(target_total - running_total, 0.0), precision)
            running_total += scaled_points

        normalized_question["points"] = scaled_points
        normalized_question["scoring_rubric"] = _normalize_scoring_rubric_points(
            normalized_question.get("scoring_rubric"),
            original_points,
            scaled_points,
            precision,
        )
        normalized_questions.append(normalized_question)

    normalized_payload = dict(exam_payload)
    normalized_payload["questions"] = normalized_questions
    normalized_payload["total_points"] = round(target_total, precision)
    return normalized_payload


def _safe_points(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_scoring_rubric_points(
    rubric: Any,
    original_question_points: float,
    normalized_question_points: float,
    precision: int,
) -> Any:
    if not isinstance(rubric, list) or original_question_points <= 0:
        return rubric

    positive_indices = [
        idx
        for idx, item in enumerate(rubric)
        if isinstance(item, dict) and _safe_points(item.get("points")) > 0
    ]
    if not positive_indices:
        return rubric
    last_positive_index = positive_indices[-1]

    normalized_rubric: List[Dict[str, Any]] = []
    question_scale = (
        normalized_question_points / original_question_points
        if original_question_points > 0
        else 1.0
    )
    running_total = 0.0

    for idx, item in enumerate(rubric):
        if not isinstance(item, dict):
            normalized_rubric.append(item)
            continue

        normalized_item = dict(item)
        base_points = _safe_points(item.get("points"))

        if base_points <= 0:
            normalized_item["points"] = round(0.0, precision)
            normalized_rubric.append(normalized_item)
            continue

        scaled_points = base_points * question_scale
        if idx != last_positive_index:
            scaled_points = round(scaled_points, precision)
            running_total += scaled_points
        else:
            scaled_points = round(
                max(normalized_question_points - running_total, 0.0), precision
            )
            running_total += scaled_points

        normalized_item["points"] = scaled_points
        normalized_rubric.append(normalized_item)

    return normalized_rubric

