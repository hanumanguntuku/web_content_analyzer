"""
PDF Report Generator Utility
"""
import io
from fpdf import FPDF
from typing import Dict, Any
from datetime import datetime

class PDFReportGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Web Content Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        cleaned_title = str(title).encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, cleaned_title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        cleaned_body = str(body).encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, cleaned_body)
        self.ln()

    def add_metric(self, metric, value):
        self.set_font('Arial', 'B', 10)
        self.cell(50, 8, metric, border=1)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, str(value), border=1)
        self.ln()

def generate_pdf_report(analysis_report: Dict[str, Any]) -> bytes:
    """Generates a PDF report from the analysis data."""
    pdf = PDFReportGenerator()
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, analysis_report.get('title', 'Analysis Report'), 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, analysis_report.get('url', ''), 0, 1, 'C')
    pdf.cell(0, 8, f"Analyzed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)

    # Summary
    pdf.chapter_title('📊 Analysis Summary')
    summary_body = analysis_report.get('summary') or analysis_report.get("metadata", {}).get("ai_summary", "No summary available.")
    pdf.chapter_body(summary_body)

    # Key Metrics
    pdf.chapter_title('📈 Key Metrics')
    pdf.add_metric("Overall Score", f"{analysis_report.get('overall_quality_score', 0):.1f}/100")
    pdf.add_metric("Word Count", f"{analysis_report.get('word_count', 0):,}")
    pdf.add_metric("Processing Time", f"{analysis_report.get('processing_time', 0):.2f}s")
    pdf.add_metric("Readability Score", f"{analysis_report.get('content_analysis', {}).get('readability_score', 0):.1f}")
    pdf.ln(5)

    # Keywords
    keywords = analysis_report.get("keywords", [])
    if keywords:
        pdf.chapter_title('🏷️ Keywords')
        keyword_str = ", ".join([kw.get('keyword', str(kw)) for kw in keywords[:15]])
        pdf.chapter_body(keyword_str)

    # SEO Analysis
    seo_analysis = analysis_report.get('content_analysis', {})
    if seo_analysis.get('seo_score'):
        pdf.chapter_title('📈 SEO Analysis')
        pdf.add_metric("SEO Score", f"{seo_analysis.get('seo_score', 0)}/100")
        recommendations = seo_analysis.get('seo_recommendations', [])
        if recommendations:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 10, "Recommendations:", 0, 1, 'L')
            for rec in recommendations:
                pdf.chapter_body(f"- {rec}")
        pdf.ln(5)

    # Sentiment Analysis
    sentiment_analysis = analysis_report.get('content_analysis', {})
    if sentiment_analysis.get('sentiment_label'):
        pdf.chapter_title('😊 Sentiment & Tone')
        pdf.add_metric("Sentiment", sentiment_analysis.get('sentiment_label', 'N/A'))
        tones = sentiment_analysis.get('detected_tones', [])
        if tones:
            pdf.add_metric("Detected Tones", ", ".join(tones))
        pdf.ln(5)

    # Contact Info
    contact_info = analysis_report.get("contact_information", {})
    emails = contact_info.get("emails", [])
    phones = contact_info.get("phones", [])
    if emails or phones:
        pdf.chapter_title('📞 Contact Information')
        if emails:
            pdf.chapter_body("Emails: " + ", ".join(emails))
        if phones:
            pdf.chapter_body("Phones: " + ", ".join(phones))

    return pdf.output(dest='S').encode('latin-1')
