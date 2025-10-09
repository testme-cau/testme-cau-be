"""
PDF routes (file upload and management)
"""
import os
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, redirect
from firebase_admin import firestore
from werkzeug.utils import secure_filename
from app.routes import api_bp
from app.routes.api import require_firebase_auth
from app.services.firebase_storage import FirebaseStorageService
from app.utils.file_utils import allowed_file


@api_bp.route('/pdf/upload', methods=['POST'])
@require_firebase_auth
def upload_pdf():
    """
    Upload PDF file to Firebase Storage
    
    Request:
        - multipart/form-data
        - file: PDF file
    
    Response:
        {
            "success": true,
            "file_id": "uuid",
            "original_filename": "lecture.pdf",
            "file_url": "/api/pdf/{file_id}/download",
            "uploaded_at": "2025-10-06T...",
            "size": 1024000
        }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > current_app.config['MAX_FILE_SIZE']:
            return jsonify({
                'error': 'File too large',
                'max_size': current_app.config['MAX_FILE_SIZE']
            }), 400
        
        # Get user info
        user_uid = request.user['uid']
        
        # Upload to Firebase Storage
        storage_service = FirebaseStorageService()
        upload_result = storage_service.upload_file(
            file,
            user_uid,
            file.filename
        )
        
        # Get file size from Firebase Storage
        file_size = storage_service.get_file_size(upload_result['storage_path'])
        
        # Save metadata to Firestore
        db = firestore.client()
        file_id = upload_result['file_id']
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        
        pdf_data = {
            'file_id': file_id,
            'original_filename': upload_result['original_filename'],
            'unique_filename': upload_result['unique_filename'],
            'storage_path': upload_result['storage_path'],
            'size': file_size,
            'user_id': user_uid,
            'uploaded_at': firestore.SERVER_TIMESTAMP,
            'status': 'uploaded'
        }
        
        pdf_ref.set(pdf_data)
        
        # Construct file URL
        file_url = f"/api/pdf/{file_id}/download"
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'original_filename': upload_result['original_filename'],
            'file_url': file_url,
            'uploaded_at': datetime.utcnow().isoformat(),
            'size': file_size
        }), 201
        
    except Exception as e:
        current_app.logger.error(f'Upload failed: {e}')
        return jsonify({'error': 'Upload failed', 'details': str(e)}), 500


@api_bp.route('/pdf/<file_id>/download', methods=['GET'])
@require_firebase_auth
def download_pdf(file_id):
    """
    Download PDF file from Firebase Storage
    Returns a signed URL that redirects to the file
    
    Args:
        file_id: UUID of the file
    
    Response:
        Redirect to signed URL or error
    """
    try:
        user_uid = request.user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            return jsonify({'error': 'File not found'}), 404
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate signed URL from Firebase Storage
        storage_service = FirebaseStorageService()
        signed_url = storage_service.get_download_url(
            pdf_data['storage_path'],
            expiration=timedelta(hours=1)
        )
        
        # Redirect to signed URL
        return redirect(signed_url)
        
    except FileNotFoundError:
        return jsonify({'error': 'File not found in storage'}), 404
    except Exception as e:
        current_app.logger.error(f'Download failed: {e}')
        return jsonify({'error': 'Download failed', 'details': str(e)}), 500


@api_bp.route('/pdf/list', methods=['GET'])
@require_firebase_auth
def list_pdfs():
    """
    List all PDFs for current user
    
    Response:
        {
            "success": true,
            "pdfs": [
                {
                    "file_id": "uuid",
                    "original_filename": "lecture.pdf",
                    "file_url": "/api/pdf/{file_id}/download",
                    "size": 1024000,
                    "uploaded_at": "2025-10-06T..."
                },
                ...
            ]
        }
    """
    try:
        user_uid = request.user['uid']
        
        # Get all PDFs for user
        db = firestore.client()
        pdfs_ref = db.collection('users').document(user_uid).collection('pdfs')
        pdfs = pdfs_ref.order_by('uploaded_at', direction=firestore.Query.DESCENDING).stream()
        
        pdf_list = []
        for pdf in pdfs:
            pdf_data = pdf.to_dict()
            pdf_list.append({
                'file_id': pdf_data['file_id'],
                'original_filename': pdf_data['original_filename'],
                'file_url': f"/api/pdf/{pdf_data['file_id']}/download",
                'size': pdf_data['size'],
                'uploaded_at': pdf_data.get('uploaded_at'),
                'status': pdf_data.get('status', 'uploaded')
            })
        
        return jsonify({
            'success': True,
            'pdfs': pdf_list,
            'count': len(pdf_list)
        })
        
    except Exception as e:
        current_app.logger.error(f'List PDFs failed: {e}')
        return jsonify({'error': 'Failed to list PDFs', 'details': str(e)}), 500


@api_bp.route('/pdf/<file_id>', methods=['DELETE'])
@require_firebase_auth
def delete_pdf(file_id):
    """
    Delete PDF file from Firebase Storage and Firestore
    
    Args:
        file_id: UUID of the file
    
    Response:
        {
            "success": true,
            "message": "File deleted successfully"
        }
    """
    try:
        user_uid = request.user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            return jsonify({'error': 'File not found'}), 404
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete file from Firebase Storage
        storage_service = FirebaseStorageService()
        storage_service.delete_file(pdf_data['storage_path'])
        
        # Delete metadata from Firestore
        pdf_ref.delete()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f'Delete failed: {e}')
        return jsonify({'error': 'Delete failed', 'details': str(e)}), 500

