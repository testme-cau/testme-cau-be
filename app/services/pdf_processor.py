"""
PDF Processing Service
Extract text content from PDF files
"""
import PyPDF2
from flask import current_app


class PDFProcessor:
    """Service for processing PDF files"""
    
    @staticmethod
    def extract_text(file_path):
        """
        Extract text content from PDF file
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            dict: {
                'success': True,
                'text': 'extracted text content',
                'pages': 10,
                'word_count': 5000
            }
        """
        try:
            # Open PDF file
            with open(file_path, 'rb') as file:
                # Create PDF reader
                pdf_reader = PyPDF2.PdfReader(file)
                
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
    def get_pdf_info(file_path):
        """
        Get PDF metadata information
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            dict: PDF metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
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

