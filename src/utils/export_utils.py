# src/utils/export_utils.py
"""Export utilities for review results and reports"""

import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from src.utils.logger import LoggerMixin
from src.storage.models import AgentFinding, ReviewSession
from src.document.processor import ProcessedContent


class ReviewExporter(LoggerMixin):
    """Handles exporting review results in various formats"""
    
    def __init__(self):
        self.supported_formats = ["json", "txt", "html"]
    
    def export_review_results(
        self, 
        processed_content: ProcessedContent,
        review_result=None,
        format_type: str = "json"
    ) -> Optional[Path]:
        """
        Export complete review results to local file
        
        Args:
            processed_content: The processed document content
            review_result: Optional AI review results
            format_type: Export format (json, txt, html)
            
        Returns:
            Path to exported file or None if cancelled
        """
        if format_type not in self.supported_formats:
            self.logger.error("Unsupported export format", format=format_type)
            return None
        
        # Prepare export data
        export_data = self._prepare_export_data(processed_content, review_result)
        
        # Get save location from user
        save_path = self._get_save_location(format_type, processed_content.document_info.filename)
        if not save_path:
            return None
        
        # Export based on format
        try:
            if format_type == "json":
                self._export_json(export_data, save_path)
            elif format_type == "txt":
                self._export_txt(export_data, save_path)
            elif format_type == "html":
                self._export_html(export_data, save_path)
            
            self.logger.info(
                "Review results exported successfully",
                format=format_type,
                path=str(save_path),
                session_id=processed_content.session_id
            )
            
            return save_path
            
        except Exception as e:
            self.logger.error("Export failed", error=str(e), format=format_type)
            return None
    
    def _prepare_export_data(self, processed_content: ProcessedContent, review_result=None) -> Dict[str, Any]:
        """Prepare data structure for export"""
        
        # Convert document info to dict
        doc_info_dict = asdict(processed_content.document_info)
        
        # Base export structure
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "app_version": "1.0.0",
                "export_type": "technical_writing_review"
            },
            "session_info": {
                "session_id": processed_content.session_id,
                "processing_time": processed_content.processing_time,
                "user_id": "current_user"  # Could be passed in
            },
            "document_info": doc_info_dict,
            "content": {
                "text_length": len(processed_content.text),
                "page_count": len(processed_content.pages),
                "images_count": len(processed_content.images),
                "tables_count": len(processed_content.tables),
                "text_preview": processed_content.text[:500] + "..." if len(processed_content.text) > 500 else processed_content.text
            }
        }
        
        # Add AI review results if available
        if review_result:
            export_data["ai_review"] = {
                "status": review_result.status,
                "total_processing_time": review_result.total_processing_time,
                "summary": review_result.summary,
                "agents_used": list(review_result.agent_results.keys()),
                "total_findings": len(review_result.findings),
                "findings_by_severity": self._count_findings_by_severity(review_result.findings),
                "findings": [self._finding_to_dict(finding) for finding in review_result.findings],
                "agent_breakdown": {
                    agent_name: {
                        "findings_count": len(findings),
                        "findings": [self._finding_to_dict(f) for f in findings]
                    }
                    for agent_name, findings in review_result.agent_results.items()
                }
            }
        
        return export_data
    
    def _finding_to_dict(self, finding: AgentFinding) -> Dict[str, Any]:
        """Convert AgentFinding to dictionary for export"""
        return {
            "id": finding.id,
            "agent_name": finding.agent_name,
            "severity": finding.severity,
            "category": finding.category,
            "description": finding.description,
            "location": finding.location,
            "suggestion": finding.suggestion,
            "confidence": finding.confidence,
            "created_at": finding.created_at.isoformat() if finding.created_at else None
        }
    
    def _count_findings_by_severity(self, findings: List[AgentFinding]) -> Dict[str, int]:
        """Count findings by severity level"""
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return counts
    
    def _get_save_location(self, format_type: str, original_filename: str) -> Optional[Path]:
        """Get save location from user using file dialog"""
        try:
            # Create hidden root window
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(original_filename).stem
            default_filename = f"{base_name}_review_{timestamp}.{format_type}"
            
            # File type options
            filetypes = {
                "json": [("JSON files", "*.json"), ("All files", "*.*")],
                "txt": [("Text files", "*.txt"), ("All files", "*.*")],
                "html": [("HTML files", "*.html"), ("All files", "*.*")]
            }
            
            # Show save dialog
            file_path = filedialog.asksaveasfilename(
                title="Export Review Results",
                defaultextension=f".{format_type}",
                filetypes=filetypes.get(format_type, [("All files", "*.*")]),
                initialfile=default_filename
            )
            
            root.destroy()
            
            return Path(file_path) if file_path else None
            
        except Exception as e:
            self.logger.error("Failed to get save location", error=str(e))
            return None
    
    def _export_json(self, data: Dict[str, Any], save_path: Path):
        """Export data as JSON"""
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_txt(self, data: Dict[str, Any], save_path: Path):
        """Export data as plain text report"""
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("TECHNICAL WRITING REVIEW REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Export info
            f.write(f"Export Date: {data['export_info']['timestamp']}\n")
            f.write(f"Session ID: {data['session_info']['session_id']}\n")
            f.write(f"Document: {data['document_info']['filename']}\n\n")
            
            # Document info
            f.write("DOCUMENT INFORMATION\n")
            f.write("-" * 20 + "\n")
            f.write(f"Pages: {data['document_info']['page_count']}\n")
            f.write(f"File Size: {data['document_info']['file_size']:,} bytes\n")
            f.write(f"Processing Method: {data['document_info']['processing_method']}\n")
            f.write(f"Processing Time: {data['session_info']['processing_time']:.2f} seconds\n")
            f.write(f"Has Text: {'Yes' if data['document_info']['has_text'] else 'No'}\n")
            f.write(f"Has Images: {'Yes' if data['document_info']['has_images'] else 'No'}\n\n")
            
            # Content preview
            f.write("CONTENT PREVIEW\n")
            f.write("-" * 15 + "\n")
            f.write(f"Text Length: {data['content']['text_length']} characters\n")
            f.write(f"Preview: {data['content']['text_preview']}\n\n")
            
            # AI Review results if available
            if "ai_review" in data:
                ai_data = data["ai_review"]
                f.write("AI REVIEW RESULTS\n")
                f.write("-" * 17 + "\n")
                f.write(f"Status: {ai_data['status']}\n")
                f.write(f"Processing Time: {ai_data['total_processing_time']:.2f} seconds\n")
                f.write(f"Agents Used: {', '.join(ai_data['agents_used'])}\n")
                f.write(f"Total Findings: {ai_data['total_findings']}\n")
                
                # Severity breakdown
                severity_counts = ai_data["findings_by_severity"]
                f.write(f"Errors: {severity_counts['error']}, ")
                f.write(f"Warnings: {severity_counts['warning']}, ")
                f.write(f"Info: {severity_counts['info']}\n\n")
                
                # Summary
                f.write(f"Summary: {ai_data['summary']}\n\n")
                
                # Findings detail
                f.write("DETAILED FINDINGS\n")
                f.write("-" * 16 + "\n")
                for finding in ai_data["findings"]:
                    f.write(f"[{finding['severity'].upper()}] {finding['location']}\n")
                    f.write(f"Agent: {finding['agent_name']}\n")
                    f.write(f"Category: {finding['category']}\n")
                    f.write(f"Issue: {finding['description']}\n")
                    if finding['suggestion']:
                        f.write(f"Suggestion: {finding['suggestion']}\n")
                    f.write(f"Confidence: {finding['confidence']:.1%}\n")
                    f.write("-" * 40 + "\n")
    
    def _export_html(self, data: Dict[str, Any], save_path: Path):
        """Export data as HTML report"""
        html_content = self._generate_html_report(data)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report content"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Technical Writing Review Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .finding {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .error {{ border-left: 5px solid #d32f2f; background-color: #ffebee; }}
        .warning {{ border-left: 5px solid #f57c00; background-color: #fff3e0; }}
        .info {{ border-left: 5px solid #1976d2; background-color: #e3f2fd; }}
        .severity {{ font-weight: bold; text-transform: uppercase; }}
        .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .preview {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Technical Writing Review Report</h1>
        <p><strong>Export Date:</strong> {data['export_info']['timestamp']}</p>
        <p><strong>Session ID:</strong> {data['session_info']['session_id']}</p>
        <p><strong>Document:</strong> {data['document_info']['filename']}</p>
    </div>
    
    <div class="section">
        <h2>Document Information</h2>
        <div class="info-grid">
            <div>
                <p><strong>Pages:</strong> {data['document_info']['page_count']}</p>
                <p><strong>File Size:</strong> {data['document_info']['file_size']:,} bytes</p>
                <p><strong>Processing Method:</strong> {data['document_info']['processing_method']}</p>
            </div>
            <div>
                <p><strong>Processing Time:</strong> {data['session_info']['processing_time']:.2f} seconds</p>
                <p><strong>Has Text:</strong> {'Yes' if data['document_info']['has_text'] else 'No'}</p>
                <p><strong>Has Images:</strong> {'Yes' if data['document_info']['has_images'] else 'No'}</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Content Preview</h2>
        <div class="stats">
            <p><strong>Text Length:</strong> {data['content']['text_length']} characters</p>
            <p><strong>Images:</strong> {data['content']['images_count']}</p>
            <p><strong>Tables:</strong> {data['content']['tables_count']}</p>
        </div>
        <div class="preview">
            {data['content']['text_preview']}
        </div>
    </div>
"""
        
        # Add AI review section if available
        if "ai_review" in data:
            ai_data = data["ai_review"]
            severity_counts = ai_data["findings_by_severity"]
            
            html += f"""
    <div class="section">
        <h2>AI Review Results</h2>
        <div class="stats">
            <p><strong>Status:</strong> {ai_data['status']}</p>
            <p><strong>Processing Time:</strong> {ai_data['total_processing_time']:.2f} seconds</p>
            <p><strong>Agents Used:</strong> {', '.join(ai_data['agents_used'])}</p>
            <p><strong>Total Findings:</strong> {ai_data['total_findings']}</p>
            <p><strong>Breakdown:</strong> {severity_counts['error']} Errors, {severity_counts['warning']} Warnings, {severity_counts['info']} Info</p>
        </div>
        <p><strong>Summary:</strong> {ai_data['summary']}</p>
    </div>
    
    <div class="section">
        <h2>Detailed Findings</h2>
"""
            
            # Add findings
            for finding in ai_data["findings"]:
                html += f"""
        <div class="finding {finding['severity']}">
            <div class="severity">[{finding['severity']}]</div>
            <p><strong>Location:</strong> {finding['location']}</p>
            <p><strong>Agent:</strong> {finding['agent_name']} | <strong>Category:</strong> {finding['category']}</p>
            <p><strong>Issue:</strong> {finding['description']}</p>
"""
                if finding['suggestion']:
                    html += f"            <p><strong>Suggestion:</strong> {finding['suggestion']}</p>\n"
                
                html += f"            <p><strong>Confidence:</strong> {finding['confidence']:.1%}</p>\n"
                html += "        </div>\n"
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        return html


class PDFReportExporter(LoggerMixin):
    """Handles PDF report generation (future enhancement)"""
    
    def __init__(self):
        self.logger.info("PDF exporter initialized (not yet implemented)")
    
    def export_pdf_report(self, data: Dict[str, Any], save_path: Path) -> bool:
        """
        Export review results as PDF report
        
        This is a placeholder for future PDF export functionality.
        Could use libraries like ReportLab, WeasyPrint, or FPDF2.
        """
        self.logger.warning("PDF export not yet implemented")
        return False