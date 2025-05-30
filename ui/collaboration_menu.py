#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Collaboration Menu
Team collaboration features for bug bounty and pentesting
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
from core.collaboration import CollaborationManager, TeamMember, Project, SharedFinding, TaskAssignment


class CollaborationMenu(Menu):
    """Menu for team collaboration features"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.collab_manager = CollaborationManager()
        self.current_user = None
        self.current_project = None
        
        # Add menu items
        self.add_item("1", "Team Management", self.team_management)
        self.add_item("2", "Project Management", self.project_management)
        self.add_item("3", "Findings & Vulnerabilities", self.findings_management)
        self.add_item("4", "Task Assignments", self.task_management)
        self.add_item("5", "Activity Dashboard", self.activity_dashboard)
        self.add_item("6", "Export Reports", self.export_reports)
        self.add_item("0", "Back", self.exit)
    
    def display(self):
        """Display collaboration menu"""
        clear_screen()
        print_banner()
        print(f"\n{Colors.HEADER}=== Team Collaboration Center ==={Colors.ENDC}\n")
        
        if self.current_user:
            print(f"Logged in as: {Colors.OKGREEN}{self.current_user.username}{Colors.ENDC} ({self.current_user.role})")
        else:
            print(f"{Colors.WARNING}[!] No user logged in. Please select a team member.{Colors.ENDC}")
            
        if self.current_project:
            print(f"Current Project: {Colors.OKBLUE}{self.current_project.name}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}[!] No project selected.{Colors.ENDC}")
            
        print()
        super().display()
    
    def team_management(self):
        """Manage team members"""
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Team Management ==={Colors.ENDC}\n")
            
            print("1. View Team Members")
            print("2. Add Team Member")
            print("3. Select Current User")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._view_team_members()
            elif choice == "2":
                self._add_team_member()
            elif choice == "3":
                self._select_current_user()
            elif choice == "0":
                break
    
    def project_management(self):
        """Manage projects"""
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Project Management ==={Colors.ENDC}\n")
            
            print("1. View Projects")
            print("2. Create Project")
            print("3. Select Current Project")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._view_projects()
            elif choice == "2":
                self._create_project()
            elif choice == "3":
                self._select_current_project()
            elif choice == "0":
                break
    
    def findings_management(self):
        """Manage security findings"""
        if not self.current_project:
            print(f"{Colors.FAIL}[!] Please select a project first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Findings Management - {self.current_project.name} ==={Colors.ENDC}\n")
            
            print("1. View Findings")
            print("2. Add Finding")
            print("3. Update Finding Status")
            print("4. Add Comment to Finding")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._view_findings()
            elif choice == "2":
                self._add_finding()
            elif choice == "3":
                self._update_finding_status()
            elif choice == "4":
                self._add_comment()
            elif choice == "0":
                break
    
    def task_management(self):
        """Manage task assignments"""
        if not self.current_user:
            print(f"{Colors.FAIL}[!] Please select a user first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        while True:
            clear_screen()
            print(f"\n{Colors.HEADER}=== Task Management ==={Colors.ENDC}\n")
            
            print("1. My Tasks")
            print("2. Assign Task")
            print("3. Update Task Status")
            print("0. Back")
            
            choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
            
            if choice == "1":
                self._view_my_tasks()
            elif choice == "2":
                self._assign_task()
            elif choice == "3":
                self._update_task_status()
            elif choice == "0":
                break
    
    def activity_dashboard(self):
        """View activity dashboard"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Activity Dashboard ==={Colors.ENDC}\n")
        
        try:
            activities = self.collab_manager.get_activity_log(limit=20)
            
            if not activities:
                print(f"{Colors.WARNING}[!] No recent activity{Colors.ENDC}")
            else:
                print(f"Recent Activity ({len(activities)} items):\n")
                
                for activity in activities:
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    time_ago = self._format_time_ago(timestamp)
                    
                    action_color = self._get_action_color(activity['action'])
                    print(f"{action_color}[{time_ago}]{Colors.ENDC} {activity['username']} {activity['action'].replace('_', ' ')}")
                    
                    if activity['details']:
                        for key, value in activity['details'].items():
                            print(f"    {key}: {value}")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error viewing activity: {e}")
            print(f"{Colors.FAIL}[!] Error viewing activity: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def export_reports(self):
        """Export project reports"""
        if not self.current_project:
            print(f"{Colors.FAIL}[!] Please select a project first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Export Report - {self.current_project.name} ==={Colors.ENDC}\n")
        
        try:
            report = self.collab_manager.export_project_report(self.current_project.id)
            
            if report:
                # Display report summary
                stats = report['statistics']
                print(f"{Colors.OKGREEN}Report Summary:{Colors.ENDC}")
                print(f"  Total Findings: {stats['total_findings']}")
                print(f"    Critical: {Colors.FAIL}{stats['critical']}{Colors.ENDC}")
                print(f"    High: {Colors.WARNING}{stats['high']}{Colors.ENDC}")
                print(f"    Medium: {Colors.OKBLUE}{stats['medium']}{Colors.ENDC}")
                print(f"    Low: {Colors.OKGREEN}{stats['low']}{Colors.ENDC}")
                print(f"    Info: {stats['info']}")
                print(f"\n  Tasks: {stats['completed_tasks']}/{stats['total_tasks']} completed")
                
                # Save report
                filename = f"report_{self.current_project.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join("reports", filename)
                os.makedirs("reports", exist_ok=True)
                
                import json
                with open(filepath, 'w') as f:
                    json.dump(report, f, indent=2)
                    
                print(f"\n{Colors.OKGREEN}[+] Report exported to: {filepath}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] Failed to generate report{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            print(f"{Colors.FAIL}[!] Error exporting report: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_team_members(self):
        """View all team members"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Team Members ==={Colors.ENDC}\n")
        
        # In a real implementation, this would query the database
        print(f"{Colors.WARNING}[!] Team member viewing not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _add_team_member(self):
        """Add a new team member"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Add Team Member ==={Colors.ENDC}\n")
        
        username = input(f"{Colors.WARNING}Username: {Colors.ENDC}")
        email = input(f"{Colors.WARNING}Email: {Colors.ENDC}")
        
        print("\nSelect role:")
        print("1. Admin")
        print("2. Pentester")
        print("3. Viewer")
        
        role_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        role_map = {"1": "admin", "2": "pentester", "3": "viewer"}
        role = role_map.get(role_choice, "pentester")
        
        try:
            member = self.collab_manager.add_team_member(username, email, role)
            print(f"\n{Colors.OKGREEN}[+] Team member added successfully!{Colors.ENDC}")
            print(f"    ID: {member.id}")
            print(f"    Username: {member.username}")
            print(f"    Role: {member.role}")
            
        except Exception as e:
            self.logger.error(f"Error adding team member: {e}")
            print(f"{Colors.FAIL}[!] Error adding team member: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _select_current_user(self):
        """Select current user (simplified for demo)"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Select Current User ==={Colors.ENDC}\n")
        
        # For demo purposes, create a default user
        try:
            self.current_user = self.collab_manager.add_team_member(
                "demo_user", "demo@chromsploit.com", "pentester"
            )
            print(f"{Colors.OKGREEN}[+] Logged in as: {self.current_user.username}{Colors.ENDC}")
        except:
            # User might already exist
            self.current_user = TeamMember(
                id="demo",
                username="demo_user",
                email="demo@chromsploit.com",
                role="pentester",
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            print(f"{Colors.OKGREEN}[+] Using demo user: {self.current_user.username}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_projects(self):
        """View all projects"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Projects ==={Colors.ENDC}\n")
        
        # In a real implementation, this would query the database
        print(f"{Colors.WARNING}[!] Project viewing not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _create_project(self):
        """Create a new project"""
        if not self.current_user:
            print(f"{Colors.FAIL}[!] Please select a user first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Create Project ==={Colors.ENDC}\n")
        
        name = input(f"{Colors.WARNING}Project Name: {Colors.ENDC}")
        description = input(f"{Colors.WARNING}Description: {Colors.ENDC}")
        target = input(f"{Colors.WARNING}Target (e.g., example.com): {Colors.ENDC}")
        scope = input(f"{Colors.WARNING}Scope (comma-separated): {Colors.ENDC}").split(',')
        bounty_program = input(f"{Colors.WARNING}Bounty Program (optional): {Colors.ENDC}")
        
        try:
            project = self.collab_manager.create_project(
                name=name,
                description=description,
                target=target,
                scope=[s.strip() for s in scope],
                created_by=self.current_user.id,
                bounty_program=bounty_program if bounty_program else None
            )
            
            self.current_project = project
            print(f"\n{Colors.OKGREEN}[+] Project created successfully!{Colors.ENDC}")
            print(f"    ID: {project.id}")
            print(f"    Name: {project.name}")
            print(f"    Target: {project.target}")
            
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            print(f"{Colors.FAIL}[!] Error creating project: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _select_current_project(self):
        """Select current project (simplified)"""
        # For demo, use the created project or create a default one
        if not self.current_user:
            print(f"{Colors.FAIL}[!] Please select a user first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        if not self.current_project:
            # Create a demo project
            try:
                self.current_project = self.collab_manager.create_project(
                    name="Demo Bug Bounty Project",
                    description="Demo project for ChromSploit",
                    target="demo.example.com",
                    scope=["*.demo.example.com"],
                    created_by=self.current_user.id,
                    bounty_program="Demo Program"
                )
                print(f"{Colors.OKGREEN}[+] Selected demo project: {self.current_project.name}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}[!] Error selecting project: {e}{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}[+] Current project: {self.current_project.name}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_findings(self):
        """View project findings"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Findings - {self.current_project.name} ==={Colors.ENDC}\n")
        
        try:
            findings = self.collab_manager.get_project_findings(self.current_project.id)
            
            if not findings:
                print(f"{Colors.WARNING}[!] No findings yet{Colors.ENDC}")
            else:
                for i, finding in enumerate(findings, 1):
                    severity_color = self._get_severity_color(finding.severity)
                    status_color = self._get_status_color(finding.status)
                    
                    print(f"{Colors.OKBLUE}[{i}]{Colors.ENDC} {finding.title}")
                    print(f"    Severity: {severity_color}{finding.severity.upper()}{Colors.ENDC}")
                    print(f"    Status: {status_color}{finding.status}{Colors.ENDC}")
                    if finding.cve_id:
                        print(f"    CVE: {Colors.WARNING}{finding.cve_id}{Colors.ENDC}")
                    print(f"    Created: {finding.created_at.strftime('%Y-%m-%d %H:%M')}")
                    print(f"    Description: {finding.description[:100]}...")
                    if finding.comments:
                        print(f"    Comments: {len(finding.comments)}")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error viewing findings: {e}")
            print(f"{Colors.FAIL}[!] Error viewing findings: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _add_finding(self):
        """Add a new finding"""
        if not self.current_user:
            print(f"{Colors.FAIL}[!] Please select a user first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Add Finding ==={Colors.ENDC}\n")
        
        title = input(f"{Colors.WARNING}Title: {Colors.ENDC}")
        description = input(f"{Colors.WARNING}Description: {Colors.ENDC}")
        
        print("\nSelect severity:")
        print("1. Critical")
        print("2. High")
        print("3. Medium")
        print("4. Low")
        print("5. Info")
        
        severity_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        severity_map = {
            "1": "critical",
            "2": "high",
            "3": "medium",
            "4": "low",
            "5": "info"
        }
        severity = severity_map.get(severity_choice, "medium")
        
        cve_id = input(f"{Colors.WARNING}CVE ID (optional): {Colors.ENDC}")
        
        try:
            finding = self.collab_manager.add_finding(
                project_id=self.current_project.id,
                title=title,
                description=description,
                severity=severity,
                created_by=self.current_user.id,
                cve_id=cve_id if cve_id else None
            )
            
            print(f"\n{Colors.OKGREEN}[+] Finding added successfully!{Colors.ENDC}")
            print(f"    ID: {finding.id}")
            print(f"    Title: {finding.title}")
            print(f"    Severity: {finding.severity}")
            
        except Exception as e:
            self.logger.error(f"Error adding finding: {e}")
            print(f"{Colors.FAIL}[!] Error adding finding: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _update_finding_status(self):
        """Update finding status"""
        # Simplified implementation
        print(f"{Colors.WARNING}[!] Finding status update not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _add_comment(self):
        """Add comment to finding"""
        # Simplified implementation
        print(f"{Colors.WARNING}[!] Comment functionality not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _view_my_tasks(self):
        """View user's tasks"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== My Tasks ==={Colors.ENDC}\n")
        
        try:
            tasks = self.collab_manager.get_user_tasks(self.current_user.id)
            
            if not tasks:
                print(f"{Colors.WARNING}[!] No tasks assigned{Colors.ENDC}")
            else:
                for i, task in enumerate(tasks, 1):
                    priority_color = self._get_priority_color(task.priority)
                    status_color = self._get_status_color(task.status)
                    
                    print(f"{Colors.OKBLUE}[{i}]{Colors.ENDC} {task.title}")
                    print(f"    Priority: {priority_color}{task.priority.upper()}{Colors.ENDC}")
                    print(f"    Status: {status_color}{task.status}{Colors.ENDC}")
                    if task.due_date:
                        print(f"    Due: {task.due_date.strftime('%Y-%m-%d')}")
                    print(f"    Description: {task.description[:100]}...")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error viewing tasks: {e}")
            print(f"{Colors.FAIL}[!] Error viewing tasks: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _assign_task(self):
        """Assign a new task"""
        if not self.current_user or not self.current_project:
            print(f"{Colors.FAIL}[!] Please select a user and project first{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Assign Task ==={Colors.ENDC}\n")
        
        title = input(f"{Colors.WARNING}Task Title: {Colors.ENDC}")
        description = input(f"{Colors.WARNING}Description: {Colors.ENDC}")
        
        # For demo, assign to self
        assigned_to = self.current_user.id
        
        print("\nSelect priority:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        
        priority_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        priority_map = {"1": "high", "2": "medium", "3": "low"}
        priority = priority_map.get(priority_choice, "medium")
        
        try:
            task = self.collab_manager.assign_task(
                project_id=self.current_project.id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                assigned_by=self.current_user.id,
                priority=priority
            )
            
            print(f"\n{Colors.OKGREEN}[+] Task assigned successfully!{Colors.ENDC}")
            print(f"    ID: {task.id}")
            print(f"    Title: {task.title}")
            print(f"    Priority: {task.priority}")
            
        except Exception as e:
            self.logger.error(f"Error assigning task: {e}")
            print(f"{Colors.FAIL}[!] Error assigning task: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _update_task_status(self):
        """Update task status"""
        # Simplified implementation
        print(f"{Colors.WARNING}[!] Task status update not fully implemented{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "critical": Colors.FAIL,
            "high": Colors.WARNING,
            "medium": Colors.OKBLUE,
            "low": Colors.OKGREEN,
            "info": Colors.ENDC
        }
        return colors.get(severity, Colors.ENDC)
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status"""
        colors = {
            "open": Colors.FAIL,
            "in_progress": Colors.WARNING,
            "resolved": Colors.OKGREEN,
            "completed": Colors.OKGREEN,
            "blocked": Colors.FAIL,
            "pending": Colors.OKBLUE
        }
        return colors.get(status, Colors.ENDC)
    
    def _get_priority_color(self, priority: str) -> str:
        """Get color for priority"""
        colors = {
            "high": Colors.FAIL,
            "medium": Colors.WARNING,
            "low": Colors.OKGREEN
        }
        return colors.get(priority, Colors.ENDC)
    
    def _get_action_color(self, action: str) -> str:
        """Get color for action type"""
        if "created" in action:
            return Colors.OKGREEN
        elif "updated" in action:
            return Colors.WARNING
        elif "deleted" in action:
            return Colors.FAIL
        else:
            return Colors.OKBLUE
    
    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as time ago"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"


if __name__ == "__main__":
    # Test the menu
    menu = CollaborationMenu()
    menu.run()