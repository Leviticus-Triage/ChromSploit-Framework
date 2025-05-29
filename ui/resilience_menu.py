#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime
from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors

class ResilienceMenu(EnhancedMenu):
    def __init__(self):
        super().__init__("Resilience & Self-Healing System")
        self.logger = get_logger()
        
        # Try to import resilience modules
        try:
            from modules.resilience import get_resilience_manager, get_self_healing_system
            self.resilience_manager = get_resilience_manager()
            self.self_healing_system = get_self_healing_system()
            self.resilience_available = True
        except ImportError:
            self.resilience_available = False
            
        self._setup_menu_items()
        
    def _setup_menu_items(self):
        """Setup menu items"""
        if not self.resilience_available:
            self.add_enhanced_item(
                "install", "Install Resilience Dependencies", 
                self._install_dependencies,
                description="Install required packages for resilience system"
            )
            return
            
        self.add_enhanced_item(
            "status", "System Health Status", 
            self._show_health_status,
            description="View current system health and component status"
        )
        
        self.add_enhanced_item(
            "monitor", "Health Monitoring", 
            self._health_monitoring_menu,
            description="Configure and control health monitoring"
        )
        
        self.add_enhanced_item(
            "healing", "Self-Healing System", 
            self._self_healing_menu,
            description="Manage self-healing strategies and history"
        )
        
        self.add_enhanced_item(
            "components", "Component Management", 
            self._component_management_menu,
            description="Manage individual component health checks"
        )
        
        self.add_enhanced_item(
            "history", "Healing History", 
            self._view_healing_history,
            description="View history of healing actions"
        )
        
        self.add_enhanced_item(
            "test", "Test Recovery", 
            self._test_recovery_menu,
            description="Test recovery procedures for components"
        )
        
    @handle_errors
    def _install_dependencies(self):
        """Install resilience system dependencies"""
        print(f"\n{Colors.CYAN}[*] Installing Resilience Dependencies{Colors.RESET}")
        
        dependencies = [
            "psutil",  # For system resource monitoring
            "requests",  # For network health checks
        ]
        
        print(f"{Colors.BLUE}[+] Required packages:{Colors.RESET}")
        for dep in dependencies:
            print(f"  - {dep}")
            
        confirm = input(f"\n{Colors.YELLOW}Install dependencies? (y/N): {Colors.RESET}")
        if confirm.lower() == 'y':
            import subprocess
            import sys
            
            for dep in dependencies:
                try:
                    print(f"{Colors.CYAN}[*] Installing {dep}...{Colors.RESET}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                    print(f"{Colors.GREEN}[+] {dep} installed successfully{Colors.RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.RED}[!] Failed to install {dep}: {e}{Colors.RESET}")
                    
            print(f"{Colors.GREEN}[+] Dependencies installation completed{Colors.RESET}")
            print(f"{Colors.YELLOW}[!] Please restart the framework to use resilience features{Colors.RESET}")
        
    @handle_errors
    def _show_health_status(self):
        """Show current system health status"""
        print(f"\n{Colors.CYAN}=== System Health Status ==={Colors.RESET}")
        
        health = self.resilience_manager.get_system_health()
        
        # Overall status
        status_color = Colors.GREEN if health['overall_status'] == 'healthy' else \
                      Colors.YELLOW if health['overall_status'] == 'degraded' else Colors.RED
        
        print(f"{Colors.BLUE}Overall Status:{Colors.RESET} {status_color}{health['overall_status'].upper()}{Colors.RESET}")
        print(f"{Colors.BLUE}Total Components:{Colors.RESET} {health['total_components']}")
        print(f"{Colors.BLUE}Healthy Components:{Colors.RESET} {Colors.GREEN}{health['healthy']}{Colors.RESET}")
        print(f"{Colors.BLUE}Failed Components:{Colors.RESET} {Colors.RED}{health['failed']}{Colors.RESET}")
        
        # Component details
        print(f"\n{Colors.CYAN}=== Component Details ==={Colors.RESET}")
        for name, component in health['components'].items():
            status = component['status']
            status_color = Colors.GREEN if status == 'healthy' else \
                          Colors.YELLOW if status in ['degraded', 'recovering'] else Colors.RED
            
            last_check = datetime.fromtimestamp(component['last_check']).strftime('%H:%M:%S') if component['last_check'] > 0 else 'Never'
            
            print(f"{Colors.BLUE}{name}:{Colors.RESET}")
            print(f"  Status: {status_color}{status}{Colors.RESET}")
            print(f"  Last Check: {last_check}")
            print(f"  Failures: {component['failure_count']}")
            print()
            
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors
    def _health_monitoring_menu(self):
        """Health monitoring configuration menu"""
        while True:
            print(f"\n{Colors.CYAN}=== Health Monitoring ==={Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} Start Monitoring")
            print(f"{Colors.BLUE}2.{Colors.RESET} Stop Monitoring")
            print(f"{Colors.BLUE}3.{Colors.RESET} View Monitoring Status")
            print(f"{Colors.BLUE}4.{Colors.RESET} Configure Check Intervals")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back to Main Menu")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self.resilience_manager.start_monitoring()
                print(f"{Colors.GREEN}[+] Health monitoring started{Colors.RESET}")
            elif choice == "2":
                self.resilience_manager.stop_monitoring()
                print(f"{Colors.YELLOW}[!] Health monitoring stopped{Colors.RESET}")
            elif choice == "3":
                status = "Active" if self.resilience_manager.monitoring_active else "Inactive"
                status_color = Colors.GREEN if self.resilience_manager.monitoring_active else Colors.RED
                print(f"{Colors.BLUE}Monitoring Status:{Colors.RESET} {status_color}{status}{Colors.RESET}")
            elif choice == "4":
                self._configure_intervals()
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
            time.sleep(1)
            
    @handle_errors
    def _configure_intervals(self):
        """Configure health check intervals"""
        print(f"\n{Colors.CYAN}=== Configure Check Intervals ==={Colors.RESET}")
        
        for name, health_check in self.resilience_manager.health_checks.items():
            print(f"{Colors.BLUE}{name}:{Colors.RESET} {health_check.interval}s")
            
        component = input(f"\n{Colors.CYAN}Component to configure (or Enter to skip): {Colors.RESET}")
        if component and component in self.resilience_manager.health_checks:
            try:
                interval = int(input(f"{Colors.CYAN}New interval in seconds: {Colors.RESET}"))
                if interval > 0:
                    self.resilience_manager.health_checks[component].interval = interval
                    print(f"{Colors.GREEN}[+] Interval updated for {component}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Interval must be positive{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}[!] Invalid interval value{Colors.RESET}")
        
    @handle_errors
    def _self_healing_menu(self):
        """Self-healing system menu"""
        while True:
            print(f"\n{Colors.CYAN}=== Self-Healing System ==={Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} Start Proactive Healing")
            print(f"{Colors.BLUE}2.{Colors.RESET} Manual Healing")
            print(f"{Colors.BLUE}3.{Colors.RESET} View Healing Strategies")
            print(f"{Colors.BLUE}4.{Colors.RESET} Test Healing Strategy")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back to Main Menu")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self.self_healing_system.start_proactive_healing()
                print(f"{Colors.GREEN}[+] Proactive healing started{Colors.RESET}")
            elif choice == "2":
                self._manual_healing()
            elif choice == "3":
                self._view_healing_strategies()
            elif choice == "4":
                self._test_healing_strategy()
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
            time.sleep(1)
            
    @handle_errors
    def _manual_healing(self):
        """Manually trigger healing for a component"""
        print(f"\n{Colors.CYAN}=== Manual Healing ==={Colors.RESET}")
        
        components = list(self.self_healing_system.healing_strategies.keys())
        
        print(f"{Colors.BLUE}Available components:{Colors.RESET}")
        for i, component in enumerate(components, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {component}")
            
        try:
            choice = int(input(f"\n{Colors.CYAN}Select component (number): {Colors.RESET}"))
            if 1 <= choice <= len(components):
                component = components[choice - 1]
                
                print(f"{Colors.CYAN}[*] Starting healing for {component}...{Colors.RESET}")
                success = self.self_healing_system.execute_healing_strategy(component)
                
                if success:
                    print(f"{Colors.GREEN}[+] Healing completed successfully{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Healing failed{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    @handle_errors
    def _view_healing_strategies(self):
        """View available healing strategies"""
        print(f"\n{Colors.CYAN}=== Healing Strategies ==={Colors.RESET}")
        
        for component, strategies in self.self_healing_system.healing_strategies.items():
            print(f"\n{Colors.BLUE}{component}:{Colors.RESET}")
            for i, strategy in enumerate(strategies, 1):
                print(f"  {i}. {strategy.__name__}")
                
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors
    def _test_healing_strategy(self):
        """Test a specific healing strategy"""
        print(f"\n{Colors.CYAN}=== Test Healing Strategy ==={Colors.RESET}")
        
        components = list(self.self_healing_system.healing_strategies.keys())
        
        print(f"{Colors.BLUE}Available components:{Colors.RESET}")
        for i, component in enumerate(components, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {component}")
            
        try:
            choice = int(input(f"\n{Colors.CYAN}Select component (number): {Colors.RESET}"))
            if 1 <= choice <= len(components):
                component = components[choice - 1]
                strategies = self.self_healing_system.healing_strategies[component]
                
                print(f"\n{Colors.BLUE}Strategies for {component}:{Colors.RESET}")
                for i, strategy in enumerate(strategies, 1):
                    print(f"{Colors.BLUE}{i}.{Colors.RESET} {strategy.__name__}")
                    
                strategy_choice = int(input(f"\n{Colors.CYAN}Select strategy (number): {Colors.RESET}"))
                if 1 <= strategy_choice <= len(strategies):
                    strategy = strategies[strategy_choice - 1]
                    
                    print(f"{Colors.CYAN}[*] Testing strategy: {strategy.__name__}{Colors.RESET}")
                    try:
                        result = strategy()
                        if result:
                            print(f"{Colors.GREEN}[+] Strategy test successful{Colors.RESET}")
                        else:
                            print(f"{Colors.YELLOW}[!] Strategy test failed{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}[!] Strategy test error: {e}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Invalid strategy selection{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid component selection{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    @handle_errors
    def _component_management_menu(self):
        """Component management menu"""
        while True:
            print(f"\n{Colors.CYAN}=== Component Management ==={Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} View Components")
            print(f"{Colors.BLUE}2.{Colors.RESET} Force Component Recovery")
            print(f"{Colors.BLUE}3.{Colors.RESET} Set Component Status")
            print(f"{Colors.BLUE}4.{Colors.RESET} Add Custom Health Check")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back to Main Menu")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self._show_health_status()
            elif choice == "2":
                self._force_component_recovery()
            elif choice == "3":
                self._set_component_status()
            elif choice == "4":
                print(f"{Colors.YELLOW}[!] Custom health check feature coming soon{Colors.RESET}")
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
            time.sleep(1)
            
    @handle_errors
    def _force_component_recovery(self):
        """Force recovery for a specific component"""
        print(f"\n{Colors.CYAN}=== Force Component Recovery ==={Colors.RESET}")
        
        components = list(self.resilience_manager.component_health.keys())
        
        print(f"{Colors.BLUE}Available components:{Colors.RESET}")
        for i, component in enumerate(components, 1):
            status = self.resilience_manager.component_health[component].status
            status_color = Colors.GREEN if status.value == 'healthy' else \
                          Colors.YELLOW if status.value in ['degraded', 'recovering'] else Colors.RED
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {component} ({status_color}{status.value}{Colors.RESET})")
            
        try:
            choice = int(input(f"\n{Colors.CYAN}Select component (number): {Colors.RESET}"))
            if 1 <= choice <= len(components):
                component = components[choice - 1]
                
                print(f"{Colors.CYAN}[*] Forcing recovery for {component}...{Colors.RESET}")
                self.resilience_manager.force_recovery(component)
                print(f"{Colors.GREEN}[+] Recovery triggered{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    @handle_errors
    def _set_component_status(self):
        """Manually set component status"""
        print(f"\n{Colors.CYAN}=== Set Component Status ==={Colors.RESET}")
        
        from modules.resilience import ComponentStatus
        
        components = list(self.resilience_manager.component_health.keys())
        statuses = list(ComponentStatus)
        
        print(f"{Colors.BLUE}Available components:{Colors.RESET}")
        for i, component in enumerate(components, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {component}")
            
        try:
            comp_choice = int(input(f"\n{Colors.CYAN}Select component (number): {Colors.RESET}"))
            if 1 <= comp_choice <= len(components):
                component = components[comp_choice - 1]
                
                print(f"\n{Colors.BLUE}Available statuses:{Colors.RESET}")
                for i, status in enumerate(statuses, 1):
                    print(f"{Colors.BLUE}{i}.{Colors.RESET} {status.value}")
                    
                status_choice = int(input(f"\n{Colors.CYAN}Select status (number): {Colors.RESET}"))
                if 1 <= status_choice <= len(statuses):
                    status = statuses[status_choice - 1]
                    
                    self.resilience_manager.set_component_status(component, status)
                    print(f"{Colors.GREEN}[+] Status updated{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Invalid status selection{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid component selection{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    @handle_errors
    def _view_healing_history(self):
        """View healing history"""
        print(f"\n{Colors.CYAN}=== Healing History ==={Colors.RESET}")
        
        history = self.self_healing_system.get_healing_history(limit=20)
        
        if not history:
            print(f"{Colors.YELLOW}[!] No healing history available{Colors.RESET}")
            return
            
        print(f"{Colors.BLUE}Recent healing attempts:{Colors.RESET}")
        print()
        
        for record in history:
            timestamp = datetime.fromtimestamp(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            component = record['component']
            strategy = record['strategy_name']
            success = record['success']
            
            success_color = Colors.GREEN if success else Colors.RED
            success_text = "SUCCESS" if success else "FAILED"
            
            print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {component}")
            print(f"  Strategy: {strategy}")
            print(f"  Result: {success_color}{success_text}{Colors.RESET}")
            
            if 'error' in record:
                print(f"  Error: {Colors.RED}{record['error']}{Colors.RESET}")
            print()
            
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors  
    def _test_recovery_menu(self):
        """Test recovery procedures"""
        while True:
            print(f"\n{Colors.CYAN}=== Test Recovery Procedures ==={Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} Test Network Recovery")
            print(f"{Colors.BLUE}2.{Colors.RESET} Test Module Recovery") 
            print(f"{Colors.BLUE}3.{Colors.RESET} Test Resource Recovery")
            print(f"{Colors.BLUE}4.{Colors.RESET} Test All Recovery Procedures")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back to Main Menu")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self._test_network_recovery()
            elif choice == "2":
                self._test_module_recovery()
            elif choice == "3":
                self._test_resource_recovery()
            elif choice == "4":
                self._test_all_recovery()
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
            time.sleep(1)
            
    def _test_network_recovery(self):
        """Test network recovery procedures"""
        print(f"\n{Colors.CYAN}[*] Testing network recovery procedures...{Colors.RESET}")
        success = self.self_healing_system.execute_healing_strategy("network_connectivity")
        if success:
            print(f"{Colors.GREEN}[+] Network recovery test successful{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Network recovery test failed{Colors.RESET}")
            
    def _test_module_recovery(self):
        """Test module recovery procedures"""
        print(f"\n{Colors.CYAN}[*] Testing module recovery procedures...{Colors.RESET}")
        success = self.self_healing_system.execute_healing_strategy("exploit_modules")
        if success:
            print(f"{Colors.GREEN}[+] Module recovery test successful{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Module recovery test failed{Colors.RESET}")
            
    def _test_resource_recovery(self):
        """Test resource recovery procedures"""
        print(f"\n{Colors.CYAN}[*] Testing resource recovery procedures...{Colors.RESET}")
        success = self.self_healing_system.execute_healing_strategy("system_resources")
        if success:
            print(f"{Colors.GREEN}[+] Resource recovery test successful{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Resource recovery test failed{Colors.RESET}")
            
    def _test_all_recovery(self):
        """Test all recovery procedures"""
        print(f"\n{Colors.CYAN}[*] Testing all recovery procedures...{Colors.RESET}")
        
        components = ["network_connectivity", "exploit_modules", "system_resources"]
        results = {}
        
        for component in components:
            print(f"{Colors.CYAN}[*] Testing {component}...{Colors.RESET}")
            success = self.self_healing_system.execute_healing_strategy(component)
            results[component] = success
            
            if success:
                print(f"{Colors.GREEN}[+] {component} recovery successful{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] {component} recovery failed{Colors.RESET}")
                
        # Summary
        print(f"\n{Colors.CYAN}=== Recovery Test Summary ==={Colors.RESET}")
        successful = sum(results.values())
        total = len(results)
        
        print(f"{Colors.BLUE}Total tests:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}Successful:{Colors.RESET} {successful}")
        print(f"{Colors.RED}Failed:{Colors.RESET} {total - successful}")
        
        if successful == total:
            print(f"{Colors.GREEN}[+] All recovery procedures working correctly{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Some recovery procedures need attention{Colors.RESET}")

def main():
    """Main function for testing"""
    menu = ResilienceMenu()
    menu.display()

if __name__ == "__main__":
    main()