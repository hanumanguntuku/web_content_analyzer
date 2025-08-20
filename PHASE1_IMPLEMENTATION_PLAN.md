# Phase 1 Implementation Plan: Main Content Identification

## 🎯 Immediate Action Plan (Next 2 Weeks)

### Week 1: Foundation Setup
**Target**: Basic content identification working

#### Day 1-2: Environment Setup
```bash
# Add new dependencies to requirements.txt
pip install lxml cssselect readability-lxml python-dateutil langdetect
```

#### Day 3-5: Core Content Identifier
**File**: `backend/src/processors/content_identifier.py`

```python
from lxml import html, etree
from readability import Document
import re
from typing import Dict, List, Tuple

class ContentIdentifier:
    """Intelligent main content identification using multiple algorithms."""
    
    def __init__(self):
        self.content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '#content', '.post-content',
            '.entry-content', '.article-body'
        ]
        
        self.exclude_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.sidebar', '.navigation', '.menu',
            '.ads', '.advertisement', '.related',
            '.comments', '.social-share'
        ]
    
    def identify_main_content(self, html_content: str, url: str = None) -> Dict:
        """
        Identify main content using multiple algorithms and return best candidate.
        
        Returns:
            Dict with 'content', 'confidence', 'method', 'metadata'
        """
        results = []
        
        # Method 1: Readability.js algorithm
        readability_result = self._extract_with_readability(html_content)
        if readability_result:
            results.append({
                'content': readability_result['content'],
                'confidence': 0.9,
                'method': 'readability',
                'title': readability_result.get('title'),
                'score': readability_result.get('score', 0)
            })
        
        # Method 2: Semantic HTML detection
        semantic_result = self._extract_semantic_content(html_content)
        if semantic_result:
            results.append({
                'content': semantic_result['content'],
                'confidence': 0.8,
                'method': 'semantic',
                'element_type': semantic_result['element_type']
            })
        
        # Method 3: Content density analysis
        density_result = self._extract_by_density(html_content)
        if density_result:
            results.append({
                'content': density_result['content'],
                'confidence': 0.7,
                'method': 'density',
                'density_score': density_result['score']
            })
        
        # Return best result based on confidence and content length
        if results:
            best_result = max(results, key=lambda x: (x['confidence'], len(x['content'])))
            return best_result
        
        # Fallback: basic cleaning
        return self._basic_extraction(html_content)
    
    def _extract_with_readability(self, html_content: str) -> Dict:
        """Use readability algorithm for content extraction."""
        try:
            doc = Document(html_content)
            return {
                'content': doc.summary(),
                'title': doc.title(),
                'score': getattr(doc, 'score', 0)
            }
        except Exception as e:
            print(f"Readability extraction failed: {e}")
            return None
    
    def _extract_semantic_content(self, html_content: str) -> Dict:
        """Extract content using semantic HTML5 elements."""
        try:
            tree = html.fromstring(html_content)
            
            # Priority order for semantic elements
            semantic_elements = ['main', 'article', 'section[role="main"]']
            
            for selector in semantic_elements:
                elements = tree.cssselect(selector)
                if elements:
                    content = self._clean_element_text(elements[0])
                    if len(content.strip()) > 200:  # Minimum content threshold
                        return {
                            'content': content,
                            'element_type': selector
                        }
            return None
        except Exception as e:
            print(f"Semantic extraction failed: {e}")
            return None
    
    def _extract_by_density(self, html_content: str) -> Dict:
        """Extract content by analyzing text density in page sections."""
        try:
            tree = html.fromstring(html_content)
            
            # Remove unwanted elements first
            for selector in self.exclude_selectors:
                for elem in tree.cssselect(selector):
                    elem.getparent().remove(elem)
            
            # Find elements with high text density
            candidates = []
            for elem in tree.iter():
                if elem.tag in ['div', 'section', 'article', 'main']:
                    text = self._clean_element_text(elem)
                    if len(text) > 100:
                        # Calculate density score
                        html_length = len(etree.tostring(elem, encoding='unicode'))
                        text_length = len(text)
                        density = text_length / html_length if html_length > 0 else 0
                        
                        candidates.append({
                            'content': text,
                            'score': density,
                            'length': text_length
                        })
            
            # Return highest scoring candidate
            if candidates:
                best = max(candidates, key=lambda x: x['score'] * x['length'])
                return {
                    'content': best['content'],
                    'score': best['score']
                }
            return None
        except Exception as e:
            print(f"Density extraction failed: {e}")
            return None
    
    def _basic_extraction(self, html_content: str) -> Dict:
        """Fallback basic extraction method."""
        try:
            tree = html.fromstring(html_content)
            
            # Remove unwanted elements
            for selector in self.exclude_selectors:
                for elem in tree.cssselect(selector):
                    if elem.getparent() is not None:
                        elem.getparent().remove(elem)
            
            content = self._clean_element_text(tree)
            return {
                'content': content,
                'confidence': 0.5,
                'method': 'basic'
            }
        except Exception:
            return {
                'content': '',
                'confidence': 0.1,
                'method': 'failed'
            }
    
    def _clean_element_text(self, element) -> str:
        """Extract and clean text from an element."""
        if element is None:
            return ''
        
        # Get text content
        text = element.text_content()
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
```

