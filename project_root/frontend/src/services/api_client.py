"""API Client for backend communication"""
import requests
import streamlit as st
from typing import Dict, Any, Optional
from ..utils.validators import validate_backend_url


class APIClient:
    """Client for communicating with the backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 60
    
    def set_base_url(self, url: str):
        """Update the base URL"""
        self.base_url = url
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to backend"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return {"success": True, "message": "Backend connected!"}
            else:
                return {"success": False, "message": f"Backend error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}
    
    def analyze_content(self, url: str) -> Dict[str, Any]:
        """Send content analysis request to backend"""
        try:
            # Test backend connection first
            health_response = requests.get(f"{self.base_url}/health", timeout=5)
            if health_response.status_code != 200:
                raise Exception("Backend health check failed")
            
            # Send analysis request
            payload = {"url": url}
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "data": result}
            else:
                # Handle HTTP errors
                error_message = f"Analysis failed with status {response.status_code}"
                try:
                    error_detail = response.json().get("detail", response.text)
                    error_message += f": {error_detail}"
                except:
                    error_message += f": {response.text}"
                
                return {
                    "success": False, 
                    "error": error_message,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - the analysis took too long (>60 seconds)",
                "error_type": "timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error - unable to reach the backend",
                "error_type": "connection"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "unexpected"
            }
    
    def get_error_guidance(self, error_type: str, status_code: Optional[int] = None) -> str:
        """Get user-friendly error guidance"""
        guidance = {
            "timeout": "💡 Try again with a different URL or check if the target site is responsive",
            "connection": "💡 Make sure the backend is running on the correct port",
            "unexpected": "💡 Please try again or contact support if the issue persists"
        }
        
        if status_code:
            if status_code == 422:
                return "💡 Tip: Check if the URL format is correct"
            elif status_code == 500:
                return "💡 Tip: The website might be blocking our scraper or temporarily unavailable"
        
        return guidance.get(error_type, "💡 Please try again")


# Global API client instance
api_client = APIClient()
