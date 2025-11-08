"""
Language support utilities
"""
from typing import List, Dict

# Supported languages with metadata
SUPPORTED_LANGUAGES = [
    {
        "code": "ko",
        "name": "Korean",
        "native_name": "한국어",
        "flag": "🇰🇷"
    },
    {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "flag": "🇺🇸"
    },
    {
        "code": "ja",
        "name": "Japanese",
        "native_name": "日本語",
        "flag": "🇯🇵"
    },
    {
        "code": "zh",
        "name": "Chinese",
        "native_name": "中文",
        "flag": "🇨🇳"
    },
    {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "flag": "🇪🇸"
    },
    {
        "code": "fr",
        "name": "French",
        "native_name": "Français",
        "flag": "🇫🇷"
    },
    {
        "code": "de",
        "name": "German",
        "native_name": "Deutsch",
        "flag": "🇩🇪"
    },
    {
        "code": "it",
        "name": "Italian",
        "native_name": "Italiano",
        "flag": "🇮🇹"
    },
    {
        "code": "pt",
        "name": "Portuguese",
        "native_name": "Português",
        "flag": "🇵🇹"
    },
    {
        "code": "ru",
        "name": "Russian",
        "native_name": "Русский",
        "flag": "🇷🇺"
    },
    {
        "code": "ar",
        "name": "Arabic",
        "native_name": "العربية",
        "flag": "🇸🇦"
    },
    {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "flag": "🇮🇳"
    },
    {
        "code": "vi",
        "name": "Vietnamese",
        "native_name": "Tiếng Việt",
        "flag": "🇻🇳"
    },
    {
        "code": "th",
        "name": "Thai",
        "native_name": "ไทย",
        "flag": "🇹🇭"
    }
]

# Language code to name mapping (for internal use)
LANGUAGE_NAMES = {
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

# Valid language codes
VALID_LANGUAGE_CODES = list(LANGUAGE_NAMES.keys())


def get_supported_languages() -> List[Dict[str, str]]:
    """
    Get list of all supported languages
    
    Returns:
        List of language dictionaries with code, name, native_name, and flag
    """
    return SUPPORTED_LANGUAGES


def get_language_name(code: str) -> str:
    """
    Get English name for language code
    
    Args:
        code: ISO 639-1 language code
    
    Returns:
        English name of the language, or "English" if code not found
    """
    return LANGUAGE_NAMES.get(code.lower(), "English")


def is_valid_language_code(code: str) -> bool:
    """
    Check if language code is supported
    
    Args:
        code: ISO 639-1 language code
    
    Returns:
        True if code is supported, False otherwise
    """
    return code.lower() in VALID_LANGUAGE_CODES



