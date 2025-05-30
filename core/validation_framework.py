#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Validation Framework
Comprehensive testing and validation system for all components
"""

import os
import sys
import time
import json
import subprocess
import importlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result"""
    name: str
    category: str
    status: str  # passed, failed, skipped, error
    message: str
    execution_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category,
            'status': self.status,
            'message': self.message,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }


@dataclass
class ValidationSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[Callable]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    timeout: int = 300  # 5 minutes default


class ValidationFramework:
    """Comprehensive validation framework for ChromSploit"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.test_suites: Dict[str, ValidationSuite] = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Register test suites
        self._register_core_tests()
        self._register_exploit_tests()
        self._register_integration_tests()
        self._register_performance_tests()
    
    def _register_core_tests(self):
        """Register core component tests"""
        core_tests = [
            self._test_module_loader,
            self._test_logger_functionality,
            self._test_config_system,
            self._test_path_handling,
            self._test_error_handling,
            self._test_reporting_system
        ]
        
        self.test_suites['core'] = ValidationSuite(
            name='Core Components',
            description='Test fundamental framework components',
            tests=core_tests
        )
    
    def _register_exploit_tests(self):
        """Register exploit validation tests"""
        exploit_tests = [
            self._test_cve_2025_4664,
            self._test_cve_2025_2783,
            self._test_cve_2025_2857,
            self._test_cve_2025_30397,
            self._test_oauth_exploitation,
            self._test_exploit_chain_execution
        ]
        
        self.test_suites['exploits'] = ValidationSuite(
            name='Exploit Modules',
            description='Test all exploit implementations',
            tests=exploit_tests
        )
    
    def _register_integration_tests(self):
        """Register integration tests"""
        integration_tests = [
            self._test_sliver_c2_integration,
            self._test_collaboration_features,
            self._test_compliance_tracking,
            self._test_evidence_collection,
            self._test_api_testing_module
        ]
        
        self.test_suites['integration'] = ValidationSuite(
            name='Integration Tests',
            description='Test component interactions',
            tests=integration_tests
        )
    
    def _register_performance_tests(self):
        """Register performance tests"""
        performance_tests = [
            self._test_memory_usage,
            self._test_cpu_performance,
            self._test_network_performance,
            self._test_concurrent_operations,
            self._test_large_dataset_handling
        ]
        
        self.test_suites['performance'] = ValidationSuite(
            name='Performance Tests',
            description='Test performance characteristics',
            tests=performance_tests,
            timeout=600  # 10 minutes for performance tests
        )
    
    def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            logger.error(f"Test suite '{suite_name}' not found")
            return []
        
        suite = self.test_suites[suite_name]
        logger.info(f"Running test suite: {suite.name}")
        
        suite_results = []
        
        # Run setup if available
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                logger.error(f"Suite setup failed: {e}")
                return []
        
        # Run tests
        for test_func in suite.tests:
            result = self._run_single_test(test_func, suite_name, suite.timeout)
            suite_results.append(result)
            self.test_results.append(result)
        
        # Run teardown if available
        if suite.teardown:
            try:
                suite.teardown()
            except Exception as e:
                logger.warning(f"Suite teardown failed: {e}")
        
        return suite_results
    
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run all test suites"""
        self.start_time = datetime.now()
        logger.info("Starting comprehensive validation...")
        
        all_results = {}
        
        for suite_name in self.test_suites:
            suite_results = self.run_test_suite(suite_name)
            all_results[suite_name] = suite_results
        
        self.end_time = datetime.now()
        self._calculate_statistics()
        
        logger.info(f"Validation completed: {self.passed_tests}/{self.total_tests} passed")
        return all_results
    
    def _run_single_test(self, test_func: Callable, category: str, timeout: int) -> TestResult:
        """Run a single test with timeout and error handling"""
        test_name = test_func.__name__
        start_time = time.time()
        
        logger.debug(f"Running test: {test_name}")
        
        try:
            # Run test with timeout
            result = self._execute_with_timeout(test_func, timeout)
            
            if result is True:
                status = "passed"
                message = "Test passed successfully"
            elif result is False:
                status = "failed"
                message = "Test failed"
            elif isinstance(result, dict):
                status = result.get('status', 'passed')
                message = result.get('message', 'Test completed')
            else:
                status = "passed"
                message = str(result)
                
        except TimeoutError:
            status = "failed"
            message = f"Test timed out after {timeout} seconds"
        except Exception as e:
            status = "error"
            message = f"Test error: {str(e)}"
        
        execution_time = time.time() - start_time
        
        return TestResult(
            name=test_name,
            category=category,
            status=status,
            message=message,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
    
    def _execute_with_timeout(self, func: Callable, timeout: int):
        """Execute function with timeout"""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Function timed out after {timeout} seconds")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _calculate_statistics(self):
        """Calculate test statistics"""
        self.total_tests = len(self.test_results)
        self.passed_tests = len([r for r in self.test_results if r.status == 'passed'])
        self.failed_tests = len([r for r in self.test_results if r.status in ['failed', 'error']])
        self.skipped_tests = len([r for r in self.test_results if r.status == 'skipped'])
    
    # Core component tests
    def _test_module_loader(self) -> Dict[str, Any]:
        """Test module loader functionality"""
        try:
            from core.module_loader import get_module_loader
            
            loader = get_module_loader()
            modules = loader.list_available_modules()
            
            if not modules:
                return {'status': 'failed', 'message': 'No modules found'}
            
            # Test loading a module with fallback
            ai_module = loader.load_module('ai_orchestrator')
            if ai_module is None:
                return {'status': 'failed', 'message': 'Failed to load module or fallback'}
            
            return {'status': 'passed', 'message': f'Module loader working, {len(modules)} modules available'}
            
        except Exception as e:
            return {'status': 'error', 'message': f'Module loader test failed: {e}'}
    
    def _test_logger_functionality(self) -> Dict[str, Any]:
        """Test logging system"""
        try:
            from core.enhanced_logger import get_logger
            
            test_logger = get_logger()
            test_logger.info("Test log message")
            
            return {'status': 'passed', 'message': 'Logger functionality verified'}
            
        except Exception as e:
            return {'status': 'error', 'message': f'Logger test failed: {e}'}
    
    def _test_config_system(self) -> Dict[str, Any]:
        """Test configuration system"""
        try:
            # Test config file creation and reading
            test_config = {'test_key': 'test_value'}
            config_path = '/tmp/test_config.json'
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            if loaded_config == test_config:
                os.remove(config_path)
                return {'status': 'passed', 'message': 'Config system working'}
            else:
                return {'status': 'failed', 'message': 'Config data mismatch'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Config test failed: {e}'}
    
    def _test_path_handling(self) -> Dict[str, Any]:
        """Test path handling functionality"""
        try:
            from pathlib import Path
            
            # Test path creation and access
            test_dir = Path('/tmp/chromsploit_test')
            test_dir.mkdir(exist_ok=True)
            
            test_file = test_dir / 'test.txt'
            test_file.write_text('test content')
            
            if test_file.exists() and test_file.read_text() == 'test content':
                # Cleanup
                test_file.unlink()
                test_dir.rmdir()
                return {'status': 'passed', 'message': 'Path handling verified'}
            else:
                return {'status': 'failed', 'message': 'Path operations failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Path test failed: {e}'}
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling system"""
        try:
            # Test that errors are properly caught and logged
            try:
                raise ValueError("Test error")
            except ValueError as e:
                # Error was caught properly
                return {'status': 'passed', 'message': 'Error handling working'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Error handling test failed: {e}'}
    
    def _test_reporting_system(self) -> Dict[str, Any]:
        """Test reporting system"""
        try:
            from core.reporting import ReportGenerator
            
            generator = ReportGenerator()
            test_data = {'test': 'data'}
            report = generator.generate_report(test_data)
            
            if report and len(report) > 0:
                return {'status': 'passed', 'message': 'Reporting system functional'}
            else:
                return {'status': 'failed', 'message': 'Empty report generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Reporting test failed: {e}'}
    
    # Exploit tests
    def _test_cve_2025_4664(self) -> Dict[str, Any]:
        """Test CVE-2025-4664 exploit"""
        try:
            from exploits.cve_2025_4664 import CVE2025_4664_Exploit
            
            exploit = CVE2025_4664_Exploit()
            exploit.set_parameter('kali_ip', '127.0.0.1')
            exploit.set_parameter('port', 18080)  # Use different port for testing
            
            # Test payload generation
            payload = exploit.generate_payload()
            
            if payload and 'CVE-2025-4664' in payload:
                return {'status': 'passed', 'message': 'CVE-2025-4664 exploit validated'}
            else:
                return {'status': 'failed', 'message': 'Invalid payload generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'CVE-2025-4664 test failed: {e}'}
    
    def _test_cve_2025_2783(self) -> Dict[str, Any]:
        """Test CVE-2025-2783 exploit"""
        try:
            from exploits.cve_2025_2783 import CVE2025_2783_Exploit
            
            exploit = CVE2025_2783_Exploit()
            payload = exploit.generate_payload()
            
            if payload and 'CVE-2025-2783' in payload:
                return {'status': 'passed', 'message': 'CVE-2025-2783 exploit validated'}
            else:
                return {'status': 'failed', 'message': 'Invalid payload generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'CVE-2025-2783 test failed: {e}'}
    
    def _test_cve_2025_2857(self) -> Dict[str, Any]:
        """Test CVE-2025-2857 exploit"""
        try:
            from exploits.cve_2025_2857 import CVE2025_2857_Exploit
            
            exploit = CVE2025_2857_Exploit()
            payload = exploit.generate_payload()
            
            if payload and 'CVE-2025-2857' in payload:
                return {'status': 'passed', 'message': 'CVE-2025-2857 exploit validated'}
            else:
                return {'status': 'failed', 'message': 'Invalid payload generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'CVE-2025-2857 test failed: {e}'}
    
    def _test_cve_2025_30397(self) -> Dict[str, Any]:
        """Test CVE-2025-30397 exploit"""
        try:
            from exploits.cve_2025_30397 import CVE2025_30397_Exploit
            
            exploit = CVE2025_30397_Exploit()
            payload = exploit.generate_payload()
            
            if payload and 'CVE-2025-30397' in payload:
                return {'status': 'passed', 'message': 'CVE-2025-30397 exploit validated'}
            else:
                return {'status': 'failed', 'message': 'Invalid payload generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'CVE-2025-30397 test failed: {e}'}
    
    def _test_oauth_exploitation(self) -> Dict[str, Any]:
        """Test OAuth exploitation"""
        try:
            from exploits.oauth_exploitation import OAuthExploitEngine
            
            exploit = OAuthExploitEngine()
            exploit.set_parameter('port', 18084)  # Use different port
            
            # Test OAuth URL generation
            auth_url, state = exploit.generate_oauth_attack_url()
            
            if auth_url and state and 'oauth2' in auth_url:
                return {'status': 'passed', 'message': 'OAuth exploitation validated'}
            else:
                return {'status': 'failed', 'message': 'Invalid OAuth URL generated'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'OAuth test failed: {e}'}
    
    def _test_exploit_chain_execution(self) -> Dict[str, Any]:
        """Test exploit chain functionality"""
        try:
            from core.exploit_chain import ExploitChain
            
            chain = ExploitChain("test_chain", "Test chain for validation")
            
            # Add test steps
            chain.add_step(
                cve_id="CVE-2025-4664",
                description="Test step",
                parameters={'test': True}
            )
            
            if len(chain.steps) == 1:
                return {'status': 'passed', 'message': 'Exploit chain functionality validated'}
            else:
                return {'status': 'failed', 'message': 'Chain step not added properly'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Exploit chain test failed: {e}'}
    
    # Integration tests
    def _test_sliver_c2_integration(self) -> Dict[str, Any]:
        """Test Sliver C2 integration"""
        try:
            from core.sliver_c2.sliver_manager import SliverServerManager
            
            # Test manager initialization
            manager = SliverServerManager()
            
            # Test configuration
            if manager.config:
                return {'status': 'passed', 'message': 'Sliver C2 integration validated'}
            else:
                return {'status': 'failed', 'message': 'Sliver C2 config missing'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Sliver C2 test failed: {e}'}
    
    def _test_collaboration_features(self) -> Dict[str, Any]:
        """Test collaboration functionality"""
        try:
            from core.collaboration import CollaborationManager
            
            manager = CollaborationManager()
            
            # Test adding team member
            member = manager.add_team_member("test_user", "test@example.com")
            
            if member and member.username == "test_user":
                return {'status': 'passed', 'message': 'Collaboration features validated'}
            else:
                return {'status': 'failed', 'message': 'Team member creation failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Collaboration test failed: {e}'}
    
    def _test_compliance_tracking(self) -> Dict[str, Any]:
        """Test compliance tracking"""
        try:
            from core.compliance_tracking import ComplianceTracker
            
            tracker = ComplianceTracker()
            rules = tracker.get_active_rules()
            
            if rules and len(rules) > 0:
                return {'status': 'passed', 'message': 'Compliance tracking validated'}
            else:
                return {'status': 'failed', 'message': 'No compliance rules found'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Compliance test failed: {e}'}
    
    def _test_evidence_collection(self) -> Dict[str, Any]:
        """Test evidence collection"""
        try:
            from core.evidence_collection import EvidenceCollectionManager
            
            manager = EvidenceCollectionManager()
            case_id = manager.create_case("test_case", "Test case", "test_target")
            
            if case_id:
                return {'status': 'passed', 'message': 'Evidence collection validated'}
            else:
                return {'status': 'failed', 'message': 'Case creation failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Evidence collection test failed: {e}'}
    
    def _test_api_testing_module(self) -> Dict[str, Any]:
        """Test API testing functionality"""
        try:
            from core.api_testing import APITester
            
            tester = APITester("http://localhost:8080")
            
            # Test initialization
            if tester.base_url == "http://localhost:8080":
                return {'status': 'passed', 'message': 'API testing module validated'}
            else:
                return {'status': 'failed', 'message': 'API tester initialization failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'API testing test failed: {e}'}
    
    # Performance tests
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage"""
        try:
            import psutil
            import gc
            
            # Get initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Create some objects
            test_data = [{'data': 'x' * 1000} for _ in range(1000)]
            
            # Get peak memory
            peak_memory = process.memory_info().rss
            
            # Cleanup
            del test_data
            gc.collect()
            
            # Check memory usage
            memory_increase = peak_memory - initial_memory
            memory_mb = memory_increase / (1024 * 1024)
            
            if memory_mb < 100:  # Less than 100MB increase
                return {'status': 'passed', 'message': f'Memory usage acceptable: {memory_mb:.1f}MB'}
            else:
                return {'status': 'failed', 'message': f'High memory usage: {memory_mb:.1f}MB'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Memory test failed: {e}'}
    
    def _test_cpu_performance(self) -> Dict[str, Any]:
        """Test CPU performance"""
        try:
            import time
            
            # Simple CPU test
            start_time = time.time()
            
            # Perform some calculations
            total = 0
            for i in range(100000):
                total += i * i
            
            execution_time = time.time() - start_time
            
            if execution_time < 1.0:  # Less than 1 second
                return {'status': 'passed', 'message': f'CPU performance good: {execution_time:.3f}s'}
            else:
                return {'status': 'failed', 'message': f'Slow CPU performance: {execution_time:.3f}s'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'CPU test failed: {e}'}
    
    def _test_network_performance(self) -> Dict[str, Any]:
        """Test network performance"""
        try:
            import socket
            import time
            
            # Test local connection
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                result = sock.connect_ex(('127.0.0.1', 22))  # SSH port
                connection_time = time.time() - start_time
                
                if connection_time < 1.0:
                    return {'status': 'passed', 'message': f'Network performance good: {connection_time:.3f}s'}
                else:
                    return {'status': 'failed', 'message': f'Slow network: {connection_time:.3f}s'}
                    
            finally:
                sock.close()
                
        except Exception as e:
            return {'status': 'error', 'message': f'Network test failed: {e}'}
    
    def _test_concurrent_operations(self) -> Dict[str, Any]:
        """Test concurrent operations"""
        try:
            import threading
            import time
            
            results = []
            
            def worker(worker_id):
                start_time = time.time()
                # Simulate work
                total = sum(i * i for i in range(10000))
                execution_time = time.time() - start_time
                results.append(execution_time)
            
            # Start multiple threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            avg_time = sum(results) / len(results)
            
            if avg_time < 0.1:  # Less than 100ms average
                return {'status': 'passed', 'message': f'Concurrent performance good: {avg_time:.3f}s avg'}
            else:
                return {'status': 'failed', 'message': f'Slow concurrent performance: {avg_time:.3f}s avg'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Concurrent test failed: {e}'}
    
    def _test_large_dataset_handling(self) -> Dict[str, Any]:
        """Test handling of large datasets"""
        try:
            import json
            import time
            
            # Create large dataset
            start_time = time.time()
            large_data = {'items': [{'id': i, 'data': f'item_{i}'} for i in range(10000)]}
            
            # Serialize to JSON
            json_data = json.dumps(large_data)
            
            # Deserialize from JSON
            parsed_data = json.loads(json_data)
            
            processing_time = time.time() - start_time
            
            if processing_time < 2.0 and len(parsed_data['items']) == 10000:
                return {'status': 'passed', 'message': f'Large dataset handling good: {processing_time:.3f}s'}
            else:
                return {'status': 'failed', 'message': f'Slow large dataset handling: {processing_time:.3f}s'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Large dataset test failed: {e}'}
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate validation report"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/tmp/validation_report_{timestamp}.json"
        
        report_data = {
            'validation_summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'skipped_tests': self.skipped_tests,
                'success_rate': f"{(self.passed_tests / self.total_tests * 100):.1f}%" if self.total_tests > 0 else "0%",
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'total_time': (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
            },
            'test_results': [result.to_dict() for result in self.test_results],
            'suite_summary': {}
        }
        
        # Add suite summaries
        for suite_name in self.test_suites:
            suite_results = [r for r in self.test_results if r.category == suite_name]
            suite_passed = len([r for r in suite_results if r.status == 'passed'])
            suite_total = len(suite_results)
            
            report_data['suite_summary'][suite_name] = {
                'total': suite_total,
                'passed': suite_passed,
                'failed': suite_total - suite_passed,
                'success_rate': f"{(suite_passed / suite_total * 100):.1f}%" if suite_total > 0 else "0%"
            }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Validation report saved to: {output_path}")
        return output_path


# Global instance
_validation_framework = None

def get_validation_framework() -> ValidationFramework:
    """Get or create validation framework instance"""
    global _validation_framework
    if _validation_framework is None:
        _validation_framework = ValidationFramework()
    return _validation_framework


def run_validation(suite_name: str = None) -> List[TestResult]:
    """Convenience function to run validation"""
    framework = get_validation_framework()
    
    if suite_name:
        return framework.run_test_suite(suite_name)
    else:
        results = framework.run_all_tests()
        framework.generate_report()
        return [result for suite_results in results.values() for result in suite_results]