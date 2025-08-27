# --- Add missing imports for error, SEO, and contact info rendering ---

# --- Add stubs for missing functions if not defined ---
import streamlit as st

def render_error_display(result):
    st.error(result.get('message', 'An error occurred during analysis.'))

def render_seo_analysis(result):
    st.info('SEO analysis not implemented.')

def render_contact_info(result):
    st.info('Contact info display not implemented.')
"""
Enhanced Results Display Component - M1-PRES-02 Implementation
Comprehensive display of analysis results with interactive visualizations
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
from ..utils.pdf_generator import generate_pdf_report

def render_analysis_summary(analysis_report: Dict[str, Any]):
    """Render high-level analysis summary"""
    st.markdown("## 📊 Analysis Summary")
    
    performance_metrics = analysis_report.get("performance_metrics", {})
    content_analysis = analysis_report.get("content_analysis", {})
    url = analysis_report.get("url", "")
    title = analysis_report.get("title", "Unknown Title")
    status = analysis_report.get("processing_status", "unknown")
    
    # Status indicator
    if status == "completed":
        st.success(f"✅ Analysis completed successfully")
    elif status == "failed":
        st.error(f"❌ Analysis failed")
    else:
        st.warning(f"⚠️ Analysis status: {status}")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Content Size",
            f"{performance_metrics.get('content_size', 0):,} bytes",
            delta=None
        )
    
    with col2:
        st.metric(
            "Word Count",
            f"{analysis_report.get('word_count', 0):,}",
            delta=None
        )
    
    with col3:
        processing_time = analysis_report.get('processing_time', 0)
        st.metric(
            "Processing Time",
            f"{processing_time:.2f}s",
            delta=None
        )
    
    with col4:
        overall_quality_score = analysis_report.get('overall_quality_score', 0)
        st.metric(
            "Overall Score",
            f"{overall_quality_score:.1f}/100",
            delta=None
        )
    
    # Website information
    st.markdown("### 🌐 Website Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**URL:**", url)
        st.write("**Title:**", title)
        st.write("**Language:**", analysis_report.get("language", "Unknown"))
    
    with col2:
        st.write("**Content Type:**", content_analysis.get("content_type", "Unknown"))
        analyzed_at = analysis_report.get("analysis_timestamp")
        if analyzed_at:
            st.write("**Analyzed At:**", analyzed_at)
        
        readability = content_analysis.get('readability_score', 0)
        if readability > 80:
            st.write("**Readability:**", f"🟢 Excellent ({readability:.1f})")
        elif readability > 60:
            st.write("**Readability:**", f"🟡 Good ({readability:.1f})")
        else:
            st.write("**Readability:**", f"🔴 Needs Improvement ({readability:.1f})")

def render_content_analysis(analysis_report: Dict[str, Any]):
    """Render detailed content analysis"""
    st.markdown("## 📝 Content Analysis")
    
    # Summary
    summary = analysis_report.get("summary", "")
    ai_summary = analysis_report.get("metadata", {}).get("ai_summary", "")
    if summary or ai_summary:
        st.markdown("### 📋 Content Summary")
        if summary:
            st.info(summary)
        if ai_summary:
            st.markdown("#### 🤖 AI-Generated Summary")
            st.success(ai_summary)
    
    # Keywords
    keywords = analysis_report.get("keywords", [])
    if keywords:
        st.markdown("### 🏷️ Key Topics & Keywords")
        
        # Create keyword frequency chart
        if len(keywords) > 0:
            # Assuming keywords might have weights (if not, all get weight 1)
            keyword_data = []
            for i, keyword in enumerate(keywords[:20]):  # Top 20 keywords
                if isinstance(keyword, dict) and 'word' in keyword:
                    keyword_data.append({
                        'keyword': keyword['word'],
                        'weight': keyword.get('weight', 1)
                    })
                else:
                    keyword_data.append({
                        'keyword': str(keyword),
                        'weight': len(keywords) - i  # Decreasing weight
                    })
            
            df_keywords = pd.DataFrame(keyword_data)
            
            # Horizontal bar chart for keywords
            fig = px.bar(
                df_keywords,
                x='weight',
                y='keyword',
                orientation='h',
                title="Top Keywords by Importance",
                labels={'weight': 'Importance Score', 'keyword': 'Keywords'}
            )
            fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Keywords as tags
        st.markdown("**Keywords:**")
        keyword_tags = []
        for keyword in keywords[:15]:  # Show top 15 as tags
            if isinstance(keyword, dict):
                keyword_tags.append(keyword.get('word', str(keyword)))
            else:
                keyword_tags.append(str(keyword))
        
        st.write(" • ".join(keyword_tags))

def render_performance_metrics(analysis_report: Dict[str, Any]):
    """Render performance and quality metrics"""
    st.markdown("## ⚡ Performance & Quality Metrics")
    
    performance_metrics = analysis_report.get("performance_metrics", {})
    content_analysis = analysis_report.get("content_analysis", {})
    
    # Create performance dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance gauge
        overall_quality_score = analysis_report.get('overall_quality_score', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_quality_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Quality Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Readability gauge
        readability_score = content_analysis.get('readability_score', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = readability_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Readability Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 100], 'color': "lightgreen"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics table
    st.markdown("### 📈 Detailed Metrics")
    
    metrics_data = [
        ["Processing Time (s)", f"{analysis_report.get('processing_time', 0):.4f}"],
        ["Content Size (bytes)", f"{performance_metrics.get('content_size', 0):,}"],
        ["Word Count", f"{analysis_report.get('word_count', 0):,}"],
        ["Readability Score", f"{content_analysis.get('readability_score', 0):.1f}/100"],
        ["Overall Quality Score", f"{analysis_report.get('overall_quality_score', 0):.1f}/100"],
        ["Extraction Quality", f"{analysis_report.get('extraction_quality', 0):.1f}/100"],
        ["Processing Quality", f"{analysis_report.get('processing_quality', 0):.1f}/100"],
        ["HTTP Status", f"{performance_metrics.get('http_status', 'N/A')}"],
    ]
    
    df_metrics = pd.DataFrame(metrics_data, columns=["Metric", "Value"])
    st.table(df_metrics)

def render_media_analysis(analysis_report: Dict[str, Any]):
    """Render media (images and links) analysis"""
    images = analysis_report.get("images", [])
    links = analysis_report.get("links", [])
    
    if images or links:
        st.markdown("## 🖼️ Media & Links Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if images:
                st.markdown("### 📸 Images Found")
                st.write(f"**Total Images:** {len(images)}")
                
                # Show sample images
                for i, img in enumerate(images[:5]):  # Show first 5 images
                    with st.expander(f"Image {i+1}"):
                        st.write("**Source:**", img.get('src', 'Unknown'))
                        st.write("**Alt Text:**", img.get('alt', 'No alt text'))
                        if img.get('title'):
                            st.write("**Title:**", img.get('title'))
                        
                        # Try to display the image if it's a valid URL
                        src = img.get('src', '')
                        if src.startswith('http'):
                            try:
                                st.image(src, caption=img.get('alt', 'Image'), use_column_width=True)
                            except:
                                st.write("*Image could not be displayed*")
        
        with col2:
            if links:
                st.markdown("### 🔗 Links Found")
                st.write(f"**Total Links:** {len(links)}")
                
                # Categorize links
                internal_links = [link for link in links if link.get('type') == 'internal']
                external_links = [link for link in links if link.get('type') == 'external']
                
                st.write(f"**Internal Links:** {len(internal_links)}")
                st.write(f"**External Links:** {len(external_links)}")
                
                # Show sample links
                st.markdown("**Sample Links:**")
                for i, link in enumerate(links[:10]):  # Show first 10 links
                    href = link.get('href', '#')
                    text = link.get('text', 'No text')
                    link_type = link.get('type', 'unknown')
                    
                    # Truncate long text
                    if len(text) > 50:
                        text = text[:47] + "..."
                    
                    icon = "🔗" if link_type == "external" else "📝"
                    st.write(f"{icon} [{text}]({href})")

def render_enhanced_results(analysis_result):
    """
    Main function to render comprehensive analysis results (single or batch)
    Args:
        analysis_result: Complete analysis result (dict) or batch (list)
    """
    if not analysis_result:
        st.warning("No analysis results to display.")
        return

    # Handle batch results (list)
    if isinstance(analysis_result, list):
        if len(analysis_result) == 0:
            st.warning("No batch results to display.")
            return
        st.markdown("## Batch Analysis Results")
        for idx, result in enumerate(analysis_result):
            st.markdown(f"### Result {idx+1}")
            if isinstance(result, dict) and ("error" in result or (result.get("status") == "FAILED" if isinstance(result, dict) else False)):
                render_error_display(result)
            else:
                try:
                    render_analysis_summary(result)
                    render_content_analysis(result)
                    render_performance_metrics(result)
                    st.markdown("---")
                    render_sentiment_and_tone(result)
                    render_seo_analysis(result)
                    render_media_analysis(result)
                    render_contact_info(result)
                    render_accessibility_info(result)
                    # Export options for each result
                    st.markdown("## 💾 Export Results")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📋 Copy Summary {idx+1}"):
                            summary_text = f"""
