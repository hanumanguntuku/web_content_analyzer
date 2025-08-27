"""
Enhanced API Client - M1-PRES-04 Implementation
Robust API client with comprehensive error handling and progress tracking
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, Callable
import time
import json
import logging
from urllib.parse import urljoin

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedAPIClient:

    def analyze_batch(self, urls: list, deep_analysis=True, extract_images=True, extract_links=True) -> list:
        """Analyze a batch of URLs via the batch endpoint."""
        from src.components.enhanced_url_input import validate_url_format
        valid_urls = [u for u in urls if validate_url_format(u)[0]]
        if not valid_urls:
            logger.warning("No valid URLs provided for batch analysis.")
            return []
        endpoint = "/api/v1/analyze/batch"
        payload = [
            {
                "url": u,
                "options": {},
                "deep_analysis": deep_analysis,
                "extract_media": extract_images,  # must match backend model
                "extract_contacts": True,
            }
            for u in valid_urls
        ]
        logger.info(f"Batch payload: {payload}")
        url = self._get_full_url(endpoint)
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"Batch analysis failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    logger.warning(f"Backend response: {e.response.text}")
                except Exception:
                    pass
            return []

    def get_analysis_history(self) -> list:
        """Get analysis history from backend.

        Returns a list of history entries or an empty list on error.
        """
        endpoint = "/api/v1/analyze/history"
        url = self._get_full_url(endpoint)
        try:
            resp = requests.get(url, timeout=min(10, self.timeout))
            resp.raise_for_status()
            data = resp.json()
            # Backend may return { "history": [...] } or a bare list
            if isinstance(data, dict) and "history" in data:
                return data.get("history") or []
            if isinstance(data, list):
                return data
            return []
        except requests.exceptions.RequestException as e:
            logger.warning("Failed to fetch analysis history: %s", e)
            return []
        except ValueError:
            logger.warning("Failed to decode analysis history JSON response")
            return []
    """
    Enhanced API client for communication with the backend analysis service
    
    Features:
    - Robust error handling
    - Progress tracking
    - Retry logic
    - Timeout management
    - Session management
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
        self.session = None
        
        # API endpoints
        self.endpoints = {
            'analyze': '/api/v1/analyze',
            'status': '/api/v1/status',
            'health': '/api/v1/health',
            'stats': '/api/v1/stats'
        }
    
    def _get_full_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint"""
        return urljoin(self.base_url, endpoint)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response with proper error handling"""
        try:
            # Check if response is successful
            if response.status_code == 200:
                return response.json()
            
            # Handle different error status codes
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
                # Other error codes
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
        """Check if the backend is available and healthy"""
        try:
            url = self._get_full_url(self.endpoints['status'])
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    "available": True,
                    "status": "healthy",
                    "data": response.json()
                }
            else:
                return {
                    "available": False,
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
        
        except requests.exceptions.ConnectionError:
            return {
                "available": False,
                "status": "unreachable",
                "error": "Could not connect to backend server"
            }
        
        except requests.exceptions.Timeout:
            return {
                "available": False,
                "status": "timeout",
                "error": "Backend server did not respond in time"
            }
        
        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_url(
        self,
        url: str,
        deep_analysis: bool = True,
        extract_images: bool = True,
        extract_links: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze a URL with comprehensive error handling and progress tracking
        
        Args:
            url: URL to analyze
            deep_analysis: Enable deep text processing
            extract_images: Extract image information
            extract_links: Extract link information
            progress_callback: Callback function for progress updates
            
        Returns:
            Analysis result or error information
        """
        
        # Prepare request data
        request_data = {
            "url": url,
            "deep_analysis": deep_analysis,
            "extract_images": extract_images,
            "extract_links": extract_links
        }
        
        # Update progress
        if progress_callback:
            progress_callback("initializing", 5, "Preparing analysis request...")
        
        try:
            # Check backend availability first
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
            
            # Make analysis request with retries
            for attempt in range(self.max_retries):
                try:
                    if progress_callback:
                        progress_callback("web_scraping", 20 + (attempt * 5), f"Sending request (attempt {attempt + 1})...")
                    
                    url_endpoint = self._get_full_url(self.endpoints['analyze'])
                    response = requests.post(
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
                    
                    # Handle the response
                    result = self._handle_response(response)
                    
                    if not result.get("error"):
                        if progress_callback:
                            progress_callback("completed", 100, "Analysis completed successfully!")
                        return result
                    
                    # If we get an error and it's not the last attempt, retry
                    if attempt < self.max_retries - 1:
                        if result.get("status_code") in [500, 502, 503, 504]:  # Server errors worth retrying
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    
                    # Return the error if we're not retrying
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
        
        # Fallback error (should not reach here)
        return {
            "error": True,
            "error_type": "UNKNOWN_ERROR",
            "message": "Analysis failed for unknown reasons",
            "technical_details": "No specific error information available"
        }
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get detailed service health information"""
        try:
            url = self._get_full_url(self.endpoints['health'])
            response = requests.get(url, timeout=10)
            return self._handle_response(response)
        
        except Exception as e:
            return {
                "error": True,
                "error_type": "HEALTH_CHECK_ERROR",
                "message": "Could not retrieve service health",
                "technical_details": str(e)
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics"""
        try:
            url = self._get_full_url(self.endpoints['stats'])
            response = requests.get(url, timeout=10)
            return self._handle_response(response)
        
        except Exception as e:
            return {
                "error": True,
                "error_type": "STATS_ERROR",
                "message": "Could not retrieve service statistics",
                "technical_details": str(e)
            }

# Global API client instance
_api_client = None

def get_api_client() -> EnhancedAPIClient:
    """Get or create the global API client instance"""
    global _api_client
    
    if _api_client is None:
        # Get backend URL from environment or use default
        backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")
        _api_client = EnhancedAPIClient(base_url=backend_url)
    
    return _api_client

def test_backend_connection() -> Dict[str, Any]:
    """Test the backend connection and return status"""
    client = get_api_client()
    return client.check_backend_status()

def analyze_website(
    url: str,
    analysis_config: Dict[str, Any],
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze a website
    
    Args:
        url: URL to analyze
        analysis_config: Analysis configuration options
        progress_callback: Optional progress callback function
        
    Returns:
        Analysis result or error information
    """
    client = get_api_client()
    if analysis_config.get("batch_mode"):
        return client.analyze_batch(
            urls=analysis_config["urls"],
            deep_analysis=analysis_config.get('deep_analysis', True),
            extract_images=analysis_config.get('extract_images', True),
            extract_links=analysis_config.get('extract_links', True)
        )
    else:
        return client.analyze_url(
            url=url,
            deep_analysis=analysis_config.get('deep_analysis', True),
            extract_images=analysis_config.get('extract_images', True),
            extract_links=analysis_config.get('extract_links', True),
            progress_callback=progress_callback
        )

def get_analysis_history():
    try:
        client = get_api_client()
        history = client.get_analysis_history()
        return history or []
    except Exception as e:
        logger.warning("Could not retrieve analysis history: %s", e)
        return []
