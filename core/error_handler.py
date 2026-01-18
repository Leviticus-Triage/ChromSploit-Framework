#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Error Handler
User-friendly error messages and troubleshooting guides
"""

import logging
import traceback
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from functools import wraps
from core.colors import Colors

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error types"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    EXPLOIT = "exploit"
    PERMISSION = "permission"
    DEPENDENCY = "dependency"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Enhanced error handler with user-friendly messages"""
    
    def __init__(self):
        self.error_messages = self._init_error_messages()
        self.troubleshooting_guides = self._init_troubleshooting_guides()
    
    def _init_error_messages(self) -> Dict[str, Dict[str, str]]:
        """Initialize user-friendly error messages"""
        return {
            "configuration": {
                "missing_config": "Configuration file not found. Using defaults.",
                "invalid_config": "Invalid configuration. Please check your settings.",
                "missing_parameter": "Required parameter is missing."
            },
            "network": {
                "connection_failed": "Could not connect to target. Check network connectivity.",
                "timeout": "Connection timed out. Target may be unreachable.",
                "port_in_use": "Port is already in use. Try a different port."
            },
            "exploit": {
                "exploit_failed": "Exploit execution failed. Target may not be vulnerable.",
                "payload_generation_failed": "Could not generate payload. Check parameters.",
                "server_start_failed": "Could not start exploit server. Check permissions."
            },
            "permission": {
                "insufficient_permissions": "Insufficient permissions. Run with appropriate privileges.",
                "file_access_denied": "File access denied. Check file permissions."
            },
            "dependency": {
                "missing_module": "Required module not found. Install missing dependencies.",
                "version_mismatch": "Module version mismatch. Update dependencies."
            },
            "validation": {
                "invalid_target": "Invalid target specified.",
                "invalid_parameters": "Invalid parameters provided."
            }
        }
    
    def _init_troubleshooting_guides(self) -> Dict[str, List[str]]:
        """Initialize troubleshooting guides"""
        return {
            "connection_failed": [
                "1. Verify target URL is correct",
                "2. Check network connectivity",
                "3. Ensure firewall allows connections",
                "4. Verify target is accessible"
            ],
            "exploit_failed": [
                "1. Verify target browser and version",
                "2. Check if target is vulnerable to this CVE",
                "3. Review exploit logs for details",
                "4. Try different obfuscation level"
            ],
            "server_start_failed": [
                "1. Check if port is available",
                "2. Verify you have permission to bind to port",
                "3. Try a different port number",
                "4. Check if another process is using the port"
            ],
            "missing_module": [
                "1. Install missing dependency: pip install <module>",
                "2. Check requirements.txt for all dependencies",
                "3. Verify Python environment is correct",
                "4. Reinstall dependencies: pip install -r requirements.txt"
            ]
        }
    
    def handle_error(self, error: Exception, error_type: ErrorType = ErrorType.UNKNOWN, 
                    context: Optional[Dict[str, Any]] = None) -> str:
        """Handle error and return user-friendly message"""
        error_name = type(error).__name__
        error_message = str(error)
        
        # Try to find user-friendly message
        user_message = self._get_user_message(error_type, error_name, error_message)
        
        # Add context if available
        if context:
            user_message += f"\n{Colors.YELLOW}Context: {context}{Colors.RESET}"
        
        # Add troubleshooting guide
        troubleshooting = self._get_troubleshooting(error_type, error_name)
        if troubleshooting:
            user_message += f"\n\n{Colors.CYAN}Troubleshooting:{Colors.RESET}"
            for step in troubleshooting:
                user_message += f"\n  {step}"
        
        # Log detailed error
        logger.error(f"Error ({error_type.value}): {error_message}")
        logger.debug(traceback.format_exc())
        
        return user_message
    
    def _get_user_message(self, error_type: ErrorType, error_name: str, 
                         error_message: str) -> str:
        """Get user-friendly error message"""
        messages = self.error_messages.get(error_type.value, {})
        
        # Try to match error name
        for key, message in messages.items():
            if key.lower() in error_name.lower() or key.lower() in error_message.lower():
                return f"{Colors.RED}Error: {message}{Colors.RESET}"
        
        # Default message
        return f"{Colors.RED}Error ({error_type.value}): {error_message}{Colors.RESET}"
    
    def _get_troubleshooting(self, error_type: ErrorType, error_name: str) -> List[str]:
        """Get troubleshooting guide"""
        # Try to find specific guide
        for key, guide in self.troubleshooting_guides.items():
            if key.lower() in error_name.lower():
                return guide
        
        # Return generic guide based on error type
        if error_type == ErrorType.NETWORK:
            return self.troubleshooting_guides.get("connection_failed", [])
        elif error_type == ErrorType.EXPLOIT:
            return self.troubleshooting_guides.get("exploit_failed", [])
        elif error_type == ErrorType.DEPENDENCY:
            return self.troubleshooting_guides.get("missing_module", [])
        
        return []
    
    def format_exception(self, exception: Exception) -> str:
        """Format exception for display"""
        error_type = self._classify_error(exception)
        return self.handle_error(exception, error_type)
    
    def _classify_error(self, exception: Exception) -> ErrorType:
        """Classify error type"""
        error_name = type(exception).__name__.lower()
        error_message = str(exception).lower()
        
        if any(keyword in error_name or keyword in error_message 
               for keyword in ["config", "parameter", "setting"]):
            return ErrorType.CONFIGURATION
        
        if any(keyword in error_name or keyword in error_message 
               for keyword in ["connection", "network", "timeout", "socket"]):
            return ErrorType.NETWORK
        
        if any(keyword in error_name or keyword in error_message 
               for keyword in ["permission", "access", "denied", "forbidden"]):
            return ErrorType.PERMISSION
        
        if any(keyword in error_name or keyword in error_message 
               for keyword in ["import", "module", "package", "dependency"]):
            return ErrorType.DEPENDENCY
        
        if any(keyword in error_name or keyword in error_message 
               for keyword in ["validation", "invalid", "check"]):
            return ErrorType.VALIDATION
        
        return ErrorType.UNKNOWN


def handle_errors(func: Callable) -> Callable:
    """Decorator for error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = get_error_handler()
            error_type = handler._classify_error(e)
            message = handler.handle_error(e, error_type)
            print(message)
            return None
    return wrapper


# Singleton instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler
