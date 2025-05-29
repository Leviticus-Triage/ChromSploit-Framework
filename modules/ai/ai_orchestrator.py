#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - AI Orchestrator
Intelligent exploit selection and attack optimization using ML
"""

import os
import json
import time
import pickle
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

# Optional ML dependencies - graceful fallback if not available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - using fallback AI implementation")

try:
    import sklearn
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available - using simplified AI")


@dataclass
class TargetProfile:
    """Target system profile for AI analysis"""
    browser: str
    version: str
    os_type: str
    os_version: str
    architecture: str
    security_features: List[str]
    network_context: str
    user_privileges: str
    additional_info: Dict[str, Any]


@dataclass
class ExploitRecommendation:
    """AI exploit recommendation"""
    cve_id: str
    confidence: float
    reasoning: str
    success_probability: float
    risk_level: str
    parameters: Dict[str, Any]
    alternatives: List[str]


class SimpleNeuralNetwork:
    """Simplified neural network for target analysis when PyTorch unavailable"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, output_size: int = 4):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize weights randomly
        np.random.seed(42)
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def forward(self, X):
        z1 = np.dot(X, self.W1) + self.b1
        a1 = self.sigmoid(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        a2 = self.softmax(z2)
        return a2
    
    def predict(self, X):
        probabilities = self.forward(X)
        return np.argmax(probabilities, axis=1), probabilities


class AIOrchestrator:
    """AI-powered exploit orchestrator with fallback mechanisms"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "/tmp/chromsploit_ai_models"
        self.models_loaded = False
        
        # CVE mappings
        self.cve_mappings = {
            0: 'CVE-2025-4664',  # Chrome Data Leak
            1: 'CVE-2025-2783',  # Chrome Mojo Sandbox Escape
            2: 'CVE-2025-2857',  # Firefox Sandbox Escape
            3: 'CVE-2025-30397'  # Edge WebAssembly JIT
        }
        
        # Feature extractors
        self.feature_extractors = {
            'browser': {'chrome': 1, 'firefox': 2, 'edge': 3, 'safari': 4, 'other': 0},
            'os_type': {'windows': 1, 'linux': 2, 'macos': 3, 'android': 4, 'ios': 5, 'other': 0},
            'architecture': {'x64': 1, 'x86': 2, 'arm': 3, 'arm64': 4, 'other': 0},
            'user_privileges': {'admin': 3, 'user': 2, 'guest': 1, 'unknown': 0}
        }
        
        # Initialize models
        self._initialize_models()
        
        # Load training data and models
        self._load_or_create_models()
        
    def _initialize_models(self):
        """Initialize AI models based on available libraries"""
        self.neural_network = None
        self.random_forest = None
        self.scaler = None
        
        # Initialize simple neural network
        self.neural_network = SimpleNeuralNetwork(input_size=20, output_size=4)
        
        # Initialize random forest if sklearn available
        if SKLEARN_AVAILABLE:
            self.random_forest = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()
            
        logger.info("AI models initialized with available libraries")
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            
            # Try to load existing models
            model_file = os.path.join(self.model_path, "exploit_classifier.pkl")
            
            if os.path.exists(model_file):
                self._load_models(model_file)
            else:
                self._create_synthetic_training_data()
                self._train_models()
                
            self.models_loaded = True
            logger.info("AI models ready for inference")
            
        except Exception as e:
            logger.warning(f"Failed to load/create AI models: {e}")
            self.models_loaded = False
    
    def _load_models(self, model_file: str):
        """Load pre-trained models"""
        try:
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
                
            if SKLEARN_AVAILABLE and 'random_forest' in model_data:
                self.random_forest = model_data['random_forest']
                self.scaler = model_data['scaler']
                
            if 'neural_network' in model_data:
                nn_data = model_data['neural_network']
                self.neural_network.W1 = nn_data['W1']
                self.neural_network.b1 = nn_data['b1']
                self.neural_network.W2 = nn_data['W2']
                self.neural_network.b2 = nn_data['b2']
                
            logger.info("Pre-trained models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self._create_synthetic_training_data()
            self._train_models()
    
    def _create_synthetic_training_data(self):
        """Create synthetic training data for model training"""
        logger.info("Creating synthetic training data...")
        
        # Generate synthetic data based on CVE characteristics
        training_data = []
        labels = []
        
        # CVE-2025-4664 (Chrome Data Leak) - targets Chrome on any OS
        for _ in range(250):
            features = self._create_feature_vector({
                'browser': 'chrome',
                'os_type': np.random.choice(['windows', 'linux', 'macos']),
                'architecture': np.random.choice(['x64', 'x86']),
                'user_privileges': np.random.choice(['admin', 'user']),
                'security_features': np.random.choice([[], ['aslr'], ['dep'], ['aslr', 'dep']]),
                'version': f"12{np.random.randint(0, 9)}.0",
                'network_context': np.random.choice(['local', 'remote']),
                'additional_info': {}
            })
            training_data.append(features)
            labels.append(0)  # CVE-2025-4664
        
        # CVE-2025-2783 (Chrome Mojo Sandbox Escape) - Windows Chrome specifically
        for _ in range(200):
            features = self._create_feature_vector({
                'browser': 'chrome',
                'os_type': 'windows',
                'architecture': np.random.choice(['x64', 'x86']),
                'user_privileges': np.random.choice(['user', 'admin']),
                'security_features': np.random.choice([['aslr'], ['dep'], ['aslr', 'dep']]),
                'version': f"12{np.random.randint(0, 9)}.0",
                'network_context': 'local',
                'additional_info': {}
            })
            training_data.append(features)
            labels.append(1)  # CVE-2025-2783
        
        # CVE-2025-2857 (Firefox Sandbox Escape) - Firefox targets
        for _ in range(200):
            features = self._create_feature_vector({
                'browser': 'firefox',
                'os_type': np.random.choice(['windows', 'linux']),
                'architecture': np.random.choice(['x64', 'x86']),
                'user_privileges': np.random.choice(['user', 'admin']),
                'security_features': np.random.choice([[], ['aslr'], ['dep']]),
                'version': f"11{np.random.randint(0, 9)}.0",
                'network_context': np.random.choice(['local', 'remote']),
                'additional_info': {}
            })
            training_data.append(features)
            labels.append(2)  # CVE-2025-2857
        
        # CVE-2025-30397 (Edge WebAssembly JIT) - Edge/IE mode targets
        for _ in range(150):
            features = self._create_feature_vector({
                'browser': 'edge',
                'os_type': 'windows',
                'architecture': np.random.choice(['x64', 'x86']),
                'user_privileges': np.random.choice(['user', 'admin']),
                'security_features': np.random.choice([['aslr'], ['dep'], ['aslr', 'dep']]),
                'version': f"1{np.random.randint(10, 20)}.0",
                'network_context': 'remote',
                'additional_info': {}
            })
            training_data.append(features)
            labels.append(3)  # CVE-2025-30397
        
        self.training_data = np.array(training_data)
        self.training_labels = np.array(labels)
        
        logger.info(f"Created {len(training_data)} synthetic training samples")
    
    def _train_models(self):
        """Train the AI models"""
        logger.info("Training AI models...")
        
        try:
            # Train Random Forest if sklearn available
            if SKLEARN_AVAILABLE and self.random_forest is not None:
                # Scale features
                X_scaled = self.scaler.fit_transform(self.training_data)
                
                # Train classifier
                self.random_forest.fit(X_scaled, self.training_labels)
                logger.info("Random Forest model trained")
            
            # Simple training for neural network (just update weights slightly)
            if self.neural_network is not None:
                # Simple weight adjustment based on data distribution
                for i in range(len(self.cve_mappings)):
                    class_mask = self.training_labels == i
                    if np.any(class_mask):
                        class_data = self.training_data[class_mask]
                        class_mean = np.mean(class_data, axis=0)
                        
                        # Adjust weights to favor this class for similar inputs
                        self.neural_network.W2[:, i] += 0.1 * class_mean[:self.neural_network.hidden_size]
                
                logger.info("Neural network weights adjusted")
            
            # Save trained models
            self._save_models()
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            model_data = {}
            
            if SKLEARN_AVAILABLE and self.random_forest is not None:
                model_data['random_forest'] = self.random_forest
                model_data['scaler'] = self.scaler
            
            if self.neural_network is not None:
                model_data['neural_network'] = {
                    'W1': self.neural_network.W1,
                    'b1': self.neural_network.b1,
                    'W2': self.neural_network.W2,
                    'b2': self.neural_network.b2
                }
            
            model_file = os.path.join(self.model_path, "exploit_classifier.pkl")
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
                
            logger.info(f"Models saved to {model_file}")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def _create_feature_vector(self, target_data: Dict[str, Any]) -> List[float]:
        """Create feature vector from target data"""
        features = []
        
        # Browser features
        browser = target_data.get('browser', 'other').lower()
        features.append(self.feature_extractors['browser'].get(browser, 0))
        
        # OS features
        os_type = target_data.get('os_type', 'other').lower()
        features.append(self.feature_extractors['os_type'].get(os_type, 0))
        
        # Architecture features
        arch = target_data.get('architecture', 'other').lower()
        features.append(self.feature_extractors['architecture'].get(arch, 0))
        
        # User privilege features
        privileges = target_data.get('user_privileges', 'unknown').lower()
        features.append(self.feature_extractors['user_privileges'].get(privileges, 0))
        
        # Security features (binary indicators)
        security_features = target_data.get('security_features', [])
        features.append(1 if 'aslr' in security_features else 0)
        features.append(1 if 'dep' in security_features else 0)
        features.append(1 if 'smep' in security_features else 0)
        features.append(1 if 'smap' in security_features else 0)
        features.append(1 if 'kaslr' in security_features else 0)
        
        # Version parsing (simplified)
        version = target_data.get('version', '0.0')
        try:
            major_version = float(version.split('.')[0])
            features.append(major_version / 100.0)  # Normalize
        except:
            features.append(0.0)
        
        # Network context
        network = target_data.get('network_context', 'unknown').lower()
        features.append(1 if network == 'local' else 0)
        features.append(1 if network == 'remote' else 0)
        
        # Additional binary features
        additional = target_data.get('additional_info', {})
        features.append(1 if additional.get('sandboxed', False) else 0)
        features.append(1 if additional.get('elevated', False) else 0)
        features.append(1 if additional.get('virtualized', False) else 0)
        features.append(1 if additional.get('patched', False) else 0)
        features.append(1 if additional.get('av_present', False) else 0)
        features.append(1 if additional.get('firewall_active', False) else 0)
        features.append(1 if additional.get('updated', False) else 0)
        
        # Pad to fixed size
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]  # Ensure fixed size
    
    def analyze_target(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze target and provide recommendations"""
        try:
            # Create feature vector
            features = self._create_feature_vector(target_data)
            features_array = np.array([features])
            
            # Get predictions from available models
            predictions = {}
            
            # Random Forest prediction
            if SKLEARN_AVAILABLE and self.random_forest is not None and self.scaler is not None:
                try:
                    features_scaled = self.scaler.transform(features_array)
                    rf_pred = self.random_forest.predict(features_scaled)[0]
                    rf_proba = self.random_forest.predict_proba(features_scaled)[0]
                    
                    predictions['random_forest'] = {
                        'prediction': int(rf_pred),
                        'confidence': float(max(rf_proba)),
                        'probabilities': rf_proba.tolist()
                    }
                except Exception as e:
                    logger.warning(f"Random Forest prediction failed: {e}")
            
            # Neural Network prediction
            if self.neural_network is not None:
                try:
                    nn_pred, nn_proba = self.neural_network.predict(features_array)
                    
                    predictions['neural_network'] = {
                        'prediction': int(nn_pred[0]),
                        'confidence': float(max(nn_proba[0])),
                        'probabilities': nn_proba[0].tolist()
                    }
                except Exception as e:
                    logger.warning(f"Neural Network prediction failed: {e}")
            
            # Ensemble prediction (if multiple models available)
            if len(predictions) > 1:
                # Average probabilities
                all_probas = [pred['probabilities'] for pred in predictions.values()]
                avg_probas = np.mean(all_probas, axis=0)
                final_prediction = np.argmax(avg_probas)
                final_confidence = max(avg_probas)
                ensemble_method = "ensemble"
            elif predictions:
                # Use single model
                model_name = list(predictions.keys())[0]
                model_pred = predictions[model_name]
                final_prediction = model_pred['prediction']
                final_confidence = model_pred['confidence']
                avg_probas = model_pred['probabilities']
                ensemble_method = model_name
            else:
                # Fallback to rule-based
                final_prediction, final_confidence, avg_probas = self._rule_based_prediction(target_data)
                ensemble_method = "rule_based"
            
            # Get recommended CVE
            recommended_cve = self.cve_mappings.get(final_prediction, 'CVE-2025-4664')
            
            # Generate alternatives
            alternatives = []
            for i, prob in enumerate(avg_probas):
                if i != final_prediction and prob > 0.1:  # At least 10% confidence
                    alternatives.append(self.cve_mappings.get(i, f'CVE-{i}'))
            
            # Calculate success probability and risk
            success_probability = self._calculate_success_probability(target_data, recommended_cve)
            risk_level = self._calculate_risk_level(target_data, recommended_cve)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(target_data, recommended_cve, final_confidence, ensemble_method)
            
            return {
                'recommended_exploit': recommended_cve,
                'confidence': final_confidence,
                'success_probability': success_probability,
                'risk_level': risk_level,
                'reasoning': reasoning,
                'alternatives': alternatives,
                'model_predictions': predictions,
                'ensemble_method': ensemble_method,
                'target_analysis': {
                    'browser_compatibility': self._assess_browser_compatibility(target_data, recommended_cve),
                    'os_compatibility': self._assess_os_compatibility(target_data, recommended_cve),
                    'security_obstacles': self._identify_security_obstacles(target_data),
                    'recommended_parameters': self._get_recommended_parameters(target_data, recommended_cve)
                }
            }
            
        except Exception as e:
            logger.error(f"Target analysis failed: {e}")
            return self._fallback_analysis(target_data)
    
    def _rule_based_prediction(self, target_data: Dict[str, Any]) -> Tuple[int, float, List[float]]:
        """Fallback rule-based prediction"""
        browser = target_data.get('browser', '').lower()
        os_type = target_data.get('os_type', '').lower()
        
        # Simple rule-based logic
        if 'chrome' in browser:
            if 'windows' in os_type:
                return 1, 0.8, [0.1, 0.8, 0.05, 0.05]  # CVE-2025-2783
            else:
                return 0, 0.75, [0.75, 0.15, 0.05, 0.05]  # CVE-2025-4664
        elif 'firefox' in browser:
            return 2, 0.85, [0.05, 0.05, 0.85, 0.05]  # CVE-2025-2857
        elif 'edge' in browser:
            return 3, 0.9, [0.05, 0.05, 0.0, 0.9]  # CVE-2025-30397
        else:
            return 0, 0.6, [0.6, 0.2, 0.1, 0.1]  # Default to CVE-2025-4664
    
    def _calculate_success_probability(self, target_data: Dict[str, Any], cve_id: str) -> float:
        """Calculate estimated success probability"""
        base_probability = 0.7
        
        # Adjust based on browser compatibility
        browser = target_data.get('browser', '').lower()
        if cve_id == 'CVE-2025-4664' and 'chrome' in browser:
            base_probability += 0.15
        elif cve_id == 'CVE-2025-2783' and 'chrome' in browser:
            base_probability += 0.2
        elif cve_id == 'CVE-2025-2857' and 'firefox' in browser:
            base_probability += 0.18
        elif cve_id == 'CVE-2025-30397' and 'edge' in browser:
            base_probability += 0.25
        
        # Adjust based on security features
        security_features = target_data.get('security_features', [])
        for feature in security_features:
            base_probability -= 0.05  # Each security feature reduces probability
        
        # Adjust based on patches
        if target_data.get('additional_info', {}).get('patched', False):
            base_probability -= 0.3
        
        return max(0.1, min(0.95, base_probability))
    
    def _calculate_risk_level(self, target_data: Dict[str, Any], cve_id: str) -> str:
        """Calculate risk level of exploitation"""
        risk_factors = 0
        
        # Network context
        if target_data.get('network_context') == 'remote':
            risk_factors += 1
        
        # User privileges
        if target_data.get('user_privileges') == 'admin':
            risk_factors += 2
        
        # Security monitoring
        additional = target_data.get('additional_info', {})
        if additional.get('av_present', False):
            risk_factors += 1
        if additional.get('firewall_active', False):
            risk_factors += 1
        
        # CVE-specific risks
        if cve_id in ['CVE-2025-2783', 'CVE-2025-2857']:  # Sandbox escapes
            risk_factors += 1
        
        if risk_factors <= 2:
            return 'low'
        elif risk_factors <= 4:
            return 'medium'
        else:
            return 'high'
    
    def _generate_reasoning(self, target_data: Dict[str, Any], cve_id: str, 
                          confidence: float, method: str) -> str:
        """Generate human-readable reasoning"""
        browser = target_data.get('browser', 'unknown')
        os_type = target_data.get('os_type', 'unknown')
        
        reasons = []
        
        # Model-based reasoning
        if method == 'ensemble':
            reasons.append(f"Multiple AI models agree with {confidence:.1%} confidence")
        elif method == 'rule_based':
            reasons.append("Based on rule-based analysis")
        else:
            reasons.append(f"AI model ({method}) recommends with {confidence:.1%} confidence")
        
        # CVE-specific reasoning
        if cve_id == 'CVE-2025-4664':
            reasons.append(f"Chrome data leak exploit suitable for {browser} on {os_type}")
        elif cve_id == 'CVE-2025-2783':
            reasons.append(f"Mojo IPC sandbox escape optimal for Chrome on Windows")
        elif cve_id == 'CVE-2025-2857':
            reasons.append(f"IPDL handle confusion targets Firefox processes")
        elif cve_id == 'CVE-2025-30397':
            reasons.append(f"WebAssembly JIT exploit designed for Edge browser")
        
        # Security considerations
        security_features = target_data.get('security_features', [])
        if security_features:
            reasons.append(f"Security features detected: {', '.join(security_features)}")
        
        return '. '.join(reasons) + '.'
    
    def _assess_browser_compatibility(self, target_data: Dict[str, Any], cve_id: str) -> str:
        """Assess browser compatibility"""
        browser = target_data.get('browser', '').lower()
        
        compatibility_map = {
            'CVE-2025-4664': ['chrome', 'chromium'],
            'CVE-2025-2783': ['chrome', 'chromium'],
            'CVE-2025-2857': ['firefox'],
            'CVE-2025-30397': ['edge', 'ie']
        }
        
        compatible_browsers = compatibility_map.get(cve_id, [])
        
        if any(comp in browser for comp in compatible_browsers):
            return 'high'
        elif 'chrome' in browser and cve_id.startswith('CVE-2025-4'):
            return 'medium'
        else:
            return 'low'
    
    def _assess_os_compatibility(self, target_data: Dict[str, Any], cve_id: str) -> str:
        """Assess OS compatibility"""
        os_type = target_data.get('os_type', '').lower()
        
        if cve_id in ['CVE-2025-2783', 'CVE-2025-30397'] and 'windows' in os_type:
            return 'high'
        elif cve_id == 'CVE-2025-4664':  # Works on multiple OS
            return 'high'
        elif cve_id == 'CVE-2025-2857' and os_type in ['windows', 'linux']:
            return 'high'
        else:
            return 'medium'
    
    def _identify_security_obstacles(self, target_data: Dict[str, Any]) -> List[str]:
        """Identify potential security obstacles"""
        obstacles = []
        
        security_features = target_data.get('security_features', [])
        obstacles.extend(security_features)
        
        additional = target_data.get('additional_info', {})
        if additional.get('av_present', False):
            obstacles.append('Antivirus protection')
        if additional.get('firewall_active', False):
            obstacles.append('Active firewall')
        if additional.get('sandboxed', True):
            obstacles.append('Browser sandbox')
        if additional.get('patched', False):
            obstacles.append('Recent security patches')
        
        return obstacles
    
    def _get_recommended_parameters(self, target_data: Dict[str, Any], cve_id: str) -> Dict[str, Any]:
        """Get recommended exploit parameters"""
        params = {}
        
        # Common parameters
        params['target_browser'] = target_data.get('browser', 'chrome')
        params['target_os'] = target_data.get('os_type', 'windows')
        
        # CVE-specific parameters
        if cve_id == 'CVE-2025-4664':
            params.update({
                'link_header_size': 8192,
                'memory_leak_size': 1024,
                'mode': 'exploit'
            })
        elif cve_id == 'CVE-2025-2783':
            params.update({
                'mojo_interface': 'NodeController',
                'handle_count': 1024,
                'payload_type': 'reverse_shell'
            })
        elif cve_id == 'CVE-2025-2857':
            params.update({
                'ipdl_interface': 'PContent',
                'handle_confusion': True
            })
        elif cve_id == 'CVE-2025-30397':
            params.update({
                'wasm_module_size': 4096,
                'jit_spray_count': 1000
            })
        
        return params
    
    def _fallback_analysis(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        browser = target_data.get('browser', 'chrome').lower()
        
        # Simple fallback logic
        if 'chrome' in browser:
            recommended = 'CVE-2025-4664'
        elif 'firefox' in browser:
            recommended = 'CVE-2025-2857'
        elif 'edge' in browser:
            recommended = 'CVE-2025-30397'
        else:
            recommended = 'CVE-2025-4664'
        
        return {
            'recommended_exploit': recommended,
            'confidence': 0.6,
            'success_probability': 0.7,
            'risk_level': 'medium',
            'reasoning': 'Fallback rule-based recommendation due to AI system unavailability',
            'alternatives': [],
            'fallback': True
        }
    
    def recommend_exploit(self, target_data: Dict[str, Any]) -> str:
        """Simple exploit recommendation (for compatibility)"""
        analysis = self.analyze_target(target_data)
        return analysis.get('recommended_exploit', 'CVE-2025-4664')
    
    def update_model(self, target_data: Dict[str, Any], actual_cve: str, success: bool):
        """Update model with feedback (placeholder for future ML improvements)"""
        logger.info(f"Feedback received: {actual_cve} {'succeeded' if success else 'failed'} on {target_data.get('browser', 'unknown')}")
        
        # In a production system, this would update the model weights
        # For now, just log the feedback for future training
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'target_data': target_data,
            'recommended_cve': actual_cve,
            'success': success
        }
        
        feedback_file = os.path.join(self.model_path, "feedback.jsonl")
        with open(feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')