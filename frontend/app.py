"""
Web Content Analyzer - Streamlit Frontend Application
Modern, responsive UI for web content analysis
"""
import streamlit as st
import requests
import time
import os
from typing import Dict, Any, Optional
import logging

from src.services.api_client import APIClient
from src.components.url_input import render_url_input
from src.components.results_display import render_results
from src.components.progress import render_progress_indicator
from src.utils.formatters import format_analysis_results
from src.utils.validators import validate_url_input

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Web Content Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/hanumanguntuku/web_content_analyzer',
        'Report a bug': 'https://github.com/hanumanguntuku/web_content_analyzer/issues',
        'About': """
        # Web Content Analyzer
        
        A powerful tool for analyzing web content using AI.
        
        **Features:**
        - Web scraping with anti-detection
        - Content extraction and cleaning
        - AI-powered analysis
        - Security-first approach (SSRF prevention)
        
        **Version:** 1.0.0
        """
    }
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B6B;
        margin: 1rem 0;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client
@st.cache_resource
def get_api_client():
    """Initialize and cache API client"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    return APIClient(base_url=backend_url)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    if 'backend_status' not in st.session_state:
        st.session_state.backend_status = None

def check_backend_status():
    """Check if backend is available"""
    try:
        api_client = get_api_client()
        status = api_client.get_status()
        st.session_state.backend_status = {
            "available": True,
            "status": status
        }
        return True
    except Exception as e:
        st.session_state.backend_status = {
            "available": False,
            "error": str(e)
        }
        return False

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Web Content Analyzer</h1>
        <p>Extract, analyze, and understand web content with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with settings and information"""
    with st.sidebar:
        st.header("🛠️ Settings")
        
        # Backend status
        st.subheader("Backend Status")
        if st.session_state.backend_status:
            if st.session_state.backend_status["available"]:
                st.markdown("""
                <div class="status-success">
                    ✅ Backend Connected
                </div>
                """, unsafe_allow_html=True)
                
                status_data = st.session_state.backend_status["status"]
                st.json({
                    "version": status_data.get("version", "unknown"),
                    "environment": status_data.get("environment", "unknown"),
                    "features": status_data.get("features", {})
                })
            else:
                st.markdown("""
                <div class="status-error">
                    ❌ Backend Unavailable
                </div>
                """, unsafe_allow_html=True)
                st.error(f"Error: {st.session_state.backend_status['error']}")
        
        # Analysis Options (for future implementation)
        st.subheader("Analysis Options")
        st.info("Advanced options will be available in later milestones")
        
        # Help section
        st.subheader("📖 Help")
        with st.expander("How to use"):
            st.markdown("""
            1. **Enter URL**: Paste the website URL you want to analyze
            2. **Click Analyze**: Start the analysis process
            3. **View Results**: Review the comprehensive analysis report
            4. **Export**: Download results in various formats (coming soon)
            """)
        
        with st.expander("Supported Sites"):
            st.markdown("""
            - **Corporate websites** (microsoft.com, apple.com)
            - **News sites** (bbc.com, techcrunch.com)
            - **Blogs** (medium.com, dev.to)
            - **E-commerce** (shopify.com)
            - **Educational** (coursera.org, edx.org)
            """)

def render_main_content():
    """Render main content area"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🌐 URL Input")
        
        # URL input component
        url = render_url_input()
        
        # Analysis button
        if st.button("🔍 Analyze Website", type="primary", use_container_width=True):
            # Debug: Show the URL value
            st.write(f"Debug: URL value = '{url}'")
            st.write(f"Debug: URL type = {type(url)}")
            st.write(f"Debug: URL bool = {bool(url)}")
            
            if url and url.strip():
                # Validate URL
                is_valid, error_message = validate_url_input(url.strip())
                if is_valid:
                    st.session_state.current_url = url.strip()
                    perform_analysis(url.strip())
                else:
                    st.error(f"❌ {error_message}")
            else:
                st.warning("⚠️ Please enter a URL to analyze")
        
        # Analysis history
        if st.session_state.analysis_history:
            st.subheader("📝 Recent Analyses")
            for i, history_item in enumerate(reversed(st.session_state.analysis_history[-5:])):
                if st.button(f"🔗 {history_item['url'][:30]}...", key=f"history_{i}"):
                    st.session_state.current_url = history_item['url']
                    st.session_state.analysis_results = history_item['results']
    
    with col2:
        st.subheader("📊 Analysis Results")
        
        if st.session_state.analysis_results:
            render_results(st.session_state.analysis_results)
        else:
            st.info("👆 Enter a URL and click 'Analyze Website' to see results")
            
            # Show example analysis
            st.markdown("### 🎯 What you'll get:")
            st.markdown("""
            <div class="feature-card">
                <strong>📄 Content Summary</strong><br>
                Key insights and main themes from the website
            </div>
            
            <div class="feature-card">
                <strong>📈 SEO Analysis</strong><br>
                Meta tags, headings structure, and optimization tips
            </div>
            
            <div class="feature-card">
                <strong>📞 Contact Information</strong><br>
                Extracted emails, phone numbers, and social links
            </div>
            
            <div class="feature-card">
                <strong>🔍 Technical Details</strong><br>
                Word count, readability score, and language detection
            </div>
            """, unsafe_allow_html=True)

def perform_analysis(url: str):
    """Perform website analysis"""
    try:
        with st.spinner("🔄 Analyzing website..."):
            # Show progress indicator
            progress_placeholder = st.empty()
            render_progress_indicator(progress_placeholder, "Validating URL...")
            
            time.sleep(0.5)  # Simulate processing time
            
            render_progress_indicator(progress_placeholder, "Scraping content...")
            time.sleep(0.5)
            
            render_progress_indicator(progress_placeholder, "Processing content...")
            time.sleep(0.5)
            
            render_progress_indicator(progress_placeholder, "Generating analysis...")
            
            # Make API request
            api_client = get_api_client()
            results = api_client.analyze_url(url)
            
            # Clear progress indicator
            progress_placeholder.empty()
            
            # Store results
            st.session_state.analysis_results = results
            
            # Add to history
            st.session_state.analysis_history.append({
                "url": url,
                "timestamp": time.time(),
                "results": results
            })
            
            # Show success message
            st.success("✅ Analysis completed successfully!")
            
            # Rerun to update display
            st.rerun()
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error: {str(e)}")
        logger.error(f"Network error analyzing {url}: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        logger.error(f"Analysis error for {url}: {str(e)}", exc_info=True)

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Check backend status
    if not st.session_state.backend_status:
        with st.spinner("Connecting to backend..."):
            check_backend_status()
    
    # Render UI
    render_header()
    render_sidebar()
    render_main_content()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Web Content Analyzer v1.0.0 | Milestone 1 - Foundation Implementation
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
