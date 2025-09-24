#!/usr/bin/env python3
"""
Simple test runner for Guardian Authentication Service
Runs tests without requiring pytest installation
"""

import sys
import traceback
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import requests

# Import our modules
from guardian_auth import GuardianAuth, AuthToken, GuardianAuthError

def test_auth_token_creation():
    """Test creating an AuthToken"""
    print("Testing AuthToken creation...")
    
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
    print("✅ AuthToken creation test passed")

def test_token_expiry_check():
    """Test token expiration checking"""
    print("Testing token expiry check...")
    
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
    print("✅ Token expiry check test passed")

def test_token_serialization():
    """Test converting token to/from dictionary"""
    print("Testing token serialization...")
    
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
    print("✅ Token serialization test passed")

def test_guardian_auth_initialization():
    """Test GuardianAuth initialization"""
    print("Testing GuardianAuth initialization...")
    
    auth = GuardianAuth(base_url="http://test-guardian:3000")
    assert auth.base_url == "http://test-guardian:3000"
    assert auth.timeout == 30
    assert auth.current_token is None
    assert "Content-Type" in auth.session.headers
    assert auth.session.headers["Content-Type"] == "application/json"
    print("✅ GuardianAuth initialization test passed")

def test_successful_login():
    """Test successful Guardian login with mocked response"""
    print("Testing successful login...")
    
    auth = GuardianAuth(base_url="http://test-guardian:3000")
    
    # Mock response data
    mock_response_data = {
        "accessToken": "mock_access_token_123",
        "refreshToken": "mock_refresh_token_456",
        "expiresIn": 3600,  # 1 hour
        "id": "user_789",
        "username": "testuser"
    }
    
    # Mock the session.post method
    with patch.object(auth.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response
        
        # Perform login
        token = auth.login("testuser", "testpass")
        
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
        assert auth.session.headers["Authorization"] == "Bearer mock_access_token_123"
        
        # Verify current token was set
        assert auth.current_token == token
    
    print("✅ Successful login test passed")

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    print("Testing login with invalid credentials...")
    
    auth = GuardianAuth(base_url="http://test-guardian:3000")
    
    # Mock 401 response
    with patch.object(auth.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_post.return_value = mock_response
        
        # Attempt login and expect exception
        try:
            auth.login("baduser", "badpass")
            assert False, "Expected GuardianAuthError"
        except GuardianAuthError as e:
            assert "Invalid username or password" in str(e)
        
        # Verify no token was set
        assert auth.current_token is None
        assert "Authorization" not in auth.session.headers
    
    print("✅ Invalid credentials test passed")

def test_successful_logout():
    """Test successful logout"""
    print("Testing successful logout...")
    
    auth = GuardianAuth(base_url="http://test-guardian:3000")
    
    # Set up authenticated state
    auth.current_token = AuthToken(
        token="test_token",
        expires_at=datetime.now() + timedelta(hours=1),
        username="testuser"
    )
    auth.session.headers["Authorization"] = "Bearer test_token"
    
    # Mock successful logout response
    with patch.object(auth.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Perform logout
        result = auth.logout()
        
        # Verify request was made
        mock_post.assert_called_once_with(
            "http://test-guardian:3000/accounts/logout",
            timeout=30
        )
        
        # Verify logout was successful
        assert result is True
        assert auth.current_token is None
        assert "Authorization" not in auth.session.headers
    
    print("✅ Successful logout test passed")

def test_token_validation():
    """Test token validation methods"""
    print("Testing token validation...")
    
    auth = GuardianAuth()
    
    # Test with no token
    assert not auth.is_token_valid()
    
    # Test with expired token
    auth.current_token = AuthToken(
        token="expired_token",
        expires_at=datetime.now() - timedelta(hours=1)
    )
    assert not auth.is_token_valid()
    
    # Test with valid token
    auth.current_token = AuthToken(
        token="valid_token",
        expires_at=datetime.now() + timedelta(hours=1)
    )
    assert auth.is_token_valid()
    
    print("✅ Token validation test passed")

def test_auth_headers():
    """Test getting authentication headers"""
    print("Testing auth headers...")
    
    auth = GuardianAuth()
    
    # Test with no token
    headers = auth.get_auth_headers()
    assert headers == {}
    
    # Test with valid token
    auth.current_token = AuthToken(
        token="valid_token_123",
        expires_at=datetime.now() + timedelta(hours=1)
    )
    headers = auth.get_auth_headers()
    assert headers == {"Authorization": "Bearer valid_token_123"}
    
    # Test with expired token
    auth.current_token = AuthToken(
        token="expired_token",
        expires_at=datetime.now() - timedelta(hours=1)
    )
    headers = auth.get_auth_headers()
    assert headers == {}
    
    print("✅ Auth headers test passed")

def run_all_tests():
    """Run all tests"""
    tests = [
        test_auth_token_creation,
        test_token_expiry_check,
        test_token_serialization,
        test_guardian_auth_initialization,
        test_successful_login,
        test_login_invalid_credentials,
        test_successful_logout,
        test_token_validation,
        test_auth_headers
    ]
    
    passed = 0
    failed = 0
    
    print("🧪 Running Guardian Authentication Service Tests")
    print("=" * 50)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            traceback.print_exc()
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)