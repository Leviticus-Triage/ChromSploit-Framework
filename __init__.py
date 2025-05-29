#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
A modular educational framework for learning about browser security

FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY
"""

__version__ = "2.0.0"
__author__ = "Leviticus-Triage"
__license__ = "Apache 2.0"
__description__ = "A modular educational framework for learning about browser security"

# Import main components
from core.simulation import SimulationMode, SimulationEngine, get_simulation_engine
from core.enhanced_logger import EnhancedLogger, get_logger, LogLevel
from core.error_handler import (
    ErrorHandler, get_error_handler, handle_errors,
    ErrorContext, ErrorSeverity, ErrorCategory,
    FrameworkError, NetworkError, ConfigurationError,
    ValidationError, PermissionError, DependencyError
)
from core.enhanced_menu import EnhancedMenu, EnhancedMenuItem, ProgressBar

# Package metadata
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    "__description__",
    
    # Simulation
    "SimulationMode",
    "SimulationEngine", 
    "get_simulation_engine",
    
    # Logging
    "EnhancedLogger",
    "get_logger",
    "LogLevel",
    
    # Error handling
    "ErrorHandler",
    "get_error_handler",
    "handle_errors",
    "ErrorContext",
    "ErrorSeverity",
    "ErrorCategory",
    "FrameworkError",
    "NetworkError",
    "ConfigurationError",
    "ValidationError",
    "PermissionError",
    "DependencyError",
    
    # UI
    "EnhancedMenu",
    "EnhancedMenuItem",
    "ProgressBar",
]