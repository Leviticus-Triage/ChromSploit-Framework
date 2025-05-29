#!/usr/bin/env python3
"""
Advanced evidence collection system for forensic documentation.
Provides screenshot capture, network traffic recording, memory dumps, and artifacts.
"""

import os
import json
import subprocess
import threading
import time
import hashlib
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import mimetypes
import shutil

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import scapy.all as scapy
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False

from .enhanced_logger import get_logger
from .error_handler import get_error_handler, handle_errors
from .simulation import get_simulation_engine


class EvidenceType(Enum):
    """Types of evidence that can be collected"""
    SCREENSHOT = "screenshot"
    NETWORK_CAPTURE = "network_capture"
    MEMORY_DUMP = "memory_dump"
    FILE_ARTIFACT = "file_artifact"
    COMMAND_OUTPUT = "command_output"
    LOG_FILE = "log_file"
    REGISTRY_DATA = "registry_data"
    PROCESS_LIST = "process_list"
    SYSTEM_INFO = "system_info"


@dataclass
class Evidence:
    """Individual evidence item"""
    evidence_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None
    data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class EvidenceCase:
    """Collection of evidence for a specific case"""
    case_id: str
    case_name: str
    description: str
    target: str
    evidence_items: List[Evidence] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    investigator: str = "ChromSploit Framework"
    status: str = "active"
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)


