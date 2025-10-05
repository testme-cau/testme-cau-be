"""
Blueprint initialization
"""
from flask import Blueprint

# Main blueprint (root routes)
main_bp = Blueprint('main', __name__)

# Admin blueprint (admin page)
admin_bp = Blueprint('admin', __name__)

# API blueprint (REST API endpoints)
api_bp = Blueprint('api', __name__)

# Import routes to register them with blueprints
from app.routes import main, admin, api

