"""
Admin routes (web-based testing interface)
"""
from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from functools import wraps
from app.routes import admin_bp


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('-page')
def admin_page():
    """Admin page - login or dashboard"""
    if session.get('admin_authenticated'):
        return render_template('admin/dashboard.html')
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    admin_pw = data.get('admin_pw')
    
    # Verify credentials from config
    if (admin_id == current_app.config['ADMIN_ID'] and 
        admin_pw == current_app.config['ADMIN_PW']):
        session['admin_authenticated'] = True
        session['admin_id'] = admin_id
        return jsonify({
            'success': True,
            'message': 'Login successful'
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
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard API endpoint"""
    return jsonify({
        'admin_id': session.get('admin_id'),
        'message': 'Welcome to test.me admin dashboard'
    })

