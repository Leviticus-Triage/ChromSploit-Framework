#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Simulation Mode for Safe Testing
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from core.colors import Colors
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors, ErrorContext
from core.reporting import ReportGenerator, ReportSeverity, get_report_generator

class SimulationMode(Enum):
 """Simulation mode types"""
 SAFE = "safe" # No actual operations
 REALISTIC = "realistic" # Realistic delays and outputs
 FAST = "fast" # Minimal delays
 DEMO = "demo" # Demo mode with explanations

@dataclass
class SimulationResult:
 """Result of a simulated operation"""
 success: bool
 message: str
 data: Dict[str, Any] = field(default_factory=dict)
 duration: float = 0.0
 timestamp: datetime = field(default_factory=datetime.now)
 
 def to_dict(self) -> Dict[str, Any]:
 """Convert to dictionary"""
 return {
 'success': self.success,
 'message': self.message,
 'data': self.data,
 'duration': self.duration,
 'timestamp': self.timestamp.isoformat()
 }

class SimulatedNetwork:
 """Simulate network operations"""
 
 def __init__(self, mode: SimulationMode = SimulationMode.SAFE):
 self.mode = mode
 self.logger = get_logger()
 self.active_connections = {}
 self.packet_loss_rate = 0.05
 self.latency_range = (50, 200) # ms
 
 @handle_errors(context="SimulatedNetwork.connect")
 def connect(self, host: str, port: int, timeout: int = 30) -> SimulationResult:
 """Simulate network connection"""
 start_time = time.time()
 
 self.logger.info(f"[SIMULATION] Connecting to {host}:{port}")
 
 # Simulate connection delay
 if self.mode != SimulationMode.FAST:
 delay = random.uniform(0.5, 2.0) if self.mode == SimulationMode.REALISTIC else 0.1
 time.sleep(delay)
 
 # Simulate connection success/failure
 if random.random() > 0.9 and self.mode == SimulationMode.REALISTIC:
 return SimulationResult(
 success=False,
 message=f"Connection to {host}:{port} failed",
 duration=time.time() - start_time
 )
 
 # Create connection ID
 conn_id = f"{host}:{port}_{int(time.time())}"
 self.active_connections[conn_id] = {
 'host': host,
 'port': port,
 'connected_at': datetime.now(),
 'bytes_sent': 0,
 'bytes_received': 0
 }
 
 return SimulationResult(
 success=True,
 message=f"Connected to {host}:{port}",
 data={'connection_id': conn_id},
 duration=time.time() - start_time
 )
 
 def send_data(self, conn_id: str, data: bytes) -> SimulationResult:
 """Simulate sending data"""
 if conn_id not in self.active_connections:
 return SimulationResult(
 success=False,
 message="Connection not found"
 )
 
 # Simulate latency
 if self.mode == SimulationMode.REALISTIC:
 latency = random.randint(*self.latency_range) / 1000
 time.sleep(latency)
 
 # Simulate packet loss
 if random.random() < self.packet_loss_rate and self.mode == SimulationMode.REALISTIC:
 return SimulationResult(
 success=False,
 message="Packet loss occurred"
 )
 
 self.active_connections[conn_id]['bytes_sent'] += len(data)
 
 return SimulationResult(
 success=True,
 message=f"Sent {len(data)} bytes",
 data={'bytes_sent': len(data)}
 )
 
 def scan_ports(self, host: str, ports: List[int]) -> SimulationResult:
 """Simulate port scanning"""
 self.logger.info(f"[SIMULATION] Scanning {len(ports)} ports on {host}")
 
 open_ports = []
 scan_results = {}
 
 for port in ports:
 if self.mode != SimulationMode.FAST:
 time.sleep(0.05 if self.mode == SimulationMode.REALISTIC else 0.01)
 
 # Simulate common open ports
 is_open = port in [22, 80, 443, 8080, 3306, 5432] and random.random() > 0.3
 scan_results[port] = 'open' if is_open else 'closed'
 
 if is_open:
 open_ports.append(port)
 
 return SimulationResult(
 success=True,
 message=f"Scan complete: {len(open_ports)} open ports found",
 data={
 'open_ports': open_ports,
 'scan_results': scan_results
 }
 )

