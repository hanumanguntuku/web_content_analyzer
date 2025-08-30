"""
Unified API Client for Web Content Analyzer
Combines robust error handling, progress tracking, and flexible analysis options.
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, Callable
import time
import json
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class UnifiedAPIClient:
    """
    Unified API client for communication with the backend analysis service
    Features:
    - Robust error handling
    - Progress tracking
    - Retry logic
    - Timeout management
    - Session management
    - Health/status/stats endpoints
    """
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WebContentAnalyzer-Frontend/1.0.0'
        })
        self.endpoints = {
            'analyze': '/api/v1/analyze',
            'status': '/api/v1/status',
            'health': '/api/v1/health',
            'stats': '/api/v1/stats',
            'supported_sites': '/api/v1/supported-sites'
        }

    def _get_full_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                return {
                    "error": True,
                    "error_type": "VALIDATION_ERROR",
                    "message": "Invalid request parameters",
                    "technical_details": error_data.get("detail", "Bad request"),
                    "status_code": 400
                }
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                return {
                    "error": True,
                    "error_type": "SECURITY_ERROR",
                    "message": "Request blocked for security reasons",
                    "technical_details": error_data.get("detail", "Forbidden"),
                    "status_code": 403
                }
            elif response.status_code == 429:
                error_data = response.json() if response.content else {}
                return {
                    "error": True,
                    "error_type": "RATE_LIMIT_ERROR",
                    "message": "Too many requests. Please wait before trying again.",
                    "technical_details": error_data.get("detail", "Rate limit exceeded"),
                    "status_code": 429
                }
            elif response.status_code >= 500:
                error_data = response.json() if response.content else {}
                return {
                    "error": True,
                    "error_type": "SERVER_ERROR",
                    "message": "Server error occurred. Please try again later.",
                    "technical_details": error_data.get("detail", f"HTTP {response.status_code}"),
                    "status_code": response.status_code
                }
            else:
                return {
                    "error": True,
                    "error_type": "HTTP_ERROR",
                    "message": f"Unexpected error (HTTP {response.status_code})",
                    "technical_details": response.text,
                    "status_code": response.status_code
                }
        except json.JSONDecodeError:
            return {
                "error": True,
                "error_type": "RESPONSE_ERROR",
                "message": "Invalid response from server",
                "technical_details": "Could not parse JSON response",
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "error": True,
                "error_type": "CLIENT_ERROR",
                "message": "Error processing server response",
                "technical_details": str(e),
                "status_code": getattr(response, 'status_code', 0)
            }

    def check_backend_status(self) -> Dict[str, Any]:
        try:
            url = self._get_full_url(self.endpoints['status'])
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return {"available": True, "status": "healthy", "data": response.json()}
            else:
                return {"available": False, "status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"available": False, "status": "unreachable", "error": "Could not connect to backend server"}
        except requests.exceptions.Timeout:
            return {"available": False, "status": "timeout", "error": "Backend server did not respond in time"}
        except Exception as e:
            return {"available": False, "status": "error", "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        url = self._get_full_url(self.endpoints['health'])
        response = self.session.get(url, timeout=10)
        return self._handle_response(response)

    def get_status(self) -> Dict[str, Any]:
        url = self._get_full_url(self.endpoints['status'])
        response = self.session.get(url, timeout=10)
        return self._handle_response(response)

    def get_supported_sites(self) -> Dict[str, Any]:
        url = self._get_full_url(self.endpoints['supported_sites'])
        response = self.session.get(url, timeout=10)
        return self._handle_response(response)

    def get_service_health(self) -> Dict[str, Any]:
        url = self._get_full_url(self.endpoints['health'])
        response = self.session.get(url, timeout=10)
        return self._handle_response(response)

    def get_service_stats(self) -> Dict[str, Any]:
        url = self._get_full_url(self.endpoints['stats'])
        response = self.session.get(url, timeout=10)
        return self._handle_response(response)

    def analyze_url(
        self,
        url: str,
        deep_analysis: bool = True,
        extract_images: bool = True,
        extract_links: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        request_data = {
            "url": url,
            "deep_analysis": deep_analysis,
            "extract_images": extract_images,
            "extract_links": extract_links
        }
        if progress_callback:
            progress_callback("initializing", 5, "Preparing analysis request...")
        try:
            backend_status = self.check_backend_status()
            if not backend_status["available"]:
                return {
                    "error": True,
                    "error_type": "CONNECTION_ERROR",
                    "message": "Backend server is not available",
                    "technical_details": backend_status.get("error", "Unknown connection error")
                }
            if progress_callback:
                progress_callback("security_validation", 15, "Connecting to analysis service...")
            for attempt in range(self.max_retries):
                try:
                    if progress_callback:
                        progress_callback("web_scraping", 20 + (attempt * 5), f"Sending request (attempt {attempt + 1})...")
                    url_endpoint = self._get_full_url(self.endpoints['analyze'])
                    response = self.session.post(
                        url_endpoint,
                        json=request_data,
                        timeout=self.timeout,
                        headers={
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }
                    )
                    if progress_callback:
                        progress_callback("content_extraction", 40, "Processing server response...")
                    result = self._handle_response(response)
                    if not result.get("error"):
                        if progress_callback:
                            progress_callback("completed", 100, "Analysis completed successfully!")
                        return result
                    if attempt < self.max_retries - 1:
                        if result.get("status_code") in [500, 502, 503, 504]:
                            time.sleep(2 ** attempt)
                            continue
                    return result
                except requests.exceptions.Timeout:
                    if attempt < self.max_retries - 1:
                        if progress_callback:
                            progress_callback("web_scraping", 25 + (attempt * 5), f"Request timed out, retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    return {
                        "error": True,
                        "error_type": "TIMEOUT_ERROR",
                        "message": "The analysis request timed out",
                        "technical_details": f"Request exceeded {self.timeout} seconds timeout"
                    }
                except requests.exceptions.ConnectionError:
                    if attempt < self.max_retries - 1:
                        if progress_callback:
                            progress_callback("web_scraping", 25 + (attempt * 5), f"Connection failed, retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    return {
                        "error": True,
                        "error_type": "CONNECTION_ERROR",
                        "message": "Could not connect to the analysis service",
                        "technical_details": "Connection refused or network error"
                    }
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            return {
                "error": True,
                "error_type": "CLIENT_ERROR",
                "message": "An unexpected error occurred",
                "technical_details": str(e)
            }
        return {
            "error": True,
            "error_type": "UNKNOWN_ERROR",
            "message": "Analysis failed for unknown reasons",
            "technical_details": "No specific error information available"
        }

# Global API client instance
_api_client = None

def get_api_client() -> UnifiedAPIClient:
    global _api_client
    if _api_client is None:
        backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")
        _api_client = UnifiedAPIClient(base_url=backend_url)
    return _api_client

def test_backend_connection() -> Dict[str, Any]:
    client = get_api_client()
    return client.check_backend_status()

def analyze_website(
    url: str,
    analysis_config: Dict[str, Any],
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    client = get_api_client()
    return client.analyze_url(
        url=url,
        deep_analysis=analysis_config.get('deep_analysis', True),
        extract_images=analysis_config.get('extract_images', True),
        extract_links=analysis_config.get('extract_links', True),
        progress_callback=progress_callback
    )
