"""
Exam routes (exam generation and management)
"""
import os
from datetime import datetime
from flask import request, jsonify, current_app
from firebase_admin import firestore
from app.routes import api_bp
from app.routes.api import require_firebase_auth
from app.services.gpt_service import GPTService
from app.services.firebase_storage import FirebaseStorageService


@api_bp.route('/exam/generate', methods=['POST'])
@require_firebase_auth
def generate_exam():
    """
    Generate exam from PDF
    
    Request Body:
        {
            "pdf_id": "uuid",
            "num_questions": 10,
            "difficulty": "medium"
        }
    
    Response:
        {
            "success": true,
            "exam_id": "uuid",
            "questions": [...],
            "total_points": 100,
            "estimated_time": 60
        }
    """
    try:
        user_uid = request.user['uid']
        data = request.get_json()
        
        # Validate request
        pdf_id = data.get('pdf_id')
        if not pdf_id:
            return jsonify({'error': 'pdf_id is required'}), 400
        
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        # Get PDF metadata from Firestore
        db = firestore.client()
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(pdf_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            return jsonify({'error': 'PDF not found'}), 404
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Download PDF from Firebase Storage
        storage_service = FirebaseStorageService()
        pdf_bytes = storage_service.download_file(pdf_data['storage_path'])
        
        # Generate exam using GPT (GPT will read the PDF directly)
        gpt_service = GPTService(api_key=current_app.config['OPENAI_API_KEY'])
        generation_result = gpt_service.generate_exam_from_pdf(
            pdf_bytes,
            pdf_data['original_filename'],
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        if not generation_result['success']:
            return jsonify({
                'error': 'Failed to generate exam',
                'details': generation_result.get('error')
            }), 500
        
        exam_data = generation_result['exam']
        
        # Save exam to Firestore
        exams_ref = db.collection('users').document(user_uid).collection('exams')
        exam_ref = exams_ref.document()
        exam_id = exam_ref.id
        
        exam_record = {
            'exam_id': exam_id,
            'pdf_id': pdf_id,
            'user_id': user_uid,
            'questions': exam_data['questions'],
            'total_points': exam_data['total_points'],
            'estimated_time': exam_data['estimated_time'],
            'num_questions': num_questions,
            'difficulty': difficulty,
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'active'
        }
        
        exam_ref.set(exam_record)
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'questions': exam_data['questions'],
            'total_points': exam_data['total_points'],
            'estimated_time': exam_data['estimated_time'],
            'created_at': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f'Exam generation failed: {e}')
        return jsonify({'error': 'Exam generation failed', 'details': str(e)}), 500


@api_bp.route('/exam/<exam_id>', methods=['GET'])
@require_firebase_auth
def get_exam(exam_id):
    """
    Get exam details
    
    Args:
        exam_id: Exam ID
    
    Response:
        {
            "success": true,
            "exam": {...}
        }
    """
    try:
        user_uid = request.user['uid']
        
        # Get exam from Firestore
        db = firestore.client()
        exam_ref = db.collection('users').document(user_uid).collection('exams').document(exam_id)
        exam_doc = exam_ref.get()
        
        if not exam_doc.exists:
            return jsonify({'error': 'Exam not found'}), 404
        
        exam_data = exam_doc.to_dict()
        
        # Verify ownership
        if exam_data.get('user_id') != user_uid:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'exam': exam_data
        })
        
    except Exception as e:
        current_app.logger.error(f'Get exam failed: {e}')
        return jsonify({'error': 'Failed to get exam', 'details': str(e)}), 500


@api_bp.route('/exam/list', methods=['GET'])
@require_firebase_auth
def list_exams():
    """
    List all exams for current user
    
    Response:
        {
            "success": true,
            "exams": [...]
        }
    """
    try:
        user_uid = request.user['uid']
        
        # Get all exams for user
        db = firestore.client()
        exams_ref = db.collection('users').document(user_uid).collection('exams')
        exams = exams_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        
        exam_list = []
        for exam in exams:
            exam_data = exam.to_dict()
            exam_list.append({
                'exam_id': exam_data['exam_id'],
                'pdf_id': exam_data.get('pdf_id'),
                'num_questions': exam_data.get('num_questions'),
                'total_points': exam_data.get('total_points'),
                'difficulty': exam_data.get('difficulty'),
                'created_at': exam_data.get('created_at'),
                'status': exam_data.get('status')
            })
        
        return jsonify({
            'success': True,
            'exams': exam_list,
            'count': len(exam_list)
        })
        
    except Exception as e:
        current_app.logger.error(f'List exams failed: {e}')
        return jsonify({'error': 'Failed to list exams', 'details': str(e)}), 500

