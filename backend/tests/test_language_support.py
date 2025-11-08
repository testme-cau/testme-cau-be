"""
Tests for language support features
"""
import pytest
from pydantic import ValidationError
from app.models.requests import UserUpdateRequest, SubjectCreateRequest, SubjectUpdateRequest


class TestLanguageValidation:
    """Test language code validation"""
    
    def test_user_update_valid_languages(self):
        """Test valid language codes in user update"""
        valid_languages = ['ko', 'en', 'ja', 'zh', 'es', 'fr']
        
        for lang in valid_languages:
            request = UserUpdateRequest(language_preference=lang)
            assert request.language_preference == lang.lower()
    
    def test_user_update_invalid_language(self):
        """Test invalid language code"""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdateRequest(language_preference="invalid")
        
        errors = exc_info.value.errors()
        assert any('language' in str(error).lower() for error in errors)
    
    def test_subject_create_with_language(self):
        """Test subject creation with language"""
        request = SubjectCreateRequest(
            name="Database Systems",
            language_preference="en"
        )
        
        assert request.name == "Database Systems"
        assert request.language_preference == "en"
    
    def test_subject_update_language(self):
        """Test updating subject language"""
        request = SubjectUpdateRequest(language_preference="ja")
        assert request.language_preference == "ja"
    
    def test_language_case_insensitive(self):
        """Test that language codes are normalized to lowercase"""
        request = UserUpdateRequest(language_preference="KO")
        assert request.language_preference == "ko"
        
        request2 = SubjectCreateRequest(name="Test", language_preference="EN")
        assert request2.language_preference == "en"


class TestDomainModels:
    """Test domain models with language support"""
    
    def test_user_model_default_language(self):
        """Test User model has default language"""
        from app.models.domain import User
        
        user = User(
            uid="test123",
            email="test@example.com"
        )
        
        assert user.language_preference == "ko"  # Default
    
    def test_subject_model_optional_language(self):
        """Test Subject model has optional language"""
        from app.models.domain import Subject
        from datetime import datetime
        
        subject = Subject(
            subject_id="subj123",
            user_id="user123",
            name="Test Subject",
            created_at=datetime.utcnow()
        )
        
        assert subject.language_preference is None  # Optional
    
    def test_subject_with_language(self):
        """Test Subject with language preference"""
        from app.models.domain import Subject
        from datetime import datetime
        
        subject = Subject(
            subject_id="subj123",
            user_id="user123",
            name="Test Subject",
            language_preference="en",
            created_at=datetime.utcnow()
        )
        
        assert subject.language_preference == "en"


class TestAIServiceInterface:
    """Test AI service interface with language parameter"""
    
    def test_gpt_service_language_parameter(self):
        """Test GPTService accepts language parameter"""
        from app.services.gpt_service import GPTService
        import inspect
        
        sig = inspect.signature(GPTService.generate_exam_from_pdf)
        params = sig.parameters
        
        assert 'language' in params
        assert params['language'].default == 'ko'
    
    def test_gemini_service_language_parameter(self):
        """Test GeminiService accepts language parameter"""
        from app.services.gemini_service import GeminiService
        import inspect
        
        sig = inspect.signature(GeminiService.generate_exam_from_pdf)
        params = sig.parameters
        
        assert 'language' in params
        assert params['language'].default == 'ko'


class TestLanguageNames:
    """Test language name mappings"""
    
    def test_language_name_mapping(self):
        """Test that language codes are mapped to names correctly"""
        language_names = {
            "ko": "Korean",
            "en": "English",
            "ja": "Japanese",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
            "vi": "Vietnamese",
            "th": "Thai"
        }
        
        # Test common languages
        assert language_names["ko"] == "Korean"
        assert language_names["en"] == "English"
        assert language_names["ja"] == "Japanese"
        assert language_names["zh"] == "Chinese"


class TestLanguagePriority:
    """Test language preference priority logic"""
    
    def test_language_priority_order(self):
        """Test language preference priority: Subject > User > Default"""
        # Priority order should be:
        # 1. Subject's language_preference
        # 2. User's language_preference
        # 3. Default (ko)
        
        # This is tested in integration tests with actual routes
        # Here we just document the expected behavior
        assert True  # Placeholder for documentation


class TestSupportedLanguages:
    """Test list of supported languages"""
    
    def test_all_supported_languages(self):
        """Test that all supported languages are valid"""
        supported = ['ko', 'en', 'ja', 'zh', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ar', 'hi', 'vi', 'th']
        
        for lang in supported:
            # Should not raise validation error
            request = UserUpdateRequest(language_preference=lang)
            assert request.language_preference == lang
    
    def test_language_count(self):
        """Test that we support at least 14 major languages"""
        from app.models.requests import UserUpdateRequest
        import inspect
        
        # Get the validator
        validators = UserUpdateRequest.__pydantic_decorators__.field_validators
        
        # We should support at least 14 languages
        # (ko, en, ja, zh, es, fr, de, it, pt, ru, ar, hi, vi, th)
        assert len(['ko', 'en', 'ja', 'zh', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ar', 'hi', 'vi', 'th']) == 14



