#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Logger-System für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.colors import Colors

class Logger:
    """
    Logger-System für das ChromSploit Framework
    Unterstützt verschiedene Logging-Level und Ausgabeformate
    """
    
    # Logging-Level
    LEVEL_CRITICAL = 50
    LEVEL_ERROR = 40
    LEVEL_WARNING = 30
    LEVEL_INFO = 20
    LEVEL_DEBUG = 10
    LEVEL_TRACE = 5
    
    def __init__(self, log_level: int = 1, log_file: Optional[str] = None, max_log_size: int = 10485760):
        """
        Initialisiert den Logger
        
        Args:
            log_level (int, optional): Logging-Level (1-5)
            log_file (str, optional): Pfad zur Log-Datei
            max_log_size (int, optional): Maximale Größe der Log-Datei in Bytes
        """
        self.log_level = log_level
        self.log_file = log_file
        self.max_log_size = max_log_size
        self.log_buffer = []
        self.log_buffer_lock = threading.Lock()
        self.log_buffer_max_size = 1000
        
        # Python-Logger initialisieren
        self.logger = logging.getLogger('chromsploit')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler für Konsolenausgabe
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(self._get_python_log_level(log_level))
        
        # Formatter für Konsolenausgabe
        console_formatter = logging.Formatter('%(message)s')
        self.console_handler.setFormatter(console_formatter)
        
        # Handler für Dateiausgabe, falls eine Log-Datei angegeben wurde
        if log_file:
            # Verzeichnis erstellen, falls es nicht existiert
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setLevel(logging.DEBUG)
            
            # Formatter für Dateiausgabe
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(self.file_handler)
        
        self.logger.addHandler(self.console_handler)
        
        # Initialen Log-Eintrag erstellen
        self.info(f"ChromSploit Logger initialisiert (Level: {log_level})")
    
    def _get_python_log_level(self, level: int) -> int:
        """
        Konvertiert den ChromSploit-Log-Level in einen Python-Log-Level
        
        Args:
            level (int): ChromSploit-Log-Level (1-5)
            
        Returns:
            int: Python-Log-Level
        """
        if level >= 5:
            return self.LEVEL_TRACE
        elif level == 4:
            return self.LEVEL_DEBUG
        elif level == 3:
            return self.LEVEL_INFO
        elif level == 2:
            return self.LEVEL_WARNING
        elif level == 1:
            return self.LEVEL_ERROR
        else:
            return self.LEVEL_CRITICAL
    
    def _add_to_buffer(self, level: str, message: str) -> None:
        """
        Fügt einen Log-Eintrag zum Puffer hinzu
        
        Args:
            level (str): Log-Level
            message (str): Log-Nachricht
        """
        with self.log_buffer_lock:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_buffer.append({
                'timestamp': timestamp,
                'level': level,
                'message': message
            })
            
            # Puffer auf maximale Größe begrenzen
            if len(self.log_buffer) > self.log_buffer_max_size:
                self.log_buffer.pop(0)
    
    def _check_log_rotation(self) -> None:
        """
        Überprüft, ob die Log-Datei rotiert werden muss
        """
        if self.log_file and os.path.exists(self.log_file):
            if os.path.getsize(self.log_file) > self.max_log_size:
                # Backup-Datei erstellen
                backup_file = f"{self.log_file}.{int(time.time())}"
                try:
                    os.rename(self.log_file, backup_file)
                    
                    # Neuen File-Handler erstellen
                    self.logger.removeHandler(self.file_handler)
                    self.file_handler = logging.FileHandler(self.log_file)
                    self.file_handler.setLevel(logging.DEBUG)
                    
                    # Formatter für Dateiausgabe
                    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    self.file_handler.setFormatter(file_formatter)
                    
                    self.logger.addHandler(self.file_handler)
                    
                    self.info(f"Log-Rotation durchgeführt: {backup_file}")
                except Exception as e:
                    self.error(f"Fehler bei Log-Rotation: {str(e)}")
    
    def critical(self, message: str) -> None:
        """
        Loggt eine kritische Nachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        formatted_message = f"{Colors.BRIGHT_RED}[KRITISCH] {message}{Colors.RESET}"
        self.logger.critical(formatted_message)
        self._add_to_buffer('KRITISCH', message)
        self._check_log_rotation()
    
    def error(self, message: str) -> None:
        """
        Loggt eine Fehlernachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        formatted_message = f"{Colors.RED}[FEHLER] {message}{Colors.RESET}"
        self.logger.error(formatted_message)
        self._add_to_buffer('FEHLER', message)
        self._check_log_rotation()
    
    def warning(self, message: str) -> None:
        """
        Loggt eine Warnungsnachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        if self.log_level >= 2:
            formatted_message = f"{Colors.YELLOW}[WARNUNG] {message}{Colors.RESET}"
            self.logger.warning(formatted_message)
            self._add_to_buffer('WARNUNG', message)
            self._check_log_rotation()
    
    def info(self, message: str) -> None:
        """
        Loggt eine Informationsnachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        if self.log_level >= 3:
            formatted_message = f"{Colors.BLUE}[INFO] {message}{Colors.RESET}"
            self.logger.info(formatted_message)
            self._add_to_buffer('INFO', message)
            self._check_log_rotation()
    
    def debug(self, message: str) -> None:
        """
        Loggt eine Debug-Nachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        if self.log_level >= 4:
            formatted_message = f"{Colors.MAGENTA}[DEBUG] {message}{Colors.RESET}"
            self.logger.debug(formatted_message)
            self._add_to_buffer('DEBUG', message)
            self._check_log_rotation()
    
    def trace(self, message: str) -> None:
        """
        Loggt eine Trace-Nachricht
        
        Args:
            message (str): Die zu loggende Nachricht
        """
        if self.log_level >= 5:
            formatted_message = f"{Colors.CYAN}[TRACE] {message}{Colors.RESET}"
            self.logger.log(self.LEVEL_TRACE, formatted_message)
            self._add_to_buffer('TRACE', message)
            self._check_log_rotation()
    
    def get_log_buffer(self, count: int = 50, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt den Log-Puffer zurück
        
        Args:
            count (int, optional): Anzahl der zurückzugebenden Log-Einträge
            level (str, optional): Nur Log-Einträge mit diesem Level zurückgeben
            
        Returns:
            list: Liste von Log-Einträgen
        """
        with self.log_buffer_lock:
            if level:
                filtered_logs = [log for log in self.log_buffer if log['level'] == level]
                return filtered_logs[-count:]
            else:
                return self.log_buffer[-count:]
    
    def clear_log_buffer(self) -> None:
        """
        Leert den Log-Puffer
        """
        with self.log_buffer_lock:
            self.log_buffer = []
    
    def set_log_level(self, level: int) -> None:
        """
        Setzt den Log-Level
        
        Args:
            level (int): Der neue Log-Level (1-5)
        """
        self.log_level = level
        self.console_handler.setLevel(self._get_python_log_level(level))
        self.info(f"Log-Level geändert auf: {level}")
    
    def get_log_level(self) -> int:
        """
        Gibt den aktuellen Log-Level zurück
        
        Returns:
            int: Der aktuelle Log-Level
        """
        return self.log_level
