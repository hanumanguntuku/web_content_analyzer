"""
Intelligent Content Identification Module

This module provides advanced algorithms for identifying main content on web pages,
removing navigation, advertisements, and other non-content elements.
"""

from lxml import html, etree
from readability import Document
import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ContentIdentifier:
    """Intelligent main content identification using multiple algorithms."""
    
    def __init__(self):
        # Semantic selectors for main content (priority order)
        self.content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '#content', '.post-content',
            '.entry-content', '.article-body', '.story-body',
            '.post-body', '.article-content'
        ]
        
        # Elements to exclude from content extraction
        self.exclude_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.sidebar', '.navigation', '.menu', '.nav',
            '.ads', '.advertisement', '.ad', '.banner',
            '.related', '.recommended', '.suggestions',
            '.comments', '.comment', '.social-share',
            '.newsletter', '.subscription', '.popup',
            '.breadcrumb', '.breadcrumbs', '.tags',
            '.author-bio', '.bio', '.share', '.sharing'
        ]
        
        # Minimum content thresholds
        self.min_content_length = 100
        self.min_paragraph_count = 2
        self.max_link_density = 0.3  # Max ratio of link text to total text
    
    def identify_main_content(self, html_content: str, url: str = None) -> Dict:
        """
        Identify main content using multiple algorithms and return best candidate.
        
        Args:
            html_content: Raw HTML content of the page
            url: Optional URL for context (used in logging/debugging)
        
        Returns:
            Dict with 'content', 'confidence', 'method', 'metadata'
        """
        if not html_content or not html_content.strip():
            return self._empty_result()
        
        results = []
        
        try:
            # Method 1: Readability.js algorithm (highest priority)
            readability_result = self._extract_with_readability(html_content)
            if readability_result:
                results.append({
                    'content': readability_result['content'],
                    'confidence': 0.9,
                    'method': 'readability',
                    'title': readability_result.get('title'),
                    'score': readability_result.get('score', 0),
                    'word_count': len(readability_result['content'].split())
                })
            
            # Method 2: Semantic HTML detection
            semantic_result = self._extract_semantic_content(html_content)
            if semantic_result:
                results.append({
                    'content': semantic_result['content'],
                    'confidence': 0.8,
                    'method': 'semantic',
                    'element_type': semantic_result['element_type'],
                    'word_count': len(semantic_result['content'].split())
                })
            
            # Method 3: Content density analysis
            density_result = self._extract_by_density(html_content)
            if density_result:
                results.append({
                    'content': density_result['content'],
                    'confidence': 0.7,
                    'method': 'density',
                    'density_score': density_result['score'],
                    'word_count': len(density_result['content'].split())
                })
            
            # Select best result based on confidence and content quality
            if results:
                best_result = self._select_best_result(results)
                logger.info(f"Content extraction successful: method={best_result['method']}, "
                           f"confidence={best_result['confidence']}, "
                           f"word_count={best_result.get('word_count', 0)}")
                return best_result
            
        except Exception as e:
            logger.error(f"Content identification failed: {e}")
        
        # Fallback: basic cleaning
        logger.warning("Falling back to basic extraction method")
        return self._basic_extraction(html_content)
    
    def _extract_with_readability(self, html_content: str) -> Optional[Dict]:
        """Use Mozilla's readability algorithm for content extraction."""
        try:
            doc = Document(html_content)
            content = doc.summary()
            title = doc.title()
            
            # Validate content quality
            if self._is_valid_content(content):
                return {
                    'content': self._clean_text(content),
                    'title': title,
                    'score': getattr(doc, 'score', 0)
                }
            return None
            
        except Exception as e:
            logger.debug(f"Readability extraction failed: {e}")
            return None
    
    def _extract_semantic_content(self, html_content: str) -> Optional[Dict]:
        """Extract content using semantic HTML5 elements."""
        try:
            tree = html.fromstring(html_content)
            
            # Try semantic selectors in priority order
            for selector in self.content_selectors:
                try:
                    elements = tree.cssselect(selector)
                    if elements:
                        # Use the first (and typically main) element
                        content = self._clean_element_text(elements[0])
                        if self._is_valid_content(content):
                            return {
                                'content': content,
                                'element_type': selector
                            }
                except Exception:
                    continue  # Try next selector
            
            return None
            
        except Exception as e:
            logger.debug(f"Semantic extraction failed: {e}")
            return None
    
    def _extract_by_density(self, html_content: str) -> Optional[Dict]:
        """Extract content by analyzing text density in page sections."""
        try:
            tree = html.fromstring(html_content)
            
            # Remove unwanted elements first
            self._remove_unwanted_elements(tree)
            
            # Find elements with high text density
            candidates = []
            
            for elem in tree.iter():
                if elem.tag in ['div', 'section', 'article', 'main', 'p']:
                    try:
                        text = self._clean_element_text(elem)
                        if len(text) > self.min_content_length:
                            # Calculate content density metrics
                            density_score = self._calculate_density_score(elem, text)
                            
                            if density_score > 0.1:  # Minimum density threshold
                                candidates.append({
                                    'content': text,
                                    'score': density_score,
                                    'length': len(text),
                                    'element': elem.tag
                                })
                    except Exception:
                        continue
            
            # Return highest scoring candidate
            if candidates:
                best = max(candidates, 
                          key=lambda x: x['score'] * (1 + x['length'] / 10000))  # Bonus for length
                return {
                    'content': best['content'],
                    'score': best['score']
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Density extraction failed: {e}")
            return None
    
    def _basic_extraction(self, html_content: str) -> Dict:
        """Fallback basic extraction method."""
        try:
            tree = html.fromstring(html_content)
            
            # Remove unwanted elements
            self._remove_unwanted_elements(tree)
            
            # Extract all remaining text
            content = self._clean_element_text(tree)
            
            return {
                'content': content[:5000] if len(content) > 5000 else content,  # Limit fallback content
                'confidence': 0.5,
                'method': 'basic',
                'word_count': len(content.split())
            }
            
        except Exception as e:
            logger.error(f"Basic extraction failed: {e}")
            return self._empty_result()
    
    def _remove_unwanted_elements(self, tree):
        """Remove unwanted elements from the DOM tree."""
        for selector in self.exclude_selectors:
            try:
                for elem in tree.cssselect(selector):
                    if elem.getparent() is not None:
                        elem.getparent().remove(elem)
            except Exception:
                continue  # Skip invalid selectors
    
    def _clean_element_text(self, element) -> str:
        """Extract and clean text from an element."""
        if element is None:
            return ''
        
        try:
            # Get text content
            text = element.text_content()
            return self._clean_text(text)
        except Exception:
            return ''
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ''
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common artifacts
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
        text = re.sub(r'^\s*\|.*?\|\s*$', '', text, flags=re.MULTILINE)  # Remove table artifacts
        
        return text
    
    def _calculate_density_score(self, element, text: str) -> float:
        """Calculate content density score for an element."""
        try:
            # Get HTML length
            html_content = etree.tostring(element, encoding='unicode')
            html_length = len(html_content)
            text_length = len(text)
            
            if html_length == 0:
                return 0.0
            
            # Basic density: text/html ratio
            density = text_length / html_length
            
            # Apply modifiers
            # 1. Penalty for high link density
            link_texts = [a.text_content() for a in element.cssselect('a') if a.text_content()]
            link_text_length = sum(len(link_text) for link_text in link_texts)
            link_density = link_text_length / text_length if text_length > 0 else 1.0
            
            if link_density > self.max_link_density:
                density *= (1 - link_density)  # Reduce score for high link density
            
            # 2. Bonus for paragraph structure
            paragraph_count = len(element.cssselect('p'))
            if paragraph_count >= self.min_paragraph_count:
                density *= 1.2  # Bonus for good paragraph structure
            
            return max(0.0, density)
            
        except Exception:
            return 0.0
    
    def _is_valid_content(self, content: str) -> bool:
        """Check if extracted content meets quality thresholds."""
        if not content or len(content.strip()) < self.min_content_length:
            return False
        
        # Check for reasonable word count
        words = content.split()
        if len(words) < 20:  # Too few words
            return False
        
        # Check for reasonable sentence structure
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) < 3:  # Too few sentences
            return False
        
        return True
    
    def _select_best_result(self, results: List[Dict]) -> Dict:
        """Select the best result from multiple extraction methods."""
        if not results:
            return self._empty_result()
        
        # Score each result based on multiple factors
        for result in results:
            base_score = result['confidence']
            word_count = result.get('word_count', 0)
            
            # Bonus for reasonable content length
            if 200 <= word_count <= 5000:
                base_score += 0.1
            elif word_count > 5000:
                base_score += 0.05  # Slight bonus for very long content
            
            # Method-specific bonuses
            if result['method'] == 'readability' and result.get('score', 0) > 0:
                base_score += 0.05
            
            result['final_score'] = base_score
        
        # Return result with highest final score
        return max(results, key=lambda x: x['final_score'])
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'content': '',
            'confidence': 0.1,
            'method': 'failed',
            'word_count': 0
        }
