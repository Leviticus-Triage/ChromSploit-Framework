#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Enhanced Ngrok Menu with CVE Integration
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.ngrok_manager import get_ngrok_manager, NgrokTunnel
from core.error_handler import handle_errors, ErrorContext

class EnhancedNgrokMenu(EnhancedMenu):
    """Enhanced Ngrok menu with CVE integration"""
    
    def __init__(self, parent=None):
        super().__init__("Ngrok Integration & CVE Auto-Config", parent)
        self.logger = get_logger()
        self.ngrok_manager = get_ngrok_manager()
        
        self.set_info_text("Advanced ngrok tunnel management with automatic CVE exploit configuration")
        
        # Add menu items
        self.add_enhanced_item(
            "View Active Tunnels", 
            self._view_active_tunnels, 
            Colors.GREEN,
            "v",
            "Display all active ngrok tunnels with details"
        )
        
        self.add_enhanced_item(
            "Start New Tunnel", 
            self._start_new_tunnel, 
            Colors.CYAN,
            "s",
            "Create a new ngrok tunnel"
        )
        
        self.add_enhanced_item(
            "External Target Mode", 
            self._toggle_external_mode, 
            Colors.YELLOW,
            "e",
            "Enable/disable automatic CVE parameter synchronization"
        )
        
        self.add_enhanced_item(
            "Auto-Sync Settings", 
            self._auto_sync_settings, 
            Colors.BLUE,
            "a",
            "Configure automatic tunnel synchronization"
        )
        
        self.add_enhanced_item(
            "Tunnel Statistics", 
            self._show_statistics, 
            Colors.MAGENTA,
            "t",
            "View tunnel usage statistics"
        )
        
        self.add_enhanced_item(
            "CVE Integration Status", 
            self._show_cve_status, 
            Colors.WHITE,
            "c",
            "Check CVE exploit integration status"
        )
        
        self.add_enhanced_item(
            "Export Configuration", 
            self._export_config, 
            Colors.BRIGHT_BLUE,
            "x",
            "Export tunnel configuration to file"
        )
        
        self.add_enhanced_item(
            "Stop All Tunnels", 
            self._stop_all_tunnels, 
            Colors.RED,
            "q",
            "Stop all active ngrok tunnels",
            dangerous=True
        )
        
        self.add_enhanced_item(
            "Back", 
            lambda: "exit", 
            Colors.RED,
            "b"
        )
        
        # Check initial status
        self._check_ngrok_status()
    
    def _check_ngrok_status(self):
        """Check ngrok daemon status and update notifications"""
        try:
            tunnels = self.ngrok_manager.get_active_tunnels()
            if tunnels:
                self.add_notification(f"{len(tunnels)} active tunnel(s) detected", "success")
            else:
                self.add_notification("No active tunnels found", "info")
                
            if self.ngrok_manager.external_target_mode:
                self.add_notification("External target mode ENABLED", "warning")
                
        except Exception as e:
            self.add_notification("Ngrok daemon not running", "error")
    
    def _view_active_tunnels(self):
        """View all active tunnels"""
        self._clear()
        self._draw_box(80, "ACTIVE NGROK TUNNELS")
        
        tunnels = self.ngrok_manager.get_active_tunnels()
        
        if not tunnels:
            print(f"\n{Colors.YELLOW}[!] No active tunnels found{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Make sure ngrok daemon is running{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Start ngrok with: ngrok http 8080{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}[+] Found {len(tunnels)} active tunnel(s):{Colors.RESET}")
            
            for i, tunnel in enumerate(tunnels, 1):
                print(f"\n{Colors.CYAN}Tunnel #{i}:{Colors.RESET}")
                print(f"  {Colors.YELLOW}Name:{Colors.RESET} {tunnel.name}")
                print(f"  {Colors.YELLOW}Public URL:{Colors.RESET} {Colors.GREEN}{tunnel.public_url}{Colors.RESET}")
                print(f"  {Colors.YELLOW}Local URL:{Colors.RESET} {tunnel.local_url}")
                print(f"  {Colors.YELLOW}Protocol:{Colors.RESET} {tunnel.protocol}")
                print(f"  {Colors.YELLOW}Port:{Colors.RESET} {tunnel.port}")
                print(f"  {Colors.YELLOW}Region:{Colors.RESET} {tunnel.region}")
                
                if tunnel.connections > 0:
                    print(f"  {Colors.YELLOW}Connections:{Colors.RESET} {tunnel.connections}")
        
        # Show external mode status
        if self.ngrok_manager.external_target_mode:
            print(f"\n{Colors.BRIGHT_YELLOW}🎯 External Target Mode: ENABLED{Colors.RESET}")
            print(f"{Colors.CYAN}[*] CVE exploits will automatically use tunnel URLs{Colors.RESET}")
        else:
            print(f"\n{Colors.DARK_GRAY}External Target Mode: Disabled{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _start_new_tunnel(self):
        """Start a new ngrok tunnel"""
        self._clear()
        self._draw_box(80, "START NEW TUNNEL")
        
        print(f"\n{Colors.CYAN}[*] Configure new ngrok tunnel{Colors.RESET}")
        
        # Get port
        while True:
            try:
                port_input = input(f"\n{Colors.YELLOW}Local port to expose: {Colors.RESET}")
                port = int(port_input)
                if 1 <= port <= 65535:
                    break
                else:
                    print(f"{Colors.RED}[!] Port must be between 1-65535{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}[!] Please enter a valid port number{Colors.RESET}")
        
        # Get protocol
        print(f"\n{Colors.CYAN}Available protocols:{Colors.RESET}")
        protocols = ["http", "tcp", "tls"]
        for i, proto in enumerate(protocols, 1):
            print(f"  {i}. {proto}")
        
        try:
            proto_choice = int(input(f"\n{Colors.YELLOW}Select protocol (1-{len(protocols)}): {Colors.RESET}"))
            protocol = protocols[proto_choice - 1]
        except (ValueError, IndexError):
            protocol = "http"
            print(f"{Colors.YELLOW}[*] Using default protocol: http{Colors.RESET}")
        
        # Get optional parameters
        name = input(f"\n{Colors.YELLOW}Tunnel name (optional): {Colors.RESET}")
        subdomain = input(f"{Colors.YELLOW}Custom subdomain (Pro feature, optional): {Colors.RESET}")
        
        # Get region
        regions = ["us", "eu", "ap", "au", "sa", "jp", "in"]
        print(f"\n{Colors.CYAN}Available regions: {', '.join(regions)}{Colors.RESET}")
        region = input(f"{Colors.YELLOW}Region (default: us): {Colors.RESET}") or "us"
        
        print(f"\n{Colors.CYAN}[*] Starting tunnel...{Colors.RESET}")
        
        # Start the tunnel
        tunnel = self.ngrok_manager.start_tunnel(
            port=port,
            protocol=protocol,
            name=name if name else None,
            region=region,
            subdomain=subdomain if subdomain else None
        )
        
        if tunnel:
            print(f"\n{Colors.GREEN}[+] Tunnel started successfully!{Colors.RESET}")
            print(f"{Colors.CYAN}Public URL: {Colors.GREEN}{tunnel.public_url}{Colors.RESET}")
            print(f"{Colors.CYAN}Local URL: {tunnel.local_url}{Colors.RESET}")
            
            if self.ngrok_manager.external_target_mode:
                print(f"\n{Colors.BRIGHT_YELLOW}🎯 External Target Mode Active{Colors.RESET}")
                print(f"{Colors.CYAN}[*] CVE exploits updated with tunnel URL{Colors.RESET}")
                
            self.add_notification("New tunnel created", "success")
        else:
            print(f"\n{Colors.RED}[!] Failed to start tunnel{Colors.RESET}")
            self.add_notification("Tunnel creation failed", "error")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _toggle_external_mode(self):
        """Toggle external target exploitation mode"""
        self._clear()
        self._draw_box(80, "EXTERNAL TARGET MODE")
        
        current_status = "ENABLED" if self.ngrok_manager.external_target_mode else "DISABLED"
        status_color = Colors.GREEN if self.ngrok_manager.external_target_mode else Colors.RED
        
        print(f"\n{Colors.CYAN}Current Status: {status_color}{current_status}{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}External Target Mode:{Colors.RESET}")
        print("• Automatically configures CVE exploits with ngrok tunnel URLs")
        print("• Enables remote exploitation through tunnels")
        print("• Synchronizes tunnel data to all PoC exploit functions")
        print("• Updates simulation engine with external targets")
        
        if self.ngrok_manager.external_target_mode:
            print(f"\n{Colors.RED}⚠️  Warning: External target mode is currently ACTIVE{Colors.RESET}")
            choice = input(f"\n{Colors.YELLOW}Disable external target mode? (y/N): {Colors.RESET}")
            
            if choice.lower() == 'y':
                self.ngrok_manager.disable_external_target_mode()
                print(f"\n{Colors.GREEN}[+] External target mode disabled{Colors.RESET}")
                self.add_notification("External target mode disabled", "info")
            else:
                print(f"\n{Colors.CYAN}[*] External target mode remains enabled{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}External target mode is currently disabled{Colors.RESET}")
            choice = input(f"\n{Colors.YELLOW}Enable external target mode? (y/N): {Colors.RESET}")
            
            if choice.lower() == 'y':
                self.ngrok_manager.enable_external_target_mode()
                print(f"\n{Colors.GREEN}[+] External target mode enabled{Colors.RESET}")
                print(f"{Colors.CYAN}[*] All CVE exploits will now use tunnel URLs{Colors.RESET}")
                self.add_notification("External target mode enabled", "warning")
                
                # Show affected CVEs
                cve_list = list(self.ngrok_manager.registered_cve_handlers.keys())
                if cve_list:
                    print(f"\n{Colors.CYAN}Affected CVE exploits:{Colors.RESET}")
                    for cve in cve_list:
                        print(f"  • {cve}")
            else:
                print(f"\n{Colors.CYAN}[*] External target mode remains disabled{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _auto_sync_settings(self):
        """Configure auto-sync settings"""
        self._clear()
        self._draw_box(80, "AUTO-SYNC SETTINGS")
        
        sync_status = "ENABLED" if self.ngrok_manager.auto_sync_enabled else "DISABLED"
        status_color = Colors.GREEN if self.ngrok_manager.auto_sync_enabled else Colors.RED
        
        print(f"\n{Colors.CYAN}Auto-Sync Status: {status_color}{sync_status}{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Auto-Sync Features:{Colors.RESET}")
        print("• Automatically detects new tunnels")
        print("• Synchronizes tunnel data to CVE exploits")
        print("• Updates configurations in real-time")
        print("• Monitors tunnel status changes")
        
        print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
        if self.ngrok_manager.auto_sync_enabled:
            print("  1. Stop auto-sync")
            print("  2. Change sync interval")
        else:
            print("  1. Start auto-sync")
        print("  3. Back")
        
        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.RESET}")
        
        if choice == "1":
            if self.ngrok_manager.auto_sync_enabled:
                self.ngrok_manager.stop_auto_sync()
                print(f"\n{Colors.GREEN}[+] Auto-sync stopped{Colors.RESET}")
                self.add_notification("Auto-sync disabled", "info")
            else:
                try:
                    interval = int(input(f"\n{Colors.YELLOW}Sync interval (seconds, default 10): {Colors.RESET}") or "10")
                    self.ngrok_manager.start_auto_sync(interval)
                    print(f"\n{Colors.GREEN}[+] Auto-sync started (interval: {interval}s){Colors.RESET}")
                    self.add_notification("Auto-sync enabled", "success")
                except ValueError:
                    print(f"{Colors.RED}[!] Invalid interval{Colors.RESET}")
        
        elif choice == "2" and self.ngrok_manager.auto_sync_enabled:
            try:
                interval = int(input(f"\n{Colors.YELLOW}New sync interval (seconds): {Colors.RESET}"))
                self.ngrok_manager.stop_auto_sync()
                time.sleep(0.5)
                self.ngrok_manager.start_auto_sync(interval)
                print(f"\n{Colors.GREEN}[+] Sync interval updated to {interval}s{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}[!] Invalid interval{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_statistics(self):
        """Show tunnel statistics"""
        self._clear()
        self._draw_box(80, "TUNNEL STATISTICS")
        
        stats = self.ngrok_manager.get_tunnel_stats()
        
        print(f"\n{Colors.CYAN}Tunnel Overview:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Total Tunnels:{Colors.RESET} {stats['total_tunnels']}")
        print(f"  {Colors.YELLOW}Total Connections:{Colors.RESET} {stats['total_connections']}")
        print(f"  {Colors.YELLOW}External Mode:{Colors.RESET} {'✓' if stats['external_mode'] else '✗'}")
        print(f"  {Colors.YELLOW}Auto-Sync:{Colors.RESET} {'✓' if stats['auto_sync'] else '✗'}")
        
        if stats['protocols']:
            print(f"\n{Colors.CYAN}Protocols:{Colors.RESET}")
            for protocol, count in stats['protocols'].items():
                print(f"  {Colors.YELLOW}{protocol}:{Colors.RESET} {count}")
        
        if stats['regions']:
            print(f"\n{Colors.CYAN}Regions:{Colors.RESET}")
            for region, count in stats['regions'].items():
                print(f"  {Colors.YELLOW}{region}:{Colors.RESET} {count}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_cve_status(self):
        """Show CVE integration status"""
        self._clear()
        self._draw_box(80, "CVE INTEGRATION STATUS")
        
        registered_cves = list(self.ngrok_manager.registered_cve_handlers.keys())
        
        print(f"\n{Colors.CYAN}Registered CVE Handlers:{Colors.RESET}")
        if registered_cves:
            for cve in registered_cves:
                status_icon = "🟢" if self.ngrok_manager.external_target_mode else "🔴"
                print(f"  {status_icon} {Colors.YELLOW}{cve}{Colors.RESET}")
        else:
            print(f"  {Colors.RED}No CVE handlers registered{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Integration Status:{Colors.RESET}")
        print(f"  {Colors.YELLOW}External Target Mode:{Colors.RESET} {'ACTIVE' if self.ngrok_manager.external_target_mode else 'INACTIVE'}")
        print(f"  {Colors.YELLOW}Auto-Sync:{Colors.RESET} {'RUNNING' if self.ngrok_manager.auto_sync_enabled else 'STOPPED'}")
        
        tunnels = self.ngrok_manager.get_active_tunnels()
        if tunnels and self.ngrok_manager.external_target_mode:
            print(f"\n{Colors.GREEN}[+] CVE exploits are configured with tunnel URLs{Colors.RESET}")
        elif tunnels and not self.ngrok_manager.external_target_mode:
            print(f"\n{Colors.YELLOW}[!] Tunnels active but external mode disabled{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[!] No active tunnels for CVE integration{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _export_config(self):
        """Export tunnel configuration"""
        self._clear()
        self._draw_box(80, "EXPORT CONFIGURATION")
        
        print(f"\n{Colors.CYAN}[*] Export tunnel configuration{Colors.RESET}")
        
        # Default filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_name = f"ngrok_config_{timestamp}.json"
        
        filename = input(f"\n{Colors.YELLOW}Filename (default: {default_name}): {Colors.RESET}")
        if not filename:
            filename = default_name
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = Path("reports") / filename
        
        if self.ngrok_manager.export_tunnel_config(str(filepath)):
            print(f"\n{Colors.GREEN}[+] Configuration exported: {filepath}{Colors.RESET}")
            self.add_notification("Configuration exported", "success")
        else:
            print(f"\n{Colors.RED}[!] Export failed{Colors.RESET}")
            self.add_notification("Export failed", "error")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _stop_all_tunnels(self):
        """Stop all active tunnels"""
        self._clear()
        self._draw_box(80, "STOP ALL TUNNELS")
        
        tunnels = self.ngrok_manager.get_active_tunnels()
        
        if not tunnels:
            print(f"\n{Colors.YELLOW}[!] No active tunnels to stop{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}⚠️  Warning: This will stop ALL {len(tunnels)} active tunnel(s){Colors.RESET}")
            
            for tunnel in tunnels:
                print(f"  • {tunnel.name} ({tunnel.public_url})")
            
            confirm = input(f"\n{Colors.YELLOW}Are you sure? (type 'yes' to confirm): {Colors.RESET}")
            
            if confirm.lower() == 'yes':
                stopped_count = 0
                for tunnel in tunnels:
                    if self.ngrok_manager.stop_tunnel(tunnel.name):
                        stopped_count += 1
                
                print(f"\n{Colors.GREEN}[+] Stopped {stopped_count}/{len(tunnels)} tunnels{Colors.RESET}")
                self.add_notification(f"Stopped {stopped_count} tunnels", "success")
            else:
                print(f"\n{Colors.CYAN}[*] Operation cancelled{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"