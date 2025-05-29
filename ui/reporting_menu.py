#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Reporting Menu - Professional report management interface
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.reporting import (
    ReportGenerator, SecurityReport, ReportSeverity, 
    ReportStatus, get_report_generator
)

class ReportingMenu(EnhancedMenu):
    """Menu for managing security reports"""
    
    def __init__(self, parent=None):
        super().__init__("Professional Reporting", parent)
        self.logger = get_logger()
        self.report_generator = get_report_generator()
        self.current_report: Optional[SecurityReport] = None
        self.report_history: List[SecurityReport] = []
        
        self.set_info_text("Generate and manage professional security reports for bug bounty and pentesting")
        
        # Add menu items
        self.add_enhanced_item(
            "Create New Report", 
            self._create_new_report, 
            Colors.GREEN, 
            "n",
            "Start a new security assessment report"
        )
        
        self.add_enhanced_item(
            "View Current Report", 
            self._view_current_report, 
            Colors.CYAN,
            "v",
            "View and edit the active report"
        )
        
        self.add_enhanced_item(
            "Export Reports", 
            self._export_reports, 
            Colors.BLUE,
            "e",
            "Export reports in various formats"
        )
        
        self.add_enhanced_item(
            "Report History", 
            self._view_history, 
            Colors.YELLOW,
            "h",
            "View previously generated reports"
        )
        
        self.add_enhanced_item(
            "Report Templates", 
            self._manage_templates, 
            Colors.MAGENTA,
            "t",
            "Manage report templates"
        )
        
        self.add_enhanced_item(
            "Report Settings", 
            self._report_settings, 
            Colors.WHITE,
            "s",
            "Configure report settings"
        )
        
        self.add_enhanced_item(
            "Back", 
            lambda: "exit", 
            Colors.RED,
            "b"
        )
        
        # Check for active report
        if self.report_generator.active_report:
            self.current_report = self.report_generator.active_report
            self.add_notification(
                f"Active report: {self.current_report.report_id[:8]}...", 
                "info"
            )
    
    def _create_new_report(self):
        """Create a new security report"""
        self._clear()
        self._draw_box(80, "CREATE NEW REPORT")
        
        print(f"\n{Colors.CYAN}[*] Starting new security assessment report{Colors.RESET}")
        
        # Get vulnerability name
        vuln_name = input(f"\n{Colors.YELLOW}Vulnerability name: {Colors.RESET}")
        if not vuln_name:
            print(f"{Colors.RED}[!] Vulnerability name is required{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        # Get severity
        print(f"\n{Colors.CYAN}Select severity level:{Colors.RESET}")
        severities = list(ReportSeverity)
        for i, sev in enumerate(severities, 1):
            color = {
                ReportSeverity.CRITICAL: Colors.BRIGHT_RED,
                ReportSeverity.HIGH: Colors.RED,
                ReportSeverity.MEDIUM: Colors.YELLOW,
                ReportSeverity.LOW: Colors.GREEN,
                ReportSeverity.INFORMATIONAL: Colors.BLUE
            }.get(sev, Colors.WHITE)
            print(f"  {i}. {color}{sev.value}{Colors.RESET}")
        
        try:
            sev_choice = int(input(f"\n{Colors.YELLOW}Select severity (1-{len(severities)}): {Colors.RESET}"))
            severity = severities[sev_choice - 1]
        except (ValueError, IndexError):
            severity = ReportSeverity.MEDIUM
            print(f"{Colors.YELLOW}[!] Using default severity: {severity.value}{Colors.RESET}")
        
        # Get target URL
        target_url = input(f"\n{Colors.YELLOW}Target URL (optional): {Colors.RESET}")
        
        # Get additional details
        print(f"\n{Colors.CYAN}Additional Information:{Colors.RESET}")
        company = input(f"{Colors.YELLOW}Company/Client name (optional): {Colors.RESET}")
        tester_email = input(f"{Colors.YELLOW}Your email (optional): {Colors.RESET}")
        
        # Create the report
        self.current_report = self.report_generator.create_report(
            vulnerability_name=vuln_name,
            severity=severity,
            target_url=target_url if target_url else None
        )
        
        # Set additional info
        if company:
            self.current_report.company = company
        if tester_email:
            self.current_report.tester_email = tester_email
        
        # Add to history
        self.report_history.append(self.current_report)
        
        print(f"\n{Colors.GREEN}[+] Report created successfully!{Colors.RESET}")
        print(f"{Colors.CYAN}Report ID: {self.current_report.report_id}{Colors.RESET}")
        
        # Show summary
        print(f"\n{self.report_generator.get_report_summary(self.current_report)}")
        
        self.add_notification("New report created", "success")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _view_current_report(self):
        """View and edit current report"""
        self._clear()
        self._draw_box(80, "CURRENT REPORT")
        
        if not self.current_report:
            print(f"\n{Colors.YELLOW}[!] No active report. Create a new report first.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        # Show report summary
        print(f"\n{self.report_generator.get_report_summary(self.current_report)}")
        
        # Edit options
        print(f"\n{Colors.CYAN}Edit Options:{Colors.RESET}")
        print("  1. Add vulnerability details")
        print("  2. Add evidence")
        print("  3. Set target browser info")
        print("  4. Add remediation steps")
        print("  5. Add references")
        print("  6. Change report status")
        print("  7. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            self._edit_vulnerability_details()
        elif choice == "2":
            self._add_evidence()
        elif choice == "3":
            self._set_browser_info()
        elif choice == "4":
            self._add_remediation()
        elif choice == "5":
            self._add_references()
        elif choice == "6":
            self._change_status()
        
        return "continue"
    
    def _edit_vulnerability_details(self):
        """Edit vulnerability details"""
        print(f"\n{Colors.CYAN}[*] Edit vulnerability details{Colors.RESET}")
        
        desc = input(f"\n{Colors.YELLOW}Description (Enter to skip): {Colors.RESET}")
        if desc:
            self.current_report.vulnerability.description = desc
        
        impact = input(f"{Colors.YELLOW}Impact (Enter to skip): {Colors.RESET}")
        if impact:
            self.current_report.vulnerability.impact = impact
        
        cve_id = input(f"{Colors.YELLOW}CVE ID (Enter to skip): {Colors.RESET}")
        if cve_id:
            self.current_report.vulnerability.cve_id = cve_id
        
        try:
            cvss = input(f"{Colors.YELLOW}CVSS Score (0-10, Enter to skip): {Colors.RESET}")
            if cvss:
                self.current_report.vulnerability.cvss_score = float(cvss)
        except ValueError:
            pass
        
        self.current_report.updated_at = datetime.utcnow().isoformat()
        print(f"\n{Colors.GREEN}[+] Vulnerability details updated{Colors.RESET}")
        time.sleep(1)
    
    def _add_evidence(self):
        """Add evidence to report"""
        print(f"\n{Colors.CYAN}[*] Add evidence{Colors.RESET}")
        
        payload = input(f"\n{Colors.YELLOW}Payload used (Enter to skip): {Colors.RESET}")
        
        # Console output
        print(f"{Colors.YELLOW}Console output (Enter empty line to finish):{Colors.RESET}")
        console_output = []
        while True:
            line = input()
            if not line:
                break
            console_output.append(line)
        
        # Screenshot
        capture_ss = input(f"\n{Colors.YELLOW}Capture screenshot? (y/N): {Colors.RESET}")
        
        # Add evidence
        evidence = self.report_generator.add_evidence(
            self.current_report,
            payload=payload if payload else None,
            console_output=console_output if console_output else None,
            capture_screenshot=capture_ss.lower() == 'y'
        )
        
        print(f"\n{Colors.GREEN}[+] Evidence added successfully{Colors.RESET}")
        if evidence.screenshot_path:
            print(f"{Colors.CYAN}Screenshot saved: {evidence.screenshot_path}{Colors.RESET}")
        
        time.sleep(1)
    
    def _set_browser_info(self):
        """Set target browser information"""
        print(f"\n{Colors.CYAN}[*] Set browser information{Colors.RESET}")
        
        browser = input(f"\n{Colors.YELLOW}Browser name (e.g., Chrome): {Colors.RESET}")
        version = input(f"{Colors.YELLOW}Browser version: {Colors.RESET}")
        user_agent = input(f"{Colors.YELLOW}User agent string (Enter to skip): {Colors.RESET}")
        
        self.report_generator.set_target_info(
            self.current_report,
            browser_name=browser if browser else None,
            browser_version=version if version else None,
            user_agent=user_agent if user_agent else None
        )
        
        print(f"\n{Colors.GREEN}[+] Browser information updated{Colors.RESET}")
        time.sleep(1)
    
    def _add_remediation(self):
        """Add remediation steps"""
        print(f"\n{Colors.CYAN}[*] Add remediation steps{Colors.RESET}")
        print(f"{Colors.YELLOW}Enter remediation steps (Enter empty line to finish):{Colors.RESET}")
        
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        if lines:
            self.current_report.remediation = '\n'.join(lines)
            self.current_report.updated_at = datetime.utcnow().isoformat()
            print(f"\n{Colors.GREEN}[+] Remediation steps added{Colors.RESET}")
        
        time.sleep(1)
    
    def _add_references(self):
        """Add references"""
        print(f"\n{Colors.CYAN}[*] Add references{Colors.RESET}")
        print(f"{Colors.YELLOW}Enter reference URLs (Enter empty line to finish):{Colors.RESET}")
        
        while True:
            ref = input()
            if not ref:
                break
            self.current_report.references.append(ref)
        
        self.current_report.updated_at = datetime.utcnow().isoformat()
        print(f"\n{Colors.GREEN}[+] References added{Colors.RESET}")
        time.sleep(1)
    
    def _change_status(self):
        """Change report status"""
        print(f"\n{Colors.CYAN}[*] Change report status{Colors.RESET}")
        print(f"Current status: {self.current_report.status.value}")
        
        statuses = list(ReportStatus)
        for i, status in enumerate(statuses, 1):
            print(f"  {i}. {status.value}")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}Select new status: {Colors.RESET}"))
            self.current_report.status = statuses[choice - 1]
            self.current_report.updated_at = datetime.utcnow().isoformat()
            print(f"\n{Colors.GREEN}[+] Status updated to: {self.current_report.status.value}{Colors.RESET}")
        except (ValueError, IndexError):
            print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
        
        time.sleep(1)
    
    def _export_reports(self):
        """Export reports menu"""
        self._clear()
        self._draw_box(80, "EXPORT REPORTS")
        
        if not self.current_report:
            print(f"\n{Colors.YELLOW}[!] No active report to export{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}Export Formats:{Colors.RESET}")
        print("  1. JSON (Bug Bounty Platforms)")
        print("  2. HTML (Professional Report)")
        print("  3. Markdown (GitHub/GitLab)")
        print("  4. All Formats")
        print("  5. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select format: {Colors.RESET}")
        
        exported_files = []
        
        if choice in ["1", "4"]:
            json_path = self.report_generator.export_json(self.current_report)
            exported_files.append(("JSON", json_path))
        
        if choice in ["2", "4"]:
            html_path = self.report_generator.export_html(self.current_report)
            exported_files.append(("HTML", html_path))
        
        if choice in ["3", "4"]:
            md_path = self.report_generator.export_markdown(self.current_report)
            exported_files.append(("Markdown", md_path))
        
        if exported_files:
            print(f"\n{Colors.GREEN}[+] Reports exported successfully:{Colors.RESET}")
            for format_name, path in exported_files:
                print(f"  {Colors.CYAN}{format_name}:{Colors.RESET} {path}")
            
            self.add_notification(f"Exported {len(exported_files)} report(s)", "success")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _view_history(self):
        """View report history"""
        self._clear()
        self._draw_box(80, "REPORT HISTORY")
        
        if not self.report_history:
            print(f"\n{Colors.YELLOW}[!] No reports in history{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}Recent Reports:{Colors.RESET}")
        for i, report in enumerate(self.report_history[-10:], 1):
            severity_color = {
                ReportSeverity.CRITICAL: Colors.BRIGHT_RED,
                ReportSeverity.HIGH: Colors.RED,
                ReportSeverity.MEDIUM: Colors.YELLOW,
                ReportSeverity.LOW: Colors.GREEN,
                ReportSeverity.INFORMATIONAL: Colors.BLUE
            }.get(report.vulnerability.severity, Colors.WHITE)
            
            print(f"\n  {i}. {Colors.CYAN}ID:{Colors.RESET} {report.report_id[:8]}...")
            print(f"     {Colors.CYAN}Title:{Colors.RESET} {report.vulnerability.name}")
            print(f"     {Colors.CYAN}Severity:{Colors.RESET} {severity_color}{report.vulnerability.severity.value}{Colors.RESET}")
            print(f"     {Colors.CYAN}Status:{Colors.RESET} {report.status.value}")
            print(f"     {Colors.CYAN}Created:{Colors.RESET} {report.created_at}")
        
        print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
        print("  1. Load report")
        print("  2. Export report")
        print("  3. Delete report")
        print("  4. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            try:
                idx = int(input(f"{Colors.YELLOW}Report number: {Colors.RESET}")) - 1
                self.current_report = self.report_history[-(idx+1)]
                self.report_generator.active_report = self.current_report
                print(f"{Colors.GREEN}[+] Report loaded{Colors.RESET}")
                self.add_notification("Report loaded from history", "success")
            except (ValueError, IndexError):
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
        
        time.sleep(1)
        return "continue"
    
    def _manage_templates(self):
        """Manage report templates"""
        self._clear()
        self._draw_box(80, "REPORT TEMPLATES")
        
        print(f"\n{Colors.CYAN}Available Templates:{Colors.RESET}")
        print("  1. OWASP Top 10 Web Application")
        print("  2. Network Penetration Test")
        print("  3. API Security Assessment")
        print("  4. Mobile Application Security")
        print("  5. Cloud Security Assessment")
        print("  6. Custom Template")
        
        print(f"\n{Colors.YELLOW}[*] Template management coming soon{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _report_settings(self):
        """Configure report settings"""
        self._clear()
        self._draw_box(80, "REPORT SETTINGS")
        
        print(f"\n{Colors.CYAN}Current Settings:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Output Directory:{Colors.RESET} {self.report_generator.output_dir}")
        print(f"  {Colors.YELLOW}Screenshot Capture:{Colors.RESET} {'Enabled' if self.report_generator.screenshot_capture else 'Disabled'}")
        print(f"  {Colors.YELLOW}Auto-save:{Colors.RESET} Enabled")
        print(f"  {Colors.YELLOW}Report Format:{Colors.RESET} Professional")
        
        print(f"\n{Colors.CYAN}Company Information:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Default Company:{Colors.RESET} {getattr(self, 'default_company', 'Not set')}")
        print(f"  {Colors.YELLOW}Default Email:{Colors.RESET} {getattr(self, 'default_email', 'Not set')}")
        
        print(f"\n{Colors.YELLOW}[*] Settings configuration coming soon{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"

# Integration function for automatic reporting
def auto_report_exploit(exploit_name: str, 
                       target: str,
                       payload: Optional[str] = None,
                       result: Optional[Dict[str, Any]] = None,
                       severity: ReportSeverity = ReportSeverity.MEDIUM) -> SecurityReport:
    """
    Automatically create a report for an exploit execution
    
    Args:
        exploit_name: Name of the exploit
        target: Target URL or identifier
        payload: Payload used
        result: Exploit execution result
        severity: Vulnerability severity
        
    Returns:
        Generated SecurityReport
    """
    generator = get_report_generator()
    
    # Create report
    report = generator.create_report(
        vulnerability_name=exploit_name,
        severity=severity,
        target_url=target
    )
    
    # Add evidence
    console_output = []
    if result:
        console_output.append(f"[*] Exploit: {exploit_name}")
        console_output.append(f"[*] Target: {target}")
        console_output.append(f"[+] Status: {result.get('status', 'Unknown')}")
        if result.get('message'):
            console_output.append(f"[+] Result: {result['message']}")
    
    generator.add_evidence(
        report,
        payload=payload,
        console_output=console_output,
        capture_screenshot=True
    )
    
    # Auto-export
    generator.export_json(report)
    
    return report