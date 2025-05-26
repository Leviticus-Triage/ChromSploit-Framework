#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Live Monitoring und Debug System
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import psutil
import threading
import queue
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class LiveMonitor:
    """
    Live Monitoring und Debug System für ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert das Live Monitoring System
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.log_queue = queue.Queue()
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.log_level = "INFO"
        self.log_filters = []
        self.log_callbacks = []
        self.system_info_callbacks = []
        self.refresh_rate = 1.0  # Aktualisierungsrate in Sekunden
        
        # Farbkodierung für verschiedene Log-Level
        self.level_colors = {
            "DEBUG": Colors.MAGENTA,
            "INFO": Colors.BLUE,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED_BOLD
        }
    
    def log(self, level: str, message: str) -> None:
        """
        Loggt eine Nachricht
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        if self.logger:
            if level.upper() == "INFO":
                self.logger.info(message)
            elif level.upper() == "WARNING":
                self.logger.warning(message)
            elif level.upper() == "ERROR":
                self.logger.error(message)
            elif level.upper() == "DEBUG":
                self.logger.debug(message)
            elif level.upper() == "CRITICAL":
                self.logger.critical(message)
        else:
            color = self.level_colors.get(level.upper(), Colors.RESET)
            print(f"{color}[{level.upper()}] {message}{Colors.RESET}")
    
    def set_log_level(self, level: str) -> None:
        """
        Setzt das Log-Level für die Anzeige
        
        Args:
            level (str): Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level.upper()
        self.log("INFO", f"Log-Level auf {self.log_level} gesetzt")
    
    def add_log_filter(self, filter_str: str) -> None:
        """
        Fügt einen Filter für Logs hinzu
        
        Args:
            filter_str (str): Filterstring
        """
        self.log_filters.append(filter_str)
        self.log("INFO", f"Log-Filter hinzugefügt: {filter_str}")
    
    def clear_log_filters(self) -> None:
        """
        Löscht alle Log-Filter
        """
        self.log_filters = []
        self.log("INFO", "Alle Log-Filter gelöscht")
    
    def add_log_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """
        Fügt einen Callback für Logs hinzu
        
        Args:
            callback (callable): Callback-Funktion (level, timestamp, message)
        """
        self.log_callbacks.append(callback)
    
    def add_system_info_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Fügt einen Callback für Systeminformationen hinzu
        
        Args:
            callback (callable): Callback-Funktion (system_info)
        """
        self.system_info_callbacks.append(callback)
    
    def start_monitoring(self) -> None:
        """
        Startet das Monitoring in einem separaten Thread
        """
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.log("WARNING", "Monitoring läuft bereits")
            return
        
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.log("INFO", "Live Monitoring gestartet")
    
    def stop_monitoring(self) -> None:
        """
        Stoppt das Monitoring
        """
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.log("WARNING", "Monitoring läuft nicht")
            return
        
        self.stop_event.set()
        self.monitor_thread.join(timeout=2.0)
        self.log("INFO", "Live Monitoring gestoppt")
    
    def _monitor_loop(self) -> None:
        """
        Hauptschleife für das Monitoring
        """
        while not self.stop_event.is_set():
            # Systeminformationen sammeln
            system_info = self._collect_system_info()
            
            # Callbacks für Systeminformationen aufrufen
            for callback in self.system_info_callbacks:
                try:
                    callback(system_info)
                except Exception as e:
                    print(f"{Colors.RED}[ERROR] Fehler im System-Info-Callback: {str(e)}{Colors.RESET}")
            
            # Logs aus der Queue verarbeiten
            self._process_log_queue()
            
            # Warten
            time.sleep(self.refresh_rate)
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """
        Sammelt Systeminformationen
        
        Returns:
            dict: Systeminformationen
        """
        try:
            # CPU-Auslastung
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Speicherauslastung
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Festplattenauslastung
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used
            disk_total = disk.total
            
            # Netzwerkstatistik
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent
            net_recv = net_io.bytes_recv
            
            # Prozesse
            process_count = len(psutil.pids())
            
            # Systemzeit
            system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            uptime_minutes = int((uptime_seconds % 3600) // 60)
            uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "percent": memory_percent,
                    "used": memory_used,
                    "total": memory_total,
                    "used_gb": memory_used / (1024 ** 3),
                    "total_gb": memory_total / (1024 ** 3)
                },
                "disk": {
                    "percent": disk_percent,
                    "used": disk_used,
                    "total": disk_total,
                    "used_gb": disk_used / (1024 ** 3),
                    "total_gb": disk_total / (1024 ** 3)
                },
                "network": {
                    "sent": net_sent,
                    "recv": net_recv,
                    "sent_mb": net_sent / (1024 ** 2),
                    "recv_mb": net_recv / (1024 ** 2)
                },
                "processes": {
                    "count": process_count
                },
                "system": {
                    "time": system_time,
                    "uptime": uptime_str,
                    "uptime_seconds": uptime_seconds
                }
            }
        except Exception as e:
            self.log("ERROR", f"Fehler beim Sammeln der Systeminformationen: {str(e)}")
            return {}
    
    def _process_log_queue(self) -> None:
        """
        Verarbeitet Logs aus der Queue
        """
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                level = log_entry.get("level", "INFO")
                timestamp = log_entry.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                message = log_entry.get("message", "")
                
                # Log-Level-Filter anwenden
                if self._should_display_log(level, message):
                    # Callbacks für Logs aufrufen
                    for callback in self.log_callbacks:
                        try:
                            callback(level, timestamp, message)
                        except Exception as e:
                            print(f"{Colors.RED}[ERROR] Fehler im Log-Callback: {str(e)}{Colors.RESET}")
                
                self.log_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"{Colors.RED}[ERROR] Fehler bei der Verarbeitung der Log-Queue: {str(e)}{Colors.RESET}")
                break
    
    def _should_display_log(self, level: str, message: str) -> bool:
        """
        Überprüft, ob ein Log angezeigt werden soll
        
        Args:
            level (str): Log-Level
            message (str): Log-Nachricht
            
        Returns:
            bool: True, wenn das Log angezeigt werden soll, sonst False
        """
        # Log-Level-Hierarchie
        level_hierarchy = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        
        # Log-Level-Filter anwenden
        if level_hierarchy.get(level.upper(), 0) < level_hierarchy.get(self.log_level, 0):
            return False
        
        # Log-Filter anwenden
        if self.log_filters:
            for filter_str in self.log_filters:
                if filter_str.lower() in message.lower():
                    return True
            return False
        
        return True
    
    def add_log_entry(self, level: str, message: str) -> None:
        """
        Fügt einen Log-Eintrag zur Queue hinzu
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.log_queue.put({
            "level": level.upper(),
            "timestamp": timestamp,
            "message": message
        })
    
    def format_log_entry(self, level: str, timestamp: str, message: str) -> str:
        """
        Formatiert einen Log-Eintrag
        
        Args:
            level (str): Log-Level
            timestamp (str): Zeitstempel
            message (str): Nachricht
            
        Returns:
            str: Formatierter Log-Eintrag
        """
        color = self.level_colors.get(level.upper(), Colors.RESET)
        return f"{color}[{timestamp}] [{level.upper()}] {message}{Colors.RESET}"
    
    def format_system_info(self, system_info: Dict[str, Any]) -> str:
        """
        Formatiert Systeminformationen
        
        Args:
            system_info (dict): Systeminformationen
            
        Returns:
            str: Formatierte Systeminformationen
        """
        if not system_info:
            return "Keine Systeminformationen verfügbar"
        
        cpu_info = system_info.get("cpu", {})
        memory_info = system_info.get("memory", {})
        disk_info = system_info.get("disk", {})
        network_info = system_info.get("network", {})
        process_info = system_info.get("processes", {})
        system_time_info = system_info.get("system", {})
        
        # CPU-Auslastung
        cpu_percent = cpu_info.get("percent", 0)
        cpu_count = cpu_info.get("count", 0)
        cpu_color = Colors.GREEN if cpu_percent < 50 else Colors.YELLOW if cpu_percent < 80 else Colors.RED
        
        # Speicherauslastung
        memory_percent = memory_info.get("percent", 0)
        memory_used_gb = memory_info.get("used_gb", 0)
        memory_total_gb = memory_info.get("total_gb", 0)
        memory_color = Colors.GREEN if memory_percent < 50 else Colors.YELLOW if memory_percent < 80 else Colors.RED
        
        # Festplattenauslastung
        disk_percent = disk_info.get("percent", 0)
        disk_used_gb = disk_info.get("used_gb", 0)
        disk_total_gb = disk_info.get("total_gb", 0)
        disk_color = Colors.GREEN if disk_percent < 50 else Colors.YELLOW if disk_percent < 80 else Colors.RED
        
        # Netzwerkstatistik
        net_sent_mb = network_info.get("sent_mb", 0)
        net_recv_mb = network_info.get("recv_mb", 0)
        
        # Prozesse
        process_count = process_info.get("count", 0)
        
        # Systemzeit und Uptime
        system_time = system_time_info.get("time", "")
        uptime = system_time_info.get("uptime", "")
        
        # Formatierte Ausgabe
        output = f"""
{Colors.CYAN_BOLD}=== SYSTEM INFORMATION ==={Colors.RESET}
{Colors.CYAN}System Time:{Colors.RESET} {system_time}
{Colors.CYAN}Uptime:{Colors.RESET} {uptime}

