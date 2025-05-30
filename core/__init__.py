#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Core modules package
"""

# Core components
from .colors import Colors
from .config import Config
from .logger import Logger
from .utils import Utils
from .path_utils import PathUtils
from .menu import Menu, MenuItem

# Enhanced components
from .enhanced_logger import EnhancedLogger, get_logger, LogLevel
from .enhanced_menu import EnhancedMenu, EnhancedMenuItem, ProgressBar
from .error_handler import (
    ErrorHandler, get_error_handler, handle_errors,
    ErrorContext, ErrorSeverity, ErrorCategory
)
from .simulation import (
    SimulationMode, SimulationEngine, SimulationResult,
    SimulatedNetwork, SimulatedExploit, SimulatedFileSystem,
    get_simulation_engine
)
from .reporting import (
    ReportGenerator, SecurityReport, ReportSeverity, ReportStatus,
    ExploitEvidence, TargetInfo, VulnerabilityDetails,
    ScreenshotCapture, get_report_generator
)

__all__ = [
    # Basic components
    "Colors",
    "Config",
    "Logger",
    "Utils",
    "PathUtils",
    "Menu",
    "MenuItem",
    
    # Enhanced components
    "EnhancedLogger",
    "get_logger",
    "LogLevel",
    "EnhancedMenu",
    "EnhancedMenuItem",
    "ProgressBar",
    "ErrorHandler",
    "get_error_handler",
    "handle_errors",
    "ErrorContext",
    "ErrorSeverity",
    "ErrorCategory",
    
    # Simulation
    "SimulationMode",
    "SimulationEngine",
    "SimulationResult",
    "SimulatedNetwork",
    "SimulatedExploit",
    "SimulatedFileSystem",
    "get_simulation_engine",
]