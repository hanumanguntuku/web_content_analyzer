#!/usr/bin/env python3
"""
Quick validation test for Phase 1 implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.content_identifier import ContentIdentifier
from src.scrapers.enhanced_content_extractor import EnhancedContentExtractor

def test_content_identifier():
    """Test the ContentIdentifier functionality."""
    print("🧪 Testing ContentIdentifier...")
    
    identifier = ContentIdentifier()
    
    # Test with semantic HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head><title>Test Article</title></head>
<body>
    <header>Site Header</header>
    <nav>Navigation Menu</nav>
    <main>
        <article>
            <h1>Breaking News: Important Update</h1>
            <p>This is the main content of the article. It contains 
            important information that users want to read. The content 
            is substantial and provides real value.</p>
            <p>Additional paragraphs provide more context and depth 
            to the main topic. This content should be identified as 
            the primary content area.</p>
        </article>
    </main>
    <aside>Sidebar content</aside>
    <footer>Footer content</footer>
</body>
</html>"""
    
    result = identifier.identify_main_content(html)
    
    print(f"  ✓ Method: {result['method']}")
    print(f"  ✓ Confidence: {result['confidence']:.2f}")
    print(f"  ✓ Word count: {result.get('word_count', 0)}")
    print(f"  ✓ Content includes main article: {'Breaking News' in result['content']}")
    print(f"  ✓ Filters navigation: {'Navigation Menu' not in result['content']}")
    
    assert result['confidence'] > 0.0, "No confidence in extraction"
    assert 'Breaking News' in result['content'], "Main content not found"
    assert 'Navigation Menu' not in result['content'], "Navigation not filtered"
    
    print("  ✅ ContentIdentifier test passed!\n")

def test_enhanced_extractor():
    """Test the Enhanced Content Extractor."""
    print("🧪 Testing Enhanced Content Extractor...")
    
    extractor = EnhancedContentExtractor()
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Complete Guide to AI Development</title>
    <meta name="description" content="Learn AI development with practical examples">
    <meta name="author" content="Dr. Jane Smith">
    <meta name="keywords" content="AI, machine learning, development">
    <meta property="og:title" content="Complete Guide to AI Development">
    <meta property="og:description" content="Comprehensive AI development tutorial">
</head>
<body>
    <header>Site Header</header>
    <main>
        <article>
            <h1>Complete Guide to AI Development</h1>
            <div class="author-info">By Dr. Jane Smith</div>
            <p>Artificial Intelligence development has become one of the most 
            exciting fields in technology. This comprehensive guide will walk 
            you through the fundamentals and advanced concepts.</p>
            <p>Whether you're a beginner or experienced developer, this guide 
            provides practical insights and real-world examples to help you 
            master AI development techniques.</p>
        </article>
    </main>
    <footer>Footer content</footer>
