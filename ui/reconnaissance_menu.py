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
        super().__init__(
            title="🔍 Reconnaissance & Target Discovery",
            description="Comprehensive target discovery and information gathering toolkit"
        )
        self.recon_manager = get_reconnaissance_manager()
        self.logger = get_logger()
        self.current_target = None
        
        self.setup_menu_items()
    
    def setup_menu_items(self):
        """Setup reconnaissance menu items"""
        self.add_enhanced_item(
            "Target Management",
            self.target_management_menu,
            color=Colors.CYAN,
            description="Add, remove, and manage reconnaissance targets",
            shortcut="t",
            key="1"
        )
        
        self.add_enhanced_item(
            "Subdomain Enumeration",
            self.subdomain_enumeration_menu,
            color=Colors.BLUE,
            description="Discover subdomains using multiple techniques",
            shortcut="s",
            key="2"
        )
        
        self.add_enhanced_item(
            "Port Scanning",
            self.port_scanning_menu,
            color=Colors.YELLOW,
            description="Network port discovery and service detection",
            shortcut="p",
            key="3"
        )
        
        self.add_enhanced_item(
            "Service Fingerprinting",
            self.service_fingerprinting_menu,
            color=Colors.GREEN,
            description="Identify services and versions on open ports",
            shortcut="f",
            key="4"
        )
        
        self.add_enhanced_item(
            "Full Reconnaissance",
            self.full_reconnaissance_menu,
            color=Colors.RED,
            description="Complete automated reconnaissance workflow",
            shortcut="r",
            key="5",
            dangerous=True
        )
        
        self.add_enhanced_item(
            "Results & Reports",
            self.results_menu,
            color=Colors.PURPLE,
            description="View reconnaissance results and generate reports",
            shortcut="v",
            key="6"
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
        menu = EnhancedMenu(
            title="🎯 Target Management",
            description="Manage reconnaissance targets"
        )
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="1",
            title="Add New Target",
            description="Add a new domain or IP address for reconnaissance",
            action=self.add_target,
            shortcut="a"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="2",
            title="List Targets",
            description="Show all configured targets and their status",
            action=self.list_targets,
            shortcut="l"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="3",
            title="Select Active Target",
            description="Choose the current target for operations",
            action=self.select_target,
            shortcut="s"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="4",
            title="Remove Target",
            description="Remove a target and its data",
            action=self.remove_target,
            shortcut="r",
            dangerous=True
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="0",
            title="Zurück",
            description="Return to reconnaissance menu",
            action=menu.exit_menu,
            shortcut="b"
        ))
        
        menu.run()
    
    @handle_errors
    def add_target(self):
        """Add a new reconnaissance target"""
        print("\n" + "="*60)
        print("📍 Neues Ziel hinzufügen")
        print("="*60)
        
        target = input("Ziel-Domain oder IP-Adresse eingeben: ").strip()
        
        if not target:
            print("❌ Ungültiges Ziel!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        # Validate target format
        if not self.validate_target(target):
            print("❌ Ungültiges Zielformat! Bitte Domain oder IP-Adresse eingeben.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        recon_target = self.recon_manager.add_target(target)
        self.current_target = target
        
        print(f"✅ Ziel '{target}' erfolgreich hinzugefügt!")
        print(f"📋 Als aktuelles Ziel ausgewählt")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def list_targets(self):
        """List all reconnaissance targets"""
        print("\n" + "="*80)
        print("📋 Reconnaissance Ziele")
        print("="*80)
        
        if not self.recon_manager.targets:
            print("ℹ️  Keine Ziele konfiguriert.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print(f"{'Nr.':<3} {'Ziel':<30} {'Status':<15} {'Subdomains':<12} {'Ports':<8} {'Services':<10}")
        print("-" * 80)
        
        for i, (target, recon_target) in enumerate(self.recon_manager.targets.items(), 1):
            status = "🎯 Aktiv" if target == self.current_target else "⚫ Inaktiv"
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
            print("❌ Keine Ziele verfügbar! Bitte zuerst ein Ziel hinzufügen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print("🎯 Aktives Ziel auswählen")
        print("="*60)
        
        targets = list(self.recon_manager.targets.keys())
        for i, target in enumerate(targets, 1):
            status = " (Aktuell)" if target == self.current_target else ""
            print(f"{i}. {target}{status}")
        
        try:
            choice = int(input("\nZiel auswählen (Nummer): ")) - 1
            if 0 <= choice < len(targets):
                self.current_target = targets[choice]
                print(f"✅ Ziel '{self.current_target}' ausgewählt!")
            else:
                print("❌ Ungültige Auswahl!")
        except ValueError:
            print("❌ Bitte eine gültige Nummer eingeben!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def remove_target(self):
        """Remove a target"""
        if not self.recon_manager.targets:
            print("❌ Keine Ziele verfügbar!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print("🗑️  Ziel entfernen")
        print("="*60)
        
        targets = list(self.recon_manager.targets.keys())
        for i, target in enumerate(targets, 1):
            print(f"{i}. {target}")
        
        try:
            choice = int(input("\nZu entfernendes Ziel (Nummer): ")) - 1
            if 0 <= choice < len(targets):
                target_to_remove = targets[choice]
                
                confirm = input(f"❗ Wirklich '{target_to_remove}' entfernen? (j/N): ").lower()
                if confirm == 'j':
                    del self.recon_manager.targets[target_to_remove]
                    if self.current_target == target_to_remove:
                        self.current_target = None
                    print(f"✅ Ziel '{target_to_remove}' entfernt!")
                else:
                    print("❌ Entfernung abgebrochen.")
            else:
                print("❌ Ungültige Auswahl!")
        except ValueError:
            print("❌ Bitte eine gültige Nummer eingeben!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def subdomain_enumeration_menu(self):
        """Subdomain enumeration submenu"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title=f"🔍 Subdomain Enumeration - {self.current_target}",
            description="Discover subdomains using various techniques"
        )
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="1",
            title="DNS Bruteforce",
            description="Bruteforce subdomains using common wordlists",
            action=lambda: self.run_subdomain_enum(['dns_bruteforce']),
            shortcut="d"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="2",
            title="Certificate Transparency",
            description="Find subdomains from certificate transparency logs",
            action=lambda: self.run_subdomain_enum(['certificate_transparency']),
            shortcut="c"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="3",
            title="All Methods",
            description="Run all subdomain enumeration techniques",
            action=lambda: self.run_subdomain_enum(),
            shortcut="a"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="4",
            title="Custom Methods",
            description="Select specific enumeration methods",
            action=self.custom_subdomain_enum,
            shortcut="s"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="0",
            title="Zurück",
            description="Return to reconnaissance menu",
            action=menu.exit_menu,
            shortcut="b"
        ))
        
        menu.run()
    
    @handle_errors
    def run_subdomain_enum(self, methods: List[str] = None):
        """Run subdomain enumeration"""
        print("\n" + "="*70)
        print(f"🔍 Subdomain Enumeration für {self.current_target}")
        print("="*70)
        
        progress = ProgressBar(total=100, description="Subdomain Enumeration")
        progress.start()
        
        try:
            # Update progress during enumeration
            progress.update(25, "DNS Bruteforce läuft...")
            time.sleep(1)  # Simulate work
            
            result = self.recon_manager.run_subdomain_enumeration(self.current_target, methods)
            
            progress.update(100, "Abgeschlossen!")
            progress.stop()
            
            print(f"\n✅ Subdomain Enumeration abgeschlossen!")
            print(f"📊 Gefundene Subdomains: {len(result.subdomains)}")
            
            if result.subdomains:
                print("\n📋 Gefundene Subdomains:")
                for subdomain in sorted(list(result.subdomains)[:20]):  # Show first 20
                    print(f"  • {subdomain}")
                
                if len(result.subdomains) > 20:
                    print(f"  ... und {len(result.subdomains) - 20} weitere")
            
            print(f"\n📁 Ergebnisse gespeichert in: recon_data/")
            
        except Exception as e:
            progress.stop()
            print(f"❌ Fehler bei Subdomain Enumeration: {e}")
        
        input("\nDrücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def custom_subdomain_enum(self):
        """Custom subdomain enumeration method selection"""
        print("\n" + "="*60)
        print("🛠️  Methoden auswählen")
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
            print("❌ Keine Methoden ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def port_scanning_menu(self):
        """Port scanning submenu"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title=f"🔍 Port Scanning - {self.current_target}",
            description="Network port discovery and service detection"
        )
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="1",
            title="Quick Scan (Top 100)",
            description="Scan most common 100 ports",
            action=lambda: self.run_port_scan("top100"),
            shortcut="q"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="2",
            title="Standard Scan (Top 1000)",
            description="Scan top 1000 most common ports",
            action=lambda: self.run_port_scan("top1000"),
            shortcut="s"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="3",
            title="Full Scan (All Ports)",
            description="Scan all 65535 ports (very slow)",
            action=lambda: self.run_port_scan("all"),
            shortcut="f",
            dangerous=True
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="4",
            title="Custom Range",
            description="Specify custom port range",
            action=self.custom_port_scan,
            shortcut="c"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="5",
            title="Scan All Subdomains",
            description="Port scan all discovered subdomains",
            action=self.scan_all_subdomains,
            shortcut="a",
            dangerous=True
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="0",
            title="Zurück",
            description="Return to reconnaissance menu",
            action=menu.exit_menu,
            shortcut="b"
        ))
        
        menu.run()
    
    @handle_errors
    def run_port_scan(self, port_range: str, host: str = None):
        """Run port scan"""
        if not host:
            host = self.current_target
        
        print("\n" + "="*70)
        print(f"🔍 Port Scan für {host} ({port_range})")
        print("="*70)
        
        progress = ProgressBar(total=100, description="Port Scanning")
        progress.start()
        
        try:
            progress.update(25, "Port Scan läuft...")
            result = self.recon_manager.run_port_scan(host, port_range)
            
            progress.update(100, "Abgeschlossen!")
            progress.stop()
            
            print(f"\n✅ Port Scan abgeschlossen!")
            print(f"📊 Offene Ports: {len(result.open_ports)}")
            print(f"⏱️  Scan-Dauer: {result.scan_duration:.2f} Sekunden")
            
            if result.open_ports:
                print("\n📋 Offene Ports:")
                for port, service in result.open_ports:
                    print(f"  • {port}/tcp - {service}")
            
            print(f"\n📁 Ergebnisse gespeichert in: recon_data/")
            
        except Exception as e:
            progress.stop()
            print(f"❌ Fehler beim Port Scan: {e}")
        
        input("\nDrücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def custom_port_scan(self):
        """Custom port range scanning"""
        print("\n" + "="*60)
        print("🛠️  Benutzerdefinierten Port-Bereich eingeben")
        print("="*60)
        
        port_range = input("Port-Bereich (z.B. '1-1000' oder 'top100'): ").strip()
        
        if port_range:
            self.run_port_scan(port_range)
        else:
            print("❌ Ungültiger Port-Bereich!")
            input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def scan_all_subdomains(self):
        """Scan all discovered subdomains"""
        if self.current_target not in self.recon_manager.targets:
            print("❌ Ziel nicht gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        target = self.recon_manager.targets[self.current_target]
        if not target.subdomains or not target.subdomains.subdomains:
            print("❌ Keine Subdomains gefunden! Führen Sie zuerst Subdomain Enumeration durch.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        subdomains = list(target.subdomains.subdomains)
        
        print(f"\n📊 {len(subdomains)} Subdomains für Port Scan gefunden")
        confirm = input("❗ Alle Subdomains scannen? Dies kann lange dauern! (j/N): ").lower()
        
        if confirm != 'j':
            return
        
        port_range = input("Port-Bereich (top100/top1000/all): ").strip() or "top100"
        
        print("\n" + "="*70)
        print(f"🔍 Port Scan für alle Subdomains ({port_range})")
        print("="*70)
        
        total_subdomains = len(subdomains)
        for i, subdomain in enumerate(subdomains, 1):
            print(f"\n[{i}/{total_subdomains}] Scanning {subdomain}...")
            try:
                self.run_port_scan(port_range, subdomain)
            except Exception as e:
                print(f"❌ Fehler beim Scannen von {subdomain}: {e}")
        
        print(f"\n✅ Port Scan für alle Subdomains abgeschlossen!")
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def service_fingerprinting_menu(self):
        """Service fingerprinting submenu"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title=f"🔍 Service Fingerprinting - {self.current_target}",
            description="Identify services and versions on open ports"
        )
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="1",
            title="Fingerprint Main Target",
            description="Fingerprint services on main target",
            action=lambda: self.run_service_fingerprinting(self.current_target),
            shortcut="m"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="2",
            title="Fingerprint All Hosts",
            description="Fingerprint all scanned hosts",
            action=self.fingerprint_all_hosts,
            shortcut="a"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="3",
            title="Select Specific Host",
            description="Choose specific host for fingerprinting",
            action=self.select_host_fingerprinting,
            shortcut="s"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="0",
            title="Zurück",
            description="Return to reconnaissance menu",
            action=menu.exit_menu,
            shortcut="b"
        ))
        
        menu.run()
    
    @handle_errors
    def run_service_fingerprinting(self, host: str):
        """Run service fingerprinting for a specific host"""
        print("\n" + "="*70)
        print(f"🔍 Service Fingerprinting für {host}")
        print("="*70)
        
        progress = ProgressBar(total=100, description="Service Fingerprinting")
        progress.start()
        
        try:
            progress.update(50, "Services identifizieren...")
            services = self.recon_manager.run_service_fingerprinting(host)
            
            progress.update(100, "Abgeschlossen!")
            progress.stop()
            
            print(f"\n✅ Service Fingerprinting abgeschlossen!")
            print(f"📊 Identifizierte Services: {len(services)}")
            
            if services:
                print("\n📋 Gefundene Services:")
                for service in services:
                    ssl_indicator = "🔒" if service.ssl_info else ""
                    version_info = f" ({service.version})" if service.version else ""
                    print(f"  • {service.port}/tcp - {service.service}{version_info} {ssl_indicator}")
            
            print(f"\n📁 Ergebnisse gespeichert in: recon_data/")
            
        except Exception as e:
            progress.stop()
            print(f"❌ Fehler beim Service Fingerprinting: {e}")
        
        input("\nDrücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def fingerprint_all_hosts(self):
        """Fingerprint all scanned hosts"""
        if self.current_target not in self.recon_manager.targets:
            print("❌ Ziel nicht gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        target = self.recon_manager.targets[self.current_target]
        
        if not target.port_scans:
            print("❌ Keine Port Scans gefunden! Führen Sie zuerst Port Scanning durch.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        hosts_with_ports = [(host, scan) for host, scan in target.port_scans.items() if scan.open_ports]
        
        if not hosts_with_ports:
            print("❌ Keine offenen Ports gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print(f"\n📊 {len(hosts_with_ports)} Hosts mit offenen Ports gefunden")
        
        for host, scan in hosts_with_ports:
            print(f"\n🔍 Fingerprinting {host} ({len(scan.open_ports)} offene Ports)...")
            try:
                self.run_service_fingerprinting(host)
            except Exception as e:
                print(f"❌ Fehler beim Fingerprinting von {host}: {e}")
        
        print(f"\n✅ Service Fingerprinting für alle Hosts abgeschlossen!")
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def select_host_fingerprinting(self):
        """Select specific host for fingerprinting"""
        if self.current_target not in self.recon_manager.targets:
            print("❌ Ziel nicht gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        target = self.recon_manager.targets[self.current_target]
        
        if not target.port_scans:
            print("❌ Keine Port Scans gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        hosts = list(target.port_scans.keys())
        
        print("\n" + "="*60)
        print("🎯 Host für Fingerprinting auswählen")
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
                print("❌ Ungültige Auswahl!")
                input("Drücken Sie Enter um fortzufahren...")
        except ValueError:
            print("❌ Bitte eine gültige Nummer eingeben!")
            input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def full_reconnaissance_menu(self):
        """Full reconnaissance workflow"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt! Bitte zuerst ein Ziel auswählen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*70)
        print(f"🚀 Vollständige Reconnaissance für {self.current_target}")
        print("="*70)
        print("⚠️  Dies führt folgende Schritte automatisch aus:")
        print("   1. Subdomain Enumeration (alle Methoden)")
        print("   2. Port Scanning (Top 1000 Ports)")
        print("   3. Service Fingerprinting")
        print("   4. Report Generation")
        print()
        
        confirm = input("❗ Vollständige Reconnaissance starten? (j/N): ").lower()
        if confirm != 'j':
            return
        
        # Configuration options
        print("\n🛠️  Konfiguration:")
        subdomain_methods = []
        
        if input("DNS Bruteforce verwenden? (J/n): ").lower() != 'n':
            subdomain_methods.append('dns_bruteforce')
        
        if input("Certificate Transparency verwenden? (J/n): ").lower() != 'n':
            subdomain_methods.append('certificate_transparency')
        
        port_range = input("Port-Bereich (top100/top1000/all) [top1000]: ").strip() or "top1000"
        
        print("\n" + "="*70)
        print("🚀 Starte vollständige Reconnaissance...")
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
            
            print(f"\n✅ Vollständige Reconnaissance abgeschlossen!")
            print("="*70)
            print(f"📊 Zusammenfassung für {self.current_target}:")
            print(f"   • Subdomains gefunden: {summary.get('subdomains_count', 0)}")
            print(f"   • Hosts gescannt: {summary.get('hosts_scanned', 0)}")
            print(f"   • Offene Ports: {summary.get('total_open_ports', 0)}")
            print(f"   • Services identifiziert: {summary.get('services_identified', 0)}")
            print(f"   • Web Services: {summary.get('web_services', 0)}")
            print(f"   • SSL Services: {summary.get('ssl_services', 0)}")
            print("="*70)
            print(f"📁 Alle Ergebnisse gespeichert in: recon_data/")
            
        except Exception as e:
            progress.stop()
            print(f"❌ Fehler bei vollständiger Reconnaissance: {e}")
        
        input("\nDrücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def results_menu(self):
        """Results and reports menu"""
        menu = EnhancedMenu(
            title="📊 Reconnaissance Results & Reports",
            description="View results and generate reports"
        )
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="1",
            title="Target Summary",
            description="Show summary of current target",
            action=self.show_target_summary,
            shortcut="s"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="2",
            title="Detailed Results",
            description="Show detailed reconnaissance results",
            action=self.show_detailed_results,
            shortcut="d"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="3",
            title="Export Results",
            description="Export results to various formats",
            action=self.export_results,
            shortcut="e"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="4",
            title="Compare Targets",
            description="Compare multiple reconnaissance targets",
            action=self.compare_targets,
            shortcut="c"
        ))
        
        menu.add_enhanced_item(EnhancedMenuItem(
            key="0",
            title="Zurück",
            description="Return to reconnaissance menu",
            action=menu.exit_menu,
            shortcut="b"
        ))
        
        menu.run()
    
    @handle_errors
    def show_target_summary(self):
        """Show target summary"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        summary = self.recon_manager.get_target_summary(self.current_target)
        
        print("\n" + "="*70)
        print(f"📊 Zusammenfassung für {self.current_target}")
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
            print("❌ Kein gültiges Ziel ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        target = self.recon_manager.targets[self.current_target]
        
        print("\n" + "="*80)
        print(f"📋 Detaillierte Ergebnisse für {self.current_target}")
        print("="*80)
        
        # Subdomains
        if target.subdomains:
            print(f"\n🔍 Subdomains ({len(target.subdomains.subdomains)}):")
            for subdomain in sorted(list(target.subdomains.subdomains)[:10]):
                print(f"  • {subdomain}")
            if len(target.subdomains.subdomains) > 10:
                print(f"  ... und {len(target.subdomains.subdomains) - 10} weitere")
        
        # Port scans
        if target.port_scans:
            print(f"\n🔍 Port Scans ({len(target.port_scans)} Hosts):")
            for host, scan in target.port_scans.items():
                print(f"  📍 {host}: {len(scan.open_ports)} offene Ports")
                for port, service in scan.open_ports[:5]:
                    print(f"    • {port}/tcp - {service}")
                if len(scan.open_ports) > 5:
                    print(f"    ... und {len(scan.open_ports) - 5} weitere")
        
        # Services
        if target.services:
            print(f"\n🔍 Services ({len(target.services)}):")
            for service in target.services[:10]:
                ssl_indicator = "🔒" if service.ssl_info else ""
                version_info = f" ({service.version})" if service.version else ""
                print(f"  • {service.host}:{service.port} - {service.service}{version_info} {ssl_indicator}")
            if len(target.services) > 10:
                print(f"  ... und {len(target.services) - 10} weitere")
        
        print("="*80)
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def export_results(self):
        """Export results to file"""
        if not self.current_target:
            print("❌ Kein Ziel ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print("📤 Ergebnisse exportieren")
        print("="*60)
        print("1. JSON Format")
        print("2. CSV Format")
        print("3. TXT Format")
        
        choice = input("Format auswählen (1-3): ").strip()
        
        if choice == "1":
            self.recon_manager.save_target_data(self.current_target)
            print("✅ Ergebnisse als JSON exportiert!")
        elif choice in ["2", "3"]:
            print("ℹ️  CSV/TXT Export wird in einer zukünftigen Version verfügbar sein.")
        else:
            print("❌ Ungültige Auswahl!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def compare_targets(self):
        """Compare multiple targets"""
        if len(self.recon_manager.targets) < 2:
            print("❌ Mindestens 2 Ziele erforderlich für Vergleich!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*80)
        print("📊 Ziel-Vergleich")
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