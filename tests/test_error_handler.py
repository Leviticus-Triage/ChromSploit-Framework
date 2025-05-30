#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Tests for error handling system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tests.test_base import TestBase

from core.error_handler import (
    ErrorHandler, ErrorSeverity, ErrorCategory, FrameworkError,
    NetworkError, ConfigurationError, ValidationError, PermissionError,
    DependencyError, handle_errors, ErrorContext, get_error_handler
)

class TestErrorEnums(TestBase):
    """Test error enumerations"""
    
    def test_error_severity_values(self):
        """Test error severity levels"""
        assert ErrorSeverity.LOW.value == 1
        assert ErrorSeverity.MEDIUM.value == 2
        assert ErrorSeverity.HIGH.value == 3
        assert ErrorSeverity.CRITICAL.value == 4
    
    def test_error_category_values(self):
        """Test error categories"""
        assert ErrorCategory.NETWORK.value == "Network Error"
        assert ErrorCategory.FILE_IO.value == "File I/O Error"
        assert ErrorCategory.CONFIGURATION.value == "Configuration Error"
        assert ErrorCategory.VALIDATION.value == "Validation Error"
        assert ErrorCategory.PERMISSION.value == "Permission Error"
        assert ErrorCategory.DEPENDENCY.value == "Dependency Error"
        assert ErrorCategory.USER_INPUT.value == "User Input Error"
        assert ErrorCategory.SYSTEM.value == "System Error"
        assert ErrorCategory.UNKNOWN.value == "Unknown Error"

class TestFrameworkError(TestBase):
    """Test base framework error"""
    
    def test_framework_error_creation(self):
        """Test creating framework error"""
        error = FrameworkError(
            message="Test error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            details={'host': 'localhost'},
            suggestions=['Check connection']
        )
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.HIGH
        assert error.details == {'host': 'localhost'}
        assert error.suggestions == ['Check connection']
        assert error.timestamp is not None
    
    def test_framework_error_to_dict(self):
        """Test converting error to dictionary"""
        error = FrameworkError(
            message="Test error",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM
        )
        
        error_dict = error.to_dict()
        
        assert error_dict['message'] == "Test error"
        assert error_dict['category'] == "Validation Error"
        assert error_dict['severity'] == "MEDIUM"
        assert 'timestamp' in error_dict
    
    def test_specific_error_types(self):
        """Test specific error type creation"""
        # Network error
        net_error = NetworkError("Connection failed")
        assert net_error.category == ErrorCategory.NETWORK
        
        # Configuration error
        config_error = ConfigurationError("Invalid config")
        assert config_error.category == ErrorCategory.CONFIGURATION
        
        # Validation error
        val_error = ValidationError("Invalid input")
        assert val_error.category == ErrorCategory.VALIDATION
        
        # Permission error
        perm_error = PermissionError("Access denied")
        assert perm_error.category == ErrorCategory.PERMISSION
        
        # Dependency error
        dep_error = DependencyError("Module not found")
        assert dep_error.category == ErrorCategory.DEPENDENCY

