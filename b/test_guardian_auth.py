#!/usr/bin/env python3
"""
Unit tests for Guardian Authentication Service
Tests authentication flows with mock Guardian responses
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import requests

from guardian_auth import GuardianAuth, AuthToken, GuardianAuthError

class TestAuthToken:
    """Test AuthToken dataclass functionality"""
    
    def test_auth_token_creation(self):
        """Test creating an AuthToken"""
        expires_at = datetime.now() + timedelta(hours=1)
        token = AuthToken(
            token="test_token_123",
            expires_at=expires_at,
            refresh_token="refresh_123",
            user_id="user_456",
            username="testuser"
        )
        
        assert token.token == "test_token_123"
        assert token.expires_at == expires_at
        assert token.refresh_token == "refresh_123"
        assert token.user_id == "user_456"
        assert token.username == "testuser"
    
    def test_token_expiry_check(self):
        """Test token expiration checking"""
        # Non-expired token (1 hour from now)
        future_token = AuthToken(
            token="valid_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        assert not future_token.is_expired()
        
        # Expired token (1 hour ago)
        expired_token = AuthToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert expired_token.is_expired()
        
        # Token expiring soon (within 5 minute buffer)
        soon_expired_token = AuthToken(
            token="soon_expired",
            expires_at=datetime.now() + timedelta(minutes=3)
        )
        assert soon_expired_token.is_expired()  # Should be considered expired due to buffer
    
    def test_time_until_expiry(self):
        """Test calculating time until token expiry"""
        expires_at = datetime.now() + timedelta(hours=2)
        token = AuthToken(token="test", expires_at=expires_at)
        
        time_left = token.time_until_expiry()
        assert time_left.total_seconds() > 7000  # Should be close to 2 hours (7200 seconds)
        assert time_left.total_seconds() < 7300
    
    def test_token_serialization(self):
        """Test converting token to/from dictionary"""
        expires_at = datetime.now() + timedelta(hours=1)
        original_token = AuthToken(
            token="test_token",
            expires_at=expires_at,
            refresh_token="refresh_token",
            user_id="user_123",
            username="testuser"
        )
        
        # Convert to dict
        token_dict = original_token.to_dict()
        assert token_dict["token"] == "test_token"
        assert token_dict["expires_at"] == expires_at.isoformat()
        assert token_dict["refresh_token"] == "refresh_token"
        assert token_dict["user_id"] == "user_123"
        assert token_dict["username"] == "testuser"
        
        # Convert back from dict
        restored_token = AuthToken.from_dict(token_dict)
        assert restored_token.token == original_token.token
        assert restored_token.expires_at == original_token.expires_at
        assert restored_token.refresh_token == original_token.refresh_token
        assert restored_token.user_id == original_token.user_id
        assert restored_token.username == original_token.username

class TestGuardianAuth:
    """Test GuardianAuth class functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.auth = GuardianAuth(base_url="http://test-guardian:3000")
        self.mock_response_data = {
            "accessToken": "mock_access_token_123",
            "refreshToken": "mock_refresh_token_456",
            "expiresIn": 3600,  # 1 hour
            "id": "user_789",
            "username": "testuser"
        }
    
    @patch('requests.Session.post')
    def test_successful_login(self, mock_post):
        """Test successful Guardian login"""
        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_post.return_value = mock_response
        
        # Perform login
        token = self.auth.login("testuser", "testpass")
        
        # Verify request was made correctly
        mock_post.assert_called_once_with(
            "http://test-guardian:3000/accounts/login",
            json={"username": "testuser", "password": "testpass"},
            timeout=30
        )
        
        # Verify token was created correctly
        assert token.token == "mock_access_token_123"
        assert token.refresh_token == "mock_refresh_token_456"
        assert token.user_id == "user_789"
        assert token.username == "testuser"
        assert not token.is_expired()
        
        # Verify session headers were updated
        assert self.auth.session.headers["Authorization"] == "Bearer mock_access_token_123"
        
        # Verify current token was set
        assert self.auth.current_token == token
    
    @patch('requests.Session.post')
    def test_login_invalid_credentials(self, mock_post):
        """Test login with invalid credentials"""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_post.return_value = mock_response
        
        # Attempt login and expect exception
        with pytest.raises(GuardianAuthError, match="Invalid username or password"):
            self.auth.login("baduser", "badpass")
        
        # Verify no token was set
        assert self.auth.current_token is None
        assert "Authorization" not in self.auth.session.headers
    
    @patch('requests.Session.post')
    def test_login_forbidden_access(self, mock_post):
        """Test login with forbidden access"""
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Access forbidden"
        mock_post.return_value = mock_response
        
        # Attempt login and expect exception
        with pytest.raises(GuardianAuthError, match="Access forbidden"):
            self.auth.login("testuser", "testpass")
    
    @patch('requests.Session.post')
    def test_login_connection_error(self, mock_post):
        """Test login with connection error"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Attempt login and expect exception
        with pytest.raises(GuardianAuthError, match="Cannot connect to Guardian API"):
            self.auth.login("testuser", "testpass")
    
    @patch('requests.Session.post')
    def test_login_timeout(self, mock_post):
        """Test login with timeout"""
        # Mock timeout error
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Attempt login and expect exception
        with pytest.raises(GuardianAuthError, match="Guardian API request timeout"):
            self.auth.login("testuser", "testpass")
    
    @patch('requests.Session.post')
    def test_successful_logout(self, mock_post):
        """Test successful logout"""
        # Set up authenticated state
        self.auth.current_token = AuthToken(
            token="test_token",
            expires_at=datetime.now() + timedelta(hours=1),
            username="testuser"
        )
        self.auth.session.headers["Authorization"] = "Bearer test_token"
        
        # Mock successful logout response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Perform logout
        result = self.auth.logout()
        
        # Verify request was made
        mock_post.assert_called_once_with(
            "http://test-guardian:3000/accounts/logout",
            timeout=30
        )
        
        # Verify logout was successful
        assert result is True
        assert self.auth.current_token is None
        assert "Authorization" not in self.auth.session.headers
    
    def test_logout_no_active_session(self):
        """Test logout when no active session exists"""
        # Ensure no active session
        self.auth.current_token = None
        
        # Perform logout
        result = self.auth.logout()
        
        # Should succeed even with no active session
        assert result is True
    
    @patch('requests.Session.post')
    def test_successful_token_refresh(self, mock_post):
        """Test successful token refresh"""
        # Set up token that needs refresh
        self.auth.current_token = AuthToken(
            token="old_token",
            expires_at=datetime.now() - timedelta(minutes=1),  # Expired
            refresh_token="refresh_token_123",
            user_id="user_789",
            username="testuser"
        )
        
        # Mock successful refresh response
        refresh_response_data = {
            "accessToken": "new_access_token_456",
            "refreshToken": "new_refresh_token_789",
            "expiresIn": 3600
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = refresh_response_data
        mock_post.return_value = mock_response
        
        # Perform token refresh
        new_token = self.auth.refresh_token()
        
        # Verify request was made correctly
        mock_post.assert_called_once_with(
            "http://test-guardian:3000/accounts/refresh",
            json={"refreshToken": "refresh_token_123"},
            timeout=30
        )
        
        # Verify new token was created
        assert new_token is not None
        assert new_token.token == "new_access_token_456"
        assert new_token.refresh_token == "new_refresh_token_789"
        assert new_token.username == "testuser"  # Preserved from old token
        assert not new_token.is_expired()
        
        # Verify session headers were updated
        assert self.auth.session.headers["Authorization"] == "Bearer new_access_token_456"
    
    def test_refresh_token_no_refresh_token(self):
        """Test token refresh when no refresh token is available"""
        # Set up token without refresh token
        self.auth.current_token = AuthToken(
            token="old_token",
            expires_at=datetime.now() - timedelta(minutes=1)
        )
        
        # Attempt refresh
        result = self.auth.refresh_token()
        
        # Should return None
        assert result is None
    
    @patch('requests.Session.post')
    def test_refresh_token_failure(self, mock_post):
        """Test token refresh failure"""
        # Set up token with refresh token
        self.auth.current_token = AuthToken(
            token="old_token",
            expires_at=datetime.now() - timedelta(minutes=1),
            refresh_token="refresh_token_123"
        )
        
        # Mock failed refresh response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response
        
        # Attempt refresh
        result = self.auth.refresh_token()
        
        # Should return None
        assert result is None
    
    def test_is_token_valid_no_token(self):
        """Test token validation when no token exists"""
        self.auth.current_token = None
        assert not self.auth.is_token_valid()
    
    def test_is_token_valid_expired_token(self):
        """Test token validation with expired token"""
        self.auth.current_token = AuthToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert not self.auth.is_token_valid()
    
    def test_is_token_valid_active_token(self):
        """Test token validation with active token"""
        self.auth.current_token = AuthToken(
            token="active_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        assert self.auth.is_token_valid()
    
    @patch('requests.Session.post')
    def test_ensure_valid_token_with_valid_token(self, mock_post):
        """Test ensure_valid_token when token is already valid"""
        # Set up valid token
        self.auth.current_token = AuthToken(
            token="valid_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        # Should return True without making any requests
        result = self.auth.ensure_valid_token()
        assert result is True
        mock_post.assert_not_called()
    
    @patch('requests.Session.post')
    def test_ensure_valid_token_with_refresh(self, mock_post):
        """Test ensure_valid_token using token refresh"""
        # Set up expired token with refresh token
        self.auth.current_token = AuthToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(minutes=1),
            refresh_token="refresh_token_123",
            username="testuser"
        )
        
        # Mock successful refresh
        refresh_response = {
            "accessToken": "refreshed_token",
            "expiresIn": 3600
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = refresh_response
        mock_post.return_value = mock_response
        
        # Should refresh token and return True
        result = self.auth.ensure_valid_token()
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_ensure_valid_token_with_reauth(self, mock_post):
        """Test ensure_valid_token using re-authentication"""
        # Set up expired token without refresh token
        self.auth.current_token = AuthToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(minutes=1)
        )
        
        # Mock successful login
        login_response = self.mock_response_data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = login_response
        mock_post.return_value = mock_response
        
        # Should re-authenticate and return True
        result = self.auth.ensure_valid_token("testuser", "testpass")
        assert result is True
        mock_post.assert_called_once()
    
    def test_get_auth_headers_valid_token(self):
        """Test getting auth headers with valid token"""
        self.auth.current_token = AuthToken(
            token="valid_token_123",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        headers = self.auth.get_auth_headers()
        assert headers == {"Authorization": "Bearer valid_token_123"}
    
    def test_get_auth_headers_no_token(self):
        """Test getting auth headers with no token"""
        self.auth.current_token = None
        
        headers = self.auth.get_auth_headers()
        assert headers == {}
    
    def test_get_auth_headers_expired_token(self):
        """Test getting auth headers with expired token"""
        self.auth.current_token = AuthToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(hours=1)
        )
        
        headers = self.auth.get_auth_headers()
        assert headers == {}
    
    @patch('requests.Session.request')
    def test_make_authenticated_request_success(self, mock_request):
        """Test making authenticated request successfully"""
        # Set up valid token
        self.auth.current_token = AuthToken(
            token="valid_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Make request
        response = self.auth.make_authenticated_request('GET', '/api/test')
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            'GET', 
            'http://test-guardian:3000/api/test',
            timeout=30
        )
        assert response == mock_response
    
    def test_make_authenticated_request_no_token(self):
        """Test making authenticated request without valid token"""
        self.auth.current_token = None
        
        with pytest.raises(GuardianAuthError, match="No valid authentication token"):
            self.auth.make_authenticated_request('GET', '/api/test')
    
    @patch('requests.Session.request')
    @patch('requests.Session.post')
    def test_make_authenticated_request_with_refresh(self, mock_post, mock_request):
        """Test making authenticated request with automatic token refresh on 401"""
        # Set up token with refresh capability
        self.auth.current_token = AuthToken(
            token="old_token",
            expires_at=datetime.now() + timedelta(hours=1),
            refresh_token="refresh_token_123"
        )
        
        # Mock 401 response first, then success after refresh
        mock_401_response = Mock()
        mock_401_response.status_code = 401
        
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        
        mock_request.side_effect = [mock_401_response, mock_success_response]
        
        # Mock successful token refresh
        refresh_response = {
            "accessToken": "new_token",
            "expiresIn": 3600
        }
        mock_refresh_response = Mock()
        mock_refresh_response.status_code = 200
        mock_refresh_response.json.return_value = refresh_response
        mock_post.return_value = mock_refresh_response
        
        # Make request
        response = self.auth.make_authenticated_request('GET', '/api/test')
        
        # Verify refresh was called and request was retried
        mock_post.assert_called_once()
        assert mock_request.call_count == 2
        assert response == mock_success_response
    
    @patch('requests.Session.request')
    def test_get_user_info_success(self, mock_request):
        """Test getting user info successfully"""
        # Set up valid token
        self.auth.current_token = AuthToken(
            token="valid_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        # Mock successful response
        user_data = {"username": "testuser", "id": "user_123", "role": "USER"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_data
        mock_request.return_value = mock_response
        
        # Get user info
        result = self.auth.get_user_info()
        
        # Verify request and result
        mock_request.assert_called_once_with(
            'GET',
            'http://test-guardian:3000/accounts/session',
            timeout=30
        )
        assert result == user_data
    
    def test_get_user_info_no_token(self):
        """Test getting user info without valid token"""
        self.auth.current_token = None
        
        result = self.auth.get_user_info()
        assert result is None

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])