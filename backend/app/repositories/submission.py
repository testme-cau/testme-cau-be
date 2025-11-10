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
    
    def get_recent_submissions_for_pdfs(
        self,
        user_id: str,
        subject_id: str,
        pdf_ids: list,
        limit: int = 3
    ) -> list:
        """
        같은 PDF 조합으로 생성된 시험의 최근 제출 기록 조회
        
        Args:
            user_id: 사용자 ID
            subject_id: 과목 ID
            pdf_ids: PDF ID 리스트 (정렬된 상태)
            limit: 조회할 최대 개수 (기본 3개)
            
        Returns:
            제출 기록 리스트 (exam 정보 포함)
        """
        # PDF IDs를 정렬하여 비교용으로 사용
        sorted_pdf_ids = sorted(pdf_ids)
        
        # 모든 시험 조회
        exams_ref = (self.db.collection('users').document(user_id)
                    .collection('subjects').document(subject_id)
                    .collection('exams'))
        
        exams = exams_ref.stream()
        
        # 같은 PDF 조합을 가진 시험 필터링
        matching_exam_ids = []
        exam_data_map = {}
        
        for exam_doc in exams:
            exam_data = exam_doc.to_dict()
            exam_pdf_ids = exam_data.get('pdf_ids', [exam_data.get('pdf_id')])
            
            # PDF IDs 정렬하여 비교
            if sorted(exam_pdf_ids) == sorted_pdf_ids:
                matching_exam_ids.append(exam_doc.id)
                exam_data_map[exam_doc.id] = exam_data
        
        # 매칭되는 시험이 없으면 빈 리스트 반환
        if not matching_exam_ids:
            return []
        
        # 각 시험의 제출 기록 수집
        submissions_with_exam = []
        
        for exam_id in matching_exam_ids:
            submissions_ref = (exams_ref.document(exam_id)
                             .collection('submissions')
                             .where('user_id', '==', user_id)
                             .where('status', '==', 'graded'))
            
            for sub_doc in submissions_ref.stream():
                sub_data = sub_doc.to_dict()
                sub_data['submission_id'] = sub_doc.id
                sub_data['exam_data'] = exam_data_map[exam_id]
                submissions_with_exam.append(sub_data)
        
        # submitted_at 기준 내림차순 정렬
        submissions_with_exam.sort(
            key=lambda x: x.get('submitted_at', datetime.min),
            reverse=True
        )
        
        # 상위 N개만 반환
        return submissions_with_exam[:limit]

