"""Results Display Component for Streamlit Frontend"""
import streamlit as st
import time
from typing import Dict, Any
from ..utils.formatters import (
    format_content_metrics, 
    format_keywords_html, 
    format_content_insights,
    format_download_data,
    generate_download_filename
)


class ResultsDisplayComponent:
    """Component for displaying analysis results"""
    
    def __init__(self):
        pass
    
    def render_preview(self):
        """Render results preview in column"""
        st.header("Results")
        
        if "analysis_result" not in st.session_state:
            st.info("👆 Enter a URL and click 'Analyze Content' to see results")
        else:
            st.info("📊 Analysis completed! Detailed results are shown below.")
    
    def render_detailed_results(self, result: Dict[str, Any]):
        """Display detailed analysis results"""
        st.success("✅ Analysis completed successfully!")
        
        # Metrics section
        self._render_metrics(result)
        
        # Summary section
        self._render_summary(result)
        
        # Keywords section
        self._render_keywords(result)
        
        # Source information
        self._render_source_info(result)
        
        # Analysis insights
        self._render_insights(result)
        
        # Action buttons
        self._render_actions(result)
        
        # Raw data section
        self._render_raw_data(result)
    
    def _render_metrics(self, result: Dict[str, Any]):
        """Render analysis metrics"""
        st.subheader("📊 Analysis Metrics")
        
        metrics = format_content_metrics(result)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Content Length", 
                metrics['content_length'],
                help="Total character count of analyzed content"
            )
        with col2:
            st.metric(
                "Keywords Found", 
                metrics['keyword_count'],
                help="Number of extracted keywords"
            )
        with col3:
            st.metric(
                "Est. Words", 
                metrics['word_count'],
                help="Estimated word count"
            )
        with col4:
            st.metric(
                "Read Time", 
                metrics['read_time'],
                help="Estimated reading time"
            )
    
    def _render_summary(self, result: Dict[str, Any]):
        """Render content summary"""
        if result.get('summary'):
            st.subheader("📝 Content Summary")
            st.info(result['summary'])
    
    def _render_keywords(self, result: Dict[str, Any]):
        """Render keywords section"""
        if result.get('keywords'):
            st.subheader("🏷️ Key Topics & Keywords")
            keywords = result['keywords']
            
            # Display formatted keywords
            keyword_html = format_keywords_html(keywords)
            if keyword_html:
                st.markdown(keyword_html, unsafe_allow_html=True)
            
            # Show remaining keywords if any
            if len(keywords) > 15:
                with st.expander(f"View all {len(keywords)} keywords"):
                    remaining_keywords = keywords[15:]
                    st.write(", ".join(remaining_keywords))
    
    def _render_source_info(self, result: Dict[str, Any]):
        """Render source information"""
        if result.get('source_url'):
            st.subheader("🔗 Source Information")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_input("Source URL", value=result['source_url'], disabled=True)
            with col2:
                st.link_button("🌐 Open Original", result['source_url'])
    
    def _render_insights(self, result: Dict[str, Any]):
        """Render analysis insights"""
        st.subheader("🔍 Analysis Insights")
        
        insights = format_content_insights(result)
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.write("**Content Characteristics:**")
            for characteristic in insights['characteristics']:
                st.write(characteristic)
        
        with insights_col2:
            st.write("**Content Quality Indicators:**")
            for indicator in insights['quality_indicators']:
                st.write(indicator)
    
    def _render_actions(self, result: Dict[str, Any]):
        """Render action buttons"""
        st.subheader("🎬 Actions")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("💾 Save Results"):
                download_data = format_download_data(result)
                filename = generate_download_filename()
                st.download_button(
                    "📥 Download JSON",
                    download_data,
                    file_name=filename,
                    mime="application/json"
                )
        
        with action_col2:
            if st.button("📋 Copy Summary"):
                if result.get('summary'):
                    st.code(result['summary'])
                    st.info("Summary displayed above - copy manually")
        
        with action_col3:
            if st.button("🔄 Analyze Another"):
                if "analysis_result" in st.session_state:
                    del st.session_state.analysis_result
                st.rerun()
    
    def _render_raw_data(self, result: Dict[str, Any]):
        """Render raw data section"""
        with st.expander("🛠️ Raw Analysis Data", expanded=False):
            st.json(result)