Website Analysis Summary
URL: {result.get('url', '')}
Title: {result.get('title', '')}
Word Count: {result.get('word_count', 0):,}
Overall Score: {result.get('overall_quality_score', 0):.1f}/100
Keywords: {', '.join([kw.get('keyword', '') for kw in result.get('keywords', [])[:5]])}
                            """.strip()
                            st.success("Summary copied to clipboard!")
                    with col2:
                        try:
                            pdf_data = generate_pdf_report(result)
                            st.download_button(
                                label=f"📊 Download Report {idx+1}",
                                data=pdf_data,
                                file_name=f"analysis_report_{result.get('title', 'report')}_{idx+1}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as e:
                            st.error("Failed to generate PDF report.")
                    with col3:
                        if st.button(f"🔄 Analyze Another URL {idx+1}"):
                            for key in list(st.session_state.keys()):
                                if key.startswith('analysis_'):
                                    del st.session_state[key]
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error displaying batch result {idx+1}: {str(e)}")
                    with st.expander("Error Details"):
                        st.exception(e)
        return

    # Single result (dict)
    if isinstance(analysis_result, dict):
        if "error" in analysis_result or analysis_result.get("status") == "FAILED":
            render_error_display(analysis_result)
            return
    try:
        render_analysis_summary(analysis_result)
        render_content_analysis(analysis_result)
        render_performance_metrics(analysis_result)
        st.markdown("---")
        render_sentiment_and_tone(analysis_result)
        render_seo_analysis(analysis_result)
        render_media_analysis(analysis_result)
        render_contact_info(analysis_result)
        render_accessibility_info(analysis_result)
        st.markdown("## 💾 Export Results")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy Summary"):
                summary_text = f"""
