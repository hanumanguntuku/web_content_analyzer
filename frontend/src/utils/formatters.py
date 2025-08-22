"""
Result Formatters
Utility functions for formatting analysis results
"""
from typing import Dict, Any, List
import json

def format_analysis_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw analysis results for display
    
    Args:
        results: Raw analysis results from API (AnalysisReport format)
        
    Returns:
        Formatted results for UI display
    """
    if not results:
        return {}
    
    # Extract content analysis data
    content_analysis = results.get('content_analysis', {})
    # Robustly extract content_type as a string
    content_type = 'unknown'
    if isinstance(content_analysis, dict):
        content_type = content_analysis.get('content_type', 'unknown')
    else:
        # Try attribute access (Pydantic model or object)
        content_type = getattr(content_analysis, 'content_type', 'unknown')
    # If content_type is an enum, get its value
    if hasattr(content_type, 'value'):
        content_type = content_type.value
    technical_metadata = results.get('technical_metadata', {})
    contact_info = results.get('contact_information', {})
    
    # Handle different result formats - new AnalysisReport structure
    formatted = {
        # Basic summary information
        'title': results.get('title', 'No Title'),
        'summary': results.get('description', 'No summary available'),
        'content_type': content_type,
        'word_count': results.get('word_count', 0),
        'character_count': results.get('character_count', 0),
        'paragraph_count': results.get('paragraph_count', 0),
        'readability_score': (
            content_analysis.get('readability_score', 0.0)
            if isinstance(content_analysis, dict)
            else getattr(content_analysis, 'readability_score', 0.0)
        ),
        'language': technical_metadata.get('encoding', 'Unknown'),
        'processing_time': results.get('processing_time', 0.0),

        # Keywords from the analysis
        'keywords': [kw.get('word', kw) if isinstance(kw, dict) else kw 
                    for kw in results.get('keywords', [])],

        # Content sections
        'key_sections': results.get('key_sections', []),

        # Contact information
        'emails': contact_info.get('emails', []),
        'phones': contact_info.get('phones', []),

        # Technical details
        'overall_quality_score': results.get('overall_quality_score', 0.0),
        'extraction_quality': results.get('extraction_quality', 0.0),
        'processing_quality': results.get('processing_quality', 0.0),

        # SEO and metadata
        'domain': technical_metadata.get('domain', ''),
        'protocol': technical_metadata.get('protocol', ''),
        'cms': technical_metadata.get('cms', 'Unknown'),

        # Counts
        'heading_count': results.get('heading_count', 0),
        'link_count': results.get('link_count', 0),
        'image_count': results.get('image_count', 0),

        # Performance metrics
        'performance_metrics': results.get('performance_metrics', {}),

        # Raw results for debugging
        '_raw_results': results
    }
    
    return formatted

def format_keywords_for_display(keywords: List[str], max_display: int = 20) -> List[str]:
    """Format keywords for UI display"""
    if not keywords:
        return []
    
    # Return top keywords only
    return keywords[:max_display]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_load_time(seconds: float) -> str:
    """Format load time for display"""
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    else:
        return f"{seconds:.2f} s"

def export_results_as_json(results: Dict[str, Any]) -> str:
    """Export results as formatted JSON string"""
    return json.dumps(results, indent=2, ensure_ascii=False)

def export_results_as_text(results: Dict[str, Any]) -> str:
    """Export results as formatted text"""
    if not results:
        return "No results to export"
    
    text_lines = []
    text_lines.append("WEB CONTENT ANALYSIS REPORT")
    text_lines.append("=" * 40)
    text_lines.append("")
    
    # Summary section
    summary = results.get('summary', {})
    text_lines.append("SUMMARY")
    text_lines.append("-" * 20)
    text_lines.append(f"Title: {summary.get('title', 'N/A')}")
    text_lines.append(f"Description: {summary.get('description', 'N/A')}")
    text_lines.append(f"Word Count: {summary.get('word_count', 0)}")
    text_lines.append(f"Page Size: {format_file_size(summary.get('page_size', 0))}")
    text_lines.append(f"Load Time: {format_load_time(summary.get('load_time', 0.0))}")
    text_lines.append("")
    
    # SEO section
    seo = results.get('seo', {})
    if any(seo.values()):
        text_lines.append("SEO INFORMATION")
        text_lines.append("-" * 20)
        text_lines.append(f"Meta Title: {seo.get('meta_title', 'N/A')}")
        text_lines.append(f"Meta Description: {seo.get('meta_description', 'N/A')}")
        if seo.get('keywords'):
            text_lines.append(f"Keywords: {', '.join(seo.get('keywords', []))}")
        text_lines.append("")
    
    # Contact section
    contact = results.get('contact', {})
    if any(contact.values()):
        text_lines.append("CONTACT INFORMATION")
        text_lines.append("-" * 20)
        if contact.get('emails'):
            text_lines.append(f"Emails: {', '.join(contact.get('emails', []))}")
        if contact.get('phones'):
            text_lines.append(f"Phones: {', '.join(contact.get('phones', []))}")
        text_lines.append("")
    
    return "\n".join(text_lines)
