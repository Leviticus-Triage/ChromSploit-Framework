#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Utility-Funktionen für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import re
import shutil
import socket
import random
import string
import platform
import subprocess
import time
import ssl
import urllib3
import requests
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock
from urllib.parse import urlparse
import hashlib
import hmac

class Utils:
    """
    Allgemeine Utility-Funktionen für das ChromSploit Framework
    """
    
    @staticmethod
    def is_tool_available(tool_name: str) -> bool:
        """
        Überprüft, ob ein Tool im System verfügbar ist
        
        Args:
            tool_name (str): Name des Tools
            
        Returns:
            bool: True, wenn das Tool verfügbar ist, sonst False
        """
        return shutil.which(tool_name) is not None
    
    @staticmethod
    def get_ip_address() -> str:
        """
        Ermittelt die IP-Adresse des Systems
        
        Returns:
            str: Die IP-Adresse oder '127.0.0.1' bei Fehler
        """
        # Method 1: Try to connect to external DNS and get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip and ip != '0.0.0.0':
                return ip
        except:
            pass
        
        # Method 2: Get hostname and resolve it
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip and not ip.startswith('127.'):
                return ip
        except:
            pass
        
        # Method 3: Parse network interfaces (Linux specific)
        try:
            import subprocess
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                import re
                # Find all IPs that are not loopback
                ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
                for ip in ips:
                    if not ip.startswith('127.') and not ip.startswith('169.254.'):
                        return ip
        except:
            pass
        
        # Method 4: Use netifaces if available
        try:
            import netifaces
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr['addr']
                        if not ip.startswith('127.') and not ip.startswith('169.254.'):
                            return ip
        except ImportError:
            pass
        
        # Fallback to localhost
        return "127.0.0.1"
    
    @staticmethod
    def check_port_available(port: int, host: str = '127.0.0.1') -> bool:
        """
        Überprüft, ob ein Port verfügbar ist
        
        Args:
            port (int): Die zu überprüfende Portnummer
            host (str, optional): Der Host, auf dem der Port überprüft werden soll
            
        Returns:
            bool: True, wenn der Port verfügbar ist, sonst False
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((host, port))
            s.close()
            return result != 0
        except:
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 8000, end_port: int = 9000, host: str = '127.0.0.1') -> int:
        """
        Findet einen verfügbaren Port im angegebenen Bereich
        
        Args:
            start_port (int, optional): Startport für die Suche
            end_port (int, optional): Endport für die Suche
            host (str, optional): Der Host, auf dem der Port überprüft werden soll
            
        Returns:
            int: Ein verfügbarer Port oder -1, wenn kein Port verfügbar ist
        """
        for port in range(start_port, end_port + 1):
            if Utils.check_port_available(port, host):
                return port
        return -1
    
    @staticmethod
    def generate_random_string(length: int = 10, include_special: bool = False) -> str:
        """
        Generiert einen zufälligen String
        
        Args:
            length (int, optional): Länge des zu generierenden Strings
            include_special (bool, optional): Ob Sonderzeichen eingeschlossen werden sollen
            
        Returns:
            str: Der generierte zufällige String
        """
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def execute_command(command: str, timeout: int = 60, shell: bool = True) -> Tuple[int, str, str]:
        """
        Führt einen Befehl aus und gibt das Ergebnis zurück
        
        Args:
            command (str): Der auszuführende Befehl
            timeout (int, optional): Timeout in Sekunden
            shell (bool, optional): Ob der Befehl in einer Shell ausgeführt werden soll
            
        Returns:
            tuple: (Rückgabecode, Standardausgabe, Standardfehlerausgabe)
        """
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=shell,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Timeout expired"
        except Exception as e:
            return -1, "", str(e)
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Überprüft, ob eine IP-Adresse gültig ist
        
        Args:
            ip (str): Die zu überprüfende IP-Adresse
            
        Returns:
            bool: True, wenn die IP-Adresse gültig ist, sonst False
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        # Überprüfen, ob jedes Oktett im gültigen Bereich liegt
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    
    @staticmethod
    def is_valid_port(port: Union[str, int]) -> bool:
        """
        Überprüft, ob ein Port gültig ist
        
        Args:
            port (Union[str, int]): Der zu überprüfende Port
            
        Returns:
            bool: True, wenn der Port gültig ist, sonst False
        """
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except:
            return False
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Gibt einen formatierten Zeitstempel zurück
        
        Returns:
            str: Der formatierte Zeitstempel
        """
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """
        Sammelt Informationen über das System
        
        Returns:
            dict: Systeminformationen
        """
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'ip_address': Utils.get_ip_address(),
            'python_version': platform.python_version()
        }
        
        # Linux-spezifische Informationen
        if platform.system() == 'Linux':
            try:
                # Kernel-Version
                kernel = subprocess.check_output(['uname', '-r']).decode().strip()
                info['kernel'] = kernel
                
                # Distribution
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release', 'r') as f:
                        os_release = f.read()
                        
                    # Name der Distribution
                    match = re.search(r'PRETTY_NAME="([^"]+)"', os_release)
                    if match:
                        info['distribution'] = match.group(1)
                
                # CPU-Informationen
                if os.path.exists('/proc/cpuinfo'):
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                    
                    # CPU-Modell
                    match = re.search(r'model name\s+:\s+(.+)', cpuinfo)
                    if match:
                        info['cpu_model'] = match.group(1)
                    
                    # CPU-Kerne
                    cores = len(re.findall(r'processor\s+:', cpuinfo))
                    info['cpu_cores'] = str(cores)
                
                # Arbeitsspeicher
                if os.path.exists('/proc/meminfo'):
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                    
                    # Gesamter Arbeitsspeicher
                    match = re.search(r'MemTotal:\s+(\d+)', meminfo)
                    if match:
                        mem_total = int(match.group(1)) // 1024
                        info['memory_total'] = f"{mem_total} MB"
            except:
                pass
        
        return info
    
    @staticmethod
    def format_bytes(size: int) -> str:
        """
        Formatiert eine Bytegröße in eine lesbare Form
        
        Args:
            size (int): Die Größe in Bytes
            
        Returns:
            str: Die formatierte Größe
        """
        power = 2**10
        n = 0
        power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        
        while size > power and n < 4:
            size /= power
            n += 1
        
        return f"{size:.2f} {power_labels[n]}"
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Überprüft, ob ein Prozess läuft
        
        Args:
            process_name (str): Name des Prozesses
            
        Returns:
            bool: True, wenn der Prozess läuft, sonst False
        """
        if platform.system() == 'Windows':
            output = subprocess.check_output('tasklist', shell=True).decode()
            return process_name.lower() in output.lower()
        else:
            try:
                output = subprocess.check_output(['pgrep', '-f', process_name]).decode()
                return bool(output.strip())
            except:
                return False
    
    @staticmethod
    def kill_process(process_name: str) -> bool:
        """
        Beendet einen Prozess
        
        Args:
            process_name (str): Name des Prozesses
            
        Returns:
            bool: True, wenn der Prozess beendet wurde, sonst False
        """
        try:
            if platform.system() == 'Windows':
                subprocess.call(['taskkill', '/F', '/IM', process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.call(['pkill', '-f', process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False


class RateLimiter:
    """
    Rate limiter implementation using token bucket algorithm
    """
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = Lock()
    
    def is_allowed(self) -> bool:
        """
        Check if request is allowed under rate limit
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def wait_time(self) -> float:
        """
        Get time to wait before next request is allowed
        
        Returns:
            float: Seconds to wait
        """
        with self.lock:
            if not self.requests:
                return 0
            
            oldest_request = min(self.requests)
            return max(0, self.time_window - (time.time() - oldest_request))


