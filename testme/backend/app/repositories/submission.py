"""
Submission repository for Firestore operations
Path: users/{user_id}/subjects/{subject_id}/exams/{exam_id}/submissions/{submission_id}
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from firebase_admin import firestore

from app.utils.exam_utils import compute_pdf_signature, normalize_pdf_ids


logger = logging.getLogger(__name__)

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

    def get_submission_by_id(
        self,
        user_id: str,
        subject_id: str,
        exam_id: str,
        submission_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch submission by explicit ID."""
        ref = (self.db.collection('users').document(user_id)
               .collection('subjects').document(subject_id)
               .collection('exams').document(exam_id)
               .collection('submissions').document(submission_id))
        doc = ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['submission_id'] = doc.id
            return data
        return None
    
    def get_recent_submissions_for_pdfs(
        self,
        user_id: str,
        subject_id: str,
        pdf_ids: List[str],
        limit: int = 3,
        per_exam_limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
        if limit <= 0:
            return []
        
        normalized_pdf_ids = normalize_pdf_ids(pdf_ids)
        sorted_pdf_ids = sorted(normalized_pdf_ids)
        pdf_signature = compute_pdf_signature(sorted_pdf_ids)
        
        exams_ref = (self.db.collection('users').document(user_id)
                     .collection('subjects').document(subject_id)
                     .collection('exams'))
        
        exam_docs: List[Any] = []
        exam_data_map: Dict[str, Dict[str, Any]] = {}
        
        if pdf_signature:
            try:
                exam_docs = list(
                    exams_ref.where('pdf_signature', '==', pdf_signature).stream()
                )
                for doc in exam_docs:
                    exam_data_map[doc.id] = doc.to_dict()
            except Exception as exc:
                logger.warning(f"Failed to query exams by pdf_signature: {exc}")
        
        # Fallback for older exams without pdf_signature or empty query result
        if not exam_docs:
            for exam_doc in exams_ref.stream():
                exam_data = exam_doc.to_dict()
                exam_pdf_ids = exam_data.get('pdf_ids')
                if not exam_pdf_ids and exam_data.get('pdf_id'):
                    exam_pdf_ids = [exam_data.get('pdf_id')]
                
                if sorted(normalize_pdf_ids(exam_pdf_ids or [])) == sorted_pdf_ids:
                    exam_docs.append(exam_doc)
                    exam_data_map[exam_doc.id] = exam_data
        
        if not exam_docs:
            return []
        
        per_exam_cap = per_exam_limit or limit
        per_exam_cap = max(1, min(per_exam_cap, limit))
        submissions_with_exam: List[Dict[str, Any]] = []
        
        for exam_doc in exam_docs:
            exam_id = exam_doc.id
            exam_data = exam_data_map.get(exam_id) or exam_doc.to_dict()
            submissions_ref = (exams_ref.document(exam_id)
                               .collection('submissions')
                               .where('user_id', '==', user_id)
                               .where('status', '==', 'graded')
                               .order_by('submitted_at', direction=firestore.Query.DESCENDING)
                               .limit(per_exam_cap))
            
            for sub_doc in submissions_ref.stream():
                sub_data = sub_doc.to_dict()
                sub_data['submission_id'] = sub_doc.id
                sub_data['exam_data'] = exam_data
                submissions_with_exam.append(sub_data)
        
        # submitted_at 기준 내림차순 정렬
        submissions_with_exam.sort(
            key=lambda x: x.get('submitted_at', datetime.min),
            reverse=True
        )
        
        # 상위 N개만 반환
        return submissions_with_exam[:limit]
    
    def get_submissions_by_subject(
        self,
        user_id: str,
        subject_id: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        과목의 모든 시험에 대한 제출 내역 조회 (exam_id로 매핑)
        
        Args:
            user_id: 사용자 ID
            subject_id: 과목 ID
            
        Returns:
            exam_id를 키로 하는 제출 내역 딕셔너리
            {exam_id: {submission_id, status, grading_result, ...}}
        """
        submissions_map = {}
        
        # 모든 시험 조회
        exams_ref = (self.db.collection('users').document(user_id)
                    .collection('subjects').document(subject_id)
                    .collection('exams'))
        
        exams = exams_ref.stream()
        
        # 각 시험의 제출 기록 조회
        for exam_doc in exams:
            exam_id = exam_doc.id
            submissions_ref = (exams_ref.document(exam_id)
                             .collection('submissions')
                             .where('user_id', '==', user_id)
                             .limit(1))  # 사용자당 1개의 제출만
            
            for sub_doc in submissions_ref.stream():
                sub_data = sub_doc.to_dict()
                sub_data['submission_id'] = sub_doc.id
                submissions_map[exam_id] = sub_data
                break  # 첫 번째 제출만
        
        return submissions_map

