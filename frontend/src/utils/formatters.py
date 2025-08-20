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
        results: Raw analysis results from API
        
    Returns:
        Formatted results for UI display
    """
    if not results:
        return {}
    
    # Handle different result formats
    formatted = {
        'summary': {
            'title': results.get('title', 'N/A'),
            'description': results.get('description', 'N/A'),
            'word_count': results.get('word_count', 0),
            'page_size': results.get('page_size', 0),
            'load_time': results.get('load_time', 0.0),
            'status_code': results.get('status_code', 200)
        },
        'content': {
            'headings': results.get('headings', []),
            'paragraphs': results.get('paragraphs', []),
            'links': results.get('links', []),
            'images': results.get('images', [])
        },
        'seo': {
            'meta_title': results.get('meta_title', ''),
            'meta_description': results.get('meta_description', ''),
            'keywords': results.get('keywords', []),
            'canonical_url': results.get('canonical_url', '')
        },
        'contact': {
            'emails': results.get('emails', []),
            'phones': results.get('phones', []),
            'addresses': results.get('addresses', [])
        },
        'metadata': {
            'language': results.get('language', 'Unknown'),
            'charset': results.get('charset', 'Unknown'),
            'last_modified': results.get('last_modified', 'Unknown'),
            'content_type': results.get('content_type', 'Unknown')
        }
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
