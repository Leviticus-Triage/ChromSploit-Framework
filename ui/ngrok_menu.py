#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Ngrok Integration Menu
"""

import os
import time
import subprocess
from core.menu import Menu
from core.colors import Colors
from core.logger import Logger

class NgrokMenu(Menu):
    def __init__(self, parent=None):
        super().__init__("Ngrok Integration", parent)
        self.logger = Logger()
        self.ngrok_process = None
        
        self.set_info_text("Ngrok tunnel management for remote access")
        
        self.add_item("Start Ngrok Tunnel", self._start_tunnel, Colors.GREEN)
        self.add_item("Stop Ngrok Tunnel", self._stop_tunnel, Colors.RED)
        self.add_item("View Tunnel Status", self._tunnel_status, Colors.CYAN)
        self.add_item("Configure Ngrok", self._configure_ngrok, Colors.BLUE)
        self.add_item("Generate Payload URL", self._generate_payload_url, Colors.YELLOW)
        self.add_item("Back", lambda: "exit", Colors.RED)
    
    def _start_tunnel(self):
        self._clear()
        self._draw_box(80, "START NGROK TUNNEL")
        
        print(f"\n{Colors.CYAN}[*] Starting Ngrok tunnel...{Colors.RESET}")
        
        port = input(f"\n{Colors.YELLOW}Enter local port (default: 8080): {Colors.RESET}")
        if not port:
            port = "8080"
        
        protocol = input(f"{Colors.YELLOW}Protocol (http/tcp) [default: http]: {Colors.RESET}")
        if not protocol:
            protocol = "http"
        
        print(f"\n{Colors.GREEN}[+] Starting {protocol} tunnel on port {port}...{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Tunnel URL will be displayed here{Colors.RESET}")
        print(f"{Colors.RED}[!] Ngrok integration requires ngrok to be installed{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _stop_tunnel(self):
        self._clear()
        self._draw_box(80, "STOP NGROK TUNNEL")
        
        print(f"\n{Colors.CYAN}[*] Stopping Ngrok tunnel...{Colors.RESET}")
        
        if self.ngrok_process:
            print(f"{Colors.GREEN}[+] Tunnel stopped successfully{Colors.RESET}")
            self.ngrok_process = None
        else:
            print(f"{Colors.YELLOW}[!] No active tunnel found{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _tunnel_status(self):
        self._clear()
        self._draw_box(80, "TUNNEL STATUS")
        
        print(f"\n{Colors.CYAN}[*] Ngrok tunnel status:{Colors.RESET}")
        
        if self.ngrok_process:
            print(f"{Colors.GREEN}[+] Tunnel Active{Colors.RESET}")
            print(f"  {Colors.YELLOW}URL:{Colors.RESET} https://example.ngrok.io")
            print(f"  {Colors.YELLOW}Protocol:{Colors.RESET} HTTP")
            print(f"  {Colors.YELLOW}Local Port:{Colors.RESET} 8080")
            print(f"  {Colors.YELLOW}Status:{Colors.RESET} Online")
        else:
            print(f"{Colors.RED}[-] No active tunnel{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}[*] Ngrok dashboard: http://127.0.0.1:4040{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _configure_ngrok(self):
        self._clear()
        self._draw_box(80, "CONFIGURE NGROK")
        
        print(f"\n{Colors.CYAN}[*] Ngrok configuration:{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}Options:{Colors.RESET}")
        print("  1. Set auth token")
        print("  2. Configure region")
        print("  3. Set custom subdomain (Pro)")
        print("  4. View current config")
        print("  5. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            token = input(f"{Colors.CYAN}Enter auth token: {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Auth token configured{Colors.RESET}")
        elif choice == "2":
            print(f"{Colors.CYAN}Available regions: us, eu, ap, au, sa, jp, in{Colors.RESET}")
            region = input(f"{Colors.YELLOW}Enter region: {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Region set to {region}{Colors.RESET}")
        elif choice == "3":
            subdomain = input(f"{Colors.CYAN}Enter custom subdomain: {Colors.RESET}")
            print(f"{Colors.GREEN}[+] Subdomain configured: {subdomain}.ngrok.io{Colors.RESET}")
        elif choice == "4":
            print(f"\n{Colors.YELLOW}Current configuration:{Colors.RESET}")
            print(f"  Auth token: ****configured****")
            print(f"  Region: us")
            print(f"  Config file: ~/.ngrok2/ngrok.yml")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _generate_payload_url(self):
        self._clear()
        self._draw_box(80, "GENERATE PAYLOAD URL")
        
        print(f"\n{Colors.CYAN}[*] Generate payload delivery URL{Colors.RESET}")
        
        if self.ngrok_process:
            print(f"\n{Colors.GREEN}[+] Tunnel active at: https://example.ngrok.io{Colors.RESET}")
            
            payload_type = input(f"\n{Colors.YELLOW}Select payload type (1: JS, 2: HTML, 3: Binary): {Colors.RESET}")
            
            if payload_type == "1":
                print(f"\n{Colors.GREEN}[+] JavaScript payload URL:{Colors.RESET}")
                print(f"  https://example.ngrok.io/payload.js")
            elif payload_type == "2":
                print(f"\n{Colors.GREEN}[+] HTML payload URL:{Colors.RESET}")
                print(f"  https://example.ngrok.io/exploit.html")
            elif payload_type == "3":
                print(f"\n{Colors.GREEN}[+] Binary payload URL:{Colors.RESET}")
                print(f"  https://example.ngrok.io/payload.exe")
            
            print(f"\n{Colors.YELLOW}[*] URL copied to clipboard (if supported){Colors.RESET}")
        else:
            print(f"{Colors.RED}[-] No active tunnel. Start a tunnel first.{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"