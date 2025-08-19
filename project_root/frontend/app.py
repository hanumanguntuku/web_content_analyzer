"""Main Streamlit Application - Modular Architecture"""
import streamlit as st
from src.components.url_input import URLInputComponent
from src.components.results_display import ResultsDisplayComponent
from src.components.progress import ProgressComponent
from src.services.api_client import api_client
from src.services.state_manager import state_manager

# MUST be the first Streamlit command - configure page
st.set_page_config(
    page_title="Web Content Analyzer",
    page_icon="🔍",
    layout="wide"
)


def analyze_content_with_progress(url: str, backend_url: str):
    """Enhanced analyze function with progress indicators and better error handling"""
    
    # Update API client with current backend URL
    api_client.set_base_url(backend_url)
    
    # Initialize progress component
    progress = ProgressComponent()
    progress.initialize()
    
    try:
        # Step 1: Validate connection
        progress.show_step("connecting", 10)
        
        # Step 2: Preparing request
        progress.show_step("preparing", 25)
        
        # Step 3: Sending request
        progress.show_step("sending", 40)
        
        # Call API
        result = api_client.analyze_content(url)
        
        if result["success"]:
            # Step 4: Processing response
            progress.show_step("processing", 70)
            
            # Step 5: Parsing results
            progress.show_step("parsing", 90)
            
            # Step 6: Complete
            progress.show_step("complete", 100)
            progress.show_success()
            
            # Store results
            state_manager.set_analysis_result(result["data"])
            st.success("✅ Analysis completed successfully!")
            st.rerun()  # Refresh to show results
            
        else:
            # Handle API errors
            error_message = result["error"]
            error_type = result.get("error_type", "unknown")
            status_code = result.get("status_code")
            
            st.error(f"❌ {error_message}")
            state_manager.set_error(error_message, url)
            
            # Show specific error guidance
            guidance = api_client.get_error_guidance(error_type, status_code)
            if guidance:
                st.warning(guidance)
                
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        st.error(error_msg)
        state_manager.set_error(str(e), url)
        st.info("💡 Please try again or contact support if the issue persists")
    
    finally:
        # Ensure progress indicators are cleared
        progress.clear()


def render_sidebar():
    """Render sidebar with settings"""
    with st.sidebar:
        st.header("Settings")
        
        # Backend URL configuration
        backend_url = st.text_input(
            "Backend URL", 
            value=state_manager.get_backend_url(),
            key="backend_url_input"
        )
        
        # Update state manager if URL changed
        if backend_url != state_manager.get_backend_url():
            state_manager.set_backend_url(backend_url)
            api_client.set_base_url(backend_url)
        
        # Health check
        if st.button("Test Connection"):
            result = api_client.test_connection()
            if result["success"]:
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ {result['message']}")


def render_examples():
    """Render example URLs section"""
    url_component = URLInputComponent()
    url_component.render_examples()


def main():
    """Main application function"""
    st.title("🔍 Web Content Analyzer")
    st.markdown("Analyze web content with AI-powered insights")
    
    # Render sidebar
    render_sidebar()
    
    # Initialize components
    url_component = URLInputComponent()
    results_component = ResultsDisplayComponent()
    
    # Main interface layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # URL input section
        url_input = url_component.render()
        
        # Action buttons
        backend_url = state_manager.get_backend_url()
        url_component.render_action_buttons(
            url_input, 
            backend_url, 
            analyze_content_with_progress
        )
    
    with col2:
        # Results preview
        results_component.render_preview()
    
    # Display detailed results outside of columns to avoid nesting issues
    if state_manager.has_analysis_result():
        st.divider()
        result = state_manager.get_analysis_result()
        results_component.render_detailed_results(result)


if __name__ == "__main__":
    # Add examples section
    with st.container():
        render_examples()
        st.divider()
    
    # Run main application
    main()
