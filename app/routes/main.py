"""
Main routes (root endpoints)
"""
import os
from flask import jsonify, current_app, send_from_directory, session, render_template
from werkzeug.utils import safe_join
from app.routes import main_bp


@main_bp.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        'name': 'test.me Backend API',
        'version': '1.0.0',
        'description': 'AI-powered exam generation and grading system',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'admin': '/admin-page',
            'api': '/api',
            'uploads': '/uploads/<path:filename>'
        }
    })


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'test.me API'
    }), 200


@main_bp.route('/admin-page')
def admin_page():
    """Admin page - login or dashboard"""
    if session.get('firebase_authenticated'):
        return render_template('admin/dashboard.html')
    return render_template('admin/login.html')


@main_bp.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """
    Serve uploaded files (PDFs)
    URL format: /uploads/{user_id}/{pdf_name}
    """
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = safe_join(upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_from_directory(
            upload_folder,
            filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f'Error serving file: {e}')
        return jsonify({'error': 'Internal server error'}), 500

