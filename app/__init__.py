"""
Flask application factory
"""
import os
import firebase_admin
from firebase_admin import credentials
from flask import Flask
from flask_cors import CORS
from config import config


def create_app(config_name=None):
    """
    Create and configure Flask application
    
    Args:
        config_name: Configuration name ('development', 'production', or None for auto-detect)
    
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS_PATH'])
            firebase_admin.initialize_app(cred, {
                'storageBucket': app.config['FIREBASE_STORAGE_BUCKET']
            })
            app.logger.info('Firebase Admin SDK initialized successfully')
        except Exception as e:
            app.logger.warning(f'Firebase initialization failed: {e}')
            app.logger.warning('Some features may not work without Firebase credentials')
    
    # Register blueprints
    from app.routes import main_bp, admin_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

