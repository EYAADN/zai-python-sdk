"""HTTP Client for Z.AI API."""

from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from .exceptions import ZAIError


class HTTPClient:
    """HTTP Client for Z.AI API requests."""
    
    def __init__(
        self,
        base_url: str,
        timeout: int,
        session: Optional[requests.Session] = None,
        verbose: bool = False
    ):
        """
        Initialize HTTP client.
        
        Args:
            base_url (str): Base URL for API requests.
            timeout (int): Request timeout in seconds.
            session (Optional[requests.Session]): Optional session to use.
            verbose (bool): Enable verbose output.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verbose = verbose
        self.session = session or self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a new session with default headers.
        
        Returns:
            requests.Session: Configured session object.
        """
        session = requests.Session()
        session.headers.update({
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "referer": "https://chat.z.ai/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        })
        return session
    
    def set_auth_header(self, token: str):
        """
        Set authorization header.
        
        Args:
            token (str): Bearer token for authentication.
        """
        self.session.headers["authorization"] = f"Bearer {token}"
    
    def update_headers(self, headers: Dict[str, str]):
        """
        Update session headers.
        
        Args:
            headers (Dict[str, str]): Headers to update.
        """
        self.session.headers.update(headers)
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        stream: bool = False
    ) -> requests.Response:
        """
        Make HTTP request to API.
        
        Args:
            method (str): HTTP method.
            endpoint (str): API endpoint.
            data (Optional[Dict]): Request payload.
            stream (bool): Whether to stream response.
        
        Returns:
            requests.Response: Response object.
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if stream:
                timeout = (30, 60)
            else:
                timeout = self.timeout
            
            if stream:
                headers = dict(self.session.headers)
                headers.pop('accept-encoding', None)
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    timeout=timeout,
                    stream=stream,
                    headers=headers
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    timeout=timeout,
                    stream=stream
                )
            
            if self.verbose:
                print(f"[DEBUG] Request to {url}")
                print(f"[DEBUG] Status: {response.status_code}")
                if not stream:
                    print(f"[DEBUG] Response text: {response.text[:500]}")
            
            response.raise_for_status()
            
            if response.cookies:
                self.session.cookies.update(response.cookies)
            
            return response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                    error_msg += f" - Response: {error_detail}"
                except:
                    pass
            raise ZAIError(error_msg)