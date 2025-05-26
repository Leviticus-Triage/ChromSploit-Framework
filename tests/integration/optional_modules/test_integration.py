#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Integrationstests für optionale Module
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import json
import time
import unittest
from typing import Dict, List, Any, Optional, Tuple, Union

# Pfad zum Hauptverzeichnis hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.logger import Logger
from core.config import Config
from core.module_loader import ModuleLoader
from core.utils import Utils
from core.path_utils import PathUtils

class OptionalModulesIntegrationTest(unittest.TestCase):
    """
    Integrationstests für optionale Module
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Initialisiert die Testumgebung
        """
        # Logger initialisieren
        cls.logger = Logger(log_file=os.path.join(PathUtils.get_logs_dir(), "integration_test.log"))
        cls.logger.info("Starte Integrationstests für optionale Module")
        
        # Konfiguration initialisieren
        cls.config = Config(config_file=os.path.join(PathUtils.get_config_dir(), "test_config.json"))
        
        # Modul-Loader initialisieren
        cls.module_loader = ModuleLoader(logger=cls.logger)
        
        # Testverzeichnis erstellen
        cls.test_dir = os.path.join(PathUtils.get_root_dir(), "tests", "integration", "optional_modules")
        PathUtils.ensure_dir_exists(cls.test_dir)
    
    def setUp(self):
        """
        Wird vor jedem Test ausgeführt
        """
        self.logger.info(f"Starte Test: {self._testMethodName}")
    
    def tearDown(self):
        """
        Wird nach jedem Test ausgeführt
        """
        self.logger.info(f"Test abgeschlossen: {self._testMethodName}")
    
    def test_module_loader_initialization(self):
        """
        Testet die Initialisierung des Modul-Loaders
        """
        self.assertIsNotNone(self.module_loader)
        self.logger.info("Modul-Loader erfolgreich initialisiert")
    
    def test_dependency_check(self):
        """
        Testet die Abhängigkeitsprüfung
        """
        deps_status = self.module_loader.check_optional_deps()
        self.assertIsInstance(deps_status, dict)
        self.assertIn('ai', deps_status)
        self.assertIn('resilience', deps_status)
        self.logger.info(f"Abhängigkeitsstatus: {deps_status}")
    
    def test_module_loading(self):
        """
        Testet das Laden der optionalen Module
        """
        module_status = self.module_loader.load_optional_modules()
        self.assertIsInstance(module_status, dict)
        self.assertIn('ai', module_status)
        self.assertIn('resilience', module_status)
        self.logger.info(f"Modulstatus: {module_status}")
    
    def test_ai_module_fallback(self):
        """
        Testet den Fallback-Mechanismus des AI-Moduls
        """
        # AI-Modul deaktiviert -> Legacy CVE-Matcher
        self.config.set('ai.enable', False)
        self.config.save()
        
        # Fallback-Test
        try:
            # Direkter Import, um zu testen, ob das Modul verfügbar ist
            sys.path.append(os.path.join(PathUtils.get_root_dir(), "modules"))
            from ai.ai_orchestrator_v2 import AIOrchestrator
            
            # Testziel erstellen
            target_data = {
                "browser": "chrome",
                "os_type": "windows",
                "version": "125.0.0.0",
                "description": "Windows 10 mit Chrome Browser"
            }
            
            # AI-Orchestrator initialisieren
            orchestrator = AIOrchestrator(logger=self.logger)
            
            # Exploit empfehlen
            exploit = orchestrator.recommend_exploit(target_data)
            
            # Überprüfen, ob ein Exploit empfohlen wurde
            self.assertIsNotNone(exploit)
            self.logger.info(f"Empfohlener Exploit: {exploit}")
            
            # Überprüfen, ob die Legacy-Methode verwendet wurde
            results = orchestrator.analyze_target(target_data)
            self.assertIn("method", results)
            self.assertEqual(results["method"], "legacy_cve_matcher")
            self.logger.info("Legacy CVE-Matcher wurde als Fallback verwendet")
        except ImportError:
            self.logger.warning("AI-Modul ist nicht verfügbar, Test übersprungen")
            self.skipTest("AI-Modul ist nicht verfügbar")
    
    def test_resilience_module_fallback(self):
        """
        Testet den Fallback-Mechanismus des Resilience-Moduls
        """
        # Resilience-Modul deaktiviert -> Standardverhalten
        self.config.set('resilience.enable', False)
        self.config.save()
        
        # Fallback-Test
        try:
            # Direkter Import, um zu testen, ob das Modul verfügbar ist
            sys.path.append(os.path.join(PathUtils.get_root_dir(), "modules"))
            from resilience.resilience_module import NetworkResilience
            
            # NetworkResilience initialisieren
            network_resilience = NetworkResilience()
            
            # Endpunkt registrieren
            network_resilience.register_endpoint(
                "test_endpoint",
                "127.0.0.1:8080",
                ["127.0.0.1:8081", "127.0.0.1:8082"]
            )
            
            # Endpunkt überprüfen (sollte fehlschlagen und zum Fallback wechseln)
            result = network_resilience.check_endpoint("test_endpoint")
            
            # Überprüfen, ob der Endpunkt gewechselt wurde
            current_endpoint = network_resilience.get_endpoint("test_endpoint")
            self.assertNotEqual(current_endpoint, "127.0.0.1:8080")
            self.logger.info(f"Endpunkt wurde zu {current_endpoint} gewechselt")
        except ImportError:
            self.logger.warning("Resilience-Modul ist nicht verfügbar, Test übersprungen")
            self.skipTest("Resilience-Modul ist nicht verfügbar")
    
    def test_ngrok_fallback(self):
        """
        Testet den Fallback-Mechanismus für Ngrok
        """
        # Ngrok nicht installiert -> Lokaler Listener
        # Simulieren, dass Ngrok nicht verfügbar ist
        original_is_tool_available = Utils.is_tool_available
        
        def mock_is_tool_available(tool_name):
            if tool_name == "ngrok":
                return False
            return original_is_tool_available(tool_name)
        
        Utils.is_tool_available = mock_is_tool_available
        
        # Fallback-Test
        try:
            from tools.ngrok_integration import NgrokIntegration
            
            # NgrokIntegration initialisieren
            ngrok = NgrokIntegration(logger=self.logger)
            
            # Tunnel erstellen (sollte fehlschlagen und zum lokalen Listener wechseln)
            tunnel = ngrok.create_tunnel(8080, "http")
            
            # Überprüfen, ob ein lokaler Listener verwendet wurde
            self.assertIsNone(tunnel)
            self.logger.info("Lokaler Listener wurde als Fallback verwendet")
        except ImportError:
            self.logger.warning("Ngrok-Integration ist nicht verfügbar, Test übersprungen")
            self.skipTest("Ngrok-Integration ist nicht verfügbar")
        finally:
            # Ursprüngliche Funktion wiederherstellen
            Utils.is_tool_available = original_is_tool_available
    
    def test_ollvm_fallback(self):
        """
        Testet den Fallback-Mechanismus für OLLVM
        """
        # OLLVM fehlgeschlagen -> XOR-Obfuscation
        # Simulieren, dass OLLVM nicht verfügbar ist
        original_is_tool_available = Utils.is_tool_available
        
        def mock_is_tool_available(tool_name):
            if tool_name == "docker" or tool_name == "clang++":
                return False
            return original_is_tool_available(tool_name)
        
        Utils.is_tool_available = mock_is_tool_available
        
        # Fallback-Test
        try:
            from tools.ollvm_integration import OLLVMIntegration
            
            # OLLVMIntegration initialisieren
            ollvm = OLLVMIntegration(logger=self.logger)
            
            # Code obfuskieren (sollte fehlschlagen und zur XOR-Obfuskierung wechseln)
            test_code = "int main() { return 0; }"
            result = ollvm.obfuscate_c_code(test_code, "test.c")
            
            # Überprüfen, ob XOR-Obfuskierung verwendet wurde
            self.assertIsNotNone(result)
            self.assertIn("xor_obfuscation", result)
            self.logger.info("XOR-Obfuskierung wurde als Fallback verwendet")
        except ImportError:
            self.logger.warning("OLLVM-Integration ist nicht verfügbar, Test übersprungen")
            self.skipTest("OLLVM-Integration ist nicht verfügbar")
        finally:
            # Ursprüngliche Funktion wiederherstellen
            Utils.is_tool_available = original_is_tool_available
    
    def test_sliver_fallback(self):
        """
        Testet den Fallback-Mechanismus für Sliver
        """
        # Sliver nicht verfügbar -> Metasploit-Fallback
        # Simulieren, dass Sliver nicht verfügbar ist
        original_is_tool_available = Utils.is_tool_available
        
        def mock_is_tool_available(tool_name):
            if tool_name == "sliver":
                return False
            return original_is_tool_available(tool_name)
        
        Utils.is_tool_available = mock_is_tool_available
        
        # Fallback-Test
        try:
            from tools.sliver_integration import SliverIntegration
            
            # SliverIntegration initialisieren
            sliver = SliverIntegration(logger=self.logger)
            
            # Implant generieren (sollte fehlschlagen und zu Metasploit wechseln)
            result = sliver.generate_implant("windows", "amd64")
            
            # Überprüfen, ob Metasploit verwendet wurde
            self.assertIsNotNone(result)
            self.assertIn("metasploit_fallback", result)
            self.logger.info("Metasploit wurde als Fallback verwendet")
        except ImportError:
            self.logger.warning("Sliver-Integration ist nicht verfügbar, Test übersprungen")
            self.skipTest("Sliver-Integration ist nicht verfügbar")
        finally:
            # Ursprüngliche Funktion wiederherstellen
            Utils.is_tool_available = original_is_tool_available
    
    def test_config_toggle(self):
        """
        Testet das Umschalten der Konfigurationsflags
        """
        # AI-Modul umschalten
        original_ai_status = self.config.get('ai.enable', False)
        self.config.set('ai.enable', not original_ai_status)
        self.config.save()
        
        # Überprüfen, ob die Änderung gespeichert wurde
        new_ai_status = self.config.get('ai.enable', False)
        self.assertNotEqual(original_ai_status, new_ai_status)
        self.logger.info(f"AI-Modul-Status geändert: {original_ai_status} -> {new_ai_status}")
        
        # Resilience-Modul umschalten
        original_resilience_status = self.config.get('resilience.enable', False)
        self.config.set('resilience.enable', not original_resilience_status)
        self.config.save()
        
        # Überprüfen, ob die Änderung gespeichert wurde
        new_resilience_status = self.config.get('resilience.enable', False)
        self.assertNotEqual(original_resilience_status, new_resilience_status)
        self.logger.info(f"Resilience-Modul-Status geändert: {original_resilience_status} -> {new_resilience_status}")
        
        # Zurücksetzen
        self.config.set('ai.enable', original_ai_status)
        self.config.set('resilience.enable', original_resilience_status)
        self.config.save()
    
    def test_logging_format(self):
        """
        Testet das Logging-Format
        """
        # Testlog erstellen
        test_log_file = os.path.join(self.test_dir, "test_log.json")
        
        # Log-Eintrag erstellen
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "module": "ai_decision",
            "status": "fallback_activated",
            "reason": "torch_not_available",
            "target": "192.168.1.105"
        }
        
        # Log-Eintrag speichern
        with open(test_log_file, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        # Überprüfen, ob die Datei erstellt wurde
        self.assertTrue(os.path.exists(test_log_file))
        self.logger.info(f"Log-Datei erstellt: {test_log_file}")
        
        # Log-Eintrag laden und überprüfen
        with open(test_log_file, "r") as f:
            loaded_entry = json.load(f)
        
        self.assertEqual(loaded_entry["module"], "ai_decision")
        self.assertEqual(loaded_entry["status"], "fallback_activated")
        self.assertEqual(loaded_entry["reason"], "torch_not_available")
        self.assertEqual(loaded_entry["target"], "192.168.1.105")
        self.logger.info("Log-Format ist korrekt")

if __name__ == "__main__":
    unittest.main()
