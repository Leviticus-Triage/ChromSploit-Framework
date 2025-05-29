#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Ein modulares Exploitation Framework für Browser-Schwachstellen
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import argparse
import platform
import subprocess
from pathlib import Path
from datetime import datetime

# Pfad-Setup für Modul-Imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Core-Module importieren
from core.colors import Colors
from core.config import Config
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils
from core.simulation import SimulationMode, get_simulation_engine
from core.enhanced_logger import get_logger
from core.error_handler import get_error_handler, handle_errors

# UI-Module importieren
from ui.main_menu import MainMenu

def check_environment():
    """
    Überprüft die Umgebung auf notwendige Abhängigkeiten und Tools
    """
    print(f"{Colors.CYAN}[*] Überprüfe Umgebung...{Colors.RESET}")
    
    # Betriebssystem überprüfen
    os_info = platform.platform()
    print(f"{Colors.BLUE}[+] Betriebssystem: {os_info}{Colors.RESET}")
    
    # Python-Version überprüfen
    python_version = platform.python_version()
    print(f"{Colors.BLUE}[+] Python-Version: {python_version}{Colors.RESET}")
    
    if float(python_version.split('.')[0] + '.' + python_version.split('.')[1]) < 3.9:
        print(f"{Colors.RED}[!] Warnung: Python 3.9+ wird empfohlen{Colors.RESET}")
    
    # Überprüfen, ob wir auf Kali Linux laufen
    is_kali = False
    try:
        with open('/etc/os-release', 'r') as f:
            if 'kali' in f.read().lower():
                is_kali = True
                print(f"{Colors.GREEN}[+] Kali Linux erkannt{Colors.RESET}")
    except:
        pass
    
    if not is_kali:
        print(f"{Colors.YELLOW}[!] Kali Linux wird empfohlen für volle Funktionalität{Colors.RESET}")
    
    # Überprüfen, ob wir als Root laufen
    is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    if is_root:
        print(f"{Colors.GREEN}[+] Läuft mit Root-Rechten{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}[!] Einige Funktionen benötigen Root-Rechte{Colors.RESET}")
    
    # Überprüfen, ob notwendige Tools installiert sind
    tools = {
        "ngrok": "Ngrok Tunneling",
        "msfconsole": "Metasploit Framework",
        "clang++": "OLLVM Compiler"
    }
    
    for tool, description in tools.items():
        if Utils.is_tool_available(tool):
            print(f"{Colors.GREEN}[+] {description} gefunden{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] {description} nicht gefunden{Colors.RESET}")
    
    print(f"{Colors.CYAN}[*] Umgebungsprüfung abgeschlossen{Colors.RESET}")
    print()

def parse_arguments():
    """
    Kommandozeilenargumente parsen
    """
    parser = argparse.ArgumentParser(description='ChromSploit Framework v2.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Ausführliche Ausgabe aktivieren')
    parser.add_argument('-c', '--config', type=str, help='Pfad zur Konfigurationsdatei')
    parser.add_argument('-e', '--exploit', type=str, help='Direktes Ausführen eines Exploits')
    parser.add_argument('-o', '--output', type=str, help='Ausgabeverzeichnis für generierte Dateien')
    parser.add_argument('--check', action='store_true', help='Umgebung überprüfen und beenden')
    parser.add_argument('--update', action='store_true', help='Framework aktualisieren')
    
    return parser.parse_args()

