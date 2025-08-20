"""
API Client Service for Backend Communication
Handles all HTTP requests to the FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, List
import logging
import time

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Web Content Analyzer backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WebContentAnalyzer-Frontend/1.0.0'
        })
        
        logger.info(f"APIClient initialized with base_url: {self.base_url}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the backend API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            logger.info(f"Request successful: {method} {url}")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {self.timeout} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to backend at {self.base_url}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            
            # Try to parse error response
            try:
                error_data = e.response.json()
                if 'detail' in error_data:
                    raise Exception(error_data['detail'])
            except:
                pass
                
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def health_check(self) -> Dict[str, Any]:
        """Check backend health status"""
        return self._make_request('GET', '/health')
    
    def get_status(self) -> Dict[str, Any]:
        """Get API service status and configuration"""
        return self._make_request('GET', '/api/v1/status')
    
    def analyze_url(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a website URL
        
        Args:
            url: URL to analyze
            options: Optional analysis configuration
            
        Returns:
            Analysis results dictionary
        """
        payload = {
            "url": url,
            "options": options or {}
        }
        
        return self._make_request('POST', '/api/v1/analyze', data=payload)
    
    def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis result by ID (for future async processing)"""
        return self._make_request('GET', f'/api/v1/analyze/{analysis_id}')
    
    def get_supported_sites(self) -> Dict[str, Any]:
        """Get list of supported website types"""
        return self._make_request('GET', '/api/v1/supported-sites')
    
    def test_connection(self) -> bool:
        """Test if backend is reachable"""
        try:
            self.health_check()
            return True
        except Exception as e:
            logger.error(f"Backend connection test failed: {str(e)}")
            return False

# Streamlit cache decorator for API client
@st.cache_resource
def get_cached_api_client(base_url: str) -> APIClient:
    """Get cached API client instance"""
    return APIClient(base_url=base_url)
