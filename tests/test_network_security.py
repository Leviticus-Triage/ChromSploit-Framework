#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Network Security Manager Tests
For Educational and Authorized Penetration Testing
"""

import unittest
import tempfile
import os
import time
from unittest.mock import Mock, patch
import sys

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import NetworkSecurityManager, RateLimiter, ExponentialBackoff
from core.path_utils import PathUtils


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality"""
    
    def setUp(self):
        self.limiter = RateLimiter(max_requests=3, time_window=1)
    
    def test_rate_limiting_basic(self):
        """Test basic rate limiting"""
        # First 3 requests should be allowed
        self.assertTrue(self.limiter.is_allowed())
        self.assertTrue(self.limiter.is_allowed())
        self.assertTrue(self.limiter.is_allowed())
        
        # 4th request should be denied
        self.assertFalse(self.limiter.is_allowed())
    
    def test_rate_limiting_time_window(self):
        """Test rate limiting with time window"""
        # Use up all requests
        for _ in range(3):
            self.assertTrue(self.limiter.is_allowed())
        
        # Should be denied
        self.assertFalse(self.limiter.is_allowed())
        
        # Wait for time window to reset
        time.sleep(1.1)
        
        # Should be allowed again
        self.assertTrue(self.limiter.is_allowed())
    
    def test_wait_time(self):
        """Test wait time calculation"""
        # Use up all requests
        for _ in range(3):
            self.limiter.is_allowed()
        
        wait_time = self.limiter.wait_time()
        self.assertGreater(wait_time, 0)
        self.assertLessEqual(wait_time, 1)


class TestExponentialBackoff(unittest.TestCase):
    """Test exponential backoff functionality"""
    
    def setUp(self):
        self.backoff = ExponentialBackoff(base_delay=1.0, max_delay=8.0, multiplier=2.0, jitter=False)
    
    def test_exponential_increase(self):
        """Test exponential delay increase"""
        delay1 = self.backoff.get_delay()
        delay2 = self.backoff.get_delay()
        delay3 = self.backoff.get_delay()
        
        self.assertEqual(delay1, 1.0)
        self.assertEqual(delay2, 2.0)
        self.assertEqual(delay3, 4.0)
    
    def test_max_delay_cap(self):
        """Test maximum delay cap"""
        # Get enough delays to exceed max
        for _ in range(5):
            delay = self.backoff.get_delay()
        
        self.assertLessEqual(delay, 8.0)
    
    def test_reset(self):
        """Test backoff reset"""
        self.backoff.get_delay()  # First delay
        self.backoff.get_delay()  # Second delay
        
        self.backoff.reset()
        
        delay = self.backoff.get_delay()
        self.assertEqual(delay, 1.0)


class TestNetworkSecurityManager(unittest.TestCase):
    """Test network security manager functionality"""
    
    def setUp(self):
        self.logger = Mock()
        self.security_manager = NetworkSecurityManager(logger=self.logger)
    
    def test_url_validation_valid(self):
        """Test valid URL validation"""
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://api.example.com/v1/test',
            'http://192.168.1.100:8080/test'
        ]
        
        for url in valid_urls:
            with patch('socket.gethostbyname', return_value='93.184.216.34'):  # example.com IP
                self.assertTrue(self.security_manager.is_valid_url(url), f"URL should be valid: {url}")
    
    def test_url_validation_invalid(self):
        """Test invalid URL validation"""
        invalid_urls = [
            'ftp://example.com',
            'javascript:alert(1)',
            'file:///etc/passwd',
            'data:text/html,<script>alert(1)</script>',
            ''
        ]
        
        for url in invalid_urls:
            self.assertFalse(self.security_manager.is_valid_url(url), f"URL should be invalid: {url}")
    
    def test_internal_ip_detection(self):
        """Test internal IP detection"""
        internal_ips = [
            '127.0.0.1',
            '10.0.0.1',
            '192.168.1.1',
            '172.16.0.1',
            '0.0.0.0'
        ]
        
        for ip in internal_ips:
            self.assertTrue(self.security_manager._is_internal_ip(ip), f"IP should be internal: {ip}")
        
        # Test external IP
        external_ip = '8.8.8.8'
        self.assertFalse(self.security_manager._is_internal_ip(external_ip))
    
    def test_csrf_token_generation_validation(self):
        """Test CSRF token generation and validation"""
        secret_key = "test_secret_key_12345"
        
        # Generate token
        token = self.security_manager.generate_csrf_token(secret_key)
        self.assertIsInstance(token, str)
        self.assertIn(':', token)
        
        # Validate token
        self.assertTrue(self.security_manager.validate_csrf_token(token, secret_key))
        
        # Test with wrong secret
        self.assertFalse(self.security_manager.validate_csrf_token(token, "wrong_secret"))
        
        # Test with malformed token
        self.assertFalse(self.security_manager.validate_csrf_token("invalid:token", secret_key))
    
    def test_security_headers(self):
        """Test security headers"""
        headers = self.security_manager.get_security_headers()
        
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        for header in expected_headers:
            self.assertIn(header, headers)
    
    @patch('requests.Session')
    def test_secure_session_creation(self, mock_session):
        """Test secure session creation"""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        session = self.security_manager.create_secure_session()
        
        # Verify session was created
        mock_session.assert_called_once()
        
        # Verify SSL verification is enabled by default
        self.assertEqual(mock_session_instance.verify, True)
    
    def test_rate_limiting_decorator(self):
        """Test rate limiting decorator"""
        @self.security_manager.rate_limit(name='test', max_requests=2, time_window=1)
        def test_function():
            return "success"
        
        # First two calls should succeed
        self.assertEqual(test_function(), "success")
        self.assertEqual(test_function(), "success")
        
        # Third call should fail with rate limit
        with self.assertRaises(Exception) as context:
            test_function()
        
        self.assertIn("Rate limit exceeded", str(context.exception))
    
    def test_timeout_configuration(self):
        """Test timeout configuration"""
        self.security_manager.set_timeouts(connect=5, read=15, total=30)
        
        timeouts = self.security_manager.default_timeouts
        self.assertEqual(timeouts['connect'], 5)
        self.assertEqual(timeouts['read'], 15)
        self.assertEqual(timeouts['total'], 30)


