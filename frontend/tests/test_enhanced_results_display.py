import pytest
import streamlit as st
from src.components import enhanced_results_display

def test_render_analysis_summary_runs(monkeypatch):
    # Minimal valid input
    analysis_report = {
        "performance_metrics": {"content_size": 1234},
        "content_analysis": {"content_type": "article", "readability_score": 75},
        "url": "https://example.com",
        "title": "Test Title",
        "processing_status": "completed",
        "word_count": 1000,
        "processing_time": 1.23,
        "overall_quality_score": 88.5,
        "language": "en"
    }
    # Should not raise
    enhanced_results_display.render_analysis_summary(analysis_report)

def test_render_content_analysis_runs():
    analysis_report = {
        "summary": "A summary.",
        "metadata": {"ai_summary": "AI summary."},
        "keywords": ["python", {"word": "ai", "weight": 2}],
    }
    # Should not raise
    enhanced_results_display.render_content_analysis(analysis_report)