class ScreenshotCapture:
    """Screenshot capture functionality"""
    
    def __init__(self, output_dir: str = "evidence/screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
    
    @handle_errors
    def capture_screenshot(self, title: str = "", region: Tuple[int, int, int, int] = None) -> Optional[str]:
        """Capture screenshot of screen or specific region"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{title}_{timestamp}.png" if title else f"screenshot_{timestamp}.png"
        filepath = self.output_dir / filename
        
        try:
            # Try different screenshot methods
            if HAS_PIL and hasattr(ImageGrab, 'grab'):
                # Use PIL/Pillow
                if region:
                    screenshot = ImageGrab.grab(bbox=region)
                else:
                    screenshot = ImageGrab.grab()
                screenshot.save(filepath)
                
            elif HAS_PYAUTOGUI:
                # Use pyautogui
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                screenshot.save(filepath)
                
            elif os.name == 'posix':
                # Linux/Mac - use scrot or screencapture
                if shutil.which('scrot'):
                    cmd = ['scrot', str(filepath)]
                    if region:
                        x, y, w, h = region
                        cmd.extend(['-a', f'{x},{y},{w},{h}'])
                    subprocess.run(cmd, check=True)
                elif shutil.which('screencapture'):
                    # macOS
                    cmd = ['screencapture', '-x', str(filepath)]
                    if region:
                        x, y, w, h = region
                        cmd.extend(['-R', f'{x},{y},{w},{h}'])
                    subprocess.run(cmd, check=True)
                else:
                    self.logger.error("No screenshot tool available")
                    return None
            else:
                self.logger.error("Screenshot capture not supported on this platform")
                return None
            
            self.logger.info(f"Screenshot captured: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
            return None
    
    @handle_errors
    def capture_window_screenshot(self, window_title: str) -> Optional[str]:
        """Capture screenshot of specific window"""
        # This would use platform-specific window capture
        # For now, capture full screen with note about window
        filepath = self.capture_screenshot(title=f"window_{window_title}")
        return filepath
    
    @handle_errors
    def capture_element_screenshot(self, element_selector: str, driver=None) -> Optional[str]:
        """Capture screenshot of specific web element (requires Selenium driver)"""
        if not driver:
            self.logger.warning("Selenium driver required for element screenshots")
            return None
        
        try:
            element = driver.find_element_by_css_selector(element_selector)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"element_{element_selector.replace(' ', '_')}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            element.screenshot(str(filepath))
            self.logger.info(f"Element screenshot captured: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Element screenshot failed: {e}")
            return None


class NetworkCapture:
    """Network traffic capture functionality"""
    
    def __init__(self, output_dir: str = "evidence/network"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
        self.capture_thread = None
        self.is_capturing = False
        self.current_capture_file = None
    
    @handle_errors
    def start_capture(self, interface: str = None, filter_expr: str = "", 
                     output_file: str = None) -> Optional[str]:
        """Start network packet capture"""
        if not HAS_SCAPY and not shutil.which('tcpdump'):
            self.logger.error("No packet capture tool available (install scapy or tcpdump)")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_file or f"capture_{timestamp}.pcap"
        self.current_capture_file = self.output_dir / filename
        
        self.is_capturing = True
        
        if HAS_SCAPY:
            # Use Scapy for capture
            self.capture_thread = threading.Thread(
                target=self._scapy_capture,
                args=(interface, filter_expr)
            )
        else:
            # Use tcpdump
            self.capture_thread = threading.Thread(
                target=self._tcpdump_capture,
                args=(interface, filter_expr)
            )
        
        self.capture_thread.start()
        self.logger.info(f"Network capture started: {self.current_capture_file}")
        return str(self.current_capture_file)
    
    @handle_errors
    def stop_capture(self) -> Optional[str]:
        """Stop network packet capture"""
        if not self.is_capturing:
            return None
        
        self.is_capturing = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        self.logger.info(f"Network capture stopped: {self.current_capture_file}")
        return str(self.current_capture_file)
    
    def _scapy_capture(self, interface: str, filter_expr: str):
        """Capture packets using Scapy"""
        try:
            packets = []
            
            def packet_handler(pkt):
                if self.is_capturing:
                    packets.append(pkt)
                else:
                    return True  # Stop sniffing
            
            # Start sniffing
            scapy.sniff(
                iface=interface,
                filter=filter_expr,
                prn=packet_handler,
                stop_filter=lambda x: not self.is_capturing
            )
            
            # Write packets to file
            if packets:
                scapy.wrpcap(str(self.current_capture_file), packets)
                
        except Exception as e:
            self.logger.error(f"Scapy capture failed: {e}")
    
    def _tcpdump_capture(self, interface: str, filter_expr: str):
        """Capture packets using tcpdump"""
        try:
            cmd = ['tcpdump', '-w', str(self.current_capture_file)]
            
            if interface:
                cmd.extend(['-i', interface])
            
            if filter_expr:
                cmd.extend(filter_expr.split())
            
            self.tcpdump_process = subprocess.Popen(cmd)
            
            # Wait until capture is stopped
            while self.is_capturing:
                time.sleep(0.1)
            
            # Stop tcpdump
            self.tcpdump_process.terminate()
            self.tcpdump_process.wait(timeout=5)
            
        except Exception as e:
            self.logger.error(f"tcpdump capture failed: {e}")
    
    @handle_errors
    def capture_http_traffic(self, duration: int = 60, port: int = 80) -> Optional[str]:
        """Capture HTTP traffic for specified duration"""
        filter_expr = f"tcp port {port}"
        capture_file = self.start_capture(filter_expr=filter_expr)
        
        if capture_file:
            time.sleep(duration)
            self.stop_capture()
        
        return capture_file
    
    @handle_errors
    def parse_capture_file(self, pcap_file: str) -> List[Dict[str, Any]]:
        """Parse PCAP file and extract key information"""
        if not HAS_SCAPY:
            self.logger.warning("Scapy required for PCAP parsing")
            return []
        
        try:
            packets = scapy.rdpcap(pcap_file)
            parsed_data = []
            
            for pkt in packets[:100]:  # Limit to first 100 packets
                pkt_info = {
                    'timestamp': float(pkt.time),
                    'length': len(pkt),
                    'layers': [layer.name for layer in pkt.layers()]
                }
                
                # Extract IP info
                if pkt.haslayer(scapy.IP):
                    pkt_info['src_ip'] = pkt[scapy.IP].src
                    pkt_info['dst_ip'] = pkt[scapy.IP].dst
                    pkt_info['protocol'] = pkt[scapy.IP].proto
                
                # Extract TCP/UDP info
                if pkt.haslayer(scapy.TCP):
                    pkt_info['src_port'] = pkt[scapy.TCP].sport
                    pkt_info['dst_port'] = pkt[scapy.TCP].dport
                elif pkt.haslayer(scapy.UDP):
                    pkt_info['src_port'] = pkt[scapy.UDP].sport
                    pkt_info['dst_port'] = pkt[scapy.UDP].dport
                
                parsed_data.append(pkt_info)
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"PCAP parsing failed: {e}")
            return []


class MemoryDumper:
    """Memory dump functionality"""
    
    def __init__(self, output_dir: str = "evidence/memory"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
    
    @handle_errors
    def dump_process_memory(self, pid: int, output_file: str = None) -> Optional[str]:
        """Dump memory of specific process"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_file or f"memory_dump_pid{pid}_{timestamp}.dmp"
        filepath = self.output_dir / filename
        
        try:
            if os.name == 'posix':
                # Linux/Mac - use gcore or lldb
                if shutil.which('gcore'):
                    subprocess.run(['gcore', '-o', str(filepath), str(pid)], check=True)
                elif shutil.which('lldb'):
                    # macOS
                    lldb_commands = f"process attach --pid {pid}\nmemory read --outfile {filepath} --force\nquit"
                    subprocess.run(['lldb', '-b', '-o', lldb_commands], check=True)
                else:
                    # Try /proc/pid/mem (Linux)
                    self._dump_proc_mem(pid, filepath)
            
            elif os.name == 'nt':
                # Windows - use procdump or custom implementation
                if shutil.which('procdump'):
                    subprocess.run(['procdump', '-ma', str(pid), str(filepath)], check=True)
                else:
                    self._dump_windows_process(pid, filepath)
            
            self.logger.info(f"Process memory dumped: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Memory dump failed: {e}")
            return None
    
    def _dump_proc_mem(self, pid: int, output_file: Path):
        """Dump memory using /proc/pid/mem (Linux)"""
        try:
            # Read memory maps
            with open(f'/proc/{pid}/maps', 'r') as f:
                maps = f.readlines()
            
            # Open memory file
            mem_file = open(f'/proc/{pid}/mem', 'rb')
            dump_file = open(output_file, 'wb')
            
            for line in maps:
                # Parse memory region
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                addr_range = parts[0].split('-')
                if len(addr_range) != 2:
                    continue
                
                try:
                    start = int(addr_range[0], 16)
                    end = int(addr_range[1], 16)
                    
                    # Read memory region
                    mem_file.seek(start)
                    data = mem_file.read(end - start)
                    dump_file.write(data)
                    
                except (ValueError, OSError):
                    # Skip inaccessible regions
                    continue
            
            mem_file.close()
            dump_file.close()
            
        except Exception as e:
            self.logger.error(f"proc mem dump failed: {e}")
            raise
    
    def _dump_windows_process(self, pid: int, output_file: Path):
        """Dump memory on Windows using ctypes"""
        # This would use Windows API via ctypes
        # For now, just create a placeholder
        self.logger.warning("Windows memory dump requires procdump or custom implementation")
        output_file.write_text(f"Memory dump placeholder for PID {pid}")
    
    @handle_errors
    def create_full_memory_dump(self) -> Optional[str]:
        """Create full system memory dump"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"full_memory_dump_{timestamp}.dmp"
        filepath = self.output_dir / filename
        
        try:
            if os.name == 'posix' and os.path.exists('/dev/mem'):
                # Requires root privileges
                self.logger.warning("Full memory dump requires root privileges")
                subprocess.run(['dd', 'if=/dev/mem', f'of={filepath}'], check=True)
            else:
                self.logger.error("Full memory dump not supported on this platform")
                return None
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Full memory dump failed: {e}")
            return None
    
    @handle_errors
    def extract_strings_from_dump(self, dump_file: str, min_length: int = 4) -> List[str]:
        """Extract readable strings from memory dump"""
        try:
            # Use strings command if available
            if shutil.which('strings'):
                result = subprocess.run(
                    ['strings', '-n', str(min_length), dump_file],
                    capture_output=True,
                    text=True
                )
                return result.stdout.strip().split('\n')[:1000]  # Limit to 1000 strings
            
            # Manual string extraction
            strings = []
            with open(dump_file, 'rb') as f:
                current_string = b""
                
                while True:
                    chunk = f.read(1024 * 1024)  # Read 1MB at a time
                    if not chunk:
                        break
                    
                    for byte in chunk:
                        if 32 <= byte <= 126:  # Printable ASCII
                            current_string += bytes([byte])
                        else:
                            if len(current_string) >= min_length:
                                strings.append(current_string.decode('ascii', errors='ignore'))
                            current_string = b""
                    
                    if len(strings) >= 1000:
                        break
            
            return strings
            
        except Exception as e:
            self.logger.error(f"String extraction failed: {e}")
            return []


class ArtifactCollector:
    """Collect various system artifacts"""
    
    def __init__(self, output_dir: str = "evidence/artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger()
    
    @handle_errors
    def collect_file_artifact(self, file_path: str, description: str = "") -> Optional[Evidence]:
        """Collect a file as evidence"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return None
            
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            dest_path = self.output_dir / filename
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Calculate hash
            hash_value = self.calculate_file_hash(str(dest_path))
            
            # Create evidence object
            evidence = Evidence(
                evidence_id=f"file_{timestamp}",
                evidence_type=EvidenceType.FILE_ARTIFACT,
                title=f"File: {source_path.name}",
                description=description or f"Collected file artifact: {source_path}",
                file_path=str(dest_path),
                hash_value=hash_value,
                metadata={
                    'original_path': str(source_path),
                    'size': source_path.stat().st_size,
                    'mime_type': mimetypes.guess_type(str(source_path))[0],
                    'permissions': oct(source_path.stat().st_mode)[-3:],
                    'modified_time': datetime.fromtimestamp(source_path.stat().st_mtime).isoformat()
                }
            )
            
            self.logger.info(f"File artifact collected: {dest_path}")
            return evidence
            
        except Exception as e:
            self.logger.error(f"File artifact collection failed: {e}")
            return None
    
    @handle_errors
    def collect_command_output(self, command: str, description: str = "") -> Optional[Evidence]:
        """Collect command output as evidence"""
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Save output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"command_output_{timestamp}.txt"
            filepath = self.output_dir / filename
            
            output_data = f"Command: {command}\n"
            output_data += f"Exit Code: {result.returncode}\n"
            output_data += f"Timestamp: {datetime.now().isoformat()}\n"
            output_data += "\n--- STDOUT ---\n"
            output_data += result.stdout
            output_data += "\n--- STDERR ---\n"
            output_data += result.stderr
            
            filepath.write_text(output_data)
            
            # Create evidence object
            evidence = Evidence(
                evidence_id=f"cmd_{timestamp}",
                evidence_type=EvidenceType.COMMAND_OUTPUT,
                title=f"Command: {command[:50]}...",
                description=description or f"Output from command: {command}",
                file_path=str(filepath),
                data=output_data,
                metadata={
                    'command': command,
                    'exit_code': result.returncode,
                    'stdout_lines': len(result.stdout.splitlines()),
                    'stderr_lines': len(result.stderr.splitlines())
                }
            )
            
            self.logger.info(f"Command output collected: {command}")
            return evidence
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return None
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return None
    
    @handle_errors
    def collect_process_list(self) -> Optional[Evidence]:
        """Collect current process list"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"process_list_{timestamp}.json"
            filepath = self.output_dir / filename
            
            processes = []
            
            if os.name == 'posix':
                # Unix-like systems
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': parts[10]
                        })
            
            elif os.name == 'nt':
                # Windows
                result = subprocess.run(
                    ['wmic', 'process', 'get', 'ProcessId,Name,ExecutablePath,CommandLine', '/format:csv'],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.strip().split('\n')[2:]  # Skip headers
                
                for line in lines:
                    parts = line.split(',')
                    if len(parts) >= 5:
                        processes.append({
                            'pid': parts[3],
                            'name': parts[2],
                            'path': parts[1],
                            'command': parts[0]
                        })
            
            # Save process list
            with open(filepath, 'w') as f:
                json.dump(processes, f, indent=2)
            
            # Create evidence object
            evidence = Evidence(
                evidence_id=f"processes_{timestamp}",
                evidence_type=EvidenceType.PROCESS_LIST,
                title="Process List Snapshot",
                description=f"System process list at {datetime.now().isoformat()}",
                file_path=str(filepath),
                data=processes,
                metadata={
                    'process_count': len(processes),
                    'platform': os.name
                }
            )
            
            self.logger.info(f"Process list collected: {len(processes)} processes")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Process list collection failed: {e}")
            return None
    
    @handle_errors
    def collect_system_info(self) -> Optional[Evidence]:
        """Collect comprehensive system information"""
        try:
            import platform
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_info_{timestamp}.json"
            filepath = self.output_dir / filename
            
            system_info = {
                'platform': {
                    'system': platform.system(),
                    'node': platform.node(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'python': {
                    'version': platform.python_version(),
                    'implementation': platform.python_implementation(),
                    'compiler': platform.python_compiler()
                },
                'network': self._get_network_info(),
                'environment': dict(os.environ),
                'users': self._get_user_info(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save system info
            with open(filepath, 'w') as f:
                json.dump(system_info, f, indent=2)
            
            # Create evidence object
            evidence = Evidence(
                evidence_id=f"sysinfo_{timestamp}",
                evidence_type=EvidenceType.SYSTEM_INFO,
                title="System Information",
                description="Comprehensive system information snapshot",
                file_path=str(filepath),
                data=system_info,
                metadata={
                    'hostname': platform.node(),
                    'os': platform.system(),
                    'architecture': platform.machine()
                }
            )
            
            self.logger.info("System information collected")
            return evidence
            
        except Exception as e:
            self.logger.error(f"System info collection failed: {e}")
            return None
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network configuration info"""
        network_info = {}
        
        try:
            if os.name == 'posix':
                # Get interfaces
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                network_info['interfaces'] = result.stdout
                
                # Get routing table
                result = subprocess.run(['netstat', '-rn'], capture_output=True, text=True)
                network_info['routing'] = result.stdout
                
            elif os.name == 'nt':
                # Windows
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                network_info['interfaces'] = result.stdout
                
                result = subprocess.run(['route', 'print'], capture_output=True, text=True)
                network_info['routing'] = result.stdout
        
        except Exception as e:
            self.logger.debug(f"Network info collection error: {e}")
        
        return network_info
    
    def _get_user_info(self) -> List[str]:
        """Get system users"""
        users = []
        
        try:
            if os.name == 'posix':
                with open('/etc/passwd', 'r') as f:
                    for line in f:
                        username = line.split(':')[0]
                        users.append(username)
            elif os.name == 'nt':
                result = subprocess.run(['net', 'user'], capture_output=True, text=True)
                users = result.stdout.strip().split()
        
        except Exception as e:
            self.logger.debug(f"User info collection error: {e}")
        
        return users
    
    @handle_errors
    def calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()


class EvidenceCollectionManager:
    """Main evidence collection manager"""
    
    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger()
        self.simulation = get_simulation_engine()
        
        # Initialize collectors
        self.screenshot = ScreenshotCapture(str(self.output_dir / "screenshots"))
        self.network = NetworkCapture(str(self.output_dir / "network"))
        self.memory = MemoryDumper(str(self.output_dir / "memory"))
        self.artifacts = ArtifactCollector(str(self.output_dir / "artifacts"))
        
        # Evidence cases
        self.cases: Dict[str, EvidenceCase] = {}
        
        # Load existing cases
        self.load_cases()
    
    @handle_errors
    def create_case(self, case_name: str, description: str, target: str) -> str:
        """Create new evidence collection case"""
        case_id = f"case_{int(time.time())}"
        
        case = EvidenceCase(
            case_id=case_id,
            case_name=case_name,
            description=description,
            target=target
        )
        
        self.cases[case_id] = case
        self.save_case(case_id)
        
        self.logger.info(f"Created evidence case: {case_name} ({case_id})")
        return case_id
    
    @handle_errors
    def add_evidence_to_case(self, case_id: str, evidence: Evidence):
        """Add evidence to case"""
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")
        
        case = self.cases[case_id]
        case.evidence_items.append(evidence)
        case.last_updated = datetime.now()
        
        # Add chain of custody entry
        custody_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'evidence_added',
            'evidence_id': evidence.evidence_id,
            'evidence_type': evidence.evidence_type.value,
            'hash': evidence.hash_value,
            'user': case.investigator
        }
        case.chain_of_custody.append(custody_entry)
        
        self.save_case(case_id)
        self.logger.info(f"Added evidence {evidence.evidence_id} to case {case_id}")
    
    @handle_errors
    def collect_screenshot(self, case_id: str, title: str = "", 
                         description: str = "", region: Tuple[int, int, int, int] = None) -> Optional[Evidence]:
        """Collect screenshot evidence"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_evidence_collection(EvidenceType.SCREENSHOT, title)
        
        filepath = self.screenshot.capture_screenshot(title, region)
        if not filepath:
            return None
        
        # Calculate hash
        hash_value = self.artifacts.calculate_file_hash(filepath)
        
        # Create evidence
        evidence = Evidence(
            evidence_id=f"screenshot_{int(time.time())}",
            evidence_type=EvidenceType.SCREENSHOT,
            title=title or "Screenshot",
            description=description or f"Screenshot captured at {datetime.now()}",
            file_path=filepath,
            hash_value=hash_value,
            metadata={
                'region': region,
                'display_size': self._get_display_size()
            }
        )
        
        # Add to case
        self.add_evidence_to_case(case_id, evidence)
        
        return evidence
    
    @handle_errors
    def collect_network_traffic(self, case_id: str, duration: int = 60, 
                               interface: str = None, filter_expr: str = "") -> Optional[Evidence]:
        """Collect network traffic evidence"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_evidence_collection(EvidenceType.NETWORK_CAPTURE, "network_capture")
        
        # Start capture
        pcap_file = self.network.start_capture(interface, filter_expr)
        if not pcap_file:
            return None
        
        # Wait for duration
        self.logger.info(f"Capturing network traffic for {duration} seconds...")
        time.sleep(duration)
        
        # Stop capture
        self.network.stop_capture()
        
        # Calculate hash
        hash_value = self.artifacts.calculate_file_hash(pcap_file)
        
        # Parse basic info
        packet_info = self.network.parse_capture_file(pcap_file)
        
        # Create evidence
        evidence = Evidence(
            evidence_id=f"pcap_{int(time.time())}",
            evidence_type=EvidenceType.NETWORK_CAPTURE,
            title=f"Network Capture ({duration}s)",
            description=f"Network traffic captured for {duration} seconds",
            file_path=pcap_file,
            hash_value=hash_value,
            metadata={
                'duration': duration,
                'interface': interface,
                'filter': filter_expr,
                'packet_count': len(packet_info),
                'capture_size': Path(pcap_file).stat().st_size
            }
        )
        
        # Add to case
        self.add_evidence_to_case(case_id, evidence)
        
        return evidence
    
    @handle_errors
    def collect_memory_dump(self, case_id: str, pid: int = None) -> Optional[Evidence]:
        """Collect memory dump evidence"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_evidence_collection(EvidenceType.MEMORY_DUMP, f"pid_{pid}")
        
        if pid:
            dump_file = self.memory.dump_process_memory(pid)
            title = f"Process Memory Dump (PID: {pid})"
            description = f"Memory dump of process {pid}"
        else:
            dump_file = self.memory.create_full_memory_dump()
            title = "Full System Memory Dump"
            description = "Complete system memory dump"
        
        if not dump_file:
            return None
        
        # Calculate hash
        hash_value = self.artifacts.calculate_file_hash(dump_file)
        
        # Extract some strings for metadata
        strings = self.memory.extract_strings_from_dump(dump_file)
        
        # Create evidence
        evidence = Evidence(
            evidence_id=f"memory_{int(time.time())}",
            evidence_type=EvidenceType.MEMORY_DUMP,
            title=title,
            description=description,
            file_path=dump_file,
            hash_value=hash_value,
            metadata={
                'pid': pid,
                'dump_size': Path(dump_file).stat().st_size,
                'string_count': len(strings),
                'sample_strings': strings[:10]  # First 10 strings
            }
        )
        
        # Add to case
        self.add_evidence_to_case(case_id, evidence)
        
        return evidence
    
    @handle_errors
    def collect_file_artifact(self, case_id: str, file_path: str, description: str = "") -> Optional[Evidence]:
        """Collect file artifact evidence"""
        evidence = self.artifacts.collect_file_artifact(file_path, description)
        
        if evidence:
            self.add_evidence_to_case(case_id, evidence)
        
        return evidence
    
    @handle_errors
    def collect_command_output(self, case_id: str, command: str, description: str = "") -> Optional[Evidence]:
        """Collect command output evidence"""
        evidence = self.artifacts.collect_command_output(command, description)
        
        if evidence:
            self.add_evidence_to_case(case_id, evidence)
        
        return evidence
    
    @handle_errors
    def collect_system_artifacts(self, case_id: str) -> List[Evidence]:
        """Collect comprehensive system artifacts"""
        artifacts = []
        
        # Process list
        proc_evidence = self.artifacts.collect_process_list()
        if proc_evidence:
            self.add_evidence_to_case(case_id, proc_evidence)
            artifacts.append(proc_evidence)
        
        # System info
        sys_evidence = self.artifacts.collect_system_info()
        if sys_evidence:
            self.add_evidence_to_case(case_id, sys_evidence)
            artifacts.append(sys_evidence)
        
        # Common commands
        commands = [
            ('netstat -an', 'Network connections'),
            ('arp -a', 'ARP cache'),
            ('whoami /all' if os.name == 'nt' else 'id', 'Current user info'),
            ('systeminfo' if os.name == 'nt' else 'uname -a', 'System information')
        ]
        
        for cmd, desc in commands:
            cmd_evidence = self.artifacts.collect_command_output(cmd, desc)
            if cmd_evidence:
                self.add_evidence_to_case(case_id, cmd_evidence)
                artifacts.append(cmd_evidence)
        
        return artifacts
    
    @handle_errors
    def generate_evidence_report(self, case_id: str, format: str = "html") -> str:
        """Generate evidence report"""
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")
        
        case = self.cases[case_id]
        
        if format == "html":
            return self._generate_html_report(case)
        elif format == "json":
            return self._generate_json_report(case)
        elif format == "markdown":
            return self._generate_markdown_report(case)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_html_report(self, case: EvidenceCase) -> str:
        """Generate HTML evidence report"""
        output_file = self.output_dir / f"report_{case.case_id}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Evidence Report - {case.case_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .evidence-item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .metadata {{ background: #f9f9f9; padding: 10px; margin: 10px 0; font-family: monospace; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .hash {{ font-family: monospace; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Evidence Report: {case.case_name}</h1>
                <p><strong>Case ID:</strong> {case.case_id}</p>
                <p><strong>Target:</strong> {case.target}</p>
                <p><strong>Created:</strong> {case.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Last Updated:</strong> {case.last_updated.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Evidence Items:</strong> {len(case.evidence_items)}</p>
            </div>
            
            <h2>Evidence Summary</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Title</th>
                    <th>Timestamp</th>
                    <th>Hash</th>
                </tr>
        """
        
        for evidence in case.evidence_items:
            html_content += f"""
                <tr>
                    <td>{evidence.evidence_id}</td>
                    <td>{evidence.evidence_type.value}</td>
                    <td>{evidence.title}</td>
                    <td>{evidence.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td class="hash">{evidence.hash_value[:16]}...</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Evidence Details</h2>
        """
        
        for evidence in case.evidence_items:
            html_content += f"""
            <div class="evidence-item">
                <h3>{evidence.title}</h3>
                <p><strong>ID:</strong> {evidence.evidence_id}</p>
                <p><strong>Type:</strong> {evidence.evidence_type.value}</p>
                <p><strong>Description:</strong> {evidence.description}</p>
                <p><strong>Timestamp:</strong> {evidence.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                {f'<p><strong>File:</strong> {evidence.file_path}</p>' if evidence.file_path else ''}
                {f'<p><strong>Hash (SHA256):</strong> <span class="hash">{evidence.hash_value}</span></p>' if evidence.hash_value else ''}
                
                {f'<div class="metadata"><strong>Metadata:</strong><pre>{json.dumps(evidence.metadata, indent=2)}</pre></div>' if evidence.metadata else ''}
            </div>
            """
        
        html_content += """
            <h2>Chain of Custody</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Evidence ID</th>
                    <th>Type</th>
                    <th>User</th>
                </tr>
        """
        
        for entry in case.chain_of_custody:
            html_content += f"""
                <tr>
                    <td>{entry['timestamp']}</td>
                    <td>{entry['action']}</td>
                    <td>{entry.get('evidence_id', 'N/A')}</td>
                    <td>{entry.get('evidence_type', 'N/A')}</td>
                    <td>{entry['user']}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _generate_json_report(self, case: EvidenceCase) -> str:
        """Generate JSON evidence report"""
        output_file = self.output_dir / f"report_{case.case_id}.json"
        
        report_data = {
            'case_info': {
                'case_id': case.case_id,
                'case_name': case.case_name,
                'description': case.description,
                'target': case.target,
                'investigator': case.investigator,
                'status': case.status,
                'created_at': case.created_at.isoformat(),
                'last_updated': case.last_updated.isoformat()
            },
            'evidence_items': [
                {
                    'evidence_id': evidence.evidence_id,
                    'evidence_type': evidence.evidence_type.value,
                    'title': evidence.title,
                    'description': evidence.description,
                    'file_path': evidence.file_path,
                    'hash_value': evidence.hash_value,
                    'timestamp': evidence.timestamp.isoformat(),
                    'metadata': evidence.metadata,
                    'tags': evidence.tags
                } for evidence in case.evidence_items
            ],
            'chain_of_custody': case.chain_of_custody,
            'summary': {
                'total_evidence': len(case.evidence_items),
                'evidence_types': {
                    etype.value: len([e for e in case.evidence_items if e.evidence_type == etype])
                    for etype in EvidenceType
                }
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return str(output_file)
    
    def _generate_markdown_report(self, case: EvidenceCase) -> str:
        """Generate Markdown evidence report"""
        output_file = self.output_dir / f"report_{case.case_id}.md"
        
        md_content = f"""# Evidence Report: {case.case_name}

