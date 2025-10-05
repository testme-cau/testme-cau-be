"""
API routes (REST API endpoints for mobile app)
"""
from flask import jsonify, request, current_app
from functools import wraps
from firebase_admin import auth
from app.routes import api_bp


def require_firebase_auth(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        # Extract token
        id_token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify token with Firebase
            decoded_token = auth.verify_id_token(id_token)
            
            # Attach user info to request
            request.user = {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'firebase_user': decoded_token
            }
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f'Token verification failed: {e}')
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function


@api_bp.route('/health')
def api_health():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })


@api_bp.route('/test-auth')
@require_firebase_auth
def test_auth():
    """Test Firebase authentication"""
    return jsonify({
        'success': True,
        'user': {
            'uid': request.user['uid'],
            'email': request.user['email']
        },
        'message': 'Authentication successful'
    })


# TODO: Implement actual API endpoints
# - PDF upload
# - Exam generation
# - Answer submission
# - Grading

