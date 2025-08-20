"""
Test suite for advanced content identification functionality.
"""

import pytest
import asyncio
from src.processors.content_identifier import ContentIdentifier
from src.scrapers.enhanced_content_extractor import EnhancedContentExtractor
from src.services.scraping_service import WebScraperService


class TestContentIdentification:
    """Test cases for intelligent content identification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.identifier = ContentIdentifier()
        self.extractor = EnhancedContentExtractor()
    
    def test_basic_content_identification(self):
        """Test basic content identification with simple HTML."""
        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <header>Site Navigation</header>
            <nav>Menu Items</nav>
            <main>
                <article>
                    <h1>Breaking News: Important Event</h1>
                    <p>This is the main content of the article. It contains
                    important information that users want to read. The content
                    is substantial and meaningful.</p>
                    <p>Another paragraph of important content that adds value
                    and context to the main story. This helps test the
                    content identification algorithms.</p>
                    <p>A third paragraph to ensure we have enough content
                    for proper testing of the extraction quality.</p>
                </article>
            </main>
            <aside>Advertisement content here</aside>
            <footer>Copyright information</footer>
        </body>
        </html>
        """
        
        result = self.identifier.identify_main_content(html)
        
        # Assertions
        assert result['confidence'] > 0.5, f"Low confidence: {result['confidence']}"
        assert 'Breaking News' in result['content'], "Title not found in content"
        assert 'main content' in result['content'], "Main content not extracted"
        assert 'Navigation' not in result['content'], "Navigation incorrectly included"
        assert 'Advertisement' not in result['content'], "Advertisement not filtered"
        assert result['word_count'] > 30, f"Too few words: {result['word_count']}"
        
        print(f"✅ Basic test passed - Method: {result['method']}, Confidence: {result['confidence']}")
    
    def test_news_article_structure(self):
        """Test with typical news article HTML structure."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Tech Company Announces New Product | Tech News</title>
            <meta name="description" content="Major tech company reveals innovative product">
            <meta name="author" content="John Smith">
            <meta property="og:title" content="Tech Company Announces New Product">
        </head>
        <body>
            <header class="site-header">
                <nav>Home | News | Tech | Business</nav>
            </header>
            
            <main class="content">
                <article class="news-article">
                    <h1>Tech Company Announces Revolutionary New Product</h1>
                    <div class="article-meta">
                        <span class="author">By John Smith</span>
                        <time datetime="2025-08-19">August 19, 2025</time>
                    </div>
                    
                    <p>In a groundbreaking announcement today, TechCorp unveiled 
                    their latest innovation that promises to revolutionize the 
                    industry. The new product combines artificial intelligence 
                    with advanced hardware to deliver unprecedented performance.</p>
                    
                    <p>The company's CEO stated that this represents a major 
                    milestone in their technology roadmap. Early testing shows 
                    remarkable improvements in efficiency and user experience.</p>
                    
                    <p>Industry experts are calling this announcement a game-changer 
                    that could reshape the competitive landscape. The product is 
                    expected to launch in Q4 2025 with pricing starting at $299.</p>
                </article>
            </main>
            
            <aside class="sidebar">
                <div class="related-articles">Related Stories</div>
                <div class="advertisement">Sponsored Content</div>
            </aside>
            
            <footer>© 2025 Tech News</footer>
        </body>
        </html>
        """
        
        result = self.identifier.identify_main_content(html)
        
        # Test content extraction quality
        assert result['confidence'] > 0.6, f"Low confidence for news article: {result['confidence']}"
        assert 'TechCorp' in result['content'], "Company name not found"
        assert 'revolutionary' in result['content'], "Key content missing"
        assert 'Related Stories' not in result['content'], "Sidebar content incorrectly included"
        assert 'Sponsored Content' not in result['content'], "Advertisement not filtered"
        
        print(f"✅ News article test passed - Method: {result['method']}")
    
    def test_enhanced_extractor_metadata(self):
        """Test enhanced extractor's metadata extraction capabilities."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Complete Guide to Web Scraping</title>
            <meta name="description" content="Learn web scraping techniques and best practices">
            <meta name="author" content="Jane Developer">
            <meta name="keywords" content="web scraping, python, automation">
            <meta property="og:title" content="Complete Guide to Web Scraping">
            <meta property="og:description" content="Comprehensive tutorial on web scraping">
            <meta property="og:image" content="https://example.com/image.jpg">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Complete Guide to Web Scraping",
                "author": {
                    "@type": "Person",
                    "name": "Jane Developer"
                },
                "datePublished": "2025-08-19"
            }
            </script>
        </head>
        <body>
            <article>
                <h1>Complete Guide to Web Scraping</h1>
                <p>Web scraping is a powerful technique for extracting data from websites. 
                This comprehensive guide covers everything you need to know about modern 
                web scraping practices, tools, and techniques.</p>
                
                <p>Whether you're a beginner or an experienced developer, this guide 
                will help you understand the fundamentals and advanced concepts of 
                web scraping using Python and other technologies.</p>
            </article>
        </body>
        </html>
        """
        
        result = self.extractor.extract_content(html, "https://example.com/guide")
        
        # Test metadata extraction
        metadata = result.get('metadata', {})
        
        assert result['title'] == "Complete Guide to Web Scraping", "Title extraction failed"
        assert metadata.get('description'), "Description not extracted"
        assert metadata.get('author') == "Jane Developer", "Author not extracted"
        assert metadata.get('keywords'), "Keywords not extracted"
        assert metadata.get('language') == "en", "Language not detected"
        
        # Test social metadata
        social_meta = metadata.get('social_meta', {})
        assert social_meta.get('og_title'), "Open Graph title not extracted"
        assert social_meta.get('og_description'), "Open Graph description not extracted"
        
        print(f"✅ Metadata extraction test passed - Confidence: {result['confidence']}")
    
    def test_content_quality_filtering(self):
        """Test filtering of low-quality content."""
        # Test with minimal content
        minimal_html = "<html><body><p>Short text</p></body></html>"
        result = self.identifier.identify_main_content(minimal_html)
        
        # Should have low confidence for minimal content
        assert result['confidence'] < 0.8, "High confidence for minimal content"
        
        # Test with high link density (navigation-like content)
        link_heavy_html = """
        <html><body>
            <div>
                <a href="/">Home</a> | 
                <a href="/news">News</a> | 
                <a href="/sports">Sports</a> | 
                <a href="/tech">Tech</a>
                Some minimal text content here.
            </div>
        </body></html>
        """
        result = self.identifier.identify_main_content(link_heavy_html)
        
        # Should handle link-heavy content appropriately
        assert result['confidence'] < 0.9, "High confidence for link-heavy content"
        
        print("✅ Content quality filtering test passed")
    
    def test_multiple_algorithm_comparison(self):
        """Test that multiple algorithms produce reasonable results."""
        complex_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Complex Page Test</title></head>
        <body>
            <header>Header content</header>
            <nav>Navigation menu</nav>
            
            <main>
                <article>
                    <h1>Main Article Title</h1>
                    <p>This is the primary content that should be extracted. 
                    It contains valuable information that users are looking for 
                    when they visit this page.</p>
                    
                    <p>Additional paragraphs provide more context and depth 
                    to the main topic. This content is substantial and 
                    represents the core value of the page.</p>
                    
                    <p>The extraction algorithm should identify this as the 
                    main content area and filter out navigation, advertisements, 
                    and other peripheral content.</p>
                </article>
            </main>
            
            <section class="related">
                <h2>Related Articles</h2>
                <ul>
                    <li><a href="/article1">Related Article 1</a></li>
                    <li><a href="/article2">Related Article 2</a></li>
                </ul>
            </section>
            
            <aside class="ads">
                <div>Advertisement 1</div>
                <div>Advertisement 2</div>
            </aside>
            
            <footer>Footer content</footer>
        </body>
        </html>
        """
        
        result = self.identifier.identify_main_content(complex_html)
        
        # Should extract main content effectively
        assert 'Main Article Title' in result['content'], "Main title not found"
        assert 'primary content' in result['content'], "Primary content not found"
        assert 'extraction algorithm' in result['content'], "Key content missing"
        
        # Should filter out peripheral content
        assert 'Related Articles' not in result['content'], "Related articles not filtered"
        assert 'Advertisement' not in result['content'], "Advertisements not filtered"
        assert 'Navigation menu' not in result['content'], "Navigation not filtered"
        
        # Should have reasonable confidence
        assert result['confidence'] > 0.6, f"Low confidence: {result['confidence']}"
        
        print(f"✅ Multiple algorithm test passed - Method: {result['method']}")


@pytest.mark.asyncio
async def test_full_integration():
    """Test full integration with scraping service."""
    service = WebScraperService()
    
    # Test HTML that simulates a real webpage
    test_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Integration Test Article</title>
        <meta name="description" content="Testing full integration pipeline">
    </head>
    <body>
        <header>Site Header</header>
        <main>
            <article>
                <h1>Integration Test Article</h1>
                <p>This content tests the full integration pipeline from 
                web scraping through intelligent content extraction.</p>
                <p>The system should identify this as the main content 
                and extract comprehensive metadata about the page.</p>
            </article>
        </main>
        <footer>Site Footer</footer>
    </body>
    </html>
    """
    
    # Note: For this test, we would normally use a mock HTTP server
    # For now, we'll test the content extraction directly
    extractor = EnhancedContentExtractor()
    result = extractor.extract_content(test_html, "https://example.com/test")
    
    assert result['content'], "No content extracted"
    assert result['confidence'] > 0.5, "Low extraction confidence"
    assert result['title'] == "Integration Test Article", "Title not extracted"
    
    print("✅ Full integration test passed")


