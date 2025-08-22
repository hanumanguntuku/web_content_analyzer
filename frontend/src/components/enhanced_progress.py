"""
Enhanced Progress Indicator Component - M1-PRES-03 Implementation
Real-time progress tracking for analysis with detailed status updates
"""
import streamlit as st
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

def render_progress_indicator(
    current_stage: str = "initializing",
    progress_percentage: float = 0,
    estimated_time_remaining: Optional[float] = None,
    detailed_status: Optional[str] = None
):
    """
    Render enhanced progress indicator with detailed status
    
    Args:
        current_stage: Current processing stage
        progress_percentage: Progress as percentage (0-100)
        estimated_time_remaining: Estimated seconds remaining
        detailed_status: Detailed status message
    """
    
    # Stage definitions with descriptions
    stages = {
        "initializing": {
            "name": "Initializing",
            "icon": "🚀",
            "description": "Setting up analysis pipeline..."
        },
        "security_validation": {
            "name": "Security Validation",
            "icon": "🛡️",
            "description": "Validating URL and performing security checks..."
        },
        "web_scraping": {
            "name": "Web Scraping",
            "icon": "🌐",
            "description": "Fetching content from the website..."
        },
        "content_extraction": {
            "name": "Content Extraction",
            "icon": "📄",
            "description": "Extracting meaningful content from the page..."
        },
        "text_processing": {
            "name": "Text Processing",
            "icon": "🔤",
            "description": "Analyzing text content and extracting insights..."
        },
        "report_generation": {
            "name": "Report Generation",
            "icon": "📊",
            "description": "Generating comprehensive analysis report..."
        },
        "completed": {
            "name": "Completed",
            "icon": "✅",
            "description": "Analysis completed successfully!"
        },
        "error": {
            "name": "Error",
            "icon": "❌",
            "description": "An error occurred during analysis."
        }
    }
    
    # Current stage info
    stage_info = stages.get(current_stage, stages["initializing"])
    
    # Progress header
    st.markdown("## 🔄 Analysis in Progress")
    
    # Current stage display
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown(f"### {stage_info['icon']}")
    
    with col2:
        st.markdown(f"### {stage_info['name']}")
        st.write(stage_info['description'])
        
        if detailed_status:
            st.caption(detailed_status)
    
    # Progress bar
    progress_bar = st.progress(progress_percentage / 100)
    
    # Progress percentage and time remaining
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Progress", f"{progress_percentage:.1f}%")
    
    with col2:
        if estimated_time_remaining is not None:
            if estimated_time_remaining > 60:
                time_display = f"{estimated_time_remaining/60:.1f} min"
            else:
                time_display = f"{estimated_time_remaining:.0f} sec"
            st.metric("Est. Time Remaining", time_display)
        else:
            st.metric("Est. Time Remaining", "Calculating...")
    
    with col3:
        # Show current time
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("Current Time", current_time)
    
    # Stage progress visualization
    render_stage_progress_visual(current_stage, stages)
    
    # Live logs section
    if detailed_status:
        with st.expander("📋 Live Analysis Logs"):
            st.text_area(
                "Analysis Progress",
                value=detailed_status,
                height=100,
                disabled=True
            )

def render_stage_progress_visual(current_stage: str, stages: Dict[str, Dict[str, str]]):
    """Render visual stage progress"""
    st.markdown("### 📈 Analysis Stages")
    
    # Define stage order
    stage_order = [
        "initializing",
        "security_validation", 
        "web_scraping",
        "content_extraction",
        "text_processing",
        "report_generation",
        "completed"
    ]
    
    # Current stage index
    try:
        current_index = stage_order.index(current_stage)
    except ValueError:
        current_index = 0
    
    # Create columns for each stage
    cols = st.columns(len(stage_order))
    
    for i, (col, stage_key) in enumerate(zip(cols, stage_order)):
        stage = stages.get(stage_key, {"name": stage_key, "icon": "❓"})
        
        with col:
            if i < current_index:
                # Completed stage
                st.markdown(f"✅ **{stage['name']}**")
            elif i == current_index:
                # Current stage
                st.markdown(f"🔄 **{stage['name']}**")
            else:
                # Pending stage
                st.markdown(f"⏳ {stage['name']}")

