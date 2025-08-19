"""State Management for Streamlit Frontend"""
import streamlit as st
from typing import Dict, Any, Optional


class StateManager:
    """Manage Streamlit session state"""
    
    def __init__(self):
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize session state variables"""
        if "last_error" not in st.session_state:
            st.session_state.last_error = None
        if "last_failed_url" not in st.session_state:
            st.session_state.last_failed_url = None
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "backend_url" not in st.session_state:
            st.session_state.backend_url = "http://localhost:8000"
    
    def set_error(self, error: str, failed_url: Optional[str] = None):
        """Set error state"""
        st.session_state.last_error = error
        if failed_url:
            st.session_state.last_failed_url = failed_url
    
    def clear_error(self):
        """Clear error state"""
        st.session_state.last_error = None
        st.session_state.last_failed_url = None
    
    def set_analysis_result(self, result: Dict[str, Any]):
        """Set analysis result"""
        st.session_state.analysis_result = result
        self.clear_error()  # Clear any previous errors
    
    def clear_analysis_result(self):
        """Clear analysis result"""
        if "analysis_result" in st.session_state:
            del st.session_state.analysis_result
    
    def get_analysis_result(self) -> Optional[Dict[str, Any]]:
        """Get current analysis result"""
        return st.session_state.get("analysis_result")
    
    def has_analysis_result(self) -> bool:
        """Check if analysis result exists"""
        return "analysis_result" in st.session_state and st.session_state.analysis_result is not None
    
    def get_last_error(self) -> Optional[str]:
        """Get last error"""
        return st.session_state.get("last_error")
    
    def get_last_failed_url(self) -> Optional[str]:
        """Get last failed URL"""
        return st.session_state.get("last_failed_url")
    
    def has_error(self) -> bool:
        """Check if there's an error"""
        return bool(st.session_state.get("last_error"))
    
    def set_backend_url(self, url: str):
        """Set backend URL"""
        st.session_state.backend_url = url
    
    def get_backend_url(self) -> str:
        """Get backend URL"""
        return st.session_state.get("backend_url", "http://localhost:8000")
    
    def reset_all(self):
        """Reset all state"""
        self.clear_error()
        self.clear_analysis_result()


# Global state manager instance
state_manager = StateManager()
