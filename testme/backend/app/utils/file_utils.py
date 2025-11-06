"""
File utility functions
"""
import os
import uuid
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """
    Check if file has allowed extension
    
    Args:
        filename: Original filename
        allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'txt'})
    
    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(original_filename):
    """
    Generate unique filename using UUID
    
    Args:
        original_filename: Original filename from upload
    
    Returns:
        str: UUID-based filename with original extension
        
    Example:
        'lecture.pdf' -> '7a8f3c2d-1b4e-4a9c-8d2f-3e5a6b7c8d9e.pdf'
    """
    # Get file extension
    ext = ''
    if '.' in original_filename:
        ext = original_filename.rsplit('.', 1)[1].lower()
    
    # Generate UUID filename
    unique_filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    
    return unique_filename


def get_user_upload_directory(upload_folder, user_id):
    """
    Get upload directory path for specific user
    
    Args:
        upload_folder: Base upload folder
        user_id: Firebase user UID
    
    Returns:
        str: Full path to user's upload directory
    """
    user_dir = os.path.join(upload_folder, user_id)
    
    # Create directory if it doesn't exist
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    return user_dir


def get_file_size(file_path):
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
    
    Returns:
        int: File size in bytes
    """
    return os.path.getsize(file_path)