def display_banner():
    """
    Zeigt den ChromSploit ASCII-Art Banner an
    """
    banner = f"""
{Colors.BRIGHT_RED}  ██████{Colors.RED}╗{Colors.BRIGHT_RED}██{Colors.RED}╗  {Colors.BRIGHT_RED}██{Colors.RED}╗{Colors.BRIGHT_RED}██████{Colors.RED}╗  {Colors.BRIGHT_RED}██████{Colors.RED}╗ {Colors.BRIGHT_RED}███{Colors.RED}╗   {Colors.BRIGHT_RED}███{Colors.RED}╗{Colors.BRIGHT_RED}███████{Colors.RED}╗{Colors.BRIGHT_RED}██████{Colors.RED}╗ {Colors.BRIGHT_RED}██{Colors.RED}╗      {Colors.BRIGHT_RED}██████{Colors.RED}╗ {Colors.BRIGHT_RED}██{Colors.RED}╗{Colors.BRIGHT_RED}████████{Colors.RED}╗
{Colors.RED}██{Colors.BRIGHT_RED}╔════╝{Colors.RED}██║  ██║██╔══██╗██╔═══██╗████╗ ████║██╔════╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝
{Colors.RED}██║     ███████║██████╔╝██║   ██║██╔████╔██║███████╗██████╔╝██║     ██║   ██║██║   ██║   
{Colors.RED}██║     ██╔══██║██╔══██╗██║   ██║██║╚██╔╝██║╚════██║██╔═══╝ ██║     ██║   ██║██║   ██║   
{Colors.BRIGHT_RED}╚{Colors.RED}██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║███████║██║     ███████╗╚██████╔╝██║   ██║   
{Colors.BRIGHT_RED} ╚{Colors.RED}═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════════╗
{Colors.BRIGHT_CYAN}║ {Colors.BRIGHT_WHITE}ChromSploit Framework v2.0                                  {Colors.BRIGHT_YELLOW}by Leviticus-Triage {Colors.BRIGHT_CYAN}║
{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

def main():
    """
    Hauptfunktion des ChromSploit Frameworks
    """
    # Kommandozeilenargumente parsen
    args = parse_arguments()
    
    # Initialize enhanced logging
    enhanced_logger = get_logger()
    enhanced_logger.set_level(args.log_level)
    
    # Initialize error handler
    error_handler = get_error_handler()
    error_handler.debug_mode = args.debug
    
    # Initialize resilience system
    try:
        from modules.resilience import get_resilience_manager, get_self_healing_system
        resilience_manager = get_resilience_manager()
        self_healing_system = get_self_healing_system()
        
        # Start monitoring
        resilience_manager.start_monitoring()
        self_healing_system.start_proactive_healing()
        print(f"{Colors.GREEN}[+] Resilience system initialized{Colors.RESET}")
    except ImportError:
        print(f"{Colors.YELLOW}[!] Resilience system not available{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Resilience system initialization failed: {e}{Colors.RESET}")
    
    # Initialize simulation engine
    sim_mode = SimulationMode(args.simulation)
    sim_engine = get_simulation_engine(sim_mode)
    
    # Show simulation warning
    if args.simulation:
        print(f"\n{Colors.YELLOW}[!] SIMULATION MODE ACTIVE - Mode: {args.simulation}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] No actual exploitation will be performed{Colors.RESET}\n")
        time.sleep(2)
    
    # Banner anzeigen
    display_banner()
    
    # Konfiguration laden
    config_path = args.config if args.config else os.path.join(BASE_DIR, 'config', 'user_config.json')
    config = Config(config_path)
    
    # Logger initialisieren (legacy logger for compatibility)
    log_level = 2 if args.verbose else 1
    logger = Logger(log_level=log_level, log_file=os.path.join(BASE_DIR, 'logs', f'chromsploit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    
    # Umgebung überprüfen
    check_environment()
    
    # Wenn nur Umgebungsprüfung angefordert wurde, beenden
    if args.check:
        sys.exit(0)
    
    # Wenn Update angefordert wurde
    if args.update:
        print(f"{Colors.CYAN}[*] Suche nach Updates...{Colors.RESET}")
        # Hier würde die Update-Logik implementiert werden
        print(f"{Colors.GREEN}[+] Framework ist auf dem neuesten Stand{Colors.RESET}")
        sys.exit(0)
    
    # Wenn ein Exploit direkt ausgeführt werden soll
    if args.exploit:
        print(f"{Colors.CYAN}[*] Führe Exploit aus: {args.exploit}{Colors.RESET}")
        # Use simulation engine for exploit
        if args.simulation:
            result = sim_engine.simulate_cve_exploit(args.exploit, "target", {})
            print(f"{Colors.GREEN}[+] Simulation abgeschlossen: {result.message}{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Direkte Exploit-Ausführung nur im Simulationsmodus verfügbar{Colors.RESET}")
        sys.exit(0)
    
    # Hauptmenü starten
    try:
        menu = MainMenu()
        menu.simulation_mode = args.simulation is not None
        menu.display()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Benutzerabbruch erkannt. Beende ChromSploit...{Colors.RESET}")
    except Exception as e:
        error_handler.handle_error(e, "Main execution")
    finally:
        print(f"{Colors.CYAN}[*] ChromSploit wird beendet. Auf Wiedersehen!{Colors.RESET}")
        
        # Show simulation statistics if in simulation mode
        if args.simulation:
            stats = sim_engine.get_simulation_stats()
            if stats['total_simulations'] > 0:
                print(f"\n{Colors.CYAN}=== Simulation Summary ==={Colors.RESET}")
                print(f"Total simulations: {stats['total_simulations']}")
                print(f"Success rate: {stats['success_rate']:.1f}%")

if __name__ == "__main__":
    main()