def create_analysis_progress_tracker():
    """Create a progress tracker that can be updated during analysis"""
    
    # Initialize session state for progress tracking
    if 'analysis_progress' not in st.session_state:
        st.session_state.analysis_progress = {
            'stage': 'initializing',
            'progress': 0,
            'start_time': time.time(),
            'logs': []
        }
    
    return st.session_state.analysis_progress

def update_progress(
    stage: str,
    progress: float,
    status: str = None,
    log_message: str = None
):
    """Update progress in session state"""
    
    if 'analysis_progress' in st.session_state:
        st.session_state.analysis_progress.update({
            'stage': stage,
            'progress': progress,
            'status': status,
            'last_update': time.time()
        })
        
        if log_message:
            st.session_state.analysis_progress['logs'].append({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'message': log_message
            })

def render_analysis_status_card(analysis_config: Dict[str, Any]):
    """Render a status card showing analysis configuration"""
    
    st.markdown("### 📋 Analysis Configuration")
    
    with st.container():
        # URL being analyzed
        st.info(f"🔗 **Analyzing:** {analysis_config.get('url', 'Unknown URL')}")
        
        # Configuration details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Deep Analysis:**", "✅" if analysis_config.get('deep_analysis') else "❌")
            st.write("**Extract Images:**", "✅" if analysis_config.get('extract_images') else "❌")
        
        with col2:
            st.write("**Extract Links:**", "✅" if analysis_config.get('extract_links') else "❌")
            st.write("**Timeout:**", f"{analysis_config.get('timeout_seconds', 30)}s")

def render_cancellation_option():
    """Render option to cancel analysis"""
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("❌ Cancel Analysis", type="secondary"):
            # Clear analysis state
            if 'analysis_progress' in st.session_state:
                del st.session_state['analysis_progress']
            if 'current_analysis_config' in st.session_state:
                del st.session_state['current_analysis_config']
            
            st.warning("Analysis cancelled.")
            st.experimental_rerun()

def simulate_analysis_progress():
    """Simulate analysis progress for demonstration"""
    
    stages = [
        ("initializing", 10, "Initializing analysis components..."),
        ("security_validation", 25, "Validating URL security..."),
        ("web_scraping", 45, "Scraping website content..."),
        ("content_extraction", 65, "Extracting meaningful content..."),
        ("text_processing", 85, "Processing and analyzing text..."),
        ("report_generation", 95, "Generating analysis report..."),
        ("completed", 100, "Analysis completed successfully!")
    ]
    
    # Create placeholder for progress
    progress_placeholder = st.empty()
    
    for stage, progress, status in stages:
        with progress_placeholder.container():
            render_progress_indicator(
                current_stage=stage,
                progress_percentage=progress,
                estimated_time_remaining=max(0, (100 - progress) * 0.5),
                detailed_status=status
            )
        
        # Simulate processing time
        time.sleep(2)
    
    return True

def render_progress_section(analysis_config: Optional[Dict[str, Any]] = None):
    """
    Main function to render the progress section
    
    Args:
        analysis_config: Configuration for the current analysis
    """
    
    if analysis_config:
        # Show analysis configuration
        render_analysis_status_card(analysis_config)
        
        # Show progress
        progress_tracker = create_analysis_progress_tracker()
        
        render_progress_indicator(
            current_stage=progress_tracker.get('stage', 'initializing'),
            progress_percentage=progress_tracker.get('progress', 0),
            detailed_status=progress_tracker.get('status')
        )
        
        # Show cancellation option
        render_cancellation_option()
        
    else:
        st.info("No analysis in progress.")

# Progress update utilities for integration with backend
class ProgressReporter:
    """Utility class for reporting progress during analysis"""
    
    def __init__(self):
        self.start_time = time.time()
        self.current_stage = "initializing"
        self.progress = 0
    
    def update_stage(self, stage: str, progress: float, status: str = None):
        """Update the current analysis stage"""
        self.current_stage = stage
        self.progress = progress
        
        # Update session state if available
        update_progress(stage, progress, status)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since analysis started"""
        return time.time() - self.start_time
    
    def estimate_remaining_time(self) -> float:
        """Estimate remaining time based on current progress"""
        if self.progress <= 0:
            return 60  # Default estimate
        
        elapsed = self.get_elapsed_time()
        estimated_total = (elapsed / self.progress) * 100
        return max(0, estimated_total - elapsed)
