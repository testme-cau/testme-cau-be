"""
Submission repository for Firestore operations
Path: users/{user_id}/subjects/{subject_id}/exams/{exam_id}/submissions/{submission_id}
"""
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from firebase_admin import firestore


class SubmissionRepository:
    def __init__(self):
        self.db = firestore.client()
    
    def create_submission(
        self, 
        user_id: str, 
        subject_id: str, 
        exam_id: str, 
        submission_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """답안 제출 생성 (중복 체크 포함)"""
        # 중복 제출 체크
        existing = self.get_by_user_and_exam(user_id, subject_id, exam_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already submitted this exam"
            )
        
        # 새 제출 생성
        ref = (self.db.collection('users').document(user_id)
               .collection('subjects').document(subject_id)
               .collection('exams').document(exam_id)
               .collection('submissions').document())
        
        submission_data['submission_id'] = ref.id
        submission_data['submitted_at'] = datetime.utcnow()
        submission_data['status'] = 'pending'
        
        ref.set(submission_data)
        return {**submission_data, 'submission_id': ref.id}
    
    def update_grading_result(
        self, 
        user_id: str, 
        subject_id: str, 
        exam_id: str, 
        submission_id: str, 
        grading_data: Dict[str, Any]
    ) -> None:
        """채점 결과 업데이트"""
        ref = (self.db.collection('users').document(user_id)
               .collection('subjects').document(subject_id)
               .collection('exams').document(exam_id)
               .collection('submissions').document(submission_id))
        
        if 'status' in grading_data and grading_data['status'] in ['graded', 'failed']:
            grading_data['graded_at'] = datetime.utcnow()
        
        ref.update(grading_data)
    
    def get_by_user_and_exam(
        self, 
        user_id: str, 
        subject_id: str, 
        exam_id: str
    ) -> Optional[Dict[str, Any]]:
        """특정 사용자의 특정 시험 제출 조회 (중복 체크 및 결과 조회용)"""
        docs = (self.db.collection('users').document(user_id)
                .collection('subjects').document(subject_id)
                .collection('exams').document(exam_id)
                .collection('submissions')
                .where('user_id', '==', user_id)
                .limit(1).stream())
        
        for doc in docs:
            return {**doc.to_dict(), 'submission_id': doc.id}
        return None