class SimulatedExploit:
 """Simulate exploit execution"""
 
 def __init__(self, mode: SimulationMode = SimulationMode.SAFE):
 self.mode = mode
 self.logger = get_logger()
 self.exploit_stages = [
 "Initializing exploit framework",
 "Checking target vulnerability",
 "Preparing payload",
 "Establishing connection",
 "Sending exploit",
 "Waiting for response",
 "Verifying success"
 ]
 
 def execute(self, 
 exploit_name: str,
 target: str,
 options: Dict[str, Any] = None) -> SimulationResult:
 """Simulate exploit execution"""
 self.logger.info(f"[SIMULATION] Executing exploit: {exploit_name} against {target}")
 
 start_time = time.time()
 results = {
 'stages': [],
 'exploit_name': exploit_name,
 'target': target,
 'options': options or {}
 }
 
 # Execute stages
 for i, stage in enumerate(self.exploit_stages):
 stage_start = time.time()
 
 if self.mode == SimulationMode.DEMO:
 print(f"\n{Colors.CYAN}Stage {i+1}/{len(self.exploit_stages)}: {stage}{Colors.RESET}")
 
 # Simulate stage execution
 if self.mode != SimulationMode.FAST:
 delay = random.uniform(0.5, 2.0) if self.mode == SimulationMode.REALISTIC else 0.2
 time.sleep(delay)
 
 # Simulate stage success/failure
 if i == 2 and random.random() > 0.8 and self.mode == SimulationMode.REALISTIC:
 # Payload preparation failure
 results['stages'].append({
 'stage': stage,
 'success': False,
 'duration': time.time() - stage_start,
 'error': 'Payload generation failed'
 })
 
 return SimulationResult(
 success=False,
 message=f"Exploit failed at stage: {stage}",
 data=results,
 duration=time.time() - start_time
 )
 
 results['stages'].append({
 'stage': stage,
 'success': True,
 'duration': time.time() - stage_start
 })
 
 # Simulate session creation
 session_id = f"session_{int(time.time())}"
 results['session_id'] = session_id
 
 return SimulationResult(
 success=True,
 message=f"Exploit successful! Session created: {session_id}",
 data=results,
 duration=time.time() - start_time
 )

class SimulatedFileSystem:
 """Simulate file system operations"""
 
 def __init__(self, mode: SimulationMode = SimulationMode.SAFE):
 self.mode = mode
 self.logger = get_logger()
 self.virtual_fs = {
 '/': {
 'type': 'directory',
 'permissions': 'drwxr-xr-x',
 'size': 4096,
 'modified': datetime.now()
 },
 '/etc/passwd': {
 'type': 'file',
 'permissions': '-rw-r--r--',
 'size': 2048,
 'content': 'root:x:0:0:root:/root:/bin/bash\n',
 'modified': datetime.now() - timedelta(days=30)
 }
 }
 
 def read_file(self, path: str) -> SimulationResult:
 """Simulate file reading"""
 self.logger.info(f"[SIMULATION] Reading file: {path}")
 
 if self.mode != SimulationMode.FAST:
 time.sleep(0.1)
 
 if path in self.virtual_fs and self.virtual_fs[path]['type'] == 'file':
 return SimulationResult(
 success=True,
 message=f"Successfully read {path}",
 data={
 'content': self.virtual_fs[path].get('content', '[Simulated content]'),
 'size': self.virtual_fs[path]['size']
 }
 )
 
 return SimulationResult(
 success=False,
 message=f"File not found: {path}"
 )
 
 def write_file(self, path: str, content: str) -> SimulationResult:
 """Simulate file writing"""
 self.logger.info(f"[SIMULATION] Writing to file: {path}")
 
 if self.mode != SimulationMode.FAST:
 time.sleep(0.2)
 
 self.virtual_fs[path] = {
 'type': 'file',
 'permissions': '-rw-r--r--',
 'size': len(content),
 'content': content,
 'modified': datetime.now()
 }
 
 return SimulationResult(
 success=True,
 message=f"Successfully wrote {len(content)} bytes to {path}",
 data={'bytes_written': len(content)}
 )

