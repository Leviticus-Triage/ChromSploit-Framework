#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
AI-Orchestrator mit Hybridmodellen
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import json
import time
import datetime
import threading
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Union

# Überprüfen, ob die erforderlichen Module verfügbar sind
REQUIRED_MODULES = ['torch', 'onnxruntime', 'xgboost', 'transformers']
MISSING_MODULES = []

for module in REQUIRED_MODULES:
    if not importlib.util.find_spec(module):
        MISSING_MODULES.append(module)

if MISSING_MODULES:
    raise ImportError(f"Die folgenden Module sind erforderlich für den AI-Orchestrator: {', '.join(MISSING_MODULES)}. "
                      f"Installieren Sie sie mit 'pip install {' '.join(MISSING_MODULES)}'.")

# Erst nach der Überprüfung importieren
import torch
import onnxruntime as ort
import xgboost as xgb
import numpy as np
from transformers import AutoModel, AutoTokenizer

class AIOrchestrator:
    """
    AI-Orchestrator mit Hybridmodellen für Entscheidungsfindung
    """
    
    def __init__(self, model_path: Optional[str] = None, logger=None):
        """
        Initialisiert den AI-Orchestrator
        
        Args:
            model_path (str, optional): Pfad zu den Modell-Assets
            logger: Logger-Instanz
        """
        self.logger = logger
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "model_assets")
        
        # Modelle initialisieren
        self.bert_model = None
        self.tokenizer = None
        self.xgb_model = None
        self.ort_session = None
        
        # Modelle laden
        self._load_models()
        
        # Feedback-Loop initialisieren
        self.feedback_data = []
        self.feedback_lock = threading.Lock()
    
    def log(self, level: str, message: str) -> None:
        """
        Loggt eine Nachricht
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        if self.logger:
            if hasattr(self.logger, level):
                getattr(self.logger, level)(message)
            else:
                print(f"[{level.upper()}] {message}")
        else:
            print(f"[{level.upper()}] {message}")
    
    def _load_models(self) -> None:
        """
        Lädt die KI-Modelle
        """
        try:
            # BERT-Modell laden
            self.log("info", "Lade BERT-Modell...")
            model_name = "microsoft/xtremedistil-l6-h256-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.bert_model = AutoModel.from_pretrained(model_name)
            
            # XGBoost-Modell laden
            self.log("info", "Lade XGBoost-Modell...")
            xgb_model_path = os.path.join(self.model_path, "cve_model.xgb")
            if os.path.exists(xgb_model_path):
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(xgb_model_path)
            else:
                self.log("warning", f"XGBoost-Modell nicht gefunden: {xgb_model_path}")
                self.xgb_model = None
            
            # ONNX-Modell laden
            self.log("info", "Lade ONNX-Modell...")
            onnx_model_path = os.path.join(self.model_path, "fusion_model.onnx")
            if os.path.exists(onnx_model_path):
                self.ort_session = ort.InferenceSession(onnx_model_path)
            else:
                self.log("warning", f"ONNX-Modell nicht gefunden: {onnx_model_path}")
                self.ort_session = None
            
            self.log("info", "KI-Modelle erfolgreich geladen")
        except Exception as e:
            self.log("error", f"Fehler beim Laden der KI-Modelle: {str(e)}")
            raise
    
    def _process_text(self, text_data: str) -> Dict[str, torch.Tensor]:
        """
        Verarbeitet Textdaten für das BERT-Modell
        
        Args:
            text_data (str): Zu verarbeitender Text
            
        Returns:
            dict: Tokenisierte Eingabe für das BERT-Modell
        """
        return self.tokenizer(text_data, return_tensors="pt", padding=True, truncation=True, max_length=128)
    
    def _process_structured(self, structured_data: Dict[str, Any]) -> np.ndarray:
        """
        Verarbeitet strukturierte Daten für das XGBoost-Modell
        
        Args:
            structured_data (dict): Strukturierte Daten
            
        Returns:
            numpy.ndarray: Feature-Matrix für das XGBoost-Modell
        """
        # Beispiel für Feature-Extraktion aus strukturierten Daten
        features = []
        
        # Betriebssystem-Features
        os_type = structured_data.get("os_type", "unknown")
        features.append(1 if os_type == "windows" else 0)
        features.append(1 if os_type == "linux" else 0)
        features.append(1 if os_type == "macos" else 0)
        
        # Browser-Features
        browser = structured_data.get("browser", "unknown")
        features.append(1 if browser == "chrome" else 0)
        features.append(1 if browser == "firefox" else 0)
        features.append(1 if browser == "edge" else 0)
        
        # Version-Features
        version = structured_data.get("version", "0.0.0")
        try:
            major_version = int(version.split(".")[0])
            features.append(major_version / 100.0)  # Normalisieren
        except (ValueError, IndexError):
            features.append(0.0)
        
        # Weitere Features
        features.append(1 if structured_data.get("is_admin", False) else 0)
        features.append(1 if structured_data.get("has_sandbox", False) else 0)
        features.append(1 if structured_data.get("has_antivirus", False) else 0)
        
        return np.array([features], dtype=np.float32)
    
    def analyze_target(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert ein Ziel und gibt Empfehlungen zurück
        
        Args:
            target_data (dict): Zieldaten
            
        Returns:
            dict: Analyseergebnisse und Empfehlungen
        """
        start_time = time.time()
        
        try:
            # Feature-Extraktion
            text_features = self._process_text(target_data.get("description", ""))
            struct_features = self._process_structured(target_data)
            
            # BERT-Inferenz
            with torch.no_grad():
                bert_output = self.bert_model(**text_features).last_hidden_state.mean(dim=1)
            
            # XGBoost-Inferenz
            if self.xgb_model:
                xgb_output = self.xgb_model.predict(xgb.DMatrix(struct_features))
                xgb_output = torch.tensor(xgb_output).unsqueeze(0)
            else:
                # Fallback, wenn kein XGBoost-Modell verfügbar ist
                xgb_output = torch.zeros(1, 10)  # Annahme: 10 Klassen
            
            # Fusion der Ergebnisse
            if self.ort_session:
                # ONNX-Inferenz für Fusion
                combined = torch.cat([bert_output, xgb_output], dim=1)
                ort_inputs = {self.ort_session.get_inputs()[0].name: combined.numpy()}
                ort_outputs = self.ort_session.run(None, ort_inputs)
                decision = ort_outputs[0]
            else:
                # Fallback, wenn kein ONNX-Modell verfügbar ist
                combined = torch.cat([bert_output, xgb_output], dim=1)
                decision = combined.numpy()
            
            # Ergebnisse interpretieren
            results = self._parse_decision(decision, target_data)
            
            # Ausführungszeit messen
            execution_time = (time.time() - start_time) * 1000  # in ms
            results["execution_time_ms"] = execution_time
            
            self.log("info", f"Zielanalyse abgeschlossen in {execution_time:.2f} ms")
            
            return results
        except Exception as e:
            self.log("error", f"Fehler bei der Zielanalyse: {str(e)}")
            
            # Fallback zur Legacy-Methode
            self.log("info", "Verwende Legacy-CVE-Matcher als Fallback")
            return self._legacy_cve_matcher(target_data)
    
    def _parse_decision(self, decision: np.ndarray, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpretiert die Entscheidung des Modells
        
        Args:
            decision (numpy.ndarray): Modellentscheidung
            target_data (dict): Zieldaten
            
        Returns:
            dict: Interpretierte Ergebnisse
        """
        # Beispiel für die Interpretation der Entscheidung
        browser = target_data.get("browser", "unknown")
        os_type = target_data.get("os_type", "unknown")
        
        # CVE-Empfehlungen basierend auf Browser und OS
        cve_recommendations = []
        
        if browser == "chrome":
            cve_recommendations.extend(["CVE-2025-4664", "CVE-2025-2783"])
        elif browser == "firefox":
            cve_recommendations.append("CVE-2025-2857")
        elif browser == "edge":
            cve_recommendations.append("CVE-2025-30397")
        
        # Konfidenz für jede CVE berechnen (Beispiel)
        confidences = {}
        for i, cve in enumerate(cve_recommendations):
            if i < len(decision[0]):
                confidences[cve] = float(decision[0][i])
            else:
                confidences[cve] = 0.5  # Standardwert
        
        # Sortieren nach Konfidenz
        sorted_cves = sorted(confidences.items(), key=lambda x: x[1], reverse=True)
        
        # Payload-Empfehlungen
        payload_recommendations = []
        if os_type == "windows":
            payload_recommendations.append("windows/meterpreter/reverse_https")
        elif os_type == "linux":
            payload_recommendations.append("linux/x64/meterpreter/reverse_tcp")
        
        # Obfuskierungsempfehlungen
        obfuscation_recommendations = []
        if target_data.get("has_antivirus", False):
            obfuscation_recommendations.append("ollvm_advanced")
        else:
            obfuscation_recommendations.append("ollvm_basic")
        
        return {
            "target": target_data,
            "cve_recommendations": [cve for cve, _ in sorted_cves],
            "confidences": {cve: conf for cve, conf in sorted_cves},
            "payload_recommendations": payload_recommendations,
            "obfuscation_recommendations": obfuscation_recommendations,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _legacy_cve_matcher(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy-Methode zur CVE-Zuordnung (Fallback)
        
        Args:
            target_data (dict): Zieldaten
            
        Returns:
            dict: Zuordnungsergebnisse
        """
        browser = target_data.get("browser", "unknown")
        os_type = target_data.get("os_type", "unknown")
        version = target_data.get("version", "0.0.0")
        
        cve_recommendations = []
        
        # Einfache regelbasierte Zuordnung
        if browser == "chrome":
            if version.startswith("120") or version.startswith("121") or version.startswith("122") or version.startswith("123") or version.startswith("124") or version.startswith("125"):
                cve_recommendations.append("CVE-2025-4664")
            if version.startswith("122") or version.startswith("123") or version.startswith("124") or version.startswith("125") or version.startswith("126"):
                cve_recommendations.append("CVE-2025-2783")
        elif browser == "firefox":
            if version.startswith("115") or version.startswith("116") or version.startswith("117") or version.startswith("118") or version.startswith("119") or version.startswith("120"):
                cve_recommendations.append("CVE-2025-2857")
        elif browser == "edge":
            if version.startswith("110") or version.startswith("111") or version.startswith("112") or version.startswith("113") or version.startswith("114") or version.startswith("115"):
                cve_recommendations.append("CVE-2025-30397")
        
        # Payload-Empfehlungen
        payload_recommendations = []
        if os_type == "windows":
            payload_recommendations.append("windows/meterpreter/reverse_https")
        elif os_type == "linux":
            payload_recommendations.append("linux/x64/meterpreter/reverse_tcp")
        
        # Obfuskierungsempfehlungen
        obfuscation_recommendations = []
        if target_data.get("has_antivirus", False):
            obfuscation_recommendations.append("ollvm_advanced")
        else:
            obfuscation_recommendations.append("ollvm_basic")
        
        return {
            "target": target_data,
            "cve_recommendations": cve_recommendations,
            "confidences": {cve: 0.7 for cve in cve_recommendations},  # Standardkonfidenz
            "payload_recommendations": payload_recommendations,
            "obfuscation_recommendations": obfuscation_recommendations,
            "timestamp": datetime.datetime.now().isoformat(),
            "method": "legacy_cve_matcher"
        }
    
    def recommend_exploit(self, target_data: Dict[str, Any]) -> str:
        """
        Empfiehlt einen Exploit für ein Ziel
        
        Args:
            target_data (dict): Zieldaten
            
        Returns:
            str: Empfohlener Exploit
        """
        results = self.analyze_target(target_data)
        cve_recommendations = results.get("cve_recommendations", [])
        
        if cve_recommendations:
            return cve_recommendations[0]  # Besten Exploit zurückgeben
        else:
            return None
    
    def add_feedback(self, target_data: Dict[str, Any], recommended_exploit: str, success: bool) -> None:
        """
        Fügt Feedback zum Lernprozess hinzu
        
        Args:
            target_data (dict): Zieldaten
            recommended_exploit (str): Empfohlener Exploit
            success (bool): Ob der Exploit erfolgreich war
        """
        with self.feedback_lock:
            self.feedback_data.append({
                "target": target_data,
                "exploit": recommended_exploit,
                "success": success,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Feedback-Datei aktualisieren
            self._save_feedback()
    
    def _save_feedback(self) -> None:
        """
        Speichert Feedback-Daten in einer Datei
        """
        feedback_file = os.path.join(self.model_path, "feedback.json")
        
        try:
            with open(feedback_file, "w") as f:
                json.dump(self.feedback_data, f, indent=2)
            
            self.log("info", f"Feedback-Daten gespeichert: {len(self.feedback_data)} Einträge")
        except Exception as e:
            self.log("error", f"Fehler beim Speichern der Feedback-Daten: {str(e)}")
    
    def _load_feedback(self) -> None:
        """
        Lädt Feedback-Daten aus einer Datei
        """
        feedback_file = os.path.join(self.model_path, "feedback.json")
        
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, "r") as f:
                    self.feedback_data = json.load(f)
                
                self.log("info", f"Feedback-Daten geladen: {len(self.feedback_data)} Einträge")
            except Exception as e:
                self.log("error", f"Fehler beim Laden der Feedback-Daten: {str(e)}")
                self.feedback_data = []
        else:
            self.feedback_data = []
    
    def update_model(self) -> None:
        """
        Aktualisiert das Modell basierend auf Feedback-Daten
        """
        if not self.feedback_data:
            self.log("info", "Keine Feedback-Daten zum Aktualisieren des Modells vorhanden")
            return
        
        self.log("info", f"Aktualisiere Modell mit {len(self.feedback_data)} Feedback-Einträgen")
        
        # Hier würde die Modellaktualisierung implementiert werden
        # Dies ist ein Platzhalter für die tatsächliche Implementierung
        
        self.log("info", "Modellaktualisierung abgeschlossen")
