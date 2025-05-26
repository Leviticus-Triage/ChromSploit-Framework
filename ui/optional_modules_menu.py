#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Optionale Module Menü
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils
from core.config import Config
from core.module_loader import ModuleLoader

class OptionalModulesMenu:
    """
    Menü für optionale Module des ChromSploit Frameworks
    """
    
    def __init__(self, config: Config, module_loader: ModuleLoader, logger: Optional[Logger] = None, display_menu: bool = True):
        """
        Initialisiert das optionale Module Menü
        
        Args:
            config (Config): Konfigurationsinstanz
            module_loader (ModuleLoader): Modul-Loader-Instanz
            logger (Logger, optional): Logger-Instanz
            display_menu (bool): Ob das Menü sofort angezeigt werden soll
        """
        self.config = config
        self.module_loader = module_loader
        self.logger = logger
        
        if display_menu:
            self.display()
    
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
    
    def display(self) -> None:
        """
        Zeigt das Menü an
        """
        while True:
            # Modulstatus abrufen
            module_status = self.module_loader.get_module_status()
            
            # Menü anzeigen
            print("\n" + "=" * 60)
            print(f"{Colors.GREEN}ChromSploit Framework - Optionale Module{Colors.RESET}")
            print("=" * 60)
            
            print(f"\n{Colors.BLUE}[*] Verfügbare Module:{Colors.RESET}\n")
            
            # AI-Modul
            ai_status = module_status.get('ai', False)
            ai_config = self.config.get('ai.enable', False)
            ai_color = Colors.GREEN if ai_status and ai_config else Colors.RED
            ai_status_text = f"{Colors.GREEN}Aktiviert{Colors.RESET}" if ai_status and ai_config else f"{Colors.RED}Deaktiviert{Colors.RESET}"
            ai_deps_text = f"{Colors.GREEN}Verfügbar{Colors.RESET}" if ai_status else f"{Colors.RED}Nicht verfügbar{Colors.RESET}"
            
            print(f"{ai_color}1. KI-Modul{Colors.RESET}")
            print(f"   Status: {ai_status_text}")
            print(f"   Abhängigkeiten: {ai_deps_text}")
            print(f"   Beschreibung: Hybride KI-Entscheidungsengine mit Echtzeit-Inferenz und Multi-Modell-Architektur")
            
            # Resilience-Modul
            resilience_status = module_status.get('resilience', False)
            resilience_config = self.config.get('resilience.enable', False)
            resilience_color = Colors.GREEN if resilience_status and resilience_config else Colors.RED
            resilience_status_text = f"{Colors.GREEN}Aktiviert{Colors.RESET}" if resilience_status and resilience_config else f"{Colors.RED}Deaktiviert{Colors.RESET}"
            resilience_deps_text = f"{Colors.GREEN}Verfügbar{Colors.RESET}" if resilience_status else f"{Colors.RED}Nicht verfügbar{Colors.RESET}"
            
            print(f"\n{resilience_color}2. Resilience-Modul{Colors.RESET}")
            print(f"   Status: {resilience_status_text}")
            print(f"   Abhängigkeiten: {resilience_deps_text}")
            print(f"   Beschreibung: Selbstheilende Infrastrukturkomponenten mit Circuit Breaker und Fallback-Mechanismen")
            
            print("\n3. Abhängigkeiten installieren")
            print("4. Konfiguration anzeigen")
            print("5. Zurück zum Hauptmenü")
            
            # Benutzereingabe
            choice = input(f"\n{Colors.BLUE}[?] Wählen Sie eine Option (1-5): {Colors.RESET}")
            
            if choice == "1":
                self._toggle_ai_module()
            elif choice == "2":
                self._toggle_resilience_module()
            elif choice == "3":
                self._install_dependencies()
            elif choice == "4":
                self._show_configuration()
            elif choice == "5":
                break
            else:
                print(f"\n{Colors.RED}[!] Ungültige Option. Bitte wählen Sie 1-5.{Colors.RESET}")
    
    def _toggle_ai_module(self) -> None:
        """
        Aktiviert oder deaktiviert das KI-Modul
        """
        # Modulstatus abrufen
        module_status = self.module_loader.get_module_status()
        ai_status = module_status.get('ai', False)
        ai_config = self.config.get('ai.enable', False)
        
        if not ai_status:
            print(f"\n{Colors.YELLOW}[!] Das KI-Modul ist nicht verfügbar. Abhängigkeiten müssen installiert werden.{Colors.RESET}")
            return
        
        # Modul umschalten
        new_status = not ai_config
        self.config.set('ai.enable', new_status)
        self.config.save()
        
        status_text = "aktiviert" if new_status else "deaktiviert"
        print(f"\n{Colors.GREEN}[+] KI-Modul wurde {status_text}.{Colors.RESET}")
    
    def _toggle_resilience_module(self) -> None:
        """
        Aktiviert oder deaktiviert das Resilience-Modul
        """
        # Modulstatus abrufen
        module_status = self.module_loader.get_module_status()
        resilience_status = module_status.get('resilience', False)
        resilience_config = self.config.get('resilience.enable', False)
        
        if not resilience_status:
            print(f"\n{Colors.YELLOW}[!] Das Resilience-Modul ist nicht verfügbar. Abhängigkeiten müssen installiert werden.{Colors.RESET}")
            return
        
        # Modul umschalten
        new_status = not resilience_config
        self.config.set('resilience.enable', new_status)
        self.config.save()
        
        status_text = "aktiviert" if new_status else "deaktiviert"
        print(f"\n{Colors.GREEN}[+] Resilience-Modul wurde {status_text}.{Colors.RESET}")
    
    def _install_dependencies(self) -> None:
        """
        Installiert die Abhängigkeiten für optionale Module
        """
        print(f"\n{Colors.BLUE}[*] Installiere Abhängigkeiten für optionale Module...{Colors.RESET}")
        
        # Abhängigkeiten für KI-Modul
        print(f"\n{Colors.BLUE}[*] Installiere Abhängigkeiten für KI-Modul...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Dies kann einige Zeit dauern.{Colors.RESET}")
        
        try:
            os.system("pip install torch onnxruntime xgboost transformers")
            print(f"{Colors.GREEN}[+] Abhängigkeiten für KI-Modul erfolgreich installiert.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[-] Fehler beim Installieren der Abhängigkeiten für KI-Modul: {str(e)}{Colors.RESET}")
        
        # Abhängigkeiten für Resilience-Modul
        print(f"\n{Colors.BLUE}[*] Installiere Abhängigkeiten für Resilience-Modul...{Colors.RESET}")
        
        try:
            os.system("pip install pybreaker psutil")
            print(f"{Colors.GREEN}[+] Abhängigkeiten für Resilience-Modul erfolgreich installiert.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[-] Fehler beim Installieren der Abhängigkeiten für Resilience-Modul: {str(e)}{Colors.RESET}")
        
        # Module neu laden
        print(f"\n{Colors.BLUE}[*] Lade Module neu...{Colors.RESET}")
        self.module_loader.load_optional_modules()
        
        print(f"\n{Colors.GREEN}[+] Installation abgeschlossen. Bitte überprüfen Sie den Status der Module.{Colors.RESET}")
    
    def _show_configuration(self) -> None:
        """
        Zeigt die Konfiguration der optionalen Module an
        """
        print("\n" + "=" * 60)
        print(f"{Colors.GREEN}ChromSploit Framework - Konfiguration der optionalen Module{Colors.RESET}")
        print("=" * 60)
        
        # KI-Modul-Konfiguration
        print(f"\n{Colors.BLUE}[*] KI-Modul-Konfiguration:{Colors.RESET}")
        print(f"   Aktiviert: {self.config.get('ai.enable', False)}")
        print(f"   Modell-Pfad: {self.config.get('ai.model_path', '/opt/chromsploit/models')}")
        print(f"   Fallback-Strategie: {self.config.get('ai.fallback_strategy', 'legacy_cve_matcher')}")
        
        # Resilience-Modul-Konfiguration
        print(f"\n{Colors.BLUE}[*] Resilience-Modul-Konfiguration:{Colors.RESET}")
        print(f"   Aktiviert: {self.config.get('resilience.enable', False)}")
        print(f"   CPU-Schwellenwert: {self.config.get('resilience.cpu_threshold', 90.0)}%")
        print(f"   Speicher-Schwellenwert: {self.config.get('resilience.memory_threshold', 90.0)}%")
        print(f"   Festplatten-Schwellenwert: {self.config.get('resilience.disk_threshold', 90.0)}%")
        print(f"   Service-Check-Intervall: {self.config.get('resilience.service_check_interval', 30)} Sekunden")
        
        # Sliver-Konfiguration
        print(f"\n{Colors.BLUE}[*] Sliver-Konfiguration:{Colors.RESET}")
        print(f"   Primärer Endpunkt: {self.config.get('sliver.primary_endpoint', '127.0.0.1:31337')}")
        print(f"   Fallback-Endpunkte: {self.config.get('sliver.fallback_endpoints', '127.0.0.1:8888,127.0.0.1:9999')}")
        
        # Metasploit-Konfiguration
        print(f"\n{Colors.BLUE}[*] Metasploit-Konfiguration:{Colors.RESET}")
        print(f"   Primärer Endpunkt: {self.config.get('metasploit.primary_endpoint', '127.0.0.1:4444')}")
        print(f"   Fallback-Endpunkte: {self.config.get('metasploit.fallback_endpoints', '127.0.0.1:5555,127.0.0.1:6666')}")
        
        # Ngrok-Konfiguration
        print(f"\n{Colors.BLUE}[*] Ngrok-Konfiguration:{Colors.RESET}")
        print(f"   Auth-Token: {self.config.get('ngrok.authtoken', 'YOUR_KALI_NGROK_TOKEN')}")
        print(f"   Region: {self.config.get('ngrok.region', 'eu')}")
        print(f"   Tunnel-Rotation: {self.config.get('ngrok.tunnel_rotation', 900)} Sekunden")
        
        # OLLVM-Konfiguration
        print(f"\n{Colors.BLUE}[*] OLLVM-Konfiguration:{Colors.RESET}")
        print(f"   Docker-Image: {self.config.get('ollvm.docker_image', 'kali/ollvm:2025.1')}")
        print(f"   Compiler-Pfad: {self.config.get('ollvm.compiler_path', '/opt/ollvm/bin/clang++')}")
        
        input(f"\n{Colors.BLUE}[?] Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
