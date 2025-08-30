"""
Content Sanitization - M1-SEC-02 Implementation
HTML and text content sanitization for XSS prevention and security
"""
import re
import html
import logging
from typing import Dict, Any, List, Optional
import unicodedata

logger = logging.getLogger(__name__)

class ContentSanitizer:
    """Content sanitizer for XSS prevention and security"""
    
    def __init__(self):
        """Initialize content sanitizer with security rules"""
        # Dangerous HTML tags to remove
        self.dangerous_tags = {
            'script', 'style', 'iframe', 'frame', 'frameset', 'object', 'embed',
            'applet', 'form', 'input', 'button', 'textarea', 'select', 'option',
            'link', 'meta', 'base', 'head', 'title', 'noscript'
        }
        
        # Dangerous attributes to remove
        self.dangerous_attributes = {
            'onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout',
            'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset',
            'javascript:', 'vbscript:', 'data:', 'src', 'href'
        }
        
        # XSS patterns to detect and remove
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'data:application/javascript',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
        ]
        
        # Suspicious content patterns
        self.suspicious_patterns = [
            r'<\?php',
            r'<%',
            r'{{',
            r'{%',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
        ]
        
        logger.info("ContentSanitizer initialized with XSS prevention rules")
    
    def sanitize_html(self, content: str) -> Dict[str, Any]:
        """Sanitize HTML content for XSS prevention"""
        try:
            logger.debug(f"Sanitizing HTML content of length: {len(content)}")
            
            if not content:
                return {
                    'sanitized_content': '',
                    'removed_elements': [],
                    'security_warnings': [],
                    'is_safe': True
                }
            
            original_length = len(content)
            removed_elements = []
            security_warnings = []
            
            # Remove dangerous tags
            for tag in self.dangerous_tags:
                pattern = rf'<{tag}[^>]*>.*?</{tag}>'
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    removed_elements.extend([f'{tag} tag' for _ in matches])
                    content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
                
                # Also remove self-closing versions
                pattern = rf'<{tag}[^>]*/?>'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    removed_elements.extend([f'{tag} tag (self-closing)' for _ in matches])
                    content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Check for XSS patterns
            for pattern in self.xss_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    security_warnings.append(f'XSS pattern detected: {pattern}')
                    content = re.sub(pattern, '[REMOVED_XSS]', content, flags=re.IGNORECASE | re.DOTALL)
                    removed_elements.extend(['XSS pattern' for _ in matches])
            
            # Check for suspicious content
            for pattern in self.suspicious_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    security_warnings.append(f'Suspicious pattern detected: {pattern}')
                    content = re.sub(pattern, '[REMOVED_SUSPICIOUS]', content, flags=re.IGNORECASE)
                    removed_elements.extend(['Suspicious content' for _ in matches])
            
            # HTML entity decode safely
            content = html.unescape(content)
            
            # Remove remaining HTML tags (basic sanitization)
            content = re.sub(r'<[^>]+>', '', content)
            
            # Clean up extra whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            is_safe = len(security_warnings) == 0
            sanitized_length = len(content)
            
            result = {
                'sanitized_content': content,
                'removed_elements': removed_elements,
                'security_warnings': security_warnings,
                'is_safe': is_safe,
                'original_length': original_length,
                'sanitized_length': sanitized_length,
                'reduction_percentage': ((original_length - sanitized_length) / original_length * 100) if original_length > 0 else 0
            }
            
            logger.info(f"HTML sanitization complete. Safe: {is_safe}, "
                       f"Removed: {len(removed_elements)} elements, "
                       f"Warnings: {len(security_warnings)}")
            
            return result
            
        except Exception as e:
            logger.error(f"HTML sanitization error: {str(e)}")
            return {
                'sanitized_content': '',
                'removed_elements': [],
                'security_warnings': [f'Sanitization error: {str(e)}'],
                'is_safe': False
            }
    
    def sanitize_text(self, text: str) -> Dict[str, Any]:
        """Sanitize plain text content"""
        try:
            logger.debug(f"Sanitizing text content of length: {len(text)}")
            
            if not text:
                return {
                    'sanitized_text': '',
                    'removed_patterns': [],
                    'is_safe': True
                }
            
            original_text = text
            removed_patterns = []
            
            # Unicode normalization
            text = unicodedata.normalize('NFKC', text)
            
            # Remove null bytes and control characters
            text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    removed_patterns.extend([f'Suspicious pattern: {pattern}' for _ in matches])
                    text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Limit text length for safety
            max_length = 100000  # 100KB limit
            if len(text) > max_length:
                text = text[:max_length] + '...[TRUNCATED]'
                removed_patterns.append(f'Text truncated at {max_length} characters')
            
            is_safe = len(removed_patterns) == 0
            
            result = {
                'sanitized_text': text,
                'removed_patterns': removed_patterns,
                'is_safe': is_safe,
                'original_length': len(original_text),
                'sanitized_length': len(text)
            }
            
            logger.debug(f"Text sanitization complete. Safe: {is_safe}")
            return result
            
        except Exception as e:
            logger.error(f"Text sanitization error: {str(e)}")
            return {
                'sanitized_text': '',
                'removed_patterns': [f'Sanitization error: {str(e)}'],
                'is_safe': False
            }
    
    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata dictionary"""
        try:
            logger.debug("Sanitizing metadata")
            
            sanitized_metadata = {}
            removed_keys = []
            security_warnings = []
            
            for key, value in metadata.items():
                # Sanitize key
                clean_key = self._sanitize_string(str(key))
                
                # Sanitize value
                if isinstance(value, str):
                    sanitized_value = self._sanitize_string(value)
                    
                    # Check for suspicious content in value
                    for pattern in self.suspicious_patterns:
                        if re.search(pattern, sanitized_value, re.IGNORECASE):
                            security_warnings.append(f'Suspicious content in metadata key: {clean_key}')
                            sanitized_value = '[REMOVED_SUSPICIOUS]'
                            break
                    
                    sanitized_metadata[clean_key] = sanitized_value
                elif isinstance(value, (int, float, bool)):
                    sanitized_metadata[clean_key] = value
                elif isinstance(value, (list, dict)):
                    # Recursively sanitize complex types (with depth limit)
                    sanitized_metadata[clean_key] = self._sanitize_complex_value(value, depth=0)
                else:
                    # Skip unknown types
                    removed_keys.append(key)
            
            result = {
                'sanitized_metadata': sanitized_metadata,
                'removed_keys': removed_keys,
                'security_warnings': security_warnings,
                'is_safe': len(security_warnings) == 0
            }
            
            logger.debug(f"Metadata sanitization complete. Keys processed: {len(metadata)}")
            return result
            
        except Exception as e:
            logger.error(f"Metadata sanitization error: {str(e)}")
            return {
                'sanitized_metadata': {},
                'removed_keys': list(metadata.keys()) if metadata else [],
                'security_warnings': [f'Sanitization error: {str(e)}'],
                'is_safe': False
            }
    
    def _sanitize_string(self, text: str, max_length: int = 1000) -> str:
        """Sanitize a single string value"""
        if not text:
            return ''
        
        # Convert to string and normalize
        text = str(text)
        text = unicodedata.normalize('NFKC', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # HTML escape
        text = html.escape(text)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _sanitize_complex_value(self, value: Any, depth: int = 0, max_depth: int = 3) -> Any:
        """Recursively sanitize complex data structures"""
        if depth > max_depth:
            return '[DEPTH_LIMIT_EXCEEDED]'
        
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, (int, float, bool)):
            return value
        elif isinstance(value, list):
            return [self._sanitize_complex_value(item, depth + 1, max_depth) for item in value[:10]]  # Limit list size
        elif isinstance(value, dict):
            sanitized_dict = {}
            for k, v in list(value.items())[:20]:  # Limit dict size
                clean_key = self._sanitize_string(str(k), max_length=100)
                sanitized_dict[clean_key] = self._sanitize_complex_value(v, depth + 1, max_depth)
            return sanitized_dict
        else:
            return str(value)  # Convert unknown types to string
    
    def add_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'Content-Security-Policy': "default-src 'self'; script-src 'none'; object-src 'none';",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    def validate_content_safety(self, content: str) -> Dict[str, Any]:
        """Comprehensive content safety validation"""
        try:
            safety_score = 100.0
            issues = []
            
            # Check content length
            if len(content) > 1000000:  # 1MB
                safety_score -= 20
                issues.append('Content too large')
            
            # Check for XSS patterns
            xss_count = 0
            for pattern in self.xss_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                xss_count += matches
            
            if xss_count > 0:
                safety_score -= min(50, xss_count * 10)
                issues.append(f'XSS patterns detected: {xss_count}')
            
            # Check for suspicious patterns
            suspicious_count = 0
            for pattern in self.suspicious_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                suspicious_count += matches
            
            if suspicious_count > 0:
                safety_score -= min(30, suspicious_count * 5)
                issues.append(f'Suspicious patterns detected: {suspicious_count}')
            
            # Check for excessive HTML tags
            html_tags = len(re.findall(r'<[^>]+>', content))
            if html_tags > 100:
                safety_score -= min(20, (html_tags - 100) / 10)
                issues.append(f'Excessive HTML tags: {html_tags}')
            
            safety_score = max(0, safety_score)
            is_safe = safety_score >= 70
            
            return {
                'safety_score': safety_score,
                'is_safe': is_safe,
                'issues': issues,
                'recommendation': 'SAFE' if is_safe else 'REQUIRES_SANITIZATION'
            }
            
        except Exception as e:
            logger.error(f"Content safety validation error: {str(e)}")
            return {
                'safety_score': 0,
                'is_safe': False,
                'issues': [f'Validation error: {str(e)}'],
                'recommendation': 'REQUIRES_SANITIZATION'
            }
