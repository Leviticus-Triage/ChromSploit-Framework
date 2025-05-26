#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Konfigurationsmanagement für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from core.colors import Colors

class Config:
    """
    Konfigurationsmanager für das ChromSploit Framework
    Verwaltet Benutzer- und Standardkonfigurationen
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisiert den Konfigurationsmanager
        
        Args:
            config_path (str, optional): Pfad zur Konfigurationsdatei
        """
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'config')
        
        # Standardkonfigurationspfad
        self.default_config_path = os.path.join(self.config_dir, 'default_config.json')
        
        # Benutzerkonfigurationspfad
        self.user_config_path = config_path if config_path else os.path.join(self.config_dir, 'user_config.json')
        
        # Konfigurationsdaten
        self.config_data = {}
        
        # Konfiguration laden
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Lädt die Konfiguration aus den Konfigurationsdateien
        """
        # Standardkonfiguration laden
        default_config = self._load_json(self.default_config_path)
        
        # Wenn die Standardkonfiguration nicht existiert, erstellen
        if not default_config:
            default_config = self._create_default_config()
        
        # Benutzerkonfiguration laden
        user_config = self._load_json(self.user_config_path)
        
        # Konfigurationen zusammenführen (Benutzereinstellungen haben Vorrang)
        self.config_data = {**default_config, **(user_config or {})}
        
        # Sicherstellen, dass die Benutzerkonfiguration existiert
        if not user_config:
            self.save_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Erstellt die Standardkonfiguration
        
        Returns:
            dict: Die Standardkonfiguration
        """
        default_config = {
            # Grundeinstellungen
            "version": "v2.0",
            "title": "ChromSploit",
            "subtitle": "by Leviticus-Triage",
            
            # Anzeigeeinstellungen
            "terminal_width": 120,
            "box_width": 80,
            "show_ascii_art": True,
            "show_status_bar": True,
            "color_theme": "default",
            
            # Logging-Einstellungen
            "debug_level": 1,
            "max_log_lines": 50,
            "auto_save_logs": True,
            "log_rotation": True,
            
            # Sicherheitseinstellungen
            "confirm_execution": True,
            "sandbox_mode": False,
            "stealth_mode": False,
            
            # Netzwerkeinstellungen
            "default_listen_address": "0.0.0.0",
            "default_listen_port": 8080,
            "use_proxy": False,
            "proxy_address": "127.0.0.1",
            "proxy_port": 8080,
            "connection_timeout": 30,
            
            # Tool-Integrations-Einstellungen
            "sliver_path": "/opt/sliver/sliver-server",
            "metasploit_path": "/opt/metasploit-framework",
            "ngrok_path": "/usr/local/bin/ngrok",
            "ollvm_path": "/opt/obfuscator-llvm",
            "backdoor_factory_path": "/opt/the-backdoor-factory",
            
            # Pfade
            "base_path": os.path.expanduser("~/.chromsploit"),
            "cve_data_path": os.path.expanduser("~/.chromsploit/cve_data"),
            "custom_exploits_path": os.path.expanduser("~/.chromsploit/custom_exploits"),
            "logs_path": os.path.expanduser("~/.chromsploit/logs"),
            "output_path": os.path.expanduser("~/.chromsploit/output"),
            "templates_path": os.path.expanduser("~/.chromsploit/templates"),
        }
        
        # Standardkonfiguration speichern
        self._save_json(self.default_config_path, default_config)
        
        # Verzeichnisse erstellen
        for path_key in ["base_path", "cve_data_path", "custom_exploits_path", "logs_path", "output_path", "templates_path"]:
            os.makedirs(default_config[path_key], exist_ok=True)
        
        return default_config
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """
        Lädt JSON-Daten aus einer Datei
        
        Args:
            file_path (str): Pfad zur JSON-Datei
            
        Returns:
            dict: Die geladenen JSON-Daten oder ein leeres Dictionary bei Fehler
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"{Colors.RED}[!] Fehler beim Laden der Konfiguration: {str(e)}{Colors.RESET}")
        return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]) -> bool:
        """
        Speichert JSON-Daten in eine Datei
        
        Args:
            file_path (str): Pfad zur JSON-Datei
            data (dict): Die zu speichernden JSON-Daten
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Verzeichnis erstellen, falls es nicht existiert
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"{Colors.RED}[!] Fehler beim Speichern der Konfiguration: {str(e)}{Colors.RESET}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Gibt den Wert eines Konfigurationsschlüssels zurück
        
        Args:
            key (str): Der Konfigurationsschlüssel
            default (Any, optional): Der Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            Any: Der Wert des Konfigurationsschlüssels oder der Standardwert
        """
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Setzt den Wert eines Konfigurationsschlüssels
        
        Args:
            key (str): Der Konfigurationsschlüssel
            value (Any): Der zu setzende Wert
        """
        self.config_data[key] = value
    
    def save_config(self) -> bool:
        """
        Speichert die aktuelle Konfiguration
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        return self._save_json(self.user_config_path, self.config_data)
    
    def reset_to_default(self) -> bool:
        """
        Setzt die Konfiguration auf die Standardwerte zurück
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        default_config = self._load_json(self.default_config_path)
        if default_config:
            self.config_data = default_config.copy()
            return self.save_config()
        return False
    
    def backup_config(self) -> str:
        """
        Erstellt ein Backup der aktuellen Konfiguration
        
        Returns:
            str: Pfad zum Backup oder leerer String bei Fehler
        """
        backup_path = f"{self.user_config_path}.bak.{int(time.time())}"
        if self._save_json(backup_path, self.config_data):
            return backup_path
        return ""
    
    def import_config(self, import_path: str) -> bool:
        """
        Importiert eine Konfiguration aus einer Datei
        
        Args:
            import_path (str): Pfad zur zu importierenden Konfigurationsdatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        imported_config = self._load_json(import_path)
        if imported_config:
            # Backup erstellen
            self.backup_config()
            
            # Konfiguration importieren
            self.config_data = imported_config
            return self.save_config()
        return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        Gibt die gesamte Konfiguration zurück
        
        Returns:
            dict: Die gesamte Konfiguration
        """
        return self.config_data.copy()
