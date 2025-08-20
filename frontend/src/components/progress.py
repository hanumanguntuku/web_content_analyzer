"""
Progress Indicator Component
Streamlit component for showing analysis progress
"""
import streamlit as st
import time
from typing import Optional, Any

def render_progress_indicator(
    placeholder: Any, 
    message: str,
    progress: Optional[float] = None
) -> None:
    """
    Render progress indicator with message
    
    Args:
        placeholder: Streamlit placeholder to render progress in
        message: Progress message to display
        progress: Optional progress value (0.0 to 1.0)
    """
    
    with placeholder.container():
        if progress is not None:
            st.progress(progress, text=message)
        else:
            # Animated progress bar
            progress_bar = st.progress(0, text=message)
            
            # Simple animation
            for i in range(1, 101, 10):
                progress_bar.progress(i, text=f"{message} ({i}%)")
                time.sleep(0.1)
            
            progress_bar.progress(100, text=f"{message} Complete!")

def render_analysis_steps() -> None:
    """Render analysis steps overview"""
    st.markdown("### 🔄 Analysis Process")
    
    steps = [
        "🔍 URL Validation & Security Check",
        "🌐 Website Content Scraping", 
        "🧹 Content Cleaning & Processing",
        "🤖 AI Analysis & Insights Generation",
        "📊 Report Generation & Formatting"
    ]
    
    for i, step in enumerate(steps):
        st.markdown(f"{i+1}. {step}")

def show_loading_animation(message: str = "Processing...") -> None:
    """Show loading animation with spinner"""
    with st.spinner(message):
        time.sleep(1)  # Simulate processing time
