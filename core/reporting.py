#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Professional Reporting System for Bug Bounty and Pentesting

This module provides comprehensive reporting functionality for security assessments,
including automated report generation, evidence collection, and multiple output formats.
"""

import os
import json
import base64
import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import socket
import getpass

try:
    from PIL import Image, ImageDraw, ImageFont
    import mss
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

from core.enhanced_logger import get_logger
from core.error_handler import handle_errors, ErrorContext
from core.colors import Colors
from core.cvss_calculator import CVSSv3, calculate_cvss_from_cve_details

class ReportSeverity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

class ReportStatus(Enum):
    """Report status"""
    DRAFT = "Draft"
    FINAL = "Final"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

@dataclass
class ExploitEvidence:
    """Evidence collected during exploit execution"""
    timestamp: str
    screenshot_path: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    payload_used: Optional[str] = None
    console_output: List[str] = field(default_factory=list)
    network_trace: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            k: v for k, v in asdict(self).items() 
            if v is not None and (not isinstance(v, list) or v)
        }

@dataclass
class TargetInfo:
    """Information about the target system"""
    url: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    protocol: str = "https"
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    user_agent: Optional[str] = None
    operating_system: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class VulnerabilityDetails:
    """Detailed vulnerability information"""
    cve_id: Optional[str] = None
    cweid: Optional[str] = None
    owasp_category: Optional[str] = None
    name: str = ""
    description: str = ""
    impact: str = ""
    severity: ReportSeverity = ReportSeverity.MEDIUM
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    cvss_base_score: Optional[float] = None
    cvss_temporal_score: Optional[float] = None
    cvss_analysis: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['severity'] = self.severity.value
        return {k: v for k, v in data.items() if v}

@dataclass
class SecurityReport:
    """Complete security assessment report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Security Assessment Report"
    status: ReportStatus = ReportStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Assessment details
    assessment_type: str = "Web Application Penetration Test"
    tester_name: str = field(default_factory=getpass.getuser)
    tester_email: Optional[str] = None
    company: Optional[str] = None
    
    # Target information
    target: TargetInfo = field(default_factory=TargetInfo)
    
    # Vulnerability details
    vulnerability: VulnerabilityDetails = field(default_factory=VulnerabilityDetails)
    
    # Evidence
    evidence: List[ExploitEvidence] = field(default_factory=list)
    
    # Remediation
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    
    # Executive Summary
    executive_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    business_impact: Optional[str] = None
    risk_rating: Optional[str] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'report_id': self.report_id,
            'title': self.title,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'assessment_type': self.assessment_type,
            'tester': {
                'name': self.tester_name,
                'email': self.tester_email,
                'company': self.company
            },
            'target': self.target.to_dict(),
            'vulnerability': self.vulnerability.to_dict(),
            'evidence': [e.to_dict() for e in self.evidence],
            'remediation': self.remediation,
            'references': self.references,
            'executive_summary': self.executive_summary,
            'technical_summary': self.technical_summary,
            'business_impact': self.business_impact,
            'risk_rating': self.risk_rating,
            'tags': self.tags,
            'custom_fields': self.custom_fields
        }
    
    def calculate_risk_score(self) -> float:
        """Calculate risk score based on severity and exploitability"""
        severity_scores = {
            ReportSeverity.CRITICAL: 10.0,
            ReportSeverity.HIGH: 8.0,
            ReportSeverity.MEDIUM: 5.0,
            ReportSeverity.LOW: 2.0,
            ReportSeverity.INFORMATIONAL: 0.5
        }
        
        base_score = severity_scores.get(self.vulnerability.severity, 5.0)
        
        # Adjust based on evidence
        if len(self.evidence) > 0:
            base_score *= 1.2  # Confirmed vulnerability
        
        return min(base_score, 10.0)

class ScreenshotCapture:
    """Handle screenshot capture for evidence"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
    
    @handle_errors(context="Screenshot capture")
    def capture(self, 
                filename_prefix: str = "evidence",
                monitor_index: int = 0,
                add_timestamp: bool = True) -> Optional[str]:
        """
        Capture screenshot of the screen
        
        Args:
            filename_prefix: Prefix for the screenshot filename
            monitor_index: Which monitor to capture (0 = primary)
            add_timestamp: Whether to add timestamp overlay
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        if not SCREENSHOT_AVAILABLE:
            self.logger.warning("Screenshot functionality not available. Install pillow and mss.")
            return None
        
        try:
            with mss.mss() as sct:
                # Get monitor info
                monitor = sct.monitors[monitor_index + 1]  # 0 is all monitors
                
                # Capture screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes(
                    'RGB', 
                    (screenshot.width, screenshot.height), 
                    screenshot.rgb
                )
                
                # Add timestamp overlay if requested
                if add_timestamp:
                    img = self._add_timestamp_overlay(img)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename_prefix}_{timestamp}.png"
                filepath = self.output_dir / filename
                
                # Save screenshot
                img.save(filepath, 'PNG', optimize=True)
                
                self.logger.info(f"Screenshot saved: {filepath}")
                return str(filepath)
                
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {str(e)}")
            return None
    
    def _add_timestamp_overlay(self, img: Image.Image) -> Image.Image:
        """Add timestamp overlay to image"""
        draw = ImageDraw.Draw(img)
        
        # Timestamp text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Add semi-transparent background
        text_bbox = draw.textbbox((10, 10), timestamp, font=font)
        padding = 5
        draw.rectangle(
            [text_bbox[0] - padding, text_bbox[1] - padding,
             text_bbox[2] + padding, text_bbox[3] + padding],
            fill=(0, 0, 0, 128)
        )
        
        # Add timestamp text
        draw.text((10, 10), timestamp, fill=(255, 255, 255), font=font)
        
        return img

class ReportGenerator:
    """Generate professional security reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
        self.screenshot_capture = ScreenshotCapture(self.output_dir / "screenshots")
        self.active_report: Optional[SecurityReport] = None
    
    def create_report(self,
                      vulnerability_name: str,
                      severity: ReportSeverity = ReportSeverity.MEDIUM,
                      target_url: Optional[str] = None) -> SecurityReport:
        """
        Create a new security report
        
        Args:
            vulnerability_name: Name of the vulnerability
            severity: Severity level
            target_url: Target URL
            
        Returns:
            New SecurityReport instance
        """
        report = SecurityReport(
            title=f"{vulnerability_name} - Security Assessment Report",
            vulnerability=VulnerabilityDetails(
                name=vulnerability_name,
                severity=severity
            )
        )
        
        if target_url:
            report.target.url = target_url
            # Extract hostname and protocol
            from urllib.parse import urlparse
            parsed = urlparse(target_url)
            report.target.hostname = parsed.hostname
            report.target.protocol = parsed.scheme
            report.target.port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        self.active_report = report
        self.logger.info(f"Created new report: {report.report_id}")
        
        return report
    
    def add_evidence(self,
                     report: SecurityReport,
                     payload: Optional[str] = None,
                     request_data: Optional[Dict[str, Any]] = None,
                     response_data: Optional[Dict[str, Any]] = None,
                     console_output: Optional[List[str]] = None,
                     capture_screenshot: bool = True) -> ExploitEvidence:
        """
        Add evidence to a report
        
        Args:
            report: The report to add evidence to
            payload: Payload used in the exploit
            request_data: HTTP request data
            response_data: HTTP response data
            console_output: Console output lines
            capture_screenshot: Whether to capture a screenshot
            
        Returns:
            ExploitEvidence instance
        """
        evidence = ExploitEvidence(
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload_used=payload,
            request_data=request_data,
            response_data=response_data,
            console_output=console_output or []
        )
        
        # Capture screenshot if requested
        if capture_screenshot and SCREENSHOT_AVAILABLE:
            screenshot_path = self.screenshot_capture.capture(
                filename_prefix=f"evidence_{report.report_id}"
            )
            if screenshot_path:
                evidence.screenshot_path = screenshot_path
        
        report.evidence.append(evidence)
        report.updated_at = datetime.now(timezone.utc).isoformat()
        
        self.logger.info(f"Added evidence to report {report.report_id}")
        
        return evidence
    
    def set_target_info(self,
                        report: SecurityReport,
                        browser_name: Optional[str] = None,
                        browser_version: Optional[str] = None,
                        user_agent: Optional[str] = None) -> None:
        """Set target browser information"""
        if browser_name:
            report.target.browser_name = browser_name
        if browser_version:
            report.target.browser_version = browser_version
        if user_agent:
            report.target.user_agent = user_agent
        
        # Try to detect OS from user agent
        if user_agent:
            os_name = self._detect_os_from_user_agent(user_agent)
            if os_name:
                report.target.operating_system = os_name
        
        report.updated_at = datetime.now(timezone.utc).isoformat()
    
    def _detect_os_from_user_agent(self, user_agent: str) -> Optional[str]:
        """Detect operating system from user agent string"""
        ua_lower = user_agent.lower()
        
        if 'windows nt 10' in ua_lower:
            return 'Windows 10'
        elif 'windows nt 6.3' in ua_lower:
            return 'Windows 8.1'
        elif 'windows nt 6.2' in ua_lower:
            return 'Windows 8'
        elif 'windows' in ua_lower:
            return 'Windows'
        elif 'mac os x' in ua_lower:
            return 'macOS'
        elif 'linux' in ua_lower:
            return 'Linux'
        elif 'android' in ua_lower:
            return 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            return 'iOS'
        
        return None
    
    def export_json(self, report: SecurityReport, filename: Optional[str] = None) -> str:
        """
        Export report as JSON
        
        Args:
            report: Report to export
            filename: Custom filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report.report_id}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported JSON report: {filepath}")
        return str(filepath)
    
    def export_html(self, report: SecurityReport, filename: Optional[str] = None) -> str:
        """
        Export report as HTML
        
        Args:
            report: Report to export
            filename: Custom filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report.report_id}_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        html_content = self._generate_html_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Exported HTML report: {filepath}")
        return str(filepath)
    
    def _generate_html_report(self, report: SecurityReport) -> str:
        """Generate HTML report content"""
        report_data = report.to_dict()
        
        # Escape HTML in strings
        def escape_html(text):
            if isinstance(text, str):
                return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return text
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(report.title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .header {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .severity-Critical {{ color: #e74c3c; font-weight: bold; }}
        .severity-High {{ color: #e67e22; font-weight: bold; }}
        .severity-Medium {{ color: #f39c12; font-weight: bold; }}
        .severity-Low {{ color: #27ae60; font-weight: bold; }}
        .severity-Informational {{ color: #3498db; font-weight: bold; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .evidence {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }}
        .screenshot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 10px 0;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .metadata {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
        }}
        .executive-summary {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #0066cc;
        }}
        .cvss-score {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .cvss-metrics {{
            width: 100%;
            margin: 10px 0;
            border-collapse: collapse;
        }}
        .cvss-metrics th {{
            background: #dee2e6;
            padding: 8px;
            text-align: left;
            font-weight: bold;
        }}
        .cvss-metrics td {{
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }}
        .cvss-analysis {{
            margin-top: 15px;
        }}
        .cvss-analysis h4 {{
            color: #0066cc;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{escape_html(report.title)}</h1>
            <div class="metadata">
                <strong>Report ID:</strong> {report_data['report_id']}<br>
                <strong>Created:</strong> {report_data['created_at']}<br>
                <strong>Status:</strong> {report_data['status']}<br>
                <strong>Risk Score:</strong> {report.calculate_risk_score():.1f}/10
            </div>
        </div>
        
        {'<div class="executive-summary">' if report_data.get('executive_summary') else ''}
        <h2>Executive Summary</h2>
        <p>{escape_html(report_data.get('executive_summary', f'This report documents a {report_data["vulnerability"]["severity"]} severity vulnerability discovered during security assessment.'))}</p>
        
        {'<h3>Business Impact</h3><p>' + escape_html(report_data.get('business_impact', 'No business impact analysis available.')) + '</p>' if report_data.get('business_impact') else ''}
        
        {'<h3>Risk Rating</h3><p>' + escape_html(report_data.get('risk_rating', 'No risk rating available.')) + '</p>' if report_data.get('risk_rating') else ''}
        {'</div>' if report_data.get('executive_summary') else ''}
        
        <div class="info-grid">
            <div class="info-box">
                <h3>Target Information</h3>
                <strong>URL:</strong> {escape_html(report_data['target'].get('url', 'N/A'))}<br>
                <strong>Hostname:</strong> {escape_html(report_data['target'].get('hostname', 'N/A'))}<br>
                <strong>Browser:</strong> {escape_html(report_data['target'].get('browser_name', 'N/A'))} {escape_html(report_data['target'].get('browser_version', ''))}<br>
                <strong>OS:</strong> {escape_html(report_data['target'].get('operating_system', 'N/A'))}
            </div>
            
            <div class="info-box">
                <h3>Vulnerability Details</h3>
                <strong>Name:</strong> {escape_html(report_data['vulnerability']['name'])}<br>
                <strong>Severity:</strong> <span class="severity-{report_data['vulnerability']['severity']}">{report_data['vulnerability']['severity']}</span><br>
                {'<strong>CVE ID:</strong> ' + escape_html(report_data['vulnerability'].get('cve_id', '')) + '<br>' if report_data['vulnerability'].get('cve_id') else ''}
                {'<strong>CWE ID:</strong> ' + escape_html(report_data['vulnerability'].get('cweid', '')) + '<br>' if report_data['vulnerability'].get('cweid') else ''}
                {'<strong>OWASP Category:</strong> ' + escape_html(report_data['vulnerability'].get('owasp_category', '')) + '<br>' if report_data['vulnerability'].get('owasp_category') else ''}
            </div>
            
            <div class="info-box">
                <h3>Assessment Details</h3>
                <strong>Type:</strong> {escape_html(report_data['assessment_type'])}<br>
                <strong>Tester:</strong> {escape_html(report_data['tester']['name'])}<br>
                {'<strong>Company:</strong> ' + escape_html(report_data['tester'].get('company', '')) + '<br>' if report_data['tester'].get('company') else ''}
            </div>
        </div>
        
        {f'''<h2>CVSS v3.1 Score</h2>
        <div class="cvss-score">
            <p><strong>Base Score:</strong> {report_data["vulnerability"]["cvss_base_score"]} {self._get_cvss_severity_color(report_data["vulnerability"]["cvss_base_score"])}</p>
            {f'<p><strong>Temporal Score:</strong> {report_data["vulnerability"]["cvss_temporal_score"]}</p>' if report_data['vulnerability'].get('cvss_temporal_score') else ''}
            <p><strong>Vector:</strong> <code>{escape_html(report_data["vulnerability"]["cvss_vector"])}</code></p>
            
            {self._generate_cvss_analysis_html(report_data['vulnerability'].get('cvss_analysis', {}))}
        </div>''' if report_data['vulnerability'].get('cvss_base_score') else ''}
        
        <h2>Technical Details</h2>
        <h3>Description</h3>
        <p>{escape_html(report_data['vulnerability'].get('description', 'No description provided.'))}</p>
        
        {f'<h3>Technical Summary</h3><p>{escape_html(report_data.get("technical_summary", "No technical summary available."))}</p>' if report_data.get('technical_summary') else ''}
        
        <h3>Impact</h3>
        <p>{escape_html(report_data['vulnerability'].get('impact', 'No impact analysis provided.'))}</p>
        
        <h2>Evidence</h2>
        {self._generate_evidence_html(report_data['evidence'])}
        
        <h2>Remediation</h2>
        <p>{escape_html(report_data.get('remediation', 'No remediation steps provided.'))}</p>
        
        {'<h2>References</h2><ul>' + ''.join(f'<li><a href="{ref}" target="_blank">{escape_html(ref)}</a></li>' for ref in report_data.get('references', [])) + '</ul>' if report_data.get('references') else ''}
        
        <div class="footer">
            <p>Generated by ChromSploit Framework v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p><small>This report is confidential and intended only for authorized recipients.</small></p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_evidence_html(self, evidence_list: List[Dict[str, Any]]) -> str:
        """Generate HTML for evidence section"""
        if not evidence_list:
            return "<p>No evidence collected.</p>"
        
        html_parts = []
        
        for i, evidence in enumerate(evidence_list, 1):
            html_parts.append(f'<div class="evidence">')
            html_parts.append(f'<h4>Evidence #{i}</h4>')
            html_parts.append(f'<div class="metadata">Timestamp: {evidence.get("timestamp", "N/A")}</div>')
            
            if evidence.get('payload_used'):
                html_parts.append(f'<p><strong>Payload:</strong></p>')
                html_parts.append(f'<pre>{self._escape_html(evidence["payload_used"])}</pre>')
            
            if evidence.get('request_data'):
                html_parts.append(f'<p><strong>Request:</strong></p>')
                html_parts.append(f'<pre>{self._escape_html(json.dumps(evidence["request_data"], indent=2))}</pre>')
            
            if evidence.get('response_data'):
                html_parts.append(f'<p><strong>Response:</strong></p>')
                html_parts.append(f'<pre>{self._escape_html(json.dumps(evidence["response_data"], indent=2))}</pre>')
            
            if evidence.get('console_output'):
                html_parts.append(f'<p><strong>Console Output:</strong></p>')
                html_parts.append(f'<pre>{self._escape_html("\\n".join(evidence["console_output"]))}</pre>')
            
            if evidence.get('screenshot_path'):
                # For HTML export, we'll embed the image as base64
                try:
                    with open(evidence['screenshot_path'], 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode()
                    html_parts.append(f'<p><strong>Screenshot:</strong></p>')
                    html_parts.append(f'<img class="screenshot" src="data:image/png;base64,{img_data}" alt="Evidence screenshot">')
                except:
                    html_parts.append(f'<p><strong>Screenshot:</strong> {evidence["screenshot_path"]}</p>')
            
            html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not isinstance(text, str):
            text = str(text)
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    
    def _get_cvss_severity_color(self, score: float) -> str:
        """Get CVSS severity color HTML"""
        if score >= 9.0:
            return '<span class="severity-critical">Critical</span>'
        elif score >= 7.0:
            return '<span class="severity-high">High</span>'
        elif score >= 4.0:
            return '<span class="severity-medium">Medium</span>'
        elif score >= 0.1:
            return '<span class="severity-low">Low</span>'
        else:
            return '<span class="severity-informational">None</span>'
    
    def _generate_cvss_analysis_html(self, cvss_analysis: Dict[str, Any]) -> str:
        """Generate HTML for CVSS analysis"""
        if not cvss_analysis:
            return ""
        
        html_parts = ['<div class="cvss-analysis">']
        
        # Metrics
        if 'metrics' in cvss_analysis:
            html_parts.append('<h4>CVSS Metrics:</h4>')
            html_parts.append('<table class="cvss-metrics">')
            
            # Base metrics
            if 'base' in cvss_analysis['metrics']:
                base = cvss_analysis['metrics']['base']
                html_parts.append('<tr><th colspan="2">Base Metrics</th></tr>')
                for key, value in base.items():
                    html_parts.append(f'<tr><td>{key.replace("_", " ").title()}:</td><td>{self._escape_html(str(value))}</td></tr>')
            
            # Temporal metrics
            if 'temporal' in cvss_analysis['metrics']:
                temporal = cvss_analysis['metrics']['temporal']
                html_parts.append('<tr><th colspan="2">Temporal Metrics</th></tr>')
                for key, value in temporal.items():
                    if value != "Not Defined":
                        html_parts.append(f'<tr><td>{key.replace("_", " ").title()}:</td><td>{self._escape_html(str(value))}</td></tr>')
            
            html_parts.append('</table>')
        
        # Impact analysis
        if 'impact_analysis' in cvss_analysis:
            html_parts.append('<h4>Impact Analysis:</h4>')
            html_parts.append('<ul>')
            for key, value in cvss_analysis['impact_analysis'].items():
                html_parts.append(f'<li><strong>{key.title()}:</strong> {self._escape_html(value)}</li>')
            html_parts.append('</ul>')
        
        # Exploitability analysis
        if 'exploitability_analysis' in cvss_analysis:
            html_parts.append('<h4>Exploitability Analysis:</h4>')
            html_parts.append('<ul>')
            for key, value in cvss_analysis['exploitability_analysis'].items():
                html_parts.append(f'<li><strong>{key.replace("_", " ").title()}:</strong> {self._escape_html(value)}</li>')
            html_parts.append('</ul>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _get_cvss_severity_text(self, score: float) -> str:
        """Get CVSS severity text"""
        if score >= 9.0:
            return "Critical"
        elif score >= 7.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score >= 0.1:
            return "Low"
        else:
            return "None"
    
    def _generate_cvss_analysis_markdown(self, cvss_analysis: Dict[str, Any]) -> str:
        """Generate Markdown for CVSS analysis"""
        if not cvss_analysis:
            return ""
        
        md_parts = []
        
        # Metrics
        if 'metrics' in cvss_analysis:
            md_parts.append("#### CVSS Metrics\n")
            
            # Base metrics
            if 'base' in cvss_analysis['metrics']:
                md_parts.append("**Base Metrics:**\n")
                base = cvss_analysis['metrics']['base']
                for key, value in base.items():
                    md_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
                md_parts.append("")
            
            # Temporal metrics
            if 'temporal' in cvss_analysis['metrics']:
                temporal = cvss_analysis['metrics']['temporal']
                has_temporal = any(v != "Not Defined" for v in temporal.values())
                if has_temporal:
                    md_parts.append("**Temporal Metrics:**\n")
                    for key, value in temporal.items():
                        if value != "Not Defined":
                            md_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
                    md_parts.append("")
        
        # Impact analysis
        if 'impact_analysis' in cvss_analysis:
            md_parts.append("#### Impact Analysis\n")
            for key, value in cvss_analysis['impact_analysis'].items():
                md_parts.append(f"- **{key.title()}:** {value}")
            md_parts.append("")
        
        # Exploitability analysis
        if 'exploitability_analysis' in cvss_analysis:
            md_parts.append("#### Exploitability Analysis\n")
            for key, value in cvss_analysis['exploitability_analysis'].items():
                md_parts.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def export_markdown(self, report: SecurityReport, filename: Optional[str] = None) -> str:
        """
        Export report as Markdown
        
        Args:
            report: Report to export
            filename: Custom filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report.report_id}_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        md_content = self._generate_markdown_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.logger.info(f"Exported Markdown report: {filepath}")
        return str(filepath)
    
    def _generate_markdown_report(self, report: SecurityReport) -> str:
        """Generate Markdown report content"""
        report_data = report.to_dict()
        
        md = f"""# {report.title}

**Report ID:** {report_data['report_id']}  
**Created:** {report_data['created_at']}  
**Status:** {report_data['status']}  
**Risk Score:** {report.calculate_risk_score():.1f}/10

## Executive Summary

{report_data.get('executive_summary', f"This report documents a **{report_data['vulnerability']['severity']}** severity vulnerability discovered during security assessment.")}

{'### Business Impact\n\n' + report_data.get('business_impact', 'No business impact analysis available.') + '\n' if report_data.get('business_impact') else ''}

{'### Risk Rating\n\n' + report_data.get('risk_rating', 'No risk rating available.') + '\n' if report_data.get('risk_rating') else ''}

## Target Information

| Field | Value |
|-------|-------|
| URL | {report_data['target'].get('url', 'N/A')} |
| Hostname | {report_data['target'].get('hostname', 'N/A')} |
| Browser | {report_data['target'].get('browser_name', 'N/A')} {report_data['target'].get('browser_version', '')} |
| Operating System | {report_data['target'].get('operating_system', 'N/A')} |

## Vulnerability Details

| Field | Value |
|-------|-------|
| Name | {report_data['vulnerability']['name']} |
| Severity | **{report_data['vulnerability']['severity']}** |
{'| CVE ID | ' + report_data['vulnerability'].get('cve_id', '') + ' |' if report_data['vulnerability'].get('cve_id') else ''}
{'| CWE ID | ' + report_data['vulnerability'].get('cweid', '') + ' |' if report_data['vulnerability'].get('cweid') else ''}
{'| OWASP Category | ' + report_data['vulnerability'].get('owasp_category', '') + ' |' if report_data['vulnerability'].get('owasp_category') else ''}

"""
        
        # Add CVSS section if available
        if report_data['vulnerability'].get('cvss_base_score'):
            md += f"""### CVSS v3.1 Score

| Metric | Value |
|--------|-------|
| Base Score | **{report_data['vulnerability']['cvss_base_score']}** ({self._get_cvss_severity_text(report_data['vulnerability']['cvss_base_score'])}) |
{'| Temporal Score | ' + str(report_data['vulnerability']['cvss_temporal_score']) + ' |' if report_data['vulnerability'].get('cvss_temporal_score') else ''}
| Vector | `{report_data['vulnerability']['cvss_vector']}` |

{self._generate_cvss_analysis_markdown(report_data['vulnerability'].get('cvss_analysis', {}))}
"""
        
        md += f"""### Description

{report_data['vulnerability'].get('description', 'No description provided.')}

{'### Technical Summary\n\n' + report_data.get('technical_summary', 'No technical summary available.') + '\n' if report_data.get('technical_summary') else ''}

### Impact

{report_data['vulnerability'].get('impact', 'No impact analysis provided.')}

## Evidence

"""
        
        # Add evidence
        for i, evidence in enumerate(report_data['evidence'], 1):
            md += f"\n### Evidence #{i}\n\n"
            md += f"**Timestamp:** {evidence.get('timestamp', 'N/A')}\n\n"
            
            if evidence.get('payload_used'):
                md += f"**Payload:**\n```\n{evidence['payload_used']}\n```\n\n"
            
            if evidence.get('screenshot_path'):
                md += f"**Screenshot:** [{os.path.basename(evidence['screenshot_path'])}]({evidence['screenshot_path']})\n\n"
        
        md += f"""
## Remediation

{report_data.get('remediation', 'No remediation steps provided.')}

## References

"""
        
        for ref in report_data.get('references', []):
            md += f"- [{ref}]({ref})\n"
        
        md += f"""

---

*Generated by ChromSploit Framework v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*  
*This report is confidential and intended only for authorized recipients.*
"""
        
        return md
    
    def calculate_cvss_score(self, report: SecurityReport, cvss_vector: Optional[str] = None) -> None:
        """
        Calculate CVSS score for the vulnerability
        
        Args:
            report: The security report
            cvss_vector: Optional CVSS v3.1 vector string
        """
        cvss = CVSSv3()
        
        if cvss_vector:
            # Parse provided vector
            cvss.parse_vector_string(cvss_vector)
        else:
            # Auto-calculate based on vulnerability type
            vuln_details = {
                'type': report.vulnerability.name.lower(),
                'severity': report.vulnerability.severity.value,
                'description': report.vulnerability.description
            }
            cvss = calculate_cvss_from_cve_details(vuln_details)
        
        # Calculate scores
        base_score = cvss.calculate_base_score()
        temporal_score = cvss.calculate_temporal_score(base_score)
        
        # Update report
        report.vulnerability.cvss_base_score = base_score
        report.vulnerability.cvss_temporal_score = temporal_score
        report.vulnerability.cvss_vector = cvss.get_vector_string()
        report.vulnerability.cvss_analysis = cvss.get_detailed_analysis()
        report.vulnerability.cvss_score = base_score  # For backward compatibility
        
        # Update severity based on CVSS score
        severity_rating = cvss.get_severity_rating(base_score)
        if severity_rating == "Critical":
            report.vulnerability.severity = ReportSeverity.CRITICAL
        elif severity_rating == "High":
            report.vulnerability.severity = ReportSeverity.HIGH
        elif severity_rating == "Medium":
            report.vulnerability.severity = ReportSeverity.MEDIUM
        elif severity_rating == "Low":
            report.vulnerability.severity = ReportSeverity.LOW
        else:
            report.vulnerability.severity = ReportSeverity.INFORMATIONAL
        
        self.logger.info(f"Calculated CVSS score for report {report.report_id}: {base_score} ({severity_rating})")
    
    def generate_executive_summary(self, report: SecurityReport) -> None:
        """
        Generate executive summary for the report
        
        Args:
            report: The security report
        """
        # Executive Summary
        exec_summary_parts = []
        
        # Overview
        severity = report.vulnerability.severity.value
        vuln_name = report.vulnerability.name
        target = report.target.hostname or report.target.url or "the target system"
        
        exec_summary_parts.append(
            f"A {severity.lower()} severity {vuln_name} vulnerability was identified in {target}. "
            f"This vulnerability could allow an attacker to {self._get_impact_summary(report.vulnerability)}."
        )
        
        # Risk assessment
        if report.vulnerability.cvss_base_score:
            exec_summary_parts.append(
                f"The vulnerability has been assigned a CVSS v3.1 base score of {report.vulnerability.cvss_base_score}, "
                f"indicating a {report.vulnerability.severity.value.lower()} risk to the organization."
            )
        
        # Evidence
        if report.evidence:
            exec_summary_parts.append(
                f"The security assessment team successfully demonstrated the vulnerability with {len(report.evidence)} "
                f"documented proof-of-concept{'s' if len(report.evidence) > 1 else ''}."
            )
        
        report.executive_summary = " ".join(exec_summary_parts)
        
        # Technical Summary
        tech_summary_parts = []
        
        # Technical details
        tech_summary_parts.append(report.vulnerability.description or f"A {vuln_name} vulnerability was discovered.")
        
        # Attack vector
        if report.vulnerability.cvss_analysis:
            exploitability = report.vulnerability.cvss_analysis.get('exploitability_analysis', {})
            if exploitability:
                tech_summary_parts.append(
                    f"The vulnerability {exploitability.get('attack_vector', 'can be exploited')}. "
                    f"{exploitability.get('user_interaction', '')}. "
                    f"{exploitability.get('privileges_required', '')}."
                )
        
        report.technical_summary = " ".join(tech_summary_parts).replace("  ", " ").strip()
        
        # Business Impact
        impact_parts = []
        
        if report.vulnerability.severity in [ReportSeverity.CRITICAL, ReportSeverity.HIGH]:
            impact_parts.append(
                "This vulnerability poses a significant risk to business operations and data security."
            )
        
        if report.vulnerability.impact:
            impact_parts.append(report.vulnerability.impact)
        
        # Add specific business impacts based on vulnerability type
        business_impacts = self._get_business_impact(report.vulnerability)
        if business_impacts:
            impact_parts.extend(business_impacts)
        
        report.business_impact = " ".join(impact_parts)
        
        # Risk Rating
        risk_score = report.calculate_risk_score()
        if risk_score >= 8:
            risk_level = "Critical"
            risk_action = "Immediate remediation is required."
        elif risk_score >= 6:
            risk_level = "High"
            risk_action = "Remediation should be prioritized within the current sprint."
        elif risk_score >= 4:
            risk_level = "Medium"
            risk_action = "Remediation should be scheduled within the next release cycle."
        elif risk_score >= 2:
            risk_level = "Low"
            risk_action = "Remediation can be scheduled as part of regular maintenance."
        else:
            risk_level = "Informational"
            risk_action = "No immediate action required, but should be noted for future reference."
        
        report.risk_rating = f"{risk_level} Risk (Score: {risk_score:.1f}/10) - {risk_action}"
        
        self.logger.info(f"Generated executive summary for report {report.report_id}")
    
    def _get_impact_summary(self, vulnerability: VulnerabilityDetails) -> str:
        """Get a brief impact summary based on vulnerability type"""
        vuln_name_lower = vulnerability.name.lower()
        
        if "xss" in vuln_name_lower or "cross-site scripting" in vuln_name_lower:
            return "execute malicious scripts in users' browsers, potentially stealing sensitive information or hijacking user sessions"
        elif "sql injection" in vuln_name_lower:
            return "access, modify, or delete database information, potentially compromising all application data"
        elif "rce" in vuln_name_lower or "remote code execution" in vuln_name_lower:
            return "execute arbitrary code on the server, potentially gaining full control of the system"
        elif "authentication" in vuln_name_lower:
            return "bypass authentication mechanisms and gain unauthorized access to the application"
        elif "authorization" in vuln_name_lower or "privilege" in vuln_name_lower:
            return "escalate privileges and access resources beyond their intended permissions"
        elif "information disclosure" in vuln_name_lower:
            return "access sensitive information that should not be publicly available"
        elif "dos" in vuln_name_lower or "denial of service" in vuln_name_lower:
            return "disrupt service availability, preventing legitimate users from accessing the application"
        elif "csrf" in vuln_name_lower:
            return "perform unauthorized actions on behalf of authenticated users"
        else:
            return "compromise the security of the application and its users"
    
    def _get_business_impact(self, vulnerability: VulnerabilityDetails) -> List[str]:
        """Get business impact statements based on vulnerability type and severity"""
        impacts = []
        
        if vulnerability.cvss_analysis:
            impact_analysis = vulnerability.cvss_analysis.get('impact_analysis', {})
            
            if impact_analysis.get('confidentiality', '').startswith('Total loss'):
                impacts.append("Complete breach of data confidentiality could lead to regulatory fines and loss of customer trust.")
            elif impact_analysis.get('confidentiality', '').startswith('Some loss'):
                impacts.append("Partial data exposure could damage reputation and require breach notifications.")
            
            if impact_analysis.get('integrity', '').startswith('Total loss'):
                impacts.append("Data integrity compromise could result in financial losses and operational disruptions.")
            
            if impact_analysis.get('availability', '').startswith('Total loss'):
                impacts.append("Service downtime would directly impact revenue and customer satisfaction.")
        
        # Add compliance considerations for high severity
        if vulnerability.severity in [ReportSeverity.CRITICAL, ReportSeverity.HIGH]:
            impacts.append("Failure to address this vulnerability may result in non-compliance with security standards (PCI-DSS, GDPR, etc.).")
        
        return impacts
    
    def get_report_summary(self, report: SecurityReport) -> str:
        """Get a brief summary of the report"""
        summary_parts = [
            f"{Colors.CYAN}Report Summary:{Colors.RESET}",
            f"  ID: {report.report_id}",
            f"  Title: {report.title}",
            f"  Severity: {report.vulnerability.severity.value}",
            f"  Target: {report.target.url or 'N/A'}",
            f"  Evidence Count: {len(report.evidence)}",
            f"  Risk Score: {report.calculate_risk_score():.1f}/10"
        ]
        
        if report.vulnerability.cvss_base_score:
            summary_parts.append(f"  CVSS Score: {report.vulnerability.cvss_base_score} ({report.vulnerability.cvss_vector})")
        
        if report.executive_summary:
            summary_parts.append(f"\n{Colors.YELLOW}Executive Summary:{Colors.RESET}")
            summary_parts.append(f"  {report.executive_summary[:200]}{'...' if len(report.executive_summary) > 200 else ''}")
        
        return "\n".join(summary_parts)

