#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Compliance & Legal Menu
Ensures compliance with legal requirements and bug bounty program rules
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.menu import Menu
from core.utils import Colors, print_banner, clear_screen, safe_execute
from core.enhanced_logger import get_logger
from core.compliance_tracking import ComplianceTracker, ComplianceRule, Authorization


class ComplianceMenu(Menu):
    """Menu for compliance and legal tracking"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.compliance_tracker = ComplianceTracker()
        self.current_user = "demo_user"  # In production, get from auth system
        
        # Add menu items
        self.add_item("1", "Legal Disclaimer", self.show_legal_disclaimer)
        self.add_item("2", "Compliance Rules", self.view_compliance_rules)
        self.add_item("3", "Authorization Management", self.authorization_management)
        self.add_item("4", "Compliance Checks", self.compliance_checks)
        self.add_item("5", "Legal Notices", self.legal_notices)
        self.add_item("6", "Compliance Report", self.generate_report)
        self.add_item("0", "Back", self.exit)
    
    def display(self):
        """Display compliance menu"""
        clear_screen()
        print_banner()
        print(f"\n{Colors.HEADER}=== Compliance & Legal Tracking ==={Colors.ENDC}\n")
        
        # Check for unacknowledged notices
        notices = self.compliance_tracker.get_unacknowledged_notices(self.current_user)
        if notices:
            print(f"{Colors.WARNING}[!] You have {len(notices)} unacknowledged legal notice(s){Colors.ENDC}")
            
        super().display()
    
    def show_legal_disclaimer(self):
        """Show legal disclaimer"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Legal Disclaimer ==={Colors.ENDC}\n")
        
        disclaimer = self.compliance_tracker.get_legal_disclaimer()
        print(disclaimer)
        
        response = input(f"\n{Colors.WARNING}Do you understand and agree to these terms? (yes/no): {Colors.ENDC}")
        
        if response.lower() == "yes":
            # Record acknowledgment
            try:
                notice = self.compliance_tracker.add_legal_notice(
                    "disclaimer",
                    "Framework Legal Disclaimer",
                    disclaimer,
                    requires_acknowledgment=True
                )
                self.compliance_tracker.acknowledge_notice(
                    notice.id, 
                    self.current_user,
                    ip_address="127.0.0.1"  # In production, get real IP
                )
                print(f"\n{Colors.OKGREEN}[+] Acknowledgment recorded{Colors.ENDC}")
            except Exception as e:
                self.logger.error(f"Error recording acknowledgment: {e}")
                
        else:
            print(f"\n{Colors.FAIL}[!] You must agree to the terms to use this framework{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def view_compliance_rules(self):
        """View compliance rules"""
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Compliance Rules ==={Colors.ENDC}\n")
            
            print("1. View All Rules")
            print("2. View by Category")
            print("3. View Critical Rules")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._view_all_rules()
            elif choice == "2":
                self._view_rules_by_category()
            elif choice == "3":
                self._view_critical_rules()
            elif choice == "0":
                break
    
    def authorization_management(self):
        """Manage testing authorizations"""
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Authorization Management ==={Colors.ENDC}\n")
            
            print("1. Add Authorization")
            print("2. Check Authorization")
            print("3. View Authorizations")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._add_authorization()
            elif choice == "2":
                self._check_authorization()
            elif choice == "3":
                self._view_authorizations()
            elif choice == "0":
                break
    
    def compliance_checks(self):
        """Perform compliance checks"""
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Compliance Checks ==={Colors.ENDC}\n")
            
            print("1. Pre-Test Compliance Check")
            print("2. Data Handling Check")
            print("3. Disclosure Compliance Check")
            print("4. View Check History")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._perform_pretest_check()
            elif choice == "2":
                self._perform_data_check()
            elif choice == "3":
                self._perform_disclosure_check()
            elif choice == "4":
                self._view_check_history()
            elif choice == "0":
                break
    
    def legal_notices(self):
        """Manage legal notices"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Legal Notices ==={Colors.ENDC}\n")
        
        try:
            # Show unacknowledged notices
            notices = self.compliance_tracker.get_unacknowledged_notices(self.current_user)
            
            if notices:
                print(f"{Colors.WARNING}Unacknowledged Notices:{Colors.ENDC}\n")
                
                for i, notice in enumerate(notices, 1):
                    print(f"{Colors.OKBLUE}[{i}]{Colors.ENDC} {notice.title}")
                    print(f"    Type: {notice.type}")
                    print(f"    Created: {notice.created_at.strftime('%Y-%m-%d')}\n")
                    
                choice = input(f"{Colors.WARNING}View notice (number) or 0 to skip: {Colors.ENDC}")
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(notices):
                        notice = notices[idx]
                        print(f"\n{Colors.HEADER}{notice.title}{Colors.ENDC}\n")
                        print(notice.content)
                        
                        if notice.requires_acknowledgment:
                            ack = input(f"\n{Colors.WARNING}Acknowledge this notice? (yes/no): {Colors.ENDC}")
                            if ack.lower() == "yes":
                                self.compliance_tracker.acknowledge_notice(
                                    notice.id, self.current_user
                                )
                                print(f"{Colors.OKGREEN}[+] Notice acknowledged{Colors.ENDC}")
                except ValueError:
                    pass
            else:
                print(f"{Colors.OKGREEN}[+] All legal notices have been acknowledged{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error managing legal notices: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def generate_report(self):
        """Generate compliance report"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Compliance Report ==={Colors.ENDC}\n")
        
        project_id = input(f"{Colors.WARNING}Project ID (or 'demo' for demo): {Colors.ENDC}")
        
        try:
            report = self.compliance_tracker.generate_compliance_report(
                project_id if project_id != "demo" else "demo_project"
            )
            
            print(f"\n{Colors.OKGREEN}Compliance Report Summary:{Colors.ENDC}")
            print(f"Generated: {report['generated_at']}")
            
            # Authorizations
            print(f"\n{Colors.HEADER}Authorizations:{Colors.ENDC}")
            if report['authorizations']:
                for auth in report['authorizations']:
                    status = "✓ Approved" if auth['approved'] else "✗ Pending"
                    print(f"  {status} - {auth['target']} ({auth['type']})")
            else:
                print(f"  {Colors.WARNING}No authorizations found{Colors.ENDC}")
                
            # Compliance checks
            print(f"\n{Colors.HEADER}Recent Compliance Checks:{Colors.ENDC}")
            if report['compliance_checks']:
                for check in report['compliance_checks'][:5]:
                    status_color = Colors.OKGREEN if check['status'] == "passed" else Colors.FAIL
                    print(f"  {status_color}{check['status'].upper()}{Colors.ENDC} - {check['type']} for {check['target']}")
            else:
                print(f"  {Colors.WARNING}No compliance checks performed{Colors.ENDC}")
                
            # Active rules
            print(f"\n{Colors.HEADER}Active Compliance Rules:{Colors.ENDC}")
            rules = report['active_rules']
            print(f"  Total: {rules['total']}")
            print(f"  Critical: {Colors.FAIL}{rules['critical']}{Colors.ENDC}")
            print(f"  High: {Colors.WARNING}{rules['high']}{Colors.ENDC}")
            
            # Risk assessment
            print(f"\n{Colors.HEADER}Risk Assessment:{Colors.ENDC}")
            risk = report['risk_assessment']
            risk_color = Colors.FAIL if risk['compliance_level'] == "critical" else Colors.WARNING
            print(f"  Compliance Level: {risk_color}{risk['compliance_level'].upper()}{Colors.ENDC}")
            print(f"  Recommendations:")
            for rec in risk['recommendations']:
                print(f"    • {rec}")
                
            # Save report
            save = input(f"\n{Colors.WARNING}Save full report to file? (yes/no): {Colors.ENDC}")
            if save.lower() == "yes":
                filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join("reports", filename)
                os.makedirs("reports", exist_ok=True)
                
                import json
                with open(filepath, 'w') as f:
                    json.dump(report, f, indent=2)
                    
                print(f"{Colors.OKGREEN}[+] Report saved to: {filepath}{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_all_rules(self):
        """View all compliance rules"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== All Compliance Rules ==={Colors.ENDC}\n")
        
        try:
            rules = self.compliance_tracker.get_active_rules()
            
            for rule in rules:
                severity_color = self._get_severity_color(rule.severity)
                print(f"{severity_color}[{rule.severity.upper()}]{Colors.ENDC} {rule.title}")
                print(f"  Category: {rule.category}")
                print(f"  Description: {rule.description}")
                print(f"  Requirements:")
                for req in rule.requirements:
                    print(f"    • {req}")
                print(f"  Consequences: {rule.consequences}\n")
                
        except Exception as e:
            self.logger.error(f"Error viewing rules: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_rules_by_category(self):
        """View rules by category"""
        clear_screen()
        print(f"\n{Colors.HEADER}Select Category:{Colors.ENDC}")
        print("1. Legal")
        print("2. Bounty Program")
        print("3. Ethical")
        print("4. Regulatory")
        
        choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        category_map = {
            "1": "legal",
            "2": "bounty_program",
            "3": "ethical",
            "4": "regulatory"
        }
        
        category = category_map.get(choice)
        if category:
            clear_screen()
            print(f"\n{Colors.HEADER}=== {category.replace('_', ' ').title()} Rules ==={Colors.ENDC}\n")
            
            try:
                rules = self.compliance_tracker.get_active_rules(category)
                
                if not rules:
                    print(f"{Colors.WARNING}No rules in this category{Colors.ENDC}")
                else:
                    for rule in rules:
                        severity_color = self._get_severity_color(rule.severity)
                        print(f"{severity_color}[{rule.severity.upper()}]{Colors.ENDC} {rule.title}")
                        print(f"  {rule.description}\n")
                        
            except Exception as e:
                self.logger.error(f"Error viewing rules: {e}")
                print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
                
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_critical_rules(self):
        """View only critical rules"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Critical Compliance Rules ==={Colors.ENDC}\n")
        
        try:
            rules = self.compliance_tracker.get_active_rules()
            critical_rules = [r for r in rules if r.severity == "critical"]
            
            if not critical_rules:
                print(f"{Colors.OKGREEN}[+] No critical rules active{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] {len(critical_rules)} critical rule(s) require attention:{Colors.ENDC}\n")
                
                for rule in critical_rules:
                    print(f"{Colors.FAIL}[CRITICAL]{Colors.ENDC} {rule.title}")
                    print(f"  {rule.description}")
                    print(f"  Consequences: {rule.consequences}")
                    print(f"  Requirements:")
                    for req in rule.requirements:
                        print(f"    • {req}")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error viewing critical rules: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _add_authorization(self):
        """Add new authorization"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Add Authorization ==={Colors.ENDC}\n")
        
        project_id = input(f"{Colors.WARNING}Project ID: {Colors.ENDC}")
        target = input(f"{Colors.WARNING}Target (e.g., example.com): {Colors.ENDC}")
        scope = input(f"{Colors.WARNING}Scope (comma-separated): {Colors.ENDC}").split(',')
        authorized_by = input(f"{Colors.WARNING}Authorized by: {Colors.ENDC}")
        
        print("\nAuthorization Type:")
        print("1. Written Consent")
        print("2. Bug Bounty Program")
        print("3. Responsible Disclosure")
        
        type_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        type_map = {
            "1": "written_consent",
            "2": "bug_bounty",
            "3": "responsible_disclosure"
        }
        auth_type = type_map.get(type_choice, "bug_bounty")
        
        try:
            auth = self.compliance_tracker.add_authorization(
                project_id=project_id,
                target=target,
                scope=[s.strip() for s in scope],
                authorized_by=authorized_by,
                authorization_type=auth_type,
                start_date=datetime.now()
            )
            
            print(f"\n{Colors.OKGREEN}[+] Authorization added successfully!{Colors.ENDC}")
            print(f"    ID: {auth.id}")
            print(f"    Target: {auth.target}")
            print(f"    Type: {auth.authorization_type}")
            print(f"\n{Colors.WARNING}[!] Note: Authorization requires approval before testing{Colors.ENDC}")
            
        except Exception as e:
            self.logger.error(f"Error adding authorization: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _check_authorization(self):
        """Check authorization for target"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Check Authorization ==={Colors.ENDC}\n")
        
        target = input(f"{Colors.WARNING}Target to check: {Colors.ENDC}")
        scope = input(f"{Colors.WARNING}Scope items (comma-separated): {Colors.ENDC}").split(',')
        
        try:
            authorized, issues = self.compliance_tracker.check_authorization(
                target, [s.strip() for s in scope]
            )
            
            if authorized:
                print(f"\n{Colors.OKGREEN}[+] Testing is AUTHORIZED for {target}{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}[!] Testing is NOT AUTHORIZED for {target}{Colors.ENDC}")
                print(f"\nIssues:")
                for issue in issues:
                    print(f"  • {issue}")
                    
        except Exception as e:
            self.logger.error(f"Error checking authorization: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_authorizations(self):
        """View authorizations (simplified)"""
        print(f"{Colors.WARNING}[!] Authorization viewing not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _perform_pretest_check(self):
        """Perform pre-test compliance check"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Pre-Test Compliance Check ==={Colors.ENDC}\n")
        
        target = input(f"{Colors.WARNING}Target: {Colors.ENDC}")
        
        try:
            check = self.compliance_tracker.perform_compliance_check(
                "pre_test", target, self.current_user
            )
            
            status_color = Colors.OKGREEN if check.status == "passed" else Colors.FAIL
            print(f"\n{Colors.HEADER}Check Result:{Colors.ENDC}")
            print(f"  Status: {status_color}{check.status.upper()}{Colors.ENDC}")
            
            if check.findings:
                print(f"\n{Colors.HEADER}Findings:{Colors.ENDC}")
                for finding in check.findings:
                    print(f"  • {finding}")
                    
            if check.recommendations:
                print(f"\n{Colors.HEADER}Recommendations:{Colors.ENDC}")
                for rec in check.recommendations:
                    print(f"  • {rec}")
                    
        except Exception as e:
            self.logger.error(f"Error performing check: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _perform_data_check(self):
        """Perform data handling compliance check"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Data Handling Compliance Check ==={Colors.ENDC}\n")
        
        target = input(f"{Colors.WARNING}Target: {Colors.ENDC}")
        
        try:
            check = self.compliance_tracker.perform_compliance_check(
                "data_handling", target, self.current_user
            )
            
            print(f"\n{Colors.HEADER}Data Handling Guidelines:{Colors.ENDC}")
            for rec in check.recommendations:
                print(f"  ✓ {rec}")
                
        except Exception as e:
            self.logger.error(f"Error performing check: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _perform_disclosure_check(self):
        """Perform disclosure compliance check"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Disclosure Compliance Check ==={Colors.ENDC}\n")
        
        target = input(f"{Colors.WARNING}Target: {Colors.ENDC}")
        
        try:
            check = self.compliance_tracker.perform_compliance_check(
                "disclosure", target, self.current_user
            )
            
            print(f"\n{Colors.HEADER}Responsible Disclosure Requirements:{Colors.ENDC}")
            for rec in check.recommendations:
                print(f"  ✓ {rec}")
                
        except Exception as e:
            self.logger.error(f"Error performing check: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_check_history(self):
        """View compliance check history"""
        print(f"{Colors.WARNING}[!] Check history viewing not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "critical": Colors.FAIL,
            "high": Colors.WARNING,
            "medium": Colors.OKBLUE,
            "low": Colors.OKGREEN
        }
        return colors.get(severity, Colors.ENDC)


if __name__ == "__main__":
    # Test the menu
    menu = ComplianceMenu()
    menu.run()