#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Detection Module
"""

from .browser_detector import (
    BrowserDetector,
    BrowserInfo,
    BrowserType,
    get_browser_detector
)

__all__ = [
    'BrowserDetector',
    'BrowserInfo',
    'BrowserType',
    'get_browser_detector'
]
