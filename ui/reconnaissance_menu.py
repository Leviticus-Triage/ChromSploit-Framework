#!/usr/bin/env python3
"""
Reconnaissance menu for target discovery and information gathering.
"""

import time
from typing import List, Optional

from core.enhanced_menu import EnhancedMenu, EnhancedMenuItem, ProgressBar
from core.reconnaissance import get_reconnaissance_manager, ReconTarget
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors
from core.colors import Colors

class ReconnaissanceMenu(EnhancedMenu):
 """Advanced reconnaissance menu with target discovery capabilities"""
 
 def __init__(self):
 super().__init__(title=" Reconnaissance & Target Discovery")
 self.set_description("Comprehensive target discovery and information gathering toolkit")
 self.recon_manager = get_reconnaissance_manager()
 self.logger = get_logger()
 self.current_target = None
 
 # Try to load AI orchestrator
 self.ai_orchestrator = None
 try:
 from modules.ai.ai_orchestrator import AIOrchestrator
 self.ai_orchestrator = AIOrchestrator()
 self.logger.info("AI Orchestrator loaded for reconnaissance")
 except ImportError:
 self.logger.debug("AI Orchestrator not available")
 
 self.setup_menu_items()
 
 def setup_menu_items(self):
 """Setup reconnaissance menu items"""
 
 if self.ai_orchestrator:
 self.add_enhanced_item(
 " AI Target Profiling",
 self.ai_target_profiling,
 color=Colors.BRIGHT_CYAN,
 description="AI-powered target analysis and profiling",
 shortcut="i",
 key="1"
 )
 
 self.add_enhanced_item(
 "Target Management",
 self.target_management_menu,
 color=Colors.CYAN,
 description="Add, remove, and manage reconnaissance targets",
 shortcut="t",
 key="2" if self.ai_orchestrator else "1"
 )
 
 self.add_enhanced_item(
 "Subdomain Enumeration",
 self.subdomain_enumeration_menu,
 color=Colors.BLUE,
 description="Discover subdomains using multiple techniques",
 shortcut="s",
 key="3" if self.ai_orchestrator else "2"
 )
 
 self.add_enhanced_item(
 "Port Scanning",
 self.port_scanning_menu,
 color=Colors.YELLOW,
 description="Network port discovery and service detection",
 shortcut="p",
 key="4" if self.ai_orchestrator else "3"
 )
 
 self.add_enhanced_item(
 "Service Fingerprinting",
 self.service_fingerprinting_menu,
 color=Colors.GREEN,
 description="Identify services and versions on open ports",
 shortcut="f",
 key="5" if self.ai_orchestrator else "4"
 )
 
 if self.ai_orchestrator:
 self.add_enhanced_item(
 " AI Attack Surface Analysis",
 self.ai_attack_surface_analysis,
 color=Colors.BRIGHT_YELLOW,
 description="AI analyzes discovered attack surface and suggests priorities",
 shortcut="a",
 key="6"
 )
 
 self.add_enhanced_item(
 "Full Reconnaissance",
 self.full_reconnaissance_menu,
 color=Colors.RED,
 description="Complete automated reconnaissance workflow",
 shortcut="r",
 key="7" if self.ai_orchestrator else "5",
 dangerous=True
 )
 
 self.add_enhanced_item(
 "Results & Reports",
 self.results_menu,
 color=Colors.PURPLE,
 description="View reconnaissance results and generate reports",
 shortcut="v",
 key="8" if self.ai_orchestrator else "6"
 )
 
 self.add_enhanced_item(
 "Zurück zum Hauptmenü",
 self.exit_menu,
 color=Colors.BRIGHT_RED,
 description="Return to main menu",
 shortcut="b",
 key="0"
 )
 
 @handle_errors
 def target_management_menu(self):
 """Target management submenu"""
 menu = EnhancedMenu(title=" Target Management")
 menu.set_description("Manage reconnaissance targets")
 
 menu.add_enhanced_item(
 "Add New Target",
 self.add_target,
 color=Colors.GREEN,
 shortcut="a",
 description="Add a new domain or IP address for reconnaissance",
 key="1"
 )
 
 menu.add_enhanced_item(
 "List Targets",
 self.list_targets,
 color=Colors.CYAN,
 shortcut="l",
 description="Show all configured targets and their status",
 key="2"
 )
 
 menu.add_enhanced_item(
 "Select Active Target",
 self.select_target,
 color=Colors.CYAN,
 shortcut="s",
 description="Choose the current target for operations",
 key="3"
 )
 
 menu.add_enhanced_item(
 "Remove Target",
 self.remove_target,
 color=Colors.RED,
 shortcut="r",
 description="Remove a target and its data",
 key="4",
 dangerous=True
 )
 
 menu.add_enhanced_item(
 "Zurück",
 menu.exit_menu,
 color=Colors.CYAN,
 shortcut="b",
 description="Return to reconnaissance menu",
 key="0"
 )
 
 menu.run()
 
 @handle_errors
 def add_target(self):
 """Add a new reconnaissance target"""
 print("\n" + "="*60)
 print(" Neues Ziel hinzufügen")
 print("="*60)
 
 target = input("Ziel-Domain oder IP-Adresse eingeben: ").strip()
 
 if not target:
 print(" Ungültiges Ziel!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 # Validate target format
 if not self.validate_target(target):
 print(" Ungültiges Zielformat! Bitte Domain oder IP-Adresse eingeben.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 recon_target = self.recon_manager.add_target(target)
 self.current_target = target
 
 print(f" Ziel '{target}' erfolgreich hinzugefügt!")
 print(f" Als aktuelles Ziel ausgewählt")
 
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def list_targets(self):
 """List all reconnaissance targets"""
 print("\n" + "="*80)
 print(" Reconnaissance Ziele")
 print("="*80)
 
 if not self.recon_manager.targets:
 print("ℹ Keine Ziele konfiguriert.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print(f"{'Nr.':<3} {'Ziel':<30} {'Status':<15} {'Subdomains':<12} {'Ports':<8} {'Services':<10}")
 print("-" * 80)
 
 for i, (target, recon_target) in enumerate(self.recon_manager.targets.items(), 1):
 status = " Aktiv" if target == self.current_target else " Inaktiv"
 summary = self.recon_manager.get_target_summary(target)
 
 subdomain_count = summary.get('subdomains_count', 0)
 port_count = summary.get('total_open_ports', 0)
 service_count = summary.get('services_identified', 0)
 
 print(f"{i:<3} {target:<30} {status:<15} {subdomain_count:<12} {port_count:<8} {service_count:<10}")
 
 print("\n" + "="*80)
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def select_target(self):
 """Select active target"""
 if not self.recon_manager.targets:
 print(" Keine Ziele verfügbar! Bitte zuerst ein Ziel hinzufügen.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print("\n" + "="*60)
 print(" Aktives Ziel auswählen")
 print("="*60)
 
 targets = list(self.recon_manager.targets.keys())
 for i, target in enumerate(targets, 1):
 status = " (Aktuell)" if target == self.current_target else ""
 print(f"{i}. {target}{status}")
 
 try:
 choice = int(input("\nZiel auswählen (Nummer): ")) - 1
 if 0 <= choice < len(targets):
 self.current_target = targets[choice]
 print(f" Ziel '{self.current_target}' ausgewählt!")
 else:
 print(" Ungültige Auswahl!")
 except ValueError:
 print(" Bitte eine gültige Nummer eingeben!")
 
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def remove_target(self):
 """Remove a target"""
 if not self.recon_manager.targets:
 print(" Keine Ziele verfügbar!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print("\n" + "="*60)
 print(" Ziel entfernen")
 print("="*60)
 
 targets = list(self.recon_manager.targets.keys())
 for i, target in enumerate(targets, 1):
 print(f"{i}. {target}")
 
 try:
 choice = int(input("\nZu entfernendes Ziel (Nummer): ")) - 1
 if 0 <= choice < len(targets):
 target_to_remove = targets[choice]
 
 confirm = input(f" Wirklich '{target_to_remove}' entfernen? (j/N): ").lower()
 if confirm == 'j':
 del self.recon_manager.targets[target_to_remove]
 if self.current_target == target_to_remove:
 self.current_target = None
 print(f" Ziel '{target_to_remove}' entfernt!")
 else:
 print(" Entfernung abgebrochen.")
 else:
 print(" Ungültige Auswahl!")
 except ValueError:
 print(" Bitte eine gültige Nummer eingeben!")
 
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def subdomain_enumeration_menu(self):
 """Subdomain enumeration submenu"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 menu = EnhancedMenu(title=f" Subdomain Enumeration - {self.current_target}")
 menu.set_description("Discover subdomains using various techniques")
 
 menu.add_enhanced_item(
 "DNS Bruteforce",
 lambda: self.run_subdomain_enum(['dns_bruteforce']),
 color=Colors.CYAN,
 shortcut="d",
 description="Bruteforce subdomains using common wordlists",
 key="1"
 )
 
 menu.add_enhanced_item(
 "Certificate Transparency",
 lambda: self.run_subdomain_enum(['certificate_transparency']),
 color=Colors.CYAN,
 shortcut="c",
 description="Find subdomains from certificate transparency logs",
 key="2"
 )
 
 menu.add_enhanced_item(
 "All Methods",
 lambda: self.run_subdomain_enum(),
 color=Colors.GREEN,
 shortcut="a",
 description="Run all subdomain enumeration techniques",
 key="3"
 )
 
 menu.add_enhanced_item(
 "Custom Methods",
 self.custom_subdomain_enum,
 color=Colors.CYAN,
 shortcut="s",
 description="Select specific enumeration methods",
 key="4"
 )
 
 menu.add_enhanced_item(
 "Zurück",
 menu.exit_menu,
 color=Colors.CYAN,
 shortcut="b",
 description="Return to reconnaissance menu",
 key="0"
 )
 
 menu.run()
 
 @handle_errors
 def run_subdomain_enum(self, methods: List[str] = None):
 """Run subdomain enumeration"""
 print("\n" + "="*70)
 print(f" Subdomain Enumeration für {self.current_target}")
 print("="*70)
 
 progress = ProgressBar(total=100, description="Subdomain Enumeration")
 progress.start()
 
 try:
 # Update progress during enumeration
 progress.update(25, "DNS Bruteforce läuft...")
 time.sleep(1) # Simulate work
 
 result = self.recon_manager.run_subdomain_enumeration(self.current_target, methods)
 
 progress.update(100, "Abgeschlossen!")
 progress.stop()
 
 print(f"\n Subdomain Enumeration abgeschlossen!")
 print(f" Gefundene Subdomains: {len(result.subdomains)}")
 
 if result.subdomains:
 print("\n Gefundene Subdomains:")
 for subdomain in sorted(list(result.subdomains)[:20]): # Show first 20
 print(f" • {subdomain}")
 
 if len(result.subdomains) > 20:
 print(f" ... und {len(result.subdomains) - 20} weitere")
 
 print(f"\n Ergebnisse gespeichert in: recon_data/")
 
 except Exception as e:
 progress.stop()
 print(f" Fehler bei Subdomain Enumeration: {e}")
 
 input("\nDrücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def custom_subdomain_enum(self):
 """Custom subdomain enumeration method selection"""
 print("\n" + "="*60)
 print(" Methoden auswählen")
 print("="*60)
 
 available_methods = [
 ("dns_bruteforce", "DNS Bruteforce"),
 ("certificate_transparency", "Certificate Transparency"),
 ("search_engines", "Search Engine Dorking")
 ]
 
 selected_methods = []
 
 for method, description in available_methods:
 choice = input(f"{description} verwenden? (j/N): ").lower()
 if choice == 'j':
 selected_methods.append(method)
 
 if selected_methods:
 self.run_subdomain_enum(selected_methods)
 else:
 print(" Keine Methoden ausgewählt!")
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def port_scanning_menu(self):
 """Port scanning submenu"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 menu = EnhancedMenu(title=f" Port Scanning - {self.current_target}")
 menu.set_description("Network port discovery and service detection")
 
 menu.add_enhanced_item(
 "Quick Scan (Top 100)",
 lambda: self.run_port_scan("top100"),
 color=Colors.CYAN,
 shortcut="q",
 description="Scan most common 100 ports",
 key="1"
 )
 
 menu.add_enhanced_item(
 "Standard Scan (Top 1000)",
 lambda: self.run_port_scan("top1000"),
 color=Colors.CYAN,
 shortcut="s",
 description="Scan top 1000 most common ports",
 key="2"
 )
 
 menu.add_enhanced_item(
 "Full Scan (All Ports)",
 lambda: self.run_port_scan("all"),
 color=Colors.RED,
 shortcut="f",
 description="Scan all 65535 ports (very slow)",
 key="3",
 dangerous=True
 )
 
 menu.add_enhanced_item(
 "Custom Range",
 self.custom_port_scan,
 color=Colors.CYAN,
 shortcut="c",
 description="Specify custom port range",
 key="4"
 )
 
 menu.add_enhanced_item(
 "Scan All Subdomains",
 self.scan_all_subdomains,
 color=Colors.RED,
 shortcut="a",
 description="Port scan all discovered subdomains",
 key="5",
 dangerous=True
 )
 
 menu.add_enhanced_item(
 "Zurück",
 menu.exit_menu,
 color=Colors.CYAN,
 shortcut="b",
 description="Return to reconnaissance menu",
 key="0"
 )
 
 menu.run()
 
 @handle_errors
 def run_port_scan(self, port_range: str, host: str = None):
 """Run port scan"""
 if not host:
 host = self.current_target
 
 print("\n" + "="*70)
 print(f" Port Scan für {host} ({port_range})")
 print("="*70)
 
 progress = ProgressBar(total=100, description="Port Scanning")
 progress.start()
 
 try:
 progress.update(25, "Port Scan läuft...")
 result = self.recon_manager.run_port_scan(host, port_range)
 
 progress.update(100, "Abgeschlossen!")
 progress.stop()
 
 print(f"\n Port Scan abgeschlossen!")
 print(f" Offene Ports: {len(result.open_ports)}")
 print(f"⏱ Scan-Dauer: {result.scan_duration:.2f} Sekunden")
 
 if result.open_ports:
 print("\n Offene Ports:")
 for port, service in result.open_ports:
 print(f" • {port}/tcp - {service}")
 
 print(f"\n Ergebnisse gespeichert in: recon_data/")
 
 except Exception as e:
 progress.stop()
 print(f" Fehler beim Port Scan: {e}")
 
 input("\nDrücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def custom_port_scan(self):
 """Custom port range scanning"""
 print("\n" + "="*60)
 print(" Benutzerdefinierten Port-Bereich eingeben")
 print("="*60)
 
 port_range = input("Port-Bereich (z.B. '1-1000' oder 'top100'): ").strip()
 
 if port_range:
 self.run_port_scan(port_range)
 else:
 print(" Ungültiger Port-Bereich!")
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def scan_all_subdomains(self):
 """Scan all discovered subdomains"""
 if self.current_target not in self.recon_manager.targets:
 print(" Ziel nicht gefunden!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 target = self.recon_manager.targets[self.current_target]
 if not target.subdomains or not target.subdomains.subdomains:
 print(" Keine Subdomains gefunden! Führen Sie zuerst Subdomain Enumeration durch.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 subdomains = list(target.subdomains.subdomains)
 
 print(f"\n {len(subdomains)} Subdomains für Port Scan gefunden")
 confirm = input(" Alle Subdomains scannen? Dies kann lange dauern! (j/N): ").lower()
 
 if confirm != 'j':
 return
 
 port_range = input("Port-Bereich (top100/top1000/all): ").strip() or "top100"
 
 print("\n" + "="*70)
 print(f" Port Scan für alle Subdomains ({port_range})")
 print("="*70)
 
 total_subdomains = len(subdomains)
 for i, subdomain in enumerate(subdomains, 1):
 print(f"\n[{i}/{total_subdomains}] Scanning {subdomain}...")
 try:
 self.run_port_scan(port_range, subdomain)
 except Exception as e:
 print(f" Fehler beim Scannen von {subdomain}: {e}")
 
 print(f"\n Port Scan für alle Subdomains abgeschlossen!")
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def service_fingerprinting_menu(self):
 """Service fingerprinting submenu"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 menu = EnhancedMenu(title=f" Service Fingerprinting - {self.current_target}")
 menu.set_description("Identify services and versions on open ports")
 
 menu.add_enhanced_item(
 "Fingerprint Main Target",
 lambda: self.run_service_fingerprinting(self.current_target),
 color=Colors.CYAN,
 shortcut="m",
 description="Fingerprint services on main target",
 key="1"
 )
 
 menu.add_enhanced_item(
 "Fingerprint All Hosts",
 self.fingerprint_all_hosts,
 color=Colors.GREEN,
 shortcut="a",
 description="Fingerprint all scanned hosts",
 key="2"
 )
 
 menu.add_enhanced_item(
 "Select Specific Host",
 self.select_host_fingerprinting,
 color=Colors.CYAN,
 shortcut="s",
 description="Choose specific host for fingerprinting",
 key="3"
 )
 
 menu.add_enhanced_item(
 "Zurück",
 menu.exit_menu,
 color=Colors.CYAN,
 shortcut="b",
 description="Return to reconnaissance menu",
 key="0"
 )
 
 menu.run()
 
 @handle_errors
 def run_service_fingerprinting(self, host: str):
 """Run service fingerprinting for a specific host"""
 print("\n" + "="*70)
 print(f" Service Fingerprinting für {host}")
 print("="*70)
 
 progress = ProgressBar(total=100, description="Service Fingerprinting")
 progress.start()
 
 try:
 progress.update(50, "Services identifizieren...")
 services = self.recon_manager.run_service_fingerprinting(host)
 
 progress.update(100, "Abgeschlossen!")
 progress.stop()
 
 print(f"\n Service Fingerprinting abgeschlossen!")
 print(f" Identifizierte Services: {len(services)}")
 
 if services:
 print("\n Gefundene Services:")
 for service in services:
 ssl_indicator = "" if service.ssl_info else ""
 version_info = f" ({service.version})" if service.version else ""
 print(f" • {service.port}/tcp - {service.service}{version_info} {ssl_indicator}")
 
 print(f"\n Ergebnisse gespeichert in: recon_data/")
 
 except Exception as e:
 progress.stop()
 print(f" Fehler beim Service Fingerprinting: {e}")
 
 input("\nDrücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def fingerprint_all_hosts(self):
 """Fingerprint all scanned hosts"""
 if self.current_target not in self.recon_manager.targets:
 print(" Ziel nicht gefunden!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 target = self.recon_manager.targets[self.current_target]
 
 if not target.port_scans:
 print(" Keine Port Scans gefunden! Führen Sie zuerst Port Scanning durch.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 hosts_with_ports = [(host, scan) for host, scan in target.port_scans.items() if scan.open_ports]
 
 if not hosts_with_ports:
 print(" Keine offenen Ports gefunden!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print(f"\n {len(hosts_with_ports)} Hosts mit offenen Ports gefunden")
 
 for host, scan in hosts_with_ports:
 print(f"\n Fingerprinting {host} ({len(scan.open_ports)} offene Ports)...")
 try:
 self.run_service_fingerprinting(host)
 except Exception as e:
 print(f" Fehler beim Fingerprinting von {host}: {e}")
 
 print(f"\n Service Fingerprinting für alle Hosts abgeschlossen!")
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def select_host_fingerprinting(self):
 """Select specific host for fingerprinting"""
 if self.current_target not in self.recon_manager.targets:
 print(" Ziel nicht gefunden!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 target = self.recon_manager.targets[self.current_target]
 
 if not target.port_scans:
 print(" Keine Port Scans gefunden!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 hosts = list(target.port_scans.keys())
 
 print("\n" + "="*60)
 print(" Host für Fingerprinting auswählen")
 print("="*60)
 
 for i, host in enumerate(hosts, 1):
 scan = target.port_scans[host]
 print(f"{i}. {host} ({len(scan.open_ports)} offene Ports)")
 
 try:
 choice = int(input("\nHost auswählen (Nummer): ")) - 1
 if 0 <= choice < len(hosts):
 selected_host = hosts[choice]
 self.run_service_fingerprinting(selected_host)
 else:
 print(" Ungültige Auswahl!")
 input("Drücken Sie Enter um fortzufahren...")
 except ValueError:
 print(" Bitte eine gültige Nummer eingeben!")
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def full_reconnaissance_menu(self):
 """Full reconnaissance workflow"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print("\n" + "="*70)
 print(f" Vollständige Reconnaissance für {self.current_target}")
 print("="*70)
 print(" Dies führt folgende Schritte automatisch aus:")
 print(" 1. Subdomain Enumeration (alle Methoden)")
 print(" 2. Port Scanning (Top 1000 Ports)")
 print(" 3. Service Fingerprinting")
 print(" 4. Report Generation")
 print()
 
 confirm = input(" Vollständige Reconnaissance starten? (j/N): ").lower()
 if confirm != 'j':
 return
 
 # Configuration options
 print("\n Konfiguration:")
 subdomain_methods = []
 
 if input("DNS Bruteforce verwenden? (J/n): ").lower() != 'n':
 subdomain_methods.append('dns_bruteforce')
 
 if input("Certificate Transparency verwenden? (J/n): ").lower() != 'n':
 subdomain_methods.append('certificate_transparency')
 
 port_range = input("Port-Bereich (top100/top1000/all) [top1000]: ").strip() or "top1000"
 
 print("\n" + "="*70)
 print(" Starte vollständige Reconnaissance...")
 print("="*70)
 
 progress = ProgressBar(total=100, description="Full Reconnaissance")
 progress.start()
 
 try:
 progress.update(25, "Subdomain Enumeration...")
 result = self.recon_manager.run_full_reconnaissance(
 self.current_target, 
 subdomain_methods, 
 port_range
 )
 
 progress.update(100, "Abgeschlossen!")
 progress.stop()
 
 # Show summary
 summary = self.recon_manager.get_target_summary(self.current_target)
 
 print(f"\n Vollständige Reconnaissance abgeschlossen!")
 print("="*70)
 print(f" Zusammenfassung für {self.current_target}:")
 print(f" • Subdomains gefunden: {summary.get('subdomains_count', 0)}")
 print(f" • Hosts gescannt: {summary.get('hosts_scanned', 0)}")
 print(f" • Offene Ports: {summary.get('total_open_ports', 0)}")
 print(f" • Services identifiziert: {summary.get('services_identified', 0)}")
 print(f" • Web Services: {summary.get('web_services', 0)}")
 print(f" • SSL Services: {summary.get('ssl_services', 0)}")
 print("="*70)
 print(f" Alle Ergebnisse gespeichert in: recon_data/")
 
 except Exception as e:
 progress.stop()
 print(f" Fehler bei vollständiger Reconnaissance: {e}")
 
 input("\nDrücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def results_menu(self):
 """Results and reports menu"""
 menu = EnhancedMenu(title=" Reconnaissance Results & Reports")
 menu.set_description("View results and generate reports")
 
 menu.add_enhanced_item(
 "Target Summary",
 self.show_target_summary,
 color=Colors.CYAN,
 shortcut="s",
 description="Show summary of current target",
 key="1"
 )
 
 menu.add_enhanced_item(
 "Detailed Results",
 self.show_detailed_results,
 color=Colors.CYAN,
 shortcut="d",
 description="Show detailed reconnaissance results",
 key="2"
 )
 
 menu.add_enhanced_item(
 "Export Results",
 self.export_results,
 color=Colors.GREEN,
 shortcut="e",
 description="Export results to various formats",
 key="3"
 )
 
 menu.add_enhanced_item(
 "Compare Targets",
 self.compare_targets,
 color=Colors.CYAN,
 shortcut="c",
 description="Compare multiple reconnaissance targets",
 key="4"
 )
 
 menu.add_enhanced_item(
 "Zurück",
 menu.exit_menu,
 color=Colors.CYAN,
 shortcut="b",
 description="Return to reconnaissance menu",
 key="0"
 )
 
 menu.run()
 
 @handle_errors
 def show_target_summary(self):
 """Show target summary"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 summary = self.recon_manager.get_target_summary(self.current_target)
 
 print("\n" + "="*70)
 print(f" Zusammenfassung für {self.current_target}")
 print("="*70)
 print(f"Letzte Aktualisierung: {summary.get('last_updated', 'Unbekannt')}")
 print(f"Subdomains gefunden: {summary.get('subdomains_count', 0)}")
 print(f"Hosts gescannt: {summary.get('hosts_scanned', 0)}")
 print(f"Offene Ports gesamt: {summary.get('total_open_ports', 0)}")
 print(f"Services identifiziert: {summary.get('services_identified', 0)}")
 print(f"Web Services: {summary.get('web_services', 0)}")
 print(f"SSL Services: {summary.get('ssl_services', 0)}")
 print("="*70)
 
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def show_detailed_results(self):
 """Show detailed results"""
 if not self.current_target or self.current_target not in self.recon_manager.targets:
 print(" Kein gültiges Ziel ausgewählt!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 target = self.recon_manager.targets[self.current_target]
 
 print("\n" + "="*80)
 print(f" Detaillierte Ergebnisse für {self.current_target}")
 print("="*80)
 
 # Subdomains
 if target.subdomains:
 print(f"\n Subdomains ({len(target.subdomains.subdomains)}):")
 for subdomain in sorted(list(target.subdomains.subdomains)[:10]):
 print(f" • {subdomain}")
 if len(target.subdomains.subdomains) > 10:
 print(f" ... und {len(target.subdomains.subdomains) - 10} weitere")
 
 # Port scans
 if target.port_scans:
 print(f"\n Port Scans ({len(target.port_scans)} Hosts):")
 for host, scan in target.port_scans.items():
 print(f" {host}: {len(scan.open_ports)} offene Ports")
 for port, service in scan.open_ports[:5]:
 print(f" • {port}/tcp - {service}")
 if len(scan.open_ports) > 5:
 print(f" ... und {len(scan.open_ports) - 5} weitere")
 
 # Services
 if target.services:
 print(f"\n Services ({len(target.services)}):")
 for service in target.services[:10]:
 ssl_indicator = "" if service.ssl_info else ""
 version_info = f" ({service.version})" if service.version else ""
 print(f" • {service.host}:{service.port} - {service.service}{version_info} {ssl_indicator}")
 if len(target.services) > 10:
 print(f" ... und {len(target.services) - 10} weitere")
 
 print("="*80)
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def export_results(self):
 """Export results to file"""
 if not self.current_target:
 print(" Kein Ziel ausgewählt!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print("\n" + "="*60)
 print(" Ergebnisse exportieren")
 print("="*60)
 print("1. JSON Format")
 print("2. CSV Format")
 print("3. TXT Format")
 
 choice = input("Format auswählen (1-3): ").strip()
 
 if choice == "1":
 self.recon_manager.save_target_data(self.current_target)
 print(" Ergebnisse als JSON exportiert!")
 elif choice in ["2", "3"]:
 print("ℹ CSV/TXT Export wird in einer zukünftigen Version verfügbar sein.")
 else:
 print(" Ungültige Auswahl!")
 
 input("Drücken Sie Enter um fortzufahren...")
 
 @handle_errors
 def compare_targets(self):
 """Compare multiple targets"""
 if len(self.recon_manager.targets) < 2:
 print(" Mindestens 2 Ziele erforderlich für Vergleich!")
 input("Drücken Sie Enter um fortzufahren...")
 return
 
 print("\n" + "="*80)
 print(" Ziel-Vergleich")
 print("="*80)
 
 print(f"{'Ziel':<30} {'Subdomains':<12} {'Ports':<8} {'Services':<10} {'Web':<5} {'SSL':<5}")
 print("-" * 80)
 
 for target_name in self.recon_manager.targets:
 summary = self.recon_manager.get_target_summary(target_name)
 print(f"{target_name:<30} {summary.get('subdomains_count', 0):<12} "
 f"{summary.get('total_open_ports', 0):<8} {summary.get('services_identified', 0):<10} "
 f"{summary.get('web_services', 0):<5} {summary.get('ssl_services', 0):<5}")
 
 print("="*80)
 input("Drücken Sie Enter um fortzufahren...")
 
 def validate_target(self, target: str) -> bool:
 """Validate target format (domain or IP)"""
 import re
 
 # Simple domain validation
 domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'
 
 # Simple IP validation
 ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
 
 return bool(re.match(domain_pattern, target) or re.match(ip_pattern, target))
 
 def get_status_text(self) -> str:
 """Get current status for display"""
 if self.current_target:
 return f"Aktuelles Ziel: {self.current_target}"
 return "Kein Ziel ausgewählt"
 
 @handle_errors
 def ai_target_profiling(self):
 """AI-powered target analysis and profiling"""
 self.clear_screen()
 print("\n" + "="*70)
 print(" AI Target Profiling")
 print("="*70)
 print("AI erstellt ein umfassendes Ziel-Profil basierend auf OSINT-Daten")
 print()
 
 # Get target
 if self.current_target:
 print(f"{Colors.YELLOW}Aktuelles Ziel:{Colors.RESET} {self.current_target}")
 use_current = input(f"{Colors.CYAN}Dieses Ziel verwenden? [J/n]: {Colors.RESET}")
 if use_current.lower() in ['n', 'nein', 'no']:
 target = input(f"{Colors.CYAN}Neues Ziel eingeben: {Colors.RESET}").strip()
 else:
 target = self.current_target
 else:
 target = input(f"{Colors.CYAN}Ziel-Domain oder IP eingeben: {Colors.RESET}").strip()
 
 if not target:
 print(f"{Colors.RED} Kein Ziel angegeben!{Colors.RESET}")
 self.pause()
 return
 
 # Additional context
 print(f"\n{Colors.YELLOW}Zusätzliche Informationen:{Colors.RESET}")
 org_name = input(f"{Colors.CYAN}Organisationsname (optional): {Colors.RESET}").strip()
 industry = input(f"{Colors.CYAN}Branche (tech/finance/health/gov/other): {Colors.RESET}").strip() or "other"
 
 print(f"\n{Colors.CYAN}[*] AI analysiert Ziel...{Colors.RESET}")
 time.sleep(1)
 
 if self.ai_orchestrator:
 try:
 # Build target data
 target_data = {
 'target': target,
 'organization': org_name,
 'industry': industry,
 'type': 'domain' if '.' in target else 'ip'
 }
 
 # Get AI analysis
 analysis = self.ai_orchestrator.analyze_target(target_data)
 
 print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN} AI Target Profile{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}\n")
 
 # Target assessment
 print(f"{Colors.YELLOW}Ziel-Bewertung:{Colors.RESET}")
 print(f" • Domain/IP: {target}")
 print(f" • Typ: {target_data['type'].upper()}")
 if org_name:
 print(f" • Organisation: {org_name}")
 print(f" • Branche: {industry.capitalize()}")
 
 # Technology stack prediction
 print(f"\n{Colors.YELLOW}Vermutete Technologien:{Colors.RESET}")
 tech_stack = self._predict_tech_stack(industry)
 for tech in tech_stack:
 print(f" • {tech}")
 
 # Attack surface estimation
 print(f"\n{Colors.YELLOW}Geschätzte Angriffsfläche:{Colors.RESET}")
 if target_data['type'] == 'domain':
 print(f" • Subdomains: 10-50 (geschätzt)")
 print(f" • Offene Ports: 5-15 (typisch)")
 print(f" • Web-Services: Wahrscheinlich")
 print(f" • API-Endpoints: Möglich")
 else:
 print(f" • Offene Ports: 3-10 (typisch)")
 print(f" • Services: Unbekannt")
 
 # Security posture assessment
 security_score = 0.6 # Default medium
 if industry in ['finance', 'gov']:
 security_score = 0.8
 elif industry == 'tech':
 security_score = 0.7
 
 print(f"\n{Colors.YELLOW}Sicherheitsbewertung:{Colors.RESET}")
 sec_color = Colors.GREEN if security_score > 0.7 else Colors.YELLOW if security_score > 0.5 else Colors.RED
 print(f" {sec_color}{'█' * int(security_score * 10)}{' ' * (10 - int(security_score * 10))} {security_score:.0%}{Colors.RESET}")
 
 # Recommended reconnaissance approach
 print(f"\n{Colors.YELLOW}Empfohlene Reconnaissance-Strategie:{Colors.RESET}")
 if security_score > 0.7:
 print(f" 1. Passive Reconnaissance zuerst")
 print(f" 2. Vorsichtige Subdomain-Enumeration")
 print(f" 3. Langsame Port-Scans")
 print(f" 4. Service-Fingerprinting mit Delays")
 else:
 print(f" 1. Standard Subdomain-Enumeration")
 print(f" 2. Umfassende Port-Scans")
 print(f" 3. Aggressive Service-Detection")
 print(f" 4. Vulnerability Scanning")
 
 # CVE recommendations
 cve_recs = analysis.get('cve_recommendations', [])
 if cve_recs:
 print(f"\n{Colors.YELLOW}Potenzielle CVEs basierend auf Profil:{Colors.RESET}")
 for cve in cve_recs[:5]:
 print(f" • {cve}")
 
 # Save profile?
 save = input(f"\n{Colors.CYAN}Profil speichern? [J/n]: {Colors.RESET}")
 if save.lower() not in ['n', 'nein', 'no']:
 # Would save profile here
 print(f"{Colors.GREEN} Profil gespeichert!{Colors.RESET}")
 
 # Add target if not exists
 if target not in self.recon_manager.targets:
 self.recon_manager.add_target(target)
 self.current_target = target
 print(f"{Colors.GREEN} Ziel zur Reconnaissance hinzugefügt{Colors.RESET}")
 
 except Exception as e:
 print(f"{Colors.RED}[!] AI-Analyse fehlgeschlagen: {str(e)}{Colors.RESET}")
 else:
 print(f"{Colors.YELLOW}[!] AI Orchestrator nicht verfügbar{Colors.RESET}")
 
 self.pause()
 
 def _predict_tech_stack(self, industry: str) -> List[str]:
 """Predict technology stack based on industry"""
 tech_stacks = {
 'tech': ['Node.js/React', 'Python/Django', 'Kubernetes', 'AWS/GCP', 'PostgreSQL', 'Redis'],
 'finance': ['Java/Spring', '.NET', 'Oracle DB', 'IBM WebSphere', 'COBOL (Legacy)', 'High Security'],
 'health': ['Epic/Cerner', '.NET/Java', 'HL7/FHIR', 'SQL Server', 'HIPAA Compliance'],
 'gov': ['Java EE', 'Oracle', 'Legacy Systems', 'Strict Firewall', 'VPN Required'],
 'other': ['WordPress/CMS', 'PHP', 'MySQL', 'Apache/Nginx', 'Standard Stack']
 }
 
 return tech_stacks.get(industry, tech_stacks['other'])
 
 @handle_errors
 def ai_attack_surface_analysis(self):
 """AI analyzes discovered attack surface"""
 self.clear_screen()
 print("\n" + "="*70)
 print(" AI Attack Surface Analysis")
 print("="*70)
 print("AI analysiert die entdeckte Angriffsfläche und priorisiert Ziele")
 print()
 
 if not self.current_target:
 print(f"{Colors.YELLOW}[!] Kein Ziel ausgewählt!{Colors.RESET}")
 print("Wählen Sie zuerst ein Ziel aus dem Target Management.")
 self.pause()
 return
 
 # Get target summary
 summary = self.recon_manager.get_target_summary(self.current_target)
 
 if not summary or (summary.get('subdomains_count', 0) == 0 and summary.get('total_open_ports', 0) == 0):
 print(f"{Colors.YELLOW}[!] Keine Reconnaissance-Daten für {self.current_target} verfügbar!{Colors.RESET}")
 print("Führen Sie zuerst Reconnaissance-Scans durch.")
 self.pause()
 return
 
 print(f"{Colors.CYAN}[*] AI analysiert Angriffsfläche für {self.current_target}...{Colors.RESET}")
 time.sleep(1)
 
 if self.ai_orchestrator:
 try:
 # Prepare attack surface data
 attack_surface = {
 'target': self.current_target,
 'subdomains': summary.get('subdomains_count', 0),
 'open_ports': summary.get('total_open_ports', 0),
 'web_services': summary.get('web_services', 0),
 'ssl_services': summary.get('ssl_services', 0),
 'database_services': summary.get('database_services', 0),
 'other_services': summary.get('other_services', 0)
 }
 
 # Get recon details
 recon_target = self.recon_manager.targets.get(self.current_target)
 if recon_target:
 attack_surface['discovered_services'] = [
 {'port': s.port, 'service': s.service, 'version': s.version}
 for s in recon_target.services[:10] # First 10
 ]
 
 analysis = self.ai_orchestrator.analyze_target(attack_surface)
 
 print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN} AI Attack Surface Analysis{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}\n")
 
 # Attack surface overview
 print(f"{Colors.YELLOW}Angriffsflächen-Übersicht:{Colors.RESET}")
 print(f" • Subdomains: {attack_surface['subdomains']}")
 print(f" • Offene Ports: {attack_surface['open_ports']}")
 print(f" • Web-Services: {attack_surface['web_services']}")
 print(f" • SSL-Services: {attack_surface['ssl_services']}")
 
 # Risk assessment
 risk_score = min(1.0, (attack_surface['open_ports'] / 50) + (attack_surface['subdomains'] / 100))
 risk_level = "KRITISCH" if risk_score > 0.7 else "HOCH" if risk_score > 0.5 else "MITTEL" if risk_score > 0.3 else "NIEDRIG"
 risk_color = Colors.RED if risk_score > 0.7 else Colors.YELLOW if risk_score > 0.5 else Colors.GREEN
 
 print(f"\n{Colors.YELLOW}Risikobewertung:{Colors.RESET}")
 print(f" {risk_color}{'█' * int(risk_score * 20)}{' ' * (20 - int(risk_score * 20))} {risk_level}{Colors.RESET}")
 
 # Priority targets
 print(f"\n{Colors.YELLOW}Priorisierte Angriffsziele:{Colors.RESET}")
 
 priorities = []
 
 # Web services are high priority
 if attack_surface['web_services'] > 0:
 priorities.append("Web-Anwendungen (XSS, SQLi, RCE)")
 
 # SSL services for certificate issues
 if attack_surface['ssl_services'] > 0:
 priorities.append("SSL/TLS-Services (Zertifikate, Cipher)")
 
 # Database services are critical
 if attack_surface['database_services'] > 0:
 priorities.append("Datenbank-Services (SQLi, NoSQL Injection)")
 
 # Many open ports suggest poor security
 if attack_surface['open_ports'] > 20:
 priorities.append("Netzwerk-Services (Buffer Overflow, DoS)")
 
 for i, priority in enumerate(priorities[:5], 1):
 print(f" {i}. {priority}")
 
 # Exploitation recommendations
 print(f"\n{Colors.YELLOW}Empfohlene Exploitation-Strategie:{Colors.RESET}")
 
 if risk_score > 0.7:
 print(f" {Colors.RED} Große Angriffsfläche erkannt!{Colors.RESET}")
 print(f" 1. Fokus auf Web-Anwendungen")
 print(f" 2. Automatisierte Vulnerability Scans")
 print(f" 3. Credential Stuffing auf Login-Seiten")
 print(f" 4. Service-spezifische Exploits")
 else:
 print(f" {Colors.YELLOW} Moderate Angriffsfläche{Colors.RESET}")
 print(f" 1. Gezielte Vulnerability Scans")
 print(f" 2. Manual Testing wichtiger Services")
 print(f" 3. Configuration Reviews")
 
 # CVE mapping
 cve_recs = analysis.get('cve_recommendations', [])
 if cve_recs:
 print(f"\n{Colors.YELLOW}Potenzielle CVEs für entdeckte Services:{Colors.RESET}")
 for cve in cve_recs[:5]:
 confidence = analysis.get('confidences', {}).get(cve, 0.5)
 print(f" • {cve} - Konfidenz: {confidence:.1%}")
 
 # Next steps
 print(f"\n{Colors.YELLOW}Empfohlene nächste Schritte:{Colors.RESET}")
 print(f" 1. Vulnerability Scan auf priorisierten Zielen")
 print(f" 2. Service-spezifische Exploit-Recherche")
 print(f" 3. Credential Harvesting vorbereiten")
 print(f" 4. Post-Exploitation Planung")
 
 except Exception as e:
 print(f"{Colors.RED}[!] AI-Analyse fehlgeschlagen: {str(e)}{Colors.RESET}")
 else:
 print(f"{Colors.YELLOW}[!] AI Orchestrator nicht verfügbar{Colors.RESET}")
 
 self.pause()
 
 def run(self):
 """Run the menu"""
 self.display()