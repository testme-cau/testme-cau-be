"""
Firebase Storage service for file management
"""
import uuid
from datetime import timedelta
from firebase_admin import storage
from werkzeug.utils import secure_filename


class FirebaseStorageService:
    """Service class for Firebase Storage operations"""
    
    def __init__(self):
        """Initialize Firebase Storage bucket"""
        self.bucket = storage.bucket()
    
    def upload_file(self, file, user_id, original_filename):
        """
        Upload file to Firebase Storage
        
        Args:
            file: File object from request.files
            user_id: Firebase user UID
            original_filename: Original filename from upload
        
        Returns:
            dict: {
                'file_id': str,  # UUID without extension
                'unique_filename': str,  # UUID-based filename
                'storage_path': str,  # Path in Firebase Storage
                'original_filename': str
            }
        
        Raises:
            Exception: If upload fails
        """
        # Generate unique filename
        ext = ''
        if '.' in original_filename:
            ext = original_filename.rsplit('.', 1)[1].lower()
        
        file_id = str(uuid.uuid4())
        unique_filename = f"{file_id}.{ext}" if ext else file_id
        
        # Construct storage path
        storage_path = f"pdfs/{user_id}/{unique_filename}"
        
        # Upload to Firebase Storage
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(file, content_type='application/pdf')
        
        # Make the file private (no public access)
        # Access will be controlled via signed URLs
        
        return {
            'file_id': file_id,
            'unique_filename': unique_filename,
            'storage_path': storage_path,
            'original_filename': secure_filename(original_filename)
        }
    
    def get_download_url(self, storage_path, expiration=timedelta(hours=1)):
        """
        Generate signed URL for file download
        
        Args:
            storage_path: Path to file in Firebase Storage
            expiration: URL expiration time (default: 1 hour)
        
        Returns:
            str: Signed URL for file download
        
        Raises:
            Exception: If URL generation fails
        """
        blob = self.bucket.blob(storage_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        
        # Generate signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        
        return url
    
    def delete_file(self, storage_path):
        """
        Delete file from Firebase Storage
        
        Args:
            storage_path: Path to file in Firebase Storage
        
        Returns:
            bool: True if deleted successfully
        
        Raises:
            Exception: If deletion fails
        """
        blob = self.bucket.blob(storage_path)
        
        if blob.exists():
            blob.delete()
            return True
        
        return False
    
    def file_exists(self, storage_path):
        """
        Check if file exists in Firebase Storage
        
        Args:
            storage_path: Path to file in Firebase Storage
        
        Returns:
            bool: True if file exists
        """
        blob = self.bucket.blob(storage_path)
        return blob.exists()
    
    def get_file_size(self, storage_path):
        """
        Get file size in bytes
        
        Args:
            storage_path: Path to file in Firebase Storage
        
        Returns:
            int: File size in bytes
        
        Raises:
            Exception: If file doesn't exist
        """
        blob = self.bucket.blob(storage_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        
        blob.reload()  # Refresh blob metadata
        return blob.size
    
    def download_file(self, storage_path):
        """
        Download file content from Firebase Storage
        
        Args:
            storage_path: Path to file in Firebase Storage
        
        Returns:
            bytes: File content
        
        Raises:
            Exception: If download fails
        """
        blob = self.bucket.blob(storage_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        
        return blob.download_as_bytes()

