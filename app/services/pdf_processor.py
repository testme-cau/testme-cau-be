"""
PDF Processing Service
Extract text content from PDF files (from Firebase Storage or bytes)
"""
import io
import PyPDF2
from flask import current_app
from app.services.firebase_storage import FirebaseStorageService


class PDFProcessor:
    """Service for processing PDF files"""
    
    @staticmethod
    def extract_text_from_storage(storage_path):
        """
        Extract text content from PDF file in Firebase Storage
        
        Args:
            storage_path: Path to PDF in Firebase Storage
        
        Returns:
            dict: {
                'success': True,
                'text': 'extracted text content',
                'pages': 10,
                'word_count': 5000
            }
        """
        try:
            # Download file from Firebase Storage
            storage_service = FirebaseStorageService()
            file_bytes = storage_service.download_file(storage_path)
            
            # Create file-like object from bytes
            file_obj = io.BytesIO(file_bytes)
            
            # Extract text from file object
            return PDFProcessor.extract_text_from_bytes(file_obj)
        
        except Exception as e:
            current_app.logger.error(f'PDF text extraction from storage failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def extract_text_from_bytes(file_obj):
        """
        Extract text content from PDF file bytes
        
        Args:
            file_obj: File-like object (BytesIO or file handle)
        
        Returns:
            dict: {
                'success': True,
                'text': 'extracted text content',
                'pages': 10,
                'word_count': 5000
            }
        """
        try:
            # Ensure we're at the start of the file
            file_obj.seek(0)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            # Get number of pages
            num_pages = len(pdf_reader.pages)
            
            # Extract text from all pages
            text_content = []
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    text_content.append(text)
            
            # Combine all text
            full_text = '\n\n'.join(text_content)
            
            # Calculate word count
            word_count = len(full_text.split())
            
            return {
                'success': True,
                'text': full_text,
                'pages': num_pages,
                'word_count': word_count
            }
        
        except Exception as e:
            current_app.logger.error(f'PDF text extraction failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_pdf_info_from_storage(storage_path):
        """
        Get PDF metadata information from Firebase Storage
        
        Args:
            storage_path: Path to PDF in Firebase Storage
        
        Returns:
            dict: PDF metadata
        """
        try:
            # Download file from Firebase Storage
            storage_service = FirebaseStorageService()
            file_bytes = storage_service.download_file(storage_path)
            
            # Create file-like object from bytes
            file_obj = io.BytesIO(file_bytes)
            
            # Get PDF info
            return PDFProcessor.get_pdf_info_from_bytes(file_obj)
        
        except Exception as e:
            current_app.logger.error(f'PDF info extraction from storage failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_pdf_info_from_bytes(file_obj):
        """
        Get PDF metadata information from bytes
        
        Args:
            file_obj: File-like object (BytesIO or file handle)
        
        Returns:
            dict: PDF metadata
        """
        try:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            # Get metadata
            metadata = pdf_reader.metadata
            
            info = {
                'pages': len(pdf_reader.pages),
                'title': metadata.get('/Title', 'Unknown') if metadata else 'Unknown',
                'author': metadata.get('/Author', 'Unknown') if metadata else 'Unknown',
                'creator': metadata.get('/Creator', 'Unknown') if metadata else 'Unknown',
            }
            
            return {
                'success': True,
                'info': info
            }
        
        except Exception as e:
            current_app.logger.error(f'PDF info extraction failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }

