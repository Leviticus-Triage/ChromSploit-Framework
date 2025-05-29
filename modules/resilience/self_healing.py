import os
import sys
import time
import subprocess
import logging
import threading
from typing import Dict, List, Callable, Any
from .resilience_manager import get_resilience_manager, ComponentStatus

class SelfHealingSystem:
    def __init__(self):
        self.resilience_manager = get_resilience_manager()
        self.logger = logging.getLogger(__name__)
        self.healing_strategies: Dict[str, List[Callable]] = {}
        self.healing_history: List[Dict[str, Any]] = []
        
        # Setup default healing strategies
        self._setup_default_strategies()
        
    def _setup_default_strategies(self):
        """Setup default self-healing strategies"""
        
        # Network connectivity healing
        self.register_healing_strategy(
            "network_connectivity",
            [
                self._restart_network_interface,
                self._flush_dns_cache,
                self._reset_network_stack
            ]
        )
        
        # Exploit module healing
        self.register_healing_strategy(
            "exploit_modules",
            [
                self._reload_exploit_modules,
                self._repair_module_dependencies,
                self._reinitialize_module_loader
            ]
        )
        
        # System resources healing
        self.register_healing_strategy(
            "system_resources",
            [
                self._clear_system_cache,
                self._garbage_collect,
                self._restart_framework_services
            ]
        )
        
        # Register recovery actions with resilience manager
        for component in self.healing_strategies:
            self.resilience_manager.register_recovery_action(
                component,
                lambda comp=component: self.execute_healing_strategy(comp)
            )
            
    def register_healing_strategy(self, component: str, strategies: List[Callable]):
        """Register healing strategies for a component"""
        self.healing_strategies[component] = strategies
        
    def execute_healing_strategy(self, component: str) -> bool:
        """Execute healing strategies for a component"""
        if component not in self.healing_strategies:
            self.logger.warning(f"No healing strategy for component: {component}")
            return False
            
        strategies = self.healing_strategies[component]
        
        for i, strategy in enumerate(strategies):
            try:
                self.logger.info(f"Executing healing strategy {i+1}/{len(strategies)} for {component}")
                
                # Record healing attempt
                healing_record = {
                    "component": component,
                    "strategy_index": i,
                    "strategy_name": strategy.__name__,
                    "timestamp": time.time(),
                    "success": False
                }
                
                # Execute strategy
                result = strategy()
                healing_record["success"] = result
                self.healing_history.append(healing_record)
                
                if result:
                    self.logger.info(f"Healing strategy {strategy.__name__} succeeded for {component}")
                    return True
                else:
                    self.logger.warning(f"Healing strategy {strategy.__name__} failed for {component}")
                    
            except Exception as e:
                self.logger.error(f"Healing strategy {strategy.__name__} raised exception: {e}")
                healing_record = {
                    "component": component,
                    "strategy_index": i,
                    "strategy_name": strategy.__name__,
                    "timestamp": time.time(),
                    "success": False,
                    "error": str(e)
                }
                self.healing_history.append(healing_record)
                
        self.logger.error(f"All healing strategies failed for component: {component}")
        return False
        
    def _restart_network_interface(self) -> bool:
        """Restart network interface (Linux only)"""
        try:
            if sys.platform.startswith('linux'):
                # Try to restart network manager
                result = subprocess.run(
                    ['sudo', 'systemctl', 'restart', 'NetworkManager'],
                    capture_output=True,
                    timeout=30
                )
                return result.returncode == 0
            else:
                self.logger.info("Network interface restart not supported on this platform")
                return False
        except Exception as e:
            self.logger.error(f"Failed to restart network interface: {e}")
            return False
            
    def _flush_dns_cache(self) -> bool:
        """Flush DNS cache"""
        try:
            if sys.platform.startswith('linux'):
                # Flush systemd-resolved cache
                result = subprocess.run(
                    ['sudo', 'systemd-resolve', '--flush-caches'],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            elif sys.platform == 'darwin':
                # macOS DNS flush
                result = subprocess.run(
                    ['sudo', 'dscacheutil', '-flushcache'],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            elif sys.platform == 'win32':
                # Windows DNS flush
                result = subprocess.run(
                    ['ipconfig', '/flushdns'],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            else:
                return False
        except Exception as e:
            self.logger.error(f"Failed to flush DNS cache: {e}")
            return False
            
    def _reset_network_stack(self) -> bool:
        """Reset network stack"""
        try:
            if sys.platform == 'win32':
                # Windows network stack reset
                commands = [
                    ['netsh', 'winsock', 'reset'],
                    ['netsh', 'int', 'ip', 'reset']
                ]
                
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, timeout=30)
                    if result.returncode != 0:
                        return False
                return True
            else:
                self.logger.info("Network stack reset not implemented for this platform")
                return False
        except Exception as e:
            self.logger.error(f"Failed to reset network stack: {e}")
            return False
            
    def _reload_exploit_modules(self) -> bool:
        """Reload exploit modules"""
        try:
            # Clear module cache
            modules_to_remove = []
            for module_name in sys.modules:
                if module_name.startswith('exploits.'):
                    modules_to_remove.append(module_name)
                    
            for module_name in modules_to_remove:
                del sys.modules[module_name]
                
            # Force reimport of core modules
            import importlib
            try:
                import exploits
                importlib.reload(exploits)
                return True
            except ImportError:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to reload exploit modules: {e}")
            return False
            
    def _repair_module_dependencies(self) -> bool:
        """Repair module dependencies"""
        try:
            # Check and restore critical files
            framework_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            critical_files = [
                os.path.join(framework_root, 'exploits', '__init__.py'),
                os.path.join(framework_root, 'core', '__init__.py'),
                os.path.join(framework_root, 'modules', '__init__.py')
            ]
            
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    # Create missing __init__.py files
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write('# Auto-generated by self-healing system\n')
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to repair module dependencies: {e}")
            return False
            
    def _reinitialize_module_loader(self) -> bool:
        """Reinitialize the module loader"""
        try:
            # Try to get and reinitialize module loader
            from core.module_loader import ModuleLoader
            
            # Create new instance to reset state
            new_loader = ModuleLoader()
            new_loader.scan_modules()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reinitialize module loader: {e}")
            return False
            
    def _clear_system_cache(self) -> bool:
        """Clear system caches"""
        try:
            if sys.platform.startswith('linux'):
                # Clear page cache, dentries and inodes
                result = subprocess.run(
                    ['sudo', 'sync'],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    subprocess.run(
                        ['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'],
                        capture_output=True,
                        timeout=5
                    )
                return True
            else:
                self.logger.info("System cache clearing not supported on this platform")
                return False
        except Exception as e:
            self.logger.error(f"Failed to clear system cache: {e}")
            return False
            
    def _garbage_collect(self) -> bool:
        """Force garbage collection"""
        try:
            import gc
            collected = gc.collect()
            self.logger.info(f"Garbage collection freed {collected} objects")
            return True
        except Exception as e:
            self.logger.error(f"Failed to run garbage collection: {e}")
            return False
            
    def _restart_framework_services(self) -> bool:
        """Restart framework services"""
        try:
            # This would restart any background services
            # For now, just clear internal caches
            
            # Clear any global caches
            if hasattr(sys.modules.get('core.module_loader'), '_instance'):
                delattr(sys.modules['core.module_loader'], '_instance')
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart framework services: {e}")
            return False
            
    def get_healing_history(self, component: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get healing history for analysis"""
        history = self.healing_history
        
        if component:
            history = [h for h in history if h.get('component') == component]
            
        # Return most recent entries
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def start_proactive_healing(self):
        """Start proactive healing monitoring"""
        def healing_monitor():
            while True:
                try:
                    health_status = self.resilience_manager.get_system_health()
                    
                    # Check for components in degraded state
                    for comp_name, comp_data in health_status['components'].items():
                        if comp_data['status'] == 'degraded':
                            # Proactively heal degraded components
                            self.logger.info(f"Proactively healing degraded component: {comp_name}")
                            self.execute_healing_strategy(comp_name)
                            
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Proactive healing monitor error: {e}")
                    time.sleep(60)
                    
        monitor_thread = threading.Thread(target=healing_monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("Proactive healing monitor started")

# Singleton instance
_self_healing_system = None

def get_self_healing_system() -> SelfHealingSystem:
    """Get the global self-healing system instance"""
    global _self_healing_system
    if _self_healing_system is None:
        _self_healing_system = SelfHealingSystem()
    return _self_healing_system