#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Pfad-Utility-Funktionen für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

class PathUtils:
    """
    Pfad-Utility-Funktionen für das ChromSploit Framework
    """
    
    @staticmethod
    def get_base_dir() -> str:
        """
        Gibt das Basisverzeichnis des Frameworks zurück
        
        Returns:
            str: Das Basisverzeichnis
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_core_dir() -> str:
        """
        Gibt das Core-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Core-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'core')
    
    @staticmethod
    def get_ui_dir() -> str:
        """
        Gibt das UI-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das UI-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'ui')
    
    @staticmethod
    def get_exploits_dir() -> str:
        """
        Gibt das Exploits-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Exploits-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'exploits')
    
    @staticmethod
    def get_tools_dir() -> str:
        """
        Gibt das Tools-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Tools-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'tools')
    
    @staticmethod
    def get_utils_dir() -> str:
        """
        Gibt das Utils-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Utils-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'utils')
    
    @staticmethod
    def get_data_dir() -> str:
        """
        Gibt das Data-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Data-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'data')
    
    @staticmethod
    def get_logs_dir() -> str:
        """
        Gibt das Logs-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Logs-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'logs')
    
    @staticmethod
    def get_output_dir() -> str:
        """
        Gibt das Output-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Output-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'output')
    
    @staticmethod
    def get_config_dir() -> str:
        """
        Gibt das Config-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Config-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'config')
    
    @staticmethod
    def get_docs_dir() -> str:
        """
        Gibt das Docs-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Docs-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'docs')
    
    @staticmethod
    def get_tests_dir() -> str:
        """
        Gibt das Tests-Verzeichnis des Frameworks zurück
        
        Returns:
            str: Das Tests-Verzeichnis
        """
        return os.path.join(PathUtils.get_base_dir(), 'tests')
    
    @staticmethod
    def get_exploit_dir(cve_id: str) -> str:
        """
        Gibt das Verzeichnis für einen bestimmten CVE-Exploit zurück
        
        Args:
            cve_id (str): Die CVE-ID (z.B. 'cve_2025_4664')
            
        Returns:
            str: Das Exploit-Verzeichnis
        """
        return os.path.join(PathUtils.get_exploits_dir(), cve_id.lower())
    
    @staticmethod
    def get_templates_dir(cve_id: Optional[str] = None) -> str:
        """
        Gibt das Templates-Verzeichnis zurück
        
        Args:
            cve_id (str, optional): Die CVE-ID für CVE-spezifische Templates
            
        Returns:
            str: Das Templates-Verzeichnis
        """
        if cve_id:
            return os.path.join(PathUtils.get_exploit_dir(cve_id), 'templates')
        else:
            return os.path.join(PathUtils.get_data_dir(), 'templates')
    
    @staticmethod
    def get_payloads_dir() -> str:
        """
        Gibt das Payloads-Verzeichnis zurück
        
        Returns:
            str: Das Payloads-Verzeichnis
        """
        return os.path.join(PathUtils.get_data_dir(), 'payloads')
    
    @staticmethod
    def get_certificates_dir() -> str:
        """
        Gibt das Certificates-Verzeichnis zurück
        
        Returns:
            str: Das Certificates-Verzeichnis
        """
        return os.path.join(PathUtils.get_data_dir(), 'certificates')
    
    @staticmethod
    def get_wordlists_dir() -> str:
        """
        Gibt das Wordlists-Verzeichnis zurück
        
        Returns:
            str: Das Wordlists-Verzeichnis
        """
        return os.path.join(PathUtils.get_data_dir(), 'wordlists')
    
    @staticmethod
    def ensure_dir_exists(directory: str) -> bool:
        """
        Stellt sicher, dass ein Verzeichnis existiert
        
        Args:
            directory (str): Das zu überprüfende Verzeichnis
            
        Returns:
            bool: True, wenn das Verzeichnis existiert oder erstellt wurde, sonst False
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except:
            return False
    
    @staticmethod
    def ensure_framework_dirs() -> None:
        """
        Stellt sicher, dass alle Framework-Verzeichnisse existieren
        """
        dirs = [
            PathUtils.get_core_dir(),
            PathUtils.get_ui_dir(),
            PathUtils.get_exploits_dir(),
            PathUtils.get_tools_dir(),
            PathUtils.get_utils_dir(),
            PathUtils.get_data_dir(),
            PathUtils.get_logs_dir(),
            PathUtils.get_output_dir(),
            PathUtils.get_config_dir(),
            PathUtils.get_docs_dir(),
            PathUtils.get_tests_dir(),
            PathUtils.get_templates_dir(),
            PathUtils.get_payloads_dir(),
            PathUtils.get_certificates_dir(),
            PathUtils.get_wordlists_dir()
        ]
        
        for directory in dirs:
            PathUtils.ensure_dir_exists(directory)
    
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """
        Überprüft, ob ein Pfad gültig ist
        
        Args:
            path (str): Der zu überprüfende Pfad
            
        Returns:
            bool: True, wenn der Pfad gültig ist, sonst False
        """
        try:
            Path(path).resolve()
            return True
        except:
            return False
    
    @staticmethod
    def is_path_writable(path: str) -> bool:
        """
        Überprüft, ob ein Pfad beschreibbar ist
        
        Args:
            path (str): Der zu überprüfende Pfad
            
        Returns:
            bool: True, wenn der Pfad beschreibbar ist, sonst False
        """
        if not os.path.exists(path):
            # Wenn der Pfad nicht existiert, überprüfen, ob das übergeordnete Verzeichnis beschreibbar ist
            parent_dir = os.path.dirname(path)
            if not os.path.exists(parent_dir):
                return False
            path = parent_dir
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def is_path_readable(path: str) -> bool:
        """
        Überprüft, ob ein Pfad lesbar ist
        
        Args:
            path (str): Der zu überprüfende Pfad
            
        Returns:
            bool: True, wenn der Pfad lesbar ist, sonst False
        """
        return os.path.exists(path) and os.access(path, os.R_OK)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Gibt die Größe einer Datei zurück
        
        Args:
            file_path (str): Pfad zur Datei
            
        Returns:
            int: Die Größe der Datei in Bytes oder -1 bei Fehler
        """
        try:
            return os.path.getsize(file_path)
        except:
            return -1
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Gibt die Dateierweiterung zurück
        
        Args:
            file_path (str): Pfad zur Datei
            
        Returns:
            str: Die Dateierweiterung oder leerer String bei Fehler
        """
        try:
            return os.path.splitext(file_path)[1].lower()
        except:
            return ""
