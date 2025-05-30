#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Session Management Menu
Interactive menu for managing C2 framework sessions
"""

import os
import time
from typing import List, Optional
from datetime import datetime

from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from modules.session_manager import get_session_manager, Session


class SessionMenu(EnhancedMenu):
    """Menu for managing C2 framework sessions"""
    
    def __init__(self):
        super().__init__(
            title="🎯 Session Management",
            description="Manage active sessions from C2 frameworks"
        )
        
        self.session_manager = get_session_manager()
        self.logger = get_logger()
        
        # Start session monitoring
        self.session_manager.start_monitoring()
        
        self._setup_menu_items()
    
    def _setup_menu_items(self):
        """Setup menu items"""
        self.add_enhanced_item(
            "📋 List Active Sessions",
            self.list_sessions,
            color=Colors.CYAN,
            description="Show all active sessions from C2 frameworks",
            key="1"
        )
        
        self.add_enhanced_item(
            "🖥️ Open Interactive Shell",
            self.open_shell,
            color=Colors.GREEN,
            description="Open shell for a specific session",
            key="2"
        )
        
        self.add_enhanced_item(
            "⚡ Execute Command",
            self.execute_command,
            color=Colors.YELLOW,
            description="Run a command in a session",
            key="3"
        )
        
        self.add_enhanced_item(
            "📊 Session Statistics",
            self.show_statistics,
            color=Colors.BLUE,
            description="View session statistics and metrics",
            key="4"
        )
        
        self.add_enhanced_item(
            "🔄 Refresh Sessions",
            self.refresh_sessions,
            color=Colors.MAGENTA,
            description="Force refresh of session list",
            key="5"
        )
        
        self.add_enhanced_item(
            "💾 Export Sessions",
            self.export_sessions,
            color=Colors.PURPLE,
            description="Export session data to file",
            key="6"
        )
        
        self.add_enhanced_item(
            "🔍 Session Details",
            self.session_details,
            color=Colors.WHITE,
            description="View detailed information about a session",
            key="7"
        )
        
        self.add_enhanced_item(
            "⚙️ Framework Status",
            self.framework_status,
            color=Colors.ORANGE,
            description="Check C2 framework connections",
            key="8"
        )
    
    def run(self):
        """Run the session menu"""
        self.display()
    
    def list_sessions(self):
        """List all active sessions"""
        self.clear_screen()
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}📋 Active Sessions{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        
        sessions = self.session_manager.get_all_sessions()
        
        if not sessions:
            print(f"\n{Colors.YELLOW}[!] No active sessions found{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Make sure C2 frameworks are running and have active sessions{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}[+] Found {len(sessions)} active session(s){Colors.RESET}\n")
            
            # Table header
            print(f"{Colors.CYAN}{'ID':<15} {'Framework':<12} {'Target':<20} {'Type':<12} {'User@Host':<25} {'Last Seen':<15}{Colors.RESET}")
            print("-" * 100)
            
            for session in sessions:
                session_key = f"{session.framework}_{session.id}"
                user_host = f"{session.username}@{session.hostname}"
                last_seen = self._format_time_ago(session.last_checkin)
                
                # Color based on framework
                if session.framework == 'sliver':
                    color = Colors.BRIGHT_BLUE
                elif session.framework == 'metasploit':
                    color = Colors.BRIGHT_RED
                else:
                    color = Colors.WHITE
                
                print(f"{color}{session_key:<15} {session.framework:<12} {session.target_ip:<20} {session.session_type:<12} {user_host:<25} {last_seen:<15}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def open_shell(self):
        """Open interactive shell for a session"""
        sessions = self.session_manager.get_all_sessions()
        
        if not sessions:
            print(f"{Colors.YELLOW}[!] No active sessions available{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Select session
        session = self._select_session(sessions)
        if not session:
            return
        
        session_key = f"{session.framework}_{session.id}"
        
        print(f"\n{Colors.CYAN}[*] Opening shell for session {session_key}...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] A new terminal window will open with the interactive shell{Colors.RESET}")
        
        if self.session_manager.open_shell(session_key):
            print(f"{Colors.GREEN}[+] Shell opened successfully!{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Check the new terminal window{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Failed to open shell{Colors.RESET}")
            print(f"{Colors.YELLOW}[*] Make sure the C2 framework is properly configured{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def execute_command(self):
        """Execute a command in a session"""
        sessions = self.session_manager.get_all_sessions()
        
        if not sessions:
            print(f"{Colors.YELLOW}[!] No active sessions available{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Select session
        session = self._select_session(sessions)
        if not session:
            return
        
        session_key = f"{session.framework}_{session.id}"
        
        # Get command
        print(f"\n{Colors.CYAN}[*] Session: {session_key}{Colors.RESET}")
        command = input(f"{Colors.CYAN}Enter command to execute: {Colors.RESET}")
        
        if not command:
            print(f"{Colors.YELLOW}[!] No command entered{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}[*] Executing command...{Colors.RESET}")
        
        success, output = self.session_manager.execute_command(session_key, command)
        
        if success:
            print(f"\n{Colors.GREEN}[+] Command executed successfully!{Colors.RESET}")
            print(f"\n{Colors.CYAN}Output:{Colors.RESET}")
            print("-" * 60)
            print(output)
            print("-" * 60)
        else:
            print(f"\n{Colors.RED}[!] Command execution failed{Colors.RESET}")
            print(f"{Colors.YELLOW}Error: {output}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def session_details(self):
        """Show detailed information about a session"""
        sessions = self.session_manager.get_all_sessions()
        
        if not sessions:
            print(f"{Colors.YELLOW}[!] No active sessions available{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Select session
        session = self._select_session(sessions)
        if not session:
            return
        
        self.clear_screen()
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}🔍 Session Details{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        
        session_key = f"{session.framework}_{session.id}"
        
        print(f"\n{Colors.BLUE}Basic Information:{Colors.RESET}")
        print(f"  Session ID: {session_key}")
        print(f"  Framework: {session.framework}")
        print(f"  Type: {session.session_type}")
        print(f"  Target IP: {session.target_ip}")
        print(f"  Username: {session.username}")
        print(f"  Hostname: {session.hostname}")
        
        print(f"\n{Colors.BLUE}Timing:{Colors.RESET}")
        print(f"  Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Check-in: {session.last_checkin.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Active: {'Yes' if session.active else 'No'}")
        
        if session.metadata:
            print(f"\n{Colors.BLUE}Metadata:{Colors.RESET}")
            for key, value in session.metadata.items():
                print(f"  {key}: {value}")
        
        if session.commands_history:
            print(f"\n{Colors.BLUE}Recent Commands:{Colors.RESET}")
            for cmd in session.commands_history[-5:]:  # Last 5 commands
                timestamp = datetime.fromisoformat(cmd['timestamp']).strftime('%H:%M:%S')
                status = "✓" if cmd['success'] else "✗"
                print(f"  [{timestamp}] {status} {cmd['command']}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def show_statistics(self):
        """Show session statistics"""
        self.clear_screen()
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}📊 Session Statistics{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        
        stats = self.session_manager.get_statistics()
        
        print(f"\n{Colors.BLUE}Overview:{Colors.RESET}")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  Active Sessions: {stats['active_sessions']}")
        print(f"  Connected Frameworks: {stats['frameworks_connected']}")
        
        if stats['sessions_by_framework']:
            print(f"\n{Colors.BLUE}Sessions by Framework:{Colors.RESET}")
            for framework, count in stats['sessions_by_framework'].items():
                print(f"  {framework}: {count}")
        
        if stats['sessions_by_type']:
            print(f"\n{Colors.BLUE}Sessions by Type:{Colors.RESET}")
            for session_type, count in stats['sessions_by_type'].items():
                print(f"  {session_type}: {count}")
        
        if stats['sessions_by_os']:
            print(f"\n{Colors.BLUE}Sessions by OS:{Colors.RESET}")
            for os_type, count in stats['sessions_by_os'].items():
                print(f"  {os_type}: {count}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def refresh_sessions(self):
        """Force refresh session list"""
        print(f"\n{Colors.CYAN}[*] Refreshing session list...{Colors.RESET}")
        
        # Manually trigger session update
        old_count = len(self.session_manager.get_all_sessions())
        
        # Re-check all frameworks
        for name, framework in self.session_manager.frameworks.items():
            print(f"{Colors.CYAN}[*] Checking {name}...{Colors.RESET}")
            try:
                sessions = framework.get_sessions()
                print(f"{Colors.GREEN}[+] Found {len(sessions)} session(s) in {name}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Error checking {name}: {e}{Colors.RESET}")
        
        new_count = len(self.session_manager.get_all_sessions())
        
        if new_count != old_count:
            print(f"\n{Colors.GREEN}[+] Session count changed: {old_count} → {new_count}{Colors.RESET}")
        else:
            print(f"\n{Colors.BLUE}[*] No changes in session count ({new_count} sessions){Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def export_sessions(self):
        """Export session data"""
        print(f"\n{Colors.CYAN}[*] Exporting session data...{Colors.RESET}")
        
        filename = self.session_manager.export_sessions()
        
        print(f"{Colors.GREEN}[+] Sessions exported to: {filename}{Colors.RESET}")
        
        # Show export summary
        sessions = self.session_manager.get_all_sessions()
        print(f"\n{Colors.BLUE}Export Summary:{Colors.RESET}")
        print(f"  Total Sessions: {len(self.session_manager.sessions)}")
        print(f"  Active Sessions: {len(sessions)}")
        print(f"  File Size: {os.path.getsize(filename)} bytes")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def framework_status(self):
        """Check C2 framework connections"""
        self.clear_screen()
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}⚙️ C2 Framework Status{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        
        frameworks_info = {
            'sliver': {
                'name': 'Sliver C2',
                'port': 31337,
                'process': 'sliver-server'
            },
            'metasploit': {
                'name': 'Metasploit',
                'port': 55553,
                'process': 'msfconsole'
            }
        }
        
        for framework_id, info in frameworks_info.items():
            print(f"\n{Colors.BLUE}{info['name']}:{Colors.RESET}")
            
            # Check if framework is in session manager
            if framework_id in self.session_manager.frameworks:
                framework = self.session_manager.frameworks[framework_id]
                connected = framework.check_connection()
                
                if connected:
                    print(f"  Status: {Colors.GREEN}Connected ✓{Colors.RESET}")
                    sessions = [s for s in self.session_manager.get_all_sessions() if s.framework == framework_id]
                    print(f"  Active Sessions: {len(sessions)}")
                else:
                    print(f"  Status: {Colors.YELLOW}Disconnected{Colors.RESET}")
                    print(f"  Check if {info['process']} is running")
            else:
                print(f"  Status: {Colors.RED}Not Available{Colors.RESET}")
                print(f"  Port {info['port']} may not be accessible")
        
        print(f"\n{Colors.CYAN}[*] Monitoring Status: {'Active' if self.session_manager.running else 'Stopped'}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def _select_session(self, sessions: List[Session]) -> Optional[Session]:
        """Helper to select a session from list"""
        print(f"\n{Colors.CYAN}Select a session:{Colors.RESET}")
        
        for i, session in enumerate(sessions, 1):
            session_key = f"{session.framework}_{session.id}"
            user_host = f"{session.username}@{session.hostname}"
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {session_key} - {user_host} ({session.target_ip})")
        
        try:
            choice = int(input(f"\n{Colors.CYAN}Enter session number: {Colors.RESET}"))
            if 1 <= choice <= len(sessions):
                return sessions[choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                return None
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return None
    
    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as time ago"""
        now = datetime.now()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s ago"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}m ago"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() / 3600)}h ago"
        else:
            return f"{int(diff.total_seconds() / 86400)}d ago"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def run(self):
        """Run the session menu"""
        try:
            self.display()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup when exiting menu"""
        # Stop monitoring when exiting
        self.session_manager.stop_monitoring()


def main():
    """Main function for testing"""
    menu = SessionMenu()
    menu.run()


if __name__ == "__main__":
    main()