#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Module Loader
Dynamic loading system for optional components with fallback mechanisms
"""

import os
import sys
import importlib.util
import threading
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """Information about a loadable module"""
    name: str
    path: str
    dependencies: List[str]
    description: str
    version: str
    enabled: bool = False
    loaded: bool = False
    instance: Optional[Any] = None
    fallback: Optional[str] = None


class ModuleLoader:
    """
    Dynamic module loader for optional components with dependency checking
    and fallback mechanisms
    """
    
    def __init__(self, config_path: str = None):
        self.modules_dir = Path(__file__).parent.parent / "modules"
        self.config_path = config_path or "config/modules.json"
        self.loaded_modules: Dict[str, ModuleInfo] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # Module registry
        self.available_modules = {
            'ai_orchestrator': ModuleInfo(
                name='ai_orchestrator',
                path='modules.ai.ai_orchestrator',
                dependencies=['torch', 'onnxruntime', 'xgboost', 'transformers'],
                description='AI-powered exploit and payload selection',
                version='2.0',
                fallback='legacy_cve_matcher'
            ),
            'resilience': ModuleInfo(
                name='resilience',
                path='modules.resilience.resilience_module',
                dependencies=['pybreaker', 'psutil'],
                description='Self-healing infrastructure components',
                version='1.0',
                fallback='basic_error_handler'
            ),
            'ollvm_obfuscator': ModuleInfo(
                name='ollvm_obfuscator',
                path='modules.obfuscation.ollvm_handler',
                dependencies=['docker'],
                description='OLLVM-based binary obfuscation',
                version='1.0',
                fallback='xor_obfuscator'
            ),
            'advanced_reporting': ModuleInfo(
                name='advanced_reporting',
                path='modules.reporting.advanced_reporter',
                dependencies=['jinja2', 'weasyprint', 'plotly'],
                description='Enhanced reporting with visualizations',
                version='1.0',
                fallback='basic_reporter'
            )
        }
        
        self._init_fallback_handlers()
        
    def _init_fallback_handlers(self):
        """Initialize fallback handlers"""
        self.fallback_handlers = {
            'legacy_cve_matcher': self._legacy_cve_matcher,
            'basic_error_handler': self._basic_error_handler,
            'xor_obfuscator': self._xor_obfuscator,
            'basic_reporter': self._basic_reporter
        }
    
    def check_dependencies(self, module_name: str) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies for a module are available
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            Tuple of (all_available, missing_dependencies)
        """
        if module_name not in self.available_modules:
            return False, [f"Module {module_name} not found"]
            
        module_info = self.available_modules[module_name]
        missing = []
        
        for dep in module_info.dependencies:
            if not self._check_dependency_available(dep):
                missing.append(dep)
                
        return len(missing) == 0, missing
    
    def _check_dependency_available(self, dependency: str) -> bool:
        """Check if a single dependency is available"""
        try:
            # Check for Python modules
            if '.' not in dependency:
                spec = importlib.util.find_spec(dependency)
                return spec is not None
            
            # Check for system tools
            if dependency == 'docker':
                import subprocess
                result = subprocess.run(['docker', '--version'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
                
            return False
        except Exception:
            return False
    
    def load_module(self, module_name: str, force: bool = False) -> Optional[Any]:
        """
        Load a module with dependency checking and fallback
        
        Args:
            module_name: Name of the module to load
            force: Force loading even if dependencies are missing
            
        Returns:
            Module instance or fallback handler
        """
        with self.lock:
            # Check if already loaded
            if module_name in self.loaded_modules and self.loaded_modules[module_name].loaded:
                return self.loaded_modules[module_name].instance
                
            # Check if module exists
            if module_name not in self.available_modules:
                logger.error(f"Module {module_name} not found")
                return None
                
            module_info = self.available_modules[module_name]
            
            # Check dependencies
            deps_ok, missing = self.check_dependencies(module_name)
            
            if not deps_ok and not force:
                logger.warning(f"Missing dependencies for {module_name}: {missing}")
                
                # Try fallback
                if module_info.fallback:
                    logger.info(f"Using fallback {module_info.fallback} for {module_name}")
                    return self._get_fallback_handler(module_info.fallback)
                    
                return None
                
            # Load the module
            try:
                module = importlib.import_module(module_info.path)
                
                # Get the main class (assumes class name is CamelCase of module name)
                class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                if hasattr(module, class_name):
                    instance = getattr(module, class_name)()
                else:
                    # Try common patterns
                    for pattern in [f"{class_name}Module", f"{class_name}Handler", class_name]:
                        if hasattr(module, pattern):
                            instance = getattr(module, pattern)()
                            break
                    else:
                        logger.error(f"No suitable class found in {module_info.path}")
                        return self._get_fallback_handler(module_info.fallback)
                
                # Update module info
                module_info.loaded = True
                module_info.enabled = True
                module_info.instance = instance
                self.loaded_modules[module_name] = module_info
                
                logger.info(f"Successfully loaded module {module_name}")
                return instance
                
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {e}")
                
                # Try fallback
                if module_info.fallback:
                    logger.info(f"Using fallback {module_info.fallback} for {module_name}")
                    return self._get_fallback_handler(module_info.fallback)
                    
                return None
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a loaded module instance"""
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name].instance
        return None
    
    def check_optional_deps(self) -> Dict[str, bool]:
        """Check optional dependencies for all modules"""
        result = {}
        for module_name in self.available_modules:
            deps_ok, _ = self.check_dependencies(module_name)
            result[module_name] = deps_ok
        return result
    
    def load_optional_modules(self) -> Dict[str, bool]:
        """Load all optional modules"""
        result = {}
        for module_name in self.available_modules:
            instance = self.load_module(module_name)
            result[module_name] = instance is not None
        return result
    
    def list_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """List all available modules with their status"""
        result = {}
        for name, info in self.available_modules.items():
            deps_ok, missing = self.check_dependencies(name)
            result[name] = {
                'description': info.description,
                'version': info.version,
                'dependencies': info.dependencies,
                'dependencies_ok': deps_ok,
                'missing_dependencies': missing,
                'loaded': info.loaded,
                'enabled': info.enabled,
                'fallback': info.fallback
            }
        return result
    
    def _get_fallback_handler(self, fallback_name: str) -> Optional[Callable]:
        """Get a fallback handler"""
        return self.fallback_handlers.get(fallback_name)
    
    # Fallback implementations
    def _legacy_cve_matcher(self):
        """Fallback CVE matcher when AI orchestrator is unavailable"""
        class LegacyCVEMatcher:
            def recommend_exploit(self, target_data: Dict) -> str:
                """Simple rule-based exploit recommendation"""
                browser = target_data.get('browser', '').lower()
                os_type = target_data.get('os_type', '').lower()
                
                if 'chrome' in browser:
                    if 'windows' in os_type:
                        return 'CVE-2025-2783'  # Chrome Mojo Sandbox Escape
                    else:
                        return 'CVE-2025-4664'  # Chrome Data Leak
                elif 'firefox' in browser:
                    return 'CVE-2025-2857'  # Firefox Sandbox Escape
                elif 'edge' in browser:
                    return 'CVE-2025-30397'  # Edge WebAssembly JIT
                else:
                    return 'CVE-2025-4664'  # Default to Chrome Data Leak
                    
            def analyze_target(self, target_data: Dict) -> Dict:
                """Simple target analysis"""
                return {
                    'recommended_exploit': self.recommend_exploit(target_data),
                    'confidence': 0.7,
                    'reasoning': 'Rule-based recommendation',
                    'fallback': True
                }
        
        return LegacyCVEMatcher()
    
    def _basic_error_handler(self):
        """Basic error handling fallback"""
        class BasicErrorHandler:
            def handle_error(self, error: Exception, context: str) -> bool:
                logger.error(f"Error in {context}: {error}")
                return True
                
            def is_healthy(self) -> bool:
                return True
                
            def restart_service(self, service_name: str) -> bool:
                logger.info(f"Basic restart attempt for {service_name}")
                return False
        
        return BasicErrorHandler()
    
    def _xor_obfuscator(self):
        """Simple XOR obfuscation fallback"""
        class XORObfuscator:
            def obfuscate_payload(self, payload: bytes, key: int = 0xAA) -> bytes:
                """Simple XOR obfuscation"""
                return bytes(b ^ key for b in payload)
                
            def generate_decoder_stub(self, key: int = 0xAA) -> str:
                """Generate decoder stub"""
                return f"""
                def decode(data):
                    return bytes(b ^ {key} for b in data)
                """
                
            def obfuscate_string(self, text: str, key: int = 0xAA) -> str:
                """Obfuscate string with XOR"""
                encoded = self.obfuscate_payload(text.encode(), key)
                return encoded.hex()
        
        return XORObfuscator()
    
    def _basic_reporter(self):
        """Basic reporting fallback"""
        class BasicReporter:
            def generate_report(self, data: Dict) -> str:
                """Generate basic text report"""
                report = "ChromSploit Framework Report\n"
                report += "=" * 30 + "\n\n"
                
                for key, value in data.items():
                    report += f"{key}: {value}\n"
                
                return report
                
            def export_json(self, data: Dict, filename: str) -> bool:
                """Export data as JSON"""
                try:
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Failed to export JSON: {e}")
                    return False
        
        return BasicReporter()


# Global instance
_module_loader = None

def get_module_loader() -> ModuleLoader:
    """Get or create module loader instance"""
    global _module_loader
    if _module_loader is None:
        _module_loader = ModuleLoader()
    return _module_loader


def load_module(module_name: str) -> Optional[Any]:
    """Convenience function to load a module"""
    loader = get_module_loader()
    return loader.load_module(module_name)


def get_module(module_name: str) -> Optional[Any]:
    """Convenience function to get a loaded module"""
    loader = get_module_loader()
    return loader.get_module(module_name)