#### Day 6-7: Integration & Testing
**File**: `backend/src/scrapers/enhanced_content_extractor.py`

```python
from .content_extractor import ContentExtractor
from ..processors.content_identifier import ContentIdentifier
from ..models.data_models import ScrapeResult
import logging

logger = logging.getLogger(__name__)

class EnhancedContentExtractor(ContentExtractor):
    """Enhanced content extractor with intelligent content identification."""
    
    def __init__(self):
        super().__init__()
        self.content_identifier = ContentIdentifier()
    
    def extract_content(self, html_content: str, url: str = None) -> dict:
        """Extract content using intelligent identification algorithms."""
        try:
            # Use intelligent content identification
            content_result = self.content_identifier.identify_main_content(html_content, url)
            
            # Get basic metadata
            soup = self._get_soup(html_content)
            basic_metadata = self._extract_basic_metadata(soup)
            
            return {
                'content': content_result.get('content', ''),
                'extraction_method': content_result.get('method', 'unknown'),
                'confidence': content_result.get('confidence', 0.0),
                'title': content_result.get('title') or basic_metadata.get('title'),
                'word_count': len(content_result.get('content', '').split()),
                'metadata': basic_metadata
            }
            
        except Exception as e:
            logger.error(f"Enhanced content extraction failed: {e}")
            # Fallback to basic extraction
            return super().extract_content(html_content)
    
    def _extract_basic_metadata(self, soup) -> dict:
        """Extract basic metadata from HTML."""
        metadata = {}
        
        # Title extraction (multiple sources)
        title_sources = [
            soup.find('title'),
            soup.find('meta', {'property': 'og:title'}),
            soup.find('meta', {'name': 'twitter:title'}),
            soup.find('h1')
        ]
        
        for source in title_sources:
            if source:
                metadata['title'] = source.get('content') or source.get_text()
                break
        
        # Description extraction
        desc_elem = soup.find('meta', {'name': 'description'}) or \
                   soup.find('meta', {'property': 'og:description'})
        if desc_elem:
            metadata['description'] = desc_elem.get('content')
        
        # Language detection
        lang_elem = soup.find('html')
        if lang_elem and lang_elem.get('lang'):
            metadata['language'] = lang_elem.get('lang')
        
        return metadata
```

### Week 2: Enhancement & Validation
**Target**: Working on 5+ major news sites with >80% accuracy

#### Day 8-10: Update Service Integration
**File**: `backend/src/services/scraping_service.py`

