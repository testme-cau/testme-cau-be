"""
Utility helpers for exam-related operations.
"""
from __future__ import annotations

from hashlib import sha1
from typing import Iterable, List


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

