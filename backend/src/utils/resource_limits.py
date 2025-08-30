"""
Content Size Limits & Rate Limiting - M1-SEC-03 Implementation
Resource management and abuse prevention
"""
import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

@dataclass
class LimitResult:
    """Result of rate/size limit check"""
    allowed: bool
    message: str
    remaining: Optional[int] = None
    reset_time: Optional[float] = None

class ContentSizeLimiter:
    """Content size limits and validation"""
    
    def __init__(self):
        """Initialize content size limiter"""
        # Size limits in bytes
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        self.max_text_length = 1 * 1024 * 1024    # 1MB for text
        self.max_title_length = 500               # 500 chars
        self.max_description_length = 2000        # 2000 chars
        self.max_url_length = 2048               # 2048 chars
        self.max_metadata_size = 100 * 1024     # 100KB
        
        # Processing limits
        self.max_processing_time = 120           # 2 minutes
        self.max_memory_usage = 512 * 1024 * 1024  # 512MB
        
        logger.info("ContentSizeLimiter initialized with safety limits")
    
    def check_content_size(self, content: bytes) -> LimitResult:
        """Check if content size is within limits"""
        try:
            content_size = len(content)
            
            if content_size > self.max_content_size:
                return LimitResult(
                    allowed=False,
                    message=f"Content size {content_size} bytes exceeds limit of {self.max_content_size} bytes"
                )
            
            return LimitResult(
                allowed=True,
                message="Content size acceptable",
                remaining=self.max_content_size - content_size
            )
            
        except Exception as e:
            logger.error(f"Content size check error: {str(e)}")
            return LimitResult(
                allowed=False,
                message=f"Size check error: {str(e)}"
            )
    
    def check_text_length(self, text: str) -> LimitResult:
        """Check if text length is within limits"""
        try:
            text_length = len(text)
            
            if text_length > self.max_text_length:
                return LimitResult(
                    allowed=False,
                    message=f"Text length {text_length} exceeds limit of {self.max_text_length}"
                )
            
            return LimitResult(
                allowed=True,
                message="Text length acceptable",
                remaining=self.max_text_length - text_length
            )
            
        except Exception as e:
            logger.error(f"Text length check error: {str(e)}")
            return LimitResult(
                allowed=False,
                message=f"Length check error: {str(e)}"
            )
    
    def truncate_content_safely(self, content: str, max_length: Optional[int] = None) -> Dict[str, Any]:
        """Safely truncate content to fit limits"""
        try:
            if max_length is None:
                max_length = self.max_text_length
            
            original_length = len(content)
            
            if original_length <= max_length:
                return {
                    'content': content,
                    'was_truncated': False,
                    'original_length': original_length,
                    'final_length': original_length
                }
            
            # Truncate at word boundary if possible
            truncated = content[:max_length]
            
            # Try to find last complete word
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # If space is in last 20%, use it
                truncated = truncated[:last_space]
            
            # Add truncation indicator
            truncated += '...[TRUNCATED]'
            
            return {
                'content': truncated,
                'was_truncated': True,
                'original_length': original_length,
                'final_length': len(truncated),
                'truncated_chars': original_length - max_length
            }
            
        except Exception as e:
            logger.error(f"Content truncation error: {str(e)}")
            return {
                'content': content[:1000] if len(content) > 1000 else content,
                'was_truncated': True,
                'error': str(e)
            }

class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self):
        """Initialize rate limiter"""
        self.requests = defaultdict(deque)  # IP -> deque of timestamps
        self.lock = threading.Lock()
        
        # Rate limits
        self.max_requests_per_minute = 30
        self.max_requests_per_hour = 200
        self.max_requests_per_day = 1000
        
        # Time windows in seconds
        self.minute_window = 60
        self.hour_window = 3600
        self.day_window = 86400
        
        logger.info("RateLimiter initialized with tiered limits")
    
    def check_rate_limit(self, client_ip: str) -> LimitResult:
        """Check if client is within rate limits"""
        try:
            with self.lock:
                current_time = time.time()
                client_requests = self.requests[client_ip]
                
                # Clean old requests
                self._clean_old_requests(client_requests, current_time)
                
                # Check minute limit
                minute_count = self._count_requests_in_window(
                    client_requests, current_time, self.minute_window
                )
                if minute_count >= self.max_requests_per_minute:
                    return LimitResult(
                        allowed=False,
                        message=f"Rate limit exceeded: {minute_count}/{self.max_requests_per_minute} per minute",
                        remaining=0,
                        reset_time=current_time + self.minute_window
                    )
                
                # Check hour limit
                hour_count = self._count_requests_in_window(
                    client_requests, current_time, self.hour_window
                )
                if hour_count >= self.max_requests_per_hour:
                    return LimitResult(
                        allowed=False,
                        message=f"Rate limit exceeded: {hour_count}/{self.max_requests_per_hour} per hour",
                        remaining=0,
                        reset_time=current_time + self.hour_window
                    )
                
                # Check day limit
                day_count = self._count_requests_in_window(
                    client_requests, current_time, self.day_window
                )
                if day_count >= self.max_requests_per_day:
                    return LimitResult(
                        allowed=False,
                        message=f"Rate limit exceeded: {day_count}/{self.max_requests_per_day} per day",
                        remaining=0,
                        reset_time=current_time + self.day_window
                    )
                
                # Add current request
                client_requests.append(current_time)
                
                return LimitResult(
                    allowed=True,
                    message="Rate limit check passed",
                    remaining=self.max_requests_per_minute - minute_count - 1
                )
                
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return LimitResult(
                allowed=True,  # Allow on error to prevent service disruption
                message=f"Rate limit check error: {str(e)}"
            )
    
    def _clean_old_requests(self, requests: deque, current_time: float):
        """Remove requests older than day window"""
        cutoff_time = current_time - self.day_window
        while requests and requests[0] < cutoff_time:
            requests.popleft()
    
    def _count_requests_in_window(self, requests: deque, current_time: float, window: int) -> int:
        """Count requests within time window"""
        cutoff_time = current_time - window
        return sum(1 for req_time in requests if req_time >= cutoff_time)
    
    def get_rate_limit_stats(self, client_ip: str) -> Dict[str, Any]:
        """Get rate limit statistics for client"""
        try:
            with self.lock:
                current_time = time.time()
                client_requests = self.requests.get(client_ip, deque())
                
                minute_count = self._count_requests_in_window(
                    client_requests, current_time, self.minute_window
                )
                hour_count = self._count_requests_in_window(
                    client_requests, current_time, self.hour_window
                )
                day_count = self._count_requests_in_window(
                    client_requests, current_time, self.day_window
                )
                
                return {
                    'requests_last_minute': minute_count,
                    'requests_last_hour': hour_count,
                    'requests_last_day': day_count,
                    'minute_limit': self.max_requests_per_minute,
                    'hour_limit': self.max_requests_per_hour,
                    'day_limit': self.max_requests_per_day,
                    'minute_remaining': max(0, self.max_requests_per_minute - minute_count),
                    'hour_remaining': max(0, self.max_requests_per_hour - hour_count),
                    'day_remaining': max(0, self.max_requests_per_day - day_count)
                }
                
        except Exception as e:
            logger.error(f"Rate limit stats error: {str(e)}")
            return {
                'error': str(e)
            }

