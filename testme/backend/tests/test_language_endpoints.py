"""
Tests for language-related API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLanguageEndpoint:
    """Test GET /api/user/languages endpoint"""
    
    def test_get_languages_success(self):
        """Test successful retrieval of language list"""
        response = client.get("/api/user/languages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'languages' in data
        assert 'count' in data
        assert isinstance(data['languages'], list)
        assert data['count'] == len(data['languages'])
    
    def test_languages_structure(self):
        """Test that each language has required fields"""
        response = client.get("/api/user/languages")
        data = response.json()
        
        languages = data['languages']
        assert len(languages) > 0
        
        # Check first language structure
        lang = languages[0]
        assert 'code' in lang
        assert 'name' in lang
        assert 'native_name' in lang
        assert 'flag' in lang
    
    def test_languages_count(self):
        """Test that we have 14 supported languages"""
        response = client.get("/api/user/languages")
        data = response.json()
        
        assert data['count'] == 14
        assert len(data['languages']) == 14
    
    def test_specific_languages_present(self):
        """Test that specific languages are in the list"""
        response = client.get("/api/user/languages")
        data = response.json()
        
        languages = data['languages']
        codes = [lang['code'] for lang in languages]
        
        # Check for common languages
        assert 'ko' in codes  # Korean
        assert 'en' in codes  # English
        assert 'ja' in codes  # Japanese
        assert 'zh' in codes  # Chinese
        assert 'es' in codes  # Spanish
    
    def test_korean_language_details(self):
        """Test Korean language details"""
        response = client.get("/api/user/languages")
        data = response.json()
        
        languages = data['languages']
        korean = next((lang for lang in languages if lang['code'] == 'ko'), None)
        
        assert korean is not None
        assert korean['name'] == 'Korean'
        assert korean['native_name'] == '한국어'
        assert korean['flag'] == '🇰🇷'
    
    def test_english_language_details(self):
        """Test English language details"""
        response = client.get("/api/user/languages")
        data = response.json()
        
        languages = data['languages']
        english = next((lang for lang in languages if lang['code'] == 'en'), None)
        
        assert english is not None
        assert english['name'] == 'English'
        assert english['native_name'] == 'English'
        assert english['flag'] == '🇺🇸'
    
    def test_no_authentication_required(self):
        """Test that endpoint doesn't require authentication"""
        # This should succeed without Authorization header
        response = client.get("/api/user/languages")
        assert response.status_code == 200


class TestLanguageUtils:
    """Test language utility functions"""
    
    def test_get_language_name(self):
        """Test get_language_name utility"""
        from app.utils.language_utils import get_language_name
        
        assert get_language_name('ko') == 'Korean'
        assert get_language_name('en') == 'English'
        assert get_language_name('ja') == 'Japanese'
        
        # Test case insensitivity
        assert get_language_name('KO') == 'Korean'
        assert get_language_name('EN') == 'English'
    
    def test_get_language_name_fallback(self):
        """Test fallback for unknown language code"""
        from app.utils.language_utils import get_language_name
        
        assert get_language_name('xx') == 'English'
        assert get_language_name('invalid') == 'English'
    
    def test_is_valid_language_code(self):
        """Test language code validation"""
        from app.utils.language_utils import is_valid_language_code
        
        # Valid codes
        assert is_valid_language_code('ko') is True
        assert is_valid_language_code('en') is True
        assert is_valid_language_code('ja') is True
        
        # Case insensitive
        assert is_valid_language_code('KO') is True
        assert is_valid_language_code('EN') is True
        
        # Invalid codes
        assert is_valid_language_code('xx') is False
        assert is_valid_language_code('invalid') is False
    
    def test_valid_language_codes_list(self):
        """Test VALID_LANGUAGE_CODES constant"""
        from app.utils.language_utils import VALID_LANGUAGE_CODES
        
        assert isinstance(VALID_LANGUAGE_CODES, list)
        assert len(VALID_LANGUAGE_CODES) == 14
        assert 'ko' in VALID_LANGUAGE_CODES
        assert 'en' in VALID_LANGUAGE_CODES
    
    def test_supported_languages_structure(self):
        """Test SUPPORTED_LANGUAGES constant structure"""
        from app.utils.language_utils import SUPPORTED_LANGUAGES
        
        assert isinstance(SUPPORTED_LANGUAGES, list)
        assert len(SUPPORTED_LANGUAGES) == 14
        
        # Check structure
        for lang in SUPPORTED_LANGUAGES:
            assert 'code' in lang
            assert 'name' in lang
            assert 'native_name' in lang
            assert 'flag' in lang
            assert isinstance(lang['code'], str)
            assert len(lang['code']) == 2  # ISO 639-1 is 2 characters