class TestErrorHandler(TestBase):
    """Test error handler functionality"""
    
    @patch('core.error_handler.get_logger')
    def test_error_handler_creation(self, mock_get_logger):
        """Test creating error handler"""
        handler = ErrorHandler()
        
        assert handler.error_history == []
        assert handler.error_callbacks == {}
        assert handler.max_history_size == 1000
        assert handler.user_friendly_mode
        assert not handler.debug_mode
    
    @patch('core.error_handler.get_logger')
    def test_handle_framework_error(self, mock_get_logger, capture_print):
        """Test handling framework errors"""
        handler = ErrorHandler()
        handler.user_friendly_mode = True
        
        error = NetworkError(
            "Connection failed",
            severity=ErrorSeverity.HIGH,
            suggestions=["Check internet connection"]
        )
        
        result = handler.handle_error(error, context="Network test")
        
        assert result['message'] == "Connection failed"
        assert result['category'] == "Network Error"
        assert result['severity'] == "HIGH"
        assert result['context'] == "Network test"
        
        # Check error was logged
        mock_get_logger.return_value.error.assert_called()
    
    @patch('core.error_handler.get_logger')
    def test_handle_standard_exception(self, mock_get_logger, capture_print):
        """Test handling standard Python exceptions"""
        handler = ErrorHandler()
        
        error = FileNotFoundError("test.txt not found")
        result = handler.handle_error(error, context="File operation")
        
        assert result['message'] == "test.txt not found"
        assert result['category'] == ErrorCategory.FILE_IO.value
        assert result['type'] == 'FileNotFoundError'
        assert len(result['suggestions']) > 0
    
    @patch('core.error_handler.get_logger')
    def test_error_categorization(self, mock_get_logger):
        """Test automatic error categorization"""
        handler = ErrorHandler()
        
        # Test various error types
        assert handler._categorize_error(FileNotFoundError()) == ErrorCategory.FILE_IO.value
        assert handler._categorize_error(PermissionError()) == ErrorCategory.PERMISSION.value
        assert handler._categorize_error(ConnectionError()) == ErrorCategory.NETWORK.value
        assert handler._categorize_error(ValueError()) == ErrorCategory.VALIDATION.value
        assert handler._categorize_error(ImportError()) == ErrorCategory.DEPENDENCY.value
        assert handler._categorize_error(Exception()) == ErrorCategory.UNKNOWN.value
    
    @patch('core.error_handler.get_logger')
    def test_severity_assessment(self, mock_get_logger):
        """Test automatic severity assessment"""
        handler = ErrorHandler()
        
        assert handler._assess_severity(SystemError()) == ErrorSeverity.CRITICAL.name
        assert handler._assess_severity(ImportError()) == ErrorSeverity.HIGH.name
        assert handler._assess_severity(ConnectionError()) == ErrorSeverity.MEDIUM.name
        assert handler._assess_severity(ValueError()) == ErrorSeverity.LOW.name
    
    @patch('core.error_handler.get_logger')
    def test_suggestion_generation(self, mock_get_logger):
        """Test automatic suggestion generation"""
        handler = ErrorHandler()
        
        # File not found suggestions
        suggestions = handler._generate_suggestions(FileNotFoundError())
        assert any("path is correct" in s for s in suggestions)
        
        # Permission error suggestions
        suggestions = handler._generate_suggestions(PermissionError())
        assert any("permissions" in s for s in suggestions)
        
        # Connection error suggestions
        suggestions = handler._generate_suggestions(ConnectionError())
        assert any("internet connection" in s for s in suggestions)
        
        # Module not found suggestions
        error = ModuleNotFoundError("No module named 'test_module'")
        suggestions = handler._generate_suggestions(error)
        assert any("pip install" in s for s in suggestions)
    
    @patch('core.error_handler.get_logger')
    def test_error_history(self, mock_get_logger):
        """Test error history management"""
        handler = ErrorHandler()
        handler.max_history_size = 3
        
        # Add errors to history
        for i in range(5):
            handler.handle_error(ValueError(f"Error {i}"))
        
        # Should only keep last 3
        assert len(handler.error_history) == 3
        assert handler.error_history[-1]['message'] == "Error 4"
    
    @patch('core.error_handler.get_logger')
    def test_error_callbacks(self, mock_get_logger):
        """Test error callback system"""
        handler = ErrorHandler()
        
        # Register callbacks
        global_callback = Mock()
        network_callback = Mock()
        
        handler.register_callback(global_callback)
        handler.register_callback(network_callback, ErrorCategory.NETWORK.value)
        
        # Trigger network error
        handler.handle_error(NetworkError("Test"))
        
        # Both callbacks should be called
        global_callback.assert_called_once()
        network_callback.assert_called_once()
        
        # Trigger non-network error
        handler.handle_error(ValueError("Test"))
        
        # Only global callback should be called again
        assert global_callback.call_count == 2
        assert network_callback.call_count == 1
    
    @patch('core.error_handler.get_logger')
    def test_error_statistics(self, mock_get_logger):
        """Test error statistics"""
        handler = ErrorHandler()
        
        # Add various errors
        handler.handle_error(NetworkError("Net 1"))
        handler.handle_error(NetworkError("Net 2"))
        handler.handle_error(ValidationError("Val 1"))
        handler.handle_error(
            FrameworkError("Critical", severity=ErrorSeverity.CRITICAL)
        )
        
        stats = handler.get_error_stats()
        
        assert stats['total_errors'] == 4
        assert stats['by_category']['Network Error'] == 2
        assert stats['by_category']['Validation Error'] == 1
        assert stats['by_severity']['MEDIUM'] == 3  # Default severity
        assert stats['by_severity']['CRITICAL'] == 1
        assert len(stats['recent_errors']) == 4
    
    @patch('core.error_handler.get_logger')
    def test_clear_history(self, mock_get_logger):
        """Test clearing error history"""
        handler = ErrorHandler()
        
        # Add errors
        handler.handle_error(ValueError("Test"))
        assert len(handler.error_history) > 0
        
        # Clear history
        handler.clear_history()
        assert len(handler.error_history) == 0
    
    @patch('core.error_handler.get_logger')
    def test_debug_mode(self, mock_get_logger, capture_print):
        """Test debug mode with traceback"""
        handler = ErrorHandler()
        handler.debug_mode = True
        handler.user_friendly_mode = False
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            result = handler.handle_error(e)
        
        assert result['traceback'] is not None
        assert "Traceback" in result['traceback']
    
    @patch('core.error_handler.get_logger')
    def test_reraise_option(self, mock_get_logger):
        """Test reraising errors after handling"""
        handler = ErrorHandler()
        
        with pytest.raises(ValueError):
            handler.handle_error(ValueError("Test"), reraise=True)

