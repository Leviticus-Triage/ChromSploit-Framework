# ChromSploit Framework - Asciinema Demos

 **Professional Terminal Recordings for GitHub Repository**

Diese Sammlung enthält hochwertige asciinema-Aufnahmen, die verschiedene Aspekte des ChromSploit Frameworks demonstrieren.

## Verfügbare Aufnahmen

### Vollständige Demo
- **`chromsploit_complete_demo.cast`** - Komplette Demonstration (106 Sekunden)
 - Alle Funktionen in einer zusammenhängenden Präsentation
 - Perfekt für GitHub README und Projektübersicht

### Einzelne Module

| Aufnahme | Beschreibung | Dauer | Highlights |
|----------|--------------|-------|------------|
| `01_framework_startup.cast` | Framework-Start & Einführung | ~13s | Grundlagen, Hilfe-System |
| `02_cve_exploits.cast` | CVE-Exploit Module | ~15s | 6 verschiedene CVE-Exploits |
| `03_advanced_features.cast` | Erweiterte Features | ~18s | AI, Monitoring, Obfuscation |
| `04_exploit_execution.cast` | CVE-2025-2783 Demo | ~22s | Mojo IPC Sandbox Escape |
| `05_wasm_jit.cast` | WebAssembly JIT Exploit | ~25s | Edge WASM Type Confusion |
| `06_tomcat_rce.cast` | Apache Tomcat RCE | ~23s | WAR-Deployment, RCE |
| `07_git_rce.cast` | Git RCE Demo | ~26s | Symbolic Links, Hooks |
| `08_framework_features.cast` | Feature-Übersicht | ~24s | Vollständige Capabilities |

## Verwendung

### Für GitHub Repository

1. **Einbettung in README.md:**
```markdown
[![asciicast](https://asciinema.org/a/YOUR_UPLOAD_ID.svg)](https://asciinema.org/a/YOUR_UPLOAD_ID)
```

2. **Upload zu asciinema.org:**
```bash
asciinema upload chromsploit_complete_demo.cast
```

3. **Lokale Wiedergabe:**
```bash
asciinema play chromsploit_complete_demo.cast
```

### Für Präsentationen

- **Einzelne Module:** Verwenden Sie spezifische .cast-Dateien
- **Vollständige Demo:** Nutzen Sie die kombinierte Version
- **Interactive Demos:** Asciinema Server für Live-Präsentationen

## Technische Details

### Aufnahme-Spezifikationen
- **Terminal:** xterm-256color
- **Auflösung:** 80x24 (Standard)
- **Format:** Asciinema v2
- **Encoding:** UTF-8

### Inhaltliche Highlights

#### Framework-Features
- 6 Advanced CVE Exploits mit echtem Code
- AI-gestützte Exploit-Orchestrierung
- Live-Monitoring & Dashboards
- Payload-Obfuscation & Anti-Analysis
- Self-Healing & Resilience
- Professionelle Security Reports

#### CVE-Exploit Demos
- **CVE-2025-2783:** Chrome Mojo IPC Sandbox Escape
- **CVE-2025-30397:** Edge WebAssembly JIT Type Confusion
- **CVE-2025-24813:** Apache Tomcat RCE
- **CVE-2024-32002:** Git RCE via Symbolic Links
- **CVE-2025-4664:** Chrome Link Header Policy
- **CVE-2025-2857:** Chrome OAuth Exploitation

## Statistiken

```
Gesamt-Aufnahmezeit: 106.28 Sekunden
Einzelne Events: 366
Aufnahme-Dateien: 8 + 1 kombiniert
Demonstrierte Features: 50+
CVE-Exploits gezeigt: 6
```

##  Erstellung & Bearbeitung

### Neue Aufnahmen erstellen
```bash
# Einzelne Aufnahme
asciinema rec new_demo.cast -t "Demo Title"

# Mit dem bereitgestellten Skript
./record_intro.sh
```

### Aufnahmen bearbeiten
```bash
# Zusammenfügen
python3 concat_recordings.py

# Trimmen/Bearbeiten (externe Tools)
# Empfohlen: asciinema-edit, terminalizer
```

## Zielgruppe

### Für Entwickler
- **Repository-Besucher:** Schneller Überblick über Capabilities
- **Potentielle Contributors:** Verständnis der Architektur
- **Security Researchers:** Demonstration der Exploit-Techniken

### Für Bildung
- **Cybersecurity-Kurse:** Praktische Demonstration
- **Penetration Testing:** Methodologie und Tools
- **Vulnerability Research:** Exploit-Entwicklung

## Metadata

### Playlist-Information
Die `playlist.json` enthält strukturierte Metadaten:
```json
{
 "title": "ChromSploit Framework Demo Playlist",
 "description": "Complete demonstration of ChromSploit Framework capabilities",
 "recordings": [...]
}
```

### Tags für asciinema.org
- `cybersecurity`
- `penetration-testing`
- `vulnerability-research`
- `exploit-development`
- `educational`
- `chrome-exploits`
- `security-testing`

## Ethische Nutzung

 **Wichtiger Hinweis:** Diese Demos dienen ausschließlich:
- **Autorisierte Penetration Tests**
- **Cybersecurity-Bildung**
- **Vulnerability Research**
- **Security Awareness Training**

## Support

Bei Fragen zu den Aufnahmen oder dem Framework:
- GitHub Issues im Hauptrepository
- Dokumentation in `/docs`
- Community-Support verfügbar

---

**ChromSploit Framework** - Professional Security Research Platform 
 *Demonstriert mit professionellen asciinema-Aufnahmen*