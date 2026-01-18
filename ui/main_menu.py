#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Hauptmenü-Implementierung
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
from typing import Optional, Dict, Any, List

from core.colors import Colors
from core.menu import Menu
from core.config import Config
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

# UI-Module importieren
from ui.cve_menu import CVEMenu
from ui.custom_menu import CustomMenu
from ui.live_view import LiveViewMenu
from ui.settings_menu import SettingsMenu
from ui.enhanced_ngrok_menu import EnhancedNgrokMenu
from ui.post_exploitation_menu import PostExploitationMenu
from ui.reporting_menu import ReportingMenu
from ui.reconnaissance_menu import ReconnaissanceMenu
from ui.vulnerability_menu import VulnerabilityMenu
from ui.evidence_menu import EvidenceMenu

# Try to import Sliver C2 menu
try:
 from ui.sliver_c2_menu import SliverC2Menu
 SLIVER_MENU_AVAILABLE = True
except ImportError:
 SLIVER_MENU_AVAILABLE = False

# Try to import Collaboration menu
try:
 from ui.collaboration_menu import CollaborationMenu
 COLLAB_MENU_AVAILABLE = True
except ImportError:
 COLLAB_MENU_AVAILABLE = False

# Try to import Browser Chain menu
try:
 from ui.browser_chain_menu import BrowserChainMenu
 BROWSER_CHAIN_AVAILABLE = True
except ImportError:
 BROWSER_CHAIN_AVAILABLE = False

# Try to import Session Management menu
try:
 from ui.session_menu import SessionMenu
 SESSION_MENU_AVAILABLE = True
except ImportError:
 SESSION_MENU_AVAILABLE = False

# Try to import AI Assistant menu
try:
 from ui.ai_assistant_menu import AIAssistantMenu
 AI_MENU_AVAILABLE = True
except ImportError:
 AI_MENU_AVAILABLE = False

