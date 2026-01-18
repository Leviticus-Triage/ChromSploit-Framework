#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing Module
"""

from .browser_test_automation import (
    BrowserTestAutomation,
    BrowserTestResult,
    BrowserTestStatus,
    get_browser_test_automation
)

__all__ = [
    'BrowserTestAutomation',
    'BrowserTestResult',
    'BrowserTestStatus',
    'get_browser_test_automation'
]
