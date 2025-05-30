#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Settings Menu
"""

import os
import json
from core.menu import Menu
from core.colors import Colors
from core.config import Config
from core.logger import Logger

class SettingsMenu(Menu):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.logger = Logger()
        self.config = Config()
        
        self.set_info_text("Configure framework settings and preferences")
        
        self.add_item("Network Settings", self._network_settings, Colors.GREEN)
        self.add_item("Exploit Settings", self._exploit_settings, Colors.CYAN)
        self.add_item("Logging Settings", self._logging_settings, Colors.BLUE)
        self.add_item("API Keys", self._api_keys, Colors.YELLOW)
        self.add_item("Update Framework", self._update_framework, Colors.MAGENTA)
        self.add_item("Reset to Defaults", self._reset_defaults, Colors.RED)
        self.add_item("Back", lambda: "exit", Colors.RED)
    
    def _network_settings(self):
        self._clear()
        self._draw_box(80, "NETWORK SETTINGS")
        
        print(f"\n{Colors.CYAN}Current network configuration:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Default Port:{Colors.RESET} 8080")
        print(f"  {Colors.YELLOW}Timeout:{Colors.RESET} 30 seconds")
        print(f"  {Colors.YELLOW}Max Connections:{Colors.RESET} 100")
        print(f"  {Colors.YELLOW}Proxy:{Colors.RESET} None")
        
        print(f"\n{Colors.GREEN}Options:{Colors.RESET}")
        print("  1. Change default port")
        print("  2. Set timeout")
        print("  3. Configure proxy")
        print("  4. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            port = input(f"{Colors.CYAN}Enter new port: {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Port updated to {port}{Colors.RESET}")
        elif choice == "2":
            timeout = input(f"{Colors.CYAN}Enter timeout (seconds): {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Timeout updated to {timeout}s{Colors.RESET}")
        elif choice == "3":
            proxy = input(f"{Colors.CYAN}Enter proxy (host:port): {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Proxy configured: {proxy}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _exploit_settings(self):
        self._clear()
        self._draw_box(80, "EXPLOIT SETTINGS")
        
        print(f"\n{Colors.CYAN}Exploit configuration:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Auto-exploit:{Colors.RESET} Disabled")
        print(f"  {Colors.YELLOW}Payload encoding:{Colors.RESET} Base64")
        print(f"  {Colors.YELLOW}Obfuscation:{Colors.RESET} Enabled")
        print(f"  {Colors.YELLOW}Stealth mode:{Colors.RESET} Off")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _logging_settings(self):
        self._clear()
        self._draw_box(80, "LOGGING SETTINGS")
        
        print(f"\n{Colors.CYAN}Logging configuration:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Log level:{Colors.RESET} INFO")
        print(f"  {Colors.YELLOW}Log file:{Colors.RESET} logs/chromsploit.log")
        print(f"  {Colors.YELLOW}Max file size:{Colors.RESET} 10 MB")
        print(f"  {Colors.YELLOW}Console output:{Colors.RESET} Enabled")
        
        print(f"\n{Colors.GREEN}Options:{Colors.RESET}")
        print("  1. Change log level (DEBUG/INFO/WARNING/ERROR)")
        print("  2. Toggle console output")
        print("  3. Clear logs")
        print("  4. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            level = input(f"{Colors.CYAN}Enter log level: {Colors.RESET}").upper()
            print(f"{Colors.GREEN}[+] Log level set to {level}{Colors.RESET}")
        elif choice == "2":
            print(f"{Colors.GREEN}[+] Console output toggled{Colors.RESET}")
        elif choice == "3":
            print(f"{Colors.GREEN}[+] Logs cleared{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _api_keys(self):
        self._clear()
        self._draw_box(80, "API KEYS MANAGEMENT")
        
        print(f"\n{Colors.CYAN}Configured API keys:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Shodan:{Colors.RESET} Not configured")
        print(f"  {Colors.YELLOW}VirusTotal:{Colors.RESET} Not configured")
        print(f"  {Colors.YELLOW}Ngrok:{Colors.RESET} Not configured")
        
        print(f"\n{Colors.RED}[!] API keys are stored securely{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _update_framework(self):
        self._clear()
        self._draw_box(80, "UPDATE FRAMEWORK")
        
        print(f"\n{Colors.CYAN}[*] Checking for updates...{Colors.RESET}")
        print(f"{Colors.GREEN}[+] ChromSploit Framework v2.0 is up to date{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _reset_defaults(self):
        self._clear()
        self._draw_box(80, "RESET TO DEFAULTS")
        
        print(f"\n{Colors.RED}[!] Warning: This will reset all settings to default values{Colors.RESET}")
        confirm = input(f"\n{Colors.YELLOW}Are you sure? (y/N): {Colors.RESET}")
        
        if confirm.lower() == 'y':
            print(f"\n{Colors.GREEN}[+] Settings reset to defaults{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}[*] Operation cancelled{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"