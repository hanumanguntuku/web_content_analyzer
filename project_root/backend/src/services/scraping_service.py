import asyncio
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
from ..models.data_models import ScrapedContent, ScrapeResult
from ..scrapers.content_extractor import ContentExtractor
from ..scrapers.enhanced_content_extractor import EnhancedContentExtractor
from ..utils.validators import validate_url
from ..utils.security import sanitize_text

# Configuration settings
class ScrapingSettings:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
    ]
    REQUEST_TIMEOUT = 10
    MAX_CONTENT_BYTES = 5 * 1024 * 1024  # 5 MB

class WebScraperService:
    """Professional web scraping service with security and anti-detection features"""
    
    def __init__(self):
        """Initialize session with proper headers and configuration"""
        self.session = requests.Session()
        self.content_extractor = EnhancedContentExtractor()  # Use enhanced extractor
        self.settings = ScrapingSettings()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        # Mount adapters with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    async def scrape_url(self, url: str) -> ScrapedContent:
        """
        Safe content extraction with comprehensive error handling
        
        Args:
            url: The URL to scrape
            
        Returns:
            ScrapedContent: Structured content data with metadata
        """
        # Validate URL first
        if not self._validate_url(url):
            return ScrapedContent(
                url=url,
                final_url=url,
                html="",
                text="",
                content_length=0,
                success=False,
                error_message="Invalid or unsafe URL"
            )
        
        try:
            # Run scraping in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._scrape_sync, url)
            return result
            
        except Exception as e:
            return ScrapedContent(
                url=url,
                final_url=url,
                html="",
                text="",
                content_length=0,
                success=False,
                error_message=f"Scraping failed: {str(e)}"
            )
    
    def _validate_url(self, url: str) -> bool:
        """
        Security validation for URLs
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is safe to scrape
        """
        try:
            # Use existing validator
            if not validate_url(url):
                return False
            
            # Additional checks
            if not url.startswith(('http://', 'https://')):
                return False
                
            # Block potentially dangerous protocols
            dangerous_schemes = ['file://', 'ftp://', 'javascript:', 'data:']
            if any(url.startswith(scheme) for scheme in dangerous_schemes):
                return False
                
            return True
            
        except Exception:
            return False
    
    def _scrape_sync(self, url: str) -> ScrapedContent:
        """
        Synchronous scraping implementation
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent: Scraped content data
        """
        try:
            # Anti-detection: Random delay
            time.sleep(random.uniform(0.5, 1.5))
            
            # Get headers with rotated user agent
            headers = self._get_headers()
            
            # Make request
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.settings.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Handle content encoding and size limits
            html = self._process_response_content(response)
            
            # Extract content using enhanced extractor
            extraction_result = self.content_extractor.extract_content(html, url)
            
            # Sanitize extracted text
            clean_text = sanitize_text(extraction_result.get('content', ''))
            
            return ScrapedContent(
                url=url,
                final_url=str(response.url),
                html=html,
                text=clean_text,
                content_length=len(clean_text),
                success=True,
                # Add enhanced metadata to the result
                metadata=extraction_result.get('metadata', {}),
                extraction_method=extraction_result.get('extraction_method', 'unknown'),
                confidence=extraction_result.get('confidence', 0.0)
            )
            
        except requests.exceptions.RequestException as e:
            return ScrapedContent(
                url=url,
                final_url=url,
                html="",
                text="",
                content_length=0,
                success=False,
                error_message=f"Request failed: {str(e)}"
            )
        except Exception as e:
            return ScrapedContent(
                url=url,
                final_url=url,
                html="",
                text="",
                content_length=0,
                success=False,
                error_message=f"Processing failed: {str(e)}"
            )
    
    def _get_headers(self) -> dict:
        """
        Generate realistic headers with rotated user agent
        
        Returns:
            dict: HTTP headers
        """
        user_agent = random.choice(self.settings.USER_AGENTS)
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _process_response_content(self, response: requests.Response) -> str:
        """
        Process response content with encoding handling and size limits
        
        Args:
            response: HTTP response object
            
        Returns:
            str: Processed HTML content
        """
        # Check content length
        content_length = len(response.content)
        if content_length > self.settings.MAX_CONTENT_BYTES:
            # Truncate if too large
            html = response.text[:self.settings.MAX_CONTENT_BYTES // 2]
        else:
            # Handle different encodings
            content_encoding = response.headers.get('content-encoding', '').lower()
            
            if content_encoding == 'br':
                # Handle Brotli compression
                try:
                    import brotli
                    html = brotli.decompress(response.content).decode('utf-8', errors='replace')
                except Exception:
                    html = response.text
            else:
                # Let requests handle gzip/deflate automatically
                html = response.text
        
        return html


# Legacy function for backwards compatibility
async def scrape_url(url: str) -> ScrapeResult:
    """Legacy function - use WebScraperService.scrape_url() instead"""
    service = WebScraperService()
    result = await service.scrape_url(url)
    
    if result.success:
        return ScrapeResult(
            url=result.final_url,
            html=result.html,
            text=result.text
        )
    else:
        raise Exception(result.error_message or "Scraping failed")