```python
# Update to use enhanced extractor
from ..scrapers.enhanced_content_extractor import EnhancedContentExtractor

class WebScraperService:
    def __init__(self):
        self.scraper = WebScraper()
        self.extractor = EnhancedContentExtractor()  # Use enhanced version
        
    async def scrape_and_extract(self, url: str) -> ScrapeResult:
        """Enhanced scraping with intelligent content extraction."""
        scrape_data = await self.scraper.scrape(url)
        
        if scrape_data.success:
            # Use enhanced extraction
            extraction_result = self.extractor.extract_content(
                scrape_data.text, 
                url
            )
            
            # Update scrape result with enhanced data
            scrape_data.text = extraction_result['content']
            scrape_data.extraction_metadata = {
                'method': extraction_result['extraction_method'],
                'confidence': extraction_result['confidence'],
                'word_count': extraction_result['word_count'],
                'title': extraction_result.get('title'),
                'description': extraction_result.get('metadata', {}).get('description')
            }
        
        return scrape_data
```

#### Day 11-12: Testing Suite
**File**: `backend/tests/test_content_identification.py`

```python
import pytest
from src.processors.content_identifier import ContentIdentifier

class TestContentIdentification:
    def setup_method(self):
        self.identifier = ContentIdentifier()
    
    def test_news_article_identification(self):
        """Test with typical news article HTML."""
        html = """
        <html>
        <body>
            <header>Site Navigation</header>
            <aside>Advertisement</aside>
            <main>
                <article>
                    <h1>Breaking News: Important Event</h1>
                    <p>This is the main content of the article. It contains
                    important information that users want to read. The content
                    is substantial and meaningful.</p>
                    <p>Another paragraph of important content that adds value
                    and context to the main story.</p>
                </article>
            </main>
            <footer>Copyright information</footer>
        </body>
        </html>
        """
        
        result = self.identifier.identify_main_content(html)
        assert result['confidence'] > 0.7
        assert 'Breaking News' in result['content']
        assert 'main content' in result['content']
        assert 'Navigation' not in result['content']
    
    def test_blog_post_identification(self):
        """Test with typical blog post structure."""
        # Similar test for blog posts
        pass
    
    def test_minimal_content_handling(self):
        """Test handling of pages with minimal content."""
        # Test edge cases
        pass
```

#### Day 13-14: Performance Testing & Optimization
```python
# Performance benchmarks
def test_extraction_speed():
    """Ensure extraction completes within performance targets."""
    start_time = time.time()
    result = identifier.identify_main_content(large_html_content)
    duration = time.time() - start_time
    assert duration < 3.0  # Must complete within 3 seconds
```

## 🎯 Success Criteria for Week 2

1. ✅ **Accuracy Target**: >80% correct content identification on test sites
2. ✅ **Performance Target**: <3 seconds extraction time per page
3. ✅ **Coverage Target**: Works on CNN, BBC, TechCrunch, Medium, Wikipedia
4. ✅ **Integration**: Seamlessly replaces basic extractor in existing pipeline
5. ✅ **Testing**: Complete test suite with >90% code coverage

## 📊 Test Sites for Validation

| Site | Content Type | Expected Challenge | Priority |
|------|--------------|-------------------|----------|
| CNN.com | News Article | Ads, related articles | HIGH |
| BBC.com | News Article | Complex navigation | HIGH |
| TechCrunch | Tech Blog | Sidebar content | HIGH |
| Medium.com | Blog Post | Recommendations | MEDIUM |
| Wikipedia | Encyclopedia | Infoboxes, references | MEDIUM |
| Reddit | Discussion | Comments, sidebar | LOW |

## 🚀 Quick Implementation Commands

```bash
# 1. Add dependencies
cd backend
pip install lxml cssselect readability-lxml python-dateutil

# 2. Create new files
touch src/processors/content_identifier.py
touch src/scrapers/enhanced_content_extractor.py
touch tests/test_content_identification.py

# 3. Run tests
pytest tests/test_content_identification.py -v

# 4. Test with sample sites
python -c "
from src.processors.content_identifier import ContentIdentifier
import requests
ci = ContentIdentifier()
html = requests.get('https://www.bbc.com/news').text
result = ci.identify_main_content(html)
print(f'Method: {result[\"method\"]}, Confidence: {result[\"confidence\"]}')
"
```

This Phase 1 implementation will establish the foundation for intelligent content extraction and provide immediate improvements to your content analysis platform.
