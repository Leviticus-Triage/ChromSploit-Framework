#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Modul-Loader für optionale Komponenten
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class ModuleLoader:
    """
    Modul-Loader für optionale Komponenten des ChromSploit Frameworks
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert den Modul-Loader
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.modules_dir = os.path.join(PathUtils.get_root_dir(), "modules")
        self.enabled_modules = {}
        
        # Sicherstellen, dass das Verzeichnis existiert
        PathUtils.ensure_dir_exists(self.modules_dir)
    
    def log(self, level: str, message: str) -> None:
        """
        Loggt eine Nachricht
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "debug":
                self.logger.debug(message)
        else:
            print(f"{Colors.BLUE}[*] {message}{Colors.RESET}" if level == "info" else
                  f"{Colors.YELLOW}[!] {message}{Colors.RESET}" if level == "warning" else
                  f"{Colors.RED}[-] {message}{Colors.RESET}" if level == "error" else
                  f"{Colors.MAGENTA}[D] {message}{Colors.RESET}")
    
    def check_optional_deps(self) -> Dict[str, bool]:
        """
        Überprüft die Abhängigkeiten für optionale Module
        
        Returns:
            dict: Status der Abhängigkeiten für jedes Modul
        """
        self.log("info", "Überprüfe Abhängigkeiten für optionale Module...")
        
        deps_status = {
            'ai': False,
            'resilience': False
        }
        
        # AI-Abhängigkeiten überprüfen
        required_ai = ['torch', 'onnxruntime', 'xgboost', 'transformers']
        ai_ok = all(self._check_module_available(m) for m in required_ai)
        deps_status['ai'] = ai_ok
        
        # Resilience-Abhängigkeiten überprüfen
        required_resilience = ['pybreaker', 'psutil']
        resilience_ok = all(self._check_module_available(m) for m in required_resilience)
        deps_status['resilience'] = resilience_ok
        
        return deps_status
    
    def _check_module_available(self, module_name: str) -> bool:
        """
        Überprüft, ob ein Python-Modul verfügbar ist
        
        Args:
            module_name (str): Name des Moduls
            
        Returns:
            bool: True, wenn das Modul verfügbar ist, sonst False
        """
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, AttributeError):
            return False
    
    def load_optional_modules(self) -> Dict[str, bool]:
        """
        Lädt optionale Module
        
        Returns:
            dict: Status der geladenen Module
        """
        self.log("info", "Lade optionale Module...")
        
        # Abhängigkeiten überprüfen
        deps_status = self.check_optional_deps()
        
        # Module laden
        self.enabled_modules = {
            'ai': self._load_ai_module() if deps_status['ai'] else False,
            'resilience': self._load_resilience_module() if deps_status['resilience'] else False
        }
        
        # Status ausgeben
        for module, status in self.enabled_modules.items():
            if status:
                self.log("info", f"Modul '{module}' erfolgreich geladen")
            else:
                self.log("warning", f"Modul '{module}' konnte nicht geladen werden")
        
        return self.enabled_modules
    
    def _load_ai_module(self) -> bool:
        """
        Lädt das AI-Modul
        
        Returns:
            bool: True, wenn das Modul erfolgreich geladen wurde, sonst False
        """
        try:
            # Pfad zum AI-Modul
            ai_module_path = os.path.join(self.modules_dir, "ai")
            
            # Überprüfen, ob das Verzeichnis existiert
            if not os.path.exists(ai_module_path):
                self.log("warning", f"AI-Modul-Verzeichnis nicht gefunden: {ai_module_path}")
                return False
            
            # Pfad zum Python-Suchpfad hinzufügen
            if ai_module_path not in sys.path:
                sys.path.append(ai_module_path)
            
            # Versuchen, den AI-Orchestrator zu importieren
            try:
                from ai_orchestrator_v2 import AIOrchestrator
                self.log("info", "AI-Orchestrator erfolgreich importiert")
                return True
            except ImportError as e:
                self.log("warning", f"Fehler beim Importieren des AI-Orchestrators: {str(e)}")
                return False
        except Exception as e:
            self.log("error", f"Fehler beim Laden des AI-Moduls: {str(e)}")
            return False
    
    def _load_resilience_module(self) -> bool:
        """
        Lädt das Resilience-Modul
        
        Returns:
            bool: True, wenn das Modul erfolgreich geladen wurde, sonst False
        """
        try:
            # Pfad zum Resilience-Modul
            resilience_module_path = os.path.join(self.modules_dir, "resilience")
            
            # Überprüfen, ob das Verzeichnis existiert
            if not os.path.exists(resilience_module_path):
                self.log("warning", f"Resilience-Modul-Verzeichnis nicht gefunden: {resilience_module_path}")
                return False
            
            # Pfad zum Python-Suchpfad hinzufügen
            if resilience_module_path not in sys.path:
                sys.path.append(resilience_module_path)
            
            # Versuchen, den CircuitBreaker zu importieren
            try:
                from resilience_module import CircuitBreaker
                self.log("info", "CircuitBreaker erfolgreich importiert")
                return True
            except ImportError as e:
                self.log("warning", f"Fehler beim Importieren des CircuitBreakers: {str(e)}")
                return False
        except Exception as e:
            self.log("error", f"Fehler beim Laden des Resilience-Moduls: {str(e)}")
            return False
    
    def is_module_enabled(self, module_name: str) -> bool:
        """
        Überprüft, ob ein Modul aktiviert ist
        
        Args:
            module_name (str): Name des Moduls
            
        Returns:
            bool: True, wenn das Modul aktiviert ist, sonst False
        """
        return self.enabled_modules.get(module_name, False)
    
    def get_module_status(self) -> Dict[str, bool]:
        """
        Gibt den Status aller Module zurück
        
        Returns:
            dict: Status aller Module
        """
        return self.enabled_modules.copy()
