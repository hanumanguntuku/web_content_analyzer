"""A reasonably robust web scraper using requests + BeautifulSoup.

Security & anti-detection notes:
- Uses rotating user-agents and sensible timeouts.
- Adds simple retry/backoff using urllib3 Retry.
- Respects max content size configured in settings.
- Does not execute JavaScript (design decision). For JS-heavy sites, use a headless browser component separately.
"""
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import brotli

# Simple settings for now - will make configurable later
class SimpleSettings:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36',
    ]
    REQUEST_TIMEOUT = 10
    MAX_CONTENT_BYTES = 5 * 1024 * 1024  # 5 MB

settings = SimpleSettings()
from .content_extractor import ContentExtractor

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.extractor = ContentExtractor()

    def _get_headers(self):
        ua = random.choice(settings.USER_AGENTS)
        return {
            'User-Agent': ua,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',  # Accept compression
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def fetch(self, url: str):
        # Simple anti-detection: random small sleep
        time.sleep(random.uniform(0.5, 1.5))
        
        # Don't use stream=True to avoid manual decompression issues
        resp = self.session.get(url, headers=self._get_headers(), timeout=settings.REQUEST_TIMEOUT)
        resp.raise_for_status()
        
        # Debug: Log response details
        print(f"DEBUG: Response encoding: {resp.encoding}")
        print(f"DEBUG: Content-Type: {resp.headers.get('content-type', 'unknown')}")
        print(f"DEBUG: Content-Encoding: {resp.headers.get('content-encoding', 'none')}")
        
        # Handle different content encodings manually if needed
        content_encoding = resp.headers.get('content-encoding', '').lower()
        
        if content_encoding == 'br':
            # Brotli compression - decompress manually
            try:
                html = brotli.decompress(resp.content).decode('utf-8', errors='replace')
                print("DEBUG: Successfully decompressed Brotli content")
            except Exception as e:
                print(f"DEBUG: Brotli decompression failed: {e}, falling back to resp.text")
                html = resp.text
        else:
            # Use resp.text which handles gzip/deflate automatically
            html = resp.text
        
        # Check if we got valid text (not binary data)
        if html and len(html) > 100:
            # Check first 100 chars to see if it looks like HTML
            preview = html[:100]
            print(f"DEBUG: Content preview: {preview}")
            if not any(char in preview for char in '<>'):
                print("WARNING: Content doesn't appear to be HTML!")
        
        # Check content length after decoding
        if len(html) > settings.MAX_CONTENT_BYTES // 2:  # Use char count, not byte count
            html = html[:settings.MAX_CONTENT_BYTES // 2]
            print(f"DEBUG: Truncated content to {len(html)} characters")
            
        final_url = resp.url
        return html, final_url

    def extract_content(self, html: str) -> str:
        return self.extractor.extract(html)
