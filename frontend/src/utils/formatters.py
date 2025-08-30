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
    
    # Robust extraction of content_analysis and technical_metadata
    content_analysis = results.get('content_analysis', {})
    technical_metadata = results.get('technical_metadata', {})
    metadata = results.get('metadata', {})

    # Content type extraction: prefer top-level, then content_analysis
    if 'content_type' in results and results['content_type']:
        content_type = str(results['content_type'])
    elif hasattr(content_analysis, 'content_type'):
        content_type = str(getattr(content_analysis, 'content_type', 'unknown'))
    elif isinstance(content_analysis, dict):
        content_type = str(content_analysis.get('content_type', 'unknown'))
    else:
        content_type = 'unknown'

    # Language extraction (try multiple sources)
    language = (
        technical_metadata.get('encoding')
        or metadata.get('language')
        or getattr(content_analysis, 'language', None)
        or 'Unknown'
    )

    # Readability score extraction
    if hasattr(content_analysis, 'readability_score'):
        readability_score = getattr(content_analysis, 'readability_score', 0.0)
    elif isinstance(content_analysis, dict):
        readability_score = content_analysis.get('readability_score', 0.0)
    else:
        readability_score = 0.0

    # Metrics mapping (populate all expected fields)
    metrics = {
        'content_size': results.get('character_count', 0),
        'word_count': results.get('word_count', 0),
        'processing_time': results.get('processing_time', 0),
        'performance_score': results.get('performance_score', 0),
        'readability_score': readability_score,
        'keyword_density': results.get('keyword_density', 0),
        'image_count': len(results.get('images', [])),
        'link_count': len(results.get('links', [])),
    }

    # Summary field (robust fallback)
    summary_value = (
        results.get('description')
        or results.get('summary')
        or ''
    )

    formatted = {
        'url': results.get('url', ''),
        'title': results.get('title', 'No Title'),
        'language': language,
        'content_type': content_type,
        'metrics': metrics,
        'summary': summary_value,
        'keywords': results.get('keywords', []),
        'images': results.get('images', []),
        'links': results.get('links', []),
        'metadata': results.get('metadata', {}),
        'status': results.get('status', 'unknown'),
        'analyzed_at': results.get('analyzed_at', ''),
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