def run_performance_benchmark():
    """Run performance benchmark for content extraction."""
    import time
    
    identifier = ContentIdentifier()
    
    # Large HTML content for performance testing
    large_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Performance Test</title></head>
    <body>
    """ + """
        <div class="content-section">
            <p>This is paragraph {} of the performance test content. 
            It contains substantial text to test the extraction speed 
            and accuracy of the content identification algorithms.</p>
        </div>
    """.format("{i}") * 100 + """
        <main>
            <article>
                <h1>Main Content Section</h1>
                <p>This is the main content that should be identified 
                as the primary content area despite the presence of 
                many other content sections in the document.</p>
            </article>
        </main>
    </body>
    </html>
    """
    
    # Perform multiple extractions to test performance
    start_time = time.time()
    iterations = 10
    
    for i in range(iterations):
        result = identifier.identify_main_content(large_html)
        assert result['confidence'] > 0.0, f"Failed extraction on iteration {i}"
    
    end_time = time.time()
    avg_time = (end_time - start_time) / iterations
    
    print(f"✅ Performance test passed - Average time: {avg_time:.3f}s per extraction")
    assert avg_time < 3.0, f"Extraction too slow: {avg_time:.3f}s (target: <3.0s)"


if __name__ == "__main__":
    """Run tests when script is executed directly."""
    test_instance = TestContentIdentification()
    test_instance.setup_method()
    
    print("🚀 Running Phase 1 Content Identification Tests\n")
    
    try:
        # Run basic functionality tests
        test_instance.test_basic_content_identification()
        test_instance.test_news_article_structure()
        test_instance.test_enhanced_extractor_metadata()
        test_instance.test_content_quality_filtering()
        test_instance.test_multiple_algorithm_comparison()
        
        # Run integration test
        asyncio.run(test_full_integration())
        
        # Run performance benchmark
        run_performance_benchmark()
        
        print("\n🎉 All tests passed! Phase 1 implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
