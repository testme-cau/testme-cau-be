"""
Admin routes (web-based testing interface)
"""
from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from functools import wraps
from app.routes import admin_bp


def admin_gate_required(f):
    """Decorator to require admin gate authentication (Step 1)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function


def firebase_auth_required(f):
    """Decorator to require full authentication (Step 1 + Step 2)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.admin_login_page'))
        if not session.get('firebase_authenticated'):
            return redirect(url_for('admin.oauth_page'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login-page')
def admin_login_page():
    """Step 1: Admin gate login page"""
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Step 1: Admin gate login (access control)"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    admin_pw = data.get('admin_pw')
    
    # Verify credentials from config
    if (admin_id == current_app.config['ADMIN_ID'] and 
        admin_pw == current_app.config['ADMIN_PW']):
        # Step 1 passed - allow access to OAuth page
        session['admin_authenticated'] = True
        session['admin_id'] = admin_id
        return jsonify({
            'success': True,
            'message': 'Admin authentication successful'
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    }), 401


@admin_bp.route('/oauth')
@admin_gate_required
def oauth_page():
    """Step 2: OAuth login page (requires Step 1)"""
    return render_template('admin/oauth.html')


@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    """Logout - clear all session data"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@admin_bp.route('/dashboard')
@firebase_auth_required
def admin_dashboard():
    """Admin dashboard API endpoint - returns session info"""
    firebase_user = session.get('firebase_user', {})
    return jsonify({
        'authenticated': True,
        'user': firebase_user,
        'message': 'Welcome to test.me admin dashboard'
    })


@admin_bp.route('/session-info')
@firebase_auth_required
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

