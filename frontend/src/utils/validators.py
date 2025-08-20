"""
Input Validators
Utility functions for validating user inputs
"""
import re
from typing import Tuple, Optional
from urllib.parse import urlparse

def validate_url_input(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL input from user
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    # Remove whitespace
    url = url.strip()
    
    # Check minimum length
    if len(url) < 10:
        return False, "URL seems too short"
    
    # Check maximum length (prevent very long URLs)
    if len(url) > 2048:
        return False, "URL is too long (max 2048 characters)"
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"
    
    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        return False, "URL must use HTTP or HTTPS protocol"
    
    # Check netloc (domain)
    if not parsed.netloc:
        return False, "URL must include a domain name"
    
    # Check for localhost/private IPs (basic SSRF prevention)
    if is_private_or_local_url(parsed.netloc):
        return False, "Cannot analyze localhost or private network URLs"
    
    # Check domain format
    if not is_valid_domain(parsed.netloc):
        return False, "Invalid domain name format"
    
    return True, None

def is_private_or_local_url(netloc: str) -> bool:
    """
    Check if URL points to localhost or private network
    Basic SSRF prevention
    """
    # Remove port if present
    hostname = netloc.split(':')[0].lower()
    
    # Check localhost patterns
    localhost_patterns = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '127.',
        '10.',
        '172.16.',
        '172.17.',
        '172.18.',
        '172.19.',
        '172.20.',
        '172.21.',
        '172.22.',
        '172.23.',
        '172.24.',
        '172.25.',
        '172.26.',
        '172.27.',
        '172.28.',
        '172.29.',
        '172.30.',
        '172.31.',
        '192.168.'
    ]
    
    for pattern in localhost_patterns:
        if hostname.startswith(pattern):
            return True
    
    return False

def is_valid_domain(domain: str) -> bool:
    """
    Validate domain name format
    """
    # Remove port if present
    domain = domain.split(':')[0]
    
    # Basic domain regex pattern
    domain_pattern = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    # Check length
    if len(domain) > 253:
        return False
    
    # Check format
    if not domain_pattern.match(domain):
        return False
    
    # Must contain at least one dot (except for localhost which we block anyway)
    if '.' not in domain:
        return False
    
    return True

def sanitize_url(url: str) -> str:
    """
    Sanitize URL for safe processing
    """
    if not url:
        return ""
    
    # Remove whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def validate_analysis_depth(depth: str) -> Tuple[bool, Optional[str]]:
    """
    Validate analysis depth parameter
    """
    valid_depths = ['basic', 'standard', 'comprehensive']
    
    if depth not in valid_depths:
        return False, f"Analysis depth must be one of: {', '.join(valid_depths)}"
    
    return True, None
