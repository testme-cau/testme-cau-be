"""
Admin routes (web-based testing interface)
"""
from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from functools import wraps
from app.routes import admin_bp


def admin_required(f):
    """Decorator to require admin authentication (Firebase OAuth)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('firebase_authenticated'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('-page')
def admin_page():
    """Admin page - login or dashboard"""
    if session.get('firebase_authenticated'):
        return render_template('admin/dashboard.html')
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Legacy admin login endpoint (deprecated, use Firebase OAuth instead)"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    admin_pw = data.get('admin_pw')
    
    # Verify credentials from config
    if (admin_id == current_app.config['ADMIN_ID'] and 
        admin_pw == current_app.config['ADMIN_PW']):
        # Create a mock Firebase user for backward compatibility
        session['firebase_authenticated'] = True
        session['admin_id'] = admin_id
        session['firebase_user'] = {
            'uid': f'admin_{admin_id}',
            'email': f'{admin_id}@test.me',
            'displayName': f'Admin {admin_id}',
            'photoURL': None
        }
        # Note: No real Firebase token in this case
        return jsonify({
            'success': True,
            'message': 'Legacy admin login successful (Firebase OAuth recommended)'
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    }), 401


@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    session.pop('admin_authenticated', None)
    session.pop('admin_id', None)
    session.pop('firebase_authenticated', None)
    session.pop('firebase_token', None)
    session.pop('firebase_user', None)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard API endpoint - returns session info"""
    firebase_user = session.get('firebase_user', {})
    return jsonify({
        'authenticated': True,
        'user': firebase_user,
        'message': 'Welcome to test.me admin dashboard'
    })


@admin_bp.route('/session-info')
@admin_required
def session_info():
    """Get current session information including Firebase user and token"""
    return jsonify({
        'authenticated': session.get('firebase_authenticated', False),
        'user': session.get('firebase_user', {}),
        'has_token': bool(session.get('firebase_token'))
    })


@admin_bp.route('/firebase-config')
def firebase_config():
    """Get Firebase Web SDK configuration for OAuth login"""
    return jsonify({
        'apiKey': current_app.config.get('FIREBASE_API_KEY'),
        'authDomain': current_app.config.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': current_app.config.get('FIREBASE_PROJECT_ID')
    })


@admin_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    """Store Firebase user info in session after OAuth login"""
    data = request.get_json()
    firebase_token = data.get('idToken')
    user_info = data.get('user')
    
    if not firebase_token or not user_info:
        return jsonify({
            'success': False,
            'error': 'Missing token or user info'
        }), 400
    
    # Store Firebase auth info in session
    session['firebase_authenticated'] = True
    session['firebase_token'] = firebase_token
    session['firebase_user'] = {
        'uid': user_info.get('uid'),
        'email': user_info.get('email'),
        'displayName': user_info.get('displayName'),
        'photoURL': user_info.get('photoURL')
    }
    
    return jsonify({
        'success': True,
        'message': 'Firebase login successful',
        'user': session['firebase_user']
    })

