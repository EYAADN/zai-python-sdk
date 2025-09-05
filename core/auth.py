"""Authentication manager for Z.AI API."""

from typing import Dict, Optional

from .exceptions import ZAIError
from .http_client import HTTPClient


class AuthManager:
    """Manages authentication for Z.AI API."""
    
    def __init__(self, http_client: HTTPClient):
        """
        Initialize auth manager.
        
        Args:
            http_client (HTTPClient): HTTP client instance.
        """
        self.http_client = http_client
        self.token: Optional[str] = None
        self.auth_data: Optional[Dict] = None
    
    def get_guest_token(self) -> str:
        """
        Get a guest token from Z.AI auth endpoint.
        
        Returns:
            str: Guest token string.
        """
        try:
            response = self.http_client.make_request(
                "GET",
                "/api/v1/auths/"
            )
            auth_data = response.json()
            token = auth_data.get("token")
            
            if not token:
                raise ZAIError("No token found in auth response")
            
            self.auth_data = auth_data
            self.token = token
            
            return token
            
        except Exception as e:
            raise ZAIError(f"Failed to get guest token: {e}")
    
    def set_token(self, token: str):
        """
        Set authentication token.
        
        Args:
            token (str): Bearer token for authentication.
        """
        self.token = token
        self.http_client.set_auth_header(token)
    
    def get_auth_data(self) -> Optional[Dict]:
        """
        Get stored authentication data.
        
        Returns:
            Optional[Dict]: Authentication data if available.
        """
        return self.auth_data