## Case Information
- **Case ID:** {case.case_id}
- **Target:** {case.target}
- **Created:** {case.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Last Updated:** {case.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
- **Investigator:** {case.investigator}
- **Status:** {case.status}

## Description
{case.description}

## Evidence Summary
Total Evidence Items: {len(case.evidence_items)}

| Type | Count |
|------|-------|
"""
        
        # Count by type
        type_counts = {}
        for evidence in case.evidence_items:
            type_name = evidence.evidence_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        for type_name, count in type_counts.items():
            md_content += f"| {type_name} | {count} |\n"
        
        md_content += "\n## Evidence Items\n\n"
        
        for evidence in case.evidence_items:
            md_content += f"""### {evidence.title}
- **ID:** {evidence.evidence_id}
- **Type:** {evidence.evidence_type.value}
- **Timestamp:** {evidence.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Description:** {evidence.description}
"""
            
            if evidence.file_path:
                md_content += f"- **File:** `{evidence.file_path}`\n"
            
            if evidence.hash_value:
                md_content += f"- **SHA256:** `{evidence.hash_value}`\n"
            
            if evidence.metadata:
                md_content += "\n**Metadata:**\n```json\n"
                md_content += json.dumps(evidence.metadata, indent=2)
                md_content += "\n```\n"
            
            md_content += "\n---\n\n"
        
        md_content += """## Chain of Custody

| Timestamp | Action | Evidence ID | Type | User |
|-----------|--------|-------------|------|------|
"""
        
        for entry in case.chain_of_custody:
            md_content += f"| {entry['timestamp']} | {entry['action']} | "
            md_content += f"{entry.get('evidence_id', 'N/A')} | "
            md_content += f"{entry.get('evidence_type', 'N/A')} | {entry['user']} |\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(output_file)
    
    @handle_errors
    def save_case(self, case_id: str):
        """Save case data to disk"""
        if case_id not in self.cases:
            return
        
        case_file = self.output_dir / f"case_{case_id}.json"
        case = self.cases[case_id]
        
        # Convert to JSON-serializable format
        case_data = {
            'case_id': case.case_id,
            'case_name': case.case_name,
            'description': case.description,
            'target': case.target,
            'created_at': case.created_at.isoformat(),
            'last_updated': case.last_updated.isoformat(),
            'investigator': case.investigator,
            'status': case.status,
            'evidence_items': [
                {
                    'evidence_id': e.evidence_id,
                    'evidence_type': e.evidence_type.value,
                    'title': e.title,
                    'description': e.description,
                    'file_path': e.file_path,
                    'hash_value': e.hash_value,
                    'timestamp': e.timestamp.isoformat(),
                    'metadata': e.metadata,
                    'tags': e.tags
                } for e in case.evidence_items
            ],
            'chain_of_custody': case.chain_of_custody
        }
        
        with open(case_file, 'w') as f:
            json.dump(case_data, f, indent=2)
        
        self.logger.info(f"Case {case_id} saved")
    
    @handle_errors
    def load_cases(self):
        """Load existing cases from disk"""
        for case_file in self.output_dir.glob("case_*.json"):
            try:
                with open(case_file, 'r') as f:
                    case_data = json.load(f)
                
                # Reconstruct case object
                case = EvidenceCase(
                    case_id=case_data['case_id'],
                    case_name=case_data['case_name'],
                    description=case_data['description'],
                    target=case_data['target'],
                    created_at=datetime.fromisoformat(case_data['created_at']),
                    last_updated=datetime.fromisoformat(case_data['last_updated']),
                    investigator=case_data.get('investigator', 'ChromSploit Framework'),
                    status=case_data.get('status', 'active'),
                    chain_of_custody=case_data.get('chain_of_custody', [])
                )
                
                # Reconstruct evidence items
                for e_data in case_data.get('evidence_items', []):
                    evidence = Evidence(
                        evidence_id=e_data['evidence_id'],
                        evidence_type=EvidenceType(e_data['evidence_type']),
                        title=e_data['title'],
                        description=e_data['description'],
                        file_path=e_data.get('file_path'),
                        hash_value=e_data.get('hash_value'),
                        timestamp=datetime.fromisoformat(e_data['timestamp']),
                        metadata=e_data.get('metadata', {}),
                        tags=e_data.get('tags', [])
                    )
                    case.evidence_items.append(evidence)
                
                self.cases[case.case_id] = case
                self.logger.info(f"Loaded case: {case.case_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load case from {case_file}: {e}")
    
    def _get_display_size(self) -> Tuple[int, int]:
        """Get display size"""
        try:
            if HAS_PYAUTOGUI:
                return pyautogui.size()
            elif os.name == 'posix':
                # Try xrandr on Linux
                result = subprocess.run(['xrandr'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ' connected' in line and ' primary' in line:
                        resolution = line.split()[3].split('+')[0]
                        w, h = map(int, resolution.split('x'))
                        return (w, h)
            
            # Default
            return (1920, 1080)
            
        except Exception:
            return (1920, 1080)
    
    @handle_errors
    def get_case_summary(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case summary"""
        if case_id not in self.cases:
            return None
        
        case = self.cases[case_id]
        
        # Count evidence by type
        type_counts = {}
        for evidence in case.evidence_items:
            type_name = evidence.evidence_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'case_id': case.case_id,
            'case_name': case.case_name,
            'target': case.target,
            'status': case.status,
            'created_at': case.created_at.isoformat(),
            'last_updated': case.last_updated.isoformat(),
            'total_evidence': len(case.evidence_items),
            'evidence_by_type': type_counts,
            'chain_of_custody_entries': len(case.chain_of_custody)
        }
    
    @handle_errors
    def list_cases(self) -> List[Dict[str, Any]]:
        """List all cases"""
        return [self.get_case_summary(case_id) for case_id in self.cases]


# Global evidence collection manager instance
_evidence_manager = None

def get_evidence_manager() -> EvidenceCollectionManager:
    """Get global evidence collection manager instance"""
    global _evidence_manager
    if _evidence_manager is None:
        _evidence_manager = EvidenceCollectionManager()
    return _evidence_manager