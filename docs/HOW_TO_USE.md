# ChromSploit Framework v3.0 - Benutzeranleitung

## Schnellstart

### Installation und Start

1. **Framework starten**:
```bash
python chromsploit.py
```

2. **Mit Simulationsmodus** (empfohlen für Tests):
```bash
python chromsploit.py --simulation safe
```

3. **Mit Debug-Modus**:
```bash
python chromsploit.py --debug
```

## Feature-Anleitungen

### 1. Module Loader System

Das Module Loader System lädt Module dynamisch und verwaltet Abhängigkeiten automatisch.

**Verwendung**:
- Module werden automatisch beim Start gescannt
- Fehlende Abhängigkeiten werden durch Fallback-Handler ersetzt
- Keine manuelle Konfiguration erforderlich

### 2. Exploit Chain Management

**Schritte zur Erstellung einer Exploit-Chain**:

1. Hauptmenü → " Exploitation Chains"
2. Wähle "Create New Chain"
3. Optionen:
 - **Manual Creation**: Schritt für Schritt konfigurieren
 - **AI-Assisted**: KI analysiert Ziel und schlägt Chain vor
 - **From Template**: Vordefinierte Chains verwenden

**Beispiel einer Chain**:
```
1. Reconnaissance (CVE-2025-4664) → Daten sammeln
2. Initial Access (OAuth Exploit) → Zugang erhalten 
3. Privilege Escalation (CVE-2025-2783) → Rechte erweitern
4. Persistence (Custom Payload) → Zugang sichern
```

### 3. AI Orchestrator

**KI-gestützte Exploit-Auswahl**:

1. Hauptmenü → " Exploitation Chains" → "AI-Assisted Chain"
2. Zielinformationen eingeben:
 - Browser-Typ und Version
 - Betriebssystem
 - Bekannte Schwachstellen
3. KI analysiert und empfiehlt optimale Exploit-Kombination

**Fallback-Modus**:
Falls ML-Bibliotheken nicht verfügbar, nutzt das System regelbasierte Auswahl.

### 4. Resilience & Self-Healing

**System-Gesundheit überwachen**:

1. Hauptmenü → "Resilience & Self-Healing"
2. Optionen:
 - **System Health Status**: Aktueller Zustand aller Komponenten
 - **Start Monitoring**: Automatische Überwachung aktivieren
 - **Self-Healing System**: Proaktive Heilung aktivieren

**Komponenten-Status**:
- **Healthy**: Komponente funktioniert normal
- **Degraded**: Teilweise Probleme
- **Failed**: Komponente ausgefallen
- **Recovering**: Wiederherstellung läuft

### 5. Enhanced Obfuscation

**JavaScript obfuskieren**:

1. Hauptmenü → "Enhanced Obfuscation"
2. "Obfuscate JavaScript"
3. Code eingeben oder Datei laden
4. Obfuskierungslevel wählen:
 - **MINIMAL**: Basis-Obfuskierung
 - **STANDARD**: Empfohlenes Level
 - **AGGRESSIVE**: Starke Obfuskierung
 - **MAXIMUM**: Maximale Obfuskierung

**Multi-Stage Payloads**:
- Erstelle mehrstufige Payloads mit steigender Obfuskierung
- Jede Stufe wird separat obfuskiert und zeitversetzt ausgeführt

### 6. Live Monitoring

**Terminal-Monitoring**:

1. Hauptmenü → "Live Monitoring"
2. "Terminal Display"
3. Tastenkombinationen:
 - `q`: Beenden
 - `s`: Statistiken ein/aus
 - `c`: Events löschen
 - `f`: Filter setzen

**Web Dashboard**:

1. "Web Dashboard" wählen
2. Browser öffnet automatisch: http://localhost:8889
3. Features:
 - Echtzeit-Statistiken
 - Event-Timeline
 - Filterbare Event-Liste

**Alerts konfigurieren**:
```
1. "Alert Configuration"
2. "Add Alert"
3. Bedingungen definieren:
 - Event-Typ (z.B. EXPLOIT_SUCCESS)
 - Mindest-Priorität
 - Nachrichteninhalt
```

