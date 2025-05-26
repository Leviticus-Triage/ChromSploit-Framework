#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Dokumentationsgenerator
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import subprocess
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class DocumentationGenerator:
    """
    Dokumentationsgenerator für das ChromSploit Framework
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert den Dokumentationsgenerator
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.docs_dir = os.path.join(PathUtils.get_root_dir(), "docs")
        self.output_dir = os.path.join(self.docs_dir, "generated")
        
        # Sicherstellen, dass die Verzeichnisse existieren
        PathUtils.ensure_dir_exists(self.docs_dir)
        PathUtils.ensure_dir_exists(self.output_dir)
    
    def log(self, level: str, message: str) -> None:
        """
        Loggt eine Nachricht
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "debug":
                self.logger.debug(message)
        else:
            print(f"{Colors.BLUE}[*] {message}{Colors.RESET}" if level == "info" else
                  f"{Colors.YELLOW}[!] {message}{Colors.RESET}" if level == "warning" else
                  f"{Colors.RED}[-] {message}{Colors.RESET}" if level == "error" else
                  f"{Colors.MAGENTA}[D] {message}{Colors.RESET}")
    
    def generate_directory_structure(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine Dokumentation der Verzeichnisstruktur
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten Dokumentation oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, "directory_structure.md")
        
        self.log("info", "Generiere Dokumentation der Verzeichnisstruktur...")
        
        try:
            # Verzeichnisstruktur mit find-Befehl generieren
            root_dir = PathUtils.get_root_dir()
            cmd = f"find {root_dir} -type d -not -path '*/\\.*' | sort"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log("error", f"Fehler beim Generieren der Verzeichnisstruktur: {result.stderr}")
                return None
            
            # Ausgabe formatieren
            directories = result.stdout.strip().split('\n')
            
            # Markdown-Dokumentation erstellen
            content = f"""# ChromSploit Framework - Verzeichnisstruktur

Generiert am: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Übersicht

Die folgende Verzeichnisstruktur zeigt den Aufbau des ChromSploit Frameworks:

```
"""
            
            # Verzeichnisbaum erstellen
            for directory in directories:
                rel_path = os.path.relpath(directory, root_dir)
                if rel_path == ".":
                    content += "ChromSploit/\n"
                else:
                    depth = rel_path.count(os.sep)
                    indent = "    " * depth
                    dir_name = os.path.basename(directory)
                    content += f"{indent}├── {dir_name}/\n"
            
            content += "```\n\n"
            
            # Beschreibung der Hauptverzeichnisse hinzufügen
            content += """## Beschreibung der Hauptverzeichnisse

- **core/**: Kernkomponenten des Frameworks (Logger, Konfiguration, Utilities)
- **ui/**: Benutzeroberflächen-Komponenten (Menüs, Dialoge)
- **exploits/**: CVE-spezifische Exploits und Payloads
  - **cve_2025_4664/**: Chrome Data Leak Exploit
  - **cve_2025_2783/**: Chrome Mojo Sandbox Escape Exploit
  - **cve_2025_2857/**: Firefox Sandbox Escape Exploit
  - **cve_2025_30397/**: Edge WebAssembly JIT Escape Exploit
- **tools/**: Integrationen mit externen Tools
  - **sliver_integration.py**: Sliver C2 Framework Integration
  - **metasploit_integration.py**: Metasploit Framework Integration
  - **ngrok_integration.py**: Ngrok Tunneling Integration
  - **ollvm_integration.py**: OLLVM Obfuscation Integration
  - **backdoor_factory.py**: Backdoor Factory Integration
  - **winpeas_integration.py**: WinPEAS Integration
  - **defendnot_integration.py**: DefendNot Integration
- **utils/**: Hilfsfunktionen und -klassen
- **data/**: Datendateien (Templates, Konfigurationen)
- **logs/**: Log-Dateien
- **output/**: Generierte Ausgabedateien
- **config/**: Konfigurationsdateien
- **docs/**: Dokumentation
- **tests/**: Testfälle und -skripte
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Verzeichnisstruktur-Dokumentation generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der Verzeichnisstruktur-Dokumentation: {str(e)}")
            return None
    
    def generate_code_documentation(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine Dokumentation des Codes
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten Dokumentation oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, "code_documentation.md")
        
        self.log("info", "Generiere Code-Dokumentation...")
        
        try:
            # Python-Dateien finden
            root_dir = PathUtils.get_root_dir()
            cmd = f"find {root_dir} -name '*.py' -not -path '*/\\.*' | sort"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log("error", f"Fehler beim Finden der Python-Dateien: {result.stderr}")
                return None
            
            python_files = result.stdout.strip().split('\n')
            
            # Markdown-Dokumentation erstellen
            content = f"""# ChromSploit Framework - Code-Dokumentation

Generiert am: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Übersicht

Diese Dokumentation beschreibt die wichtigsten Komponenten und Module des ChromSploit Frameworks.

