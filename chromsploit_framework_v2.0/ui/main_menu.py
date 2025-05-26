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
from ui.ngrok_menu import NgrokMenu
from ui.post_exploitation_menu import PostExploitationMenu

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
        self.add_item("CVE-2025-4664 (Chrome Data Leak)", self._open_cve_2025_4664, Colors.BRIGHT_GREEN)
        self.add_item("CVE-2025-2783 (Chrome Mojo Sandbox Escape)", self._open_cve_2025_2783, Colors.BRIGHT_GREEN)
        self.add_item("CVE-2025-2857 (Firefox Sandbox Escape)", self._open_cve_2025_2857, Colors.BRIGHT_GREEN)
        self.add_item("CVE-2025-30397 (Edge WebAssembly JIT Escape)", self._open_cve_2025_30397, Colors.BRIGHT_GREEN)
        self.add_item("Custom Exploit Engine", self._open_custom_menu, Colors.BRIGHT_YELLOW)
        self.add_item("Live View & Debug Console", self._open_live_view, Colors.BRIGHT_BLUE)
        self.add_item("Ngrok Tunneling", self._open_ngrok_menu, Colors.BRIGHT_MAGENTA)
        self.add_item("Post-Exploitation", self._open_post_exploitation, Colors.BRIGHT_CYAN)
        self.add_item("Einstellungen", self._open_settings, Colors.BRIGHT_WHITE)
        self.add_item("Beenden", self._exit_program, Colors.BRIGHT_RED)
    
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
        Öffnet das Ngrok-Menü
        """
        menu = NgrokMenu(self)
        menu.display()
    
    def _open_post_exploitation(self) -> None:
        """
        Öffnet das Post-Exploitation-Menü
        """
        menu = PostExploitationMenu(self)
        menu.display()
    
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
