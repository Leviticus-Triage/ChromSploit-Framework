#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - AI Module
AI-powered exploit selection and decision making
"""

try:
    from .ai_orchestrator import AIOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIOrchestrator = None

__all__ = ['AIOrchestrator', 'AI_AVAILABLE']