class TestPathUtilsSecurity(unittest.TestCase):
    """Test enhanced path utilities security features"""
    
    def test_path_traversal_detection(self):
        """Test path traversal attack detection"""
        dangerous_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/%2e%2e/%2e%2e/%2e%2e/etc/passwd',
            '/var/www/html/../../../etc/passwd',
            'file.txt\x00.exe',
            'normal_file.txt\r\nmalicious_content',
            '//example.com/share/file.txt'
        ]
        
        for path in dangerous_paths:
            self.assertFalse(PathUtils.is_safe_path(path), f"Path should be unsafe: {path}")
    
    def test_safe_path_validation(self):
        """Test safe path validation"""
        safe_paths = [
            'normal_file.txt',
            'folder/file.txt',
            'data/output/report.html',
            'logs/chromsploit.log'
        ]
        
        for path in safe_paths:
            self.assertTrue(PathUtils.is_safe_path(path), f"Path should be safe: {path}")
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        test_cases = [
            ('normal_file.txt', 'normal_file.txt'),
            ('file<with>dangerous:chars.txt', 'file_with_dangerous_chars.txt'),
            ('file|with*wildcards?.txt', 'file_with_wildcards_.txt'),
            ('CON.txt', '_CON.txt'),  # Reserved Windows name
            ('  .hidden_file.txt  ', 'hidden_file.txt'),  # Leading/trailing dots and spaces
            ('very_long_filename' * 20 + '.txt', None)  # Will be truncated
        ]
        
        for original, expected in test_cases:
            sanitized = PathUtils.sanitize_filename(original)
            if expected is not None:
                self.assertEqual(sanitized, expected)
            else:
                self.assertLessEqual(len(sanitized), 255)
    
    def test_file_type_validation(self):
        """Test file type validation"""
        allowed_files = [
            'document.txt',
            'report.html',
            'data.json',
            'image.png',
            'cert.pem'
        ]
        
        dangerous_files = [
            'malware.exe',
            'script.bat',
            'virus.scr',
            'backdoor.dll'
        ]
        
        for file_path in allowed_files:
            self.assertTrue(PathUtils.is_allowed_file_type(file_path), 
                          f"File should be allowed: {file_path}")
        
        for file_path in dangerous_files:
            self.assertFalse(PathUtils.is_allowed_file_type(file_path), 
                           f"File should be dangerous: {file_path}")
    
    def test_secure_temp_path(self):
        """Test secure temporary path creation"""
        temp_path = PathUtils.get_secure_temp_path('test_', '.tmp')
        
        # Should be within base directory
        base_dir = PathUtils.get_base_dir()
        self.assertTrue(temp_path.startswith(os.path.join(base_dir, 'temp')))
        
        # Should contain prefix and suffix
        filename = os.path.basename(temp_path)
        self.assertTrue(filename.startswith('test_'))
        self.assertTrue(filename.endswith('.tmp'))
    
    def test_base_directory_validation(self):
        """Test base directory validation"""
        base_dir = PathUtils.get_base_dir()
        
        # Path within base directory should be valid
        safe_path = os.path.join(base_dir, 'logs', 'test.log')
        self.assertTrue(PathUtils.is_within_base_directory(safe_path))
        
        # Path outside base directory should be invalid
        unsafe_path = '/etc/passwd'
        self.assertFalse(PathUtils.is_within_base_directory(unsafe_path))
    
    def test_secure_file_operations(self):
        """Test secure file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test source file
            src_file = os.path.join(temp_dir, 'source.txt')
            with open(src_file, 'w') as f:
                f.write('test content')
            
            # Test secure copy within safe directory
            dst_file = os.path.join(temp_dir, 'destination.txt')
            
            # This should fail because temp_dir is outside base directory
            # In a real scenario, we'd use paths within the framework
            result = PathUtils.secure_file_copy(src_file, dst_file)
            # Expected to fail due to path validation
            self.assertFalse(result)


def run_security_tests():
    """Run all security tests"""
    test_classes = [
        TestRateLimiter,
        TestExponentialBackoff, 
        TestNetworkSecurityManager,
        TestPathUtilsSecurity
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("ChromSploit Framework - Network Security Tests")
    print("=" * 50)
    
    success = run_security_tests()
    
    if success:
        print("\n✅ All security tests passed!")
        exit(0)
    else:
        print("\n❌ Some security tests failed!")
        exit(1)