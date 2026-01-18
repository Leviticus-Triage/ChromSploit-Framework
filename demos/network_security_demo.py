#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Network Security Demo
Demonstrates the new network security features
For Educational and Authorized Penetration Testing
"""

import os
import sys
import time
import logging
from typing import Dict, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import NetworkSecurityManager, RateLimiter, ExponentialBackoff
from core.path_utils import PathUtils
from core.colors import Colors

def setup_demo_logger() -> logging.Logger:
 """Setup logger for demo"""
 logger = logging.getLogger('network_security_demo')
 logger.setLevel(logging.INFO)
 
 # Create console handler
 handler = logging.StreamHandler()
 handler.setLevel(logging.INFO)
 
 # Create formatter
 formatter = logging.Formatter(
 f'{Colors.CYAN}%(asctime)s{Colors.RESET} - '
 f'{Colors.YELLOW}%(name)s{Colors.RESET} - '
 f'{Colors.GREEN}%(levelname)s{Colors.RESET} - '
 f'%(message)s'
 )
 handler.setFormatter(formatter)
 
 logger.addHandler(handler)
 return logger

def demo_rate_limiting():
 """Demonstrate rate limiting functionality"""
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Rate Limiting Demo ==={Colors.RESET}")
 
 # Create a rate limiter: 3 requests per 5 seconds
 limiter = RateLimiter(max_requests=3, time_window=5)
 
 print(f"{Colors.BLUE}Testing rate limiter (3 requests per 5 seconds):{Colors.RESET}")
 
 for i in range(6):
 if limiter.is_allowed():
 print(f"{Colors.GREEN} Request {i+1}: Allowed{Colors.RESET}")
 else:
 wait_time = limiter.wait_time()
 print(f"{Colors.YELLOW}⏸ Request {i+1}: Rate limited! "
 f"Wait {wait_time:.1f} seconds{Colors.RESET}")
 break
 
 print(f"\n{Colors.BLUE}Waiting for rate limit to reset...{Colors.RESET}")
 time.sleep(2)
 
 if limiter.is_allowed():
 print(f"{Colors.GREEN} Request after wait: Allowed{Colors.RESET}")

def demo_exponential_backoff():
 """Demonstrate exponential backoff"""
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Exponential Backoff Demo ==={Colors.RESET}")
 
 backoff = ExponentialBackoff(base_delay=0.5, max_delay=4.0, multiplier=2.0)
 
 print(f"{Colors.BLUE}Simulating failed requests with exponential backoff:{Colors.RESET}")
 
 for attempt in range(5):
 delay = backoff.get_delay()
 print(f"{Colors.YELLOW} Attempt {attempt+1}: Wait {delay:.1f} seconds{Colors.RESET}")
 if attempt < 4: # Don't actually wait on the last attempt
 time.sleep(min(delay, 1.0)) # Cap sleep for demo purposes
 
 print(f"{Colors.BLUE}Resetting backoff...{Colors.RESET}")
 backoff.reset()
 delay = backoff.get_delay()
 print(f"{Colors.GREEN} After reset: Wait {delay:.1f} seconds{Colors.RESET}")

def demo_network_security_manager():
 """Demonstrate NetworkSecurityManager features"""
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Network Security Manager Demo ==={Colors.RESET}")
 
 logger = setup_demo_logger()
 security_manager = NetworkSecurityManager(logger=logger)
 
 # Demo 1: URL validation
 print(f"\n{Colors.BLUE}1. URL Validation:{Colors.RESET}")
 test_urls = [
 ('https://httpbin.org/get', 'Valid HTTPS URL'),
 ('http://httpbin.org/get', 'Valid HTTP URL'),
 ('ftp://example.com/file', 'Invalid FTP URL'),
 ('javascript:alert(1)', 'Malicious JavaScript URL'),
 ('https://127.0.0.1/admin', 'Internal IP URL (blocked)')
 ]
 
 for url, description in test_urls:
 is_valid = security_manager.is_valid_url(url)
 status = f"{Colors.GREEN} Valid" if is_valid else f"{Colors.RED} Invalid"
 print(f" {status}{Colors.RESET} - {description}: {url}")
 
 # Demo 2: Security headers
 print(f"\n{Colors.BLUE}2. Security Headers:{Colors.RESET}")
 headers = security_manager.get_security_headers()
 for header, value in headers.items():
 print(f" {Colors.CYAN}{header}{Colors.RESET}: {value}")
 
 # Demo 3: CSRF token generation and validation
 print(f"\n{Colors.BLUE}3. CSRF Token Security:{Colors.RESET}")
 secret_key = "demo_secret_key_12345"
 
 # Generate token
 csrf_token = security_manager.generate_csrf_token(secret_key)
 print(f" Generated token: {Colors.CYAN}{csrf_token[:20]}...{Colors.RESET}")
 
 # Validate token
 is_valid = security_manager.validate_csrf_token(csrf_token, secret_key)
 status = f"{Colors.GREEN} Valid" if is_valid else f"{Colors.RED} Invalid"
 print(f" Token validation: {status}{Colors.RESET}")
 
 # Test with wrong secret
 is_valid_wrong = security_manager.validate_csrf_token(csrf_token, "wrong_secret")
 status = f"{Colors.GREEN} Valid" if is_valid_wrong else f"{Colors.RED} Invalid"
 print(f" Wrong secret validation: {status}{Colors.RESET} (should be invalid)")
 
 # Demo 4: Rate limited function
 print(f"\n{Colors.BLUE}4. Rate Limited Function:{Colors.RESET}")
 
 @security_manager.rate_limit(name='demo_function', max_requests=2, time_window=3)
 def demo_api_call(data: str) -> str:
 return f"Processed: {data}"
 
 try:
 print(f" {Colors.GREEN} Call 1: {demo_api_call('data1')}{Colors.RESET}")
 print(f" {Colors.GREEN} Call 2: {demo_api_call('data2')}{Colors.RESET}")
 print(f" {Colors.YELLOW}⏸ Call 3: {demo_api_call('data3')}{Colors.RESET}")
 except Exception as e:
 print(f" {Colors.RED} Call 3 failed: {e}{Colors.RESET}")

def demo_path_security():
 """Demonstrate enhanced path security features"""
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Path Security Demo ==={Colors.RESET}")
 
 # Demo 1: Path traversal detection
 print(f"\n{Colors.BLUE}1. Path Traversal Detection:{Colors.RESET}")
 test_paths = [
 ('normal_file.txt', 'Normal file path'),
 ('data/reports/output.html', 'Nested safe path'),
 ('../../../etc/passwd', 'Path traversal attack'),
 ('file.txt\x00.exe', 'Null byte injection'),
 ('%2e%2e/%2e%2e/etc/passwd', 'URL-encoded traversal'),
 ('//network/share/file', 'Network path injection')
 ]
 
 for path, description in test_paths:
 is_safe = PathUtils.is_safe_path(path)
 status = f"{Colors.GREEN} Safe" if is_safe else f"{Colors.RED} Unsafe"
 print(f" {status}{Colors.RESET} - {description}: {path}")
 
 # Demo 2: Filename sanitization
 print(f"\n{Colors.BLUE}2. Filename Sanitization:{Colors.RESET}")
 dangerous_filenames = [
 'normal_file.txt',
 'file<with>dangerous:chars.txt',
 'file|with*wildcards?.txt',
 'CON.txt', # Reserved Windows name
 ' .hidden_file.txt ', # Leading/trailing chars
 'very_long_filename' + 'x' * 250 + '.txt' # Too long
 ]
 
 for filename in dangerous_filenames:
 sanitized = PathUtils.sanitize_filename(filename)
 print(f" {Colors.CYAN}Original{Colors.RESET}: {filename[:50]}{'...' if len(filename) > 50 else ''}")
 print(f" {Colors.GREEN}Sanitized{Colors.RESET}: {sanitized}")
 print()
 
 # Demo 3: File type validation
 print(f"\n{Colors.BLUE}3. File Type Validation:{Colors.RESET}")
 test_files = [
 ('document.txt', 'Text file'),
 ('report.html', 'HTML file'),
 ('data.json', 'JSON file'),
 ('certificate.pem', 'Certificate file'),
 ('malware.exe', 'Executable file'),
 ('script.bat', 'Batch script'),
 ('virus.scr', 'Screensaver file')
 ]
 
 for filename, description in test_files:
 is_allowed = PathUtils.is_allowed_file_type(filename)
 status = f"{Colors.GREEN} Allowed" if is_allowed else f"{Colors.RED} Blocked"
 print(f" {status}{Colors.RESET} - {description}: {filename}")
 
 # Demo 4: Secure temporary path
 print(f"\n{Colors.BLUE}4. Secure Temporary Paths:{Colors.RESET}")
 for i in range(3):
 temp_path = PathUtils.get_secure_temp_path('demo_', '.tmp')
 print(f" {Colors.CYAN}Temp path {i+1}{Colors.RESET}: {temp_path}")

def demo_secure_requests():
 """Demonstrate secure HTTP requests"""
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Secure HTTP Requests Demo ==={Colors.RESET}")
 
 logger = setup_demo_logger()
 security_manager = NetworkSecurityManager(logger=logger)
 
 print(f"{Colors.BLUE}Making secure HTTP request to httpbin.org...{Colors.RESET}")
 
 try:
 # Make a secure request
 response = security_manager.secure_request('GET', 'https://httpbin.org/headers')
 
 if response.status_code == 200:
 print(f"{Colors.GREEN} Request successful!{Colors.RESET}")
 print(f" Status Code: {response.status_code}")
 print(f" Response Headers: {len(response.headers)} headers received")
 
 # Show some security headers if present
 security_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'Strict-Transport-Security']
 for header in security_headers:
 if header in response.headers:
 print(f" {Colors.CYAN}{header}{Colors.RESET}: {response.headers[header]}")
 else:
 print(f"{Colors.YELLOW} Request returned status: {response.status_code}{Colors.RESET}")
 
 except Exception as e:
 print(f"{Colors.RED} Request failed: {e}{Colors.RESET}")
 
 # Demo SSL verification
 print(f"\n{Colors.BLUE}Testing SSL verification (this should fail for self-signed certs):{Colors.RESET}")
 try:
 # This would fail for a self-signed certificate
 response = security_manager.secure_request('GET', 'https://self-signed.badssl.com/')
 print(f"{Colors.YELLOW} Unexpected success with self-signed cert{Colors.RESET}")
 except Exception as e:
 print(f"{Colors.GREEN} SSL verification working: {type(e).__name__}{Colors.RESET}")

def main():
 """Main demo function"""
 print(f"{Colors.BOLD}{Colors.CYAN}")
 print("ChromSploit Framework v2.0")
 print("Network Security Enhancements Demo")
 print("For Educational and Authorized Penetration Testing")
 print("=" * 60)
 print(f"{Colors.RESET}")
 
 demos = [
 ("Rate Limiting", demo_rate_limiting),
 ("Exponential Backoff", demo_exponential_backoff),
 ("Network Security Manager", demo_network_security_manager),
 ("Path Security", demo_path_security),
 ("Secure HTTP Requests", demo_secure_requests)
 ]
 
 for demo_name, demo_func in demos:
 try:
 demo_func()
 except KeyboardInterrupt:
 print(f"\n{Colors.YELLOW}Demo interrupted by user{Colors.RESET}")
 break
 except Exception as e:
 print(f"\n{Colors.RED}Error in {demo_name} demo: {e}{Colors.RESET}")
 continue
 
 print(f"\n{Colors.BOLD}{Colors.CYAN}=== Demo Complete ==={Colors.RESET}")
 print(f"{Colors.BLUE}The ChromSploit Framework now includes comprehensive network security features:{Colors.RESET}")
 print(f" • {Colors.GREEN}Rate limiting for network requests{Colors.RESET}")
 print(f" • {Colors.GREEN}Exponential backoff for failed requests{Colors.RESET}")
 print(f" • {Colors.GREEN}Enhanced path validation and sanitization{Colors.RESET}")
 print(f" • {Colors.GREEN}Secure HTTP headers for web interfaces{Colors.RESET}")
 print(f" • {Colors.GREEN}Proper SSL/TLS certificate validation{Colors.RESET}")
 print(f" • {Colors.GREEN}CSRF token generation and validation{Colors.RESET}")
 print(f" • {Colors.GREEN}Connection timeouts and security monitoring{Colors.RESET}")

if __name__ == '__main__':
 main()