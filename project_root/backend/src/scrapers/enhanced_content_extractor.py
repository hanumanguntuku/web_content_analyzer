"""
Enhanced Content Extractor

This module provides intelligent content extraction using advanced algorithms
for main content identification and comprehensive metadata extraction.
"""

from .content_extractor import ContentExtractor
from ..processors.content_identifier import ContentIdentifier
from ..models.data_models import ScrapeResult
from bs4 import BeautifulSoup
import logging
import re
from typing import Dict, Optional, List
from datetime import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)


class EnhancedContentExtractor(ContentExtractor):
    """Enhanced content extractor with intelligent content identification."""
    
    def __init__(self):
        super().__init__()
        self.content_identifier = ContentIdentifier()
    
    def _get_soup(self, html_content: str) -> BeautifulSoup:
        """Get BeautifulSoup object from HTML content."""
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_content(self, html_content: str, url: str = None) -> Dict:
        """Extract content using intelligent identification algorithms."""
        try:
            # Use intelligent content identification
            content_result = self.content_identifier.identify_main_content(html_content, url)
            
            # Get comprehensive metadata
            soup = self._get_soup(html_content)
            metadata = self._extract_comprehensive_metadata(soup, url)
            
            # Detect language if not already specified
            if not metadata.get('language') and content_result.get('content'):
                metadata['language'] = self._detect_language(content_result['content'])
            
            return {
                'content': content_result.get('content', ''),
                'extraction_method': content_result.get('method', 'unknown'),
                'confidence': content_result.get('confidence', 0.0),
                'title': content_result.get('title') or metadata.get('title'),
                'word_count': content_result.get('word_count', 0),
                'metadata': metadata,
                'extraction_stats': {
                    'method': content_result.get('method'),
                    'confidence': content_result.get('confidence'),
                    'density_score': content_result.get('density_score'),
                    'element_type': content_result.get('element_type')
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced content extraction failed for URL {url}: {e}")
            # Fallback to basic extraction
            return self._fallback_extraction(html_content, url)
    
    def _extract_comprehensive_metadata(self, soup: BeautifulSoup, url: str = None) -> Dict:
        """Extract comprehensive metadata from HTML."""
        metadata = {}
        
        # Title extraction from multiple sources
        metadata['title'] = self._extract_title(soup)
        
        # Description extraction
        metadata['description'] = self._extract_description(soup)
        
        # Author information
        metadata['author'] = self._extract_author(soup)
        
        # Publication date
        metadata['publish_date'] = self._extract_publish_date(soup)
        
        # Language detection
        metadata['language'] = self._extract_language(soup)
        
        # Keywords
        metadata['keywords'] = self._extract_keywords(soup)
        
        # Canonical URL
        metadata['canonical_url'] = self._extract_canonical_url(soup, url)
        
        # Social media metadata
        metadata['social_meta'] = self._extract_social_metadata(soup)
        
        # Technical metadata
        metadata['technical'] = self._extract_technical_metadata(soup)
        
        return {k: v for k, v in metadata.items() if v is not None}
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title from multiple sources with priority."""
        title_sources = [
            # Priority 1: Open Graph title
            lambda: self._get_meta_content(soup, 'property', 'og:title'),
            # Priority 2: Twitter title
            lambda: self._get_meta_content(soup, 'name', 'twitter:title'),
            # Priority 3: HTML title tag
            lambda: soup.find('title').get_text().strip() if soup.find('title') else None,
            # Priority 4: First H1 tag
            lambda: soup.find('h1').get_text().strip() if soup.find('h1') else None,
            # Priority 5: JSON-LD title
            lambda: self._extract_json_ld_field(soup, 'headline') or self._extract_json_ld_field(soup, 'name')
        ]
        
        for source in title_sources:
            try:
                title = source()
                if title and len(title.strip()) > 0:
                    # Clean and validate title
                    title = re.sub(r'\s+', ' ', title.strip())
                    if len(title) <= 200:  # Reasonable title length
                        return title
            except Exception:
                continue
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from multiple sources."""
        description_sources = [
            # Priority 1: Meta description
            lambda: self._get_meta_content(soup, 'name', 'description'),
            # Priority 2: Open Graph description
            lambda: self._get_meta_content(soup, 'property', 'og:description'),
            # Priority 3: Twitter description
            lambda: self._get_meta_content(soup, 'name', 'twitter:description'),
            # Priority 4: JSON-LD description
            lambda: self._extract_json_ld_field(soup, 'description'),
            # Priority 5: First paragraph (if substantial)
            lambda: self._extract_first_paragraph(soup)
        ]
        
        for source in description_sources:
            try:
                description = source()
                if description and 50 <= len(description.strip()) <= 500:
                    return description.strip()
            except Exception:
                continue
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information."""
        author_sources = [
            # Meta author tag
            lambda: self._get_meta_content(soup, 'name', 'author'),
            # JSON-LD author
            lambda: self._extract_json_ld_author(soup),
            # Common author selectors
            lambda: self._extract_by_selectors(soup, [
                '.author', '.byline', '.author-name',
                '[rel="author"]', '.post-author',
                '.article-author', '.by-author'
            ]),
            # Microdata author
            lambda: self._extract_microdata_author(soup)
        ]
        
        for source in author_sources:
            try:
                author = source()
                if author and len(author.strip()) > 0:
                    return author.strip()
            except Exception:
                continue
        
        return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date."""
        date_sources = [
            # JSON-LD dates
            lambda: self._extract_json_ld_field(soup, 'datePublished'),
            lambda: self._extract_json_ld_field(soup, 'dateCreated'),
            # Meta tags
            lambda: self._get_meta_content(soup, 'property', 'article:published_time'),
            lambda: self._get_meta_content(soup, 'name', 'publish_date'),
            lambda: self._get_meta_content(soup, 'name', 'date'),
            # Time elements
            lambda: self._extract_time_element(soup),
            # Common date selectors
            lambda: self._extract_by_selectors(soup, [
                '.publish-date', '.date', '.published',
                '.post-date', '.article-date', '.timestamp'
            ])
        ]
        
        for source in date_sources:
            try:
                date_str = source()
                if date_str:
                    return self._normalize_date(date_str)
            except Exception:
                continue
        
        return None
    
    def _extract_language(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract language from HTML attributes."""
        try:
            # HTML lang attribute
            html_elem = soup.find('html')
            if html_elem and html_elem.get('lang'):
                return html_elem.get('lang')
            
            # Meta language
            lang = self._get_meta_content(soup, 'http-equiv', 'content-language')
            if lang:
                return lang
            
            # JSON-LD language
            lang = self._extract_json_ld_field(soup, 'inLanguage')
            if lang:
                return lang
            
        except Exception:
            pass
        
        return None
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags and content."""
        keywords = []
        
        try:
            # Meta keywords
            meta_keywords = self._get_meta_content(soup, 'name', 'keywords')
            if meta_keywords:
                keywords.extend([k.strip() for k in meta_keywords.split(',') if k.strip()])
            
            # JSON-LD keywords
            json_keywords = self._extract_json_ld_field(soup, 'keywords')
            if json_keywords:
                if isinstance(json_keywords, list):
                    keywords.extend(json_keywords)
                elif isinstance(json_keywords, str):
                    keywords.extend([k.strip() for k in json_keywords.split(',') if k.strip()])
            
            # Remove duplicates and limit
            return list(dict.fromkeys(keywords))[:10]  # Max 10 keywords
            
        except Exception:
            return []
    
    def _extract_canonical_url(self, soup: BeautifulSoup, url: str = None) -> Optional[str]:
        """Extract canonical URL."""
        try:
            canonical = soup.find('link', {'rel': 'canonical'})
            if canonical and canonical.get('href'):
                return canonical.get('href')
            
            # Open Graph URL
            og_url = self._get_meta_content(soup, 'property', 'og:url')
            if og_url:
                return og_url
            
            return url  # Fallback to provided URL
            
        except Exception:
            return url
    
    def _extract_social_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract Open Graph and Twitter Card metadata."""
        social_meta = {}
        
        try:
            # Open Graph
            og_fields = ['title', 'description', 'image', 'type', 'url', 'site_name']
            for field in og_fields:
                value = self._get_meta_content(soup, 'property', f'og:{field}')
                if value:
                    social_meta[f'og_{field}'] = value
            
            # Twitter Cards
            twitter_fields = ['card', 'title', 'description', 'image', 'site', 'creator']
            for field in twitter_fields:
                value = self._get_meta_content(soup, 'name', f'twitter:{field}')
                if value:
                    social_meta[f'twitter_{field}'] = value
                    
        except Exception:
            pass
        
        return social_meta
    
    def _extract_technical_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract technical metadata."""
        technical = {}
        
        try:
            # Charset
            charset = soup.find('meta', {'charset': True})
            if charset:
                technical['charset'] = charset.get('charset')
            
            # Viewport
            viewport = self._get_meta_content(soup, 'name', 'viewport')
            if viewport:
                technical['viewport'] = viewport
            
            # Generator
            generator = self._get_meta_content(soup, 'name', 'generator')
            if generator:
                technical['generator'] = generator
                
        except Exception:
            pass
        
        return technical
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of text content."""
        try:
            if text and len(text.strip()) > 50:  # Minimum text for reliable detection
                return detect(text)
        except (LangDetectException, Exception):
            pass
        return None
    
    def _get_meta_content(self, soup: BeautifulSoup, attr_name: str, attr_value: str) -> Optional[str]:
        """Helper to get meta tag content."""
        meta = soup.find('meta', {attr_name: attr_value})
        return meta.get('content') if meta else None
    
    def _extract_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using CSS selectors."""
        for selector in selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text().strip()
                    if text:
                        return text
            except Exception:
                continue
        return None
    
    def _extract_json_ld_field(self, soup: BeautifulSoup, field: str) -> Optional[str]:
        """Extract field from JSON-LD structured data."""
        try:
            import json
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and field in data:
                        return str(data[field])
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and field in item:
                                return str(item[field])
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception:
            pass
        return None
    
    def _extract_json_ld_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from JSON-LD."""
        try:
            import json
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    author = self._find_author_in_json_ld(data)
                    if author:
                        return author
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception:
            pass
        return None
    
    def _find_author_in_json_ld(self, data) -> Optional[str]:
        """Find author in JSON-LD data structure."""
        if isinstance(data, dict):
            if 'author' in data:
                author = data['author']
                if isinstance(author, str):
                    return author
                elif isinstance(author, dict) and 'name' in author:
                    return author['name']
                elif isinstance(author, list) and author:
                    first_author = author[0]
                    if isinstance(first_author, str):
                        return first_author
                    elif isinstance(first_author, dict) and 'name' in first_author:
                        return first_author['name']
        elif isinstance(data, list):
            for item in data:
                author = self._find_author_in_json_ld(item)
                if author:
                    return author
        return None
    
    def _extract_microdata_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from microdata."""
        try:
            author_elem = soup.find(attrs={'itemprop': 'author'})
            if author_elem:
                return author_elem.get_text().strip()
        except Exception:
            pass
        return None
    
    def _extract_time_element(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from time elements."""
        try:
            time_elem = soup.find('time', {'datetime': True})
            if time_elem:
                return time_elem.get('datetime')
        except Exception:
            pass
        return None
    
    def _extract_first_paragraph(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract first substantial paragraph as description."""
        try:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if 50 <= len(text) <= 300:  # Reasonable description length
                    return text
        except Exception:
            pass
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO format."""
        try:
            from dateutil import parser
            parsed_date = parser.parse(date_str)
            return parsed_date.isoformat()
        except Exception:
            return date_str  # Return original if parsing fails
    
    def _fallback_extraction(self, html_content: str, url: str = None) -> Dict:
        """Fallback to basic extraction if enhanced extraction fails."""
        try:
            basic_result = super().extract(html_content)  # Call parent's extract method
            soup = self._get_soup(html_content)
            
            return {
                'content': basic_result,
                'extraction_method': 'basic_fallback',
                'confidence': 0.3,
                'title': self._extract_title(soup),
                'word_count': len(basic_result.split()) if basic_result else 0,
                'metadata': {'extraction_note': 'Fallback method used due to extraction failure'},
                'extraction_stats': {
                    'method': 'basic_fallback',
                    'confidence': 0.3
                }
            }
        except Exception as e:
            logger.error(f"Fallback extraction also failed: {e}")
            return {
                'content': '',
                'extraction_method': 'failed',
                'confidence': 0.0,
                'title': None,
                'word_count': 0,
                'metadata': {'error': str(e)},
                'extraction_stats': {'method': 'failed', 'confidence': 0.0}
            }