class ResourceMonitor:
    """Monitor system resources and processing time"""
    
    def __init__(self):
        """Initialize resource monitor"""
        self.active_processes = {}
        self.max_concurrent_processes = 10
        self.max_processing_time = 120  # 2 minutes
        self.lock = threading.Lock()
        
        logger.info("ResourceMonitor initialized")
    
    def start_processing(self, process_id: str, client_ip: str) -> LimitResult:
        """Start monitoring a processing task"""
        try:
            with self.lock:
                # Check concurrent process limit
                if len(self.active_processes) >= self.max_concurrent_processes:
                    return LimitResult(
                        allowed=False,
                        message=f"Too many concurrent processes: {len(self.active_processes)}/{self.max_concurrent_processes}"
                    )
                
                # Start tracking
                self.active_processes[process_id] = {
                    'client_ip': client_ip,
                    'start_time': time.time(),
                    'status': 'active'
                }
                
                return LimitResult(
                    allowed=True,
                    message="Processing started",
                    remaining=self.max_concurrent_processes - len(self.active_processes)
                )
                
        except Exception as e:
            logger.error(f"Start processing error: {str(e)}")
            return LimitResult(
                allowed=False,
                message=f"Resource monitoring error: {str(e)}"
            )
    
    def finish_processing(self, process_id: str) -> bool:
        """Finish monitoring a processing task"""
        try:
            with self.lock:
                if process_id in self.active_processes:
                    process_info = self.active_processes[process_id]
                    processing_time = time.time() - process_info['start_time']
                    
                    logger.info(f"Process {process_id} completed in {processing_time:.2f}s")
                    del self.active_processes[process_id]
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Finish processing error: {str(e)}")
            return False
    
    def check_timeout(self, process_id: str) -> bool:
        """Check if process has timed out"""
        try:
            with self.lock:
                if process_id not in self.active_processes:
                    return False
                
                process_info = self.active_processes[process_id]
                processing_time = time.time() - process_info['start_time']
                
                if processing_time > self.max_processing_time:
                    logger.warning(f"Process {process_id} timed out after {processing_time:.2f}s")
                    process_info['status'] = 'timeout'
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Timeout check error: {str(e)}")
            return False
    
    def cleanup_stale_processes(self):
        """Clean up stale or timed out processes"""
        try:
            with self.lock:
                current_time = time.time()
                stale_processes = []
                
                for process_id, process_info in self.active_processes.items():
                    processing_time = current_time - process_info['start_time']
                    
                    if processing_time > self.max_processing_time * 1.5:  # 50% grace period
                        stale_processes.append(process_id)
                
                for process_id in stale_processes:
                    logger.warning(f"Cleaning up stale process: {process_id}")
                    del self.active_processes[process_id]
                
                return len(stale_processes)
                
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return 0
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource monitoring statistics"""
        try:
            with self.lock:
                current_time = time.time()
                active_count = len(self.active_processes)
                
                # Calculate average processing time for active processes
                if active_count > 0:
                    total_time = sum(
                        current_time - info['start_time'] 
                        for info in self.active_processes.values()
                    )
                    avg_processing_time = total_time / active_count
                else:
                    avg_processing_time = 0
                
                return {
                    'active_processes': active_count,
                    'max_concurrent': self.max_concurrent_processes,
                    'available_slots': self.max_concurrent_processes - active_count,
                    'average_processing_time': avg_processing_time,
                    'max_processing_time': self.max_processing_time
                }
                
        except Exception as e:
            logger.error(f"Resource stats error: {str(e)}")
            return {
                'error': str(e)
            }
