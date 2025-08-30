"""
Web Scraper Service - M1-DATA-01 Implementation
Robust web scraping with BeautifulSoup, user-agent rotation, and anti-detection measures
"""
import asyncio
import aiohttp
import logging
import random
import time
from typing import Dict, Any, List, Optional, NamedTuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Data structure for scraped web content"""
    url: str
    title: str
    description: str
    content: str
    headings: Dict[str, List[str]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    meta_data: Dict[str, Any]
    word_count: int
    page_size: int
    load_time: float
    status_code: int
    content_type: str
    language: Optional[str] = None
    emails: List[str] = None
    phones: List[str] = None

class WebScraperService:
    """Robust web scraper with anti-detection and security features"""
    
    def __init__(self):
        """Initialize scraper with proper headers and session management"""
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0  # Minimum delay between requests (seconds)
        
        # Content validation settings
        self.max_content_size = 10 * 1024 * 1024  # 10MB limit
        self.allowed_content_types = [
            'text/html',
            'application/xhtml+xml',
            'application/xml',
            'text/xml'
        ]
        
        logger.info("WebScraperService initialized with anti-detection measures")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with proper configuration"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_random_headers()
            )
        
        return self.session
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers with user-agent rotation"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _validate_url(self, url: str) -> bool:
        """Security validation to prevent SSRF attacks"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Invalid scheme: {parsed.scheme}")
                return False
            
            # Check for localhost/private IPs
            hostname = parsed.hostname
            if not hostname:
                return False
                
            # Block localhost and private networks
            private_patterns = [
                'localhost', '127.', '10.', '192.168.',
                '172.16.', '172.17.', '172.18.', '172.19.',
                '172.20.', '172.21.', '172.22.', '172.23.',
                '172.24.', '172.25.', '172.26.', '172.27.',
                '172.28.', '172.29.', '172.30.', '172.31.',
                '0.0.0.0', '::1'
            ]
            
            hostname_lower = hostname.lower()
            for pattern in private_patterns:
                if hostname_lower.startswith(pattern):
                    logger.warning(f"Blocked private/local address: {hostname}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def _validate_content_type(self, content_type: str) -> bool:
        """Validate content type to ensure it's HTML/XML"""
        if not content_type:
            return False
        
        content_type_lower = content_type.lower()
        return any(allowed in content_type_lower for allowed in self.allowed_content_types)
    
    async def _rate_limit(self):
        """Implement respectful crawling with rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def scrape_url(self, url: str) -> ScrapedContent:
        """
        Main scraping method with comprehensive content extraction
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent: Extracted content and metadata
            
        Raises:
            ValueError: For invalid URLs or security violations
            aiohttp.ClientError: For network/HTTP errors
        """
        start_time = time.time()
        
        # Security validation
        if not self._validate_url(url):
            raise ValueError(f"URL failed security validation: {url}")
        
        # Rate limiting
        await self._rate_limit()
        
        session = await self._get_session()
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Make request with retry logic
            response = await self._fetch_with_retry(session, url)
            
            # Validate content type
            content_type = response.headers.get('content-type', '')
            if not self._validate_content_type(content_type):
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_size:
                raise ValueError(f"Content too large: {content_length} bytes")
            
            # Read content with size limit
            content_bytes = await self._read_content_safely(response)
            content_text = content_bytes.decode('utf-8', errors='ignore')
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content_text, 'lxml')
            
            # Extract content
            scraped_content = await self._extract_content(
                soup, url, response.status, content_type, 
                len(content_bytes), time.time() - start_time
            )
            
            logger.info(f"Successfully scraped {url}: {scraped_content.word_count} words")
            return scraped_content
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            raise
    
    async def _fetch_with_retry(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> aiohttp.ClientResponse:
        """Fetch URL with retry logic and exponential backoff"""
        for attempt in range(max_retries + 1):
            try:
                # Rotate headers for each attempt
                headers = self._get_random_headers()
                
                async with session.get(url, headers=headers) as response:
                    # Check for successful status codes
                    if response.status == 200:
                        return response
                    elif response.status in [403, 429]:  # Rate limited or forbidden
                        if attempt < max_retries:
                            wait_time = (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"Status {response.status}, retrying in {wait_time:.2f}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    response.raise_for_status()
                    
            except aiohttp.ClientError as e:
                if attempt == max_retries:
                    raise
                
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time:.2f}s: {e}")
                await asyncio.sleep(wait_time)
        
        raise aiohttp.ClientError(f"Failed to fetch {url} after {max_retries + 1} attempts")
    
    async def _read_content_safely(self, response: aiohttp.ClientResponse) -> bytes:
        """Read response content with size limit"""
        content = b''
        async for chunk in response.content.iter_chunked(8192):
            content += chunk
            if len(content) > self.max_content_size:
                raise ValueError(f"Content exceeds size limit: {len(content)} bytes")
        return content
    
    async def _extract_content(self, soup: BeautifulSoup, url: str, status_code: int, 
                             content_type: str, page_size: int, load_time: float) -> ScrapedContent:
        """Extract comprehensive content from parsed HTML"""
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No title'
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Extract main content (remove script, style, nav, footer, etc.)
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Get main content
        main_content = ''
        content_selectors = ['main', 'article', '.content', '#content', '.post', '.entry']
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator=' ', strip=True)
                break
        
        # Fallback to body content
        if not main_content:
            body = soup.find('body')
            main_content = body.get_text(separator=' ', strip=True) if body else soup.get_text(separator=' ', strip=True)
        
        # Extract headings
        headings = {
            'h1': [h.get_text().strip() for h in soup.find_all('h1')],
            'h2': [h.get_text().strip() for h in soup.find_all('h2')],
            'h3': [h.get_text().strip() for h in soup.find_all('h3')],
            'h4': [h.get_text().strip() for h in soup.find_all('h4')],
            'h5': [h.get_text().strip() for h in soup.find_all('h5')],
            'h6': [h.get_text().strip() for h in soup.find_all('h6')]
        }
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            if text and href:
                absolute_url = urljoin(url, href)
                links.append({
                    'text': text,
                    'url': absolute_url,
                    'internal': urlparse(absolute_url).netloc == urlparse(url).netloc
                })
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '').strip()
            absolute_src = urljoin(url, src)
            images.append({
                'src': absolute_src,
                'alt': alt,
                'title': img.get('title', '').strip()
            })
        
        # Extract emails and phone numbers
        emails = self._extract_emails(main_content)
        phones = self._extract_phones(main_content)
        
        # Extract metadata
        meta_data = self._extract_meta_data(soup)
        
        # Calculate word count
        word_count = len(main_content.split())
        
        # Detect language
        language = self._detect_language(soup)
        
        return ScrapedContent(
            url=url,
            title=title,
            description=description,
            content=main_content,
            headings=headings,
            links=links,
            images=images,
            meta_data=meta_data,
            word_count=word_count,
            page_size=page_size,
            load_time=load_time,
            status_code=status_code,
            content_type=content_type,
            language=language,
            emails=emails,
            phones=phones
        )
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\+?1?\d{9,15}',  # International format
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # US format (123) 456-7890
            r'\d{3}-\d{3}-\d{4}',  # US format 123-456-7890
            r'\d{3}\.\d{3}\.\d{4}',  # US format 123.456.7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))  # Remove duplicates
    
    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML head"""
        meta_data = {}
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                meta_data[f'og_{prop}'] = content
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                meta_data[f'twitter_{name}'] = content
        
        # Standard meta tags
        standard_tags = ['keywords', 'author', 'viewport', 'robots']
        for tag_name in standard_tags:
            tag = soup.find('meta', attrs={'name': tag_name})
            if tag:
                meta_data[tag_name] = tag.get('content', '')
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            meta_data['canonical_url'] = canonical.get('href', '')
        
        return meta_data
    
    def _detect_language(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect page language from HTML attributes"""
        # Check html lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang']
        
        # Check meta language
        lang_meta = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if lang_meta:
            return lang_meta.get('content', '')
        
        return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("WebScraperService session closed")

# Compatibility wrapper for existing API
class ScrapingService:
    """Service wrapper that uses WebScraperService for analysis"""
    
    def __init__(self):
        self.scraper = WebScraperService()
        logger.info("ScrapingService initialized with WebScraperService")
    
    async def analyze_url(self, url: str) -> dict:
        """Analyze URL using WebScraperService"""
        try:
            scraped_content = await self.scraper.scrape_url(url)
            
            # Convert to dict format for API response
            return {
                "status": "success",
                "url": scraped_content.url,
                "title": scraped_content.title,
                "description": scraped_content.description,
                "word_count": scraped_content.word_count,
                "page_size": scraped_content.page_size,
                "load_time": scraped_content.load_time,
                "status_code": scraped_content.status_code,
                "content_type": scraped_content.content_type,
                "language": scraped_content.language,
                "headings": scraped_content.headings,
                "links": len(scraped_content.links),
                "images": len(scraped_content.images),
                "emails": scraped_content.emails,
                "phones": scraped_content.phones,
                "meta_data": scraped_content.meta_data,
                "content_preview": scraped_content.content[:500] + "..." if len(scraped_content.content) > 500 else scraped_content.content
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def close(self):
        """Close the scraper service"""
        await self.scraper.close()
