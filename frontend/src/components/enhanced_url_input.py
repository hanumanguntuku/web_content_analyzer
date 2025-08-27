"""
Enhanced URL Input Component - M1-PRES-01 Implementation
Advanced URL input with comprehensive validation and user feedback
"""
import streamlit as st
import re
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import time

def validate_url_format(url: str) -> Tuple[bool, str]:
    """
    Validate URL format and basic security checks
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or len(url.strip()) == 0:
        return False, "Please enter a URL"
    
    url = url.strip()
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Please enter a valid URL (must start with http:// or https://)"
    
    # Parse URL for additional checks
    try:
        parsed = urlparse(url)
        
        # Check for suspicious schemes
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS URLs are supported"
        
        # Basic localhost/private IP warning (not blocking, just warning)
        if parsed.hostname:
            if parsed.hostname in ['localhost', '127.0.0.1']:
                return False, "Local URLs are not allowed for security reasons"
            
            # Check for private IP ranges (basic check)
            if parsed.hostname.startswith(('192.168.', '10.', '172.')):
                return False, "Private IP addresses are not allowed"
        
        # Check URL length
        if len(url) > 2000:
            return False, "URL is too long (maximum 2000 characters)"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"

def render_url_input() -> Optional[Dict[str, Any]]:
    """
    Render enhanced URL input component with validation
    
    Returns:
        Dictionary with URL and analysis options, or None if invalid
    """
    st.markdown("### 🔗 Enter Website URL(s)")
    batch_mode = st.checkbox("Batch Mode: Analyze Multiple URLs", value=False)
    url = ""
    urls = []
    if batch_mode:
        urls_text = st.text_area(
            "Website URLs (one per line)",
            placeholder="https://example.com\nhttps://another.com",
            help="Enter one URL per line to analyze multiple sites."
        )
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if urls:
            invalids = [u for u in urls if not validate_url_format(u)[0]]
            if invalids:
                st.error(f"Invalid URLs: {', '.join(invalids)}")
                return None
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            url = st.text_input(
                "Website URL",
                placeholder="https://example.com",
                help="Enter the URL of the website you want to analyze",
                label_visibility="collapsed"
            )
        with col2:
            if url:
                is_valid, error_msg = validate_url_format(url)
                if is_valid:
                    st.success("✅ Valid URL")
                else:
                    st.error("❌ Invalid")
        if url:
            is_valid, error_msg = validate_url_format(url)
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
                return None
        if not url:
            return None
    
    # Analysis options section
    st.markdown("### ⚙️ Analysis Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        deep_analysis = st.checkbox(
            "Deep Analysis",
            value=True,
            help="Enable advanced text processing, sentiment analysis, and entity extraction"
        )
    with col2:
        extract_images = st.checkbox(
            "Extract Images",
            value=True,
            help="Extract and analyze image information from the page"
        )
    with col3:
        extract_links = st.checkbox(
            "Extract Links",
            value=True,
            help="Extract and analyze all links from the page"
        )
    
    # Advanced options in an expander
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            max_content_size = st.selectbox(
                "Max Content Size",
                options=["5MB", "10MB", "15MB", "20MB"],
                index=1,
                help="Maximum size of content to analyze"
            )
        
        with col2:
            timeout_seconds = st.slider(
                "Request Timeout (seconds)",
                min_value=10,
                max_value=60,
                value=30,
                help="Maximum time to wait for the website to respond"
            )
    
    # Sample URLs for testing
    st.markdown("### 📝 Sample URLs for Testing")
    sample_urls = [
        "https://example.com",
        "https://www.wikipedia.org",
        "https://github.com/python/cpython",
        "https://docs.python.org/3/",
        "https://www.bbc.com/news"
    ]
    
    selected_sample = st.selectbox(
        "Or choose a sample URL:",
        options=[""] + sample_urls,
        format_func=lambda x: "Select a sample URL..." if x == "" else x
    )
    
    if selected_sample:
        st.info(f"💡 Selected sample URL: {selected_sample}")
        url = selected_sample
        # Revalidate with selected URL
        is_valid, error_msg = validate_url_format(url)
        if not is_valid:
            st.error(f"⚠️ {error_msg}")
            return None
    
    # Return analysis configuration
    if batch_mode and urls:
        return {
            "batch_mode": True,
            "urls": urls,
            "deep_analysis": deep_analysis,
            "extract_images": extract_images,
            "extract_links": extract_links,
            "max_content_size": max_content_size,
            "timeout_seconds": timeout_seconds
        }
    elif url and (not batch_mode):
        return {
            "url": url,
            "deep_analysis": deep_analysis,
            "extract_images": extract_images,
            "extract_links": extract_links,
            "max_content_size": max_content_size,
            "timeout_seconds": timeout_seconds
        }
    return None

def render_analysis_button(analysis_config: Dict[str, Any]) -> bool:
    """
    Render the analysis button with configuration summary
    
    Args:
        analysis_config: Configuration dictionary from render_url_input
        
    Returns:
        True if button was clicked, False otherwise
    """
    if not analysis_config:
        return False
    
    # Show configuration summary
    st.markdown("### 🚀 Ready to Analyze")
    
    with st.expander("📋 Analysis Configuration"):
        if analysis_config.get("batch_mode"):
            st.write("**URLs:**")
            for u in analysis_config["urls"]:
                st.write(f"- {u}")
        else:
            st.write("**URL:**", analysis_config["url"])
        st.write("**Deep Analysis:**", "✅ Enabled" if analysis_config["deep_analysis"] else "❌ Disabled")
        st.write("**Extract Images:**", "✅ Enabled" if analysis_config["extract_images"] else "❌ Disabled")
        st.write("**Extract Links:**", "✅ Enabled" if analysis_config["extract_links"] else "❌ Disabled")
        st.write("**Max Content Size:**", analysis_config["max_content_size"])
        st.write("**Timeout:**", f"{analysis_config['timeout_seconds']} seconds")
    
    # Analysis button with custom styling
    analyze_button = st.button(
        "🔍 Analyze Website",
        type="primary",
        use_container_width=True,
        help="Start the comprehensive analysis of the website"
    )
    
    if analyze_button:
        # Store analysis config in session state for use during analysis
        st.session_state.current_analysis_config = analysis_config
        return True
    
    return False

def render_url_input_section() -> Optional[Dict[str, Any]]:
    """
    Render the complete URL input section
    
    Returns:
        Analysis configuration if ready to analyze, None otherwise
    """
    # Main URL input and validation
    analysis_config = render_url_input()
    
    if analysis_config:
        # Show analysis button if URL is valid
        if render_analysis_button(analysis_config):
            return analysis_config
    
    return None