class MainMenu(Menu):
 """
 Hauptmenü des ChromSploit Frameworks
 """
 
 def __init__(self):
 """
 Initialisiert das Hauptmenü
 """
 super().__init__("ChromSploit Framework v2.0")
 
 # Informationstext setzen
 self.set_info_text("Willkommen im ChromSploit Framework - Ein modulares Exploitation Framework für Browser-Schwachstellen")
 
 # Menüeinträge hinzufügen
 self.add_item(" Reconnaissance & Target Discovery", self._open_reconnaissance, Colors.BRIGHT_BLUE)
 self.add_item(" Vulnerability Scanner", self._open_vulnerability_scanner, Colors.BRIGHT_YELLOW)
 self.add_item(" Exploitation Chains", self._open_exploitation_chains, Colors.BRIGHT_RED)
 self.add_item(" Evidence Collection", self._open_evidence_collection, Colors.BRIGHT_MAGENTA)
 self.add_item(" Analytics Dashboard", self._open_analytics_dashboard, Colors.BRIGHT_CYAN)
 self.add_item("CVE-2025-4664 (Chrome Data Leak)", self._open_cve_2025_4664, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2025-2783 (Chrome Mojo Sandbox Escape)", self._open_cve_2025_2783, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2025-2857 (Firefox Sandbox Escape)", self._open_cve_2025_2857, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2025-30397 (Edge WebAssembly JIT Escape)", self._open_cve_2025_30397, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2025-49741 (Edge Information Disclosure)", self._open_cve_2025_49741, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2020-6519 (Chromium CSP Bypass)", self._open_cve_2020_6519, Colors.BRIGHT_GREEN)
 self.add_item("CVE-2017-5375 (Firefox ASM.JS JIT-Spray)", self._open_cve_2017_5375, Colors.BRIGHT_GREEN)
 if BROWSER_CHAIN_AVAILABLE:
 self.add_item(" Browser Multi-Exploit Chain", self._open_browser_chain, Colors.BRIGHT_RED)
 if AI_MENU_AVAILABLE:
 self.add_item(" AI Exploit Assistant", self._open_ai_assistant, Colors.BRIGHT_CYAN)
 self.add_item("Custom Exploit Engine", self._open_custom_menu, Colors.BRIGHT_YELLOW)
 self.add_item("Live View & Debug Console", self._open_live_view, Colors.BRIGHT_BLUE)
 self.add_item("Professional Reporting", self._open_reporting_menu, Colors.BRIGHT_CYAN)
 self.add_item("Resilience & Self-Healing", self._open_resilience_menu, Colors.BRIGHT_GREEN)
 self.add_item("Enhanced Obfuscation", self._open_obfuscation_menu, Colors.BRIGHT_YELLOW)
 self.add_item("Live Monitoring", self._open_monitoring_menu, Colors.BRIGHT_CYAN)
 self.add_item("Ngrok Tunneling", self._open_ngrok_menu, Colors.BRIGHT_MAGENTA)
 self.add_item("Post-Exploitation", self._open_post_exploitation, Colors.BRIGHT_CYAN)
 if SESSION_MENU_AVAILABLE:
 self.add_item(" Session Management", self._open_session_management, Colors.BRIGHT_YELLOW)
 if SLIVER_MENU_AVAILABLE:
 self.add_item(" Sliver C2 Command & Control", self._open_sliver_c2, Colors.BRIGHT_RED)
 if COLLAB_MENU_AVAILABLE:
 self.add_item(" Team Collaboration", self._open_collaboration, Colors.BRIGHT_MAGENTA)
 self.add_item(" Compliance & Legal", self._open_compliance, Colors.BRIGHT_YELLOW)
 self.add_item("Einstellungen", self._open_settings, Colors.BRIGHT_WHITE)
 self.add_item("Beenden", self._exit_program, Colors.BRIGHT_RED)
 
 def _open_reconnaissance(self) -> None:
 """
 Öffnet das Reconnaissance-Menü
 """
 menu = ReconnaissanceMenu()
 menu.run()
 
 def _open_vulnerability_scanner(self) -> None:
 """
 Öffnet das Vulnerability Scanner-Menü
 """
 menu = VulnerabilityMenu()
 menu.run()
 
 def _open_exploitation_chains(self) -> None:
 """
 Öffnet das Exploitation Chains-Menü
 """
 if BROWSER_CHAIN_AVAILABLE:
 menu = BrowserChainMenu()
 menu.display()
 else:
 # Fallback to exploitation chain menu
 try:
 from ui.exploit_chain_menu import ExploitChainMenu
 menu = ExploitChainMenu()
 menu.display()
 except ImportError:
 print(f"{Colors.YELLOW}[!] Exploitation Chains Menü nicht verfügbar{Colors.RESET}")
 print(f"{Colors.RED}[!] Browser Chain Module konnte nicht geladen werden{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_evidence_collection(self) -> None:
 """
 Öffnet das Evidence Collection-Menü
 """
 menu = EvidenceMenu()
 menu.run()
 
 def _open_cve_2025_4664(self) -> None:
 """
 Öffnet das Menü für CVE-2025-4664
 """
 menu = CVEMenu("cve_2025_4664", "Chrome Data Leak", self)
 menu.display()
 
 def _open_cve_2025_2783(self) -> None:
 """
 Öffnet das Menü für CVE-2025-2783
 """
 menu = CVEMenu("cve_2025_2783", "Chrome Mojo Sandbox Escape", self)
 menu.display()
 
 def _open_cve_2025_2857(self) -> None:
 """
 Öffnet das Menü für CVE-2025-2857
 """
 menu = CVEMenu("cve_2025_2857", "Firefox Sandbox Escape", self)
 menu.display()
 
 def _open_cve_2025_30397(self) -> None:
 """
 Öffnet das Menü für CVE-2025-30397
 """
 menu = CVEMenu("cve_2025_30397", "Edge WebAssembly JIT Escape", self)
 menu.display()
 
 def _open_cve_2025_49741(self) -> None:
 """
 Öffnet das Menü für CVE-2025-49741
 """
 menu = CVEMenu("cve_2025_49741", "Edge Information Disclosure", self)
 menu.display()
 
 def _open_cve_2020_6519(self) -> None:
 """
 Öffnet das Menü für CVE-2020-6519
 """
 menu = CVEMenu("cve_2020_6519", "Chromium CSP Bypass", self)
 menu.display()
 
 def _open_cve_2017_5375(self) -> None:
 """
 Öffnet das Menü für CVE-2017-5375
 """
 menu = CVEMenu("cve_2017_5375", "Firefox ASM.JS JIT-Spray", self)
 menu.display()
 
 def _open_custom_menu(self) -> None:
 """
 Öffnet das Menü für benutzerdefinierte Exploits
 """
 menu = CustomMenu(self)
 menu.display()
 
 def _open_live_view(self) -> None:
 """
 Öffnet das Live-View-Menü
 """
 menu = LiveViewMenu(self)
 menu.display()
 
 def _open_ngrok_menu(self) -> None:
 """
 Öffnet das erweiterte Ngrok-Menü
 """
 menu = EnhancedNgrokMenu(self)
 menu.display()
 
 def _open_reporting_menu(self) -> None:
 """
 Öffnet das Professional Reporting Menü
 """
 menu = ReportingMenu(self)
 menu.display()
 
 def _open_post_exploitation(self) -> None:
 """
 Öffnet das Post-Exploitation-Menü
 """
 menu = PostExploitationMenu(self)
 menu.display()
 
 def _open_sliver_c2(self) -> None:
 """
 Öffnet das Sliver C2 Command & Control Menü
 """
 if SLIVER_MENU_AVAILABLE:
 menu = SliverC2Menu()
 menu.run()
 else:
 print(f"{Colors.YELLOW}[!] Sliver C2 Menü ist nicht verfügbar{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_collaboration(self) -> None:
 """
 Öffnet das Team Collaboration Menü
 """
 if COLLAB_MENU_AVAILABLE:
 menu = CollaborationMenu()
 menu.run()
 else:
 print(f"{Colors.YELLOW}[!] Collaboration Menü ist nicht verfügbar{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_resilience_menu(self) -> None:
 """
 Öffnet das Resilience & Self-Healing Menü
 """
 from ui.resilience_menu import ResilienceMenu
 menu = ResilienceMenu()
 menu.display()
 
 def _open_obfuscation_menu(self) -> None:
 """
 Öffnet das Enhanced Obfuscation Menü
 """
 from ui.obfuscation_menu import ObfuscationMenu
 menu = ObfuscationMenu()
 menu.display()
 
 def _open_monitoring_menu(self) -> None:
 """
 Öffnet das Live Monitoring Menü
 """
 from ui.monitoring_menu import MonitoringMenu
 menu = MonitoringMenu()
 menu.display()
 
 def _open_compliance(self) -> None:
 """
 Öffnet das Compliance & Legal Menü
 """
 from ui.compliance_menu import ComplianceMenu
 menu = ComplianceMenu()
 menu.run()
 
 def _open_browser_chain(self) -> None:
 """
 Öffnet das Browser Multi-Exploit Chain Menü
 """
 if BROWSER_CHAIN_AVAILABLE:
 menu = BrowserChainMenu()
 menu.run()
 else:
 print(f"{Colors.YELLOW}[!] Browser Chain Menü nicht verfügbar{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_ai_assistant(self) -> None:
 """
 Öffnet das AI Assistant Menü
 """
 if AI_MENU_AVAILABLE:
 menu = AIAssistantMenu()
 menu.run()
 else:
 print(f"{Colors.YELLOW}[!] AI Assistant Menü nicht verfügbar{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_session_management(self) -> None:
 """
 Öffnet das Session Management Menü
 """
 if SESSION_MENU_AVAILABLE:
 menu = SessionMenu()
 menu.run()
 else:
 print(f"{Colors.YELLOW}[!] Session Management Menü nicht verfügbar{Colors.RESET}")
 input("Drücken Sie Enter um fortzufahren...")
 
 def _open_settings(self) -> None:
 """
 Öffnet das Einstellungsmenü
 """
 menu = SettingsMenu(self)
 menu.display()
 
 def _exit_program(self) -> str:
 """
 Beendet das Programm
 
 Returns:
 str: "exit" als Signal zum Beenden
 """
 print(f"\n{Colors.CYAN}ChromSploit wird beendet. Auf Wiedersehen!{Colors.RESET}")
 sys.exit(0)