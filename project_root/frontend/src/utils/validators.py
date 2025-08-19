"""Input validation utilities for the frontend"""
import re
from typing import Dict, Any
from urllib.parse import urlparse


def validate_url_input(url: str) -> Dict[str, Any]:
    """Validate URL input and return validation result with feedback"""
    if not url:
        return {"valid": False, "error": "URL cannot be empty"}
    
    if not url.startswith(("http://", "https://")):
        return {"valid": False, "error": "URL must start with http:// or https://"}
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return {"valid": False, "error": "Invalid URL format"}
        
        # Check for basic domain structure
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$'
        if not re.match(domain_pattern, parsed.netloc.split(':')[0]):
            return {"valid": False, "error": "Invalid domain format"}
        
        return {"valid": True, "domain": parsed.netloc, "scheme": parsed.scheme}
    except Exception as e:
        return {"valid": False, "error": f"URL parsing error: {str(e)}"}


def validate_backend_url(url: str) -> bool:
    """Validate backend URL format"""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and parsed.netloc
    except:
        return False
