"""
Analytics helper for admin dashboard KPIs.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from firebase_admin import firestore

from app.models.admin import AnalyticsSummary, AnalyticsSummaryResponse, UserAnalytics


def _to_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return value.to_datetime()
    except AttributeError:
        return None


class AdminAnalyticsService:
    """Aggregate Firestore usage metrics for admin dashboard."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = firestore.client()
        return self._db

    def _collect_user_stats(self) -> Tuple[List[UserAnalytics], AnalyticsSummary]:
        users_ref = self.db.collection("users")
        user_docs = list(users_ref.stream())

        per_user_stats: List[UserAnalytics] = []
        total_subjects = 0
        total_exams = 0
        total_pdfs = 0
        mau_count = 0
        now = datetime.utcnow()
        mau_cutoff = now - timedelta(days=30)

        for doc in user_docs:
            data = doc.to_dict() or {}
            uid = data.get("uid") or doc.id
            email = data.get("email")

            subjects_ref = doc.reference.collection("subjects")
            subjects = list(subjects_ref.stream())
            subject_count = len(subjects)
            total_subjects += subject_count

            exam_count = 0
            pdf_count = 0
            for subject_doc in subjects:
                exams_ref = subject_doc.reference.collection("exams")
                exam_count += len(list(exams_ref.stream()))

                pdfs_ref = subject_doc.reference.collection("pdfs")
                pdf_count += len(list(pdfs_ref.stream()))

            total_exams += exam_count
            total_pdfs += pdf_count

            last_active = (
                _to_datetime(data.get("last_login"))
                or _to_datetime(data.get("updated_at"))
                or _to_datetime(data.get("created_at"))
            )
            if last_active and last_active >= mau_cutoff:
                mau_count += 1

            per_user_stats.append(
                UserAnalytics(
                    uid=uid,
                    email=email,
                    subject_count=subject_count,
                    exam_count=exam_count,
                    pdf_count=pdf_count,
                    last_active=last_active,
                )
            )

        total_users = len(user_docs)
        summary = AnalyticsSummary(
            total_users=total_users,
            monthly_active_users=mau_count,
            total_subjects=total_subjects,
            total_exams=total_exams,
            total_pdfs=total_pdfs,
            average_subjects_per_user=round(
                total_subjects / total_users, 2
            ) if total_users else 0.0,
            average_exams_per_user=round(
                total_exams / total_users, 2
            ) if total_users else 0.0,
        )
        return per_user_stats, summary

    def get_summary(self, per_user_limit: int = 50) -> AnalyticsSummaryResponse:
        """Return aggregated numbers capped by per_user_limit list."""
        user_stats, summary = self._collect_user_stats()
        user_stats.sort(key=lambda item: item.exam_count, reverse=True)
        limited_users = user_stats[:per_user_limit]
        return AnalyticsSummaryResponse(
            success=True,
            summary=summary,
            users=limited_users,
        )

