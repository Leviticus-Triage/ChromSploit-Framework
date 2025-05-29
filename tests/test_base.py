#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Base test utilities and fixtures
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from typing import Generator, Any

class TestBase:
    """Base class for all tests with common utilities"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Setup
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        yield
        
        # Teardown
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_input(self, monkeypatch):
        """Mock user input"""
        inputs = []
        
        def mock_input_func(prompt=""):
            if inputs:
                return inputs.pop(0)
            return ""
        
        monkeypatch.setattr('builtins.input', mock_input_func)
        return inputs
    
    @pytest.fixture
    def temp_file(self) -> Generator[Path, None, None]:
        """Create a temporary file"""
        fd, path = tempfile.mkstemp(dir=self.temp_dir)
        os.close(fd)
        yield Path(path)
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger"""
        logger = Mock()
        logger.info = Mock()
        logger.debug = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.critical = Mock()
        logger.exception = Mock()
        return logger
    
    def assert_color_removed(self, text: str) -> str:
        """Remove color codes from text for testing"""
        import re
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def create_test_config(self, **kwargs) -> dict:
        """Create test configuration"""
        default_config = {
            'debug': False,
            'log_level': 'INFO',
            'simulation_mode': True,
            'color_output': False
        }
        default_config.update(kwargs)
        return default_config

# Fixtures for common mocks
@pytest.fixture
def mock_menu_display(monkeypatch):
    """Mock menu display to prevent actual output"""
    def mock_clear():
        pass
    
    monkeypatch.setattr('os.system', lambda x: None)
    return mock_clear

@pytest.fixture
def mock_time(monkeypatch):
    """Mock time.sleep to speed up tests"""
    monkeypatch.setattr('time.sleep', lambda x: None)

@pytest.fixture
def capture_print(monkeypatch):
    """Capture print output"""
    output = []
    
    def mock_print(*args, **kwargs):
        output.append(' '.join(str(arg) for arg in args))
    
    monkeypatch.setattr('builtins.print', mock_print)
    return output