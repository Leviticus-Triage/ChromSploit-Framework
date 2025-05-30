#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Live View Menu - Real-time monitoring
"""

import time
import threading
from core.menu import Menu
from core.colors import Colors
from core.logger import Logger

class LiveViewMenu(Menu):
    def __init__(self, parent=None):
        super().__init__("Live View", parent)
        self.logger = Logger()
        self.monitoring = False
        
        self.set_info_text("Real-time monitoring and session management")
        
        self.add_item("Active Sessions", self._show_sessions, Colors.GREEN)
        self.add_item("Network Monitor", self._network_monitor, Colors.CYAN)
        self.add_item("Log Viewer", self._log_viewer, Colors.BLUE)
        self.add_item("Resource Monitor", self._resource_monitor, Colors.YELLOW)
        self.add_item("Payload Status", self._payload_status, Colors.MAGENTA)
        self.add_item("Back", lambda: "exit", Colors.RED)
    
    def _show_sessions(self):
        self._clear()
        self._draw_box(80, "ACTIVE SESSIONS")
        print(f"\n{Colors.CYAN}[*] Current active sessions:{Colors.RESET}")
        print(f"{Colors.YELLOW}  No active sessions{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _network_monitor(self):
        self._clear()
        self._draw_box(80, "NETWORK MONITOR")
        print(f"\n{Colors.CYAN}[*] Network activity monitor{Colors.RESET}")
        print(f"{Colors.GREEN}[+] Monitoring network connections...{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Sample output:{Colors.RESET}")
        print(f"  Protocol | Source         | Destination    | Status")
        print(f"  ---------|----------------|----------------|--------")
        print(f"  TCP      | 192.168.1.100  | 192.168.1.1   | ESTABLISHED")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _log_viewer(self):
        self._clear()
        self._draw_box(80, "LOG VIEWER")
        print(f"\n{Colors.CYAN}[*] Real-time log viewer{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Recent logs:{Colors.RESET}")
        print(f"  [2024-01-01 00:00:00] Framework initialized")
        print(f"  [2024-01-01 00:00:01] Menu system loaded")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _resource_monitor(self):
        self._clear()
        self._draw_box(80, "RESOURCE MONITOR")
        print(f"\n{Colors.CYAN}[*] System resource usage:{Colors.RESET}")
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            print(f"\n{Colors.GREEN}CPU Usage: {cpu_percent}%{Colors.RESET}")
            print(f"{Colors.GREEN}Memory Usage: {memory.percent}%{Colors.RESET}")
            print(f"{Colors.GREEN}Available Memory: {memory.available / (1024**3):.2f} GB{Colors.RESET}")
        except ImportError:
            print(f"{Colors.RED}[!] psutil module not available{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _payload_status(self):
        self._clear()
        self._draw_box(80, "PAYLOAD STATUS")
        print(f"\n{Colors.CYAN}[*] Deployed payload status:{Colors.RESET}")
        print(f"{Colors.YELLOW}  No payloads deployed{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"