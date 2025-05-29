#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Enhanced Logger System with advanced features
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from collections import deque, defaultdict

from core.colors import Colors

class LogLevel:
    """Log level constants"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5
    
    @staticmethod
    def to_string(level: int) -> str:
        """Convert numeric level to string"""
        levels = {
            50: "CRITICAL",
            40: "ERROR",
            30: "WARNING",
            20: "INFO",
            10: "DEBUG",
            5: "TRACE"
        }
        return levels.get(level, "UNKNOWN")

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'CRITICAL': Colors.BRIGHT_RED,
        'ERROR': Colors.RED,
        'WARNING': Colors.YELLOW,
        'INFO': Colors.BLUE,
        'DEBUG': Colors.MAGENTA,
        'TRACE': Colors.CYAN
    }
    
    def __init__(self, fmt=None, datefmt=None, style='%', use_colors=True):
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors
    
    def format(self, record):
        if self.use_colors and record.levelname in self.COLORS:
            levelname = record.levelname
            record.levelname = f"{self.COLORS[levelname]}[{levelname}]{Colors.RESET}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Colors.RESET}"
        
        result = super().format(record)
        
        # Reset levelname for file output
        if hasattr(record, '_original_levelname'):
            record.levelname = record._original_levelname
        
        return result

class LogFilter:
    """Filter logs based on various criteria"""
    
    def __init__(self):
        self.filters = {
            'level': None,
            'module': None,
            'contains': None,
            'excludes': None
        }
    
    def set_level_filter(self, min_level: int):
        """Set minimum log level"""
        self.filters['level'] = min_level
    
    def set_module_filter(self, modules: List[str]):
        """Filter by module names"""
        self.filters['module'] = modules
    
    def set_text_filter(self, contains: Optional[str] = None, excludes: Optional[str] = None):
        """Filter by text content"""
        self.filters['contains'] = contains
        self.filters['excludes'] = excludes
    
    def apply(self, record: Dict[str, Any]) -> bool:
        """Apply all filters to a log record"""
        # Level filter
        if self.filters['level'] and record.get('level_no', 0) < self.filters['level']:
            return False
        
        # Module filter
        if self.filters['module'] and record.get('module') not in self.filters['module']:
            return False
        
        # Text filters
        message = record.get('message', '')
        if self.filters['contains'] and self.filters['contains'] not in message:
            return False
        if self.filters['excludes'] and self.filters['excludes'] in message:
            return False
        
        return True

class LogAnalyzer:
    """Analyze log patterns and statistics"""
    
    def __init__(self):
        self.stats = defaultdict(int)
        self.error_patterns = defaultdict(int)
        self.module_stats = defaultdict(lambda: defaultdict(int))
        
    def analyze(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze log entries and return statistics"""
        self.stats.clear()
        self.error_patterns.clear()
        self.module_stats.clear()
        
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            module = log.get('module', 'unknown')
            
            # Count by level
            self.stats[f'level_{level}'] += 1
            
            # Module statistics
            self.module_stats[module][level] += 1
            
            # Error pattern analysis
            if level in ['ERROR', 'CRITICAL']:
                # Extract error type from message
                message = log.get('message', '')
                if 'Exception' in message:
                    error_type = message.split('Exception')[0].split()[-1] + 'Exception'
                    self.error_patterns[error_type] += 1
        
        # Calculate time-based statistics
        if logs:
            timestamps = [datetime.fromisoformat(log['timestamp']) for log in logs if 'timestamp' in log]
            if timestamps:
                time_span = max(timestamps) - min(timestamps)
                logs_per_minute = len(logs) / max(time_span.total_seconds() / 60, 1)
            else:
                logs_per_minute = 0
        else:
            logs_per_minute = 0
        
        return {
            'total_logs': len(logs),
            'levels': dict(self.stats),
            'error_patterns': dict(self.error_patterns),
            'module_stats': {k: dict(v) for k, v in self.module_stats.items()},
            'logs_per_minute': round(logs_per_minute, 2)
        }

class EnhancedLogger:
    """Enhanced logger with advanced features"""
    
    def __init__(self, 
                 name: str = 'chromsploit',
                 log_level: Union[int, str] = LogLevel.INFO,
                 log_dir: str = 'logs',
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_output: bool = True,
                 json_output: bool = False):
        """
        Initialize enhanced logger
        
        Args:
            name: Logger name
            log_level: Logging level (numeric or string)
            log_dir: Directory for log files
            max_file_size: Maximum size per log file
            backup_count: Number of backup files to keep
            console_output: Enable console output
            json_output: Use JSON format for file output
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Convert string level to numeric
        if isinstance(log_level, str):
            log_level = getattr(LogLevel, log_level.upper(), LogLevel.INFO)
        
        # Setup Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LogLevel.TRACE)
        self.logger.handlers.clear()
        
        # Add custom log level for TRACE
        logging.addLevelName(LogLevel.TRACE, 'TRACE')
        
        # Log buffer for analysis
        self.log_buffer = deque(maxlen=10000)
        self.log_filter = LogFilter()
        self.log_analyzer = LogAnalyzer()
        
        # Performance metrics
        self.performance_metrics = {
            'log_count': 0,
            'start_time': time.time(),
            'last_rotation': None
        }
        
        # Setup handlers
        self._setup_console_handler(console_output, log_level)
        self._setup_file_handler(json_output, log_level)
        
        # Log initialization
        self.info(f"Enhanced logger initialized - Level: {LogLevel.to_string(log_level)}")
    
    def _setup_console_handler(self, enabled: bool, level: int):
        """Setup console output handler"""
        if not enabled:
            return
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Colored formatter for console
        console_fmt = "%(asctime)s - %(levelname)s - %(message)s"
        console_formatter = ColoredFormatter(console_fmt, datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, json_format: bool, level: int):
        """Setup file output handler with rotation"""
        # Main log file
        log_file = self.log_dir / f"{self.name}.log"
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        if json_format:
            # JSON formatter for structured logging
            file_handler.setFormatter(self._json_formatter)
        else:
            # Standard text formatter
            file_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
            file_formatter = logging.Formatter(file_fmt)
            file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
        
        # Error-only log file
        error_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(LogLevel.ERROR)
        error_handler.setFormatter(logging.Formatter(file_fmt))
        
        self.logger.addHandler(error_handler)
    
    def _json_formatter(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'level_no': record.levelno,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.logger.handlers[0].format(record)
        
        return json.dumps(log_data)
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """Internal logging method with buffer update"""
        # Log the message
        self.logger.log(level, message, *args, **kwargs)
        
        # Update metrics
        self.performance_metrics['log_count'] += 1
        
        # Add to buffer
        caller_frame = sys._getframe(2)
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': LogLevel.to_string(level),
            'level_no': level,
            'module': caller_frame.f_globals.get('__name__', 'unknown'),
            'function': caller_frame.f_code.co_name,
            'line': caller_frame.f_lineno,
            'message': message % args if args else message
        }
        self.log_buffer.append(log_entry)
    
    # Logging methods
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self._log(LogLevel.ERROR, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self._log(LogLevel.INFO, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, *args, **kwargs)
    
    def trace(self, message: str, *args, **kwargs):
        """Log trace message"""
        self._log(LogLevel.TRACE, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, **kwargs)
    
    # Advanced features
    def set_level(self, level: Union[int, str]):
        """Change logging level"""
        if isinstance(level, str):
            level = getattr(LogLevel, level.upper(), LogLevel.INFO)
        
        for handler in self.logger.handlers:
            handler.setLevel(level)
        
        self.info(f"Log level changed to {LogLevel.to_string(level)}")
    
    def get_logs(self, 
                 count: Optional[int] = None,
                 level: Optional[str] = None,
                 module: Optional[str] = None,
                 contains: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get filtered logs from buffer"""
        # Apply filters
        if level:
            self.log_filter.set_level_filter(getattr(LogLevel, level.upper(), 0))
        if module:
            self.log_filter.set_module_filter([module])
        if contains:
            self.log_filter.set_text_filter(contains=contains)
        
        # Filter logs
        filtered_logs = [log for log in self.log_buffer if self.log_filter.apply(log)]
        
        # Return requested count
        if count:
            return list(filtered_logs)[-count:]
        return list(filtered_logs)
    
    def analyze_logs(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Analyze logs and return statistics"""
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            logs = [log for log in self.log_buffer 
                   if datetime.fromisoformat(log['timestamp']) > cutoff_time]
        else:
            logs = list(self.log_buffer)
        
        return self.log_analyzer.analyze(logs)
    
    def export_logs(self, 
                    filepath: str,
                    format: str = 'json',
                    filters: Optional[Dict[str, Any]] = None) -> bool:
        """Export logs to file"""
        try:
            logs = self.get_logs()
            
            if format == 'json':
                with open(filepath, 'w') as f:
                    json.dump(logs, f, indent=2)
            elif format == 'csv':
                import csv
                with open(filepath, 'w', newline='') as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
            elif format == 'txt':
                with open(filepath, 'w') as f:
                    for log in logs:
                        f.write(f"{log['timestamp']} - {log['level']} - {log['message']}\n")
            
            self.info(f"Exported {len(logs)} logs to {filepath}")
            return True
            
        except Exception as e:
            self.error(f"Failed to export logs: {str(e)}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get logger performance metrics"""
        uptime = time.time() - self.performance_metrics['start_time']
        logs_per_second = self.performance_metrics['log_count'] / max(uptime, 1)
        
        return {
            'total_logs': self.performance_metrics['log_count'],
            'uptime_seconds': round(uptime, 2),
            'logs_per_second': round(logs_per_second, 2),
            'buffer_size': len(self.log_buffer),
            'last_rotation': self.performance_metrics['last_rotation']
        }
    
    def clear_logs(self):
        """Clear log buffer"""
        self.log_buffer.clear()
        self.info("Log buffer cleared")

# Global logger instance
_logger_instance = None

def get_logger(name: Optional[str] = None) -> EnhancedLogger:
    """Get or create logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = EnhancedLogger(name or 'chromsploit')
    return _logger_instance

# Example usage
if __name__ == "__main__":
    # Create logger
    logger = EnhancedLogger(
        name='test',
        log_level='DEBUG',
        console_output=True,
        json_output=True
    )
    
    # Test different log levels
    logger.trace("This is a trace message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test exception logging
    try:
        1 / 0
    except Exception:
        logger.exception("Division by zero error")
    
    # Analyze logs
    stats = logger.analyze_logs()
    print("\nLog Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Export logs
    logger.export_logs('test_logs.json', format='json')
    logger.export_logs('test_logs.txt', format='txt')