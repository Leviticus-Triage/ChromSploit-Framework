#!/usr/bin/env python3
"""
Evidence collection menu for forensic documentation and chain of custody.
"""

import time
import os
from typing import List, Optional, Tuple

from core.enhanced_menu import EnhancedMenu, ProgressBar
from core.colors import Colors
from core.evidence_collection import get_evidence_manager, EvidenceType
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors


class EvidenceMenu(EnhancedMenu):
    """Evidence collection and management menu"""
    
    def __init__(self):
        super().__init__(
            title="🔍 Evidence Collection System",
            description="Forensic evidence collection with chain of custody"
        )
        self.evidence_manager = get_evidence_manager()
        self.logger = get_logger()
        self.current_case = None
        
        self.setup_menu_items()
    
    def setup_menu_items(self):
        """Setup evidence menu items"""
        self.add_enhanced_item(
            "Case Management",
            self.case_management_menu,
            key="1",
            description="Create and manage evidence collection cases",
            shortcut="c",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "Capture Screenshots",
            self.screenshot_menu,
            key="2",
            description="Capture screen evidence with timestamps",
            shortcut="s",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "Network Traffic Capture",
            self.network_capture_menu,
            key="3",
            description="Record network packets (PCAP format)",
            shortcut="n",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "Memory Dumps",
            self.memory_dump_menu,
            key="4",
            description="Capture process or system memory",
            shortcut="m",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "File & Artifact Collection",
            self.artifact_collection_menu,
            key="5",
            description="Collect files and system artifacts",
            shortcut="f",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "System Information",
            self.system_info_menu,
            key="6",
            description="Collect comprehensive system data",
            shortcut="i",
            color=Colors.CYAN
        )
        
        self.add_enhanced_item(
            "Evidence Reports",
            self.report_menu,
            key="7",
            description="Generate evidence reports and exports",
            shortcut="r",
            color=Colors.GREEN
        )
        
        self.add_enhanced_item(
            "Zurück zum Hauptmenü",
            self.exit_menu,
            key="0",
            description="Return to main menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
    
    @handle_errors
    def case_management_menu(self):
        """Case management submenu"""
        menu = EnhancedMenu(
            title="📁 Case Management",
            description="Manage evidence collection cases"
        )
        
        menu.add_enhanced_item(
            "Create New Case",
            self.create_case,
            key="1",
            description="Start a new evidence collection case",
            shortcut="n",
            color=Colors.GREEN
        )
        
        menu.add_enhanced_item(
            "List Cases",
            self.list_cases,
            key="2",
            description="Show all evidence cases",
            shortcut="l",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Select Active Case",
            self.select_case,
            key="3",
            description="Choose case for evidence collection",
            shortcut="s",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Case Details",
            self.case_details,
            key="4",
            description="View detailed case information",
            shortcut="d",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def create_case(self):
        """Create new evidence case"""
        print("\n" + "="*60)
        print("📁 Neuen Fall erstellen")
        print("="*60)
        
        case_name = input("Fall-Name: ").strip()
        if not case_name:
            print("❌ Ungültiger Fall-Name!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        description = input("Beschreibung: ").strip()
        target = input("Ziel/System: ").strip()
        
        case_id = self.evidence_manager.create_case(case_name, description, target)
        self.current_case = case_id
        
        print(f"✅ Fall erstellt: {case_name}")
        print(f"📋 Fall-ID: {case_id}")
        print(f"🎯 Als aktiver Fall ausgewählt")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def list_cases(self):
        """List all evidence cases"""
        cases = self.evidence_manager.list_cases()
        
        print("\n" + "="*90)
        print("📋 Evidence Collection Cases")
        print("="*90)
        
        if not cases:
            print("ℹ️  Keine Fälle gefunden.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print(f"{'Nr.':<3} {'Fall-ID':<15} {'Name':<25} {'Ziel':<20} {'Evidence':<10} {'Status':<10}")
        print("-" * 90)
        
        for i, case in enumerate(cases, 1):
            active = " 🎯" if case['case_id'] == self.current_case else ""
            print(f"{i:<3} {case['case_id']:<15} {case['case_name'][:24]:<25} "
                  f"{case['target'][:19]:<20} {case['total_evidence']:<10} {case['status']:<10}{active}")
        
        print("="*90)
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def select_case(self):
        """Select active case"""
        cases = self.evidence_manager.list_cases()
        
        if not cases:
            print("❌ Keine Fälle verfügbar! Bitte zuerst einen Fall erstellen.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print("🎯 Aktiven Fall auswählen")
        print("="*60)
        
        for i, case in enumerate(cases, 1):
            status = " (Aktuell)" if case['case_id'] == self.current_case else ""
            print(f"{i}. {case['case_name']} - {case['case_id']}{status}")
        
        try:
            choice = int(input("\nFall auswählen (Nummer): ")) - 1
            if 0 <= choice < len(cases):
                self.current_case = cases[choice]['case_id']
                print(f"✅ Fall '{cases[choice]['case_name']}' ausgewählt!")
            else:
                print("❌ Ungültige Auswahl!")
        except ValueError:
            print("❌ Bitte eine gültige Nummer eingeben!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def case_details(self):
        """Show case details"""
        if not self.current_case:
            print("❌ Kein Fall ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        summary = self.evidence_manager.get_case_summary(self.current_case)
        
        if not summary:
            print("❌ Fall nicht gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*70)
        print(f"📋 Fall-Details: {summary['case_name']}")
        print("="*70)
        print(f"Fall-ID: {summary['case_id']}")
        print(f"Ziel: {summary['target']}")
        print(f"Status: {summary['status']}")
        print(f"Erstellt: {summary['created_at']}")
        print(f"Zuletzt aktualisiert: {summary['last_updated']}")
        print(f"Anzahl Evidence-Items: {summary['total_evidence']}")
        print(f"Chain of Custody Einträge: {summary['chain_of_custody_entries']}")
        
        if summary['evidence_by_type']:
            print("\nEvidence nach Typ:")
            for etype, count in summary['evidence_by_type'].items():
                print(f"  • {etype}: {count}")
        
        print("="*70)
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def screenshot_menu(self):
        """Screenshot capture submenu"""
        if not self.current_case:
            print("❌ Bitte zuerst einen Fall auswählen!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title="📸 Screenshot Capture",
            description="Capture screen evidence"
        )
        
        menu.add_enhanced_item(
            "Full Screen Capture",
            self.capture_full_screenshot,
            key="1",
            description="Capture entire screen",
            shortcut="f",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Region Capture",
            self.capture_region_screenshot,
            key="2",
            description="Capture specific screen region",
            shortcut="r",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Window Capture",
            self.capture_window_screenshot,
            key="3",
            description="Capture specific window",
            shortcut="w",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Timed Capture",
            self.timed_screenshot,
            key="4",
            description="Capture after delay",
            shortcut="t",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def capture_full_screenshot(self):
        """Capture full screen"""
        print("\n" + "="*60)
        print("📸 Vollbild-Screenshot")
        print("="*60)
        
        title = input("Screenshot-Titel (optional): ").strip()
        description = input("Beschreibung (optional): ").strip()
        
        print("\n📸 Erfasse Screenshot...")
        
        evidence = self.evidence_manager.collect_screenshot(
            self.current_case, 
            title or "Full Screen", 
            description or "Full screen capture"
        )
        
        if evidence:
            print(f"✅ Screenshot erfasst!")
            print(f"📁 Datei: {evidence.file_path}")
            print(f"🔒 Hash: {evidence.hash_value[:32]}...")
        else:
            print("❌ Screenshot-Erfassung fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def capture_region_screenshot(self):
        """Capture screen region"""
        print("\n" + "="*60)
        print("📸 Bereichs-Screenshot")
        print("="*60)
        
        print("Bildschirmbereich definieren:")
        try:
            x = int(input("X-Position: "))
            y = int(input("Y-Position: "))
            width = int(input("Breite: "))
            height = int(input("Höhe: "))
            
            region = (x, y, x + width, y + height)
            
            title = input("Screenshot-Titel (optional): ").strip()
            description = input("Beschreibung (optional): ").strip()
            
            print("\n📸 Erfasse Bereich...")
            
            evidence = self.evidence_manager.collect_screenshot(
                self.current_case,
                title or "Region Capture",
                description or f"Region capture at ({x},{y}) size {width}x{height}",
                region=region
            )
            
            if evidence:
                print(f"✅ Bereichs-Screenshot erfasst!")
                print(f"📁 Datei: {evidence.file_path}")
            else:
                print("❌ Screenshot-Erfassung fehlgeschlagen!")
                
        except ValueError:
            print("❌ Ungültige Eingabe!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def capture_window_screenshot(self):
        """Capture specific window"""
        print("\n" + "="*60)
        print("📸 Fenster-Screenshot")
        print("="*60)
        
        window_title = input("Fenstertitel: ").strip()
        
        if not window_title:
            print("❌ Kein Fenstertitel angegeben!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        description = input("Beschreibung (optional): ").strip()
        
        print(f"\n📸 Erfasse Fenster '{window_title}'...")
        
        # For now, capture full screen with window title in metadata
        evidence = self.evidence_manager.collect_screenshot(
            self.current_case,
            f"Window: {window_title}",
            description or f"Window capture: {window_title}"
        )
        
        if evidence:
            print(f"✅ Fenster-Screenshot erfasst!")
            print(f"📁 Datei: {evidence.file_path}")
        else:
            print("❌ Screenshot-Erfassung fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def timed_screenshot(self):
        """Capture screenshot after delay"""
        print("\n" + "="*60)
        print("📸 Zeitverzögerter Screenshot")
        print("="*60)
        
        try:
            delay = int(input("Verzögerung in Sekunden (Standard: 5): ") or "5")
            
            title = input("Screenshot-Titel (optional): ").strip()
            description = input("Beschreibung (optional): ").strip()
            
            print(f"\n⏱️  Screenshot in {delay} Sekunden...")
            
            for i in range(delay, 0, -1):
                print(f"\r{i}...", end="", flush=True)
                time.sleep(1)
            
            print("\n📸 Erfasse Screenshot...")
            
            evidence = self.evidence_manager.collect_screenshot(
                self.current_case,
                title or "Timed Screenshot",
                description or f"Screenshot captured after {delay}s delay"
            )
            
            if evidence:
                print(f"✅ Screenshot erfasst!")
                print(f"📁 Datei: {evidence.file_path}")
            else:
                print("❌ Screenshot-Erfassung fehlgeschlagen!")
                
        except ValueError:
            print("❌ Ungültige Eingabe!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def network_capture_menu(self):
        """Network capture submenu"""
        if not self.current_case:
            print("❌ Bitte zuerst einen Fall auswählen!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title="🌐 Network Traffic Capture",
            description="Capture network packets"
        )
        
        menu.add_enhanced_item(
            "Quick Capture (60s)",
            lambda: self.network_capture(60),
            key="1",
            description="Capture all traffic for 60 seconds",
            shortcut="q",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Custom Duration",
            self.custom_network_capture,
            key="2",
            description="Specify capture duration",
            shortcut="c",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "HTTP/HTTPS Traffic",
            self.http_capture,
            key="3",
            description="Capture only web traffic",
            shortcut="h",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Filtered Capture",
            self.filtered_capture,
            key="4",
            description="Capture with custom BPF filter",
            shortcut="f",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def network_capture(self, duration: int = 60):
        """Capture network traffic"""
        print("\n" + "="*70)
        print(f"🌐 Network Traffic Capture ({duration}s)")
        print("="*70)
        
        interface = input("Netzwerk-Interface (leer für default): ").strip() or None
        
        print(f"\n📡 Starte Netzwerk-Aufzeichnung für {duration} Sekunden...")
        
        progress = ProgressBar(total=duration, description="Capturing packets")
        progress.start()
        
        # Start capture in background
        evidence = self.evidence_manager.collect_network_traffic(
            self.current_case,
            duration=duration,
            interface=interface
        )
        
        # Update progress
        for i in range(duration):
            progress.update(i + 1, f"Capturing... {duration - i - 1}s remaining")
            time.sleep(1)
        
        progress.stop()
        
        if evidence:
            print(f"✅ Netzwerk-Traffic erfasst!")
            print(f"📁 PCAP-Datei: {evidence.file_path}")
            print(f"📊 Metadaten: {evidence.metadata.get('packet_count', 'Unknown')} Pakete")
        else:
            print("❌ Netzwerk-Aufzeichnung fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def custom_network_capture(self):
        """Custom duration network capture"""
        print("\n" + "="*60)
        print("🌐 Benutzerdefinierte Netzwerk-Aufzeichnung")
        print("="*60)
        
        try:
            duration = int(input("Dauer in Sekunden: "))
            if duration <= 0 or duration > 3600:
                print("❌ Ungültige Dauer! (1-3600 Sekunden)")
                input("Drücken Sie Enter um fortzufahren...")
                return
            
            self.network_capture(duration)
            
        except ValueError:
            print("❌ Ungültige Eingabe!")
            input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def http_capture(self):
        """Capture HTTP/HTTPS traffic"""
        print("\n" + "="*60)
        print("🌐 HTTP/HTTPS Traffic Capture")
        print("="*60)
        
        try:
            duration = int(input("Dauer in Sekunden (Standard: 60): ") or "60")
            ports = input("Ports (Standard: 80,443,8080,8443): ").strip()
            
            if not ports:
                ports = "80,443,8080,8443"
            
            port_list = [p.strip() for p in ports.split(',')]
            filter_expr = " or ".join([f"tcp port {p}" for p in port_list])
            
            interface = input("Netzwerk-Interface (leer für default): ").strip() or None
            
            print(f"\n📡 Erfasse HTTP/HTTPS Traffic auf Ports {ports}...")
            
            evidence = self.evidence_manager.collect_network_traffic(
                self.current_case,
                duration=duration,
                interface=interface,
                filter_expr=filter_expr
            )
            
            if evidence:
                print(f"✅ HTTP/HTTPS Traffic erfasst!")
                print(f"📁 PCAP-Datei: {evidence.file_path}")
            else:
                print("❌ Traffic-Aufzeichnung fehlgeschlagen!")
                
        except ValueError:
            print("❌ Ungültige Eingabe!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def filtered_capture(self):
        """Capture with BPF filter"""
        print("\n" + "="*60)
        print("🌐 Gefilterte Netzwerk-Aufzeichnung")
        print("="*60)
        
        print("Beispiel-Filter:")
        print("  • host 192.168.1.1")
        print("  • port 22")
        print("  • tcp and port 80")
        print("  • src host 10.0.0.1 and dst port 443")
        print()
        
        filter_expr = input("BPF Filter: ").strip()
        
        if not filter_expr:
            print("❌ Kein Filter angegeben!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        try:
            duration = int(input("Dauer in Sekunden (Standard: 60): ") or "60")
            interface = input("Netzwerk-Interface (leer für default): ").strip() or None
            
            print(f"\n📡 Erfasse gefilterten Traffic: {filter_expr}")
            
            evidence = self.evidence_manager.collect_network_traffic(
                self.current_case,
                duration=duration,
                interface=interface,
                filter_expr=filter_expr
            )
            
            if evidence:
                print(f"✅ Gefilterter Traffic erfasst!")
                print(f"📁 PCAP-Datei: {evidence.file_path}")
            else:
                print("❌ Traffic-Aufzeichnung fehlgeschlagen!")
                
        except ValueError:
            print("❌ Ungültige Eingabe!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def memory_dump_menu(self):
        """Memory dump submenu"""
        if not self.current_case:
            print("❌ Bitte zuerst einen Fall auswählen!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title="💾 Memory Dumps",
            description="Capture process and system memory"
        )
        
        menu.add_enhanced_item(
            "Process Memory Dump",
            self.process_memory_dump,
            key="1",
            description="Dump memory of specific process",
            shortcut="p",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Current Process Dump",
            self.current_process_dump,
            key="2",
            description="Dump memory of current Python process",
            shortcut="c",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Full System Memory",
            self.full_memory_dump,
            key="3",
            description="Dump complete system memory (requires root)",
            shortcut="f",
            dangerous=True,
            color=Colors.RED
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def process_memory_dump(self):
        """Dump specific process memory"""
        print("\n" + "="*60)
        print("💾 Process Memory Dump")
        print("="*60)
        
        try:
            pid = int(input("Process ID (PID): "))
            
            print(f"\n💾 Erstelle Memory Dump für PID {pid}...")
            
            evidence = self.evidence_manager.collect_memory_dump(self.current_case, pid=pid)
            
            if evidence:
                print(f"✅ Memory Dump erstellt!")
                print(f"📁 Datei: {evidence.file_path}")
                print(f"📊 Größe: {evidence.metadata.get('dump_size', 0) / (1024*1024):.2f} MB")
                
                if evidence.metadata.get('sample_strings'):
                    print("\n📝 Beispiel-Strings aus dem Dump:")
                    for s in evidence.metadata['sample_strings'][:5]:
                        print(f"  • {s[:50]}...")
            else:
                print("❌ Memory Dump fehlgeschlagen!")
                print("ℹ️  Benötigt möglicherweise erhöhte Berechtigungen")
                
        except ValueError:
            print("❌ Ungültige PID!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def current_process_dump(self):
        """Dump current process memory"""
        print("\n" + "="*60)
        print("💾 Current Process Memory Dump")
        print("="*60)
        
        current_pid = os.getpid()
        print(f"Aktueller Prozess PID: {current_pid}")
        
        confirm = input("Memory Dump des aktuellen Prozesses erstellen? (j/N): ").lower()
        if confirm != 'j':
            return
        
        print(f"\n💾 Erstelle Memory Dump für aktuellen Prozess...")
        
        evidence = self.evidence_manager.collect_memory_dump(self.current_case, pid=current_pid)
        
        if evidence:
            print(f"✅ Memory Dump erstellt!")
            print(f"📁 Datei: {evidence.file_path}")
        else:
            print("❌ Memory Dump fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def full_memory_dump(self):
        """Full system memory dump"""
        print("\n" + "="*60)
        print("💾 Full System Memory Dump")
        print("="*60)
        print("⚠️  WARNUNG: Benötigt Root-Berechtigungen!")
        print("⚠️  Kann sehr groß werden (mehrere GB)")
        print()
        
        confirm = input("❗ Vollständigen System Memory Dump erstellen? (j/N): ").lower()
        if confirm != 'j':
            return
        
        print("\n💾 Erstelle vollständigen Memory Dump...")
        
        evidence = self.evidence_manager.collect_memory_dump(self.current_case)
        
        if evidence:
            print(f"✅ System Memory Dump erstellt!")
            print(f"📁 Datei: {evidence.file_path}")
        else:
            print("❌ Memory Dump fehlgeschlagen!")
            print("ℹ️  Benötigt Root-Berechtigungen")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def artifact_collection_menu(self):
        """Artifact collection submenu"""
        if not self.current_case:
            print("❌ Bitte zuerst einen Fall auswählen!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        menu = EnhancedMenu(
            title="📁 File & Artifact Collection",
            description="Collect files and system artifacts"
        )
        
        menu.add_enhanced_item(
            "Collect Specific File",
            self.collect_file,
            key="1",
            description="Collect a file as evidence",
            shortcut="f",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Command Output",
            self.collect_command,
            key="2",
            description="Collect command execution output",
            shortcut="c",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Log Files",
            self.collect_logs,
            key="3",
            description="Collect system and application logs",
            shortcut="l",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Browser Artifacts",
            self.collect_browser_artifacts,
            key="4",
            description="Collect browser data and history",
            shortcut="b",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def collect_file(self):
        """Collect specific file"""
        print("\n" + "="*60)
        print("📁 Datei als Evidence sammeln")
        print("="*60)
        
        file_path = input("Dateipfad: ").strip()
        
        if not file_path:
            print("❌ Kein Dateipfad angegeben!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        description = input("Beschreibung (optional): ").strip()
        
        print(f"\n📁 Sammle Datei: {file_path}")
        
        evidence = self.evidence_manager.collect_file_artifact(
            self.current_case,
            file_path,
            description
        )
        
        if evidence:
            print(f"✅ Datei gesammelt!")
            print(f"📁 Kopie: {evidence.file_path}")
            print(f"🔒 SHA256: {evidence.hash_value}")
            print(f"📊 Größe: {evidence.metadata.get('size', 0)} Bytes")
        else:
            print("❌ Datei-Sammlung fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def collect_command(self):
        """Collect command output"""
        print("\n" + "="*60)
        print("💻 Command Output sammeln")
        print("="*60)
        
        command = input("Befehl: ").strip()
        
        if not command:
            print("❌ Kein Befehl angegeben!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        description = input("Beschreibung (optional): ").strip()
        
        print(f"\n💻 Führe Befehl aus: {command}")
        
        evidence = self.evidence_manager.collect_command_output(
            self.current_case,
            command,
            description
        )
        
        if evidence:
            print(f"✅ Command Output gesammelt!")
            print(f"📁 Datei: {evidence.file_path}")
            print(f"📊 Exit Code: {evidence.metadata.get('exit_code', 'Unknown')}")
        else:
            print("❌ Command-Ausführung fehlgeschlagen!")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def collect_logs(self):
        """Collect log files"""
        print("\n" + "="*60)
        print("📝 Log-Dateien sammeln")
        print("="*60)
        
        # Common log locations
        if os.name == 'posix':
            log_paths = [
                "/var/log/syslog",
                "/var/log/auth.log",
                "/var/log/messages",
                "/var/log/secure",
                "~/.bash_history"
            ]
        else:
            log_paths = [
                "C:\\Windows\\System32\\winevt\\Logs\\System.evtx",
                "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx",
                "C:\\Windows\\System32\\winevt\\Logs\\Application.evtx"
            ]
        
        print("Verfügbare Log-Dateien:")
        for i, path in enumerate(log_paths, 1):
            print(f"{i}. {path}")
        
        print("\nWelche Logs sammeln? (Nummern durch Komma getrennt, oder 'alle'):")
        selection = input("Auswahl: ").strip()
        
        selected_paths = []
        if selection.lower() == 'alle':
            selected_paths = log_paths
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_paths = [log_paths[i] for i in indices if 0 <= i < len(log_paths)]
            except:
                print("❌ Ungültige Auswahl!")
                input("Drücken Sie Enter um fortzufahren...")
                return
        
        collected = 0
        for log_path in selected_paths:
            expanded_path = os.path.expanduser(log_path)
            if os.path.exists(expanded_path):
                evidence = self.evidence_manager.collect_file_artifact(
                    self.current_case,
                    expanded_path,
                    f"Log file: {log_path}"
                )
                if evidence:
                    collected += 1
                    print(f"✅ Gesammelt: {log_path}")
            else:
                print(f"❌ Nicht gefunden: {log_path}")
        
        print(f"\n📊 {collected} Log-Dateien gesammelt")
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def collect_browser_artifacts(self):
        """Collect browser artifacts"""
        print("\n" + "="*60)
        print("🌐 Browser Artifacts sammeln")
        print("="*60)
        
        # Common browser data locations
        browser_paths = {
            'Chrome': {
                'Windows': os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default'),
                'Linux': os.path.expanduser('~/.config/google-chrome/Default'),
                'Darwin': os.path.expanduser('~/Library/Application Support/Google/Chrome/Default')
            },
            'Firefox': {
                'Windows': os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles'),
                'Linux': os.path.expanduser('~/.mozilla/firefox'),
                'Darwin': os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
            }
        }
        
        artifacts = [
            'History',
            'Cookies',
            'Login Data',
            'Web Data',
            'Bookmarks'
        ]
        
        print("Browser-Artifacts sammeln für:")
        print("1. Chrome")
        print("2. Firefox")
        print("3. Beide")
        
        choice = input("Auswahl (1-3): ").strip()
        
        browsers = []
        if choice == '1':
            browsers = ['Chrome']
        elif choice == '2':
            browsers = ['Firefox']
        elif choice == '3':
            browsers = ['Chrome', 'Firefox']
        else:
            print("❌ Ungültige Auswahl!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        collected = 0
        platform = os.name
        if platform == 'posix':
            import platform as plat
            platform = 'Linux' if plat.system() == 'Linux' else 'Darwin'
        elif platform == 'nt':
            platform = 'Windows'
        
        for browser in browsers:
            base_path = browser_paths.get(browser, {}).get(platform)
            
            if not base_path or not os.path.exists(base_path):
                print(f"❌ {browser} Profil nicht gefunden")
                continue
            
            print(f"\n📁 Sammle {browser} Artifacts...")
            
            for artifact in artifacts:
                artifact_path = os.path.join(base_path, artifact)
                if os.path.exists(artifact_path):
                    evidence = self.evidence_manager.collect_file_artifact(
                        self.current_case,
                        artifact_path,
                        f"{browser} {artifact}"
                    )
                    if evidence:
                        collected += 1
                        print(f"✅ Gesammelt: {artifact}")
                else:
                    print(f"❌ Nicht gefunden: {artifact}")
        
        print(f"\n📊 {collected} Browser-Artifacts gesammelt")
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def system_info_menu(self):
        """System information collection"""
        if not self.current_case:
            print("❌ Bitte zuerst einen Fall auswählen!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print("🖥️  System-Informationen sammeln")
        print("="*60)
        
        print("Sammle umfassende System-Informationen...")
        
        artifacts = self.evidence_manager.collect_system_artifacts(self.current_case)
        
        print(f"\n✅ {len(artifacts)} System-Artifacts gesammelt:")
        for artifact in artifacts:
            print(f"  • {artifact.title}")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def report_menu(self):
        """Evidence report menu"""
        menu = EnhancedMenu(
            title="📊 Evidence Reports",
            description="Generate and export evidence reports"
        )
        
        menu.add_enhanced_item(
            "Generate HTML Report",
            lambda: self.generate_report('html'),
            key="1",
            description="Create detailed HTML evidence report",
            shortcut="h",
            color=Colors.GREEN
        )
        
        menu.add_enhanced_item(
            "Generate JSON Report",
            lambda: self.generate_report('json'),
            key="2",
            description="Export evidence data as JSON",
            shortcut="j",
            color=Colors.GREEN
        )
        
        menu.add_enhanced_item(
            "Generate Markdown Report",
            lambda: self.generate_report('markdown'),
            key="3",
            description="Create Markdown documentation",
            shortcut="m",
            color=Colors.GREEN
        )
        
        menu.add_enhanced_item(
            "View Chain of Custody",
            self.view_chain_of_custody,
            key="4",
            description="Show evidence chain of custody",
            shortcut="c",
            color=Colors.CYAN
        )
        
        menu.add_enhanced_item(
            "Zurück",
            menu.exit_menu,
            key="0",
            description="Return to evidence menu",
            shortcut="b",
            color=Colors.BRIGHT_RED
        )
        
        menu.run()
    
    @handle_errors
    def generate_report(self, format: str):
        """Generate evidence report"""
        if not self.current_case:
            print("❌ Kein Fall ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*60)
        print(f"📊 Evidence Report generieren ({format.upper()})")
        print("="*60)
        
        print(f"Generiere {format.upper()} Report...")
        
        try:
            report_file = self.evidence_manager.generate_evidence_report(
                self.current_case,
                format=format
            )
            
            print(f"✅ Report generiert!")
            print(f"📁 Datei: {report_file}")
            
            if format == 'html':
                open_browser = input("\nIm Browser öffnen? (j/N): ").lower()
                if open_browser == 'j':
                    import webbrowser
                    webbrowser.open(f"file://{report_file}")
                    
        except Exception as e:
            print(f"❌ Report-Generierung fehlgeschlagen: {e}")
        
        input("Drücken Sie Enter um fortzufahren...")
    
    @handle_errors
    def view_chain_of_custody(self):
        """View chain of custody"""
        if not self.current_case:
            print("❌ Kein Fall ausgewählt!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        case = self.evidence_manager.cases.get(self.current_case)
        if not case:
            print("❌ Fall nicht gefunden!")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print("\n" + "="*90)
        print(f"🔒 Chain of Custody - {case.case_name}")
        print("="*90)
        
        if not case.chain_of_custody:
            print("ℹ️  Keine Chain of Custody Einträge.")
            input("Drücken Sie Enter um fortzufahren...")
            return
        
        print(f"{'Zeit':<20} {'Aktion':<15} {'Evidence ID':<20} {'Typ':<15} {'Benutzer':<15}")
        print("-" * 90)
        
        for entry in case.chain_of_custody[-20:]:  # Show last 20 entries
            timestamp = entry['timestamp'][:19]  # Remove microseconds
            action = entry['action']
            evidence_id = entry.get('evidence_id', 'N/A')[:19]
            evidence_type = entry.get('evidence_type', 'N/A')[:14]
            user = entry['user'][:14]
            
            print(f"{timestamp:<20} {action:<15} {evidence_id:<20} {evidence_type:<15} {user:<15}")
        
        if len(case.chain_of_custody) > 20:
            print(f"\n... und {len(case.chain_of_custody) - 20} weitere Einträge")
        
        print("="*90)
        input("Drücken Sie Enter um fortzufahren...")
    
    def get_status_text(self) -> str:
        """Get current status for display"""
        if self.current_case:
            summary = self.evidence_manager.get_case_summary(self.current_case)
            if summary:
                return f"Aktiver Fall: {summary['case_name']} ({summary['total_evidence']} Items)"
        return "Kein Fall ausgewählt"
    
    def run(self):
        """Run the menu"""
        self.display()