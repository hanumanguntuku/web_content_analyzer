"""
URL Input Component
Streamlit component for URL input with validation and suggestions
"""
import streamlit as st
import re
from typing import Optional, List

def validate_url_format(url: str) -> bool:
    """Basic URL format validation"""
    if not url:
        return False
    
    # URL pattern matching
    url_pattern = re.compile(
        r'^https?://'  # http or https
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?'  # domain
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def get_example_urls() -> List[str]:
    """Get list of example URLs for testing"""
    return [
        "https://www.microsoft.com",
        "https://www.apple.com",
        "https://www.bbc.com",
        "https://techcrunch.com",
        "https://medium.com",
        "https://dev.to",
        "https://www.coursera.org",
        "https://www.amzur.com"
    ]

def render_url_input() -> Optional[str]:
    """
    Render URL input component with validation and examples
    
    Returns:
        str: The entered URL, or None if empty
    """
    
    # URL input field
    url = st.text_input(
        "🌐 Website URL",
        placeholder="https://example.com",
        help="Enter the full URL of the website you want to analyze",
        key="url_input"
    )
    
    # Example URLs section
    st.markdown("**📚 Example URLs:**")
    st.markdown("*Click to copy and paste into the URL field above*")
    
    example_urls = get_example_urls()
    cols = st.columns(2)
    
    for i, example_url in enumerate(example_urls):
        col = cols[i % 2]
        with col:
            st.code(example_url, language=None)
    
    # URL validation feedback
    if url:
        if validate_url_format(url):
            st.success("✅ Valid URL format")
        else:
            st.error("❌ Invalid URL format. Please include http:// or https://")
            return None
    
    # URL tips
    with st.expander("💡 URL Tips"):
        st.markdown("""
        **Supported URL formats:**
        - ✅ `https://example.com`
        - ✅ `http://example.com`
        - ✅ `https://www.example.com/page`
        - ✅ `https://subdomain.example.com`
        
        **Security Notes:**
        - 🛡️ URLs are validated for security (SSRF prevention)
        - 🚫 Private IP addresses are blocked
        - ⏱️ Request timeout: 30 seconds
        - 📊 Content size limit: 10MB
        """)
    
    return url

def render_url_history() -> None:
    """Render recent URL analysis history"""
    if 'analysis_history' in st.session_state and st.session_state.analysis_history:
        st.markdown("**📝 Recent Analyses:**")
        
        # Show last 5 analyses
        recent = list(reversed(st.session_state.analysis_history[-5:]))
        
        for i, history_item in enumerate(recent):
            url = history_item['url']
            timestamp = history_item['timestamp']
            
            # Format timestamp
            import time
            time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
            
            # Create clickable history item
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(
                    f"🔗 {url[:40]}{'...' if len(url) > 40 else ''}",
                    key=f"history_{i}",
                    help=f"Analyzed at {time_str}"
                ):
                    st.session_state.selected_example = url
                    st.rerun()
                    st.session_state.analysis_results = history_item['results']
                    st.rerun()
            
            with col2:
                st.text(time_str)
