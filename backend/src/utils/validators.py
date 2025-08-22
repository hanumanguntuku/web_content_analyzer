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
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """URL validation result"""
    is_valid: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    parsed_url: Optional[Dict[str, Any]] = None

class URLValidator:
    """Comprehensive URL validator with SSRF prevention"""
    
    def __init__(self):
        """Initialize URL validator with security rules"""
        # Blocked schemes
        self.blocked_schemes = {
            'file', 'ftp', 'sftp', 'ssh', 'telnet', 'ldap', 'ldaps',
            'gopher', 'dict', 'jar', 'netdoc', 'javascript', 'data'
        }
        
        # Allowed schemes
        self.allowed_schemes = {'http', 'https'}
        
        # Private IP ranges (RFC 1918, RFC 3927, RFC 4193, etc.)
        self.private_ip_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),        # RFC 1918
            ipaddress.ip_network('172.16.0.0/12'),     # RFC 1918
            ipaddress.ip_network('192.168.0.0/16'),    # RFC 1918
            ipaddress.ip_network('127.0.0.0/8'),       # Loopback
            ipaddress.ip_network('169.254.0.0/16'),    # Link-local
            ipaddress.ip_network('224.0.0.0/4'),       # Multicast
            ipaddress.ip_network('240.0.0.0/4'),       # Reserved
            ipaddress.ip_network('::1/128'),           # IPv6 loopback
            ipaddress.ip_network('fe80::/10'),         # IPv6 link-local
            ipaddress.ip_network('fc00::/7'),          # IPv6 unique local
        ]
        
        # Blocked hostnames
        self.blocked_hostnames = {
            'localhost', 'localhost.localdomain',
            '0.0.0.0', '0', 'local', 'localdomain',
            'ip6-localhost', 'ip6-loopback'
        }
        
        # Blocked domains (cloud metadata services, etc.)
        self.blocked_domains = {
            'metadata.google.internal',
            '169.254.169.254',  # AWS/GCP metadata
            'metadata',
            'instance-data',
            'consul',
            'vault',
            'etcd'
        }
        
        # Blocked ports (common internal services)
        self.blocked_ports = {
            22,    # SSH
            23,    # Telnet
            25,    # SMTP
            53,    # DNS
            110,   # POP3
            135,   # RPC
            139,   # NetBIOS
            143,   # IMAP
            389,   # LDAP
            445,   # SMB
            993,   # IMAPS
            995,   # POP3S
            1433,  # SQL Server
            1521,  # Oracle
            2049,  # NFS
            3306,  # MySQL
            3389,  # RDP
            5432,  # PostgreSQL
            5984,  # CouchDB
            6379,  # Redis
            8080,  # HTTP Alt (often internal)
            9200,  # Elasticsearch
            27017, # MongoDB
        }
        
        # Suspicious patterns in URLs
        self.suspicious_patterns = [
            r'\.\./',           # Directory traversal
            r'%2e%2e%2f',      # Encoded directory traversal
            r'\\',             # Backslash (Windows paths)
            r'%5c',            # Encoded backslash
            r'@',              # User info (potential bypass)
            r'%40',            # Encoded @
        ]
        
        # Rate limiting tracking
        self.validation_counts: Dict[str, int] = {}
        self.max_validations_per_ip = 100
        
        logger.info("URLValidator initialized with comprehensive security rules")
    
    def validate_url(self, url: str, client_ip: Optional[str] = None) -> ValidationResult:
        """Comprehensive URL validation with SSRF prevention"""
        try:
            logger.debug(f"Validating URL: {url}")
            
            # Rate limiting check
            if client_ip and not self._check_rate_limit(client_ip):
                return ValidationResult(
                    is_valid=False,
                    error_type="rate_limit",
                    error_message="Rate limit exceeded for this IP"
                )
            
            # Basic format validation
            basic_result = self._validate_basic_format(url)
            if not basic_result.is_valid:
                return basic_result
            
            # Parse URL
            try:
                parsed = urlparse(url)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    error_type="parse_error",
                    error_message=f"Failed to parse URL: {str(e)}"
                )
            
            # Scheme validation
            scheme_result = self._validate_scheme(parsed.scheme)
            if not scheme_result.is_valid:
                return scheme_result
            
            # Hostname validation
            hostname_result = self._validate_hostname(parsed.hostname)
            if not hostname_result.is_valid:
                return hostname_result
            
            # Port validation
            port_result = self._validate_port(parsed.port, parsed.scheme)
            if not port_result.is_valid:
                return port_result
            
            # IP address validation (resolve hostname)
            ip_result = self._validate_ip_address(parsed.hostname)
            if not ip_result.is_valid:
                return ip_result
            
            # Suspicious pattern detection
            pattern_result = self._check_suspicious_patterns(url)
            if not pattern_result.is_valid:
                return pattern_result
            
            # Security bypass detection
            bypass_result = self._detect_security_bypasses(url, parsed)
            if not bypass_result.is_valid:
                return bypass_result
            
            # Create successful result with parsed data
            parsed_data = {
                'scheme': parsed.scheme,
                'hostname': parsed.hostname,
                'port': parsed.port,
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
            
            logger.info(f"URL validation successful: {url}")
            return ValidationResult(
                is_valid=True,
                parsed_url=parsed_data,
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                error_type="validation_error",
                error_message=f"Validation error: {str(e)}"
            )
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check rate limiting for client IP"""
        current_count = self.validation_counts.get(client_ip, 0)
        if current_count >= self.max_validations_per_ip:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        self.validation_counts[client_ip] = current_count + 1
        return True
    
    def _validate_basic_format(self, url: str) -> ValidationResult:
        """Basic URL format validation"""
        if not url or not isinstance(url, str):
            return ValidationResult(
                is_valid=False,
                error_type="format_error",
                error_message="URL must be a non-empty string"
            )
        
        # Length check
        if len(url) > 2048:  # Reasonable URL length limit
            return ValidationResult(
                is_valid=False,
                error_type="format_error",
                error_message="URL too long (max 2048 characters)"
            )
        
        # Basic URL pattern
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                error_type="format_error",
                error_message="Invalid URL format"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_scheme(self, scheme: str) -> ValidationResult:
        """Validate URL scheme"""
        if not scheme:
            return ValidationResult(
                is_valid=False,
                error_type="scheme_error",
                error_message="URL scheme is required"
            )
        
        scheme_lower = scheme.lower()
        
        if scheme_lower in self.blocked_schemes:
            return ValidationResult(
                is_valid=False,
                error_type="scheme_blocked",
                error_message=f"Scheme '{scheme}' is not allowed"
            )
        
        if scheme_lower not in self.allowed_schemes:
            return ValidationResult(
                is_valid=False,
                error_type="scheme_invalid",
                error_message=f"Only HTTP and HTTPS schemes are allowed"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_hostname(self, hostname: str) -> ValidationResult:
        """Validate hostname for SSRF prevention"""
        if not hostname:
            return ValidationResult(
                is_valid=False,
                error_type="hostname_error",
                error_message="Hostname is required"
            )
        
        hostname_lower = hostname.lower()
        
        # Check blocked hostnames
        if hostname_lower in self.blocked_hostnames:
            return ValidationResult(
                is_valid=False,
                error_type="hostname_blocked",
                error_message=f"Hostname '{hostname}' is blocked"
            )
        
        # Check blocked domains
        for blocked_domain in self.blocked_domains:
            if hostname_lower == blocked_domain or hostname_lower.endswith(f'.{blocked_domain}'):
                return ValidationResult(
                    is_valid=False,
                    error_type="domain_blocked",
                    error_message=f"Domain '{hostname}' is blocked"
                )
        
        # Validate hostname format
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(hostname_pattern, hostname):
            # Check if it's an IP address
            if not self._is_valid_ip(hostname):
                return ValidationResult(
                    is_valid=False,
                    error_type="hostname_invalid",
                    error_message="Invalid hostname format"
                )
        
        return ValidationResult(is_valid=True)
    
    def _validate_port(self, port: Optional[int], scheme: str) -> ValidationResult:
        """Validate port number"""
        # Use default ports if not specified
        default_ports = {'http': 80, 'https': 443}
        actual_port = port or default_ports.get(scheme.lower(), 80)
        
        # Check blocked ports
        if actual_port in self.blocked_ports:
            return ValidationResult(
                is_valid=False,
                error_type="port_blocked",
                error_message=f"Port {actual_port} is blocked"
            )
        
        # Validate port range
        if not (1 <= actual_port <= 65535):
            return ValidationResult(
                is_valid=False,
                error_type="port_invalid",
                error_message="Port must be between 1 and 65535"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_ip_address(self, hostname: str) -> ValidationResult:
        """Validate IP address to prevent SSRF"""
        try:
            # Try to resolve hostname to IP
            try:
                ip_addresses = socket.getaddrinfo(hostname, None)
                resolved_ips = [addr[4][0] for addr in ip_addresses]
            except (socket.gaierror, socket.herror):
                # If hostname doesn't resolve, check if it's a direct IP
                if self._is_valid_ip(hostname):
                    resolved_ips = [hostname]
                else:
                    return ValidationResult(
                        is_valid=False,
                        error_type="hostname_resolution",
                        error_message=f"Cannot resolve hostname: {hostname}"
                    )
            
            # Check each resolved IP
            for ip_str in resolved_ips:
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    
                    # Check if IP is in private ranges
                    for private_range in self.private_ip_ranges:
                        if ip_obj in private_range:
                            return ValidationResult(
                                is_valid=False,
                                error_type="private_ip",
                                error_message=f"Access to private IP address {ip_str} is blocked"
                            )
                    
                    # Additional checks for special IPs
                    if ip_obj.is_reserved or ip_obj.is_multicast:
                        return ValidationResult(
                            is_valid=False,
                            error_type="special_ip",
                            error_message=f"Access to special IP address {ip_str} is blocked"
                        )
                        
                except ipaddress.AddressValueError:
                    continue  # Skip invalid IPs
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            logger.error(f"IP validation error for {hostname}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                error_type="ip_validation_error",
                error_message=f"IP validation failed: {str(e)}"
            )
    
    def _is_valid_ip(self, hostname: str) -> bool:
        """Check if string is a valid IP address"""
        try:
            ipaddress.ip_address(hostname)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def _check_suspicious_patterns(self, url: str) -> ValidationResult:
        """Check for suspicious patterns in URL"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error_type="suspicious_pattern",
                    error_message=f"Suspicious pattern detected in URL"
                )
        
        return ValidationResult(is_valid=True)
    
    def _detect_security_bypasses(self, url: str, parsed) -> ValidationResult:
        """Detect common SSRF bypass attempts"""
        # Check for user info (username:password@host)
        if parsed.username or parsed.password:
            return ValidationResult(
                is_valid=False,
                error_type="user_info_bypass",
                error_message="User information in URLs is not allowed"
            )
        
        # Check for double encoding
        if '%25' in url:  # %25 = encoded %
            return ValidationResult(
                is_valid=False,
                error_type="double_encoding",
                error_message="Double encoding detected"
            )
        
        # Check for Unicode bypasses
        if any(ord(char) > 127 for char in url):
            return ValidationResult(
                is_valid=False,
                error_type="unicode_bypass",
                error_message="Non-ASCII characters in URL are not allowed"
            )
        
        # Check for redirect attempts in parameters
        params = parse_qs(parsed.query)
        redirect_params = ['redirect', 'url', 'next', 'goto', 'return_to', 'continue']
        for param in redirect_params:
            if param in params:
                return ValidationResult(
                    is_valid=False,
                    error_type="redirect_parameter",
                    error_message="Redirect parameters are not allowed"
                )
        
        return ValidationResult(is_valid=True)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'total_validations': sum(self.validation_counts.values()),
            'unique_ips': len(self.validation_counts),
            'blocked_schemes': list(self.blocked_schemes),
            'allowed_schemes': list(self.allowed_schemes),
            'blocked_ports_count': len(self.blocked_ports),
            'private_ip_ranges_count': len(self.private_ip_ranges)
        }
    
    def reset_rate_limits(self):
        """Reset rate limiting counters"""
        self.validation_counts.clear()
        logger.info("Rate limiting counters reset")
                return False
            
            # Basic format check
            if not self.url_pattern.match(url):
                return False
            
            # Parse URL
            parsed = urlparse(url)
            
            # Basic scheme validation
            if parsed.scheme not in ('http', 'https'):
                return False
            
            # Basic hostname validation
            if not parsed.hostname:
                return False
            
            # TODO: Add SSRF prevention in M1-SEC-01
            # - Block private IP ranges
            # - Block metadata endpoints
            # - Add comprehensive security checks
            
            return True
            
        except Exception:
            return False

# Note: Complete security validation will be implemented in M1-SEC phase