class ExponentialBackoff:
    """
    Exponential backoff implementation for retry logic
    """
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, 
                 multiplier: float = 2.0, jitter: bool = True):
        """
        Initialize exponential backoff
        
        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            multiplier: Backoff multiplier
            jitter: Add random jitter to prevent thundering herd
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self.attempt = 0
    
    def get_delay(self) -> float:
        """
        Get delay for current attempt
        
        Returns:
            float: Delay in seconds
        """
        delay = min(self.base_delay * (self.multiplier ** self.attempt), 
                   self.max_delay)
        
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)  # Add ±25% jitter
        
        self.attempt += 1
        return delay
    
    def reset(self):
        """Reset attempt counter"""
        self.attempt = 0


class NetworkSecurityManager:
    """
    Network Security Manager for ChromSploit Framework
    Implements rate limiting, request throttling, secure headers, and SSL validation
    """
    
    def __init__(self, logger=None):
        """
        Initialize Network Security Manager
        
        Args:
            logger: Logger instance for security events
        """
        self.logger = logger
        self.rate_limiters = {}
        self.failed_requests = {}
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        self.default_timeouts = {
            'connect': 10,
            'read': 30,
            'total': 60
        }
        
        # Disable urllib3 warnings for unverified HTTPS requests
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def create_rate_limiter(self, name: str, max_requests: int = 100, 
                          time_window: int = 60) -> RateLimiter:
        """
        Create or get rate limiter for specific endpoint
        
        Args:
            name: Rate limiter name/identifier
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
            
        Returns:
            RateLimiter: Rate limiter instance
        """
        if name not in self.rate_limiters:
            self.rate_limiters[name] = RateLimiter(max_requests, time_window)
        return self.rate_limiters[name]
    
    def rate_limit(self, name: str = 'default', max_requests: int = 100, 
                  time_window: int = 60):
        """
        Rate limiting decorator
        
        Args:
            name: Rate limiter name
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                limiter = self.create_rate_limiter(name, max_requests, time_window)
                
                if not limiter.is_allowed():
                    wait_time = limiter.wait_time()
                    if self.logger:
                        self.logger.warning(f"Rate limit exceeded for {name}. "
                                          f"Wait {wait_time:.2f} seconds")
                    raise Exception(f"Rate limit exceeded. Wait {wait_time:.2f} seconds")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def retry_with_backoff(self, max_retries: int = 3, base_delay: float = 1.0,
                          max_delay: float = 60.0):
        """
        Retry decorator with exponential backoff
        
        Args:
            max_retries: Maximum number of retries
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                backoff = ExponentialBackoff(base_delay, max_delay)
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries:
                            if self.logger:
                                self.logger.error(f"Function {func.__name__} failed "
                                                f"after {max_retries} retries: {e}")
                            raise
                        
                        delay = backoff.get_delay()
                        if self.logger:
                            self.logger.warning(f"Attempt {attempt + 1} failed for "
                                              f"{func.__name__}: {e}. "
                                              f"Retrying in {delay:.2f} seconds")
                        time.sleep(delay)
                
            return wrapper
        return decorator
    
    def create_secure_session(self, verify_ssl: bool = True, 
                            client_cert: Optional[Tuple[str, str]] = None) -> requests.Session:
        """
        Create secure requests session with proper SSL configuration
        
        Args:
            verify_ssl: Whether to verify SSL certificates
            client_cert: Optional client certificate (cert_file, key_file)
            
        Returns:
            requests.Session: Configured session
        """
        session = requests.Session()
        
        # Set timeouts
        session.request = self._add_timeout(session.request)
        
        # SSL configuration
        session.verify = verify_ssl
        if client_cert:
            session.cert = client_cert
        
        # Add security headers
        session.headers.update({
            'User-Agent': 'ChromSploit-Framework/2.0 (Security Testing Tool)',
            **self.security_headers
        })
        
        # Configure SSL context for more security
        if verify_ssl:
            session.mount('https://', self._create_ssl_adapter())
        
        return session
    
    def _create_ssl_adapter(self) -> requests.adapters.HTTPAdapter:
        """
        Create SSL adapter with secure configuration
        
        Returns:
            HTTPAdapter: Configured SSL adapter
        """
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Disable weak ciphers
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        class SecureHTTPSAdapter(requests.adapters.HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs['ssl_context'] = ssl_context
                kwargs['socket_options'] = [
                    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                    (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60),
                    (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
                    (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)
                ]
                return super().init_poolmanager(*args, **kwargs)
        
        adapter = SecureHTTPSAdapter()
        
        return adapter
    
    def _add_timeout(self, request_func: Callable) -> Callable:
        """
        Add timeout to request function
        
        Args:
            request_func: Original request function
            
        Returns:
            Callable: Wrapped function with timeout
        """
        @wraps(request_func)
        def wrapper(*args, **kwargs):
            if 'timeout' not in kwargs:
                kwargs['timeout'] = (
                    self.default_timeouts['connect'],
                    self.default_timeouts['read']
                )
            return request_func(*args, **kwargs)
        return wrapper
    
    def secure_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make secure HTTP request with all security features enabled
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response: Response object
        """
        session = self.create_secure_session()
        
        # Validate URL
        if not self.is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Log security event
        if self.logger:
            self.logger.info(f"Making secure {method} request to {url}")
        
        try:
            response = session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        
        except requests.exceptions.SSLError as e:
            if self.logger:
                self.logger.error(f"SSL verification failed for {url}: {e}")
            raise
        except requests.exceptions.Timeout as e:
            if self.logger:
                self.logger.error(f"Request timeout for {url}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"Request failed for {url}: {e}")
            raise
        finally:
            session.close()
    
    def is_valid_url(self, url: str) -> bool:
        """
        Validate URL format and security
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is valid and secure
        """
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check hostname
            if not parsed.hostname:
                return False
            
            # Prevent SSRF to internal networks
            if self._is_internal_ip(parsed.hostname):
                if self.logger:
                    self.logger.warning(f"Blocked request to internal IP: {parsed.hostname}")
                return False
            
            return True
        except Exception:
            return False
    
    def _is_internal_ip(self, hostname: str) -> bool:
        """
        Check if hostname resolves to internal IP
        
        Args:
            hostname: Hostname to check
            
        Returns:
            bool: True if internal IP
        """
        try:
            ip = socket.gethostbyname(hostname)
            return (
                ip.startswith('127.') or
                ip.startswith('10.') or
                ip.startswith('192.168.') or
                ip.startswith('172.16.') or
                ip.startswith('172.17.') or
                ip.startswith('172.18.') or
                ip.startswith('172.19.') or
                ip.startswith('172.20.') or
                ip.startswith('172.21.') or
                ip.startswith('172.22.') or
                ip.startswith('172.23.') or
                ip.startswith('172.24.') or
                ip.startswith('172.25.') or
                ip.startswith('172.26.') or
                ip.startswith('172.27.') or
                ip.startswith('172.28.') or
                ip.startswith('172.29.') or
                ip.startswith('172.30.') or
                ip.startswith('172.31.') or
                ip == '0.0.0.0'
            )
        except socket.gaierror:
            return True  # Err on the side of caution
    
    def generate_csrf_token(self, secret_key: str) -> str:
        """
        Generate CSRF token
        
        Args:
            secret_key: Secret key for token generation
            
        Returns:
            str: CSRF token
        """
        timestamp = str(int(time.time()))
        message = f"{timestamp}:{random.randint(100000, 999999)}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{message}:{signature}"
    
    def validate_csrf_token(self, token: str, secret_key: str, 
                          max_age: int = 3600) -> bool:
        """
        Validate CSRF token
        
        Args:
            token: Token to validate
            secret_key: Secret key used for generation
            max_age: Maximum token age in seconds
            
        Returns:
            bool: True if token is valid
        """
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            timestamp, nonce, signature = parts
            
            # Check age
            if int(time.time()) - int(timestamp) > max_age:
                return False
            
            # Verify signature
            message = f"{timestamp}:{nonce}"
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except (ValueError, IndexError):
            return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for web interfaces
        
        Returns:
            Dict[str, str]: Security headers
        """
        return self.security_headers.copy()
    
    def update_security_headers(self, headers: Dict[str, str]):
        """
        Update security headers
        
        Args:
            headers: Headers to add/update
        """
        self.security_headers.update(headers)
    
    def set_timeouts(self, connect: int = 10, read: int = 30, total: int = 60):
        """
        Set default timeouts for network operations
        
        Args:
            connect: Connection timeout in seconds
            read: Read timeout in seconds
            total: Total timeout in seconds
        """
        self.default_timeouts = {
            'connect': connect,
            'read': read,
            'total': total
        }
    
    def log_security_event(self, event_type: str, details: str):
        """
        Log security event
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        if self.logger:
            self.logger.warning(f"SECURITY EVENT [{event_type}]: {details}")