### 7. Exploit-Ausführung

**Einzelnen Exploit ausführen**:

1. Wähle CVE aus Hauptmenü (z.B. "CVE-2025-4664")
2. Ziel-URL eingeben
3. Parameter konfigurieren
4. "Execute Exploit" wählen

**Sicherheitshinweise**:
-  Nur auf eigenen Systemen oder mit Erlaubnis verwenden
-  Simulationsmodus für Tests nutzen
- Alle Aktionen werden geloggt

##  Erweiterte Funktionen

### Validation Framework

**Tests ausführen**:
```bash
# Aus dem Framework heraus
Hauptmenü → Einstellungen → Validation Framework → Run All Tests

# Oder direkt
python -m core.validation_framework
```

**Test-Kategorien**:
- Core Components
- Exploit Tests
- Integration Tests
- Performance Tests

### Export und Reporting

**Monitoring-Daten exportieren**:
1. Live Monitoring → "Export Events"
2. Format wählen (JSON/CSV)
3. Datei wird mit Zeitstempel gespeichert

**Exploit-Reports**:
- Werden automatisch nach erfolgreichen Exploits erstellt
- Verfügbar in: JSON, HTML, Markdown
- Speicherort: `reports/`

## Konfiguration

### Abhängigkeiten installieren

**Für KI-Features**:
```bash
pip install scikit-learn numpy
```

**Für Resilience-Monitoring**:
```bash
pip install psutil
```

**Für erweiterte Obfuskierung**:
```bash
pip install astor
# Optional: OLLVM für Binary-Obfuskierung
```

### Framework-Einstellungen

1. Hauptmenü → "Einstellungen"
2. Optionen:
 - Logging-Level anpassen
 - Simulationsmodus aktivieren
 - Ausgabeverzeichnis ändern
 - Module aktivieren/deaktivieren

## Typische Workflows

### 1. Penetrationstest-Workflow

```
1. Reconnaissance
 → Ziel analysieren
 → Schwachstellen identifizieren

2. Exploit-Auswahl
 → KI-Orchestrator nutzen
 → Passende CVEs auswählen

3. Chain erstellen
 → Exploit-Reihenfolge planen
 → Abhängigkeiten prüfen

4. Ausführung
 → Live-Monitoring aktivieren
 → Chain ausführen
 → Ergebnisse überwachen

5. Reporting
 → Automatische Reports prüfen
 → Zusätzliche Dokumentation
```

### 2. Entwicklungs-Workflow

```
1. Neuen Exploit entwickeln
 → Template verwenden
 → In exploits/ speichern

2. Validation
 → Tests schreiben
 → Framework-Tests ausführen

3. Integration
 → Module Loader registrierung
 → Menü-Integration

4. Obfuskierung
 → Payload obfuskieren
 → Anti-Detection hinzufügen
```

## Häufige Fragen

**Q: Wie aktiviere ich alle Features?**
A: Installiere alle optionalen Abhängigkeiten mit:
```bash
pip install -r requirements-full.txt
```

**Q: Warum funktioniert die KI nicht?**
A: Prüfe ob scikit-learn installiert ist. Das System fällt automatisch auf regelbasierte Auswahl zurück.

**Q: Wie erstelle ich eigene Exploits?**
A: Nutze die Vorlagen in `exploits/` und registriere sie im Module Loader.

**Q: Kann ich das Framework remote nutzen?**
A: Ja, nutze Ngrok Tunneling aus dem Hauptmenü für Remote-Zugriff.

## Sicherheitshinweise

1. **Nur für autorisierte Tests** verwenden
2. **Simulationsmodus** für Entwicklung und Tests
3. **Logging** immer aktiviert lassen für Audit-Trail
4. **Verschlüsselte Verbindungen** für Remote-Zugriff
5. **Regelmäßige Updates** für Sicherheitspatches

---

Weitere Hilfe: Siehe API_REFERENCE.md für technische Details