class TestErrorDecorator(TestBase):
    """Test error handling decorator"""
    
    @patch('core.error_handler.get_error_handler')
    def test_handle_errors_decorator(self, mock_get_handler):
        """Test handle_errors decorator"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler
        
        @handle_errors(context="Test function", default_return=None)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        
        assert result is None
        mock_handler.handle_error.assert_called_once()
        
        # Check error details
        call_args = mock_handler.handle_error.call_args
        assert isinstance(call_args[0][0], ValueError)
        assert call_args[0][1] == "Test function"
    
    @patch('core.error_handler.get_error_handler')
    def test_decorator_with_reraise(self, mock_get_handler):
        """Test decorator with reraise option"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler
        mock_handler.handle_error.side_effect = lambda e, c, r: e if r else None
        
        @handle_errors(reraise=True)
        def failing_function():
            raise ValueError("Test")
        
        with pytest.raises(ValueError):
            failing_function()
    
    @patch('core.error_handler.get_error_handler')
    def test_decorator_preserves_function_info(self, mock_get_handler):
        """Test decorator preserves function metadata"""
        @handle_errors()
        def test_function():
            """Test docstring"""
            return "success"
        
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test docstring"

class TestErrorContext(TestBase):
    """Test error context manager"""
    
    @patch('core.error_handler.get_error_handler')
    def test_error_context_manager(self, mock_get_handler):
        """Test ErrorContext context manager"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler
        
        with ErrorContext("Test context", suppress=True):
            raise ValueError("Test error")
        
        mock_handler.handle_error.assert_called_once()
        
        # Check error was suppressed
        call_args = mock_handler.handle_error.call_args
        assert call_args[0][1] == "Test context"
        assert call_args[0][2] is False  # not reraise when suppressed
    
    @patch('core.error_handler.get_error_handler')
    def test_context_manager_with_callback(self, mock_get_handler):
        """Test context manager with callback"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler
        callback = Mock()
        
        with ErrorContext("Test", suppress=True, callback=callback):
            error = ValueError("Test")
            raise error
        
        callback.assert_called_once_with(error)
    
    @patch('core.error_handler.get_error_handler')
    def test_context_manager_no_error(self, mock_get_handler):
        """Test context manager when no error occurs"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler
        
        with ErrorContext("Test context"):
            pass  # No error
        
        mock_handler.handle_error.assert_not_called()

class TestGlobalErrorHandler(TestBase):
    """Test global error handler instance"""
    
    def test_get_error_handler(self):
        """Test getting global error handler"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        assert handler1 is handler2
        assert isinstance(handler1, ErrorHandler)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])