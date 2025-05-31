#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Ngrok Manager - Advanced ngrok tunnel management with CVE integration
"""

import json
import requests
import subprocess
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from core.enhanced_logger import get_logger
from core.error_handler import handle_errors, ErrorContext
from core.colors import Colors

@dataclass
class NgrokTunnel:
    """Represents an active ngrok tunnel"""
    name: str
    public_url: str
    local_url: str
    protocol: str
    port: int
    region: str
    tunnel_type: str
    created_at: datetime
    connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'public_url': self.public_url,
            'local_url': self.local_url,
            'protocol': self.protocol,
            'port': self.port,
            'region': self.region,
            'tunnel_type': self.tunnel_type,
            'created_at': self.created_at.isoformat(),
            'connections': self.connections
        }

class NgrokManager:
    """Advanced ngrok tunnel management"""
    
    def __init__(self):
        self.logger = get_logger()
        self.ngrok_api_url = "http://127.0.0.1:4040/api"
        self.active_tunnels: Dict[str, NgrokTunnel] = {}
        self.auto_sync_enabled = False
        self.sync_thread = None
        self.external_target_mode = False
        self.registered_cve_handlers = {}
        
    @handle_errors(context="NgrokManager.get_tunnels")
    def get_active_tunnels(self) -> List[NgrokTunnel]:
        """
        Fetch all active ngrok tunnels from local API
        
        Returns:
            List of active NgrokTunnel objects
        """
        try:
            response = requests.get(f"{self.ngrok_api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = []
                
                for tunnel_data in data.get('tunnels', []):
                    tunnel = NgrokTunnel(
                        name=tunnel_data.get('name', ''),
                        public_url=tunnel_data.get('public_url', ''),
                        local_url=f"http://127.0.0.1:{tunnel_data.get('config', {}).get('addr', '').split(':')[-1]}",
                        protocol=tunnel_data.get('proto', ''),
                        port=int(tunnel_data.get('config', {}).get('addr', ':0').split(':')[-1]),
                        region=tunnel_data.get('config', {}).get('region', 'us'),
                        tunnel_type=tunnel_data.get('config', {}).get('inspect', 'http'),
                        created_at=datetime.now(),  # ngrok doesn't provide creation time in API
                        connections=tunnel_data.get('metrics', {}).get('conns', {}).get('count', 0)
                    )
                    tunnels.append(tunnel)
                    self.active_tunnels[tunnel.name] = tunnel
                
                self.logger.info(f"Found {len(tunnels)} active ngrok tunnels")
                return tunnels
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Could not connect to ngrok API: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching tunnels: {str(e)}")
            return []
        
        return []
    
    @handle_errors(context="NgrokManager.start_tunnel")
    def start_tunnel(self, port: int, protocol: str = "http", name: Optional[str] = None, 
                    region: str = "us", subdomain: Optional[str] = None) -> Optional[NgrokTunnel]:
        """
        Start a new ngrok tunnel
        
        Args:
            port: Local port to expose
            protocol: Protocol (http, tcp, etc.)
            name: Tunnel name
            region: Ngrok region
            subdomain: Custom subdomain (Pro feature)
            
        Returns:
            NgrokTunnel object if successful
        """
        tunnel_config = {
            "addr": f"127.0.0.1:{port}",
            "proto": protocol,
            "name": name or f"{protocol}_{port}",
            "bind_tls": True
        }
        
        if region:
            tunnel_config["region"] = region
        if subdomain:
            tunnel_config["subdomain"] = subdomain
        
        try:
            response = requests.post(
                f"{self.ngrok_api_url}/tunnels",
                json=tunnel_config,
                timeout=10
            )
            
            if response.status_code == 201:
                tunnel_data = response.json()
                tunnel = NgrokTunnel(
                    name=tunnel_data.get('name', ''),
                    public_url=tunnel_data.get('public_url', ''),
                    local_url=f"http://127.0.0.1:{port}",
                    protocol=protocol,
                    port=port,
                    region=region,
                    tunnel_type=protocol,
                    created_at=datetime.now()
                )
                
                self.active_tunnels[tunnel.name] = tunnel
                self.logger.info(f"Started tunnel: {tunnel.public_url} -> localhost:{port}")
                
                # Auto-sync CVE parameters if external target mode is enabled
                if self.external_target_mode:
                    self._sync_tunnel_to_cve_configs(tunnel)
                
                return tunnel
            else:
                self.logger.error(f"Failed to start tunnel: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error starting tunnel: {str(e)}")
            return None
    
    def create_tunnel(self, port: int, protocol: str = "http", name: Optional[str] = None, 
                     region: str = "us", subdomain: Optional[str] = None) -> Optional[NgrokTunnel]:
        """
        Create a new ngrok tunnel (alias for start_tunnel for backward compatibility)
        
        Args:
            port: Local port to expose
            protocol: Protocol (http, tcp, etc.)
            name: Tunnel name
            region: Ngrok region
            subdomain: Custom subdomain (Pro feature)
            
        Returns:
            NgrokTunnel object if successful
        """
        return self.start_tunnel(port, protocol, name, region, subdomain)
    
    @handle_errors(context="NgrokManager.stop_tunnel")
    def stop_tunnel(self, tunnel_name: str) -> bool:
        """
        Stop a specific ngrok tunnel
        
        Args:
            tunnel_name: Name of tunnel to stop
            
        Returns:
            True if successful
        """
        try:
            response = requests.delete(f"{self.ngrok_api_url}/tunnels/{tunnel_name}")
            if response.status_code == 204:
                if tunnel_name in self.active_tunnels:
                    del self.active_tunnels[tunnel_name]
                self.logger.info(f"Stopped tunnel: {tunnel_name}")
                return True
            else:
                self.logger.error(f"Failed to stop tunnel {tunnel_name}: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error stopping tunnel: {str(e)}")
            return False
    
    def enable_external_target_mode(self):
        """Enable external target exploitation mode"""
        self.external_target_mode = True
        self.logger.info("External target exploitation mode enabled")
        
        # Sync existing tunnels
        tunnels = self.get_active_tunnels()
        for tunnel in tunnels:
            self._sync_tunnel_to_cve_configs(tunnel)
    
    def disable_external_target_mode(self):
        """Disable external target exploitation mode"""
        self.external_target_mode = False
        self.logger.info("External target exploitation mode disabled")
    
    def register_cve_handler(self, cve_id: str, config_callback: callable):
        """
        Register a CVE exploit handler for automatic parameter updates
        
        Args:
            cve_id: CVE identifier (e.g., 'CVE-2025-4664')
            config_callback: Function to call with tunnel data
        """
        self.registered_cve_handlers[cve_id] = config_callback
        self.logger.debug(f"Registered CVE handler for {cve_id}")
    
    def _sync_tunnel_to_cve_configs(self, tunnel: NgrokTunnel):
        """
        Sync tunnel data to all registered CVE exploit configurations
        
        Args:
            tunnel: NgrokTunnel to sync
        """
        tunnel_data = {
            'public_url': tunnel.public_url,
            'local_url': tunnel.local_url,
            'port': tunnel.port,
            'protocol': tunnel.protocol,
            'region': tunnel.region
        }
        
        self.logger.info(f"Syncing tunnel {tunnel.name} to CVE configurations...")
        
        for cve_id, callback in self.registered_cve_handlers.items():
            try:
                callback(tunnel_data)
                self.logger.debug(f"Updated {cve_id} configuration with tunnel data")
            except Exception as e:
                self.logger.error(f"Failed to update {cve_id} configuration: {str(e)}")
        
        # Also update simulation engine if available
        self._update_simulation_engine(tunnel_data)
    
    def _update_simulation_engine(self, tunnel_data: Dict[str, Any]):
        """Update simulation engine with tunnel data"""
        try:
            from core.simulation import get_simulation_engine
            sim_engine = get_simulation_engine()
            
            # Update network configuration for external targets
            if hasattr(sim_engine, 'network'):
                sim_engine.network.external_tunnel = tunnel_data
                
            self.logger.debug("Updated simulation engine with tunnel data")
        except ImportError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to update simulation engine: {str(e)}")
    
    def start_auto_sync(self, interval: int = 10):
        """
        Start automatic tunnel synchronization
        
        Args:
            interval: Sync interval in seconds
        """
        if self.auto_sync_enabled:
            return
        
        self.auto_sync_enabled = True
        
        def sync_worker():
            while self.auto_sync_enabled:
                try:
                    tunnels = self.get_active_tunnels()
                    if self.external_target_mode:
                        for tunnel in tunnels:
                            self._sync_tunnel_to_cve_configs(tunnel)
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in auto-sync: {str(e)}")
                    time.sleep(interval)
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
        self.logger.info(f"Started auto-sync every {interval} seconds")
    
    def stop_auto_sync(self):
        """Stop automatic tunnel synchronization"""
        self.auto_sync_enabled = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
        self.logger.info("Stopped auto-sync")
    
    def get_tunnel_stats(self) -> Dict[str, Any]:
        """Get statistics about active tunnels"""
        tunnels = self.get_active_tunnels()
        
        stats = {
            'total_tunnels': len(tunnels),
            'protocols': {},
            'regions': {},
            'total_connections': 0,
            'external_mode': self.external_target_mode,
            'auto_sync': self.auto_sync_enabled
        }
        
        for tunnel in tunnels:
            # Count protocols
            stats['protocols'][tunnel.protocol] = stats['protocols'].get(tunnel.protocol, 0) + 1
            
            # Count regions
            stats['regions'][tunnel.region] = stats['regions'].get(tunnel.region, 0) + 1
            
            # Sum connections
            stats['total_connections'] += tunnel.connections
        
        return stats
    
    def export_tunnel_config(self, filepath: str) -> bool:
        """
        Export current tunnel configuration to file
        
        Args:
            filepath: Path to save configuration
            
        Returns:
            True if successful
        """
        try:
            tunnels = self.get_active_tunnels()
            config_data = {
                'exported_at': datetime.now().isoformat(),
                'external_target_mode': self.external_target_mode,
                'auto_sync_enabled': self.auto_sync_enabled,
                'tunnels': [tunnel.to_dict() for tunnel in tunnels],
                'stats': self.get_tunnel_stats()
            }
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Exported tunnel configuration to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {str(e)}")
            return False

# Global instance
_ngrok_manager = None

def get_ngrok_manager() -> NgrokManager:
    """Get or create ngrok manager instance"""
    global _ngrok_manager
    if _ngrok_manager is None:
        _ngrok_manager = NgrokManager()
    return _ngrok_manager

# CVE Integration Helpers
def register_cve_integration(cve_id: str, exploit_config_updater: callable):
    """
    Register a CVE exploit for automatic ngrok parameter updates
    
    Args:
        cve_id: CVE identifier
        exploit_config_updater: Function that accepts tunnel_data dict
    """
    manager = get_ngrok_manager()
    manager.register_cve_handler(cve_id, exploit_config_updater)

def update_cve_2025_4664_config(tunnel_data: Dict[str, Any]):
    """Update CVE-2025-4664 exploit configuration with tunnel data"""
    # This would be called automatically when external target mode is enabled
    pass

def update_cve_2025_2783_config(tunnel_data: Dict[str, Any]):
    """Update CVE-2025-2783 exploit configuration with tunnel data"""
    # This would be called automatically when external target mode is enabled
    pass

def update_cve_2025_2857_config(tunnel_data: Dict[str, Any]):
    """Update CVE-2025-2857 exploit configuration with tunnel data"""
    # This would be called automatically when external target mode is enabled
    pass

def update_cve_2025_30397_config(tunnel_data: Dict[str, Any]):
    """Update CVE-2025-30397 exploit configuration with tunnel data"""
    # This would be called automatically when external target mode is enabled
    pass

# Auto-register CVE handlers
def initialize_cve_integrations():
    """Initialize all CVE integrations"""
    register_cve_integration('CVE-2025-4664', update_cve_2025_4664_config)
    register_cve_integration('CVE-2025-2783', update_cve_2025_2783_config)
    register_cve_integration('CVE-2025-2857', update_cve_2025_2857_config)
    register_cve_integration('CVE-2025-30397', update_cve_2025_30397_config)

# Initialize on import
initialize_cve_integrations()