#!/usr/bin/env python3
"""
Advanced reconnaissance module for target discovery and information gathering.
Integrates multiple tools and techniques for comprehensive target analysis.
"""

import subprocess
import json
import asyncio
import socket
import ssl
import requests
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import dns.resolver
import threading
import time

from .enhanced_logger import get_logger
from .error_handler import get_error_handler, handle_errors
from .simulation import get_simulation_engine


@dataclass
class SubdomainResult:
    """Result from subdomain enumeration"""
    domain: str
    subdomains: Set[str] = field(default_factory=set)
    sources: Dict[str, Set[str]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PortScanResult:
    """Result from port scanning"""
    host: str
    open_ports: List[Tuple[int, str]] = field(default_factory=list)  # (port, service)
    closed_ports: List[int] = field(default_factory=list)
    filtered_ports: List[int] = field(default_factory=list)
    scan_duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceInfo:
    """Service fingerprinting information"""
    host: str
    port: int
    service: str
    version: str = ""
    banner: str = ""
    ssl_info: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReconTarget:
    """Complete reconnaissance target information"""
    target: str
    subdomains: SubdomainResult = None
    port_scans: Dict[str, PortScanResult] = field(default_factory=dict)
    services: List[ServiceInfo] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class SubdomainEnumerator:
    """Subdomain enumeration using multiple techniques"""
    
    def __init__(self, output_dir: str = "recon_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger()
        
    @handle_errors
    def enumerate_dns_bruteforce(self, domain: str, wordlist: List[str] = None) -> Set[str]:
        """DNS bruteforce subdomain enumeration"""
        if not wordlist:
            # Common subdomain wordlist
            wordlist = [
                "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
                "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m", "imap", "test",
                "ns", "blog", "pop3", "dev", "www2", "admin", "forum", "news", "vpn", "ns3",
                "mail2", "new", "mysql", "old", "www1", "email", "img", "www3", "help", "shop"
            ]
        
        found_subdomains = set()
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3
        
        self.logger.info(f"Starting DNS bruteforce for {domain} with {len(wordlist)} words")
        
        for subdomain in wordlist:
            try:
                target = f"{subdomain}.{domain}"
                answers = resolver.resolve(target, 'A')
                if answers:
                    found_subdomains.add(target)
                    self.logger.debug(f"Found subdomain: {target}")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                continue
            except Exception as e:
                self.logger.debug(f"Error resolving {subdomain}.{domain}: {e}")
        
        self.logger.info(f"DNS bruteforce found {len(found_subdomains)} subdomains")
        return found_subdomains
    
    @handle_errors
    def enumerate_certificate_transparency(self, domain: str) -> Set[str]:
        """Certificate transparency log enumeration"""
        subdomains = set()
        
        try:
            # crt.sh API
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                certificates = response.json()
                for cert in certificates:
                    name_value = cert.get('name_value', '')
                    for name in name_value.split('\n'):
                        name = name.strip()
                        if name.endswith(f'.{domain}') and '*' not in name:
                            subdomains.add(name)
                
                self.logger.info(f"Certificate transparency found {len(subdomains)} subdomains")
        
        except Exception as e:
            self.logger.warning(f"Certificate transparency enumeration failed: {e}")
        
        return subdomains
    
    @handle_errors
    def enumerate_search_engines(self, domain: str) -> Set[str]:
        """Search engine dorking for subdomains"""
        # This would integrate with search engines (with rate limiting)
        # For now, return empty set to avoid API rate limits
        self.logger.info("Search engine enumeration skipped (rate limiting)")
        return set()
    
    @handle_errors
    def enumerate_all(self, domain: str, methods: List[str] = None) -> SubdomainResult:
        """Run all enumeration methods"""
        if not methods:
            methods = ['dns_bruteforce', 'certificate_transparency']
        
        result = SubdomainResult(domain=domain)
        
        for method in methods:
            try:
                if method == 'dns_bruteforce':
                    subs = self.enumerate_dns_bruteforce(domain)
                    result.sources['dns_bruteforce'] = subs
                elif method == 'certificate_transparency':
                    subs = self.enumerate_certificate_transparency(domain)
                    result.sources['certificate_transparency'] = subs
                elif method == 'search_engines':
                    subs = self.enumerate_search_engines(domain)
                    result.sources['search_engines'] = subs
                
                result.subdomains.update(subs)
                
            except Exception as e:
                self.logger.error(f"Subdomain enumeration method {method} failed: {e}")
        
        # Save results
        output_file = self.output_dir / f"subdomains_{domain}_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'domain': domain,
                'subdomains': list(result.subdomains),
                'sources': {k: list(v) for k, v in result.sources.items()},
                'timestamp': result.timestamp.isoformat()
            }, f, indent=2)
        
        self.logger.info(f"Subdomain enumeration complete: {len(result.subdomains)} total subdomains found")
        return result


