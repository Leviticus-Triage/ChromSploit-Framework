#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Enhanced Error Handling System
"""

import sys
import traceback
import functools
from typing import Optional, Type, Callable, Any, Dict, List, Union
from datetime import datetime
from enum import Enum

from core.colors import Colors
from core.enhanced_logger import get_logger

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 1      # Minor issues, can continue
    MEDIUM = 2   # Important issues, may affect functionality
    HIGH = 3     # Critical issues, feature unavailable
    CRITICAL = 4 # System-wide issues, may need restart

class ErrorCategory(Enum):
    """Error categories for better organization"""
    NETWORK = "Network Error"
    FILE_IO = "File I/O Error"
    CONFIGURATION = "Configuration Error"
    VALIDATION = "Validation Error"
    PERMISSION = "Permission Error"
    DEPENDENCY = "Dependency Error"
    USER_INPUT = "User Input Error"
    SYSTEM = "System Error"
    UNKNOWN = "Unknown Error"

class FrameworkError(Exception):
    """Base exception for ChromSploit Framework"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging"""
        return {
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.name,
            'details': self.details,
            'suggestions': self.suggestions,
            'timestamp': self.timestamp.isoformat()
        }

# Specific error types
class NetworkError(FrameworkError):
    """Network-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.NETWORK, **kwargs)

class ConfigurationError(FrameworkError):
    """Configuration-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.CONFIGURATION, **kwargs)

class ValidationError(FrameworkError):
    """Validation-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)

class PermissionError(FrameworkError):
    """Permission-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.PERMISSION, **kwargs)