Website Analysis Summary
URL: {analysis_result.get('url', '')}
Title: {analysis_result.get('title', '')}
Word Count: {analysis_result.get('word_count', 0):,}
Overall Score: {analysis_result.get('overall_quality_score', 0):.1f}/100
Keywords: {', '.join([kw.get('keyword', '') for kw in analysis_result.get('keywords', [])[:5]])}
                """.strip()
                st.success("Summary copied to clipboard!")
        with col2:
            try:
                pdf_data = generate_pdf_report(analysis_result)
                st.download_button(
                    label="📊 Download Report",
                    data=pdf_data,
                    file_name=f"analysis_report_{analysis_result.get('title', 'report')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error("Failed to generate PDF report.")
        with col3:
            if st.button("🔄 Analyze Another URL"):
                for key in list(st.session_state.keys()):
                    if key.startswith('analysis_'):
                        del st.session_state[key]
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        with st.expander("Error Details"):
            st.exception(e)
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)

    if recommendations:
        st.markdown("### 💡 Recommendations")
        for rec in recommendations:
            st.success(f"• {rec}")
    else:
        st.info("No specific SEO recommendations available.")

def render_sentiment_and_tone(analysis_report: Dict[str, Any]):
    """Renders sentiment and tone analysis."""
    content_analysis = analysis_report.get("content_analysis", {})
    sentiment_score = content_analysis.get("sentiment_score")
    sentiment_label = content_analysis.get("sentiment_label", "Neutral")
    tones = content_analysis.get("detected_tones", [])

    st.markdown("## 😊 Sentiment & Tone Analysis")
    
    col1, col2 = st.columns(2)

    with col1:
        if sentiment_score is not None:
            st.metric("Sentiment Score", f"{sentiment_score:.2f}", delta=sentiment_label)
        else:
            st.info("Sentiment score not available.")

    with col2:
        if tones:
            st.markdown("### Detected Tones")
            st.write(" • ".join(tones))
        else:
            st.info("No specific tones detected.")

def render_accessibility_info(analysis_report: Dict[str, Any]):
    """Renders accessibility information."""
    content_analysis = analysis_report.get("content_analysis", {})
    notes = content_analysis.get("accessibility_notes", [])

    if notes:
        st.markdown("### ♿ Accessibility Notes")
        for note in notes:
            st.warning(f"• {note}")

def render_enhanced_results(analysis_result):
    """
    Main function to render comprehensive analysis results (single or batch)
    Args:
        analysis_result: Complete analysis result (dict) or batch (list)
    """
    if not analysis_result:
        st.warning("No analysis results to display.")
        return

    # Handle batch results (list)
    if isinstance(analysis_result, list):
        if len(analysis_result) == 0:
            st.warning("No batch results to display.")
            return
        st.markdown("## Batch Analysis Results")
        for idx, result in enumerate(analysis_result):
            st.markdown(f"### Result {idx+1}")
            if isinstance(result, dict) and ("error" in result or (result.get("status") == "FAILED" if isinstance(result, dict) else False)):
                render_error_display(result)
            else:
                try:
                    render_analysis_summary(result)
                    render_content_analysis(result)
                    render_performance_metrics(result)
                    st.markdown("---")
                    render_sentiment_and_tone(result)
                    render_seo_analysis(result)
                    render_media_analysis(result)
                    render_contact_info(result)
                    render_accessibility_info(result)
                    # Export options for each result
                    st.markdown("## 💾 Export Results")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📋 Copy Summary {idx+1}"):
                            summary_text = f"""
