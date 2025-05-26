#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Ngrok Tunneling Integration
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import requests
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class NgrokIntegration:
    """
    Integration von Ngrok Tunneling in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die Ngrok-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.ngrok_path = "/usr/local/bin/ngrok"
        self.active_tunnels = {}
        self.authtoken = None
        self.api_url = "http://127.0.0.1:4040/api"
    
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
        Überprüft, ob Ngrok verfügbar ist
        
        Returns:
            bool: True, wenn Ngrok verfügbar ist, sonst False
        """
        return os.path.exists(self.ngrok_path) or Utils.is_tool_available("ngrok")
    
    def get_version(self) -> str:
        """
        Gibt die Ngrok-Version zurück
        
        Returns:
            str: Die Ngrok-Version oder "Unbekannt" bei Fehler
        """
        try:
            if os.path.exists(self.ngrok_path):
                result = subprocess.run([self.ngrok_path, "version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            elif Utils.is_tool_available("ngrok"):
                result = subprocess.run(["ngrok", "version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            return "Nicht verfügbar"
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Ngrok-Version: {str(e)}")
            return "Unbekannt"
    
    def install(self) -> bool:
        """
        Installiert Ngrok, falls es nicht verfügbar ist
        
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available():
            self.log("info", "Ngrok ist bereits installiert")
            return True
        
        self.log("info", "Installiere Ngrok...")
        
        try:
            # Ngrok herunterladen
            self.log("info", "Lade Ngrok herunter...")
            download_cmd = "curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.tgz -o ngrok.tgz"
            result = subprocess.run(download_cmd, shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Ngrok entpacken
            self.log("info", "Entpacke Ngrok...")
            extract_cmd = "tar xzf ngrok.tgz"
            subprocess.run(extract_cmd, shell=True, check=True)
            
            # Ngrok installieren
            self.log("info", "Installiere Ngrok...")
            install_cmd = "sudo mv ngrok /usr/local/bin/"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Aufräumen
            cleanup_cmd = "rm ngrok.tgz"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            # Überprüfen, ob die Installation erfolgreich war
            if self.is_available():
                self.log("info", "Ngrok wurde erfolgreich installiert")
                return True
            else:
                self.log("error", "Ngrok-Installation fehlgeschlagen")
                return False
        except Exception as e:
            self.log("error", f"Fehler bei der Ngrok-Installation: {str(e)}")
            return False
    
    def set_authtoken(self, token: str) -> bool:
        """
        Setzt den Ngrok-Authtoken
        
        Args:
            token (str): Der Authtoken
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not self.is_available():
            self.log("error", "Ngrok ist nicht verfügbar")
            return False
        
        self.log("info", "Setze Ngrok-Authtoken...")
        
        try:
            cmd = [self.ngrok_path if os.path.exists(self.ngrok_path) else "ngrok", 
                 "authtoken", token]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log("info", "Ngrok-Authtoken erfolgreich gesetzt")
                self.authtoken = token
                return True
            else:
                self.log("error", f"Fehler beim Setzen des Ngrok-Authtokens: {result.stderr}")
                return False
        except Exception as e:
            self.log("error", f"Fehler beim Setzen des Ngrok-Authtokens: {str(e)}")
            return False
    
    def create_tunnel(self, 
                     local_port: int, 
                     protocol: str = "http", 
                     region: str = "us",
                     subdomain: Optional[str] = None,
                     hostname: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Erstellt einen Ngrok-Tunnel
        
        Args:
            local_port (int): Lokaler Port
            protocol (str, optional): Protokoll (http, tcp, tls)
            region (str, optional): Region (us, eu, ap, au, sa, jp, in)
            subdomain (str, optional): Subdomain (nur mit Authtoken)
            hostname (str, optional): Hostname (nur mit Authtoken)
            
        Returns:
            dict: Tunnel-Informationen oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "Ngrok ist nicht verfügbar")
            return None
        
        # Überprüfen, ob bereits ein Tunnel für diesen Port existiert
        if local_port in self.active_tunnels:
            self.log("warning", f"Es existiert bereits ein Tunnel für Port {local_port}")
            return self.active_tunnels[local_port]["info"]
        
        self.log("info", f"Erstelle Ngrok-Tunnel für Port {local_port} ({protocol})...")
        
        # Befehl zum Erstellen des Tunnels erstellen
        cmd = [self.ngrok_path if os.path.exists(self.ngrok_path) else "ngrok", 
               protocol, str(local_port), "--region", region]
        
        # Subdomain hinzufügen, falls angegeben und Authtoken gesetzt
        if subdomain and self.authtoken:
            cmd.extend(["--subdomain", subdomain])
        
        # Hostname hinzufügen, falls angegeben und Authtoken gesetzt
        if hostname and self.authtoken:
            cmd.extend(["--hostname", hostname])
        
        try:
            # Tunnel erstellen
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Warten, bis der Tunnel erstellt wurde
            time.sleep(3)
            
            # Tunnel-Informationen abrufen
            tunnel_info = self._get_tunnel_info()
            
            if tunnel_info:
                self.log("info", f"Ngrok-Tunnel erfolgreich erstellt: {tunnel_info['public_url']}")
                
                # Tunnel zur Liste hinzufügen
                self.active_tunnels[local_port] = {
                    "process": process,
                    "info": tunnel_info,
                    "protocol": protocol,
                    "region": region,
                    "subdomain": subdomain,
                    "hostname": hostname
                }
                
                return tunnel_info
            else:
                self.log("error", "Fehler beim Erstellen des Ngrok-Tunnels: Keine Tunnel-Informationen verfügbar")
                process.terminate()
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Erstellen des Ngrok-Tunnels: {str(e)}")
            return None
    
    def _get_tunnel_info(self) -> Optional[Dict[str, Any]]:
        """
        Ruft Informationen über den aktiven Tunnel ab
        
        Returns:
            dict: Tunnel-Informationen oder None bei Fehler
        """
        try:
            response = requests.get(f"{self.api_url}/tunnels", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("tunnels"):
                    tunnel = data["tunnels"][0]
                    
                    return {
                        "public_url": tunnel["public_url"],
                        "proto": tunnel["proto"],
                        "addr": tunnel["config"]["addr"],
                        "name": tunnel["name"]
                    }
            
            return None
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Tunnel-Informationen: {str(e)}")
            return None
    
    def get_all_tunnels(self) -> List[Dict[str, Any]]:
        """
        Gibt Informationen über alle aktiven Tunnel zurück
        
        Returns:
            list: Liste der aktiven Tunnel
        """
        try:
            response = requests.get(f"{self.api_url}/tunnels", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("tunnels"):
                    tunnels = []
                    
                    for tunnel in data["tunnels"]:
                        tunnels.append({
                            "public_url": tunnel["public_url"],
                            "proto": tunnel["proto"],
                            "addr": tunnel["config"]["addr"],
                            "name": tunnel["name"]
                        })
                    
                    return tunnels
            
            return []
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der Tunnel-Informationen: {str(e)}")
            return []
    
    def close_tunnel(self, local_port: int) -> bool:
        """
        Schließt einen Ngrok-Tunnel
        
        Args:
            local_port (int): Lokaler Port
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if local_port in self.active_tunnels:
            try:
                # Tunnel-Prozess beenden
                self.active_tunnels[local_port]["process"].terminate()
                self.active_tunnels[local_port]["process"].wait(timeout=5)
                
                self.log("info", f"Ngrok-Tunnel für Port {local_port} geschlossen")
                
                # Tunnel aus der Liste entfernen
                del self.active_tunnels[local_port]
                
                return True
            except Exception as e:
                self.log("error", f"Fehler beim Schließen des Ngrok-Tunnels: {str(e)}")
                return False
        else:
            self.log("warning", f"Kein aktiver Tunnel für Port {local_port} gefunden")
            return False
    
    def close_all_tunnels(self) -> bool:
        """
        Schließt alle aktiven Ngrok-Tunnel
        
        Returns:
            bool: True bei Erfolg, sonst False
        """
        success = True
        
        for port in list(self.active_tunnels.keys()):
            if not self.close_tunnel(port):
                success = False
        
        return success
    
    def get_active_tunnels(self) -> Dict[int, Dict[str, Any]]:
        """
        Gibt alle aktiven Ngrok-Tunnel zurück
        
        Returns:
            dict: Dictionary der aktiven Tunnel
        """
        return self.active_tunnels
    
    def get_tunnel_url(self, local_port: int) -> Optional[str]:
        """
        Gibt die öffentliche URL für einen Tunnel zurück
        
        Args:
            local_port (int): Lokaler Port
            
        Returns:
            str: Öffentliche URL oder None, wenn kein Tunnel existiert
        """
        if local_port in self.active_tunnels:
            return self.active_tunnels[local_port]["info"]["public_url"]
        else:
            self.log("warning", f"Kein aktiver Tunnel für Port {local_port} gefunden")
            return None
    
    def get_tunnel_status(self, local_port: int) -> Optional[Dict[str, Any]]:
        """
        Gibt den Status eines Tunnels zurück
        
        Args:
            local_port (int): Lokaler Port
            
        Returns:
            dict: Tunnel-Status oder None, wenn kein Tunnel existiert
        """
        if local_port in self.active_tunnels:
            try:
                # Überprüfen, ob der Prozess noch läuft
                if self.active_tunnels[local_port]["process"].poll() is None:
                    # Tunnel-Informationen aktualisieren
                    tunnel_info = self._get_tunnel_info()
                    
                    if tunnel_info:
                        self.active_tunnels[local_port]["info"] = tunnel_info
                    
                    return {
                        "status": "online",
                        "info": self.active_tunnels[local_port]["info"]
                    }
                else:
                    return {
                        "status": "offline",
                        "info": self.active_tunnels[local_port]["info"]
                    }
            except Exception as e:
                self.log("error", f"Fehler beim Abrufen des Tunnel-Status: {str(e)}")
                return None
        else:
            self.log("warning", f"Kein aktiver Tunnel für Port {local_port} gefunden")
            return None
    
    def restart_tunnel(self, local_port: int) -> Optional[Dict[str, Any]]:
        """
        Startet einen Ngrok-Tunnel neu
        
        Args:
            local_port (int): Lokaler Port
            
        Returns:
            dict: Neue Tunnel-Informationen oder None bei Fehler
        """
        if local_port in self.active_tunnels:
            # Tunnel-Konfiguration speichern
            protocol = self.active_tunnels[local_port]["protocol"]
            region = self.active_tunnels[local_port]["region"]
            subdomain = self.active_tunnels[local_port]["subdomain"]
            hostname = self.active_tunnels[local_port]["hostname"]
            
            # Tunnel schließen
            if self.close_tunnel(local_port):
                # Tunnel neu erstellen
                return self.create_tunnel(local_port, protocol, region, subdomain, hostname)
            else:
                self.log("error", f"Fehler beim Neustarten des Ngrok-Tunnels: Tunnel konnte nicht geschlossen werden")
                return None
        else:
            self.log("warning", f"Kein aktiver Tunnel für Port {local_port} gefunden")
            return None