class DependencyError(FrameworkError):
    """Dependency-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.DEPENDENCY, **kwargs)

class ErrorHandler:
    """Central error handling system"""
    
    def __init__(self):
        self.logger = get_logger()
        self.error_history = []
        self.error_callbacks = {}
        self.max_history_size = 1000
        self.user_friendly_mode = True
        self.debug_mode = False
    
    def handle_error(self, 
                     error: Exception,
                     context: Optional[str] = None,
                     reraise: bool = False) -> Optional[Dict[str, Any]]:
        """
        Handle an error with appropriate logging and user feedback
        
        Args:
            error: The exception to handle
            context: Additional context about where the error occurred
            reraise: Whether to re-raise the error after handling
        
        Returns:
            Error details dictionary
        """
        error_info = self._extract_error_info(error, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Add to history
        self._add_to_history(error_info)
        
        # Display to user
        if self.user_friendly_mode:
            self._display_user_friendly_error(error_info)
        else:
            self._display_technical_error(error_info)
        
        # Execute callbacks
        self._execute_callbacks(error_info)
        
        # Re-raise if requested
        if reraise:
            raise error
        
        return error_info
    
    def _extract_error_info(self, error: Exception, context: Optional[str]) -> Dict[str, Any]:
        """Extract detailed error information"""
        if isinstance(error, FrameworkError):
            error_info = error.to_dict()
            error_info['context'] = context
            error_info['traceback'] = traceback.format_exc() if self.debug_mode else None
        else:
            # Handle standard exceptions
            error_info = {
                'message': str(error),
                'category': self._categorize_error(error),
                'severity': self._assess_severity(error),
                'context': context,
                'type': type(error).__name__,
                'traceback': traceback.format_exc() if self.debug_mode else None,
                'timestamp': datetime.now().isoformat(),
                'suggestions': self._generate_suggestions(error)
            }
        
        return error_info
    
    def _categorize_error(self, error: Exception) -> str:
        """Categorize standard exceptions"""
        error_mapping = {
            FileNotFoundError: ErrorCategory.FILE_IO,
            PermissionError: ErrorCategory.PERMISSION,
            ConnectionError: ErrorCategory.NETWORK,
            TimeoutError: ErrorCategory.NETWORK,
            ValueError: ErrorCategory.VALIDATION,
            KeyError: ErrorCategory.CONFIGURATION,
            ImportError: ErrorCategory.DEPENDENCY,
            ModuleNotFoundError: ErrorCategory.DEPENDENCY
        }
        
        for error_type, category in error_mapping.items():
            if isinstance(error, error_type):
                return category.value
        
        return ErrorCategory.UNKNOWN.value
    
    def _assess_severity(self, error: Exception) -> str:
        """Assess error severity"""
        critical_errors = (SystemError, MemoryError, SystemExit)
        high_errors = (ImportError, ModuleNotFoundError, PermissionError)
        medium_errors = (ConnectionError, TimeoutError, FileNotFoundError)
        
        if isinstance(error, critical_errors):
            return ErrorSeverity.CRITICAL.name
        elif isinstance(error, high_errors):
            return ErrorSeverity.HIGH.name
        elif isinstance(error, medium_errors):
            return ErrorSeverity.MEDIUM.name
        else:
            return ErrorSeverity.LOW.name
    
    def _generate_suggestions(self, error: Exception) -> List[str]:
        """Generate helpful suggestions based on error type"""
        suggestions = []
        
        if isinstance(error, FileNotFoundError):
            suggestions.extend([
                "Check if the file path is correct",
                "Ensure the file exists at the specified location",
                "Verify you have read permissions for the file"
            ])
        elif isinstance(error, PermissionError):
            suggestions.extend([
                "Run the application with appropriate permissions",
                "Check file/directory permissions",
                "Ensure you have necessary access rights"
            ])
        elif isinstance(error, ConnectionError):
            suggestions.extend([
                "Check your internet connection",
                "Verify the target server is accessible",
                "Check firewall settings",
                "Try again later if the service is down"
            ])
        elif isinstance(error, ModuleNotFoundError):
            module_name = str(error).split("'")[1] if "'" in str(error) else "unknown"
            suggestions.extend([
                f"Install the missing module: pip install {module_name}",
                "Check if you're in the correct virtual environment",
                "Verify all dependencies are installed: pip install -r requirements.txt"
            ])
        
        return suggestions
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error with appropriate level"""
        severity = error_info.get('severity', 'MEDIUM')
        message = f"[{error_info.get('category', 'Unknown')}] {error_info.get('message', 'Unknown error')}"
        
        if error_info.get('context'):
            message = f"{error_info['context']}: {message}"
        
        if severity == ErrorSeverity.CRITICAL.name:
            self.logger.critical(message)
        elif severity == ErrorSeverity.HIGH.name:
            self.logger.error(message)
        elif severity == ErrorSeverity.MEDIUM.name:
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Log full traceback in debug mode
        if self.debug_mode and error_info.get('traceback'):
            self.logger.debug(f"Traceback:\n{error_info['traceback']}")
    
    def _add_to_history(self, error_info: Dict[str, Any]):
        """Add error to history with size limit"""
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def _display_user_friendly_error(self, error_info: Dict[str, Any]):
        """Display error in user-friendly format"""
        severity_colors = {
            ErrorSeverity.LOW.name: Colors.YELLOW,
            ErrorSeverity.MEDIUM.name: Colors.YELLOW,
            ErrorSeverity.HIGH.name: Colors.RED,
            ErrorSeverity.CRITICAL.name: Colors.BRIGHT_RED
        }
        
        color = severity_colors.get(error_info.get('severity', 'MEDIUM'), Colors.RED)
        
        print(f"\n{color}{'═' * 60}{Colors.RESET}")
        print(f"{color}⚠  Error Detected{Colors.RESET}")
        print(f"{color}{'═' * 60}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_WHITE}What happened:{Colors.RESET}")
        print(f"  {error_info.get('message', 'An unknown error occurred')}")
        
        if error_info.get('context'):
            print(f"\n{Colors.BRIGHT_WHITE}Where:{Colors.RESET}")
            print(f"  {error_info['context']}")
        
        suggestions = error_info.get('suggestions', [])
        if suggestions:
            print(f"\n{Colors.BRIGHT_WHITE}Suggestions:{Colors.RESET}")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print(f"\n{color}{'─' * 60}{Colors.RESET}")
        
        if self.debug_mode:
            print(f"\n{Colors.DARK_GRAY}Error Type: {error_info.get('type', 'Unknown')}")
            print(f"Category: {error_info.get('category', 'Unknown')}")
            print(f"Severity: {error_info.get('severity', 'Unknown')}")
            print(f"Time: {error_info.get('timestamp', 'Unknown')}{Colors.RESET}")
    
    def _display_technical_error(self, error_info: Dict[str, Any]):
        """Display error in technical format"""
        print(f"\n{Colors.RED}[ERROR] {error_info}{Colors.RESET}")
        if error_info.get('traceback'):
            print(f"\n{Colors.DARK_GRAY}{error_info['traceback']}{Colors.RESET}")
    
    def _execute_callbacks(self, error_info: Dict[str, Any]):
        """Execute registered error callbacks"""
        category = error_info.get('category', ErrorCategory.UNKNOWN.value)
        
        # Execute category-specific callbacks
        if category in self.error_callbacks:
            for callback in self.error_callbacks[category]:
                try:
                    callback(error_info)
                except Exception as e:
                    self.logger.error(f"Error in callback: {str(e)}")
        
        # Execute global callbacks
        if 'global' in self.error_callbacks:
            for callback in self.error_callbacks['global']:
                try:
                    callback(error_info)
                except Exception as e:
                    self.logger.error(f"Error in global callback: {str(e)}")
    
    def register_callback(self, 
                         callback: Callable[[Dict[str, Any]], None],
                         category: Optional[str] = None):
        """Register an error callback"""
        category = category or 'global'
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        stats = {
            'total_errors': len(self.error_history),
            'by_category': {},
            'by_severity': {},
            'recent_errors': self.error_history[-10:]
        }
        
        for error in self.error_history:
            category = error.get('category', 'Unknown')
            severity = error.get('severity', 'Unknown')
            
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        return stats
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()

# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get or create error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

# Decorator for automatic error handling
def handle_errors(
    context: Optional[str] = None,
    reraise: bool = False,
    default_return: Any = None
):
    """
    Decorator for automatic error handling
    
    Args:
        context: Context string for the operation
        reraise: Whether to re-raise exceptions
        default_return: Default value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = get_error_handler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ctx = context or f"{func.__module__}.{func.__name__}"
                handler.handle_error(e, ctx, reraise)
                return default_return
        return wrapper
    return decorator

# Context manager for error handling
class ErrorContext:
    """Context manager for error handling blocks"""
    
    def __init__(self, 
                 context: str,
                 suppress: bool = False,
                 callback: Optional[Callable] = None):
        self.context = context
        self.suppress = suppress
        self.callback = callback
        self.handler = get_error_handler()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.handler.handle_error(exc_val, self.context, not self.suppress)
            if self.callback:
                self.callback(exc_val)
        return self.suppress

# Example usage
if __name__ == "__main__":
    # Initialize error handler
    handler = get_error_handler()
    handler.debug_mode = True
    
    # Test framework errors
    try:
        raise NetworkError(
            "Failed to connect to server",
            severity=ErrorSeverity.HIGH,
            details={'host': 'example.com', 'port': 443},
            suggestions=[
                "Check your internet connection",
                "Verify the server is online",
                "Check firewall settings"
            ]
        )
    except FrameworkError as e:
        handler.handle_error(e, "Connection test")
    
    # Test decorator
    @handle_errors(context="Math operation", default_return=0)
    def divide(a, b):
        return a / b
    
    result = divide(10, 0)  # Will handle the error gracefully
    print(f"Result: {result}")
    
    # Test context manager
    with ErrorContext("File operation", suppress=True):
        with open("nonexistent.txt", "r") as f:
            content = f.read()
    
    # Get error statistics
    stats = handler.get_error_stats()
    print(f"\nError Statistics: {stats}")