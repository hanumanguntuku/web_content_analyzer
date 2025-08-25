# """
# Results Display Component
# Streamlit component for displaying analysis results
# """
# import streamlit as st
# import json
# from typing import Dict, Any, List
# import time

# def format_timestamp(timestamp: float) -> str:
#     """Format timestamp for display"""
#     return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

# def render_summary_card(results: Dict[str, Any]) -> None:
#     """Render summary card with key metrics"""
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric(
#             label="📄 Word Count",
#             value=results.get('word_count', 0)
#         )
    
#     with col2:
#         readability = results.get('readability_score', 0)
#         st.metric(
#             label="📈 Readability",
#             value=f"{readability:.1f}/100"
#         )
    
#     with col3:
#         st.metric(
#             label="🌐 Language",
#             value=results.get('language', 'Unknown').upper()
#         )
    
#     with col4:
#         processing_time = results.get('processing_time', 0)
#         st.metric(
#             label="⚡ Processing Time",
#             value=f"{processing_time:.2f}s"
#         )

# def render_content_summary(results: Dict[str, Any]) -> None:
#     """Render content summary section"""
#     st.subheader("📋 Content Summary")
    
#     # Title
#     title = results.get('title', 'No title found')
#     st.markdown(f"**Title:** {title}")
    
#     # Summary
#     summary = results.get('summary', 'No summary available')
#     st.markdown(f"**Summary:** {summary}")
    
#     # Content type
#     content_type = results.get('content_type', 'Unknown')
#     st.markdown(f"**Type:** {content_type.replace('_', ' ').title()}")

# def render_keywords(results: Dict[str, Any]) -> None:
#     """Render keywords section"""
#     keywords = results.get('keywords', [])
    
#     if keywords:
#         st.subheader("🏷️ Keywords")
        
#         # Display keywords as tags
#         keyword_html = " ".join([
#             f'<span style="background: #FF6B6B; color: white; padding: 0.25rem 0.5rem; '
#             f'border-radius: 12px; margin: 0.1rem; display: inline-block; font-size: 0.8rem;">'
#             f'{keyword}</span>'
#             for keyword in keywords[:10]  # Show max 10 keywords
#         ])
        
#         st.markdown(keyword_html, unsafe_allow_html=True)
#     else:
#         st.info("No keywords extracted")

# def render_sections(results: Dict[str, Any]) -> None:
#     """Render content sections"""
#     sections = results.get('key_sections', [])
    
#     if sections:
#         st.subheader("📑 Content Sections")
        
#         for i, section in enumerate(sections):
#             with st.expander(f"📄 {section.get('title', f'Section {i+1}')}"):
#                 content = section.get('content', 'No content available')
#                 word_count = section.get('word_count', 0)
                
#                 st.markdown(f"**Word Count:** {word_count}")
#                 st.markdown("**Content:**")
#                 st.text_area(
#                     label="",
#                     value=content[:500] + ("..." if len(content) > 500 else ""),
#                     height=100,
#                     disabled=True,
#                     key=f"section_content_{i}"
#                 )
#     else:
#         st.info("No content sections found")

# def render_contact_info(results: Dict[str, Any]) -> None:
#     """Render contact information"""
#     contact_info = results.get('contact_information', {})
    
#     if any(contact_info.values()):
#         st.subheader("📞 Contact Information")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             emails = contact_info.get('emails', [])
#             if emails:
#                 st.markdown("**📧 Emails:**")
#                 for email in emails:
#                     st.text(email)
        
#         with col2:
#             phones = contact_info.get('phones', [])
#             if phones:
#                 st.markdown("**📱 Phone Numbers:**")
#                 for phone in phones:
#                     st.text(phone)
        
#         with col3:
#             urls = contact_info.get('urls', [])
#             if urls:
#                 st.markdown("**🔗 Related URLs:**")
#                 for url in urls[:3]:  # Show max 3 URLs
#                     st.text(url)
#     else:
#         st.info("No contact information found")

# def render_metadata(results: Dict[str, Any]) -> None:
#     """Render metadata and technical details"""
#     metadata = results.get('metadata', {})
    
#     if metadata:
#         st.subheader("🔧 Technical Details")
        
#         with st.expander("View Metadata"):
#             # Analysis details
#             st.markdown("**Analysis Information:**")
#             analysis_time = results.get('analysis_timestamp', 0)
#             st.text(f"Analysis Time: {format_timestamp(analysis_time)}")
#             st.text(f"URL: {results.get('url', 'N/A')}")
            
#             # Raw metadata
#             st.markdown("**Raw Metadata:**")
#             st.json(metadata, expanded=False)

# def render_export_options(results: Dict[str, Any]) -> None:
#     """Render export options (placeholder for future implementation)"""
#     st.subheader("💾 Export Options")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if st.button("📄 Export as JSON", disabled=True):
#             st.info("JSON export will be available in Milestone 3")
    
#     with col2:
#         if st.button("📊 Export as PDF", disabled=True):
#             st.info("PDF export will be available in Milestone 3")
    
#     with col3:
#         if st.button("📈 Export as CSV", disabled=True):
#             st.info("CSV export will be available in Milestone 3")

# def render_structured_data(results: Dict[str, Any]) -> None:
#     """Render JSON-LD and microdata if present"""
#     metadata = results.get('metadata', {})
#     jsonld = metadata.get('jsonld', [])
#     microdata = metadata.get('microdata', [])
#     if jsonld or microdata:
#         st.subheader("🧩 Structured Data (JSON-LD & Microdata)")
#         if jsonld:
#             with st.expander("JSON-LD Blocks", expanded=False):
#                 for i, block in enumerate(jsonld):
#                     st.json(block, expanded=False)
#         if microdata:
#             with st.expander("Microdata Items", expanded=False):
#                 for i, item in enumerate(microdata):
#                     st.json(item, expanded=False)

# def render_ai_summary(results: Dict[str, Any]) -> None:
#     """Render AI-generated summary/insights from LLM"""
#     metadata = results.get('metadata', {})
#     ai_summary = metadata.get('ai_summary')
#     if ai_summary:
#         st.subheader("🤖 AI Insights (LLM)")
#         st.markdown(ai_summary)
#     else:
#         st.info("No AI-generated summary available.")

# def render_results(results: Dict[str, Any]) -> None:
#     """
#     Main function to render analysis results
    
#     Args:
#         results: Analysis results dictionary from the API
#     """
    
#     if not results:
#         st.info("No results to display")
#         return
    
#     try:
#         # Summary metrics card
#         render_summary_card(results)
        
#         st.markdown("---")
        
#         # Main content sections
#         render_content_summary(results)
        
#         st.markdown("---")
        
#         # Keywords
#         render_keywords(results)
        
#         st.markdown("---")
        
#         # Content sections
#         render_sections(results)
        
#         st.markdown("---")
        
#         # Contact information
#         render_contact_info(results)
        
#         st.markdown("---")
        
#         # Technical details
#         render_metadata(results)
        
#         st.markdown("---")
        
#         # AI-generated summary/insights
#         render_ai_summary(results)
        
#         st.markdown("---")
        
#         # Structured data (JSON-LD, microdata)
#         render_structured_data(results)
        
#         st.markdown("---")
        
#         # Export options
#         render_export_options(results)
        
#     except Exception as e:
#         st.error(f"Error displaying results: {str(e)}")
        
#         # Show raw results as fallback
#         with st.expander("Raw Results (Debug)"):
#             st.json(results)