"""
            
            # Modulbeschreibungen hinzufügen
            for python_file in python_files:
                if not python_file:
                    continue
                
                rel_path = os.path.relpath(python_file, root_dir)
                module_name = os.path.basename(python_file)
                
                # Modul-Header
                content += f"## {module_name}\n\n"
                content += f"**Pfad:** `{rel_path}`\n\n"
                
                # Docstring extrahieren
                try:
                    with open(python_file, "r") as f:
                        file_content = f.read()
                    
                    # Modul-Docstring extrahieren
                    module_docstring = ""
                    if '"""' in file_content:
                        docstring_start = file_content.find('"""', file_content.find('# -*- coding:')) + 3
                        docstring_end = file_content.find('"""', docstring_start)
                        if docstring_start > 3 and docstring_end > docstring_start:
                            module_docstring = file_content[docstring_start:docstring_end].strip()
                    
                    if module_docstring:
                        content += f"**Beschreibung:**\n\n{module_docstring}\n\n"
                    
                    # Klassen und Funktionen extrahieren
                    classes = []
                    functions = []
                    
                    lines = file_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("class "):
                            class_name = line.split("class ")[1].split("(")[0].strip()
                            classes.append(class_name)
                        elif line.startswith("def ") and "def __" not in line:
                            function_name = line.split("def ")[1].split("(")[0].strip()
                            functions.append(function_name)
                    
                    # Klassen auflisten
                    if classes:
                        content += "**Klassen:**\n\n"
                        for class_name in classes:
                            content += f"- `{class_name}`\n"
                        content += "\n"
                    
                    # Funktionen auflisten
                    if functions:
                        content += "**Funktionen:**\n\n"
                        for function_name in functions:
                            content += f"- `{function_name}`\n"
                        content += "\n"
                    
                    content += "---\n\n"
                except Exception as e:
                    self.log("warning", f"Fehler beim Extrahieren der Docstrings aus {python_file}: {str(e)}")
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Code-Dokumentation generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der Code-Dokumentation: {str(e)}")
            return None
    
    def generate_workflow_documentation(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine Dokumentation der Workflows
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten Dokumentation oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, "workflow_documentation.md")
        
        self.log("info", "Generiere Workflow-Dokumentation...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = f"""# ChromSploit Framework - Workflow-Dokumentation

Generiert am: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Übersicht

Diese Dokumentation beschreibt die wichtigsten Workflows und Prozesse des ChromSploit Frameworks.

## Hauptworkflows

### 1. Framework-Initialisierung

1. **Konfiguration laden**
   - Laden der Konfigurationsdateien aus dem `config/`-Verzeichnis
   - Initialisierung des Loggers
   - Überprüfung der Abhängigkeiten

2. **Menüsystem starten**
   - Anzeigen des ASCII-Art Headers
   - Initialisierung des Hauptmenüs
   - Bereitstellung der Menüoptionen

### 2. Exploit-Ausführung

1. **Exploit auswählen**
   - Navigieren zum entsprechenden CVE-Menü
   - Konfigurieren der Exploit-Parameter

2. **Payload generieren**
   - Auswahl des Payload-Typs
   - Konfiguration der Payload-Parameter
   - Generierung des Payloads

3. **C2-Integration einrichten**
   - Konfiguration der C2-Parameter (Sliver oder Metasploit)
   - Starten des Listeners

4. **Exploit ausführen**
   - Generieren der Exploit-Dateien
   - Starten des Ngrok-Tunnels (falls erforderlich)
   - Bereitstellen des Exploits

5. **Post-Exploitation**
   - Ausführen von Post-Exploitation-Modulen (WinPEAS, DefendNot)
   - Sammeln von Informationen
   - Ausführen von Befehlen auf dem Zielsystem

### 3. Tool-Integration

1. **Tool auswählen**
   - Navigieren zum entsprechenden Tool-Menü
   - Überprüfen der Tool-Verfügbarkeit
   - Installation des Tools (falls erforderlich)

2. **Tool konfigurieren**
   - Einstellen der Tool-Parameter
   - Vorbereiten der Eingabedaten

3. **Tool ausführen**
   - Starten des Tools mit den konfigurierten Parametern
   - Überwachen der Ausführung
   - Sammeln der Ergebnisse

### 4. Live Monitoring

1. **Monitoring starten**
   - Konfigurieren der Monitoring-Parameter
   - Starten des Monitoring-Threads

2. **Logs anzeigen**
   - Anzeigen der Echtzeit-Logs
   - Filtern der Logs nach Level oder Inhalt

3. **Systeminformationen anzeigen**
   - Anzeigen von CPU-, Speicher- und Netzwerkauslastung
   - Überwachen der Systemressourcen

## Detaillierte Prozesse

### CVE-2025-4664 (Chrome Data Leak) Workflow

1. **Konfiguration**
   - Einstellen der Link-Header-Manipulation
   - Konfigurieren der WebSocket-Verbindung
   - Festlegen des Exfiltrationspfads

2. **Payload-Generierung**
   - Generieren der HTML-Payload
   - Einbetten der WebSocket-Verbindung
   - Konfigurieren der Exfiltrationsmethode

3. **Ausführung**
   - Starten des WebSocket-Servers
   - Bereitstellen der HTML-Payload
   - Empfangen der exfiltrierten Daten

### CVE-2025-2783 (Chrome Mojo Sandbox Escape) Workflow

1. **Konfiguration**
   - Einstellen der Mojo IPC-Parameter
   - Konfigurieren des Fuzzing-Prozesses
   - Festlegen der Post-Exploitation-Befehle

2. **Payload-Generierung**
   - Generieren des Mojo IPC-Payloads
   - Einbetten des 0xBADCOFFEE-Headers
   - Konfigurieren des Windows Handle Validation Bypass

3. **Ausführung**
   - Starten des Sliver C2-Listeners
   - Bereitstellen des Mojo IPC-Payloads
   - Ausführen der Post-Exploitation-Befehle

### Sliver C2 Integration Workflow

1. **Konfiguration**
   - Einstellen der Sliver-Parameter
   - Konfigurieren des Listeners
   - Festlegen der Implant-Parameter

2. **Implant-Generierung**
   - Auswahl des Implant-Typs
   - Konfiguration der Implant-Parameter
   - Generierung des Implants

3. **Listener-Start**
   - Starten des Sliver-Listeners
   - Überwachen der eingehenden Verbindungen

4. **Session-Management**
   - Verwalten der aktiven Sessions
   - Ausführen von Befehlen auf den Zielsystemen
   - Sammeln von Informationen

### WinPEAS Integration Workflow

1. **Konfiguration**
   - Auswahl der WinPEAS-Version
   - Konfigurieren der Ausführungsparameter

2. **Befehlsgenerierung**
   - Generieren des PowerShell-Oneliners
   - Generieren des Base64-Payloads
   - Generieren des Memory-Execution-Befehls

3. **Ausführung**
   - Ausführen des WinPEAS-Befehls auf dem Zielsystem
   - Sammeln der Privilege-Escalation-Informationen
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Workflow-Dokumentation generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der Workflow-Dokumentation: {str(e)}")
            return None
    
    def generate_work_breakdown_structure(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine Work Breakdown Structure (WBS)
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten WBS oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, "work_breakdown_structure.md")
        
        self.log("info", "Generiere Work Breakdown Structure...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = f"""# ChromSploit Framework - Work Breakdown Structure (WBS)

Generiert am: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Übersicht

Diese Work Breakdown Structure (WBS) beschreibt die Aufgliederung des ChromSploit Framework-Projekts in einzelne Arbeitspakete.

## 1. Framework-Architektur

### 1.1 Kernkomponenten
- 1.1.1 Logger-System implementieren
- 1.1.2 Konfigurationssystem entwickeln
- 1.1.3 Utility-Funktionen erstellen
- 1.1.4 Pfad-Utilities implementieren

### 1.2 Menüsystem
- 1.2.1 ASCII-Art Header erstellen
- 1.2.2 Hauptmenü implementieren
- 1.2.3 CVE-Menüs entwickeln
- 1.2.4 Tool-Menüs implementieren
- 1.2.5 Einstellungsmenü erstellen

### 1.3 Verzeichnisstruktur
- 1.3.1 Verzeichnishierarchie definieren
- 1.3.2 Verzeichnisse erstellen
- 1.3.3 Berechtigungen konfigurieren

## 2. CVE-Implementierungen

### 2.1 CVE-2025-4664 (Chrome Data Leak)
- 2.1.1 Link-Header-Manipulation implementieren
- 2.1.2 WebSocket-Exfiltration entwickeln
- 2.1.3 HTML-Payload-Generator erstellen
- 2.1.4 Ngrok-Integration implementieren

### 2.2 CVE-2025-2783 (Chrome Mojo Sandbox Escape)
- 2.2.1 Mojo IPC Message Fuzzing implementieren
- 2.2.2 Windows Handle Validation Bypass entwickeln
- 2.2.3 Post-Exploitation-Befehle implementieren
- 2.2.4 Sliver C2-Integration entwickeln

### 2.3 CVE-2025-2857 (Firefox Sandbox Escape)
- 2.3.1 IPDL Handle Confusion Exploit implementieren
- 2.3.2 DuplicateHandle()-Abuse entwickeln
- 2.3.3 Privilege Escalation implementieren
- 2.3.4 Metasploit-Integration entwickeln

### 2.4 CVE-2025-30397 (Edge WebAssembly JIT Escape)
- 2.4.1 TurboFan Compiler Bounds Check Bypass implementieren
- 2.4.2 WebAssembly.Table Growth Exploitation entwickeln
- 2.4.3 V8 Heap Corruption implementieren
- 2.4.4 ROP Chain Generator entwickeln

## 3. Tool-Integrationen

### 3.1 Sliver C2 Framework
- 3.1.1 Implant-Generator implementieren
- 3.1.2 Listener-Management entwickeln
- 3.1.3 Session-Handling implementieren
- 3.1.4 Callback-URL-Generator erstellen

### 3.2 Metasploit Framework
- 3.2.1 Payload-Generator implementieren
- 3.2.2 Handler-Automation entwickeln
- 3.2.3 Encoder-Integration implementieren

### 3.3 OLLVM Obfuscation
- 3.3.1 Binary-Obfuskierung implementieren
- 3.3.2 Obfuskierungslevel definieren
- 3.3.3 Clang++-Integration entwickeln

### 3.4 Ngrok Tunneling
- 3.4.1 Tunnel-Management implementieren
- 3.4.2 Authtoken-Integration entwickeln
- 3.4.3 Multi-Region-Support implementieren
- 3.4.4 URL-Generator erstellen

### 3.5 Backdoor Factory
- 3.5.1 Binary-Injection implementieren
- 3.5.2 PE/ELF-Manipulation entwickeln
- 3.5.3 Signature-Preservation implementieren

## 4. Post-Exploitation

### 4.1 DefendNot Integration
- 4.1.1 Windows Defender Bypass implementieren
- 4.1.2 PowerShell-Script-Generator entwickeln
- 4.1.3 One-Liner-Generator erstellen
- 4.1.4 Silent Mode implementieren

### 4.2 WinPEAS Integration
- 4.2.1 Memory-Execution-Befehle implementieren
- 4.2.2 Base64-Payload-Generator entwickeln
- 4.2.3 Obfuscated Version Support implementieren
- 4.2.4 Privilege Escalation Enumeration automatisieren

## 5. Live Monitoring & Debug System

### 5.1 Log-Viewing
- 5.1.1 Echtzeit-Log-Anzeige implementieren
- 5.1.2 Farb-Kodierung entwickeln
- 5.1.3 Log-Filter implementieren

### 5.2 Multi-threaded Monitoring
- 5.2.1 Thread-Management implementieren
- 5.2.2 Queue-System entwickeln
- 5.2.3 Thread-Synchronisation implementieren

### 5.3 System Information Display
- 5.3.1 CPU-Monitoring implementieren
- 5.3.2 Memory-Monitoring entwickeln
- 5.3.3 Network-Monitoring implementieren

### 5.4 Debug Settings
- 5.4.1 Debug-Level-Konfiguration implementieren
- 5.4.2 Debug-Filter entwickeln
- 5.4.3 Debug-Einstellungen-Management implementieren

## 6. Dokumentation

### 6.1 Technische Dokumentation
- 6.1.1 Code-Dokumentation erstellen
- 6.1.2 Architektur-Dokumentation entwickeln
- 6.1.3 API-Dokumentation erstellen

### 6.2 Benutzerhandbuch
- 6.2.1 Installationsanleitung erstellen
- 6.2.2 Bedienungsanleitung entwickeln
- 6.2.3 Beispiel-Workflows dokumentieren

### 6.3 Entwicklerdokumentation
- 6.3.1 Entwicklungsumgebung dokumentieren
- 6.3.2 Erweiterungsrichtlinien erstellen
- 6.3.3 Beitragsrichtlinien entwickeln

## 7. Tests

### 7.1 Unit-Tests
- 7.1.1 Kernkomponenten-Tests erstellen
- 7.1.2 Utility-Tests entwickeln
- 7.1.3 Integrations-Tests implementieren

### 7.2 Funktionale Tests
- 7.2.1 CVE-Exploit-Tests erstellen
- 7.2.2 Tool-Integrations-Tests entwickeln
- 7.2.3 End-to-End-Tests implementieren

### 7.3 Penetrationstests
- 7.3.1 Testumgebung aufsetzen
- 7.3.2 Exploits gegen Testumgebung ausführen
- 7.3.3 Ergebnisse dokumentieren
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Work Breakdown Structure generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der Work Breakdown Structure: {str(e)}")
            return None
    
    def generate_readme(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine README-Datei
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten README oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(PathUtils.get_root_dir(), "README.md")
        
        self.log("info", "Generiere README...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = """# ChromSploit Framework v2.0

Ein modulares Exploitation Framework für Chrome, Firefox und Edge Browser-Schwachstellen.

## Übersicht

Das ChromSploit Framework ist ein umfassendes Exploitation Framework, das speziell für das Testen und Ausnutzen von Browser-Schwachstellen entwickelt wurde. Es bietet eine modulare Architektur, die es ermöglicht, verschiedene Exploits, Payloads und Post-Exploitation-Module zu kombinieren.

**Hinweis:** Dieses Framework ist ausschließlich für Bildungs- und autorisierte Penetrationstests gedacht. Die Verwendung für illegale Aktivitäten ist strengstens untersagt.

## Funktionen

- **Modulare Architektur**: Einfache Erweiterung mit neuen Exploits und Tools
- **Interaktives CLI**: Benutzerfreundliche Kommandozeilenschnittstelle mit farbiger Ausgabe
- **CVE-Implementierungen**: Implementierung aktueller Browser-Schwachstellen
- **Tool-Integrationen**: Nahtlose Integration mit Sliver, Metasploit, Ngrok und mehr
- **Post-Exploitation**: Automatisierte Post-Exploitation mit WinPEAS und DefendNot
- **Live Monitoring**: Echtzeit-Überwachung von Logs und Systemressourcen

## Anforderungen

- Python 3.9+
- Kali Linux 2025 (empfohlen)
- Internetverbindung für Tool-Downloads und Updates

## Installation

1. Repository klonen:
   ```
   git clone https://github.com/username/chromsploit.git
   cd chromsploit
   ```

2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

3. Framework starten:
   ```
   python chromsploit.py
   ```

## Verzeichnisstruktur

- **core/**: Kernkomponenten des Frameworks
- **ui/**: Benutzeroberflächen-Komponenten
- **exploits/**: CVE-spezifische Exploits und Payloads
- **tools/**: Integrationen mit externen Tools
- **utils/**: Hilfsfunktionen und -klassen
- **data/**: Datendateien
- **logs/**: Log-Dateien
- **output/**: Generierte Ausgabedateien
- **config/**: Konfigurationsdateien
- **docs/**: Dokumentation
- **tests/**: Testfälle und -skripte

## Dokumentation

Die vollständige Dokumentation finden Sie im `docs/`-Verzeichnis:

- [Benutzerhandbuch](docs/user_manual.md)
- [Entwicklerhandbuch](docs/developer_manual.md)
- [API-Dokumentation](docs/api_documentation.md)
- [CVE-Beschreibungen](docs/cve_descriptions.md)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## Haftungsausschluss

Dieses Framework ist ausschließlich für Bildungs- und autorisierte Penetrationstests gedacht. Die Verwendung für illegale Aktivitäten ist strengstens untersagt. Die Autoren übernehmen keine Haftung für Schäden, die durch die Verwendung dieses Frameworks entstehen.
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"README generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der README: {str(e)}")
            return None
    
    def generate_user_manual(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert ein Benutzerhandbuch
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zum generierten Benutzerhandbuch oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.docs_dir, "user_manual.md")
        
        self.log("info", "Generiere Benutzerhandbuch...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = """# ChromSploit Framework - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Installation](#installation)
3. [Erste Schritte](#erste-schritte)
4. [Hauptmenü](#hauptmenü)
5. [CVE-Exploits](#cve-exploits)
6. [Tool-Integrationen](#tool-integrationen)
7. [Post-Exploitation](#post-exploitation)
8. [Live Monitoring](#live-monitoring)
9. [Fehlerbehebung](#fehlerbehebung)
10. [FAQ](#faq)

## Einführung

Das ChromSploit Framework ist ein umfassendes Exploitation Framework, das speziell für das Testen und Ausnutzen von Browser-Schwachstellen entwickelt wurde. Es bietet eine modulare Architektur, die es ermöglicht, verschiedene Exploits, Payloads und Post-Exploitation-Module zu kombinieren.

**Hinweis:** Dieses Framework ist ausschließlich für Bildungs- und autorisierte Penetrationstests gedacht. Die Verwendung für illegale Aktivitäten ist strengstens untersagt.

## Installation

### Voraussetzungen

- Python 3.9+
- Kali Linux 2025 (empfohlen)
- Internetverbindung für Tool-Downloads und Updates

### Installationsschritte

1. Repository klonen:
   ```
   git clone https://github.com/username/chromsploit.git
   cd chromsploit
   ```

2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

3. Framework starten:
   ```
   python chromsploit.py
   ```

## Erste Schritte

Nach dem Start des Frameworks wird das Hauptmenü angezeigt. Von hier aus können Sie zu den verschiedenen Modulen und Funktionen navigieren.

### Tastenkombinationen

- `Strg+C`: Beenden des aktuellen Vorgangs
- `Strg+D`: Beenden des Frameworks
- `Tab`: Autovervollständigung (in einigen Menüs)

## Hauptmenü

Das Hauptmenü bietet Zugriff auf alle Funktionen des Frameworks:

1. **CVE-Exploits**: Zugriff auf implementierte CVE-Exploits
2. **Tool-Integrationen**: Zugriff auf integrierte Tools
3. **Post-Exploitation**: Zugriff auf Post-Exploitation-Module
4. **Live Monitoring**: Echtzeit-Überwachung von Logs und Systemressourcen
5. **Einstellungen**: Konfiguration des Frameworks
6. **Hilfe**: Anzeigen der Hilfe
7. **Beenden**: Beenden des Frameworks

## CVE-Exploits

### CVE-2025-4664 (Chrome Data Leak)

1. Navigieren Sie zu `CVE-Exploits > CVE-2025-4664`
2. Konfigurieren Sie die Exploit-Parameter:
   - Link-Header-Manipulation
   - WebSocket-Exfiltration
   - Ngrok-Tunnel (optional)
3. Generieren Sie den Payload
4. Führen Sie den Exploit aus

### CVE-2025-2783 (Chrome Mojo Sandbox Escape)

1. Navigieren Sie zu `CVE-Exploits > CVE-2025-2783`
2. Konfigurieren Sie die Exploit-Parameter:
   - Mojo IPC-Parameter
   - Fuzzing-Prozess
   - Post-Exploitation-Befehle
3. Generieren Sie den Payload
4. Führen Sie den Exploit aus

### CVE-2025-2857 (Firefox Sandbox Escape)

1. Navigieren Sie zu `CVE-Exploits > CVE-2025-2857`
2. Konfigurieren Sie die Exploit-Parameter:
   - IPDL Handle Confusion
   - DuplicateHandle()-Parameter
   - Privilege Escalation
3. Generieren Sie den Payload
4. Führen Sie den Exploit aus

### CVE-2025-30397 (Edge WebAssembly JIT Escape)

1. Navigieren Sie zu `CVE-Exploits > CVE-2025-30397`
2. Konfigurieren Sie die Exploit-Parameter:
   - TurboFan Compiler Parameter
   - WebAssembly.Table Growth
   - V8 Heap Corruption
3. Generieren Sie den Payload
4. Führen Sie den Exploit aus

## Tool-Integrationen

### Sliver C2 Framework

1. Navigieren Sie zu `Tool-Integrationen > Sliver C2`
2. Wählen Sie eine der folgenden Optionen:
   - Implant generieren
   - Listener starten
   - Sessions verwalten
   - Stager generieren

### Metasploit Framework

1. Navigieren Sie zu `Tool-Integrationen > Metasploit`
2. Wählen Sie eine der folgenden Optionen:
   - Payload generieren
   - Handler starten
   - Module ausführen

### OLLVM Obfuscation

1. Navigieren Sie zu `Tool-Integrationen > OLLVM`
2. Wählen Sie eine der folgenden Optionen:
   - C/C++-Code obfuskieren
   - Binärdatei obfuskieren
   - Shellcode generieren

### Ngrok Tunneling

1. Navigieren Sie zu `Tool-Integrationen > Ngrok`
2. Wählen Sie eine der folgenden Optionen:
   - Tunnel starten
   - Aktive Tunnel anzeigen
   - Tunnel konfigurieren
   - Tunnel stoppen

### Backdoor Factory

1. Navigieren Sie zu `Tool-Integrationen > Backdoor Factory`
2. Wählen Sie eine der folgenden Optionen:
   - Backdoor injizieren
   - Shellcode injizieren
   - Binärdatei analysieren
   - Signatur erhalten

## Post-Exploitation

### DefendNot (Windows Defender Bypass)

1. Navigieren Sie zu `Post-Exploitation > DefendNot`
2. Wählen Sie eine der folgenden Optionen:
   - Bypass-Script generieren
   - Oneliner generieren
   - Base64-Payload generieren

### WinPEAS (Privilege Escalation)

1. Navigieren Sie zu `Post-Exploitation > WinPEAS`
2. Wählen Sie eine der folgenden Optionen:
   - Neueste Version herunterladen
   - PowerShell-Oneliner generieren
   - Base64-Payload generieren
   - Memory-Execution-Befehl generieren
   - Obfuscated Version ausführen

## Live Monitoring

1. Navigieren Sie zu `Live Monitoring`
2. Wählen Sie eine der folgenden Optionen:
   - Logs anzeigen
   - Systeminformationen anzeigen
   - Debug-Einstellungen verwalten

### Log-Anzeige

- Filtern Sie Logs nach Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Filtern Sie Logs nach Inhalt
- Speichern Sie Logs in eine Datei

### Systeminformationen

- CPU-Auslastung
- Speicherauslastung
- Festplattenauslastung
- Netzwerkstatistik
- Prozesse

## Fehlerbehebung

### Häufige Probleme

1. **Framework startet nicht**
   - Überprüfen Sie die Python-Version (Python 3.9+ erforderlich)
   - Überprüfen Sie die installierten Abhängigkeiten
   - Überprüfen Sie die Berechtigungen

2. **Tool-Integration funktioniert nicht**
   - Überprüfen Sie, ob das Tool installiert ist
   - Überprüfen Sie die Netzwerkverbindung
   - Überprüfen Sie die Konfiguration

3. **Exploit funktioniert nicht**
   - Überprüfen Sie die Zielversion
   - Überprüfen Sie die Exploit-Parameter
   - Überprüfen Sie die Netzwerkverbindung

### Logs

Die Log-Dateien befinden sich im `logs/`-Verzeichnis. Sie können bei der Fehlerbehebung helfen.

## FAQ

### Allgemeine Fragen

**F: Ist das Framework legal?**
A: Das Framework selbst ist legal, aber die Verwendung zum Angreifen von Systemen ohne Genehmigung ist illegal. Verwenden Sie es nur für Bildungs- und autorisierte Penetrationstests.

**F: Kann ich eigene Exploits hinzufügen?**
A: Ja, das Framework ist modular aufgebaut und kann leicht erweitert werden. Siehe das Entwicklerhandbuch für Details.

**F: Funktioniert das Framework auf Windows/macOS?**
A: Das Framework ist primär für Kali Linux entwickelt, sollte aber auf den meisten Linux-Distributionen funktionieren. Windows und macOS werden nicht offiziell unterstützt.

### Technische Fragen

**F: Wie aktualisiere ich das Framework?**
A: Führen Sie `git pull` im Repository-Verzeichnis aus und installieren Sie ggf. neue Abhängigkeiten mit `pip install -r requirements.txt`.

**F: Wie kann ich die Ausgabe eines Exploits speichern?**
A: Die meisten Exploits speichern ihre Ausgabe automatisch im `output/`-Verzeichnis. Sie können auch die Logging-Funktion verwenden, um die Ausgabe in eine Datei zu schreiben.

**F: Wie kann ich einen Bug melden?**
A: Erstellen Sie ein Issue im GitHub-Repository mit einer detaillierten Beschreibung des Problems und Schritten zur Reproduktion.
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Benutzerhandbuch generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Benutzerhandbuchs: {str(e)}")
            return None
    
    def generate_developer_manual(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert ein Entwicklerhandbuch
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zum generierten Entwicklerhandbuch oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.docs_dir, "developer_manual.md")
        
        self.log("info", "Generiere Entwicklerhandbuch...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = """# ChromSploit Framework - Entwicklerhandbuch

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Architektur](#architektur)
3. [Entwicklungsumgebung](#entwicklungsumgebung)
4. [Codierungsrichtlinien](#codierungsrichtlinien)
5. [Module erweitern](#module-erweitern)
6. [CVE-Exploits hinzufügen](#cve-exploits-hinzufügen)
7. [Tool-Integrationen hinzufügen](#tool-integrationen-hinzufügen)
8. [Tests](#tests)
9. [Dokumentation](#dokumentation)
10. [Beitragsrichtlinien](#beitragsrichtlinien)

## Einführung

Dieses Handbuch richtet sich an Entwickler, die das ChromSploit Framework erweitern oder modifizieren möchten. Es bietet einen Überblick über die Architektur, Entwicklungsumgebung und Richtlinien für Beiträge.

## Architektur

Das ChromSploit Framework folgt einer modularen Architektur, die es ermöglicht, verschiedene Komponenten unabhängig voneinander zu entwickeln und zu erweitern.

### Hauptkomponenten

- **Core**: Kernkomponenten des Frameworks (Logger, Konfiguration, Utilities)
- **UI**: Benutzeroberflächen-Komponenten (Menüs, Dialoge)
- **Exploits**: CVE-spezifische Exploits und Payloads
- **Tools**: Integrationen mit externen Tools
- **Utils**: Hilfsfunktionen und -klassen

### Datenfluss

1. **Benutzereingabe**: Der Benutzer interagiert mit dem Menüsystem
2. **Menüsystem**: Verarbeitet die Benutzereingabe und ruft die entsprechenden Module auf
3. **Module**: Führen die gewünschten Aktionen aus und geben Ergebnisse zurück
4. **Logger**: Protokolliert alle Aktionen und Ergebnisse
5. **Ausgabe**: Ergebnisse werden dem Benutzer angezeigt oder in Dateien gespeichert

## Entwicklungsumgebung

### Voraussetzungen

- Python 3.9+
- Git
- Virtualenv (empfohlen)
- IDE mit Python-Unterstützung (VSCode, PyCharm, etc.)

### Einrichtung

1. Repository klonen:
   ```
   git clone https://github.com/username/chromsploit.git
   cd chromsploit
   ```

2. Virtuelle Umgebung erstellen und aktivieren:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate   # Windows
   ```

3. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

4. Entwicklungsabhängigkeiten installieren:
   ```
   pip install -r requirements-dev.txt
   ```

## Codierungsrichtlinien

### Allgemeine Richtlinien

- Folgen Sie PEP 8 für Python-Code
- Verwenden Sie aussagekräftige Variablen- und Funktionsnamen
- Kommentieren Sie komplexen Code
- Schreiben Sie Docstrings für alle Klassen und Funktionen
- Vermeiden Sie globale Variablen
- Behandeln Sie Fehler mit try-except-Blöcken

### Docstring-Format

Verwenden Sie das folgende Format für Docstrings:

```python
def function_name(param1, param2):
    """
    Kurze Beschreibung der Funktion
    
    Args:
        param1 (type): Beschreibung des Parameters
        param2 (type): Beschreibung des Parameters
        
    Returns:
        type: Beschreibung des Rückgabewerts
        
    Raises:
        ExceptionType: Beschreibung der Ausnahme
    """
    # Funktionsimplementierung
```

### Imports

Organisieren Sie Imports in der folgenden Reihenfolge:

1. Standardbibliotheken
2. Drittanbieterbibliotheken
3. Lokale Module

Beispiel:

```python
import os
import sys
import time

import requests
import psutil

from core.logger import Logger
from core.utils import Utils
```

## Module erweitern

### Neue Utility-Funktion hinzufügen

1. Öffnen Sie die entsprechende Utility-Datei (z.B. `core/utils.py`)
2. Fügen Sie Ihre Funktion mit Docstring hinzu
3. Aktualisieren Sie die Tests, falls vorhanden

Beispiel:

```python
def is_valid_ip(ip_address):
    """
    Überprüft, ob eine IP-Adresse gültig ist
    
    Args:
        ip_address (str): Die zu überprüfende IP-Adresse
        
    Returns:
        bool: True, wenn die IP-Adresse gültig ist, sonst False
    """
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    
    octets = ip_address.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True
```

### Neues Menü hinzufügen

1. Erstellen Sie eine neue Menü-Datei in `ui/` (z.B. `ui/new_menu.py`)
2. Implementieren Sie die Menüklasse
3. Fügen Sie das Menü zum Hauptmenü hinzu

Beispiel:

```python
class NewMenu:
    def __init__(self, logger=None):
        self.logger = logger
    
    def display(self):
        # Menü anzeigen
        print("=== Neues Menü ===")
        print("1. Option 1")
        print("2. Option 2")
        print("3. Zurück")
        
        choice = input("Wählen Sie eine Option: ")
        
        if choice == "1":
            self.option_1()
        elif choice == "2":
            self.option_2()
        elif choice == "3":
            return
        else:
            print("Ungültige Option")
        
        # Menü erneut anzeigen
        self.display()
    
    def option_1(self):
        # Implementierung von Option 1
        print("Option 1 ausgewählt")
    
    def option_2(self):
        # Implementierung von Option 2
        print("Option 2 ausgewählt")
```

## CVE-Exploits hinzufügen

### Neuen CVE-Exploit erstellen

1. Erstellen Sie ein neues Verzeichnis in `exploits/` (z.B. `exploits/cve_2025_xxxx/`)
2. Erstellen Sie die Hauptdatei für den Exploit (z.B. `exploits/cve_2025_xxxx/exploit.py`)
3. Erstellen Sie ein Verzeichnis für Templates (z.B. `exploits/cve_2025_xxxx/templates/`)
4. Implementieren Sie den Exploit
5. Fügen Sie den Exploit zum CVE-Menü hinzu

Beispiel:

```python
class CVE2025XXXX:
    def __init__(self, logger=None):
        self.logger = logger
        self.name = "CVE-2025-XXXX"
        self.description = "Beschreibung des Exploits"
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    def generate_payload(self, params):
        # Payload generieren
        payload = "..."
        
        # Payload in Datei schreiben
        output_dir = os.path.join(PathUtils.get_output_dir(), "cve_2025_xxxx")
        PathUtils.ensure_dir_exists(output_dir)
        output_file = os.path.join(output_dir, "payload.html")
        
        with open(output_file, "w") as f:
            f.write(payload)
        
        return output_file
    
    def run(self, params):
        # Exploit ausführen
        payload_file = self.generate_payload(params)
        
        # Weitere Aktionen
        
        return True
```

## Tool-Integrationen hinzufügen

### Neue Tool-Integration erstellen

1. Erstellen Sie eine neue Datei in `tools/` (z.B. `tools/new_tool_integration.py`)
2. Implementieren Sie die Integration
3. Fügen Sie die Integration zum Tool-Menü hinzu

Beispiel:

```python
class NewToolIntegration:
    def __init__(self, logger=None):
        self.logger = logger
        self.tool_path = "/path/to/tool"
    
    def is_available(self):
        # Überprüfen, ob das Tool verfügbar ist
        return os.path.exists(self.tool_path)
    
    def install(self):
        # Tool installieren
        # ...
        return True
    
    def run(self, params):
        # Tool ausführen
        # ...
        return True
```

## Tests

### Unit-Tests

Unit-Tests befinden sich im `tests/`-Verzeichnis. Verwenden Sie das `unittest`-Framework für Tests.

Beispiel:

```python
import unittest
from core.utils import Utils

class TestUtils(unittest.TestCase):
    def test_is_valid_ip(self):
        self.assertTrue(Utils.is_valid_ip("192.168.1.1"))
        self.assertTrue(Utils.is_valid_ip("10.0.0.1"))
        self.assertFalse(Utils.is_valid_ip("256.0.0.1"))
        self.assertFalse(Utils.is_valid_ip("192.168.1"))
        self.assertFalse(Utils.is_valid_ip("192.168.1.1.1"))

if __name__ == "__main__":
    unittest.main()
```

### Tests ausführen

```
python -m unittest discover tests
```

## Dokumentation

### Code-Dokumentation

- Schreiben Sie Docstrings für alle Klassen und Funktionen
- Kommentieren Sie komplexen Code
- Halten Sie die Dokumentation aktuell

### Externe Dokumentation

- Aktualisieren Sie die README.md
- Aktualisieren Sie das Benutzerhandbuch
- Aktualisieren Sie das Entwicklerhandbuch
- Dokumentieren Sie neue Funktionen und Änderungen

## Beitragsrichtlinien

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/neue-funktion`)
3. Committen Sie Ihre Änderungen (`git commit -am 'Neue Funktion hinzugefügt'`)
4. Pushen Sie den Branch (`git push origin feature/neue-funktion`)
5. Erstellen Sie einen Pull Request

### Commit-Nachrichten

Verwenden Sie aussagekräftige Commit-Nachrichten im folgenden Format:

```
Kurze Zusammenfassung (max. 50 Zeichen)

Detaillierte Beschreibung der Änderungen (optional)
```

### Code-Review

Alle Pull Requests werden einem Code-Review unterzogen. Stellen Sie sicher, dass Ihr Code:

- Den Codierungsrichtlinien entspricht
- Dokumentiert ist
- Tests enthält
- Keine Sicherheitslücken enthält
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"Entwicklerhandbuch generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des Entwicklerhandbuchs: {str(e)}")
            return None
    
    def generate_cve_descriptions(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine Dokumentation der CVE-Beschreibungen
        
        Args:
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten Dokumentation oder None bei Fehler
        """
        if not output_file:
            output_file = os.path.join(self.docs_dir, "cve_descriptions.md")
        
        self.log("info", "Generiere CVE-Beschreibungen...")
        
        try:
            # Markdown-Dokumentation erstellen
            content = """# ChromSploit Framework - CVE-Beschreibungen

## Übersicht

Diese Dokumentation beschreibt die im ChromSploit Framework implementierten CVEs (Common Vulnerabilities and Exposures).

## CVE-2025-4664 (Chrome Data Leak)

### Beschreibung

CVE-2025-4664 ist eine Schwachstelle im Chrome-Browser, die es einem Angreifer ermöglicht, sensible Daten durch Manipulation von Link-Headern zu exfiltrieren.

### Technische Details

Die Schwachstelle basiert auf einer fehlerhaften Implementierung der Referrer-Policy in Chrome. Durch Manipulation des `referrerpolicy=unsafe-url`-Headers kann ein Angreifer dazu führen, dass der Browser sensible Daten an einen vom Angreifer kontrollierten Server sendet.

### Exploit-Methode

1. **Link-Header-Manipulation**: Der Angreifer erstellt eine HTML-Seite mit manipulierten Link-Headern.
2. **WebSocket-Exfiltration**: Die Seite öffnet eine WebSocket-Verbindung zu einem vom Angreifer kontrollierten Server.
3. **Datenexfiltration**: Sensible Daten werden über die WebSocket-Verbindung an den Angreifer gesendet.

### Betroffene Versionen

- Chrome 120.0.0.0 - 125.0.0.0

### Gegenmaßnahmen

- Aktualisieren Sie Chrome auf die neueste Version
- Verwenden Sie eine sichere Referrer-Policy
- Blockieren Sie unbekannte WebSocket-Verbindungen

## CVE-2025-2783 (Chrome Mojo Sandbox Escape)

### Beschreibung

CVE-2025-2783 ist eine Schwachstelle im Chrome-Browser, die es einem Angreifer ermöglicht, aus der Sandbox auszubrechen und Code mit höheren Rechten auszuführen.

### Technische Details

Die Schwachstelle basiert auf einem Fehler in der Mojo IPC-Implementierung von Chrome. Durch Fuzzing von Mojo IPC-Nachrichten mit einem speziellen 0xBADCOFFEE-Header kann ein Angreifer einen Windows Handle Validation Bypass auslösen und aus der Sandbox ausbrechen.

### Exploit-Methode

1. **Mojo IPC Message Fuzzing**: Der Angreifer sendet speziell gestaltete Mojo IPC-Nachrichten an den Browser.
2. **Windows Handle Validation Bypass**: Durch den Fehler in der Validierung kann der Angreifer auf Handles außerhalb der Sandbox zugreifen.
3. **Post-Exploitation**: Nach dem Ausbruch aus der Sandbox kann der Angreifer Code mit höheren Rechten ausführen.

### Betroffene Versionen

- Chrome 122.0.0.0 - 126.0.0.0

### Gegenmaßnahmen

- Aktualisieren Sie Chrome auf die neueste Version
- Aktivieren Sie die Site Isolation
- Verwenden Sie eine Sandbox-Lösung auf Betriebssystemebene

## CVE-2025-2857 (Firefox Sandbox Escape)

### Beschreibung

CVE-2025-2857 ist eine Schwachstelle im Firefox-Browser, die es einem Angreifer ermöglicht, aus der Sandbox auszubrechen und Code mit höheren Rechten auszuführen.

### Technische Details

Die Schwachstelle basiert auf einem Fehler in der IPDL (Inter-Process Communication Definition Language) Handle-Validierung von Firefox. Durch Ausnutzung einer Handle Confusion kann ein Angreifer DuplicateHandle() missbrauchen und PROCESS_ALL_ACCESS-Rechte erlangen.

### Exploit-Methode

1. **IPDL Handle Confusion**: Der Angreifer erzeugt eine Handle Confusion durch speziell gestaltete IPDL-Nachrichten.
2. **DuplicateHandle() Abuse**: Durch den Fehler in der Validierung kann der Angreifer DuplicateHandle() missbrauchen.
3. **Privilege Escalation**: Der Angreifer erlangt PROCESS_ALL_ACCESS-Rechte und kann Code mit höheren Rechten ausführen.

### Betroffene Versionen

- Firefox 115.0.0 - 120.0.0

### Gegenmaßnahmen

- Aktualisieren Sie Firefox auf die neueste Version
- Aktivieren Sie die Content Process Isolation
- Verwenden Sie eine Sandbox-Lösung auf Betriebssystemebene

## CVE-2025-30397 (Edge WebAssembly JIT Escape)

### Beschreibung

CVE-2025-30397 ist eine Schwachstelle im Edge-Browser, die es einem Angreifer ermöglicht, durch Ausnutzung des WebAssembly JIT-Compilers aus der Sandbox auszubrechen.

### Technische Details

Die Schwachstelle basiert auf einem Fehler im TurboFan-Compiler von V8, der in Edge verwendet wird. Durch einen Bounds Check Bypass in Kombination mit WebAssembly.Table Growth kann ein Angreifer eine V8 Heap Corruption auslösen und einen ROP-Chain ausführen, der SMEP/SMAP umgeht.

### Exploit-Methode

1. **TurboFan Compiler Bounds Check Bypass**: Der Angreifer nutzt einen Fehler im Bounds-Checking des TurboFan-Compilers aus.
2. **WebAssembly.Table Growth Exploitation**: Durch Manipulation der WebAssembly.Table-Größe kann der Angreifer eine Heap-Korruption auslösen.
3. **V8 Heap Corruption**: Der Angreifer korruptiert den V8-Heap durch einen Out-of-Bounds-Zugriff auf einen ArrayBuffer.
4. **ROP Chain Execution**: Der Angreifer führt einen ROP-Chain aus, der SMEP/SMAP umgeht und Code mit höheren Rechten ausführt.

### Betroffene Versionen

- Edge 110.0.0.0 - 115.0.0.0

### Gegenmaßnahmen

- Aktualisieren Sie Edge auf die neueste Version
- Deaktivieren Sie WebAssembly, wenn nicht benötigt
- Verwenden Sie eine Sandbox-Lösung auf Betriebssystemebene
"""
            
            # Dokumentation in Datei schreiben
            with open(output_file, "w") as f:
                f.write(content)
            
            self.log("info", f"CVE-Beschreibungen generiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der CVE-Beschreibungen: {str(e)}")
            return None
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """
        Generiert alle Dokumentationen
        
        Returns:
            dict: Dictionary mit Pfaden zu allen generierten Dokumentationen
        """
        self.log("info", "Generiere alle Dokumentationen...")
        
        docs = {}
        
        # Verzeichnisstruktur
        dir_structure = self.generate_directory_structure()
        if dir_structure:
            docs["directory_structure"] = dir_structure
        
        # Code-Dokumentation
        code_doc = self.generate_code_documentation()
        if code_doc:
            docs["code_documentation"] = code_doc
        
        # Workflow-Dokumentation
        workflow_doc = self.generate_workflow_documentation()
        if workflow_doc:
            docs["workflow_documentation"] = workflow_doc
        
        # Work Breakdown Structure
        wbs = self.generate_work_breakdown_structure()
        if wbs:
            docs["work_breakdown_structure"] = wbs
        
        # README
        readme = self.generate_readme()
        if readme:
            docs["readme"] = readme
        
        # Benutzerhandbuch
        user_manual = self.generate_user_manual()
        if user_manual:
            docs["user_manual"] = user_manual
        
        # Entwicklerhandbuch
        dev_manual = self.generate_developer_manual()
        if dev_manual:
            docs["developer_manual"] = dev_manual
        
        # CVE-Beschreibungen
        cve_desc = self.generate_cve_descriptions()
        if cve_desc:
            docs["cve_descriptions"] = cve_desc
        
        self.log("info", f"Alle Dokumentationen generiert: {len(docs)} Dokumente")
        return docs
    
    def generate_pdf_documentation(self, markdown_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generiert eine PDF-Dokumentation aus einer Markdown-Datei
        
        Args:
            markdown_file (str): Pfad zur Markdown-Datei
            output_file (str, optional): Pfad zur Ausgabedatei
            
        Returns:
            str: Pfad zur generierten PDF-Dokumentation oder None bei Fehler
        """
        if not os.path.exists(markdown_file):
            self.log("error", f"Markdown-Datei existiert nicht: {markdown_file}")
            return None
        
        if not output_file:
            base_name = os.path.basename(markdown_file)
            name, _ = os.path.splitext(base_name)
            output_file = os.path.join(self.output_dir, f"{name}.pdf")
        
        self.log("info", f"Generiere PDF-Dokumentation aus {markdown_file}...")
        
        try:
            # Markdown zu PDF konvertieren
            cmd = f"manus-md-to-pdf {markdown_file} {output_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("info", f"PDF-Dokumentation generiert: {output_file}")
                return output_file
            else:
                self.log("error", f"Fehler beim Generieren der PDF-Dokumentation: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Generieren der PDF-Dokumentation: {str(e)}")
            return None
