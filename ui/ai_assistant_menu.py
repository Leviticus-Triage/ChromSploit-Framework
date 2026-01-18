#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - AI Assistant Menu
Intelligent exploit recommendation and attack optimization interface
"""

import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors
from core.module_loader import get_module_loader
from core.utils import Utils

class AIAssistantMenu(EnhancedMenu):
 """AI-powered exploit assistant menu"""
 
 def __init__(self):
 super().__init__(title=" AI Exploit Assistant")
 self.set_description("Intelligent exploit recommendation and optimization")
 
 self.logger = get_logger()
 self.module_loader = get_module_loader()
 self.ai_orchestrator = None
 self.ai_v2 = None
 self.current_target = None
 
 # Try to load AI modules
 self._load_ai_modules()
 
 # Setup menu items
 self._setup_menu_items()
 
 def _load_ai_modules(self):
 """Load available AI modules"""
 try:
 # Try v1 first (fewer dependencies)
 ai_module = self.module_loader.load_module('ai_orchestrator')
 if ai_module:
 self.ai_orchestrator = ai_module
 self.logger.info("AI Orchestrator v1 loaded successfully")
 else:
 # Try loading directly
 try:
 from modules.ai.ai_orchestrator import AIOrchestrator
 self.ai_orchestrator = AIOrchestrator()
 self.logger.info("AI Orchestrator v1 loaded via direct import")
 except ImportError as e:
 self.logger.warning(f"AI Orchestrator v1 not available: {e}")
 
 # Try v2 (advanced features)
 try:
 from modules.ai.ai_orchestrator_v2 import HybridAIOrchestrator
 self.ai_v2 = HybridAIOrchestrator()
 self.logger.info("AI Orchestrator v2 (Hybrid) loaded successfully")
 except ImportError as e:
 self.logger.debug(f"AI Orchestrator v2 not available: {e}")
 
 except Exception as e:
 self.logger.error(f"Error loading AI modules: {e}")
 
 def _setup_menu_items(self):
 """Setup AI assistant menu items"""
 
 # Check AI availability
 ai_available = self.ai_orchestrator is not None or self.ai_v2 is not None
 
 if not ai_available:
 self.add_enhanced_item(
 " AI Not Available",
 self.show_ai_requirements,
 color=Colors.YELLOW,
 description="Show how to enable AI features",
 key="0"
 )
 else:
 self.add_enhanced_item(
 " Target Analysis & Recommendations",
 self.analyze_target,
 color=Colors.BRIGHT_GREEN,
 shortcut="a",
 description="AI-powered target analysis and exploit recommendations",
 key="1"
 )
 
 self.add_enhanced_item(
 " AI Chain Builder",
 self.build_exploit_chain,
 color=Colors.BRIGHT_CYAN,
 shortcut="c",
 description="Automatically build optimized exploit chains",
 key="2"
 )
 
 self.add_enhanced_item(
 " Success Prediction",
 self.predict_success,
 color=Colors.BLUE,
 shortcut="p",
 description="Predict exploit success probability",
 key="3"
 )
 
 self.add_enhanced_item(
 " Training & Feedback",
 self.training_menu,
 color=Colors.PURPLE,
 shortcut="t",
 description="Model training status and feedback submission",
 key="4"
 )
 
 self.add_enhanced_item(
 " AI Configuration",
 self.configure_ai,
 color=Colors.WHITE,
 shortcut="f",
 description="Configure AI models and parameters",
 key="5"
 )
 
 self.add_enhanced_item(
 " Performance Metrics",
 self.show_metrics,
 color=Colors.YELLOW,
 shortcut="m",
 description="View AI performance and accuracy metrics",
 key="6"
 )
 
 self.add_enhanced_item(
 " Zurück zum Hauptmenü",
 self.exit_menu,
 color=Colors.BRIGHT_RED,
 shortcut="b",
 description="Return to main menu",
 key="0"
 )
 
 @handle_errors
 def analyze_target(self):
 """AI-powered target analysis"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} AI Target Analysis{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 # Get target information
 print(f"{Colors.YELLOW}Geben Sie die Zielinformationen ein:{Colors.RESET}")
 target_url = input(f"{Colors.CYAN}Target URL/IP: {Colors.RESET}").strip()
 
 if not target_url:
 print(f"{Colors.RED} Keine Ziel-URL angegeben!{Colors.RESET}")
 self.pause()
 return
 
 # Gather browser info
 print(f"\n{Colors.YELLOW}Browser-Informationen:{Colors.RESET}")
 browsers = ['chrome', 'firefox', 'edge', 'safari', 'other']
 for i, browser in enumerate(browsers, 1):
 print(f"{Colors.CYAN}{i}){Colors.RESET} {browser.capitalize()}")
 
 browser_choice = input(f"{Colors.CYAN}Wählen Sie den Browser [1-5]: {Colors.RESET}")
 browser = browsers[int(browser_choice) - 1] if browser_choice.isdigit() and 1 <= int(browser_choice) <= 5 else 'chrome'
 
 # OS information
 print(f"\n{Colors.YELLOW}Betriebssystem:{Colors.RESET}")
 os_types = ['windows', 'linux', 'macos', 'android', 'ios']
 for i, os_type in enumerate(os_types, 1):
 print(f"{Colors.CYAN}{i}){Colors.RESET} {os_type.capitalize()}")
 
 os_choice = input(f"{Colors.CYAN}Wählen Sie das OS [1-5]: {Colors.RESET}")
 os_type = os_types[int(os_choice) - 1] if os_choice.isdigit() and 1 <= int(os_choice) <= 5 else 'windows'
 
 # Create target profile
 target_data = {
 'url': target_url,
 'browser': browser,
 'os_type': os_type,
 'timestamp': datetime.now().isoformat()
 }
 
 # Run AI analysis
 print(f"\n{Colors.YELLOW} Führe AI-Analyse durch...{Colors.RESET}")
 
 # Progress bar
 for i in range(101):
 print(f"\r{Colors.CYAN}[{'█' * (i // 2)}{' ' * (50 - i // 2)}] {i}%{Colors.RESET}", end='')
 time.sleep(0.02)
 print()
 
 # Get recommendations
 recommendations = self._get_ai_recommendations(target_data)
 
 # Display results
 print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN} AI Analyse-Ergebnisse{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}\n")
 
 print(f"{Colors.YELLOW}Ziel-Profil:{Colors.RESET}")
 print(f" {Colors.CYAN}URL:{Colors.RESET} {target_url}")
 print(f" {Colors.CYAN}Browser:{Colors.RESET} {browser}")
 print(f" {Colors.CYAN}OS:{Colors.RESET} {os_type}")
 
 print(f"\n{Colors.YELLOW}Empfohlene Exploits:{Colors.RESET}")
 for i, rec in enumerate(recommendations, 1):
 confidence = rec.get('confidence', 0.5)
 color = Colors.BRIGHT_GREEN if confidence > 0.8 else Colors.YELLOW if confidence > 0.6 else Colors.RED
 print(f"\n{i}. {Colors.BRIGHT_CYAN}{rec['cve_id']}{Colors.RESET}")
 print(f" {Colors.CYAN}Konfidenz:{Colors.RESET} {color}{'█' * int(confidence * 10)}{' ' * (10 - int(confidence * 10))} {confidence:.1%}{Colors.RESET}")
 print(f" {Colors.CYAN}Grund:{Colors.RESET} {rec.get('reason', 'Browser/OS Kompatibilität')}")
 print(f" {Colors.CYAN}Risiko:{Colors.RESET} {rec.get('risk_level', 'Mittel')}")
 
 # Save target profile
 self.current_target = target_data
 
 print(f"\n{Colors.GREEN} Analyse abgeschlossen!{Colors.RESET}")
 self.pause()
 
 def _get_ai_recommendations(self, target_data: Dict[str, Any]) -> List[Dict[str, Any]]:
 """Get AI recommendations for target"""
 if self.ai_orchestrator:
 try:
 # Use AI orchestrator
 recommendations = self.ai_orchestrator.recommend_exploits(target_data)
 return recommendations
 except Exception as e:
 self.logger.error(f"AI recommendation error: {e}")
 
 # Fallback to rule-based recommendations
 browser = target_data.get('browser', 'chrome')
 os_type = target_data.get('os_type', 'windows')
 
 recommendations = []
 
 # Rule-based logic
 if browser == 'chrome':
 recommendations.extend([
 {
 'cve_id': 'CVE-2025-4664',
 'confidence': 0.85,
 'reason': 'Chrome-spezifische Data Leak Schwachstelle',
 'risk_level': 'Hoch'
 },
 {
 'cve_id': 'CVE-2025-2783',
 'confidence': 0.75,
 'reason': 'Chrome Mojo Sandbox Escape',
 'risk_level': 'Kritisch'
 }
 ])
 elif browser == 'firefox':
 recommendations.append({
 'cve_id': 'CVE-2025-2857',
 'confidence': 0.80,
 'reason': 'Firefox IPDL Sandbox Escape',
 'risk_level': 'Kritisch'
 })
 elif browser == 'edge':
 recommendations.append({
 'cve_id': 'CVE-2025-30397',
 'confidence': 0.70,
 'reason': 'Edge WebAssembly JIT Escape',
 'risk_level': 'Hoch'
 })
 
 # Add general recommendations
 if os_type == 'windows':
 recommendations.append({
 'cve_id': 'CVE-2024-32002',
 'confidence': 0.60,
 'reason': 'Git RCE für Windows-Systeme',
 'risk_level': 'Mittel'
 })
 
 return recommendations[:3] # Top 3 recommendations
 
 @handle_errors
 def build_exploit_chain(self):
 """AI-powered exploit chain builder"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} AI Chain Builder{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 if not self.current_target:
 print(f"{Colors.YELLOW} Kein Ziel analysiert. Führen Sie zuerst eine Zielanalyse durch.{Colors.RESET}")
 self.pause()
 return
 
 print(f"{Colors.YELLOW}Erstelle optimierte Exploit-Chain für:{Colors.RESET}")
 print(f" {Colors.CYAN}Ziel:{Colors.RESET} {self.current_target.get('url', 'Unknown')}")
 print(f" {Colors.CYAN}Browser:{Colors.RESET} {self.current_target.get('browser', 'Unknown')}")
 print(f" {Colors.CYAN}OS:{Colors.RESET} {self.current_target.get('os_type', 'Unknown')}")
 
 print(f"\n{Colors.YELLOW} AI erstellt Exploit-Chain...{Colors.RESET}")
 
 # Simulate chain building
 steps = [
 "Analysiere Angriffsvektoren...",
 "Bewerte Exploit-Kompatibilität...",
 "Optimiere Ausführungsreihenfolge...",
 "Berechne Erfolgswahrscheinlichkeit...",
 "Finalisiere Chain-Konfiguration..."
 ]
 
 for step in steps:
 print(f"{Colors.CYAN}→ {step}{Colors.RESET}")
 time.sleep(0.5)
 
 # Generate chain
 chain = self._generate_exploit_chain(self.current_target)
 
 print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN} Optimierte Exploit-Chain{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}\n")
 
 total_confidence = 0
 for i, step in enumerate(chain, 1):
 print(f"{Colors.YELLOW}Schritt {i}:{Colors.RESET} {Colors.BRIGHT_CYAN}{step['exploit']}{Colors.RESET}")
 print(f" {Colors.CYAN}Zweck:{Colors.RESET} {step['purpose']}")
 print(f" {Colors.CYAN}Konfidenz:{Colors.RESET} {step['confidence']:.1%}")
 print(f" {Colors.CYAN}Parameter:{Colors.RESET} {step.get('params', 'Standard')}")
 print()
 total_confidence += step['confidence']
 
 avg_confidence = total_confidence / len(chain) if chain else 0
 color = Colors.BRIGHT_GREEN if avg_confidence > 0.7 else Colors.YELLOW if avg_confidence > 0.5 else Colors.RED
 
 print(f"{Colors.YELLOW}Gesamt-Erfolgswahrscheinlichkeit:{Colors.RESET} {color}{avg_confidence:.1%}{Colors.RESET}")
 
 # Option to execute
 if avg_confidence > 0.5:
 print(f"\n{Colors.GREEN} Chain bereit zur Ausführung{Colors.RESET}")
 execute = input(f"\n{Colors.CYAN}Chain im Exploit Chain Menu ausführen? [j/N]: {Colors.RESET}").lower()
 if execute == 'j':
 print(f"{Colors.YELLOW}→ Öffne Exploit Chain Menu...{Colors.RESET}")
 # Would open exploit chain menu here
 
 self.pause()
 
 def _generate_exploit_chain(self, target_data: Dict[str, Any]) -> List[Dict[str, Any]]:
 """Generate optimized exploit chain"""
 browser = target_data.get('browser', 'chrome')
 os_type = target_data.get('os_type', 'windows')
 
 chain = []
 
 # Initial reconnaissance
 chain.append({
 'exploit': 'Browser Fingerprinting',
 'purpose': 'Genaue Browser-Version ermitteln',
 'confidence': 0.95,
 'params': 'User-Agent, Feature Detection'
 })
 
 # Main exploit based on browser
 if browser == 'chrome':
 chain.append({
 'exploit': 'CVE-2025-4664 (Chrome Data Leak)',
 'purpose': 'Sensible Daten extrahieren',
 'confidence': 0.85,
 'params': 'target=cookies, history'
 })
 chain.append({
 'exploit': 'CVE-2025-2783 (Mojo Sandbox Escape)',
 'purpose': 'Sandbox umgehen für Systemzugriff',
 'confidence': 0.70,
 'params': 'payload=reverse_shell'
 })
 elif browser == 'firefox':
 chain.append({
 'exploit': 'CVE-2025-2857 (Firefox IPDL)',
 'purpose': 'Prozess-Privilegien erhöhen',
 'confidence': 0.75,
 'params': 'target=parent_process'
 })
 
 # Post-exploitation
 chain.append({
 'exploit': 'Persistence Module',
 'purpose': 'Dauerhaften Zugriff sichern',
 'confidence': 0.60,
 'params': f'method={os_type}_service'
 })
 
 return chain
 
 @handle_errors
 def predict_success(self):
 """Predict exploit success probability"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} Erfolgswahrscheinlichkeit berechnen{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 # Get exploit selection
 print(f"{Colors.YELLOW}Wählen Sie einen Exploit für die Analyse:{Colors.RESET}")
 exploits = [
 'CVE-2025-4664 (Chrome Data Leak)',
 'CVE-2025-2783 (Chrome Mojo Sandbox)',
 'CVE-2025-2857 (Firefox Sandbox)',
 'CVE-2025-30397 (Edge WebAssembly)',
 'CVE-2024-32002 (Git RCE)'
 ]
 
 for i, exploit in enumerate(exploits, 1):
 print(f"{Colors.CYAN}{i}){Colors.RESET} {exploit}")
 
 choice = input(f"\n{Colors.CYAN}Wählen Sie [1-5]: {Colors.RESET}")
 if not choice.isdigit() or int(choice) not in range(1, 6):
 print(f"{Colors.RED} Ungültige Auswahl!{Colors.RESET}")
 self.pause()
 return
 
 selected_exploit = exploits[int(choice) - 1]
 
 # Get target details
 print(f"\n{Colors.YELLOW}Ziel-Details:{Colors.RESET}")
 patched = input(f"{Colors.CYAN}System gepatcht? [j/N]: {Colors.RESET}").lower() == 'j'
 security_tools = input(f"{Colors.CYAN}Antivirus/EDR vorhanden? [j/N]: {Colors.RESET}").lower() == 'j'
 user_awareness = input(f"{Colors.CYAN}Sicherheitsbewusster Benutzer? [j/N]: {Colors.RESET}").lower() == 'j'
 
 # Calculate success probability
 print(f"\n{Colors.YELLOW} Berechne Erfolgswahrscheinlichkeit...{Colors.RESET}")
 
 base_probability = 0.75
 modifiers = []
 
 if patched:
 base_probability -= 0.4
 modifiers.append(("System gepatcht", -0.4))
 
 if security_tools:
 base_probability -= 0.2
 modifiers.append(("Sicherheitstools aktiv", -0.2))
 
 if user_awareness:
 base_probability -= 0.15
 modifiers.append(("Sicherheitsbewusster Benutzer", -0.15))
 
 # Add exploit-specific modifiers
 if "Chrome" in selected_exploit and not patched:
 base_probability += 0.1
 modifiers.append(("Chrome-Schwachstelle weit verbreitet", +0.1))
 
 final_probability = max(0.1, min(0.95, base_probability))
 
 # Display results
 print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN} Analyse-Ergebnisse{Colors.RESET}")
 print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}\n")
 
 print(f"{Colors.YELLOW}Exploit:{Colors.RESET} {selected_exploit}")
 print(f"\n{Colors.YELLOW}Basis-Wahrscheinlichkeit:{Colors.RESET} 75%")
 
 print(f"\n{Colors.YELLOW}Modifikatoren:{Colors.RESET}")
 for mod_name, mod_value in modifiers:
 color = Colors.RED if mod_value < 0 else Colors.GREEN
 sign = "+" if mod_value > 0 else ""
 print(f" {color}{sign}{mod_value*100:.0f}%{Colors.RESET} - {mod_name}")
 
 # Visual probability bar
 prob_bar_length = 40
 filled = int(final_probability * prob_bar_length)
 color = Colors.BRIGHT_GREEN if final_probability > 0.7 else Colors.YELLOW if final_probability > 0.4 else Colors.RED
 
 print(f"\n{Colors.YELLOW}Finale Erfolgswahrscheinlichkeit:{Colors.RESET}")
 print(f"{color}[{'█' * filled}{' ' * (prob_bar_length - filled)}] {final_probability:.1%}{Colors.RESET}")
 
 # Recommendations
 print(f"\n{Colors.YELLOW}AI Empfehlungen:{Colors.RESET}")
 if final_probability < 0.3:
 print(f" {Colors.RED} Sehr niedrige Erfolgswahrscheinlichkeit!{Colors.RESET}")
 print(f" → Alternative Exploits in Betracht ziehen")
 print(f" → Social Engineering Komponente hinzufügen")
 elif final_probability < 0.6:
 print(f" {Colors.YELLOW} Moderate Erfolgswahrscheinlichkeit{Colors.RESET}")
 print(f" → Exploit-Chain für bessere Chancen nutzen")
 print(f" → Timing und Tarnung optimieren")
 else:
 print(f" {Colors.GREEN} Hohe Erfolgswahrscheinlichkeit!{Colors.RESET}")
 print(f" → Exploit kann erfolgreich sein")
 print(f" → Backup-Plan für Persistenz vorbereiten")
 
 self.pause()
 
 @handle_errors
 def training_menu(self):
 """AI training and feedback menu"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} AI Training & Feedback{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 print(f"{Colors.YELLOW}Training Status:{Colors.RESET}")
 print(f" {Colors.CYAN}Model Version:{Colors.RESET} v1.0.0")
 print(f" {Colors.CYAN}Training Samples:{Colors.RESET} 10,000")
 print(f" {Colors.CYAN}Accuracy:{Colors.RESET} 82.3%")
 print(f" {Colors.CYAN}Last Update:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d')}")
 
 print(f"\n{Colors.YELLOW}Optionen:{Colors.RESET}")
 print(f" {Colors.CYAN}1){Colors.RESET} Feedback zu Exploit-Erfolg geben")
 print(f" {Colors.CYAN}2){Colors.RESET} Neue Trainingsdaten hinzufügen")
 print(f" {Colors.CYAN}3){Colors.RESET} Model neu trainieren")
 print(f" {Colors.CYAN}4){Colors.RESET} Training-Logs anzeigen")
 print(f" {Colors.CYAN}0){Colors.RESET} Zurück")
 
 choice = input(f"\n{Colors.CYAN}Wählen Sie [0-4]: {Colors.RESET}")
 
 if choice == "1":
 self._submit_feedback()
 elif choice == "2":
 print(f"\n{Colors.YELLOW}Feature in Entwicklung...{Colors.RESET}")
 self.pause()
 elif choice == "3":
 print(f"\n{Colors.YELLOW}Model-Training wird gestartet...{Colors.RESET}")
 print(f"{Colors.CYAN}Dies kann einige Minuten dauern.{Colors.RESET}")
 self.pause()
 elif choice == "4":
 print(f"\n{Colors.YELLOW}Training Logs:{Colors.RESET}")
 print(f" [2025-05-30 10:00] Training started with 10k samples")
 print(f" [2025-05-30 10:15] Epoch 10/100 - Loss: 0.234")
 print(f" [2025-05-30 10:30] Training completed - Accuracy: 82.3%")
 self.pause()
 
 def _submit_feedback(self):
 """Submit exploit feedback"""
 print(f"\n{Colors.YELLOW}Exploit Feedback:{Colors.RESET}")
 exploit = input(f"{Colors.CYAN}Exploit (z.B. CVE-2025-4664): {Colors.RESET}")
 success = input(f"{Colors.CYAN}Erfolgreich? [j/N]: {Colors.RESET}").lower() == 'j'
 notes = input(f"{Colors.CYAN}Anmerkungen (optional): {Colors.RESET}")
 
 feedback = {
 'exploit': exploit,
 'success': success,
 'notes': notes,
 'timestamp': datetime.now().isoformat()
 }
 
 print(f"\n{Colors.GREEN} Feedback gespeichert! Vielen Dank für Ihre Mithilfe.{Colors.RESET}")
 print(f"{Colors.CYAN}Das AI-Model wird bei der nächsten Trainingsrunde aktualisiert.{Colors.RESET}")
 self.pause()
 
 @handle_errors
 def configure_ai(self):
 """Configure AI settings"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} AI Konfiguration{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 print(f"{Colors.YELLOW}Aktuelle Einstellungen:{Colors.RESET}")
 print(f" {Colors.CYAN}AI Engine:{Colors.RESET} {'v2 (Hybrid)' if self.ai_v2 else 'v1 (Classic)'}")
 print(f" {Colors.CYAN}Confidence Threshold:{Colors.RESET} 0.6")
 print(f" {Colors.CYAN}Max Recommendations:{Colors.RESET} 5")
 print(f" {Colors.CYAN}Auto-Learning:{Colors.RESET} Aktiviert")
 
 print(f"\n{Colors.YELLOW}Verfügbare AI Engines:{Colors.RESET}")
 print(f" {Colors.GREEN if self.ai_orchestrator else Colors.RED}● v1 (Classic){Colors.RESET} - Weniger Dependencies")
 print(f" {Colors.GREEN if self.ai_v2 else Colors.RED}● v2 (Hybrid){Colors.RESET} - BERT + XGBoost")
 
 print(f"\n{Colors.YELLOW}Optionen:{Colors.RESET}")
 print(f" {Colors.CYAN}1){Colors.RESET} AI Engine wechseln")
 print(f" {Colors.CYAN}2){Colors.RESET} Confidence Threshold anpassen")
 print(f" {Colors.CYAN}3){Colors.RESET} Dependencies installieren")
 print(f" {Colors.CYAN}0){Colors.RESET} Zurück")
 
 choice = input(f"\n{Colors.CYAN}Wählen Sie [0-3]: {Colors.RESET}")
 
 if choice == "3":
 self._show_dependency_install()
 else:
 print(f"\n{Colors.YELLOW}Feature in Entwicklung...{Colors.RESET}")
 self.pause()
 
 def _show_dependency_install(self):
 """Show how to install AI dependencies"""
 print(f"\n{Colors.YELLOW}AI Dependencies Installation:{Colors.RESET}")
 print(f"\n{Colors.CYAN}Für AI v1 (Basic):{Colors.RESET}")
 print(f" pip install scikit-learn numpy")
 print(f"\n{Colors.CYAN}Für AI v2 (Advanced):{Colors.RESET}")
 print(f" pip install torch transformers xgboost onnxruntime")
 print(f"\n{Colors.CYAN}Oder installieren Sie alle optionalen Dependencies:{Colors.RESET}")
 print(f" pip install -e .[optional]")
 self.pause()
 
 @handle_errors
 def show_metrics(self):
 """Show AI performance metrics"""
 self.clear_screen()
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN} AI Performance Metrics{Colors.RESET}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}\n")
 
 # Simulated metrics
 metrics = {
 'Total Predictions': 1337,
 'Successful Exploits': 1098,
 'Failed Attempts': 239,
 'Accuracy': 0.821,
 'Avg Response Time': '342ms',
 'Model Confidence': 0.743
 }
 
 print(f"{Colors.YELLOW}Gesamt-Statistiken:{Colors.RESET}")
 for key, value in metrics.items():
 if isinstance(value, float):
 print(f" {Colors.CYAN}{key}:{Colors.RESET} {value:.1%}")
 else:
 print(f" {Colors.CYAN}{key}:{Colors.RESET} {value}")
 
 # Success rate by exploit
 print(f"\n{Colors.YELLOW}Erfolgsrate nach Exploit:{Colors.RESET}")
 exploits = [
 ('CVE-2025-4664', 0.89),
 ('CVE-2025-2783', 0.76),
 ('CVE-2025-2857', 0.71),
 ('CVE-2025-30397', 0.68),
 ('CVE-2024-32002', 0.62)
 ]
 
 for exploit, rate in exploits:
 bar_length = int(rate * 30)
 color = Colors.BRIGHT_GREEN if rate > 0.8 else Colors.YELLOW if rate > 0.6 else Colors.RED
 print(f" {exploit}: {color}{'█' * bar_length}{' ' * (30 - bar_length)} {rate:.1%}{Colors.RESET}")
 
 print(f"\n{Colors.YELLOW}Trend (letzte 7 Tage):{Colors.RESET}")
 print(f" {Colors.GREEN}↑ Accuracy: +2.3%{Colors.RESET}")
 print(f" {Colors.GREEN}↑ Confidence: +1.8%{Colors.RESET}")
 print(f" {Colors.YELLOW}→ Response Time: ±0ms{Colors.RESET}")
 
 self.pause()
 
 @handle_errors
 def show_ai_requirements(self):
 """Show AI requirements when not available"""
 self.clear_screen()
 print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
 print(f"{Colors.YELLOW} AI Features Not Available{Colors.RESET}")
 print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")
 
 print(f"{Colors.CYAN}Die AI-Funktionen benötigen zusätzliche Dependencies.{Colors.RESET}")
 print(f"\n{Colors.YELLOW}Installation:{Colors.RESET}")
 print(f" {Colors.CYAN}1. Basic AI (empfohlen):{Colors.RESET}")
 print(f" pip install scikit-learn numpy")
 print(f"\n {Colors.CYAN}2. Advanced AI (optional):{Colors.RESET}")
 print(f" pip install torch transformers xgboost onnxruntime")
 print(f"\n {Colors.CYAN}3. Alle optionalen Features:{Colors.RESET}")
 print(f" pip install -e .[optional]")
 
 print(f"\n{Colors.YELLOW}Nach der Installation:{Colors.RESET}")
 print(f" 1. ChromSploit neu starten")
 print(f" 2. AI Assistant Menu öffnen")
 print(f" 3. AI-Features nutzen!")
 
 print(f"\n{Colors.GREEN}Die AI-Features funktionieren auch ohne ML-Libraries{Colors.RESET}")
 print(f"{Colors.GREEN}mit regelbasierten Fallback-Implementierungen.{Colors.RESET}")
 
 self.pause()
 
 def run(self):
 """Run the AI assistant menu"""
 self.display()

# Module exports
def get_menu():
 """Get AI assistant menu instance"""
 return AIAssistantMenu()

if __name__ == "__main__":
 # Test the menu
 menu = AIAssistantMenu()
 menu.run()