"""
Web Scraper Service Core - M1-DATA-01 Implementation
High-performance async web scraping with anti-detection measures
"""
import aiohttp
import asyncio
import random
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
from ..models.data_models import ScrapedContent
from ..utils.exceptions import ScrapingException
from .robots_parser import RobotsParser

logger = logging.getLogger(__name__)

class WebScraperService:
    """High-performance web scraping service with anti-detection"""
    
    def __init__(self):
        """Initialize web scraper with anti-detection measures and persistent session"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.session = None
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_content_size = 10 * 1024 * 1024  # 10MB limit
        self._ensure_session()

    def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30, connect=10),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
            )
        
    async def close(self):
        """Close the aiohttp session (call on app shutdown)"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def scrape_website(self, url: str) -> ScrapedContent:
        """
        Scrape content from URL with comprehensive error handling
        
        Args:
            url: Target URL to scrape
            
        Returns:
            ScrapedContent object with extracted content and metadata
            
        Raises:
            ScrapingException: When scraping fails
        """
        # --- robots.txt enforcement ---
        """ parsed = urlparse(url)
        robots = RobotsParser(user_agent=random.choice(self.user_agents))
        await robots.fetch_robots(f"{parsed.scheme}://{parsed.netloc}")
        if not robots.is_allowed(url):
            raise ScrapingException(f"Crawling disallowed by robots.txt for {url}", error_type="BLOCKED_BY_ROBOTS")
        crawl_delay = robots.get_crawl_delay() """
    
        crawl_delay=0

        if crawl_delay > 0:
            await asyncio.sleep(crawl_delay)

        self._ensure_session()
        return await self._scrape_with_retries(url)
            
    async def _scrape_with_retries(self, url: str) -> ScrapedContent:
        """Scrape URL with retry logic and exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{self.max_retries} for {url}")
                
                # Random delay for anti-detection
                if attempt > 0:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                
                return await self._perform_scrape(url)
                
            except ScrapingException as e:
                last_exception = e
                logger.warning(f"Scraping attempt {attempt + 1} failed for {url}: {str(e)}")
                
                # Don't retry for certain error types
                if e.error_type in ['BLOCKED_DOMAIN', 'INVALID_URL', 'CONTENT_TOO_LARGE']:
                    break
                    
        # All retries failed
        raise last_exception or ScrapingException(
            f"Failed to scrape {url} after {self.max_retries} attempts"
        )
        
    async def _perform_scrape(self, url: str) -> ScrapedContent:
        """Perform single scraping attempt"""
        start_time = time.time()
        
        try:
            # Prepare headers with random user agent
            headers = self._get_headers()
            
            logger.debug(f"Making request to {url} with headers: {headers}")
            
            # Make HTTP request
            async with self.session.get(url, headers=headers) as response:
                # Check response status
                if response.status == 403:
                    raise ScrapingException(
                        f"Access denied (403) for {url}",
                        error_type='ACCESS_DENIED'
                    )
                elif response.status == 404:
                    raise ScrapingException(
                        f"Page not found (404) for {url}",
                        error_type='NOT_FOUND'
                    )
                elif response.status >= 400:
                    raise ScrapingException(
                        f"HTTP error {response.status} for {url}",
                        error_type='HTTP_ERROR'
                    )
                
                # Check content length
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_content_size:
                    raise ScrapingException(
                        f"Content too large: {content_length} bytes",
                        error_type='CONTENT_TOO_LARGE'
                    )
                
                # Read content with size limit
                content = await self._read_content_safely(response)
                
                # Parse metadata
                metadata = self._extract_metadata(response, url, content)
                
                processing_time = time.time() - start_time
                
                logger.info(f"Successfully scraped {url} in {processing_time:.2f}s")
                
                # Use content_type from header, fallback to 'text/html'
                content_type = response.headers.get('content-type') or 'text/html'
                return ScrapedContent(
                    url=url,
                    title=metadata.get('title', ''),
                    description=metadata.get('description', ''),
                    content=content,
                    headings={},  # Will be filled by content extractor
                    links=[],     # Will be filled by content extractor
                    images=[],    # Will be filled by content extractor
                    meta_data=metadata,
                    word_count=len(content.split()),
                    page_size=len(content.encode('utf-8')),
                    load_time=processing_time,
                    status_code=response.status,
                    content_type=content_type,
                    language=None,  # Will be detected later
                    emails=[],      # Will be extracted later
                    phones=[],      # Will be extracted later
                    success=True,
                    error=None
                )
                
        except aiohttp.ClientError as e:
            raise ScrapingException(
                f"Network error scraping {url}: {str(e)}",
                error_type='NETWORK_ERROR'
            )
        except asyncio.TimeoutError:
            raise ScrapingException(
                f"Timeout scraping {url}",
                error_type='TIMEOUT'
            )
        except Exception as e:
            raise ScrapingException(
                f"Unexpected error scraping {url}: {str(e)}",
                error_type='UNKNOWN_ERROR'
            )
            
    async def _read_content_safely(self, response: aiohttp.ClientResponse) -> str:
        """Read response content with size limits"""
        content_chunks = []
        total_size = 0
        
        async for chunk in response.content.iter_chunked(8192):  # 8KB chunks
            total_size += len(chunk)
            
            if total_size > self.max_content_size:
                raise ScrapingException(
                    f"Content exceeds size limit: {total_size} bytes",
                    error_type='CONTENT_TOO_LARGE'
                )
                
            content_chunks.append(chunk)
            
        # Combine chunks and decode
        content_bytes = b''.join(content_chunks)
        
        # Try to decode with detected encoding
        encoding = response.charset or 'utf-8'
        try:
            return content_bytes.decode(encoding)
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            return content_bytes.decode('utf-8', errors='replace')
            
    def _get_headers(self) -> Dict[str, str]:
        """Generate realistic headers for scraping"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def _extract_metadata(self, response: aiohttp.ClientResponse, url: str, content: str = None) -> Dict[str, Any]:
        """Extract metadata from HTTP response and HTML content (for <title>)"""
        parsed_url = urlparse(url)
        title = ''
        if content:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            except Exception:
                pass
        content_type = response.headers.get('content-type') or 'text/html'
        return {
            'domain': parsed_url.netloc,
            'path': parsed_url.path,
            'protocol': parsed_url.scheme,
            'status_code': response.status,
            'content_type': content_type,
            'server': response.headers.get('server', ''),
            'encoding': response.charset or 'utf-8',
            'content_length': response.headers.get('content-length'),
            'last_modified': response.headers.get('last-modified'),
            'cache_control': response.headers.get('cache-control'),
            'final_url': str(response.url),  # Handle redirects
            'title': title
        }

# Convenience function for one-off scraping
async def scrape_url(url: str) -> ScrapedContent:
    """Convenience function to scrape a single URL"""
    async with WebScraperService() as scraper:
        return await scraper.scrape_url(url)