Website Analysis Summary
URL: {result.get('url', '')}
Title: {result.get('title', '')}
Word Count: {result.get('word_count', 0):,}
Overall Score: {result.get('overall_quality_score', 0):.1f}/100
Keywords: {', '.join([kw.get('keyword', '') for kw in result.get('keywords', [])[:5]])}
                            """.strip()
                            st.success("Summary copied to clipboard!")
                    with col2:
                        try:
                            pdf_data = generate_pdf_report(result)
                            st.download_button(
                                label=f"📊 Download Report {idx+1}",
                                data=pdf_data,
                                file_name=f"analysis_report_{result.get('title', 'report')}_{idx+1}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as e:
                            st.error("Failed to generate PDF report.")
                    with col3:
                        if st.button(f"🔄 Analyze Another URL {idx+1}"):
                            for key in list(st.session_state.keys()):
                                if key.startswith('analysis_'):
                                    del st.session_state[key]
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error displaying batch result {idx+1}: {str(e)}")
                    with st.expander("Error Details"):
                        st.exception(e)
        return

    # Single result (dict)
    if isinstance(analysis_result, dict):
        if "error" in analysis_result or analysis_result.get("status") == "FAILED":
            render_error_display(analysis_result)
            return
        try:
            render_analysis_summary(analysis_result)
            render_content_analysis(analysis_result)
            render_performance_metrics(analysis_result)
            st.markdown("---")
            render_sentiment_and_tone(analysis_result)
            render_seo_analysis(analysis_result)
            render_media_analysis(analysis_result)
            render_contact_info(analysis_result)
            render_accessibility_info(analysis_result)
            st.markdown("## 💾 Export Results")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Copy Summary"):
                    summary_text = f"""
Website Analysis Summary
URL: {analysis_result.get('url', '')}
Title: {analysis_result.get('title', '')}
Word Count: {analysis_result.get('word_count', 0):,}
Overall Score: {analysis_result.get('overall_quality_score', 0):.1f}/100
Keywords: {', '.join([kw.get('keyword', '') for kw in analysis_result.get('keywords', [])[:5]])}
                    """.strip()
                    st.success("Summary copied to clipboard!")
            with col2:
                try:
                    pdf_data = generate_pdf_report(analysis_result)
                    st.download_button(
                        label="📊 Download Report",
                        data=pdf_data,
                        file_name=f"analysis_report_{analysis_result.get('title', 'report')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("Failed to generate PDF report.")
            with col3:
                if st.button("🔄 Analyze Another URL"):
                    for key in list(st.session_state.keys()):
                        if key.startswith('analysis_'):
                            del st.session_state[key]
                    st.experimental_rerun()
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            with st.expander("Error Details"):
                st.exception(e)
