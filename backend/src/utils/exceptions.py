"""
Custom Exceptions - M1-SVC-02 Implementation
Comprehensive error handling with specific exception types for all failure scenarios
"""
from typing import Optional, Any, Dict

class WebAnalyzerException(Exception):
    """Base exception for Web Content Analyzer"""
    
    def __init__(
        self, 
        detail: str, 
        error_type: str = "WEB_ANALYZER_ERROR",
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        # Remove any conflicting keys from kwargs
        kwargs.pop('error_type', None)
        kwargs.pop('status_code', None)
        kwargs.pop('context', None)
        
        self.detail = detail
        self.error_type = error_type
        self.status_code = status_code
        self.context = context or {}
        super().__init__(detail)

# Security-related exceptions
class SecurityException(WebAnalyzerException):
    """Base class for security-related exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        super().__init__(detail, error_type="SECURITY_ERROR", status_code=403, **kwargs)

class SSRFException(SecurityException):
    """SSRF attempt detected"""
    
    def __init__(self, detail: str, url: str = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['blocked_url'] = url
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class RateLimitException(SecurityException):
    """Rate limit exceeded"""
    
    def __init__(self, detail: str, client_ip: str = None, reset_time: float = None, **kwargs):
        context = kwargs.get('context', {})
        if client_ip:
            context['client_ip'] = client_ip
        if reset_time:
            context['reset_time'] = reset_time
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class ContentSizeException(SecurityException):
    """Content size limits exceeded"""
    
    def __init__(self, detail: str, size: int = None, limit: int = None, **kwargs):
        context = kwargs.get('context', {})
        if size:
            context['actual_size'] = size
        if limit:
            context['size_limit'] = limit
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

# Validation exceptions
class ValidationException(WebAnalyzerException):
    """Base class for validation exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        super().__init__(detail, error_type="VALIDATION_ERROR", status_code=400, **kwargs)

class URLValidationException(ValidationException):
    """URL validation failed"""
    
    def __init__(self, detail: str, url: str = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['invalid_url'] = url
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class ContentValidationException(ValidationException):
    """Content validation failed"""
    
    def __init__(self, detail: str, content_type: str = None, **kwargs):
        context = kwargs.get('context', {})
        if content_type:
            context['content_type'] = content_type
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

# Processing exceptions
class ProcessingException(WebAnalyzerException):
    """Base class for processing exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code']}
        super().__init__(detail, error_type="PROCESSING_ERROR", status_code=500, **clean_kwargs)

class ScrapingException(ProcessingException):
    """Web scraping failed"""
    
    def __init__(self, detail: str, url: str = None, status_code: int = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['target_url'] = url
        if status_code:
            context['http_status'] = status_code
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class ExtractionException(ProcessingException):
    """Content extraction failed"""
    
    def __init__(self, detail: str, url: str = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['source_url'] = url
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class TextProcessingException(ProcessingException):
    """Text processing failed"""
    
    def __init__(self, detail: str, processing_stage: str = None, **kwargs):
        context = kwargs.get('context', {})
        if processing_stage:
            context['processing_stage'] = processing_stage
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

# Network-related exceptions
class NetworkException(WebAnalyzerException):
    """Base class for network-related exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code']}
        super().__init__(detail, error_type="NETWORK_ERROR", status_code=502, **clean_kwargs)

class ConnectionException(NetworkException):
    """Network connection failed"""
    
    def __init__(self, detail: str, url: str = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['target_url'] = url
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class TimeoutException(NetworkException):
    """Request timeout"""
    
    def __init__(self, detail: str, url: str = None, timeout: float = None, **kwargs):
        context = kwargs.get('context', {})
        if url:
            context['target_url'] = url
        if timeout:
            context['timeout_seconds'] = timeout
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class HTTPException(NetworkException):
    """HTTP error response"""
    
    def __init__(self, detail: str, status_code: int, url: str = None, **kwargs):
        context = kwargs.get('context', {})
        context['http_status'] = status_code
        if url:
            context['target_url'] = url
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

# Resource exceptions
class ResourceException(WebAnalyzerException):
    """Base class for resource-related exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code']}
        super().__init__(detail, error_type="RESOURCE_ERROR", status_code=503, **clean_kwargs)

class ResourceExhaustedException(ResourceException):
    """System resources exhausted"""
    
    def __init__(self, detail: str, resource_type: str = None, **kwargs):
        context = kwargs.get('context', {})
        if resource_type:
            context['resource_type'] = resource_type
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class ProcessingTimeoutException(ResourceException):
    """Processing timeout exceeded"""
    
    def __init__(self, detail: str, process_id: str = None, elapsed_time: float = None, **kwargs):
        context = kwargs.get('context', {})
        if process_id:
            context['process_id'] = process_id
        if elapsed_time:
            context['elapsed_time'] = elapsed_time
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

# Configuration exceptions
class ConfigurationException(WebAnalyzerException):
    """Configuration error"""
    
    def __init__(self, detail: str, config_key: str = None, **kwargs):
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, error_type="CONFIGURATION_ERROR", status_code=500, context=context, **clean_kwargs)

# API-specific exceptions
class APIException(WebAnalyzerException):
    """Base class for API-related exceptions"""
    
    def __init__(self, detail: str, **kwargs):
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type']}
        super().__init__(detail, error_type="API_ERROR", **clean_kwargs)

class InvalidRequestException(APIException):
    """Invalid API request"""
    
    def __init__(self, detail: str, field: str = None, **kwargs):
        context = kwargs.get('context', {})
        if field:
            context['invalid_field'] = field
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code', 'context']}
        super().__init__(detail, context=context, **clean_kwargs)

class ServiceUnavailableException(APIException):
    """Service temporarily unavailable"""
    
    def __init__(self, detail: str = "Service temporarily unavailable", **kwargs):
        # Clean kwargs to avoid conflicts
        clean_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['error_type', 'status_code']}
        super().__init__(detail, error_type="SERVICE_UNAVAILABLE", status_code=503, **clean_kwargs)

# Utility functions for exception handling
def create_error_response(exception: WebAnalyzerException) -> Dict[str, Any]:
    """Create standardized error response from exception"""
    return {
        "error": {
            "type": exception.error_type,
            "message": exception.detail,
            "status_code": exception.status_code,
            "context": exception.context
        }
    }

def is_client_error(exception: WebAnalyzerException) -> bool:
    """Check if exception is a client error (4xx)"""
    return 400 <= exception.status_code < 500

def is_server_error(exception: WebAnalyzerException) -> bool:
    """Check if exception is a server error (5xx)"""
    return exception.status_code >= 500

def get_user_friendly_message(exception: WebAnalyzerException) -> str:
    """Get user-friendly error message"""
    user_friendly_messages = {
        "SSRF_BLOCKED": "The requested URL is not accessible for security reasons.",
        "RATE_LIMIT_EXCEEDED": "Too many requests. Please wait before trying again.",
        "CONTENT_SIZE_EXCEEDED": "The content is too large to process.",
        "INVALID_URL": "The provided URL is not valid or accessible.",
        "SCRAPING_FAILED": "Unable to retrieve content from the website.",
        "EXTRACTION_FAILED": "Unable to extract meaningful content from the page.",
        "CONNECTION_FAILED": "Unable to connect to the website.",
        "REQUEST_TIMEOUT": "The request took too long to complete.",
        "SERVICE_UNAVAILABLE": "The service is temporarily unavailable."
    }
    
    return user_friendly_messages.get(
        exception.error_type, 
        "An error occurred while processing your request."
    )

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
