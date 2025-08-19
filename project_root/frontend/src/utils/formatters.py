"""Content formatting utilities for the frontend"""
import json
import time
from typing import Dict, Any, List


def format_content_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format content metrics for display"""
    content_length = result.get('content_length', 0)
    keywords = result.get('keywords', [])
    word_count = content_length // 5  # Rough estimate
    read_time = max(1, word_count // 200)  # Average reading speed
    
    return {
        'content_length': f"{content_length:,} chars",
        'keyword_count': len(keywords),
        'word_count': f"{word_count:,}",
        'read_time': f"{read_time} min"
    }


def format_keywords_html(keywords: List[str], max_display: int = 15) -> str:
    """Format keywords as colored HTML tags"""
    if not keywords:
        return ""
    
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF"]
    keyword_html = ""
    
    for i, keyword in enumerate(keywords[:max_display]):
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
    
    return keyword_html


def format_content_insights(result: Dict[str, Any]) -> Dict[str, List[str]]:
    """Generate content analysis insights"""
    content_length = result.get('content_length', 0)
    keyword_count = len(result.get('keywords', []))
    
    characteristics = []
    quality_indicators = []
    
    # Content characteristics
    if content_length > 5000:
        characteristics.append("• 📄 Long-form content")
    elif content_length > 1000:
        characteristics.append("• 📝 Medium-length content")
    else:
        characteristics.append("• 📃 Short-form content")
    
    if keyword_count > 10:
        characteristics.append("• 🎯 Rich topic diversity")
    elif keyword_count > 5:
        characteristics.append("• 📚 Moderate topic coverage")
    else:
        characteristics.append("• 🎪 Focused topic scope")
    
    # Quality indicators
    if result.get('summary'):
        quality_indicators.append("• ✅ Summary extractable")
    if keyword_count > 0:
        quality_indicators.append("• ✅ Keywords identified")
    if content_length > 100:
        quality_indicators.append("• ✅ Substantial content")
    
    return {
        'characteristics': characteristics,
        'quality_indicators': quality_indicators
    }


def format_download_data(result: Dict[str, Any]) -> str:
    """Format analysis result for download"""
    return json.dumps(result, indent=2)


def generate_download_filename() -> str:
    """Generate filename for download"""
    return f"analysis_{int(time.time())}.json"
