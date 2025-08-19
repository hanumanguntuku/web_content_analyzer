import streamlit as st
import requests
import json
import time
import re
from typing import Dict, Any
from urllib.parse import urlparse

# MUST be the first Streamlit command - configure page
st.set_page_config(
    page_title="Web Content Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Configuration
BACKEND_URL = "http://localhost:8000"

def validate_url_input(url: str) -> Dict[str, Any]:
    """Validate URL input and return validation result with feedback"""
    if not url:
        return {"valid": False, "error": "URL cannot be empty"}
    
    if not url.startswith(("http://", "https://")):
        return {"valid": False, "error": "URL must start with http:// or https://"}
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return {"valid": False, "error": "Invalid URL format"}
        
        # Check for basic domain structure
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$'
        if not re.match(domain_pattern, parsed.netloc.split(':')[0]):
            return {"valid": False, "error": "Invalid domain format"}
        
        return {"valid": True, "domain": parsed.netloc, "scheme": parsed.scheme}
    except Exception as e:
        return {"valid": False, "error": f"URL parsing error: {str(e)}"}

def analyze_content_with_progress(url: str, backend_url: str):
    """Enhanced analyze function with progress indicators and better error handling"""
    
    # Initialize session state for error tracking
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "last_failed_url" not in st.session_state:
        st.session_state.last_failed_url = None
    
    # Create progress indicators
    progress_container = st.container()
    
    with progress_container:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Validate connection
            status_text.text("🔗 Connecting to backend...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            # Test backend connection first
            try:
                health_response = requests.get(f"{backend_url}/health", timeout=5)
                if health_response.status_code != 200:
                    raise Exception("Backend health check failed")
            except Exception as e:
                st.error("🔌 Backend connection failed. Please ensure the backend is running.")
                st.session_state.last_error = f"Backend connection error: {str(e)}"
                st.session_state.last_failed_url = url
                return
            
            # Step 2: Preparing request
            status_text.text("📝 Preparing analysis request...")
            progress_bar.progress(25)
            time.sleep(0.3)
            
            # Step 3: Sending request
            status_text.text("🚀 Sending request to analyzer...")
            progress_bar.progress(40)
            
            payload = {"url": url}
            response = requests.post(
                f"{backend_url}/analyze",
                json=payload,
                timeout=60  # Increased timeout for longer analyses
            )
            
            # Step 4: Processing response
            status_text.text("⚙️ Processing response...")
            progress_bar.progress(70)
            time.sleep(0.3)
            
            if response.status_code == 200:
                # Step 5: Parsing results
                status_text.text("📊 Parsing analysis results...")
                progress_bar.progress(90)
                time.sleep(0.3)
                
                result = response.json()
                
                # Step 6: Complete
                status_text.text("✅ Analysis completed successfully!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Clear any previous errors
                st.session_state.last_error = None
                st.session_state.last_failed_url = None
                
                # Store and display results
                st.session_state.analysis_result = result
                
                # Clear progress indicators
                progress_container.empty()
                
                # Store results in session state for display outside columns
                st.session_state.analysis_result = result
                st.success("✅ Analysis completed successfully!")
                st.rerun()  # Refresh to show results
                
            else:
                # Handle HTTP errors
                error_message = f"Analysis failed with status {response.status_code}"
                try:
                    error_detail = response.json().get("detail", response.text)
                    error_message += f": {error_detail}"
                except:
                    error_message += f": {response.text}"
                
                st.error(f"❌ {error_message}")
                st.session_state.last_error = error_message
                st.session_state.last_failed_url = url
                
                # Show specific error guidance
                if response.status_code == 422:
                    st.warning("💡 Tip: Check if the URL format is correct")
                elif response.status_code == 500:
                    st.warning("💡 Tip: The website might be blocking our scraper or temporarily unavailable")
                
        except requests.exceptions.Timeout:
            error_msg = "⏰ Request timeout - the analysis took too long (>60 seconds)"
            st.error(error_msg)
            st.session_state.last_error = "Timeout error"
            st.session_state.last_failed_url = url
            st.info("💡 Try again with a different URL or check if the target site is responsive")
            
        except requests.exceptions.ConnectionError:
            error_msg = "🔌 Connection error - unable to reach the backend"
            st.error(error_msg)
            st.session_state.last_error = "Connection error"
            st.session_state.last_failed_url = url
            st.info("💡 Make sure the backend is running on the correct port")
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            st.error(error_msg)
            st.session_state.last_error = str(e)
            st.session_state.last_failed_url = url
            st.info("💡 Please try again or contact support if the issue persists")
        
        finally:
            # Ensure progress indicators are cleared
            try:
                progress_container.empty()
            except:
                pass

def main():
    st.title("🔍 Web Content Analyzer")
    st.markdown("Analyze web content with AI-powered insights")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings")
        backend_url = st.text_input("Backend URL", value=BACKEND_URL)
        
        # Health check
        if st.button("Test Connection"):
            try:
                response = requests.get(f"{backend_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Backend connected!")
                else:
                    st.error(f"❌ Backend error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Input")
        
        # URL input with enhanced validation
        url_input = st.text_input(
            "Enter URL to analyze:",
            placeholder="https://example.com",
            help="Enter a valid HTTP/HTTPS URL",
            key="url_input"
        )
        
        # Real-time URL validation feedback
        if url_input:
            validation_result = validate_url_input(url_input)
            if validation_result["valid"]:
                st.success(f"✅ Valid URL: {validation_result['domain']}")
            else:
                st.error(f"❌ {validation_result['error']}")
        
        # Analysis button with conditional enabling
        analysis_disabled = not (url_input and validate_url_input(url_input)["valid"])
        
        # Analysis and retry buttons in a single row without nested columns
        if st.button("🚀 Analyze Content", type="primary", disabled=analysis_disabled):
            analyze_content_with_progress(url_input, backend_url)
        
        if st.button("🔄 Retry", disabled=not st.session_state.get("last_failed_url")):
            if st.session_state.get("last_failed_url"):
                analyze_content_with_progress(st.session_state.last_failed_url, backend_url)
        
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
    
    with col2:
        st.header("Results")
        
        # Results preview in the column (simple display)
        if "analysis_result" not in st.session_state:
            st.info("👆 Enter a URL and click 'Analyze Content' to see results")
        else:
            st.info("📊 Analysis completed! Detailed results are shown below.")
    
    # Display detailed results outside of columns to avoid nesting issues
    if "analysis_result" in st.session_state:
        st.divider()
        display_results(st.session_state.analysis_result)

def display_results(result: Dict[str, Any]):
    """Display analysis results in a formatted way with enhanced metrics"""
    
    st.success("✅ Analysis completed successfully!")
    
    # Metrics row
    st.subheader("📊 Analysis Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Content Length", 
            f"{result.get('content_length', 0):,} chars",
            help="Total character count of analyzed content"
        )
    with col2:
        st.metric(
            "Keywords Found", 
            len(result.get('keywords', [])),
            help="Number of extracted keywords"
        )
    with col3:
        word_count = result.get('content_length', 0) // 5  # Rough estimate
        st.metric(
            "Est. Words", 
            f"{word_count:,}",
            help="Estimated word count"
        )
    with col4:
        read_time = max(1, word_count // 200)  # Average reading speed
        st.metric(
            "Read Time", 
            f"{read_time} min",
            help="Estimated reading time"
        )
    
    # Summary section
    if result.get('summary'):
        st.subheader("📝 Content Summary")
        st.info(result['summary'])
    
    # Keywords section with improved visualization
    if result.get('keywords'):
        st.subheader("🏷️ Key Topics & Keywords")
        keywords = result['keywords']
        
        # Create a more visual keyword display
        keyword_html = ""
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF"]
        
        for i, keyword in enumerate(keywords[:15]):  # Show top 15
            color = colors[i % len(colors)]
            keyword_html += f"""
            <span style="
                background-color: {color}; 
                color: white; 
                padding: 0.3rem 0.6rem; 
                margin: 0.2rem; 
                border-radius: 1rem; 
                font-size: 0.9rem;
                display: inline-block;
                font-weight: 500;
            ">{keyword}</span>
            """
        
        st.markdown(keyword_html, unsafe_allow_html=True)
        
        if len(keywords) > 15:
            with st.expander(f"View all {len(keywords)} keywords"):
                remaining_keywords = keywords[15:]
                st.write(", ".join(remaining_keywords))
    
    # Source information
    if result.get('source_url'):
        st.subheader("🔗 Source Information")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Source URL", value=result['source_url'], disabled=True)
        with col2:
            st.link_button("🌐 Open Original", result['source_url'])
    
    # Additional analysis insights
    st.subheader("🔍 Analysis Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.write("**Content Characteristics:**")
        content_length = result.get('content_length', 0)
        if content_length > 5000:
            st.write("• 📄 Long-form content")
        elif content_length > 1000:
            st.write("• 📝 Medium-length content")
        else:
            st.write("• 📃 Short-form content")
        
        keyword_count = len(result.get('keywords', []))
        if keyword_count > 10:
            st.write("• 🎯 Rich topic diversity")
        elif keyword_count > 5:
            st.write("• 📚 Moderate topic coverage")
        else:
            st.write("• 🎪 Focused topic scope")
    
    with insights_col2:
        st.write("**Content Quality Indicators:**")
        if result.get('summary'):
            st.write("• ✅ Summary extractable")
        if keyword_count > 0:
            st.write("• ✅ Keywords identified")
        if content_length > 100:
            st.write("• ✅ Substantial content")
    
    # Action buttons
    st.subheader("🎬 Actions")
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("💾 Save Results"):
            # Convert to downloadable format
            download_data = json.dumps(result, indent=2)
            st.download_button(
                "📥 Download JSON",
                download_data,
                file_name=f"analysis_{int(time.time())}.json",
                mime="application/json"
            )
    
    with action_col2:
        if st.button("📋 Copy Summary"):
            if result.get('summary'):
                st.code(result['summary'])
                st.info("Summary displayed above - copy manually")
    
    with action_col3:
        if st.button("🔄 Analyze Another"):
            # Clear current results to start fresh
            if "analysis_result" in st.session_state:
                del st.session_state.analysis_result
            st.rerun()
    
    # Raw data section (collapsible)
    with st.expander("�️ Raw Analysis Data", expanded=False):
        st.json(result)

def add_examples():
    """Add example URLs for testing"""
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
                st.session_state.example_url = url
                st.rerun()

if __name__ == "__main__":
    # Add examples section
    with st.container():
        add_examples()
        st.divider()
    
    main()
