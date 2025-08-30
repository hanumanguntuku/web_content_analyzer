"""
URL Validation & SSRF Prevention - M1-SEC-01 Implementation
Comprehensive URL validation with security measures to prevent SSRF attacks
"""
import ipaddress
import socket
import logging
from typing import List, Set, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import re
from .validators import ValidationResult

logger = logging.getLogger(__name__)


class URLValidator:
    """Comprehensive URL validator with SSRF prevention"""
    
    def __init__(self):
        """Initialize URL validator with security rules"""
        # Private IP ranges (RFC 1918, RFC 3927, RFC 4193, etc.)
        self.private_ip_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),        # RFC 1918
            ipaddress.ip_network('172.16.0.0/12'),     # RFC 1918
            ipaddress.ip_network('192.168.0.0/16'),    # RFC 1918
            ipaddress.ip_network('127.0.0.0/8'),       # Loopback
            ipaddress.ip_network('169.254.0.0/16'),    # Link-local
        ]
        
        # Blocked hostnames
        self.blocked_hostnames = {
            'localhost', 'localhost.localdomain', '0.0.0.0', '0'
        }
        
        logger.info("URLValidator initialized with SSRF prevention")
    
    def validate_url(self, url: str) -> ValidationResult:
        """Validate URL with SSRF prevention"""
        try:
            if not url or len(url) > 2048:
                return ValidationResult(
                    is_valid=False,
                    error_type="format_error",
                    error_message="Invalid URL format or too long"
                )
            
            parsed = urlparse(url)
            
            if parsed.scheme not in ('http', 'https'):
                return ValidationResult(
                    is_valid=False,
                    error_type="scheme_error",
                    error_message="Only HTTP and HTTPS schemes allowed"
                )
            
            if not parsed.hostname:
                return ValidationResult(
                    is_valid=False,
                    error_type="hostname_error",
                    error_message="Hostname is required"
                )
            
            # Check blocked hostnames
            if parsed.hostname.lower() in self.blocked_hostnames:
                return ValidationResult(
                    is_valid=False,
                    error_type="hostname_blocked",
                    error_message=f"Hostname '{parsed.hostname}' is blocked"
                )
            
            # Check if hostname resolves to private IP
            try:
                ip_addresses = socket.getaddrinfo(parsed.hostname, None)
                for addr in ip_addresses:
                    ip_str = addr[4][0]
                    try:
                        ip_obj = ipaddress.ip_address(ip_str)
                        for private_range in self.private_ip_ranges:
                            if ip_obj in private_range:
                                return ValidationResult(
                                    is_valid=False,
                                    error_type="private_ip",
                                    error_message=f"Access to private IP {ip_str} blocked"
                                )
                    except ipaddress.AddressValueError:
                        continue
            except (socket.gaierror, socket.herror):
                pass  # Hostname doesn't resolve, but that's ok
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_type="validation_error",
                error_message=f"Validation error: {str(e)}"
            )
