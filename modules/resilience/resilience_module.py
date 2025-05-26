#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Resilience-Modul mit selbstheilenden Infrastrukturkomponenten
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import socket
import threading
import subprocess
import psutil
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

try:
    import pybreaker
except ImportError:
    raise ImportError("Das Modul 'pybreaker' ist erforderlich für das Resilience-Modul. Installieren Sie es mit 'pip install pybreaker'.")

class CircuitBreaker:
    """
    Circuit Breaker für fehlertolerante Operationen
    """
    
    def __init__(self, name: str, fail_max: int = 5, reset_timeout: int = 60):
        """
        Initialisiert den Circuit Breaker
        
        Args:
            name (str): Name des Circuit Breakers
            fail_max (int): Maximale Anzahl an Fehlern, bevor der Circuit geöffnet wird
            reset_timeout (int): Timeout in Sekunden, bevor der Circuit wieder geschlossen wird
        """
        self.name = name
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            name=name
        )
        
        # Event-Listener hinzufügen
        self.breaker.add_listener(self._on_state_change)
    
    def _on_state_change(self, breaker: pybreaker.CircuitBreaker) -> None:
        """
        Wird aufgerufen, wenn sich der Zustand des Circuit Breakers ändert
        
        Args:
            breaker (CircuitBreaker): Circuit Breaker-Instanz
        """
        print(f"[CircuitBreaker] {breaker.name}: Zustand geändert zu {breaker.current_state}")
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Führt eine Funktion mit Circuit Breaker-Schutz aus
        
        Args:
            func (callable): Auszuführende Funktion
            *args: Argumente für die Funktion
            **kwargs: Keyword-Argumente für die Funktion
            
        Returns:
            Any: Rückgabewert der Funktion
            
        Raises:
            pybreaker.CircuitBreakerError: Wenn der Circuit geöffnet ist
        """
        return self.breaker.call(func, *args, **kwargs)

class ServiceMonitor:
    """
    Überwacht und verwaltet Dienste
    """
    
    def __init__(self):
        """
        Initialisiert den Service-Monitor
        """
        self.services = {}
        self.monitor_thread = None
        self.running = False
    
    def register_service(self, name: str, check_func: Callable, restart_func: Callable, check_interval: int = 30) -> None:
        """
        Registriert einen Dienst zur Überwachung
        
        Args:
            name (str): Name des Dienstes
            check_func (callable): Funktion zur Überprüfung des Dienstes
            restart_func (callable): Funktion zum Neustart des Dienstes
            check_interval (int): Intervall in Sekunden zwischen Überprüfungen
        """
        self.services[name] = {
            'check_func': check_func,
            'restart_func': restart_func,
            'check_interval': check_interval,
            'last_check': time.time(),
            'status': 'unknown',
            'failures': 0,
            'circuit_breaker': CircuitBreaker(f"service_{name}")
        }
    
    def start_monitoring(self) -> None:
        """
        Startet die Überwachung der registrierten Dienste
        """
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """
        Stoppt die Überwachung der registrierten Dienste
        """
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self) -> None:
        """
        Überwachungsschleife für registrierte Dienste
        """
        while self.running:
            current_time = time.time()
            
            for name, service in self.services.items():
                if current_time - service['last_check'] >= service['check_interval']:
                    self._check_and_restart_service(name)
                    service['last_check'] = current_time
            
            time.sleep(1)
    
    def _check_and_restart_service(self, name: str) -> None:
        """
        Überprüft einen Dienst und startet ihn bei Bedarf neu
        
        Args:
            name (str): Name des Dienstes
        """
        service = self.services[name]
        
        try:
            # Dienst überprüfen
            status = service['circuit_breaker'].execute(service['check_func'])
            
            if status:
                service['status'] = 'running'
                service['failures'] = 0
            else:
                service['status'] = 'failed'
                service['failures'] += 1
                
                # Neustart versuchen
                if service['failures'] <= 3:  # Maximal 3 Neustartversuche
                    print(f"[ServiceMonitor] Dienst '{name}' ist ausgefallen. Neustart wird versucht...")
                    service['circuit_breaker'].execute(service['restart_func'])
        except pybreaker.CircuitBreakerError:
            print(f"[ServiceMonitor] Circuit Breaker für Dienst '{name}' ist geöffnet. Neustart wird übersprungen.")

class NetworkResilience:
    """
    Netzwerk-Resilienz-Funktionen
    """
    
    def __init__(self):
        """
        Initialisiert die Netzwerk-Resilienz
        """
        self.connections = {}
        self.fallback_endpoints = {}
    
    def register_endpoint(self, name: str, primary_endpoint: str, fallback_endpoints: List[str]) -> None:
        """
        Registriert einen Endpunkt mit Fallback-Optionen
        
        Args:
            name (str): Name des Endpunkts
            primary_endpoint (str): Primärer Endpunkt (z.B. "192.168.1.1:8080")
            fallback_endpoints (list): Liste von Fallback-Endpunkten
        """
        self.fallback_endpoints[name] = {
            'primary': primary_endpoint,
            'fallbacks': fallback_endpoints,
            'current': primary_endpoint,
            'circuit_breaker': CircuitBreaker(f"endpoint_{name}")
        }
    
    def get_endpoint(self, name: str) -> str:
        """
        Gibt den aktuellen Endpunkt zurück
        
        Args:
            name (str): Name des Endpunkts
            
        Returns:
            str: Aktueller Endpunkt
            
        Raises:
            KeyError: Wenn der Endpunkt nicht registriert ist
        """
        if name not in self.fallback_endpoints:
            raise KeyError(f"Endpunkt '{name}' ist nicht registriert")
        
        return self.fallback_endpoints[name]['current']
    
    def check_endpoint(self, name: str) -> bool:
        """
        Überprüft einen Endpunkt und wechselt bei Bedarf zum Fallback
        
        Args:
            name (str): Name des Endpunkts
            
        Returns:
            bool: True, wenn der Endpunkt erreichbar ist, sonst False
            
        Raises:
            KeyError: Wenn der Endpunkt nicht registriert ist
        """
        if name not in self.fallback_endpoints:
            raise KeyError(f"Endpunkt '{name}' ist nicht registriert")
        
        endpoint_info = self.fallback_endpoints[name]
        current_endpoint = endpoint_info['current']
        
        try:
            # Endpunkt überprüfen
            def check_connection():
                host, port = current_endpoint.split(':')
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, int(port)))
                sock.close()
                return result == 0
            
            is_available = endpoint_info['circuit_breaker'].execute(check_connection)
            
            if not is_available:
                # Zum nächsten Fallback wechseln
                self._switch_to_fallback(name)
                return False
            
            return True
        except pybreaker.CircuitBreakerError:
            # Circuit Breaker ist geöffnet, zum nächsten Fallback wechseln
            self._switch_to_fallback(name)
            return False
    
    def _switch_to_fallback(self, name: str) -> None:
        """
        Wechselt zum nächsten Fallback-Endpunkt
        
        Args:
            name (str): Name des Endpunkts
        """
        endpoint_info = self.fallback_endpoints[name]
        current_endpoint = endpoint_info['current']
        
        # Wenn der aktuelle Endpunkt der primäre ist, zum ersten Fallback wechseln
        if current_endpoint == endpoint_info['primary']:
            if endpoint_info['fallbacks']:
                endpoint_info['current'] = endpoint_info['fallbacks'][0]
                print(f"[NetworkResilience] Wechsel von primärem Endpunkt zu Fallback für '{name}': {endpoint_info['current']}")
            else:
                print(f"[NetworkResilience] Keine Fallbacks für '{name}' verfügbar")
        else:
            # Zum nächsten Fallback wechseln
            try:
                current_index = endpoint_info['fallbacks'].index(current_endpoint)
                if current_index < len(endpoint_info['fallbacks']) - 1:
                    endpoint_info['current'] = endpoint_info['fallbacks'][current_index + 1]
                    print(f"[NetworkResilience] Wechsel zum nächsten Fallback für '{name}': {endpoint_info['current']}")
                else:
                    # Zurück zum primären Endpunkt
                    endpoint_info['current'] = endpoint_info['primary']
                    print(f"[NetworkResilience] Zurück zum primären Endpunkt für '{name}': {endpoint_info['current']}")
            except ValueError:
                # Zurück zum primären Endpunkt
                endpoint_info['current'] = endpoint_info['primary']
                print(f"[NetworkResilience] Zurück zum primären Endpunkt für '{name}': {endpoint_info['current']}")

class ResourceMonitor:
    """
    Überwacht Systemressourcen und führt Aktionen bei Überlastung aus
    """
    
    def __init__(self):
        """
        Initialisiert den Resource-Monitor
        """
        self.thresholds = {
            'cpu': 90.0,  # Prozent
            'memory': 90.0,  # Prozent
            'disk': 90.0  # Prozent
        }
        self.actions = {
            'cpu': [],
            'memory': [],
            'disk': []
        }
        self.monitor_thread = None
        self.running = False
    
    def set_threshold(self, resource: str, threshold: float) -> None:
        """
        Setzt den Schwellenwert für eine Ressource
        
        Args:
            resource (str): Ressourcentyp ('cpu', 'memory', 'disk')
            threshold (float): Schwellenwert in Prozent
            
        Raises:
            ValueError: Wenn der Ressourcentyp ungültig ist
        """
        if resource not in self.thresholds:
            raise ValueError(f"Ungültiger Ressourcentyp: {resource}")
        
        self.thresholds[resource] = threshold
    
    def register_action(self, resource: str, action: Callable) -> None:
        """
        Registriert eine Aktion, die bei Überschreitung des Schwellenwerts ausgeführt wird
        
        Args:
            resource (str): Ressourcentyp ('cpu', 'memory', 'disk')
            action (callable): Auszuführende Aktion
            
        Raises:
            ValueError: Wenn der Ressourcentyp ungültig ist
        """
        if resource not in self.actions:
            raise ValueError(f"Ungültiger Ressourcentyp: {resource}")
        
        self.actions[resource].append(action)
    
    def start_monitoring(self) -> None:
        """
        Startet die Überwachung der Systemressourcen
        """
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """
        Stoppt die Überwachung der Systemressourcen
        """
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self) -> None:
        """
        Überwachungsschleife für Systemressourcen
        """
        while self.running:
            # CPU-Auslastung überprüfen
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['cpu']:
                self._execute_actions('cpu', cpu_percent)
            
            # Speicherauslastung überprüfen
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.thresholds['memory']:
                self._execute_actions('memory', memory_percent)
            
            # Festplattenauslastung überprüfen
            disk_percent = psutil.disk_usage('/').percent
            if disk_percent > self.thresholds['disk']:
                self._execute_actions('disk', disk_percent)
            
            time.sleep(5)
    
    def _execute_actions(self, resource: str, value: float) -> None:
        """
        Führt die registrierten Aktionen für eine Ressource aus
        
        Args:
            resource (str): Ressourcentyp
            value (float): Aktueller Wert
        """
        print(f"[ResourceMonitor] {resource.upper()}-Schwellenwert überschritten: {value:.1f}% (Schwellenwert: {self.thresholds[resource]:.1f}%)")
        
        for action in self.actions[resource]:
            try:
                action(resource, value)
            except Exception as e:
                print(f"[ResourceMonitor] Fehler bei Ausführung der Aktion für {resource}: {str(e)}")

class SelfHealingSystem:
    """
    Selbstheilendes System, das alle Resilienz-Komponenten kombiniert
    """
    
    def __init__(self):
        """
        Initialisiert das selbstheilende System
        """
        self.service_monitor = ServiceMonitor()
        self.network_resilience = NetworkResilience()
        self.resource_monitor = ResourceMonitor()
    
    def start(self) -> None:
        """
        Startet alle Überwachungskomponenten
        """
        self.service_monitor.start_monitoring()
        self.resource_monitor.start_monitoring()
        print("[SelfHealingSystem] Selbstheilendes System gestartet")
    
    def stop(self) -> None:
        """
        Stoppt alle Überwachungskomponenten
        """
        self.service_monitor.stop_monitoring()
        self.resource_monitor.stop_monitoring()
        print("[SelfHealingSystem] Selbstheilendes System gestoppt")
    
    def register_service(self, name: str, check_func: Callable, restart_func: Callable, check_interval: int = 30) -> None:
        """
        Registriert einen Dienst zur Überwachung
        
        Args:
            name (str): Name des Dienstes
            check_func (callable): Funktion zur Überprüfung des Dienstes
            restart_func (callable): Funktion zum Neustart des Dienstes
            check_interval (int): Intervall in Sekunden zwischen Überprüfungen
        """
        self.service_monitor.register_service(name, check_func, restart_func, check_interval)
    
    def register_endpoint(self, name: str, primary_endpoint: str, fallback_endpoints: List[str]) -> None:
        """
        Registriert einen Endpunkt mit Fallback-Optionen
        
        Args:
            name (str): Name des Endpunkts
            primary_endpoint (str): Primärer Endpunkt (z.B. "192.168.1.1:8080")
            fallback_endpoints (list): Liste von Fallback-Endpunkten
        """
        self.network_resilience.register_endpoint(name, primary_endpoint, fallback_endpoints)
    
    def get_endpoint(self, name: str) -> str:
        """
        Gibt den aktuellen Endpunkt zurück
        
        Args:
            name (str): Name des Endpunkts
            
        Returns:
            str: Aktueller Endpunkt
        """
        return self.network_resilience.get_endpoint(name)
    
    def check_endpoint(self, name: str) -> bool:
        """
        Überprüft einen Endpunkt und wechselt bei Bedarf zum Fallback
        
        Args:
            name (str): Name des Endpunkts
            
        Returns:
            bool: True, wenn der Endpunkt erreichbar ist, sonst False
        """
        return self.network_resilience.check_endpoint(name)
    
    def set_resource_threshold(self, resource: str, threshold: float) -> None:
        """
        Setzt den Schwellenwert für eine Ressource
        
        Args:
            resource (str): Ressourcentyp ('cpu', 'memory', 'disk')
            threshold (float): Schwellenwert in Prozent
        """
        self.resource_monitor.set_threshold(resource, threshold)
    
    def register_resource_action(self, resource: str, action: Callable) -> None:
        """
        Registriert eine Aktion, die bei Überschreitung des Schwellenwerts ausgeführt wird
        
        Args:
            resource (str): Ressourcentyp ('cpu', 'memory', 'disk')
            action (callable): Auszuführende Aktion
        """
        self.resource_monitor.register_action(resource, action)
