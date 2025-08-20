"""
Custom Exceptions for Web Content Analyzer
Comprehensive error handling with specific exception types
"""
from typing import Optional, Any, Dict

class WebAnalyzerException(Exception):
    """Base exception for Web Content Analyzer"""
    
    def __init__(
        self, 
        detail: str, 
        error_type: str = "WEB_ANALYZER_ERROR",
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.error_type = error_type
        self.status_code = status_code
        self.context = context or {}
        super().__init__(self.detail)

class ValidationError(WebAnalyzerException):
    """Raised when input validation fails"""
    
    def __init__(self, detail: str, invalid_value: Optional[str] = None):
        super().__init__(
            detail=detail,
            error_type="VALIDATION_ERROR",
            status_code=400,
            context={"invalid_value": invalid_value}
        )

class SecurityError(WebAnalyzerException):
    """Raised when security validation fails"""
    
    def __init__(self, detail: str, url: Optional[str] = None):
        super().__init__(
            detail=detail,
            error_type="SECURITY_ERROR", 
            status_code=403,
            context={"url": url}
        )

class ScrapingError(WebAnalyzerException):
    """Raised when web scraping fails"""
    
    def __init__(self, detail: str, url: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(
            detail=detail,
            error_type="SCRAPING_ERROR",
            status_code=422,
            context={"url": url, "http_status": status_code}
        )

class ContentProcessingError(WebAnalyzerException):
    """Raised when content processing fails"""
    
    def __init__(self, detail: str, content_size: Optional[int] = None):
        super().__init__(
            detail=detail,
            error_type="CONTENT_PROCESSING_ERROR",
            status_code=422,
            context={"content_size": content_size}
        )

class RateLimitError(WebAnalyzerException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            detail=detail,
            error_type="RATE_LIMIT_ERROR",
            status_code=429,
            context={"retry_after": retry_after}
        )

class TimeoutError(WebAnalyzerException):
    """Raised when operation times out"""
    
    def __init__(self, detail: str, timeout_seconds: Optional[int] = None):
        super().__init__(
            detail=detail,
            error_type="TIMEOUT_ERROR",
            status_code=408,
            context={"timeout_seconds": timeout_seconds}
        )

class ContentSizeError(WebAnalyzerException):
    """Raised when content size exceeds limits"""
    
    def __init__(self, detail: str, content_size: int, max_size: int):
        super().__init__(
            detail=detail,
            error_type="CONTENT_SIZE_ERROR",
            status_code=413,
            context={"content_size": content_size, "max_size": max_size}
        )

class InvalidURLError(SecurityError):
    """Raised when URL is invalid or forbidden (SSRF prevention)"""
    
    def __init__(self, detail: str, url: str):
        super().__init__(
            detail=f"Invalid or forbidden URL: {detail}",
            url=url
        )
        self.error_type = "INVALID_URL_ERROR"

class NetworkError(ScrapingError):
    """Raised when network request fails"""
    
    def __init__(self, detail: str, url: str, status_code: Optional[int] = None):
        super().__init__(
            detail=f"Network request failed: {detail}",
            url=url,
            status_code=status_code
        )
        self.error_type = "NETWORK_ERROR"

# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    SecurityError: 403,
    InvalidURLError: 403,
    TimeoutError: 408,
    ContentSizeError: 413,
    ScrapingError: 422,
    ContentProcessingError: 422,
    NetworkError: 422,
    RateLimitError: 429,
    WebAnalyzerException: 500
}
