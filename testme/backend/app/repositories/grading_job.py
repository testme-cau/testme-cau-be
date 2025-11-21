"""
Repository for grading jobs stored under subjects
Path: users/{user_id}/subjects/{subject_id}/grading_jobs/{job_id}
"""
from typing import Dict, Any, List
from firebase_admin import firestore
from fastapi import HTTPException, status
from datetime import datetime


class GradingJobRepository:
    """Firestore repository for grading job documents."""

    def __init__(self):
        self.db = firestore.client()

    def _get_collection(self, user_id: str, subject_id: str):
        return (self.db.collection('users')
                .document(user_id)
                .collection('subjects')
                .document(subject_id)
                .collection('grading_jobs'))

    def create_job(self, user_id: str, subject_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            col_ref = self._get_collection(user_id, subject_id)
            job_ref = col_ref.document()
            job_data['job_id'] = job_ref.id
            job_data['created_at'] = firestore.SERVER_TIMESTAMP
            job_data.setdefault('status', 'pending')
            job_ref.set(job_data)
            return job_ref.get().to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create grading job: {str(e)}"
            )

    def list_jobs(self, user_id: str, subject_id: str) -> List[Dict[str, Any]]:
        try:
            col_ref = self._get_collection(user_id, subject_id)
            docs = col_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list grading jobs: {str(e)}"
            )

    def get_job(self, user_id: str, subject_id: str, job_id: str) -> Dict[str, Any]:
        try:
            job_ref = self._get_collection(user_id, subject_id).document(job_id)
            doc = job_ref.get()
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Grading job not found"
                )
            return doc.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get grading job: {str(e)}"
            )

    def update_job(self, user_id: str, subject_id: str, job_id: str, data: Dict[str, Any]) -> None:
        try:
            job_ref = self._get_collection(user_id, subject_id).document(job_id)
            data['updated_at'] = datetime.utcnow()
            job_ref.update(data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update grading job: {str(e)}"
            )

    def delete_job(self, user_id: str, subject_id: str, job_id: str) -> None:
        try:
            self._get_collection(user_id, subject_id).document(job_id).delete()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete grading job: {str(e)}"
            )