</body>
</html>"""
    
    result = extractor.extract_content(html, "https://example.com/ai-guide")
    
    print(f"  ✓ Extraction Method: {result['extraction_method']}")
    print(f"  ✓ Confidence: {result['confidence']:.2f}")
    print(f"  ✓ Title: {result.get('title')}")
    print(f"  ✓ Word count: {result.get('word_count', 0)}")
    
    metadata = result.get('metadata', {})
    print(f"  ✓ Description extracted: {bool(metadata.get('description'))}")
    print(f"  ✓ Author extracted: {metadata.get('author')}")
    print(f"  ✓ Language detected: {metadata.get('language')}")
    print(f"  ✓ Keywords found: {len(metadata.get('keywords', []))}")
    
    social_meta = metadata.get('social_meta', {})
    print(f"  ✓ Open Graph data: {len(social_meta)} fields")
    
    assert result['title'] == "Complete Guide to AI Development", "Title not extracted correctly"
    assert metadata.get('author') == "Dr. Jane Smith", "Author not extracted"
    assert metadata.get('description'), "Description not extracted"
    assert 'AI development' in result['content'], "Main content not found"
    
    print("  ✅ Enhanced Content Extractor test passed!\n")

def test_real_world_simulation():
    """Test with complex real-world-like HTML."""
    print("🧪 Testing Real-world HTML simulation...")
    
    identifier = ContentIdentifier()
    
    # Simulate a complex news article page
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Major Tech Breakthrough Announced | TechNews</title>
    <meta name="description" content="Scientists announce revolutionary discovery">
</head>
<body>
    <header class="site-header">
        <nav class="main-nav">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/tech">Technology</a></li>
                <li><a href="/science">Science</a></li>
            </ul>
        </nav>
    </header>
    
    <div class="container">
        <aside class="sidebar">
            <div class="ad-banner">Advertisement</div>
            <div class="trending">
                <h3>Trending Now</h3>
                <ul>
                    <li><a href="/trend1">Trending Article 1</a></li>
                    <li><a href="/trend2">Trending Article 2</a></li>
                </ul>
            </div>
        </aside>
        
        <main class="content-area">
            <article class="news-article">
                <h1>Scientists Announce Major Breakthrough in Quantum Computing</h1>
                <div class="article-meta">
                    <span class="byline">By Sarah Johnson</span>
                    <time datetime="2025-08-19">August 19, 2025</time>
                </div>
                
                <p>In a groundbreaking development, researchers at QuantumTech 
                University have successfully demonstrated a new quantum computing 
                architecture that could revolutionize the field. The breakthrough 
                represents a significant leap forward in quantum stability and 
                error correction.</p>
                
                <p>The research team, led by Dr. Michael Chen, has been working 
                on this project for over five years. Their innovative approach 
                uses a novel qubit design that maintains coherence for 
                unprecedented durations.</p>
                
                <p>"This discovery opens up new possibilities for quantum 
                applications in cryptography, drug discovery, and artificial 
                intelligence," said Dr. Chen in an exclusive interview.</p>
                
                <p>The findings have been published in the prestigious Journal 
                of Quantum Sciences and are expected to accelerate development 
                of practical quantum computers.</p>
            </article>
        </main>
        
        <aside class="related-content">
            <h3>Related Articles</h3>
            <div class="related-item">
                <a href="/quantum1">Previous Quantum Discoveries</a>
            </div>
            <div class="related-item">
                <a href="/quantum2">Future of Quantum Computing</a>
            </div>
        </aside>
    </div>
    
    <footer class="site-footer">
        <p>&copy; 2025 TechNews. All rights reserved.</p>
    </footer>
</body>
</html>"""
    
    result = identifier.identify_main_content(html)
    
    print(f"  ✓ Method: {result['method']}")
    print(f"  ✓ Confidence: {result['confidence']:.2f}")
    print(f"  ✓ Word count: {result.get('word_count', 0)}")
    
    content = result['content']
    
    # Check that main content is extracted
    main_content_found = (
        'quantum computing' in content.lower() and
        'breakthrough' in content.lower() and
        'Dr. Michael Chen' in content
    )
    
    # Check that peripheral content is filtered
    nav_filtered = 'Home' not in content or 'Technology' not in content
    ads_filtered = 'Advertisement' not in content
    related_filtered = 'Related Articles' not in content
    
    print(f"  ✓ Main content extracted: {main_content_found}")
    print(f"  ✓ Navigation filtered: {nav_filtered}")
    print(f"  ✓ Advertisements filtered: {ads_filtered}")
    print(f"  ✓ Related content filtered: {related_filtered}")
    
    assert main_content_found, "Main article content not found"
    assert nav_filtered, "Navigation content not properly filtered"
    assert ads_filtered, "Advertisement content not filtered"
    
    print("  ✅ Real-world simulation test passed!\n")

def run_performance_test():
    """Quick performance test."""
    print("🧪 Running Performance Test...")
    
    import time
    
    identifier = ContentIdentifier()
    
    # Generate moderately complex HTML
    html = """<!DOCTYPE html>
<html>
<head><title>Performance Test</title></head>
<body>
    <header>Header content</header>
    <nav>Navigation</nav>
    <main>
        <article>
            <h1>Performance Test Article</h1>
""" + "".join([
        f"<p>This is paragraph {i} of the performance test. " +
        "It contains enough text to make the extraction meaningful " +
        "while testing the speed of the content identification algorithms.</p>"
        for i in range(20)
    ]) + """
        </article>
    </main>
    <aside>Sidebar content</aside>
    <footer>Footer content</footer>
</body>
</html>"""
    
    # Test multiple extractions
    iterations = 5
    start_time = time.time()
    
    for i in range(iterations):
        result = identifier.identify_main_content(html)
        assert result['confidence'] > 0.0, f"Failed on iteration {i}"
    
    end_time = time.time()
    avg_time = (end_time - start_time) / iterations
    
    print(f"  ✓ Average extraction time: {avg_time:.3f} seconds")
    print(f"  ✓ Performance target (<3.0s): {'✅ PASS' if avg_time < 3.0 else '❌ FAIL'}")
    
    assert avg_time < 3.0, f"Performance target missed: {avg_time:.3f}s"
    
    print("  ✅ Performance test passed!\n")

if __name__ == "__main__":
    print("🚀 Phase 1 Implementation Validation\n")
    print("=" * 50)
    
    try:
        test_content_identifier()
        test_enhanced_extractor()
        test_real_world_simulation()
        run_performance_test()
        
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Phase 1 implementation is working correctly")
        print("✅ Content identification algorithms functional")
        print("✅ Metadata extraction operational")
        print("✅ Performance targets met")
        print("\n🚀 Ready for production testing!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
