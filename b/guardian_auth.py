#!/usr/bin/env python3
"""
Guardian Authentication Service
Handles authentication, token management, and session handling for Guardian API
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import requests
import json

from guardian_error_handler import (
    GuardianErrorHandler, 
    ErrorContext, 
    RetryStrategy,
    get_guardian_error_handler
)

logger = logging.getLogger('guardian.auth')

@dataclass
class AuthToken:
    """Guardian authentication token with metadata"""
    token: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)"""
        buffer_time = datetime.now() + timedelta(minutes=5)
        return self.expires_at <= buffer_time
    
    def time_until_expiry(self) -> timedelta:
        """Get time remaining until token expires"""
        return self.expires_at - datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "username": self.username
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthToken':
        """Create from dictionary"""
        return cls(
            token=data["token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            refresh_token=data.get("refresh_token"),
            user_id=data.get("user_id"),
            username=data.get("username")
        )

class GuardianAuthError(Exception):
    """Guardian authentication specific errors"""
    pass

class GuardianAuth:
    """Guardian authentication service with token management"""
    
    def __init__(self, base_url: str = "http://localhost:3000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.current_token: Optional[AuthToken] = None
        self.session = requests.Session()
        
        # Initialize error handler
        self.error_handler = get_guardian_error_handler()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @get_guardian_error_handler().with_error_handling("guardian_login")
    def login(self, username: str, password: str) -> AuthToken:
        """
        Authenticate with Guardian using username/password
        Returns AuthToken with bearer token and expiration info
        """
        login_data = {
            "username": username,
            "password": password
        }
        
        logger.info(f"🔐 Attempting Guardian login for user: {username}", 
                   extra={'guardian_operation': 'login', 'username': username})
        
        response = self.session.post(
            f"{self.base_url}/api/v1/accounts/login",
            json=login_data,
            timeout=self.timeout
        )
            
        if response.status_code == 200:
            auth_data = response.json()
            
            # Extract token information from Guardian response
            # Guardian returns refreshToken as the main authentication token
            refresh_token = auth_data.get("refreshToken")
            if not refresh_token:
                raise GuardianAuthError("No refresh token in Guardian response")
            
            # Calculate expiration time (Guardian tokens typically expire in 24 hours)
            # We'll decode the JWT to get the actual expiration time
            expires_at = datetime.now() + timedelta(hours=24)  # Default 24 hours
            
            # Try to decode JWT to get actual expiration
            try:
                import base64
                import json
                # Decode JWT payload (second part after first dot)
                parts = refresh_token.split('.')
                if len(parts) >= 2:
                    # Add padding if needed
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.b64decode(payload)
                    jwt_data = json.loads(decoded)
                    
                    # Get expiration from JWT if available
                    if 'expireAt' in jwt_data:
                        expires_at = datetime.fromtimestamp(jwt_data['expireAt'] / 1000)
                    elif 'exp' in jwt_data:
                        expires_at = datetime.fromtimestamp(jwt_data['exp'])
            except:
                # If JWT decoding fails, use default expiration
                pass
            
            # Create auth token
            self.current_token = AuthToken(
                token=refresh_token,  # Use refreshToken as the main token
                expires_at=expires_at,
                refresh_token=refresh_token,  # Same token for refresh
                user_id=auth_data.get("id"),
                username=username
            )
            
            # Update session headers with bearer token
            self.session.headers.update({
                'Authorization': f'Bearer {refresh_token}'
            })
            
            logger.info(f"✅ Guardian login successful for {username}",
                       extra={'guardian_operation': 'login', 'username': username, 'token_expires': expires_at.isoformat()})
            
            return self.current_token
            
        elif response.status_code == 401:
            error_msg = f"Invalid credentials for {username}"
            logger.error(f"❌ Guardian login failed: {error_msg}",
                        extra={'guardian_operation': 'login', 'username': username, 'status_code': 401})
            raise GuardianAuthError("Invalid username or password")
        elif response.status_code == 403:
            error_msg = f"Access forbidden for {username}"
            logger.error(f"❌ Guardian login failed: {error_msg}",
                        extra={'guardian_operation': 'login', 'username': username, 'status_code': 403})
            raise GuardianAuthError("Access forbidden - user may not have required permissions")
        else:
            error_msg = f"HTTP {response.status_code} - {response.text}"
            logger.error(f"❌ Guardian login failed: {error_msg}",
                        extra={'guardian_operation': 'login', 'username': username, 'status_code': response.status_code})
            raise GuardianAuthError(f"Login failed with status {response.status_code}: {response.text}")
    
    def logout(self) -> bool:
        """
        Logout from Guardian and invalidate current token
        Returns True if successful, False otherwise
        """
        try:
            if not self.current_token:
                logger.warning("⚠️ No active Guardian session to logout")
                return True
            
            logger.info(f"🔓 Logging out Guardian user: {self.current_token.username}")
            
            # Call Guardian logout endpoint
            response = self.session.post(
                f"{self.base_url}/api/v1/accounts/logout",
                timeout=self.timeout
            )
            
            # Clear current token and session headers regardless of response
            self.current_token = None
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            if response.status_code in [200, 204]:
                logger.info("✅ Guardian logout successful")
                return True
            else:
                logger.warning(f"⚠️ Guardian logout returned status {response.status_code}, but token cleared locally")
                return True  # Still return True since we cleared the local token
                
        except Exception as e:
            logger.error(f"❌ Error during Guardian logout: {e}")
            # Clear token anyway for security
            self.current_token = None
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            return False
    
    def refresh_token(self) -> Optional[AuthToken]:
        """
        Refresh the current authentication token
        Returns new AuthToken if successful, None otherwise
        """
        try:
            if not self.current_token or not self.current_token.refresh_token:
                logger.warning("⚠️ No refresh token available")
                return None
            
            logger.info("🔄 Refreshing Guardian authentication token")
            
            refresh_data = {
                "refreshToken": self.current_token.refresh_token
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/accounts/refresh",
                json=refresh_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                
                access_token = auth_data.get("accessToken")
                if not access_token:
                    logger.error("❌ No access token in refresh response")
                    return None
                
                # Calculate new expiration time
                expires_in_seconds = auth_data.get("expiresIn", 86400)
                expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
                
                # Update current token
                self.current_token = AuthToken(
                    token=access_token,
                    expires_at=expires_at,
                    refresh_token=auth_data.get("refreshToken", self.current_token.refresh_token),
                    user_id=self.current_token.user_id,
                    username=self.current_token.username
                )
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
                
                logger.info("✅ Guardian token refresh successful")
                logger.info(f"🕒 New token expires at: {expires_at.isoformat()}")
                
                return self.current_token
            else:
                logger.error(f"❌ Token refresh failed: HTTP {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during token refresh: {e}")
            return None
    
    def is_token_valid(self) -> bool:
        """
        Check if current token is valid and not expired
        Returns True if token is valid, False otherwise
        """
        if not self.current_token:
            return False
        
        return not self.current_token.is_expired()
    
    def ensure_valid_token(self, username: str = None, password: str = None) -> bool:
        """
        Ensure we have a valid token, refreshing or re-authenticating if needed
        Returns True if valid token is available, False otherwise
        """
        try:
            # Check if current token is valid
            if self.is_token_valid():
                return True
            
            # Try to refresh token if available
            if self.current_token and self.current_token.refresh_token:
                logger.info("🔄 Token expired, attempting refresh...")
                refreshed_token = self.refresh_token()
                if refreshed_token:
                    return True
            
            # If refresh failed or no refresh token, try to re-authenticate
            if username and password:
                logger.info("🔐 Token refresh failed, attempting re-authentication...")
                self.login(username, password)
                return self.is_token_valid()
            
            logger.warning("⚠️ No valid token and no credentials provided for re-authentication")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error ensuring valid token: {e}")
            return False
    
    def get_current_token(self) -> Optional[AuthToken]:
        """Get the current authentication token"""
        return self.current_token
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with current authentication token"""
        if self.current_token and not self.current_token.is_expired():
            return {'Authorization': f'Bearer {self.current_token.token}'}
        return {}
    
    def make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to Guardian API
        Automatically handles token refresh if needed
        """
        # Ensure we have a valid token
        if not self.is_token_valid():
            raise GuardianAuthError("No valid authentication token available")
        
        # Make the request
        url = f"{self.base_url}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            # If we get 401, try to refresh token and retry once
            if response.status_code == 401 and self.current_token and self.current_token.refresh_token:
                logger.info("🔄 Got 401, attempting token refresh...")
                if self.refresh_token():
                    # Retry the request with new token
                    response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error making authenticated request to {endpoint}: {e}")
            raise
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information from Guardian"""
        try:
            if not self.is_token_valid():
                return None
            
            response = self.make_authenticated_request('GET', '/api/v1/accounts/session')
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get user info: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user info: {e}")
            return None

# Example usage and testing
if __name__ == "__main__":
    # Test Guardian authentication
    auth = GuardianAuth()
    
    # Test with environment variables
    username = os.getenv("GUARDIAN_USERNAME")
    password = os.getenv("GUARDIAN_PASSWORD")
    
    if username and password:
        try:
            print("🔍 Testing Guardian authentication...")
            
            # Test login
            token = auth.login(username, password)
            print(f"✅ Login successful: {token.username}")
            print(f"🕒 Token expires: {token.expires_at}")
            
            # Test token validation
            print(f"🔍 Token valid: {auth.is_token_valid()}")
            
            # Test user info
            user_info = auth.get_user_info()
            if user_info:
                print(f"👤 User info: {user_info.get('username', 'unknown')}")
            
            # Test logout
            logout_success = auth.logout()
            print(f"🔓 Logout successful: {logout_success}")
            
        except GuardianAuthError as e:
            print(f"❌ Authentication error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    else:
        print("⚠️ Set GUARDIAN_USERNAME and GUARDIAN_PASSWORD environment variables to test")