{Colors.CYAN_BOLD}CPU:{Colors.RESET} {cpu_color}{cpu_percent:.1f}%{Colors.RESET} ({cpu_count} cores)
{self._generate_progress_bar(cpu_percent, cpu_color)}

{Colors.CYAN_BOLD}Memory:{Colors.RESET} {memory_color}{memory_percent:.1f}%{Colors.RESET} ({memory_used_gb:.1f} GB / {memory_total_gb:.1f} GB)
{self._generate_progress_bar(memory_percent, memory_color)}

{Colors.CYAN_BOLD}Disk:{Colors.RESET} {disk_color}{disk_percent:.1f}%{Colors.RESET} ({disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB)
{self._generate_progress_bar(disk_percent, disk_color)}

{Colors.CYAN_BOLD}Network:{Colors.RESET}
{Colors.CYAN}↑ Sent:{Colors.RESET} {net_sent_mb:.2f} MB
{Colors.CYAN}↓ Received:{Colors.RESET} {net_recv_mb:.2f} MB

{Colors.CYAN_BOLD}Processes:{Colors.RESET} {process_count}
"""
        
        return output
    
    def _generate_progress_bar(self, percent: float, color: str, width: int = 30) -> str:
        """
        Generiert einen Fortschrittsbalken
        
        Args:
            percent (float): Prozentsatz
            color (str): Farbe
            width (int, optional): Breite des Balkens
            
        Returns:
            str: Formatierter Fortschrittsbalken
        """
        filled_width = int(width * percent / 100)
        empty_width = width - filled_width
        
        bar = f"{color}{'█' * filled_width}{Colors.RESET}{'░' * empty_width} {percent:.1f}%"
        
        return bar
    
    def tail_log_file(self, log_file: str, lines: int = 10) -> List[str]:
        """
        Liest die letzten Zeilen einer Log-Datei
        
        Args:
            log_file (str): Pfad zur Log-Datei
            lines (int, optional): Anzahl der Zeilen
            
        Returns:
            list: Liste der letzten Zeilen
        """
        if not os.path.exists(log_file):
            self.log("ERROR", f"Log-Datei existiert nicht: {log_file}")
            return []
        
        try:
            with open(log_file, "r") as f:
                # Alle Zeilen lesen
                all_lines = f.readlines()
                
                # Letzte Zeilen zurückgeben
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            self.log("ERROR", f"Fehler beim Lesen der Log-Datei: {str(e)}")
            return []
    
    def watch_log_file(self, log_file: str) -> None:
        """
        Überwacht eine Log-Datei und fügt neue Einträge zur Queue hinzu
        
        Args:
            log_file (str): Pfad zur Log-Datei
        """
        if not os.path.exists(log_file):
            self.log("ERROR", f"Log-Datei existiert nicht: {log_file}")
            return
        
        # Thread zum Überwachen der Log-Datei starten
        watch_thread = threading.Thread(
            target=self._watch_log_file_thread,
            args=(log_file,),
            daemon=True
        )
        watch_thread.start()
        
        self.log("INFO", f"Überwachung der Log-Datei gestartet: {log_file}")
    
    def _watch_log_file_thread(self, log_file: str) -> None:
        """
        Thread-Funktion zum Überwachen einer Log-Datei
        
        Args:
            log_file (str): Pfad zur Log-Datei
        """
        try:
            # Datei öffnen und an das Ende springen
            with open(log_file, "r") as f:
                f.seek(0, 2)  # Zum Ende der Datei springen
                
                while not self.stop_event.is_set():
                    line = f.readline()
                    
                    if line:
                        # Neue Zeile zur Queue hinzufügen
                        self.add_log_entry("INFO", line.strip())
                    else:
                        # Kurz warten, wenn keine neue Zeile verfügbar ist
                        time.sleep(0.1)
        except Exception as e:
            self.log("ERROR", f"Fehler beim Überwachen der Log-Datei: {str(e)}")
    
    def get_debug_settings(self) -> Dict[str, Any]:
        """
        Gibt die aktuellen Debug-Einstellungen zurück
        
        Returns:
            dict: Debug-Einstellungen
        """
        return {
            "log_level": self.log_level,
            "log_filters": self.log_filters,
            "refresh_rate": self.refresh_rate,
            "monitoring_active": self.monitor_thread is not None and self.monitor_thread.is_alive()
        }
    
    def set_debug_settings(self, settings: Dict[str, Any]) -> None:
        """
        Setzt die Debug-Einstellungen
        
        Args:
            settings (dict): Debug-Einstellungen
        """
        if "log_level" in settings:
            self.set_log_level(settings["log_level"])
        
        if "log_filters" in settings:
            self.log_filters = settings["log_filters"]
        
        if "refresh_rate" in settings:
            self.refresh_rate = float(settings["refresh_rate"])
        
        self.log("INFO", "Debug-Einstellungen aktualisiert")
    
    def save_debug_settings(self, settings_file: Optional[str] = None) -> bool:
        """
        Speichert die Debug-Einstellungen in einer Datei
        
        Args:
            settings_file (str, optional): Pfad zur Einstellungsdatei
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not settings_file:
            settings_file = os.path.join(PathUtils.get_config_dir(), "debug_settings.json")
        
        try:
            settings = self.get_debug_settings()
            
            # Monitoring-Status nicht speichern
            if "monitoring_active" in settings:
                del settings["monitoring_active"]
            
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=4)
            
            self.log("INFO", f"Debug-Einstellungen gespeichert: {settings_file}")
            return True
        except Exception as e:
            self.log("ERROR", f"Fehler beim Speichern der Debug-Einstellungen: {str(e)}")
            return False
    
    def load_debug_settings(self, settings_file: Optional[str] = None) -> bool:
        """
        Lädt die Debug-Einstellungen aus einer Datei
        
        Args:
            settings_file (str, optional): Pfad zur Einstellungsdatei
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not settings_file:
            settings_file = os.path.join(PathUtils.get_config_dir(), "debug_settings.json")
        
        if not os.path.exists(settings_file):
            self.log("WARNING", f"Einstellungsdatei existiert nicht: {settings_file}")
            return False
        
        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
            
            self.set_debug_settings(settings)
            
            self.log("INFO", f"Debug-Einstellungen geladen: {settings_file}")
            return True
        except Exception as e:
            self.log("ERROR", f"Fehler beim Laden der Debug-Einstellungen: {str(e)}")
            return False
