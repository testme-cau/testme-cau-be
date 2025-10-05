"""
Main routes (root endpoints)
"""
from flask import jsonify, current_app
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
            'api': '/api'
        }
    })


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'test.me API'
    }), 200