class PortScanner:
    """Advanced port scanning with service detection"""
    
    def __init__(self, output_dir: str = "recon_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger()
    
    @handle_errors
    def scan_tcp_connect(self, host: str, ports: List[int], timeout: float = 3.0) -> PortScanResult:
        """TCP connect scan"""
        result = PortScanResult(host=host)
        start_time = time.time()
        
        self.logger.info(f"Starting TCP connect scan on {host} for {len(ports)} ports")
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result_code = sock.connect_ex((host, port))
                sock.close()
                
                if result_code == 0:
                    # Try to get service name
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    
                    result.open_ports.append((port, service))
                    self.logger.debug(f"Port {port} open on {host} ({service})")
                else:
                    result.closed_ports.append(port)
                    
            except Exception as e:
                result.filtered_ports.append(port)
                self.logger.debug(f"Port {port} filtered/error on {host}: {e}")
        
        # Use threading for parallel scanning
        threads = []
        for port in ports:
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        result.scan_duration = time.time() - start_time
        
        # Save results
        output_file = self.output_dir / f"portscan_{host}_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'host': host,
                'open_ports': result.open_ports,
                'closed_ports': result.closed_ports,
                'filtered_ports': result.filtered_ports,
                'scan_duration': result.scan_duration,
                'timestamp': result.timestamp.isoformat()
            }, f, indent=2)
        
        self.logger.info(f"Port scan complete: {len(result.open_ports)} open ports found on {host}")
        return result
    
    @handle_errors
    def get_common_ports(self, profile: str = "top1000") -> List[int]:
        """Get common port lists"""
        if profile == "top100":
            return [
                21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306,
                3389, 5900, 8080, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993,
                995, 1723, 3306, 3389, 5900, 8080, 135, 139, 445, 1433, 1521, 3306, 3389,
                5432, 5900, 6379, 8080, 8443, 9200, 27017, 6667, 6697, 6379, 11211, 50000
            ]
        elif profile == "top1000":
            # Common 1000 ports (abbreviated for space)
            return list(range(1, 1001))
        else:  # all
            return list(range(1, 65536))


class ServiceFingerprinter:
    """Service version detection and banner grabbing"""
    
    def __init__(self):
        self.logger = get_logger()
    
    @handle_errors
    def grab_banner(self, host: str, port: int, timeout: float = 5.0) -> str:
        """Grab service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            
            # Send common probes
            if port in [80, 8080, 8443]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
            elif port == 25:
                sock.send(b"EHLO test\r\n")
            elif port == 21:
                pass  # FTP sends banner immediately
            else:
                sock.send(b"\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner
            
        except Exception as e:
            self.logger.debug(f"Banner grab failed for {host}:{port}: {e}")
            return ""
    
    @handle_errors
    def check_ssl_info(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """Get SSL/TLS certificate information"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    return {
                        'version': ssock.version(),
                        'cipher': cipher,
                        'certificate': cert,
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'san': cert.get('subjectAltName', [])
                    }
                    
        except Exception as e:
            self.logger.debug(f"SSL info collection failed for {host}:{port}: {e}")
            return None
    
    @handle_errors
    def fingerprint_http(self, host: str, port: int) -> Dict[str, str]:
        """HTTP service fingerprinting"""
        headers = {}
        try:
            url = f"http{'s' if port in [443, 8443] else ''}://{host}:{port}/"
            response = requests.get(url, timeout=10, verify=False, allow_redirects=False)
            headers = dict(response.headers)
            
        except Exception as e:
            self.logger.debug(f"HTTP fingerprinting failed for {host}:{port}: {e}")
        
        return headers
    
    @handle_errors
    def fingerprint_service(self, host: str, port: int, service: str) -> ServiceInfo:
        """Complete service fingerprinting"""
        info = ServiceInfo(host=host, port=port, service=service)
        
        # Get banner
        info.banner = self.grab_banner(host, port)
        
        # SSL/TLS info for secure services
        if port in [443, 993, 995, 8443] or 'ssl' in service.lower():
            info.ssl_info = self.check_ssl_info(host, port)
        
        # HTTP-specific fingerprinting
        if service.lower() in ['http', 'https', 'http-proxy'] or port in [80, 443, 8080, 8443]:
            info.headers = self.fingerprint_http(host, port)
            
            # Try to determine web server version
            server_header = info.headers.get('Server', '')
            if server_header:
                info.version = server_header
        
        # Extract version from banner if not found elsewhere
        if not info.version and info.banner:
            # Simple version extraction patterns
            import re
            version_patterns = [
                r'(\d+\.\d+\.\d+)',
                r'v(\d+\.\d+)',
                r'(\d+\.\d+)'
            ]
            for pattern in version_patterns:
                match = re.search(pattern, info.banner)
                if match:
                    info.version = match.group(1)
                    break
        
        self.logger.debug(f"Fingerprinted {host}:{port} - {service} {info.version}")
        return info


