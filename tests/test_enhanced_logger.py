#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Tests for enhanced logger system
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tests.test_base import TestBase

from core.enhanced_logger import (
    EnhancedLogger, LogLevel, ColoredFormatter, LogFilter,
    LogAnalyzer, get_logger
)

class TestLogLevel(TestBase):
    """Test log level constants and conversions"""
    
    def test_log_level_values(self):
        """Test log level numeric values"""
        assert LogLevel.CRITICAL == 50
        assert LogLevel.ERROR == 40
        assert LogLevel.WARNING == 30
        assert LogLevel.INFO == 20
        assert LogLevel.DEBUG == 10
        assert LogLevel.TRACE == 5
    
    def test_to_string_conversion(self):
        """Test converting numeric levels to strings"""
        assert LogLevel.to_string(50) == "CRITICAL"
        assert LogLevel.to_string(40) == "ERROR"
        assert LogLevel.to_string(30) == "WARNING"
        assert LogLevel.to_string(20) == "INFO"
        assert LogLevel.to_string(10) == "DEBUG"
        assert LogLevel.to_string(5) == "TRACE"
        assert LogLevel.to_string(999) == "UNKNOWN"

class TestColoredFormatter(TestBase):
    """Test colored formatter"""
    
    def test_formatter_creation(self):
        """Test creating colored formatter"""
        formatter = ColoredFormatter(use_colors=True)
        assert formatter.use_colors
        
        formatter_no_color = ColoredFormatter(use_colors=False)
        assert not formatter_no_color.use_colors
    
    def test_format_with_colors(self):
        """Test formatting with colors"""
        formatter = ColoredFormatter(use_colors=True)
        
        # Create a log record
        record = MagicMock()
        record.levelname = "INFO"
        record.msg = "Test message"
        record.getMessage.return_value = "Test message"
        
        # Mock parent format method
        with patch.object(formatter.__class__.__bases__[0], 'format', return_value="Formatted"):
            result = formatter.format(record)
            assert result == "Formatted"

class TestLogFilter(TestBase):
    """Test log filtering functionality"""
    
    def test_filter_creation(self):
        """Test creating log filter"""
        filter = LogFilter()
        assert filter.filters['level'] is None
        assert filter.filters['module'] is None
        assert filter.filters['contains'] is None
        assert filter.filters['excludes'] is None
    
    def test_level_filter(self):
        """Test filtering by level"""
        filter = LogFilter()
        filter.set_level_filter(LogLevel.WARNING)
        
        # Test records
        assert not filter.apply({'level_no': LogLevel.DEBUG})
        assert not filter.apply({'level_no': LogLevel.INFO})
        assert filter.apply({'level_no': LogLevel.WARNING})
        assert filter.apply({'level_no': LogLevel.ERROR})
    
    def test_module_filter(self):
        """Test filtering by module"""
        filter = LogFilter()
        filter.set_module_filter(['core', 'ui'])
        
        assert filter.apply({'module': 'core'})
        assert filter.apply({'module': 'ui'})
        assert not filter.apply({'module': 'test'})
    
    def test_text_filter(self):
        """Test filtering by text content"""
        filter = LogFilter()
        
        # Contains filter
        filter.set_text_filter(contains="error")
        assert filter.apply({'message': 'An error occurred'})
        assert not filter.apply({'message': 'All is well'})
        
        # Excludes filter
        filter.filters['contains'] = None
        filter.set_text_filter(excludes="debug")
        assert filter.apply({'message': 'Normal message'})
        assert not filter.apply({'message': 'Debug information'})

class TestLogAnalyzer(TestBase):
    """Test log analysis functionality"""
    
    def test_analyzer_creation(self):
        """Test creating log analyzer"""
        analyzer = LogAnalyzer()
        assert len(analyzer.stats) == 0
        assert len(analyzer.error_patterns) == 0
        assert len(analyzer.module_stats) == 0
    
    def test_log_analysis(self):
        """Test analyzing logs"""
        analyzer = LogAnalyzer()
        
        logs = [
            {'level': 'INFO', 'module': 'core', 'message': 'Started', 'timestamp': '2024-01-01T00:00:00'},
            {'level': 'ERROR', 'module': 'core', 'message': 'ValueError occurred', 'timestamp': '2024-01-01T00:00:01'},
            {'level': 'WARNING', 'module': 'ui', 'message': 'Deprecated', 'timestamp': '2024-01-01T00:00:02'},
            {'level': 'ERROR', 'module': 'ui', 'message': 'KeyError in config', 'timestamp': '2024-01-01T00:00:03'},
        ]
        
        stats = analyzer.analyze(logs)
        
        assert stats['total_logs'] == 4
        assert stats['levels']['level_INFO'] == 1
        assert stats['levels']['level_ERROR'] == 2
        assert stats['levels']['level_WARNING'] == 1
        assert stats['module_stats']['core']['ERROR'] == 1
        assert stats['module_stats']['ui']['ERROR'] == 1

