"""
Content Extractor Engine - M1-DATA-02 Implementation
Intelligent content extraction with noise removal and main content identification
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import urljoin, urlparse
from ..models.data_models import ExtractedContent, ContentSection

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Intelligent content extraction engine"""
    
    def __init__(self):
        """Initialize content extractor with noise and content selectors"""
        # Common navigation and advertisement selectors to remove
        self.noise_selectors = [
            'nav', 'header', 'footer', 'aside', '.sidebar', '.navigation',
            '.ads', '.advertisement', '.social', '.comments', '.breadcrumb',
            'script', 'style', 'noscript', '.popup', '.modal', '.menu',
            '.widget', '.share', '.related', '.recommended', '.sponsored',
            '.cookie-notice', '.newsletter', '.subscription', '.promo'
        ]
        
        # Likely main content selectors (ordered by priority)
        self.content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.entry-content', '.article-body', '#content', '#main',
            '.blog-post', '.story-body', '.text-content', '.page-content'
        ]
        
        # CMS-specific content selectors
        self.cms_selectors = {
            'wordpress': ['.post', '.entry', '.single-post', '.blog-post'],
            'drupal': ['.node', '.article', '.page-content'],
            'joomla': ['.item-page', '.blog-item', '.article-content'],
            'squarespace': ['.blog-item-content', '.sqs-block-content'],
            'wix': ['.blog-post-content', '.page-content']
        }
        
        logger.info("ContentExtractor initialized with intelligent extraction patterns")
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> ExtractedContent:
        """Extract meaningful content from HTML soup"""
        try:
            logger.info(f"Starting content extraction for {url}")
            
            # Create working copy
            working_soup = BeautifulSoup(str(soup), 'html.parser')
            
            # Remove noise elements
            cleaned_soup = self._remove_noise(working_soup)
            
            # Extract main content with multiple strategies
            main_content = self._extract_main_content(cleaned_soup)
            
            # Extract structured data
            headings = self._extract_headings(cleaned_soup)
            links = self._extract_links(cleaned_soup, url)
            images = self._extract_images(cleaned_soup, url)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)  # Use original soup for metadata
            
            # Identify content sections
            sections = self._identify_sections(cleaned_soup)
            
            # Calculate content metrics
            word_count = len(main_content.split()) if main_content else 0
            
            extracted = ExtractedContent(
                url=url,
                main_content=main_content,
                headings=headings,
                links=links,
                images=images,
                metadata=metadata,
                word_count=word_count,
                sections=sections,
                extraction_quality=self._calculate_quality_score(main_content, headings, links)
            )
            
            logger.info(f"Extracted {word_count} words from {url} with quality score {extracted.extraction_quality:.2f}")
            return extracted
            
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {str(e)}")
            raise
    
    def _remove_noise(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove navigation, ads, and other noise elements"""
        logger.debug("Removing noise elements from content")
        
        # Remove elements by selectors
        for selector in self.noise_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        # Remove elements with noise-indicating attributes
        noise_attrs = [
            ('class', ['nav', 'menu', 'sidebar', 'ad', 'advertisement', 'social']),
            ('id', ['nav', 'menu', 'sidebar', 'footer', 'header']),
            ('role', ['navigation', 'banner', 'complementary'])
        ]
        
        for attr_name, attr_values in noise_attrs:
            for value in attr_values:
                elements = soup.find_all(attrs={attr_name: lambda x: x and value in str(x).lower()})
                for element in elements:
                    element.decompose()
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True) and not element.find('img'):
                element.decompose()
        
        logger.debug(f"Noise removal complete, remaining content size: {len(soup.get_text())}")
        return soup
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content text using multiple strategies"""
        logger.debug("Extracting main content using intelligent selectors")
        
        # Strategy 1: Try specific content selectors
        for selector in self.content_selectors:
            elements = soup.select(selector)
            if elements:
                # Use the element with most text content
                content_element = max(elements, key=lambda x: len(x.get_text()))
                content = self._clean_text(content_element.get_text())
                if self._is_substantial_content(content):
                    logger.debug(f"Found main content using selector: {selector}")
                    return content
        
        # Strategy 2: Try CMS-specific selectors
        for cms_name, selectors in self.cms_selectors.items():
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    content_element = max(elements, key=lambda x: len(x.get_text()))
                    content = self._clean_text(content_element.get_text())
                    if self._is_substantial_content(content):
                        logger.debug(f"Found main content using {cms_name} selector: {selector}")
                        return content
        
        # Strategy 3: Find largest content block
        all_divs = soup.find_all(['div', 'section', 'article'])
        if all_divs:
            content_div = max(all_divs, key=lambda x: len(x.get_text()))
            content = self._clean_text(content_div.get_text())
            if self._is_substantial_content(content):
                logger.debug("Found main content using largest content block strategy")
                return content
        
        # Strategy 4: Fallback to body content
        body = soup.find('body')
        if body:
            content = self._clean_text(body.get_text())
            logger.debug("Using body content as fallback")
            return content
        
        # Strategy 5: Last resort - all text
        content = self._clean_text(soup.get_text())
        logger.debug("Using all text content as last resort")
        return content
    
    def _is_substantial_content(self, content: str) -> bool:
        """Check if content is substantial enough to be main content"""
        if not content:
            return False
        
        word_count = len(content.split())
        return word_count >= 50  # Minimum 50 words for substantial content
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common boilerplate phrases
        boilerplate_patterns = [
            r'cookie policy',
            r'privacy policy', 
            r'terms of service',
            r'subscribe to newsletter',
            r'follow us on',
            r'share this article',
            r'advertisement',
            r'sponsored content',
            r'related articles',
            r'you might also like'
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces again after cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract heading hierarchy"""
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in range(1, 7):
            tag_name = f'h{level}'
            heading_elements = soup.find_all(tag_name)
            for heading in heading_elements:
                text = self._clean_text(heading.get_text())
                if text and len(text) <= 200:  # Reasonable heading length
                    headings[tag_name].append(text)
        
        logger.debug(f"Extracted {sum(len(h) for h in headings.values())} headings")
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract and categorize links"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = self._clean_text(link.get_text())
            
            if not text or not href:
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Categorize link
            link_type = self._categorize_link(absolute_url, base_url)
            
            links.append({
                'text': text,
                'url': absolute_url,
                'type': link_type,
                'internal': urlparse(absolute_url).netloc == urlparse(base_url).netloc
            })
        
        logger.debug(f"Extracted {len(links)} links")
        return links
    
    def _categorize_link(self, url: str, base_url: str) -> str:
        """Categorize link based on URL patterns"""
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in ['mailto:', 'tel:']):
            return 'contact'
        elif any(pattern in url_lower for pattern in ['facebook', 'twitter', 'linkedin', 'instagram']):
            return 'social'
        elif any(pattern in url_lower for pattern in ['.pdf', '.doc', '.xls', '.zip']):
            return 'download'
        elif urlparse(url).netloc != urlparse(base_url).netloc:
            return 'external'
        else:
            return 'internal'
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract images with metadata"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            
            # Convert to absolute URL
            absolute_src = urljoin(base_url, src)
            
            images.append({
                'src': absolute_src,
                'alt': img.get('alt', '').strip(),
                'title': img.get('title', '').strip(),
                'width': img.get('width'),
                'height': img.get('height'),
                'type': self._categorize_image(absolute_src)
            })
        
        logger.debug(f"Extracted {len(images)} images")
        return images
    
    def _categorize_image(self, src: str) -> str:
        """Categorize image based on URL patterns"""
        src_lower = src.lower()
        
        if any(pattern in src_lower for pattern in ['logo', 'brand']):
            return 'logo'
        elif any(pattern in src_lower for pattern in ['icon', 'ico']):
            return 'icon'
        elif any(pattern in src_lower for pattern in ['banner', 'hero']):
            return 'banner'
        elif any(pattern in src_lower for pattern in ['thumb', 'preview']):
            return 'thumbnail'
        else:
            return 'content'
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive metadata, including JSON-LD and microdata"""
        metadata = {}
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                metadata[f'og_{prop}'] = content
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                metadata[f'twitter_{name}'] = content
        # Standard meta tags
        standard_tags = ['keywords', 'author', 'viewport', 'robots', 'generator']
        for tag_name in standard_tags:
            tag = soup.find('meta', attrs={'name': tag_name})
            if tag:
                metadata[tag_name] = tag.get('content', '')
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata['canonical_url'] = canonical.get('href', '')
        # Language detection
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']

        # --- JSON-LD extraction ---
        jsonld_blocks = soup.find_all('script', type='application/ld+json')
        jsonld_data = []
        import json
        for block in jsonld_blocks:
            try:
                data = json.loads(block.string)
                jsonld_data.append(data)
            except Exception:
                continue
        if jsonld_data:
            metadata['jsonld'] = jsonld_data

        # --- Microdata extraction (basic) ---
        microdata_items = []
        for item in soup.find_all(attrs={"itemscope": True}):
            itemtype = item.get('itemtype', '')
            properties = {}
            for prop in item.find_all(attrs={"itemprop": True}):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text(strip=True)
                properties[prop_name] = prop_value
            microdata_items.append({"type": itemtype, "properties": properties})
        if microdata_items:
            metadata['microdata'] = microdata_items

        logger.debug(f"Extracted {len(metadata)} metadata items (including structured data)")
        return metadata
    
    def _identify_sections(self, soup: BeautifulSoup) -> List[ContentSection]:
        """Identify different content sections"""
        sections = []
        
        # Look for semantic sections
        semantic_elements = soup.find_all(['section', 'article', 'div'], 
                                        class_=lambda x: x and any(term in str(x).lower() 
                                        for term in ['section', 'content', 'block', 'part']))
        
        for element in semantic_elements:
            text = self._clean_text(element.get_text())
            if self._is_substantial_content(text):
                # Try to identify section type
                section_type = self._identify_section_type(element)
                
                sections.append(ContentSection(
                    type=section_type,
                    content=text,
                    word_count=len(text.split()),
                    headings=self._extract_headings(element)
                ))
        
        logger.debug(f"Identified {len(sections)} content sections")
        return sections
    
    def _identify_section_type(self, element: Tag) -> str:
        """Identify the type of content section"""
        classes = element.get('class', [])
        class_str = ' '.join(classes).lower() if classes else ''
        
        if any(term in class_str for term in ['intro', 'summary', 'abstract']):
            return 'introduction'
        elif any(term in class_str for term in ['conclusion', 'summary', 'end']):
            return 'conclusion'
        elif any(term in class_str for term in ['list', 'items', 'bullet']):
            return 'list'
        elif any(term in class_str for term in ['quote', 'blockquote', 'citation']):
            return 'quote'
        else:
            return 'paragraph'
    
    def _calculate_quality_score(self, content: str, headings: Dict[str, List[str]], 
                               links: List[Dict[str, Any]]) -> float:
        """Calculate content extraction quality score"""
        score = 0.0
        
        # Content length score (0-40 points)
        if content:
            word_count = len(content.split())
            if word_count >= 100:
                score += 40
            elif word_count >= 50:
                score += 20
            elif word_count >= 20:
                score += 10
        
        # Heading structure score (0-30 points)
        total_headings = sum(len(h) for h in headings.values())
        if total_headings >= 3:
            score += 30
        elif total_headings >= 1:
            score += 15
        
        # Link quality score (0-20 points)
        if links:
            internal_links = sum(1 for link in links if link.get('internal'))
            if internal_links >= 3:
                score += 20
            elif internal_links >= 1:
                score += 10
        
        # Content diversity score (0-10 points)
        if content and any(headings.values()) and links:
            score += 10
        
        return min(score, 100.0)  # Cap at 100
