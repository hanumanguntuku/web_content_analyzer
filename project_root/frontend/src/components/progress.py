"""Progress Component for Streamlit Frontend"""
import streamlit as st
import time
from typing import Optional


class ProgressComponent:
    """Component for displaying progress indicators during analysis"""
    
    def __init__(self):
        self.progress_container = None
        self.progress_bar = None
        self.status_text = None
    
    def initialize(self):
        """Initialize progress components"""
        self.progress_container = st.container()
        
        with self.progress_container:
            self.progress_bar = st.progress(0)
            self.status_text = st.empty()
    
    def update(self, progress: int, message: str, delay: float = 0.3):
        """Update progress bar and status message"""
        if self.progress_bar and self.status_text:
            self.status_text.text(message)
            self.progress_bar.progress(progress)
            if delay > 0:
                time.sleep(delay)
    
    def show_step(self, step: str, progress: int, delay: float = 0.3):
        """Show a specific step with predefined messages"""
        steps = {
            "connecting": ("🔗 Connecting to backend...", 10),
            "preparing": ("📝 Preparing analysis request...", 25),
            "sending": ("🚀 Sending request to analyzer...", 40),
            "processing": ("⚙️ Processing response...", 70),
            "parsing": ("📊 Parsing analysis results...", 90),
            "complete": ("✅ Analysis completed successfully!", 100)
        }
        
        if step in steps:
            message, default_progress = steps[step]
            self.update(progress or default_progress, message, delay)
    
    def clear(self):
        """Clear progress indicators"""
        if self.progress_container:
            try:
                self.progress_container.empty()
            except:
                pass
    
    def show_error(self, message: str):
        """Show error message and clear progress"""
        if self.status_text:
            self.status_text.error(f"❌ {message}")
        self.clear()
    
    def show_success(self, message: str = "Analysis completed successfully!"):
        """Show success message"""
        if self.status_text:
            self.status_text.success(f"✅ {message}")
            time.sleep(1)
        self.clear()
