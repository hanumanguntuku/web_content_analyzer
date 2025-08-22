"""
Enhanced Web Content Analyzer - M1-PRES-05 Implementation
Complete Streamlit frontend integrating all Milestone 1 features
"""
import streamlit as st
import time
import threading
from typing import Dict, Any, Optional
import logging

# Import enhanced components
from src.components.enhanced_url_input import render_url_input_section
from src.components.enhanced_results_display import render_enhanced_results
from src.components.enhanced_progress import (
    render_progress_section,
    ProgressReporter,
    update_progress
)
from src.services.enhanced_api_client import (
    get_api_client,
    test_backend_connection,
    analyze_website
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Web Content Analyzer - Milestone 1",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/hanumanguntuku/web_content_analyzer',
        'Report a bug': 'https://github.com/hanumanguntuku/web_content_analyzer/issues',
        'About': """
        # Web Content Analyzer - Milestone 1
        
        **Intelligent Content Processing System**
        
        **Key Features:**
        - 🛡️ Security-first approach with SSRF prevention
        - 🧠 Intelligent content extraction with noise removal
        - 📊 Deep text processing and analysis
        - 🔍 Keyword extraction and sentiment analysis
        - ⚡ Real-time progress tracking
        - 📈 Comprehensive performance metrics
        
        **Milestone 1 Implementation:**
        - ✅ Phase 1: Infrastructure Foundation
        - ✅ Phase 2: Data Layer Implementation
        - ✅ Phase 3: Security Implementation
        - ✅ Phase 4: Service Layer Integration
        - ✅ Phase 5: Presentation Layer
        
        **Version:** 1.0.0 (Milestone 1)
        """
    }
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Status indicators */
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-unhealthy {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-degraded {
        color: #ffc107;
        font-weight: bold;
    }
    
    /* Progress indicators */
    .progress-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Results styling */
    .results-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Error styling */
    .error-container {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success styling */
    .success-container {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def render_app_header():
    """Render the main application header"""
    st.markdown("""
    <div class="app-header">
        <h1>🔍 Web Content Analyzer</h1>
        <h3>Intelligent Content Processing - Milestone 1</h3>
        <p>Secure • Intelligent • Comprehensive</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the enhanced sidebar with system information"""
    with st.sidebar:
        st.markdown("## 🛠️ System Information")
        
        # Backend connection status
        st.markdown("### 🌐 Backend Status")
        
        # Check backend connection
        backend_status = test_backend_connection()
        
        if backend_status["available"]:
            st.markdown('<p class="status-healthy">✅ Connected</p>', unsafe_allow_html=True)
            
            # Show backend details if available
            if "data" in backend_status:
                data = backend_status["data"]
                st.write(f"**Environment:** {data.get('environment', 'Unknown')}")
                st.write(f"**Version:** {data.get('version', 'Unknown')}")
                
                # Health information
                health_info = data.get('health', {})
                if health_info:
                    status = health_info.get('status', 'unknown')
                    if status == 'healthy':
                        st.markdown('<p class="status-healthy">🟢 System Healthy</p>', unsafe_allow_html=True)
                    elif status == 'degraded':
                        st.markdown('<p class="status-degraded">🟡 System Degraded</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="status-unhealthy">🔴 System Unhealthy</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-unhealthy">❌ Disconnected</p>', unsafe_allow_html=True)
            st.error(f"Error: {backend_status.get('error', 'Unknown error')}")
            
            st.markdown("### 🔧 Troubleshooting")
            st.info("""
            **Backend connection failed:**
            1. Ensure the backend server is running
            2. Check the server URL configuration
            3. Verify network connectivity
            4. Check firewall settings
            """)
        
        # Feature status
        st.markdown("### ✨ Features")
        st.write("🛡️ Security Validation")
        st.write("🧠 Content Extraction")
        st.write("📊 Text Processing")
        st.write("🔍 Deep Analysis")
        st.write("📈 Performance Metrics")
        
        # System capabilities
        st.markdown("### 🎯 Capabilities")
        st.write("• SSRF Prevention")
        st.write("• XSS Protection")
        st.write("• Rate Limiting")
        st.write("• Content Sanitization")
        st.write("• Intelligent Extraction")
        st.write("• Sentiment Analysis")
        st.write("• Keyword Extraction")
        st.write("• Real-time Progress")
        
        # Performance stats (if available)
        if backend_status["available"]:
            if st.button("📊 View System Stats"):
                st.session_state.show_stats = True

def render_system_stats():
    """Render system performance statistics"""
    if st.session_state.get('show_stats', False):
        st.markdown("## 📊 System Performance Statistics")
        
        try:
            client = get_api_client()
            stats_result = client.get_service_stats()
            
            if not stats_result.get("error"):
                stats = stats_result.get("performance_stats", {})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Analyses",
                        stats.get("total_analyses", 0)
                    )
                
                with col2:
                    success_rate = stats.get("success_rate", 0)
                    st.metric(
                        "Success Rate",
                        f"{success_rate:.1f}%"
                    )
                
                with col3:
                    avg_time = stats.get("average_processing_time", 0)
                    st.metric(
                        "Avg. Processing Time",
                        f"{avg_time:.2f}s"
                    )
                
                with col4:
                    security_blocks = stats.get("security_blocks", 0)
                    st.metric(
                        "Security Blocks",
                        security_blocks
                    )
                
                # Detailed stats
                with st.expander("Detailed Statistics"):
                    st.json(stats)
            
            else:
                st.error(f"Could not retrieve statistics: {stats_result.get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error retrieving statistics: {str(e)}")
        
        if st.button("❌ Close Stats"):
            st.session_state.show_stats = False
            st.experimental_rerun()

def progress_callback(stage: str, progress: float, status: str):
    """Progress callback function for API client"""
    update_progress(stage, progress, status, f"Stage: {stage} - {status}")

def main():
    """Main application function"""
    
    # Render header
    render_app_header()
    
    # Render sidebar
    render_sidebar()
    
    # Show system stats if requested
    if st.session_state.get('show_stats', False):
        render_system_stats()
        return
    
    # Check if we have an analysis in progress
    if 'analysis_in_progress' in st.session_state and st.session_state.analysis_in_progress:
        st.markdown("## 🔄 Analysis in Progress")
        
        # Show progress
        render_progress_section(st.session_state.get('current_analysis_config'))
        
        # Simulate progress updates (in real implementation, this would be handled by the API)
        if 'analysis_start_time' not in st.session_state:
            st.session_state.analysis_start_time = time.time()
        
        elapsed = time.time() - st.session_state.analysis_start_time
        
        # Simulate completion after some time
        if elapsed > 10:  # 10 seconds for demo
            st.session_state.analysis_in_progress = False
            st.session_state.analysis_complete = True
            st.experimental_rerun()
        
        # Auto-refresh every 2 seconds
        time.sleep(2)
        st.experimental_rerun()
    
    # Check if analysis is complete
    elif st.session_state.get('analysis_complete', False):
        
        # Show results if we have them
        if 'analysis_result' in st.session_state:
            render_enhanced_results(st.session_state.analysis_result)
        else:
            st.warning("Analysis completed but no results available.")
        
        # Option to start new analysis
        if st.button("🔄 Analyze Another URL"):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith('analysis_'):
                    del st.session_state[key]
            if 'current_analysis_config' in st.session_state:
                del st.session_state['current_analysis_config']
            st.experimental_rerun()
    
    # Main URL input and analysis initiation
    else:
        st.markdown("## 🚀 Start Analysis")
        
        # Render URL input section
        analysis_config = render_url_input_section()
        
        if analysis_config:
            # Start analysis
            st.markdown("---")
            st.markdown("### 🔍 Starting Analysis...")
            
            # Store configuration
            st.session_state.current_analysis_config = analysis_config
            
            # Perform analysis
            try:
                with st.spinner("Initializing analysis..."):
                    result = analyze_website(
                        url=analysis_config["url"],
                        analysis_config=analysis_config,
                        progress_callback=progress_callback
                    )
                
                # Store result and show
                st.session_state.analysis_result = result
                st.session_state.analysis_complete = True
                st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                
                # Show error details
                st.session_state.analysis_result = {
                    "error": True,
                    "error_type": "CLIENT_ERROR",
                    "message": "Analysis failed due to an unexpected error",
                    "technical_details": str(e)
                }
                st.session_state.analysis_complete = True
                st.experimental_rerun()

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'show_stats' not in st.session_state:
        st.session_state.show_stats = False

if __name__ == "__main__":
    # Initialize session state
    initialize_session_state()
    
    # Run main application
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)