# Global report generator instance
_report_generator = None

def get_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """Get or create report generator instance"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator(output_dir)
    return _report_generator

# Example usage
if __name__ == "__main__":
    # Create report generator
    generator = ReportGenerator()
    
    # Create a new report
    report = generator.create_report(
        vulnerability_name="Cross-Site Scripting (XSS)",
        severity=ReportSeverity.HIGH,
        target_url="https://example.com/vulnerable-page"
    )
    
    # Set target info
    generator.set_target_info(
        report,
        browser_name="Chrome",
        browser_version="121.0.6167.85",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Add vulnerability details
    report.vulnerability.description = "A reflected XSS vulnerability was found in the search parameter."
    report.vulnerability.impact = "An attacker could execute arbitrary JavaScript in the victim's browser."
    report.vulnerability.cve_id = "CVE-2024-XXXXX"
    report.vulnerability.cvss_score = 7.5
    
    # Add evidence
    generator.add_evidence(
        report,
        payload='<script>alert("XSS")</script>',
        request_data={"method": "GET", "url": "/search?q=<script>alert('XSS')</script>"},
        response_data={"status": 200, "body": "Search results for: <script>alert('XSS')</script>"},
        console_output=["[*] Payload injected successfully", "[+] XSS vulnerability confirmed"],
        capture_screenshot=True
    )
    
    # Add remediation
    report.remediation = "Implement proper input validation and output encoding for all user inputs."
    report.references = [
        "https://owasp.org/www-community/attacks/xss/",
        "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
    ]
    
    # Export reports
    json_path = generator.export_json(report)
    html_path = generator.export_html(report)
    md_path = generator.export_markdown(report)
    
    print(f"\nReports generated:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")
    print(f"  Markdown: {md_path}")
    
    # Print summary
    print(f"\n{generator.get_report_summary(report)}")