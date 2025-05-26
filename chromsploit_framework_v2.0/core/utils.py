#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Utility-Funktionen für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import re
import shutil
import socket
import random
import string
import platform
import subprocess
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

class Utils:
    """
    Allgemeine Utility-Funktionen für das ChromSploit Framework
    """
    
    @staticmethod
    def is_tool_available(tool_name: str) -> bool:
        """
        Überprüft, ob ein Tool im System verfügbar ist
        
        Args:
            tool_name (str): Name des Tools
            
        Returns:
            bool: True, wenn das Tool verfügbar ist, sonst False
        """
        return shutil.which(tool_name) is not None
    
    @staticmethod
    def get_ip_address() -> str:
        """
        Ermittelt die IP-Adresse des Systems
        
        Returns:
            str: Die IP-Adresse oder '127.0.0.1' bei Fehler
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def check_port_available(port: int, host: str = '127.0.0.1') -> bool:
        """
        Überprüft, ob ein Port verfügbar ist
        
        Args:
            port (int): Die zu überprüfende Portnummer
            host (str, optional): Der Host, auf dem der Port überprüft werden soll
            
        Returns:
            bool: True, wenn der Port verfügbar ist, sonst False
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((host, port))
            s.close()
            return result != 0
        except:
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 8000, end_port: int = 9000, host: str = '127.0.0.1') -> int:
        """
        Findet einen verfügbaren Port im angegebenen Bereich
        
        Args:
            start_port (int, optional): Startport für die Suche
            end_port (int, optional): Endport für die Suche
            host (str, optional): Der Host, auf dem der Port überprüft werden soll
            
        Returns:
            int: Ein verfügbarer Port oder -1, wenn kein Port verfügbar ist
        """
        for port in range(start_port, end_port + 1):
            if Utils.check_port_available(port, host):
                return port
        return -1
    
    @staticmethod
    def generate_random_string(length: int = 10, include_special: bool = False) -> str:
        """
        Generiert einen zufälligen String
        
        Args:
            length (int, optional): Länge des zu generierenden Strings
            include_special (bool, optional): Ob Sonderzeichen eingeschlossen werden sollen
            
        Returns:
            str: Der generierte zufällige String
        """
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def execute_command(command: str, timeout: int = 60, shell: bool = True) -> Tuple[int, str, str]:
        """
        Führt einen Befehl aus und gibt das Ergebnis zurück
        
        Args:
            command (str): Der auszuführende Befehl
            timeout (int, optional): Timeout in Sekunden
            shell (bool, optional): Ob der Befehl in einer Shell ausgeführt werden soll
            
        Returns:
            tuple: (Rückgabecode, Standardausgabe, Standardfehlerausgabe)
        """
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=shell,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Timeout expired"
        except Exception as e:
            return -1, "", str(e)
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Überprüft, ob eine IP-Adresse gültig ist
        
        Args:
            ip (str): Die zu überprüfende IP-Adresse
            
        Returns:
            bool: True, wenn die IP-Adresse gültig ist, sonst False
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        # Überprüfen, ob jedes Oktett im gültigen Bereich liegt
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    
    @staticmethod
    def is_valid_port(port: Union[str, int]) -> bool:
        """
        Überprüft, ob ein Port gültig ist
        
        Args:
            port (Union[str, int]): Der zu überprüfende Port
            
        Returns:
            bool: True, wenn der Port gültig ist, sonst False
        """
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except:
            return False
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Gibt einen formatierten Zeitstempel zurück
        
        Returns:
            str: Der formatierte Zeitstempel
        """
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """
        Sammelt Informationen über das System
        
        Returns:
            dict: Systeminformationen
        """
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'ip_address': Utils.get_ip_address(),
            'python_version': platform.python_version()
        }
        
        # Linux-spezifische Informationen
        if platform.system() == 'Linux':
            try:
                # Kernel-Version
                kernel = subprocess.check_output(['uname', '-r']).decode().strip()
                info['kernel'] = kernel
                
                # Distribution
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release', 'r') as f:
                        os_release = f.read()
                        
                    # Name der Distribution
                    match = re.search(r'PRETTY_NAME="([^"]+)"', os_release)
                    if match:
                        info['distribution'] = match.group(1)
                
                # CPU-Informationen
                if os.path.exists('/proc/cpuinfo'):
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                    
                    # CPU-Modell
                    match = re.search(r'model name\s+:\s+(.+)', cpuinfo)
                    if match:
                        info['cpu_model'] = match.group(1)
                    
                    # CPU-Kerne
                    cores = len(re.findall(r'processor\s+:', cpuinfo))
                    info['cpu_cores'] = str(cores)
                
                # Arbeitsspeicher
                if os.path.exists('/proc/meminfo'):
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                    
                    # Gesamter Arbeitsspeicher
                    match = re.search(r'MemTotal:\s+(\d+)', meminfo)
                    if match:
                        mem_total = int(match.group(1)) // 1024
                        info['memory_total'] = f"{mem_total} MB"
            except:
                pass
        
        return info
    
    @staticmethod
    def format_bytes(size: int) -> str:
        """
        Formatiert eine Bytegröße in eine lesbare Form
        
        Args:
            size (int): Die Größe in Bytes
            
        Returns:
            str: Die formatierte Größe
        """
        power = 2**10
        n = 0
        power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        
        while size > power and n < 4:
            size /= power
            n += 1
        
        return f"{size:.2f} {power_labels[n]}"
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Überprüft, ob ein Prozess läuft
        
        Args:
            process_name (str): Name des Prozesses
            
        Returns:
            bool: True, wenn der Prozess läuft, sonst False
        """
        if platform.system() == 'Windows':
            output = subprocess.check_output('tasklist', shell=True).decode()
            return process_name.lower() in output.lower()
        else:
            try:
                output = subprocess.check_output(['pgrep', '-f', process_name]).decode()
                return bool(output.strip())
            except:
                return False
    
    @staticmethod
    def kill_process(process_name: str) -> bool:
        """
        Beendet einen Prozess
        
        Args:
            process_name (str): Name des Prozesses
            
        Returns:
            bool: True, wenn der Prozess beendet wurde, sonst False
        """
        try:
            if platform.system() == 'Windows':
                subprocess.call(['taskkill', '/F', '/IM', process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.call(['pkill', '-f', process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False