class TestEnhancedLogger(TestBase):
    """Test enhanced logger functionality"""
    
    def test_logger_creation(self):
        """Test creating enhanced logger"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=True,
                json_output=False
            )
            
            assert logger.name == 'test'
            assert logger.log_dir == Path(temp_dir)
            assert len(logger.log_buffer) == 0
    
    def test_logging_methods(self):
        """Test various logging methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.TRACE,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Test all log levels
            logger.trace("Trace message")
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Check buffer
            assert len(logger.log_buffer) == 6
            
            # Verify log levels
            levels = [log['level'] for log in logger.log_buffer]
            assert 'TRACE' in levels
            assert 'DEBUG' in levels
            assert 'INFO' in levels
            assert 'WARNING' in levels
            assert 'ERROR' in levels
            assert 'CRITICAL' in levels
    
    def test_log_filtering(self):
        """Test getting filtered logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.TRACE,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Add various logs
            logger.info("Info 1")
            logger.error("Error 1")
            logger.info("Info 2")
            logger.error("Error 2")
            
            # Test count filter
            logs = logger.get_logs(count=2)
            assert len(logs) == 2
            
            # Test level filter
            error_logs = logger.get_logs(level='ERROR')
            assert all(log['level'] == 'ERROR' for log in error_logs)
            
            # Test contains filter
            logs_with_1 = logger.get_logs(contains='1')
            assert all('1' in log['message'] for log in logs_with_1)
    
    def test_log_analysis(self):
        """Test log analysis feature"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Add logs
            for i in range(5):
                logger.info(f"Info {i}")
            for i in range(3):
                logger.error(f"Error {i}")
            
            # Analyze logs
            stats = logger.analyze_logs()
            
            assert stats['total_logs'] == 8
            assert stats['levels']['level_INFO'] == 5
            assert stats['levels']['level_ERROR'] == 3
    
    def test_log_export(self):
        """Test exporting logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Add logs
            logger.info("Test log 1")
            logger.error("Test log 2")
            
            # Export to JSON
            json_path = Path(temp_dir) / 'export.json'
            assert logger.export_logs(str(json_path), format='json')
            assert json_path.exists()
            
            # Verify JSON content
            with open(json_path) as f:
                data = json.load(f)
                assert len(data) == 2
            
            # Export to TXT
            txt_path = Path(temp_dir) / 'export.txt'
            assert logger.export_logs(str(txt_path), format='txt')
            assert txt_path.exists()
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Add some logs
            for i in range(10):
                logger.info(f"Log {i}")
            
            metrics = logger.get_performance_metrics()
            
            assert metrics['total_logs'] == 10
            assert metrics['buffer_size'] == 10
            assert 'uptime_seconds' in metrics
            assert 'logs_per_second' in metrics
    
    def test_set_level(self):
        """Test changing log level"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Log at debug level (should not appear)
            logger.debug("Debug message")
            initial_count = len(logger.log_buffer)
            
            # Change level to DEBUG
            logger.set_level('DEBUG')
            
            # Now debug messages should appear
            logger.debug("Debug message 2")
            assert len(logger.log_buffer) > initial_count
    
    def test_clear_logs(self):
        """Test clearing log buffer"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            # Add logs
            logger.info("Test 1")
            logger.info("Test 2")
            assert len(logger.log_buffer) > 0
            
            # Clear logs
            logger.clear_logs()
            assert len(logger.log_buffer) == 0
    
    def test_exception_logging(self):
        """Test exception logging with traceback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = EnhancedLogger(
                name='test',
                log_level=LogLevel.INFO,
                log_dir=temp_dir,
                console_output=False
            )
            
            try:
                1 / 0
            except ZeroDivisionError:
                logger.exception("Division error")
            
            # Should have logged the exception
            assert any('Division error' in str(handler.format.call_args) 
                      for handler in logger.logger.handlers 
                      if hasattr(handler, 'format'))

class TestGlobalLogger(TestBase):
    """Test global logger instance"""
    
    def test_get_logger(self):
        """Test getting global logger instance"""
        logger1 = get_logger()
        logger2 = get_logger()
        
        # Should return same instance
        assert logger1 is logger2
        
        # Should be an EnhancedLogger
        assert isinstance(logger1, EnhancedLogger)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])