class SimulationEngine:
 """Main simulation engine"""
 
 def __init__(self, mode: SimulationMode = SimulationMode.SAFE):
 self.mode = mode
 self.logger = get_logger()
 self.network = SimulatedNetwork(mode)
 self.exploit = SimulatedExploit(mode)
 self.filesystem = SimulatedFileSystem(mode)
 self.active_sessions = {}
 self.simulation_history = []
 self.auto_report = True # Enable automatic reporting
 self.report_generator = get_report_generator()
 
 self.logger.info(f"Simulation engine initialized in {mode.value} mode")
 
 def set_mode(self, mode: SimulationMode):
 """Change simulation mode"""
 self.mode = mode
 self.network.mode = mode
 self.exploit.mode = mode
 self.filesystem.mode = mode
 self.logger.info(f"Simulation mode changed to {mode.value}")
 
 def simulate_cve_exploit(self, cve_id: str, target: str, options: Dict[str, Any] = None) -> SimulationResult:
 """Simulate CVE exploit with ngrok integration"""
 self.logger.info(f"[SIMULATION] Simulating {cve_id} exploit against {target}")
 
 # Check for ngrok tunnel integration
 tunnel_config = self._get_tunnel_config_for_cve(cve_id)
 if tunnel_config:
 self.logger.info(f"[TUNNEL] Using ngrok tunnel for external target: {tunnel_config['public_url']}")
 target = tunnel_config['public_url'] # Override target with tunnel URL
 
 if self.mode == SimulationMode.DEMO:
 self._show_demo_info(cve_id)
 if tunnel_config:
 print(f"\n{Colors.BRIGHT_YELLOW} External Target Mode: Using ngrok tunnel{Colors.RESET}")
 print(f"{Colors.CYAN}Tunnel URL: {tunnel_config['public_url']}{Colors.RESET}")
 
 # Simulate reconnaissance
 print(f"\n{Colors.CYAN}[*] Phase 1: Reconnaissance{Colors.RESET}")
 recon_result = self._simulate_reconnaissance(target)
 
 if not recon_result.success:
 return recon_result
 
 # Simulate exploitation
 print(f"\n{Colors.CYAN}[*] Phase 2: Exploitation{Colors.RESET}")
 exploit_result = self.exploit.execute(cve_id, target, options)
 
 if not exploit_result.success:
 return exploit_result
 
 # Add tunnel information to exploit result
 if tunnel_config:
 exploit_result.data['tunnel_used'] = tunnel_config
 exploit_result.data['external_target'] = True
 
 # Simulate post-exploitation
 print(f"\n{Colors.CYAN}[*] Phase 3: Post-Exploitation{Colors.RESET}")
 post_exploit_result = self._simulate_post_exploitation(exploit_result.data.get('session_id'))
 
 # Store in history
 self.simulation_history.append({
 'timestamp': datetime.now(),
 'cve_id': cve_id,
 'target': target,
 'success': exploit_result.success,
 'session_id': exploit_result.data.get('session_id'),
 'tunnel_used': tunnel_config is not None
 })
 
 # Auto-generate report if enabled
 if self.auto_report and exploit_result.success:
 self._generate_exploit_report(cve_id, target, exploit_result, options)
 
 return exploit_result
 
 def _simulate_reconnaissance(self, target: str) -> SimulationResult:
 """Simulate reconnaissance phase"""
 # Port scan
 common_ports = [22, 80, 443, 3389, 8080, 8443]
 scan_result = self.network.scan_ports(target, common_ports)
 
 if self.mode != SimulationMode.FAST:
 time.sleep(1.0 if self.mode == SimulationMode.REALISTIC else 0.5)
 
 print(f"{Colors.GREEN}[+] Found {len(scan_result.data['open_ports'])} open ports{Colors.RESET}")
 
 return SimulationResult(
 success=True,
 message="Reconnaissance complete",
 data={'scan_result': scan_result.data}
 )
 
 def _simulate_post_exploitation(self, session_id: str) -> SimulationResult:
 """Simulate post-exploitation activities"""
 activities = [
 "Establishing persistence",
 "Gathering system information",
 "Enumerating users",
 "Checking privileges"
 ]
 
 results = []
 for activity in activities:
 if self.mode != SimulationMode.FAST:
 time.sleep(0.5 if self.mode == SimulationMode.REALISTIC else 0.2)
 
 print(f"{Colors.BLUE}[*] {activity}...{Colors.RESET}")
 results.append(activity)
 
 return SimulationResult(
 success=True,
 message="Post-exploitation complete",
 data={'activities': results}
 )
 
 def _show_demo_info(self, cve_id: str):
 """Show demo information about the CVE"""
 demo_info = {
 'CVE-2025-4664': {
 'name': 'Chrome Data Leak',
 'description': 'Memory corruption in Chrome Link-Header processing',
 'impact': 'Information disclosure',
 'cvss': 7.5
 },
 'CVE-2025-2783': {
 'name': 'Chrome Mojo Sandbox Escape',
 'description': 'Mojo IPC handle validation bypass',
 'impact': 'Privilege escalation',
 'cvss': 8.8
 }
 }
 
 info = demo_info.get(cve_id, {'name': 'Unknown CVE', 'description': 'No information available'})
 
 print(f"\n{Colors.YELLOW}=== DEMO MODE - CVE Information ==={Colors.RESET}")
 print(f"CVE ID: {cve_id}")
 print(f"Name: {info['name']}")
 print(f"Description: {info['description']}")
 print(f"Impact: {info.get('impact', 'Unknown')}")
 print(f"CVSS Score: {info.get('cvss', 'N/A')}")
 print(f"{Colors.YELLOW}==================================={Colors.RESET}\n")
 
 print(f"{Colors.RED}[!] This is a SIMULATION - no actual exploitation is performed{Colors.RESET}")
 time.sleep(2)
 
 def get_simulation_stats(self) -> Dict[str, Any]:
 """Get simulation statistics"""
 total_simulations = len(self.simulation_history)
 successful = sum(1 for s in self.simulation_history if s['success'])
 
 return {
 'total_simulations': total_simulations,
 'successful': successful,
 'failed': total_simulations - successful,
 'success_rate': (successful / total_simulations * 100) if total_simulations > 0 else 0,
 'mode': self.mode.value,
 'active_sessions': len(self.active_sessions),
 'history': self.simulation_history[-10:] # Last 10 simulations
 }
 
 def export_simulation_data(self, filepath: str) -> bool:
 """Export simulation data for analysis"""
 try:
 data = {
 'metadata': {
 'exported_at': datetime.now().isoformat(),
 'mode': self.mode.value,
 'total_simulations': len(self.simulation_history)
 },
 'statistics': self.get_simulation_stats(),
 'history': [
 {
 'timestamp': s['timestamp'].isoformat(),
 'cve_id': s['cve_id'],
 'target': s['target'],
 'success': s['success'],
 'session_id': s.get('session_id')
 }
 for s in self.simulation_history
 ]
 }
 
 with open(filepath, 'w') as f:
 json.dump(data, f, indent=2)
 
 self.logger.info(f"Simulation data exported to {filepath}")
 return True
 
 except Exception as e:
 self.logger.error(f"Failed to export simulation data: {str(e)}")
 return False
 
 def _generate_exploit_report(self, cve_id: str, target: str, 
 result: SimulationResult, options: Dict[str, Any] = None):
 """Generate automatic report for successful exploit"""
 self.logger.info(f"[REPORT] Generating report for {cve_id}")
 
 # Map CVE to severity
 severity_map = {
 'CVE-2025-4664': ReportSeverity.HIGH,
 'CVE-2025-2783': ReportSeverity.CRITICAL,
 'CVE-2025-2857': ReportSeverity.CRITICAL,
 'CVE-2025-30397': ReportSeverity.HIGH
 }
 
 severity = severity_map.get(cve_id, ReportSeverity.MEDIUM)
 
 # Create report
 report = self.report_generator.create_report(
 vulnerability_name=f"{cve_id} - Simulated Exploit",
 severity=severity,
 target_url=target
 )
 
 # Add vulnerability details
 cve_details = {
 'CVE-2025-4664': {
 'desc': 'Chrome Link-Header memory corruption vulnerability',
 'impact': 'Allows remote attackers to leak sensitive data from browser memory'
 },
 'CVE-2025-2783': {
 'desc': 'Chrome Mojo IPC sandbox escape vulnerability',
 'impact': 'Allows attackers to escape the Chrome sandbox and execute arbitrary code'
 },
 'CVE-2025-2857': {
 'desc': 'Firefox IPDL handle confusion vulnerability',
 'impact': 'Allows privilege escalation and sandbox escape in Firefox'
 },
 'CVE-2025-30397': {
 'desc': 'Edge WebAssembly JIT compiler vulnerability',
 'impact': 'Allows remote code execution through malicious WebAssembly modules'
 }
 }
 
 if cve_id in cve_details:
 report.vulnerability.description = cve_details[cve_id]['desc']
 report.vulnerability.impact = cve_details[cve_id]['impact']
 report.vulnerability.cve_id = cve_id
 
 # Add browser info (simulated)
 report.target.browser_name = "Chrome" if "chrome" in cve_id.lower() else "Firefox" if "firefox" in cve_id.lower() else "Edge"
 report.target.browser_version = "121.0.6167.85" # Simulated version
 
 # Add evidence from simulation
 console_output = [
 f"[*] Starting {cve_id} exploit simulation",
 f"[*] Target: {target}",
 f"[*] Mode: {self.mode.value}"
 ]
 
 # Add stage information
 if 'stages' in result.data:
 for stage in result.data['stages']:
 status = "" if stage['success'] else ""
 console_output.append(f"[{status}] {stage['stage']}")
 
 console_output.append(f"[+] Exploit completed in {result.duration:.2f} seconds")
 
 if result.data.get('session_id'):
 console_output.append(f"[+] Session created: {result.data['session_id']}")
 
 # Add evidence
 self.report_generator.add_evidence(
 report,
 payload=options.get('payload', '[Simulated payload]') if options else None,
 console_output=console_output,
 capture_screenshot=True
 )
 
 # Add remediation
 report.remediation = (
 "1. Update browser to the latest version\n"
 "2. Apply security patches as soon as available\n"
 "3. Enable browser security features\n"
 "4. Use Content Security Policy (CSP) headers\n"
 "5. Implement proper input validation"
 )
 
 # Add references
 report.references = [
 f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}",
 "https://owasp.org/www-project-top-ten/",
 "https://developer.mozilla.org/en-US/docs/Web/Security"
 ]
 
 # Export report
 json_path = self.report_generator.export_json(report)
 html_path = self.report_generator.export_html(report)
 
 print(f"\n{Colors.GREEN}[+] Professional report generated:{Colors.RESET}")
 print(f" {Colors.CYAN}JSON:{Colors.RESET} {json_path}")
 print(f" {Colors.CYAN}HTML:{Colors.RESET} {html_path}")
 print(f" {Colors.CYAN}Report ID:{Colors.RESET} {report.report_id}")
 
 self.logger.info(f"[REPORT] Report generated successfully: {report.report_id}")
 
 def _get_tunnel_config_for_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
 """Get tunnel configuration for specific CVE if external mode is active"""
 try:
 from modules.cve_integrations import get_cve_config
 config = get_cve_config(cve_id)
 
 if config and config.external_mode and config.tunnel_url:
 return {
 'public_url': config.tunnel_url,
 'local_port': config.local_port,
 'cve_id': cve_id,
 'exploit_parameters': config.exploit_parameters
 }
 except ImportError:
 self.logger.debug("CVE integrations module not available")
 except Exception as e:
 self.logger.error(f"Error getting tunnel config for {cve_id}: {str(e)}")
 
 return None

# Global simulation engine
_simulation_engine = None

def get_simulation_engine(mode: SimulationMode = SimulationMode.SAFE) -> SimulationEngine:
 """Get or create simulation engine"""
 global _simulation_engine
 if _simulation_engine is None:
 _simulation_engine = SimulationEngine(mode)
 return _simulation_engine

# Example usage
if __name__ == "__main__":
 # Create simulation engine
 engine = SimulationEngine(SimulationMode.DEMO)
 
 # Simulate CVE exploit
 result = engine.simulate_cve_exploit(
 cve_id="CVE-2025-4664",
 target="192.168.1.100",
 options={'payload_type': 'reverse_shell'}
 )
 
 print(f"\n{Colors.CYAN}=== Simulation Result ==={Colors.RESET}")
 print(f"Success: {result.success}")
 print(f"Message: {result.message}")
 print(f"Duration: {result.duration:.2f} seconds")
 
 # Get statistics
 stats = engine.get_simulation_stats()
 print(f"\n{Colors.CYAN}=== Simulation Statistics ==={Colors.RESET}")
 print(f"Total Simulations: {stats['total_simulations']}")
 print(f"Success Rate: {stats['success_rate']:.1f}%")
 
 # Export data
 engine.export_simulation_data('simulation_results.json')