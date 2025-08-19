"""URL Input Component for Streamlit Frontend"""
import streamlit as st
from typing import Dict, Any
from ..utils.validators import validate_url_input


class URLInputComponent:
    """Component for URL input and validation"""
    
    def __init__(self):
        self.key = "url_input"
    
    def render(self) -> str:
        """Render URL input component and return the URL value"""
        st.header("Input")
        
        # URL input with enhanced validation
        url_input = st.text_input(
            "Enter URL to analyze:",
            placeholder="https://example.com",
            help="Enter a valid HTTP/HTTPS URL",
            key=self.key
        )
        
        # Real-time URL validation feedback
        if url_input:
            validation_result = validate_url_input(url_input)
            if validation_result["valid"]:
                st.success(f"✅ Valid URL: {validation_result['domain']}")
            else:
                st.error(f"❌ {validation_result['error']}")
        
        return url_input
    
    def is_valid(self, url: str) -> bool:
        """Check if URL is valid"""
        if not url:
            return False
        return validate_url_input(url)["valid"]
    
    def render_action_buttons(self, url: str, backend_url: str, analyze_callback):
        """Render action buttons for analysis"""
        # Analysis button with conditional enabling
        analysis_disabled = not self.is_valid(url)
        
        # Analysis and retry buttons
        if st.button("🚀 Analyze Content", type="primary", disabled=analysis_disabled):
            analyze_callback(url, backend_url)
        
        if st.button("🔄 Retry", disabled=not st.session_state.get("last_failed_url")):
            if st.session_state.get("last_failed_url"):
                analyze_callback(st.session_state.last_failed_url, backend_url)
        
        # Error recovery section
        if st.session_state.get("last_error"):
            with st.expander("🔧 Troubleshooting", expanded=False):
                st.error(f"Last error: {st.session_state.last_error}")
                
                st.subheader("Suggested Actions:")
                st.write("• Check if the URL is accessible in your browser")
                st.write("• Verify the backend is running (use sidebar connection test)")
                st.write("• Try a different URL")
                st.write("• Wait a moment and retry")
                
                if st.button("Clear Error"):
                    st.session_state.last_error = None
                    st.session_state.last_failed_url = None
                    st.rerun()
    
    def render_examples(self):
        """Render example URLs for testing"""
        st.subheader("📚 Try These Examples")
        
        examples = [
            ("BBC News", "https://www.bbc.com/news"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Artificial_intelligence"),
            ("GitHub", "https://github.com"),
        ]
        
        cols = st.columns(len(examples))
        for i, (name, url) in enumerate(examples):
            with cols[i]:
                if st.button(f"📰 {name}"):
                    st.session_state[self.key] = url
                    st.rerun()
