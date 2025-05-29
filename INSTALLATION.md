# 🚀 ChromSploit Framework - Installation Guide

## 📋 System Requirements

### **Für Kali Linux (Empfohlen)**
Die meisten Abhängigkeiten sind bereits vorinstalliert. Zusätzlich benötigt:

```bash
# Python 3.8+ und pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Git (falls nicht vorhanden)
sudo apt install git

# Zusätzliche System-Tools
sudo apt install curl wget netcat-traditional

# Optional aber empfohlen
sudo apt install asciinema tmux
```

### **Für Debian/Ubuntu**
Vollständige Installation aller benötigten Pakete:

```bash
# System Update
sudo apt update && sudo apt upgrade -y

# Python und Entwicklungstools
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Git und Versionskontrolle
sudo apt install -y git

# Netzwerk-Tools
sudo apt install -y curl wget netcat-traditional nmap dnsutils

# System-Tools
sudo apt install -y tmux screen htop

# Optional: Terminal Recording
sudo apt install -y asciinema

# Optional: Metasploit (für Integration)
# curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
# chmod 755 msfinstall && ./msfinstall

# Optional: Go (für Sliver C2)
# sudo apt install -y golang-go
```

## 🛠️ Installation ChromSploit Framework

### **1. Entpacken des Archives**
```bash
# Archive entpacken
tar -xzf ChromSploit-Framework.tar.gz
cd ChromSploit-Framework/
```

### **2. Python Virtual Environment erstellen**
```bash
# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### **3. Dependencies installieren**
```bash
# Basis-Dependencies
pip install -r requirements.txt

# Development Dependencies (optional)
pip install -r requirements-dev.txt

# Optional Features (falls gewünscht)
pip install -r requirements-optional.txt
```

### **4. Framework Setup**
```bash
# Berechtigungen setzen
chmod +x chromsploit.py
chmod +x asciinema/*.sh

# Konfiguration prüfen
python3 chromsploit.py --check
```

## 🔧 Konfiguration

### **Basis-Konfiguration**
Die Standardkonfiguration funktioniert out-of-the-box. Anpassungen in:
- `config/user_config.json` - Persönliche Einstellungen
- `config/kali_defaults.ini` - Kali-spezifische Pfade

### **Wichtige Einstellungen**
```json
{
  "general": {
    "debug_mode": false,
    "simulation_mode": "safe"  // safe, demo, fast, off
  },
  "network": {
    "default_interface": "eth0",
    "callback_ip": "YOUR_IP_HERE"
  }
}
```

## 🚀 Erster Start

### **1. Framework starten**
```bash
# Normaler Start
python3 chromsploit.py

# Mit Debug-Ausgabe
python3 chromsploit.py --debug

# Nur Simulation (sicher)
python3 chromsploit.py --simulation safe

# Hilfe anzeigen
python3 chromsploit.py --help
```

### **2. Erste Schritte**
1. **Hauptmenü** - Übersicht aller Module
2. **CVE Exploits** - Verfügbare Exploits testen
3. **Settings** - Konfiguration anpassen
4. **Help** - Integrierte Dokumentation

## 🧪 Test-Empfehlungen

### **Sichere Tests (Simulation Mode)**
```bash
# Simulation Mode aktivieren
python3 chromsploit.py --simulation safe

# Dann im Menü:
# 1. CVE Exploits -> Test einzelne Module
# 2. Reporting -> Generiere Test-Reports
# 3. Monitoring -> Live View aktivieren
```

### **Lokale Tests (Vorsicht!)**
```bash
# NUR in isolierter Testumgebung!
# 1. Eigenen Webserver starten
python3 -m http.server 8080

# 2. ChromSploit mit lokalem Target
# CVE Exploits -> Target: localhost:8080
```

## ⚠️ Sicherheitshinweise

### **WICHTIG: Nur für autorisierte Tests verwenden!**

1. **Testumgebung**: Verwenden Sie eine isolierte VM oder Lab-Umgebung
2. **Netzwerk**: Testen Sie niemals gegen fremde Systeme
3. **Simulation**: Nutzen Sie primär den Simulation Mode
4. **Logging**: Alle Aktionen werden protokolliert

### **Empfohlene Testumgebung**
```
Kali VM (ChromSploit) <---> Target VM (Vulnerable Apps)
         |
         +-- Isoliertes Netzwerk (keine Internet-Verbindung)
```

## 🐛 Troubleshooting

### **Python-Module fehlen**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Permission Errors**
```bash
# Scripts ausführbar machen
find . -name "*.py" -exec chmod +x {} \;
find . -name "*.sh" -exec chmod +x {} \;
```

### **Import Errors**
```bash
# Python Path setzen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Git nicht installiert (für CVE-2024-32002)**
```bash
sudo apt install git
```

## 📦 Optionale Features

### **Sliver C2 Integration**
```bash
# Sliver installieren (optional)
curl https://sliver.sh/install|bash

# In ChromSploit aktivieren
# Main Menu -> Optional Modules -> Sliver C2
```

### **Metasploit Integration**
```bash
# MSF muss installiert sein
# Main Menu -> Tools -> Metasploit Integration
```

### **Asciinema Recordings**
```bash
# Demos anschauen
cd asciinema/
asciinema play chromsploit_complete_demo.cast
```

## 🔍 Komponenten-Check

### **Verfügbare Module prüfen**
```bash
# Module auflisten
ls modules/

# Exploits prüfen
ls exploits/

# UI-Komponenten
ls ui/
```

### **Logs prüfen**
```bash
# Log-Verzeichnis
ls logs/

# Aktuelles Log
tail -f logs/chromsploit_*.log
```

## 📚 Weitere Dokumentation

- `README.md` - Projekt-Übersicht
- `docs/HOW_TO_USE.md` - Detaillierte Anleitung
- `docs/API_REFERENCE.md` - API-Dokumentation
- `docs/ARCHITECTURE.md` - System-Architektur
- `CLAUDE.md` - AI-Assistant Guidelines

## 💡 Quick Tips

1. **Starten Sie immer im Simulation Mode** für erste Tests
2. **Lesen Sie die Logs** für detaillierte Informationen
3. **Nutzen Sie die Help-Funktion** im Menü
4. **Testen Sie einzelne Module** bevor Sie Chains verwenden
5. **Dokumentieren Sie Ihre Tests** mit dem Reporting-Modul

---

## ✅ Installation Complete!

Nach erfolgreicher Installation:
```bash
python3 chromsploit.py
```

**Willkommen bei ChromSploit Framework! 🚀**

*Professional Security Research Platform*