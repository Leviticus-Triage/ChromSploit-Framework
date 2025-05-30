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
import re
import stat
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from urllib.parse import unquote

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
    
    @staticmethod
    def is_safe_path(path: str, allow_parent_traversal: bool = False) -> bool:
        """
        Überprüft, ob ein Pfad sicher ist (keine Path Traversal-Angriffe)
        
        Args:
            path (str): Der zu überprüfende Pfad
            allow_parent_traversal (bool): Ob Parent-Directory-Traversal erlaubt ist
            
        Returns:
            bool: True, wenn der Pfad sicher ist, sonst False
        """
        try:
            # URL-Dekodierung für Web-Pfade
            decoded_path = unquote(path)
            
            # Normalisiere Pfad
            normalized_path = os.path.normpath(decoded_path)
            
            # Überprüfe auf gefährliche Zeichen und Muster
            dangerous_patterns = [
                '../',
                '..\\',
                '/../',
                '\\..\\',
                '/..',
                '\\..',
                '%2e%2e/',
                '%2e%2e\\',
                '..%2f',
                '..%5c',
                '%c0%af',  # Unicode bypass
                '%c1%9c',  # Unicode bypass
                '\x00',    # Null byte
                '\r',      # Carriage return
                '\n'       # Newline
            ]
            
            path_lower = decoded_path.lower()
            for pattern in dangerous_patterns:
                if pattern in path_lower:
                    return False
            
            # Überprüfe auf absoluten Pfad wenn nicht erlaubt
            if os.path.isabs(normalized_path) and not allow_parent_traversal:
                # Erlaubt nur Framework-Basispfade
                base_dir = PathUtils.get_base_dir()
                try:
                    resolved_path = os.path.realpath(normalized_path)
                    if not resolved_path.startswith(base_dir):
                        return False
                except:
                    return False
            
            # Überprüfe auf Parent-Directory-Traversal
            if not allow_parent_traversal:
                if normalized_path.startswith('../') or '/../' in normalized_path:
                    return False
            
            # Überprüfe auf gefährliche Dateierweiterungen
            dangerous_extensions = [
                '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
                '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
                '.msi', '.dll', '.so', '.dylib'
            ]
            
            ext = PathUtils.get_file_extension(path)
            if ext in dangerous_extensions:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Bereinigt einen Dateinamen von gefährlichen Zeichen
        
        Args:
            filename (str): Der zu bereinigende Dateiname
            
        Returns:
            str: Der bereinigte Dateiname
        """
        # Entferne gefährliche Zeichen
        unsafe_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(unsafe_chars, '_', filename)
        
        # Entferne führende und abschließende Punkte und Leerzeichen
        sanitized = sanitized.strip('. ')
        
        # Verhindere reservierte Namen (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = os.path.splitext(sanitized)[0].upper()
        if name_without_ext in reserved_names:
            sanitized = f"_{sanitized}"
        
        # Begrenze Länge
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized or 'unnamed_file'
    
    @staticmethod
    def validate_file_path(file_path: str, base_dir: Optional[str] = None) -> bool:
        """
        Validiert einen Dateipfad umfassend
        
        Args:
            file_path (str): Der zu validierende Dateipfad
            base_dir (str, optional): Basisverzeichnis für relative Pfade
            
        Returns:
            bool: True, wenn der Pfad gültig ist, sonst False
        """
        try:
            if not file_path or not isinstance(file_path, str):
                return False
            
            # Überprüfe Pfadsicherheit
            if not PathUtils.is_safe_path(file_path):
                return False
            
            # Setze Basisverzeichnis falls nicht angegeben
            if base_dir is None:
                base_dir = PathUtils.get_base_dir()
            
            # Behandle relative Pfade
            if not os.path.isabs(file_path):
                file_path = os.path.join(base_dir, file_path)
            
            # Normalisiere und löse Pfad auf
            normalized_path = os.path.normpath(file_path)
            resolved_path = os.path.realpath(normalized_path)
            
            # Überprüfe, ob der aufgelöste Pfad innerhalb des Basisverzeichnisses liegt
            if not resolved_path.startswith(os.path.realpath(base_dir)):
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_secure_temp_path(prefix: str = 'chromsploit_', suffix: str = '') -> str:
        """
        Erstellt einen sicheren temporären Pfad
        
        Args:
            prefix (str): Präfix für den temporären Pfad
            suffix (str): Suffix für den temporären Pfad
            
        Returns:
            str: Sicherer temporärer Pfad
        """
        import tempfile
        import uuid
        
        # Bereinige Präfix und Suffix
        clean_prefix = PathUtils.sanitize_filename(prefix)
        clean_suffix = suffix if suffix else ''  # Don't sanitize suffix to preserve file extensions
        
        # Erstelle einzigartigen Namen
        unique_name = f"{clean_prefix}{uuid.uuid4().hex[:8]}{clean_suffix}"
        
        # Verwende Framework-spezifisches Temp-Verzeichnis
        temp_base = os.path.join(PathUtils.get_base_dir(), 'temp')
        PathUtils.ensure_dir_exists(temp_base)
        
        # Setze sichere Berechtigungen
        try:
            os.chmod(temp_base, stat.S_IRWXU)  # Nur Besitzer kann lesen/schreiben/ausführen
        except:
            pass
        
        return os.path.join(temp_base, unique_name)
    
    @staticmethod
    def is_within_base_directory(path: str, base_dir: Optional[str] = None) -> bool:
        """
        Überprüft, ob ein Pfad innerhalb des Basisverzeichnisses liegt
        
        Args:
            path (str): Der zu überprüfende Pfad
            base_dir (str, optional): Basisverzeichnis
            
        Returns:
            bool: True, wenn der Pfad innerhalb des Basisverzeichnisses liegt
        """
        try:
            if base_dir is None:
                base_dir = PathUtils.get_base_dir()
            
            # Normalisiere beide Pfade
            real_path = os.path.realpath(path)
            real_base = os.path.realpath(base_dir)
            
            # Überprüfe, ob der Pfad innerhalb der Basis liegt
            return real_path.startswith(real_base + os.sep) or real_path == real_base
        except Exception:
            return False
    
    @staticmethod
    def get_allowed_file_extensions() -> List[str]:
        """
        Gibt eine Liste erlaubter Dateierweiterungen zurück
        
        Returns:
            List[str]: Liste erlaubter Dateierweiterungen
        """
        return [
            '.txt', '.log', '.json', '.xml', '.csv', '.html', '.htm',
            '.py', '.js', '.css', '.md', '.rst', '.yaml', '.yml',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.bz2', '.7z',
            '.key', '.pem', '.crt', '.p12', '.pfx'
        ]
    
    @staticmethod
    def is_allowed_file_type(file_path: str) -> bool:
        """
        Überprüft, ob eine Datei einen erlaubten Typ hat
        
        Args:
            file_path (str): Pfad zur Datei
            
        Returns:
            bool: True, wenn der Dateityp erlaubt ist
        """
        extension = PathUtils.get_file_extension(file_path)
        allowed_extensions = PathUtils.get_allowed_file_extensions()
        return extension in allowed_extensions
    
    @staticmethod
    def create_secure_directory(directory: str, mode: int = 0o700) -> bool:
        """
        Erstellt ein Verzeichnis mit sicheren Berechtigungen
        
        Args:
            directory (str): Das zu erstellende Verzeichnis
            mode (int): Berechtigungsmodus (Standard: nur Besitzer)
            
        Returns:
            bool: True, wenn das Verzeichnis erstellt wurde
        """
        try:
            # Validiere Pfad
            if not PathUtils.is_safe_path(directory):
                return False
            
            # Erstelle Verzeichnis
            os.makedirs(directory, mode=mode, exist_ok=True)
            
            # Setze explizit Berechtigungen (für Systeme, die umask ignorieren)
            os.chmod(directory, mode)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def secure_file_copy(src: str, dst: str, preserve_permissions: bool = False) -> bool:
        """
        Kopiert eine Datei sicher mit Validierung
        
        Args:
            src (str): Quelldatei
            dst (str): Zieldatei
            preserve_permissions (bool): Berechtigungen beibehalten
            
        Returns:
            bool: True, wenn das Kopieren erfolgreich war
        """
        try:
            # Validiere beide Pfade
            if not PathUtils.validate_file_path(src) or not PathUtils.is_safe_path(dst):
                return False
            
            # Überprüfe, ob Quelldatei existiert und lesbar ist
            if not PathUtils.is_path_readable(src):
                return False
            
            # Erstelle Zielverzeichnis falls nötig
            dst_dir = os.path.dirname(dst)
            if not PathUtils.create_secure_directory(dst_dir):
                return False
            
            # Kopiere Datei
            shutil.copy2(src, dst) if preserve_permissions else shutil.copy(src, dst)
            
            # Setze sichere Berechtigungen für Zieldatei
            if not preserve_permissions:
                os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR)  # Nur Besitzer read/write
            
            return True
        except Exception:
            return False
