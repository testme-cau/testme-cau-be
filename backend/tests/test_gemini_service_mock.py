"""
Test Gemini Service (Mock)
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module under test
import app.services.gemini_service

@pytest.fixture
def mock_gemini_service():
    with patch.dict(os.environ, {'GOOGLE_API_KEY': 'dummy-key'}):
        # Patch 'genai' in the namespace of app.services.gemini_service
        # This replaces the imported google.generativeai module with a mock
        with patch('app.services.gemini_service.genai') as mock_genai:
            # Setup mock model
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Setup file mocks
            mock_file = MagicMock()
            mock_file.name = "uploaded_file_id"
            mock_genai.upload_file.return_value = mock_file
            
            # Setup delete_file mock
            mock_genai.delete_file.return_value = None
            
            # Import class
            from app.services.gemini_service import GeminiService
            service = GeminiService(api_key='dummy-key', model='gemini-2.5-pro')
            
            yield service, mock_model, mock_genai.upload_file, mock_genai.delete_file

@pytest.mark.asyncio
async def test_generate_exam_success(mock_gemini_service):
    """Test successful exam generation with mocked response"""
    service, mock_model, mock_upload, mock_delete = mock_gemini_service
    
    # Verify patch is working
    import app.services.gemini_service
    # Ensure the genai attribute is indeed a Mock
    assert isinstance(app.services.gemini_service.genai, MagicMock), "genai was not patched correctly"
    
    # Mock response data
    mock_exam_data = {
        "title": "Test Exam",
        "questions": [
            {
                "id": 1,
                "question": "Test Question?",
                "type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "points": 10,
                "model_answer": "B is correct because..."
            }
        ],
        "total_points": 100,
        "estimated_time": 60
    }
    
    # Configure mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_exam_data)
    
    # Mock _run_blocking to handle different calls
    # We need to mock this because _run_blocking executes the function in a thread.
    # If we don't mock it, it will execute the mock function which returns a mock, which is fine.
    # BUT, we want to control the return value of generate_content to be our response object.
    
    async def mock_run_blocking(func, *args, **kwargs):
        # If func is the mock_upload function
        if func == mock_upload:
             return mock_upload.return_value
        # If func is mock_delete
        elif func == mock_delete:
             return None
        # If func is mock_model.generate_content
        elif func == mock_model.generate_content:
             return mock_response
        
        # Fallback: if func is a mock, calling it returns its configured return value
        if isinstance(func, MagicMock):
            return func(*args, **kwargs)
            
        return mock_response

    with patch.object(service, '_run_blocking', side_effect=mock_run_blocking):
        result = await service.generate_exam_from_pdf(
            pdf_bytes=b"fake pdf content",
            original_filename="test.pdf",
            num_questions=1
        )
        
        assert result['success'] is True
        assert result['exam']['title'] == "Test Exam"
        assert len(result['exam']['questions']) == 1
        assert result['model'] == 'gemini-2.5-pro'

@pytest.mark.asyncio
async def test_generate_exam_failure(mock_gemini_service):
    """Test exam generation failure handling"""
    service, mock_model, mock_upload, mock_delete = mock_gemini_service
    
    # Mock failure
    async def mock_run_blocking_fail(func, *args, **kwargs):
        if func == mock_upload:
             return mock_upload.return_value
        raise Exception("API Error")

    with patch.object(service, '_run_blocking', side_effect=mock_run_blocking_fail):
        result = await service.generate_exam_from_pdf(
            pdf_bytes=b"fake pdf content",
            original_filename="test.pdf"
        )
        
        assert result['success'] is False
        assert "API Error" in result['error']

@pytest.mark.asyncio
async def test_grade_answer_success(mock_gemini_service):
    """Test simple answer grading"""
    service, mock_model, _, _ = mock_gemini_service
    
    mock_grade_data = {
        "score": 85,
        "feedback": "Good job",
        "is_correct": True
    }
    
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_grade_data)
    
    async def mock_run_blocking(func, *args, **kwargs):
        return mock_response

    with patch.object(service, '_run_blocking', side_effect=mock_run_blocking):
        result = await service.grade_answer(
            question="Test question",
            student_answer="Test answer"
        )
        
        assert result['success'] is True
        assert result['grade']['score'] == 85
        assert result['grade']['is_correct'] is True