class ReconnaissanceManager:
    """Main reconnaissance manager coordinating all recon activities"""
    
    def __init__(self, output_dir: str = "recon_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger()
        self.simulation = get_simulation_engine()
        
        self.subdomain_enum = SubdomainEnumerator(output_dir)
        self.port_scanner = PortScanner(output_dir)
        self.fingerprinter = ServiceFingerprinter()
        
        self.targets: Dict[str, ReconTarget] = {}
    
    @handle_errors
    def add_target(self, target: str) -> ReconTarget:
        """Add a new reconnaissance target"""
        if target not in self.targets:
            self.targets[target] = ReconTarget(target=target)
            self.logger.info(f"Added reconnaissance target: {target}")
        
        return self.targets[target]
    
    @handle_errors
    def run_subdomain_enumeration(self, target: str, methods: List[str] = None) -> SubdomainResult:
        """Run subdomain enumeration for a target"""
        if self.simulation.is_simulation_mode():
            # Simulate subdomain enumeration
            return self.simulation.simulate_subdomain_enumeration(target, methods or [])
        
        recon_target = self.add_target(target)
        result = self.subdomain_enum.enumerate_all(target, methods)
        recon_target.subdomains = result
        recon_target.last_updated = datetime.now()
        
        self.logger.info(f"Subdomain enumeration completed for {target}: {len(result.subdomains)} subdomains")
        return result
    
    @handle_errors
    def run_port_scan(self, host: str, port_range: str = "top1000") -> PortScanResult:
        """Run port scan on a host"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_port_scan(host, port_range)
        
        # Get port list based on range
        if port_range == "top100":
            ports = self.port_scanner.get_common_ports("top100")
        elif port_range == "top1000":
            ports = self.port_scanner.get_common_ports("top1000")
        elif port_range == "all":
            ports = self.port_scanner.get_common_ports("all")
        else:
            # Custom range like "1-1000"
            try:
                start, end = map(int, port_range.split('-'))
                ports = list(range(start, end + 1))
            except:
                ports = self.port_scanner.get_common_ports("top1000")
        
        result = self.port_scanner.scan_tcp_connect(host, ports)
        
        # Update target information
        for target_name, target in self.targets.items():
            if host == target_name or (target.subdomains and host in target.subdomains.subdomains):
                target.port_scans[host] = result
                target.last_updated = datetime.now()
                break
        
        return result
    
    @handle_errors
    def run_service_fingerprinting(self, host: str, ports: List[Tuple[int, str]] = None) -> List[ServiceInfo]:
        """Run service fingerprinting on open ports"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_service_fingerprinting(host, ports or [])
        
        if not ports:
            # Get ports from previous scan
            for target in self.targets.values():
                if host in target.port_scans:
                    ports = target.port_scans[host].open_ports
                    break
            
            if not ports:
                self.logger.warning(f"No open ports found for {host}, run port scan first")
                return []
        
        services = []
        for port, service in ports:
            service_info = self.fingerprinter.fingerprint_service(host, port, service)
            services.append(service_info)
        
        # Update target information
        for target in self.targets.values():
            if host == target.target or (target.subdomains and host in target.subdomains.subdomains):
                target.services.extend(services)
                target.last_updated = datetime.now()
                break
        
        self.logger.info(f"Service fingerprinting completed for {host}: {len(services)} services")
        return services
    
    @handle_errors
    def run_full_reconnaissance(self, target: str, subdomain_methods: List[str] = None, 
                              port_range: str = "top1000") -> ReconTarget:
        """Run complete reconnaissance on a target"""
        self.logger.info(f"Starting full reconnaissance on {target}")
        
        recon_target = self.add_target(target)
        
        # Step 1: Subdomain enumeration
        subdomain_result = self.run_subdomain_enumeration(target, subdomain_methods)
        
        # Step 2: Port scanning on main domain and subdomains
        hosts_to_scan = [target]
        if subdomain_result.subdomains:
            hosts_to_scan.extend(list(subdomain_result.subdomains)[:10])  # Limit to top 10
        
        for host in hosts_to_scan:
            try:
                port_result = self.run_port_scan(host, port_range)
                if port_result.open_ports:
                    # Step 3: Service fingerprinting
                    self.run_service_fingerprinting(host, port_result.open_ports)
            except Exception as e:
                self.logger.error(f"Error scanning {host}: {e}")
        
        recon_target.last_updated = datetime.now()
        
        # Save complete reconnaissance data
        self.save_target_data(target)
        
        self.logger.info(f"Full reconnaissance completed for {target}")
        return recon_target
    
    @handle_errors
    def save_target_data(self, target: str):
        """Save complete target reconnaissance data"""
        if target not in self.targets:
            return
        
        recon_target = self.targets[target]
        output_file = self.output_dir / f"full_recon_{target}_{int(time.time())}.json"
        
        data = {
            'target': target,
            'created_at': recon_target.created_at.isoformat(),
            'last_updated': recon_target.last_updated.isoformat(),
            'subdomains': {
                'domain': recon_target.subdomains.domain if recon_target.subdomains else None,
                'subdomains': list(recon_target.subdomains.subdomains) if recon_target.subdomains else [],
                'sources': {k: list(v) for k, v in recon_target.subdomains.sources.items()} if recon_target.subdomains else {}
            },
            'port_scans': {
                host: {
                    'open_ports': scan.open_ports,
                    'closed_ports': scan.closed_ports,
                    'filtered_ports': scan.filtered_ports,
                    'scan_duration': scan.scan_duration,
                    'timestamp': scan.timestamp.isoformat()
                } for host, scan in recon_target.port_scans.items()
            },
            'services': [
                {
                    'host': service.host,
                    'port': service.port,
                    'service': service.service,
                    'version': service.version,
                    'banner': service.banner,
                    'ssl_info': service.ssl_info,
                    'headers': service.headers,
                    'timestamp': service.timestamp.isoformat()
                } for service in recon_target.services
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Target data saved to {output_file}")
    
    @handle_errors
    def get_target_summary(self, target: str) -> Dict[str, Any]:
        """Get summary of reconnaissance results"""
        if target not in self.targets:
            return {}
        
        recon_target = self.targets[target]
        
        summary = {
            'target': target,
            'last_updated': recon_target.last_updated.isoformat(),
            'subdomains_count': len(recon_target.subdomains.subdomains) if recon_target.subdomains else 0,
            'hosts_scanned': len(recon_target.port_scans),
            'total_open_ports': sum(len(scan.open_ports) for scan in recon_target.port_scans.values()),
            'services_identified': len(recon_target.services),
            'web_services': len([s for s in recon_target.services if s.service.lower() in ['http', 'https']]),
            'ssl_services': len([s for s in recon_target.services if s.ssl_info])
        }
        
        return summary


# Global reconnaissance manager instance
_recon_manager = None

def get_reconnaissance_manager() -> ReconnaissanceManager:
    """Get global reconnaissance manager instance"""
    global _recon_manager
    if _recon_manager is None:
        _recon_manager = ReconnaissanceManager()
    return _recon_manager