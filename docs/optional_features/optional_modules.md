# ChromSploit Framework v3.0 - Optionale Module

## Übersicht

Diese Dokumentation beschreibt die optionalen KI- und Resilienz-Module des ChromSploit Frameworks v3.0. Diese Module erweitern die Funktionalität des Frameworks, sind aber nicht für den Kernbetrieb erforderlich.

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Installation](#installation)
3. [KI-Modul](#ki-modul)
4. [Resilienz-Modul](#resilienz-modul)
5. [Konfiguration](#konfiguration)
6. [Fallback-Mechanismen](#fallback-mechanismen)
7. [Integration mit dem Hauptframework](#integration-mit-dem-hauptframework)
8. [Fehlerbehebung](#fehlerbehebung)

## Einführung

ChromSploit v3.0 führt zwei neue optionale Module ein:

1. **KI-Modul**: Eine hybride KI-Entscheidungsengine mit Echtzeit-Inferenz und Multi-Modell-Architektur
2. **Resilienz-Modul**: Selbstheilende Infrastrukturkomponenten mit Circuit Breaker und Fallback-Mechanismen

Diese Module können unabhängig voneinander aktiviert oder deaktiviert werden, ohne die Kernfunktionalität des Frameworks zu beeinträchtigen.

## Installation

### Voraussetzungen

#### KI-Modul
- Python 3.9+
- PyTorch 2.3.1+
- ONNX Runtime 1.17.0+
- XGBoost 2.1.0+
- Transformers 4.40.0+

#### Resilienz-Modul
- Python 3.9+
- PyBreaker
- psutil

### Installationsschritte

1. Installieren Sie die Abhängigkeiten für die optionalen Module:

```bash
pip install -r requirements-optional.txt
```

2. Aktivieren Sie die Module über das Menü:

```
ChromSploit Framework > Optionale Module > [1-2]
```

3. Oder aktivieren Sie die Module in der Konfigurationsdatei:

```ini
[ai]
enable = true

[resilience]
enable = true
```

## KI-Modul

### Übersicht

Das KI-Modul bietet eine intelligente Entscheidungsengine für die Auswahl von Exploits, Payloads und Obfuskierungstechniken basierend auf Zielcharakteristiken.

### Komponenten

- **AIOrchestrator**: Hauptklasse für die KI-Entscheidungsfindung
- **Hybridmodelle**: Kombination aus BERT, XGBoost und ONNX-Modellen
- **Feedback-Loop**: Selbstlernender Mechanismus zur Verbesserung der Empfehlungen

### Funktionen

- **Zielanalyse**: Analyse von Zielsystemen und Empfehlung geeigneter Exploits
- **Payload-Auswahl**: Intelligente Auswahl von Payloads basierend auf Zielcharakteristiken
- **Obfuskierungsempfehlungen**: Empfehlungen für Obfuskierungstechniken basierend auf Zielumgebung

### Verwendung

```python
from modules.ai.ai_orchestrator_v2 import AIOrchestrator

# AIOrchestrator initialisieren
orchestrator = AIOrchestrator()

# Zieldaten definieren
target_data = {
    "browser": "chrome",
    "os_type": "windows",
    "version": "125.0.0.0",
    "description": "Windows 10 mit Chrome Browser"
}

# Ziel analysieren
results = orchestrator.analyze_target(target_data)

# Exploit empfehlen
recommended_exploit = orchestrator.recommend_exploit(target_data)
```

## Resilienz-Modul

### Übersicht

Das Resilienz-Modul bietet selbstheilende Infrastrukturkomponenten, die die Zuverlässigkeit des Frameworks verbessern und automatisch auf Fehler reagieren.

### Komponenten

- **CircuitBreaker**: Verhindert wiederholte Fehler durch temporäre Deaktivierung fehlerhafter Komponenten
- **ServiceMonitor**: Überwacht und verwaltet Dienste
- **NetworkResilience**: Bietet Netzwerk-Resilienz-Funktionen mit Fallback-Endpunkten
- **ResourceMonitor**: Überwacht Systemressourcen und führt Aktionen bei Überlastung aus
- **SelfHealingSystem**: Kombiniert alle Resilienz-Komponenten

### Funktionen

- **Dienst-Überwachung**: Automatische Überwachung und Neustart von Diensten
- **Endpunkt-Fallback**: Automatischer Wechsel zu Fallback-Endpunkten bei Verbindungsproblemen
- **Ressourcen-Überwachung**: Überwachung von CPU, Speicher und Festplatte mit konfigurierbaren Schwellenwerten

### Verwendung

```python
from modules.resilience.resilience_module import SelfHealingSystem

# SelfHealingSystem initialisieren
healing_system = SelfHealingSystem()

# Dienst registrieren
healing_system.register_service(
    "ngrok",
    check_func=lambda: check_ngrok_running(),
    restart_func=lambda: restart_ngrok(),
    check_interval=30
)

# Endpunkt registrieren
healing_system.register_endpoint(
    "sliver",
    "127.0.0.1:31337",
    ["127.0.0.1:8888", "127.0.0.1:9999"]
)

# System starten
healing_system.start()
```

## Konfiguration

Die Konfiguration der optionalen Module erfolgt über die Datei `config/kali_defaults.ini`:

```ini
[ai]
enable = false
model_path = /opt/chromsploit/models
fallback_strategy = legacy_cve_matcher

[resilience]
enable = false
cpu_threshold = 90.0
memory_threshold = 90.0
disk_threshold = 90.0
service_check_interval = 30

[sliver]
primary_endpoint = 127.0.0.1:31337
fallback_endpoints = 127.0.0.1:8888,127.0.0.1:9999

[metasploit]
primary_endpoint = 127.0.0.1:4444
fallback_endpoints = 127.0.0.1:5555,127.0.0.1:6666

[ngrok]
authtoken = YOUR_KALI_NGROK_TOKEN
region = eu
tunnel_rotation = 900

[ollvm]
docker_image = kali/ollvm:2025.1
compiler_path = /opt/ollvm/bin/clang++
```

## Fallback-Mechanismen

Das Framework implementiert verschiedene Fallback-Mechanismen, um die Zuverlässigkeit zu gewährleisten:

1. **AI-Modul deaktiviert → Legacy CVE-Matcher**
   - Wenn das KI-Modul nicht verfügbar ist, wird automatisch auf den Legacy-CVE-Matcher zurückgegriffen

2. **Ngrok nicht installiert → Lokaler Listener**
   - Wenn Ngrok nicht verfügbar ist, wird automatisch ein lokaler Listener verwendet

3. **OLLVM fehlgeschlagen → XOR-Obfuscation**
   - Wenn OLLVM nicht verfügbar ist, wird automatisch auf XOR-Obfuskierung zurückgegriffen

4. **Sliver nicht verfügbar → Metasploit-Fallback**
   - Wenn Sliver nicht verfügbar ist, wird automatisch auf Metasploit zurückgegriffen

## Integration mit dem Hauptframework

Die optionalen Module sind vollständig in das Hauptframework integriert:

1. **Modul-Loader**: Lädt optionale Module basierend auf Verfügbarkeit und Konfiguration
2. **Menüsystem**: Ermöglicht die Aktivierung/Deaktivierung der Module über die Benutzeroberfläche
3. **Konfigurationssystem**: Speichert den Status der optionalen Module
4. **Logging-System**: Protokolliert Aktivitäten der optionalen Module

## Fehlerbehebung

### KI-Modul

| Problem | Lösung |
|---------|--------|
| Modul wird nicht geladen | Überprüfen Sie die Installation der Abhängigkeiten mit `pip list \| grep torch` |
| Langsame Inferenz | Reduzieren Sie die Modellgröße oder verwenden Sie GPU-Beschleunigung |
| Falsche Empfehlungen | Aktualisieren Sie die Modelle oder verwenden Sie den Legacy-CVE-Matcher |

### Resilienz-Modul

| Problem | Lösung |
|---------|--------|
| Modul wird nicht geladen | Überprüfen Sie die Installation der Abhängigkeiten mit `pip list \| grep pybreaker` |
| Dienste werden nicht überwacht | Überprüfen Sie die Registrierung der Dienste und die Berechtigungen |
| Endpunkt-Fallback funktioniert nicht | Überprüfen Sie die Konfiguration der Fallback-Endpunkte |
