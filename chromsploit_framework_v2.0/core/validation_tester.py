#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Validierungsmodul für Funktionalitäts- und Benutzererfahrungstests
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import subprocess
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class ValidationTester:
    """
    Validierungsmodul für Funktionalitäts- und Benutzererfahrungstests des ChromSploit Frameworks
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert das Validierungsmodul
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.tests_dir = os.path.join(PathUtils.get_root_dir(), "tests")
        self.results_dir = os.path.join(self.tests_dir, "results")
        
        # Sicherstellen, dass die Verzeichnisse existieren
        PathUtils.ensure_dir_exists(self.tests_dir)
        PathUtils.ensure_dir_exists(self.results_dir)
        
        # Teststatistiken
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
    
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
    
    def test_core_components(self) -> Dict[str, Any]:
        """
        Testet die Kernkomponenten des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste Kernkomponenten...")
        
        results = {
            "logger": self._test_logger(),
            "config": self._test_config(),
            "utils": self._test_utils(),
            "path_utils": self._test_path_utils(),
            "live_monitor": self._test_live_monitor()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"Kernkomponententests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_logger(self) -> Dict[str, Any]:
        """
        Testet das Logger-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            from core.logger import Logger
            
            # Temporäre Log-Datei erstellen
            log_file = os.path.join(self.results_dir, "test_logger.log")
            
            # Logger initialisieren
            logger = Logger(log_file=log_file, console=True)
            
            # Logs schreiben
            logger.debug("Debug-Nachricht")
            logger.info("Info-Nachricht")
            logger.warning("Warning-Nachricht")
            logger.error("Error-Nachricht")
            logger.critical("Critical-Nachricht")
            
            # Überprüfen, ob die Log-Datei existiert und Inhalte hat
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                return {
                    "component": "Logger",
                    "status": "passed",
                    "message": "Logger-Test erfolgreich"
                }
            else:
                return {
                    "component": "Logger",
                    "status": "failed",
                    "message": "Log-Datei existiert nicht oder ist leer"
                }
        except Exception as e:
            return {
                "component": "Logger",
                "status": "failed",
                "message": f"Logger-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_config(self) -> Dict[str, Any]:
        """
        Testet das Konfigurationsmodul
        
        Returns:
            dict: Testergebnis
        """
        try:
            from core.config import Config
            
            # Temporäre Konfigurationsdatei erstellen
            config_file = os.path.join(self.results_dir, "test_config.json")
            
            # Konfiguration initialisieren
            config = Config(config_file=config_file)
            
            # Konfiguration setzen
            config.set("test_key", "test_value")
            config.set("test_section.nested_key", 123)
            
            # Konfiguration speichern
            config.save()
            
            # Neue Konfigurationsinstanz erstellen und laden
            config2 = Config(config_file=config_file)
            config2.load()
            
            # Überprüfen, ob die Konfiguration korrekt geladen wurde
            if (config2.get("test_key") == "test_value" and 
                config2.get("test_section.nested_key") == 123):
                return {
                    "component": "Config",
                    "status": "passed",
                    "message": "Konfigurations-Test erfolgreich"
                }
            else:
                return {
                    "component": "Config",
                    "status": "failed",
                    "message": "Konfiguration wurde nicht korrekt geladen"
                }
        except Exception as e:
            return {
                "component": "Config",
                "status": "failed",
                "message": f"Konfigurations-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_utils(self) -> Dict[str, Any]:
        """
        Testet das Utils-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            from core.utils import Utils
            
            # Einige Utility-Funktionen testen
            is_tool_available = Utils.is_tool_available("python")
            random_string = Utils.generate_random_string(10)
            
            if is_tool_available and len(random_string) == 10:
                return {
                    "component": "Utils",
                    "status": "passed",
                    "message": "Utils-Test erfolgreich"
                }
            else:
                return {
                    "component": "Utils",
                    "status": "failed",
                    "message": "Utils-Funktionen liefern unerwartete Ergebnisse"
                }
        except Exception as e:
            return {
                "component": "Utils",
                "status": "failed",
                "message": f"Utils-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_path_utils(self) -> Dict[str, Any]:
        """
        Testet das PathUtils-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            from core.path_utils import PathUtils
            
            # Einige PathUtils-Funktionen testen
            root_dir = PathUtils.get_root_dir()
            test_dir = os.path.join(self.results_dir, "test_path_utils")
            
            # Verzeichnis erstellen
            PathUtils.ensure_dir_exists(test_dir)
            
            if os.path.exists(root_dir) and os.path.exists(test_dir):
                return {
                    "component": "PathUtils",
                    "status": "passed",
                    "message": "PathUtils-Test erfolgreich"
                }
            else:
                return {
                    "component": "PathUtils",
                    "status": "failed",
                    "message": "PathUtils-Funktionen liefern unerwartete Ergebnisse"
                }
        except Exception as e:
            return {
                "component": "PathUtils",
                "status": "failed",
                "message": f"PathUtils-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_live_monitor(self) -> Dict[str, Any]:
        """
        Testet das LiveMonitor-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            from core.live_monitor import LiveMonitor
            
            # LiveMonitor initialisieren
            monitor = LiveMonitor()
            
            # Monitoring starten
            monitor.start_monitoring()
            
            # Log-Einträge hinzufügen
            monitor.add_log_entry("INFO", "Test-Info-Nachricht")
            monitor.add_log_entry("WARNING", "Test-Warning-Nachricht")
            monitor.add_log_entry("ERROR", "Test-Error-Nachricht")
            
            # Kurz warten, damit die Logs verarbeitet werden können
            time.sleep(2)
            
            # Monitoring stoppen
            monitor.stop_monitoring()
            
            return {
                "component": "LiveMonitor",
                "status": "passed",
                "message": "LiveMonitor-Test erfolgreich"
            }
        except Exception as e:
            return {
                "component": "LiveMonitor",
                "status": "failed",
                "message": f"LiveMonitor-Test fehlgeschlagen: {str(e)}"
            }
    
    def test_ui_components(self) -> Dict[str, Any]:
        """
        Testet die UI-Komponenten des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste UI-Komponenten...")
        
        results = {
            "main_menu": self._test_main_menu(),
            "cve_menu": self._test_cve_menu()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"UI-Komponententests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_main_menu(self) -> Dict[str, Any]:
        """
        Testet das Hauptmenü
        
        Returns:
            dict: Testergebnis
        """
        try:
            from ui.main_menu import MainMenu
            
            # Hauptmenü initialisieren (ohne tatsächliche Anzeige)
            menu = MainMenu(display_menu=False)
            
            # Überprüfen, ob die Menüoptionen vorhanden sind
            if hasattr(menu, "menu_options") and len(menu.menu_options) > 0:
                return {
                    "component": "MainMenu",
                    "status": "passed",
                    "message": "MainMenu-Test erfolgreich"
                }
            else:
                return {
                    "component": "MainMenu",
                    "status": "failed",
                    "message": "MainMenu hat keine Menüoptionen"
                }
        except Exception as e:
            return {
                "component": "MainMenu",
                "status": "failed",
                "message": f"MainMenu-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_cve_menu(self) -> Dict[str, Any]:
        """
        Testet das CVE-Menü
        
        Returns:
            dict: Testergebnis
        """
        try:
            from ui.cve_menu import CVEMenu
            
            # CVE-Menü initialisieren (ohne tatsächliche Anzeige)
            menu = CVEMenu(display_menu=False)
            
            # Überprüfen, ob die CVE-Optionen vorhanden sind
            if hasattr(menu, "cve_options") and len(menu.cve_options) > 0:
                return {
                    "component": "CVEMenu",
                    "status": "passed",
                    "message": "CVEMenu-Test erfolgreich"
                }
            else:
                return {
                    "component": "CVEMenu",
                    "status": "failed",
                    "message": "CVEMenu hat keine CVE-Optionen"
                }
        except Exception as e:
            return {
                "component": "CVEMenu",
                "status": "failed",
                "message": f"CVEMenu-Test fehlgeschlagen: {str(e)}"
            }
    
    def test_exploits(self) -> Dict[str, Any]:
        """
        Testet die Exploit-Module des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste Exploit-Module...")
        
        results = {
            "cve_2025_4664": self._test_cve_2025_4664(),
            "cve_2025_2783": self._test_cve_2025_2783(),
            "cve_2025_2857": self._test_cve_2025_2857(),
            "cve_2025_30397": self._test_cve_2025_30397()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"Exploit-Modultests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_cve_2025_4664(self) -> Dict[str, Any]:
        """
        Testet das CVE-2025-4664-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            # Überprüfen, ob das Modul existiert
            module_path = os.path.join(PathUtils.get_root_dir(), "exploits", "cve_2025_4664", "exploit.py")
            
            if os.path.exists(module_path):
                # Hier könnte eine detailliertere Überprüfung erfolgen
                return {
                    "component": "CVE-2025-4664",
                    "status": "passed",
                    "message": "CVE-2025-4664-Modul existiert"
                }
            else:
                return {
                    "component": "CVE-2025-4664",
                    "status": "failed",
                    "message": "CVE-2025-4664-Modul existiert nicht"
                }
        except Exception as e:
            return {
                "component": "CVE-2025-4664",
                "status": "failed",
                "message": f"CVE-2025-4664-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_cve_2025_2783(self) -> Dict[str, Any]:
        """
        Testet das CVE-2025-2783-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            # Überprüfen, ob das Modul existiert
            module_path = os.path.join(PathUtils.get_root_dir(), "exploits", "cve_2025_2783", "exploit.py")
            
            if os.path.exists(module_path):
                # Hier könnte eine detailliertere Überprüfung erfolgen
                return {
                    "component": "CVE-2025-2783",
                    "status": "passed",
                    "message": "CVE-2025-2783-Modul existiert"
                }
            else:
                return {
                    "component": "CVE-2025-2783",
                    "status": "failed",
                    "message": "CVE-2025-2783-Modul existiert nicht"
                }
        except Exception as e:
            return {
                "component": "CVE-2025-2783",
                "status": "failed",
                "message": f"CVE-2025-2783-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_cve_2025_2857(self) -> Dict[str, Any]:
        """
        Testet das CVE-2025-2857-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            # Überprüfen, ob das Modul existiert
            module_path = os.path.join(PathUtils.get_root_dir(), "exploits", "cve_2025_2857", "exploit.py")
            
            if os.path.exists(module_path):
                # Hier könnte eine detailliertere Überprüfung erfolgen
                return {
                    "component": "CVE-2025-2857",
                    "status": "passed",
                    "message": "CVE-2025-2857-Modul existiert"
                }
            else:
                return {
                    "component": "CVE-2025-2857",
                    "status": "failed",
                    "message": "CVE-2025-2857-Modul existiert nicht"
                }
        except Exception as e:
            return {
                "component": "CVE-2025-2857",
                "status": "failed",
                "message": f"CVE-2025-2857-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_cve_2025_30397(self) -> Dict[str, Any]:
        """
        Testet das CVE-2025-30397-Modul
        
        Returns:
            dict: Testergebnis
        """
        try:
            # Überprüfen, ob das Modul existiert
            module_path = os.path.join(PathUtils.get_root_dir(), "exploits", "cve_2025_30397", "exploit.py")
            
            if os.path.exists(module_path):
                # Hier könnte eine detailliertere Überprüfung erfolgen
                return {
                    "component": "CVE-2025-30397",
                    "status": "passed",
                    "message": "CVE-2025-30397-Modul existiert"
                }
            else:
                return {
                    "component": "CVE-2025-30397",
                    "status": "failed",
                    "message": "CVE-2025-30397-Modul existiert nicht"
                }
        except Exception as e:
            return {
                "component": "CVE-2025-30397",
                "status": "failed",
                "message": f"CVE-2025-30397-Test fehlgeschlagen: {str(e)}"
            }
    
    def test_tool_integrations(self) -> Dict[str, Any]:
        """
        Testet die Tool-Integrationen des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste Tool-Integrationen...")
        
        results = {
            "sliver": self._test_sliver_integration(),
            "metasploit": self._test_metasploit_integration(),
            "ngrok": self._test_ngrok_integration(),
            "ollvm": self._test_ollvm_integration(),
            "backdoor_factory": self._test_backdoor_factory_integration()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"Tool-Integrationstests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_sliver_integration(self) -> Dict[str, Any]:
        """
        Testet die Sliver-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.sliver_integration import SliverIntegration
            
            # Sliver-Integration initialisieren
            sliver = SliverIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(sliver, "is_available") and 
                hasattr(sliver, "generate_implant") and 
                hasattr(sliver, "start_listener")):
                return {
                    "component": "SliverIntegration",
                    "status": "passed",
                    "message": "Sliver-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "SliverIntegration",
                    "status": "failed",
                    "message": "Sliver-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "SliverIntegration",
                "status": "failed",
                "message": f"Sliver-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_metasploit_integration(self) -> Dict[str, Any]:
        """
        Testet die Metasploit-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.metasploit_integration import MetasploitIntegration
            
            # Metasploit-Integration initialisieren
            metasploit = MetasploitIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(metasploit, "is_available") and 
                hasattr(metasploit, "generate_payload") and 
                hasattr(metasploit, "start_handler")):
                return {
                    "component": "MetasploitIntegration",
                    "status": "passed",
                    "message": "Metasploit-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "MetasploitIntegration",
                    "status": "failed",
                    "message": "Metasploit-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "MetasploitIntegration",
                "status": "failed",
                "message": f"Metasploit-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_ngrok_integration(self) -> Dict[str, Any]:
        """
        Testet die Ngrok-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.ngrok_integration import NgrokIntegration
            
            # Ngrok-Integration initialisieren
            ngrok = NgrokIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(ngrok, "is_available") and 
                hasattr(ngrok, "create_tunnel") and 
                hasattr(ngrok, "close_tunnel")):
                return {
                    "component": "NgrokIntegration",
                    "status": "passed",
                    "message": "Ngrok-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "NgrokIntegration",
                    "status": "failed",
                    "message": "Ngrok-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "NgrokIntegration",
                "status": "failed",
                "message": f"Ngrok-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_ollvm_integration(self) -> Dict[str, Any]:
        """
        Testet die OLLVM-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.ollvm_integration import OLLVMIntegration
            
            # OLLVM-Integration initialisieren
            ollvm = OLLVMIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(ollvm, "is_available") and 
                hasattr(ollvm, "obfuscate_c_code") and 
                hasattr(ollvm, "obfuscate_binary")):
                return {
                    "component": "OLLVMIntegration",
                    "status": "passed",
                    "message": "OLLVM-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "OLLVMIntegration",
                    "status": "failed",
                    "message": "OLLVM-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "OLLVMIntegration",
                "status": "failed",
                "message": f"OLLVM-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_backdoor_factory_integration(self) -> Dict[str, Any]:
        """
        Testet die Backdoor-Factory-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.backdoor_factory import BackdoorFactoryIntegration
            
            # Backdoor-Factory-Integration initialisieren
            bdf = BackdoorFactoryIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(bdf, "is_available") and 
                hasattr(bdf, "inject_backdoor") and 
                hasattr(bdf, "analyze_binary")):
                return {
                    "component": "BackdoorFactoryIntegration",
                    "status": "passed",
                    "message": "Backdoor-Factory-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "BackdoorFactoryIntegration",
                    "status": "failed",
                    "message": "Backdoor-Factory-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "BackdoorFactoryIntegration",
                "status": "failed",
                "message": f"Backdoor-Factory-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def test_post_exploitation(self) -> Dict[str, Any]:
        """
        Testet die Post-Exploitation-Module des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste Post-Exploitation-Module...")
        
        results = {
            "winpeas": self._test_winpeas_integration(),
            "defendnot": self._test_defendnot_integration()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"Post-Exploitation-Modultests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_winpeas_integration(self) -> Dict[str, Any]:
        """
        Testet die WinPEAS-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.winpeas_integration import WinPEASIntegration
            
            # WinPEAS-Integration initialisieren
            winpeas = WinPEASIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(winpeas, "download_winpeas") and 
                hasattr(winpeas, "generate_powershell_oneliner") and 
                hasattr(winpeas, "generate_base64_payload")):
                return {
                    "component": "WinPEASIntegration",
                    "status": "passed",
                    "message": "WinPEAS-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "WinPEASIntegration",
                    "status": "failed",
                    "message": "WinPEAS-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "WinPEASIntegration",
                "status": "failed",
                "message": f"WinPEAS-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_defendnot_integration(self) -> Dict[str, Any]:
        """
        Testet die DefendNot-Integration
        
        Returns:
            dict: Testergebnis
        """
        try:
            from tools.defendnot_integration import DefendNotIntegration
            
            # DefendNot-Integration initialisieren
            defendnot = DefendNotIntegration()
            
            # Überprüfen, ob die Hauptmethoden vorhanden sind
            if (hasattr(defendnot, "download_defendnot") and 
                hasattr(defendnot, "generate_bypass_script") and 
                hasattr(defendnot, "generate_oneliner")):
                return {
                    "component": "DefendNotIntegration",
                    "status": "passed",
                    "message": "DefendNot-Integration-Test erfolgreich"
                }
            else:
                return {
                    "component": "DefendNotIntegration",
                    "status": "failed",
                    "message": "DefendNot-Integration fehlt wichtige Methoden"
                }
        except Exception as e:
            return {
                "component": "DefendNotIntegration",
                "status": "failed",
                "message": f"DefendNot-Integration-Test fehlgeschlagen: {str(e)}"
            }
    
    def test_documentation(self) -> Dict[str, Any]:
        """
        Testet die Dokumentation des Frameworks
        
        Returns:
            dict: Testergebnisse
        """
        self.log("info", "Teste Dokumentation...")
        
        results = {
            "readme": self._test_readme(),
            "user_manual": self._test_user_manual(),
            "developer_manual": self._test_developer_manual(),
            "cve_descriptions": self._test_cve_descriptions()
        }
        
        passed = sum(1 for result in results.values() if result["status"] == "passed")
        total = len(results)
        
        self.log("info", f"Dokumentationstests abgeschlossen: {passed}/{total} bestanden")
        
        self.total_tests += total
        self.passed_tests += passed
        self.failed_tests += (total - passed)
        
        return results
    
    def _test_readme(self) -> Dict[str, Any]:
        """
        Testet die README-Datei
        
        Returns:
            dict: Testergebnis
        """
        try:
            readme_path = os.path.join(PathUtils.get_root_dir(), "README.md")
            
            if os.path.exists(readme_path) and os.path.getsize(readme_path) > 0:
                return {
                    "component": "README",
                    "status": "passed",
                    "message": "README-Test erfolgreich"
                }
            else:
                return {
                    "component": "README",
                    "status": "failed",
                    "message": "README existiert nicht oder ist leer"
                }
        except Exception as e:
            return {
                "component": "README",
                "status": "failed",
                "message": f"README-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_user_manual(self) -> Dict[str, Any]:
        """
        Testet das Benutzerhandbuch
        
        Returns:
            dict: Testergebnis
        """
        try:
            user_manual_path = os.path.join(PathUtils.get_root_dir(), "docs", "user_manual.md")
            
            if os.path.exists(user_manual_path) and os.path.getsize(user_manual_path) > 0:
                return {
                    "component": "UserManual",
                    "status": "passed",
                    "message": "Benutzerhandbuch-Test erfolgreich"
                }
            else:
                return {
                    "component": "UserManual",
                    "status": "failed",
                    "message": "Benutzerhandbuch existiert nicht oder ist leer"
                }
        except Exception as e:
            return {
                "component": "UserManual",
                "status": "failed",
                "message": f"Benutzerhandbuch-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_developer_manual(self) -> Dict[str, Any]:
        """
        Testet das Entwicklerhandbuch
        
        Returns:
            dict: Testergebnis
        """
        try:
            dev_manual_path = os.path.join(PathUtils.get_root_dir(), "docs", "developer_manual.md")
            
            if os.path.exists(dev_manual_path) and os.path.getsize(dev_manual_path) > 0:
                return {
                    "component": "DeveloperManual",
                    "status": "passed",
                    "message": "Entwicklerhandbuch-Test erfolgreich"
                }
            else:
                return {
                    "component": "DeveloperManual",
                    "status": "failed",
                    "message": "Entwicklerhandbuch existiert nicht oder ist leer"
                }
        except Exception as e:
            return {
                "component": "DeveloperManual",
                "status": "failed",
                "message": f"Entwicklerhandbuch-Test fehlgeschlagen: {str(e)}"
            }
    
    def _test_cve_descriptions(self) -> Dict[str, Any]:
        """
        Testet die CVE-Beschreibungen
        
        Returns:
            dict: Testergebnis
        """
        try:
            cve_desc_path = os.path.join(PathUtils.get_root_dir(), "docs", "cve_descriptions.md")
            
            if os.path.exists(cve_desc_path) and os.path.getsize(cve_desc_path) > 0:
                return {
                    "component": "CVEDescriptions",
                    "status": "passed",
                    "message": "CVE-Beschreibungen-Test erfolgreich"
                }
            else:
                return {
                    "component": "CVEDescriptions",
                    "status": "failed",
                    "message": "CVE-Beschreibungen existieren nicht oder sind leer"
                }
        except Exception as e:
            return {
                "component": "CVEDescriptions",
                "status": "failed",
                "message": f"CVE-Beschreibungen-Test fehlgeschlagen: {str(e)}"
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Führt alle Tests aus
        
        Returns:
            dict: Alle Testergebnisse
        """
        self.log("info", "Starte alle Tests...")
        
        start_time = time.time()
        
        results = {
            "core": self.test_core_components(),
            "ui": self.test_ui_components(),
            "exploits": self.test_exploits(),
            "tools": self.test_tool_integrations(),
            "post_exploitation": self.test_post_exploitation(),
            "documentation": self.test_documentation()
        }
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("info", f"Alle Tests abgeschlossen in {duration:.2f} Sekunden")
        self.log("info", f"Gesamtergebnis: {self.passed_tests}/{self.total_tests} Tests bestanden ({self.failed_tests} fehlgeschlagen, {self.skipped_tests} übersprungen)")
        
        # Zusammenfassung erstellen
        summary = {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "duration": duration,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": results
        }
        
        # Ergebnisse speichern
        self._save_test_results(summary)
        
        return summary
    
    def _save_test_results(self, results: Dict[str, Any]) -> None:
        """
        Speichert die Testergebnisse
        
        Args:
            results (dict): Testergebnisse
        """
        try:
            # JSON-Datei
            json_file = os.path.join(self.results_dir, f"test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(json_file, "w") as f:
                json.dump(results, f, indent=4)
            
            self.log("info", f"Testergebnisse gespeichert: {json_file}")
            
            # Markdown-Datei
            md_file = os.path.join(self.results_dir, f"test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            
            with open(md_file, "w") as f:
                f.write(f"# ChromSploit Framework - Testergebnisse\n\n")
                f.write(f"Generiert am: {results['timestamp']}\n\n")
                f.write(f"## Zusammenfassung\n\n")
                f.write(f"- **Gesamttests:** {results['total_tests']}\n")
                f.write(f"- **Bestanden:** {results['passed_tests']}\n")
                f.write(f"- **Fehlgeschlagen:** {results['failed_tests']}\n")
                f.write(f"- **Übersprungen:** {results['skipped_tests']}\n")
                f.write(f"- **Dauer:** {results['duration']:.2f} Sekunden\n\n")
                
                # Detaillierte Ergebnisse
                f.write(f"## Detaillierte Ergebnisse\n\n")
                
                for category, category_results in results["results"].items():
                    f.write(f"### {category.capitalize()}\n\n")
                    
                    for component, result in category_results.items():
                        status = result["status"]
                        message = result["message"]
                        component_name = result["component"]
                        
                        status_icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
                        
                        f.write(f"- {status_icon} **{component_name}**: {message}\n")
                    
                    f.write("\n")
            
            self.log("info", f"Testergebnisse als Markdown gespeichert: {md_file}")
        except Exception as e:
            self.log("error", f"Fehler beim Speichern der Testergebnisse: {str(e)}")
    
    def generate_test_report(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert einen Testbericht
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zum generierten Testbericht oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.results_dir, f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        self.log("info", "Generiere Testbericht...")
        
        try:
            # Alle Tests ausführen
            results = self.run_all_tests()
            
            # Testbericht erstellen
            with open(output_file, "w") as f:
                f.write(f"# ChromSploit Framework - Testbericht\n\n")
                f.write(f"Generiert am: {results['timestamp']}\n\n")
                
                f.write(f"## Zusammenfassung\n\n")
                f.write(f"- **Gesamttests:** {results['total_tests']}\n")
                f.write(f"- **Bestanden:** {results['passed_tests']} ({results['passed_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"- **Fehlgeschlagen:** {results['failed_tests']} ({results['failed_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"- **Übersprungen:** {results['skipped_tests']} ({results['skipped_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"- **Dauer:** {results['duration']:.2f} Sekunden\n\n")
                
                # Diagramm (ASCII-Art)
                f.write(f"## Ergebnisdiagramm\n\n")
                f.write(f"```\n")
                passed_bar = "█" * int(results['passed_tests'] / results['total_tests'] * 50)
                failed_bar = "█" * int(results['failed_tests'] / results['total_tests'] * 50)
                skipped_bar = "█" * int(results['skipped_tests'] / results['total_tests'] * 50)
                
                f.write(f"Bestanden: {passed_bar} {results['passed_tests']} ({results['passed_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"Fehlgeschlagen: {failed_bar} {results['failed_tests']} ({results['failed_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"Übersprungen: {skipped_bar} {results['skipped_tests']} ({results['skipped_tests'] / results['total_tests'] * 100:.1f}%)\n")
                f.write(f"```\n\n")
                
                # Detaillierte Ergebnisse
                f.write(f"## Detaillierte Ergebnisse\n\n")
                
                for category, category_results in results["results"].items():
                    category_passed = sum(1 for result in category_results.values() if result["status"] == "passed")
                    category_total = len(category_results)
                    
                    f.write(f"### {category.capitalize()} ({category_passed}/{category_total})\n\n")
                    
                    for component, result in category_results.items():
                        status = result["status"]
                        message = result["message"]
                        component_name = result["component"]
                        
                        status_icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
                        
                        f.write(f"- {status_icon} **{component_name}**: {message}\n")
                    
                    f.write("\n")
                
                # Empfehlungen
                f.write(f"## Empfehlungen\n\n")
                
                if results["failed_tests"] == 0:
                    f.write(f"Alle Tests wurden erfolgreich bestanden. Das Framework ist bereit für die Produktion.\n\n")
                else:
                    f.write(f"Es wurden {results['failed_tests']} fehlgeschlagene Tests festgestellt. Folgende Komponenten sollten überprüft werden:\n\n")
                    
                    for category, category_results in results["results"].items():
                        for component, result in category_results.items():
                            if result["status"] == "failed":
                                f.write(f"- **{result['component']}**: {result['message']}\n")
                    
                    f.write("\n")
            
            self.log("info", f"Testbericht generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Testberichts: {str(e)}")
            return None
