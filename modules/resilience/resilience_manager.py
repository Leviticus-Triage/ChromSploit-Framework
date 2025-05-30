import threading
import time
import socket
import subprocess
import json
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class HealthCheck:
    name: str
    check_function: Callable[[], bool]
    interval: int = 30
    timeout: int = 10
    retry_count: int = 3
    critical: bool = False

@dataclass
class ComponentHealth:
    name: str
    status: ComponentStatus
    last_check: float
    failure_count: int = 0
    recovery_actions: List[str] = None

class ResilienceManager:
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        self.recovery_actions: Dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Self-healing configuration
        self.auto_recovery = True
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5 minutes
        
        # Initialize default health checks
        self._setup_default_checks()
        
    def _setup_default_checks(self):
        """Setup default health checks for core components"""
        # Network connectivity check
        self.register_health_check(
            "network_connectivity",
            self._check_network_connectivity,
            interval=60,
            critical=True
        )
        
        # Exploit module availability
        self.register_health_check(
            "exploit_modules",
            self._check_exploit_modules,
            interval=120,
            critical=False
        )
        
        # System resources
        self.register_health_check(
            "system_resources",
            self._check_system_resources,
            interval=45,
            critical=True
        )
        
    def register_health_check(self, name: str, check_function: Callable[[], bool],
                            interval: int = 30, timeout: int = 10,
                            retry_count: int = 3, critical: bool = False):
        """Register a new health check"""
        self.health_checks[name] = HealthCheck(
            name=name,
            check_function=check_function,
            interval=interval,
            timeout=timeout,
            retry_count=retry_count,
            critical=critical
        )
        
        self.component_health[name] = ComponentHealth(
            name=name,
            status=ComponentStatus.HEALTHY,
            last_check=0,
            recovery_actions=[]
        )
        
    def register_recovery_action(self, component: str, action: Callable):
        """Register a recovery action for a component"""
        self.recovery_actions[component] = action
        
    def start_monitoring(self):
        """Start the health monitoring system"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Resilience monitoring started")
        
    def stop_monitoring(self):
        """Stop the health monitoring system"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Resilience monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            current_time = time.time()
            
            for name, health_check in self.health_checks.items():
                component = self.component_health[name]
                
                # Check if it's time for a health check
                if current_time - component.last_check >= health_check.interval:
                    self._perform_health_check(name, health_check)
                    
            time.sleep(10)  # Check every 10 seconds
            
    def _perform_health_check(self, name: str, health_check: HealthCheck):
        """Perform a single health check"""
        component = self.component_health[name]
        component.last_check = time.time()
        
        try:
            # Execute health check with timeout
            result = self._execute_with_timeout(
                health_check.check_function,
                health_check.timeout
            )
            
            if result:
                # Health check passed
                if component.status == ComponentStatus.FAILED:
                    component.status = ComponentStatus.RECOVERING
                    self.logger.info(f"Component {name} is recovering")
                elif component.status == ComponentStatus.RECOVERING:
                    component.status = ComponentStatus.HEALTHY
                    component.failure_count = 0
                    self.logger.info(f"Component {name} has recovered")
                    
            else:
                # Health check failed
                component.failure_count += 1
                
                if component.failure_count >= health_check.retry_count:
                    if component.status != ComponentStatus.FAILED:
                        component.status = ComponentStatus.FAILED
                        self.logger.error(f"Component {name} has failed")
                        
                        # Trigger recovery if enabled
                        if self.auto_recovery:
                            self._trigger_recovery(name, health_check)
                else:
                    component.status = ComponentStatus.DEGRADED
                    self.logger.warning(f"Component {name} is degraded ({component.failure_count}/{health_check.retry_count})")
                    
        except Exception as e:
            self.logger.error(f"Health check for {name} failed with exception: {e}")
            component.failure_count += 1
            component.status = ComponentStatus.FAILED
            
    def _execute_with_timeout(self, func: Callable, timeout: int) -> bool:
        """Execute a function with timeout"""
        result = [False]
        
        def target():
            try:
                result[0] = func()
            except Exception:
                result[0] = False
                
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        return result[0] if not thread.is_alive() else False
        
    def _trigger_recovery(self, component_name: str, health_check: HealthCheck):
        """Trigger recovery actions for a failed component"""
        if component_name in self.recovery_actions:
            try:
                self.logger.info(f"Triggering recovery for {component_name}")
                recovery_action = self.recovery_actions[component_name]
                recovery_action()
                
                # Mark as recovering
                self.component_health[component_name].status = ComponentStatus.RECOVERING
                
            except Exception as e:
                self.logger.error(f"Recovery action for {component_name} failed: {e}")
                
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        total_components = len(self.component_health)
        healthy_count = sum(1 for c in self.component_health.values() 
                          if c.status == ComponentStatus.HEALTHY)
        failed_count = sum(1 for c in self.component_health.values() 
                         if c.status == ComponentStatus.FAILED)
        
        # Determine overall status
        if failed_count == 0:
            overall_status = "healthy"
        elif healthy_count == 0:
            overall_status = "critical"
        else:
            overall_status = "degraded"
            
        return {
            "overall_status": overall_status,
            "total_components": total_components,
            "healthy": healthy_count,
            "failed": failed_count,
            "components": {
                name: {
                    "status": comp.status.value,
                    "last_check": comp.last_check,
                    "failure_count": comp.failure_count
                }
                for name, comp in self.component_health.items()
            }
        }
        
    def _check_network_connectivity(self) -> bool:
        """Check network connectivity"""
        try:
            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except (socket.error, OSError):
            return False
            
    def _check_exploit_modules(self) -> bool:
        """Check if exploit modules are available"""
        try:
            import importlib
            import os
            
            # Check if exploits directory exists and has modules
            exploits_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exploits")
            if not os.path.exists(exploits_dir):
                return False
                
            # Try to import a core exploit module
            spec = importlib.util.find_spec("exploits.cve_2025_4664")
            return spec is not None
            
        except Exception:
            return False
            
    def _check_system_resources(self) -> bool:
        """Check system resource availability"""
        try:
            # Check memory usage
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return False
                
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                return False
                
            return True
            
        except ImportError:
            # Fallback check without psutil
            try:
                # Simple memory check using /proc/meminfo on Linux
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    
                mem_total = None
                mem_available = None
                
                for line in lines:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])
                        
                if mem_total and mem_available:
                    usage_percent = ((mem_total - mem_available) / mem_total) * 100
                    return usage_percent < 90
                    
            except Exception:
                pass
                
            return True  # Assume healthy if we can't check
            
    def force_recovery(self, component_name: str):
        """Manually trigger recovery for a component"""
        if component_name in self.recovery_actions:
            self._trigger_recovery(component_name, self.health_checks[component_name])
        else:
            self.logger.warning(f"No recovery action registered for {component_name}")
            
    def set_component_status(self, component_name: str, status: ComponentStatus):
        """Manually set component status"""
        if component_name in self.component_health:
            self.component_health[component_name].status = status
            self.logger.info(f"Component {component_name} status set to {status.value}")

# Singleton instance
_resilience_manager = None

def get_resilience_manager() -> ResilienceManager:
    """Get the global resilience manager instance"""
    global _resilience_manager
    if _resilience_manager is None:
        _resilience_manager = ResilienceManager()
    return _resilience_manager