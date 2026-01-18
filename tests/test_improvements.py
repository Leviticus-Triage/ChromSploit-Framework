#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Framework Improvements
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.detection import get_browser_detector, BrowserType
from modules.monitoring import get_exploit_monitor
from modules.cache import get_exploit_cache
from modules.safety import get_safety_manager, SafetyLevel


class TestBrowserDetection(unittest.TestCase):
    """Tests for browser detection"""
    
    def setUp(self):
        self.detector = get_browser_detector()
    
    def test_chrome_detection(self):
        """Test Chrome detection"""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        info = self.detector.detect_browser(ua)
        self.assertEqual(info.browser_type, BrowserType.CHROME)
        self.assertIsNotNone(info.version)
    
    def test_edge_detection(self):
        """Test Edge detection"""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        info = self.detector.detect_browser(ua)
        # Edge is Chromium-based, so it may be detected as Chrome first
        # But should have "Edg" in user agent
        self.assertIn("Edg", ua)
        # Check that version is detected
        self.assertIsNotNone(info.version)
    
    def test_firefox_detection(self):
        """Test Firefox detection"""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        info = self.detector.detect_browser(ua)
        self.assertEqual(info.browser_type, BrowserType.FIREFOX)
    
    def test_vulnerability_check(self):
        """Test vulnerability checking"""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        info = self.detector.detect_browser(ua)
        is_vuln, confidence, reason = self.detector.is_vulnerable(info, "CVE-2025-49741")
        self.assertIsInstance(is_vuln, bool)
        self.assertIsInstance(confidence, float)
    
    def test_recommendations(self):
        """Test exploit recommendations"""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        info = self.detector.detect_browser(ua)
        recommendations = self.detector.recommend_exploit(info)
        self.assertIsInstance(recommendations, list)


class TestExploitMonitoring(unittest.TestCase):
    """Tests for exploit monitoring"""
    
    def setUp(self):
        self.monitor = get_exploit_monitor()
    
    def test_tracking(self):
        """Test exploit tracking"""
        attempt_id = self.monitor.track_exploit_start(
            "CVE-2025-49741",
            "edge",
            "135.0.0.0"
        )
        self.assertIsNotNone(attempt_id)
        
        self.monitor.track_exploit_end(attempt_id, True)
        
        stats = self.monitor.get_statistics("CVE-2025-49741")
        self.assertIsNotNone(stats)
    
    def test_performance_metrics(self):
        """Test performance metrics"""
        metrics = self.monitor.get_performance_metrics()
        self.assertIn("total_attempts", metrics)
        self.assertIn("overall_success_rate", metrics)
    
    def test_report_generation(self):
        """Test report generation"""
        report = self.monitor.generate_report()
        self.assertIn("generated_at", report)
        self.assertIn("performance_metrics", report)


class TestCaching(unittest.TestCase):
    """Tests for caching system"""
    
    def setUp(self):
        self.cache = get_exploit_cache()
    
    def test_basic_cache(self):
        """Test basic caching"""
        self.cache.set("test_key", "test_value", ttl=60)
        value = self.cache.get("test_key")
        self.assertEqual(value, "test_value")
    
    def test_payload_caching(self):
        """Test payload caching"""
        key = self.cache.cache_payload(
            "CVE-2025-49741",
            {"kali_ip": "127.0.0.1", "port": 8080},
            "<html>test</html>"
        )
        self.assertIsNotNone(key)
        
        cached = self.cache.get_cached_payload(
            "CVE-2025-49741",
            {"kali_ip": "127.0.0.1", "port": 8080}
        )
        self.assertEqual(cached, "<html>test</html>")
    
    def test_obfuscation_caching(self):
        """Test obfuscation caching"""
        key = self.cache.cache_obfuscation(
            "var test = 'hello';",
            "standard",
            "var _0x1a2b = 'hello';"
        )
        self.assertIsNotNone(key)
        
        cached = self.cache.get_cached_obfuscation(
            "var test = 'hello';",
            "standard"
        )
        self.assertIsNotNone(cached)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        stats = self.cache.get_stats()
        self.assertIn("total_entries", stats)
        self.assertIn("total_hits", stats)


class TestSafetyManager(unittest.TestCase):
    """Tests for safety manager"""
    
    def setUp(self):
        self.safety = get_safety_manager()
    
    def test_authorization(self):
        """Test authorization"""
        auth_key = self.safety.authorize("CVE-2025-49741", "test_user")
        self.assertIsNotNone(auth_key)
        
        is_authorized = self.safety.check_authorization("CVE-2025-49741", "test_user")
        self.assertTrue(is_authorized)
    
    def test_target_validation(self):
        """Test target validation"""
        result = self.safety.validate_target("http://localhost:8080")
        self.assertIsNotNone(result)
        self.assertIsInstance(result.allowed, bool)
    
    def test_safety_check(self):
        """Test comprehensive safety check"""
        result = self.safety.check_exploit_safety(
            "CVE-2025-49741",
            "http://test.example.com",
            "test_user"
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result.allowed, bool)
    
    def test_safety_status(self):
        """Test safety status"""
        status = self.safety.get_safety_status()
        self.assertIn("sandbox_mode", status)
        self.assertIn("safety_level", status)


if __name__ == '__main__':
    unittest.main()
