"""
Tests for authentication system
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.models.admin import ServiceStatus


def test_health_without_auth(client: TestClient):
    """Test that health endpoint doesn't require auth"""
    response = client.get("/health")
    assert response.status_code == 200


def test_api_health_without_auth(client: TestClient):
    """Test that API health endpoint doesn't require auth"""
    response = client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token():
    """Test get_current_user with valid Firebase token"""
    from app.dependencies.auth import get_current_user
    from unittest.mock import AsyncMock, MagicMock
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid_token_123"
    mock_request.session = {}
    
    # Mock Firebase auth.verify_id_token
    with patch('app.dependencies.auth.auth') as mock_auth, \
         patch('app.dependencies.auth.config_service.get_config') as mock_config:
        mock_auth.verify_id_token.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com'
        }
        mock_config.return_value = SimpleNamespace(
            status=ServiceStatus.open_beta,
            allowed_emails=[]
        )
        
        user = await get_current_user(mock_request)
        
        assert user['uid'] == 'test_user_123'
        assert user['email'] == 'test@example.com'
        mock_auth.verify_id_token.assert_called_once_with('valid_token_123')


@pytest.mark.asyncio
async def test_get_current_user_without_token():
    """Test get_current_user without token raises HTTPException"""
    from app.dependencies.auth import get_current_user
    from unittest.mock import MagicMock
    
    # Mock request without Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = None
    mock_request.session = {}
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)
    
    assert exc_info.value.status_code == 401
    assert "No token provided" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    """Test get_current_user with invalid token raises HTTPException"""
    from app.dependencies.auth import get_current_user
    from unittest.mock import MagicMock
    
    # Mock request with invalid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer invalid_token"
    mock_request.session = {}
    
    # Mock Firebase auth.verify_id_token to raise exception
    with patch('app.dependencies.auth.auth') as mock_auth, \
         patch('app.dependencies.auth.config_service.get_config') as mock_config:
        mock_auth.verify_id_token.side_effect = Exception("Invalid token")
        mock_config.return_value = SimpleNamespace(
            status=ServiceStatus.open_beta,
            allowed_emails=[]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_with_session():
    """Test get_current_user with session-based auth (admin)"""
    from app.dependencies.auth import get_current_user
    from unittest.mock import MagicMock
    
    # Mock request with session auth
    mock_request = MagicMock()
    mock_request.headers.get.return_value = None
    mock_request.session = {
        'firebase_authenticated': True,
        'firebase_token': 'session_token_123'
    }
    
    # Mock Firebase auth.verify_id_token
    with patch('app.dependencies.auth.auth') as mock_auth, \
         patch('app.dependencies.auth.config_service.get_config') as mock_config:
        mock_auth.verify_id_token.return_value = {
            'uid': 'admin_user_123',
            'email': 'admin@example.com'
        }
        mock_config.return_value = SimpleNamespace(
            status=ServiceStatus.open_beta,
            allowed_emails=[]
        )
        
        user = await get_current_user(mock_request)
@pytest.mark.asyncio
async def test_get_current_user_denied_during_closed_beta():
    """Non-allowlisted users are blocked during closed beta."""
    from app.dependencies.auth import get_current_user
    from unittest.mock import MagicMock

    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer closed_beta_token"
    mock_request.session = {}

    with patch('app.dependencies.auth.auth') as mock_auth, \
         patch('app.dependencies.auth.config_service.get_config') as mock_config:
        mock_auth.verify_id_token.return_value = {
            'uid': 'test_user_456',
            'email': 'notallowed@example.com'
        }
        mock_config.return_value = SimpleNamespace(
            status=ServiceStatus.closed_beta,
            allowed_emails=['allowed@example.com']
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_request)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == 'closed_beta_not_allowed'

