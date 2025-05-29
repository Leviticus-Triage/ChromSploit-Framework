#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Browser Exploit Chain Menu
UI for managing and executing multi-CVE browser exploitation chains
"""

import time
from typing import Dict, Any, Optional
from core.enhanced_menu import EnhancedMenu
from core.color_utils import Colors
from core.enhanced_logger import get_logger
from modules.browser_exploit_chain import BrowserExploitChain
try:
    from modules.browser_exploit_chain_enhanced import EnhancedBrowserExploitChain, execute_enhanced_browser_attack
    ENHANCED_CHAIN_AVAILABLE = True
except ImportError:
    ENHANCED_CHAIN_AVAILABLE = False

logger = get_logger()


class BrowserChainMenu(EnhancedMenu):
    """Menu for browser exploit chain operations"""
    
    def __init__(self):
        super().__init__(
            title="Browser Multi-Exploit Chain",
            description="Automated browser CVE combination attacks"
        )
        
        self.browser_chain = BrowserExploitChain()
        self.active_chain_id: Optional[str] = None
        
        # Define menu items
        self._add_menu_items()
        
    def _add_menu_items(self):
        """Add browser chain menu items"""
        
        # Quick launch options
        self.add_enhanced_item(
            key='1',
            title='🚀 Quick Full Browser Compromise',
            description='Execute all 4 browser CVEs automatically',
            handler=self.quick_full_compromise,
            hotkey='f'
        )
        
        if ENHANCED_CHAIN_AVAILABLE:
            self.add_enhanced_item(
                key='2',
                title='🔥 Enhanced Attack (Obfuscation + Ngrok)',
                description='Full attack with obfuscation and auto-ngrok tunneling',
                handler=self.enhanced_full_compromise,
                hotkey='e'
            )
        
        self.add_enhanced_item(
            key='3',
            title='⚡ Chrome-Focused Attack',
            description='Target Chrome browser with 3 CVEs',
            handler=self.chrome_focused_attack,
            hotkey='c'
        )
        
        self.add_enhanced_item(
            key='4',
            title='🏃 Rapid Parallel Exploitation',
            description='Fast parallel execution of all exploits',
            handler=self.rapid_exploitation,
            hotkey='r'
        )
        
        self.add_enhanced_item(
            key='5',
            title='🥷 Stealth Browser Chain',
            description='Low-profile exploitation chain',
            handler=self.stealth_exploitation,
            hotkey='s'
        )
        
        # Advanced options
        self.add_separator("Advanced Operations")
        
        self.add_enhanced_item(
            key='5',
            title='🛠️ Create Custom Chain',
            description='Build custom browser exploitation chain',
            handler=self.create_custom_chain
        )
        
        self.add_enhanced_item(
            key='6',
            title='📊 View Active Chains',
            description='Monitor running exploitation chains',
            handler=self.view_active_chains
        )
        
        self.add_enhanced_item(
            key='7',
            title='🔍 Chain Status Details',
            description='Detailed status of specific chain',
            handler=self.view_chain_details
        )
        
        self.add_enhanced_item(
            key='8',
            title='⏹️ Stop Active Chain',
            description='Stop a running exploitation chain',
            handler=self.stop_chain
        )
        
        # Configuration
        self.add_separator("Configuration")
        
        self.add_enhanced_item(
            key='9',
            title='⚙️ Configure Targets',
            description='Set target URLs and callback settings',
            handler=self.configure_targets
        )
        
        self.add_enhanced_item(
            key='10',
            title='📋 Export Chain Results',
            description='Export exploitation results',
            handler=self.export_results
        )
    
    def quick_full_compromise(self):
        """Execute full browser compromise chain"""
        self.clear_screen()
        self.display_header("🚀 Full Browser Compromise Chain")
        
        print(f"\n{Colors.YELLOW}This will execute all 4 browser CVEs in sequence:{Colors.END}")
        print("1. CVE-2025-4664 - Chrome Data Leak (Reconnaissance)")
        print("2. CVE-2025-2857 - Chrome OAuth Exploitation")
        print("3. CVE-2025-30397 - Edge WebAssembly JIT")
        print("4. CVE-2025-2783 - Chrome Sandbox Escape")
        
        if not self.confirm("\nProceed with full browser compromise?"):
            return
        
        # Get configuration
        config = self._get_default_config()
        
        # Create and execute chain
        self.display_progress("Creating exploitation chain...")
        chain_id = self.browser_chain.create_browser_chain('full_browser_compromise', config)
        
        if not chain_id:
            self.display_error("Failed to create exploitation chain")
            return
        
        self.active_chain_id = chain_id
        self.display_success(f"Chain created: {chain_id[:8]}...")
        
        # Execute
        self.display_progress("Starting browser exploitation...")
        result = self.browser_chain.execute_browser_chain(chain_id, async_mode=False)
        
        # Display results
        self._display_execution_results(result)
    
    def enhanced_full_compromise(self):
        """Execute enhanced browser compromise with obfuscation and ngrok"""
        if not ENHANCED_CHAIN_AVAILABLE:
            self.display_error("Enhanced chain module not available")
            return
            
        self.clear_screen()
        self.display_header("🔥 Enhanced Browser Compromise (Obfuscation + Ngrok)")
        
        print(f"\n{Colors.YELLOW}Enhanced features enabled:{Colors.END}")
        print("✓ Full payload obfuscation (EXTREME level)")
        print("✓ Control flow obfuscation")
        print("✓ String encryption & encoding")
        print("✓ Anti-debugging & Anti-VM")
        print("✓ Polymorphic code generation")
        print("✓ Auto-ngrok tunnel creation")
        print("✓ Binary data obfuscation")
        print("✓ Dead code injection")
        
        print(f"\n{Colors.CYAN}Attack sequence:{Colors.END}")
        print("1. Setup ngrok tunnels for callbacks")
        print("2. Obfuscate all exploit payloads")
        print("3. Execute CVE-2025-4664 (Recon)")
        print("4. Execute CVE-2025-2857 (OAuth)")
        print("5. Execute CVE-2025-30397 (WebAssembly)")
        print("6. Execute CVE-2025-2783 (Sandbox Escape)")
        
        if not self.confirm("\nProceed with enhanced attack?"):
            return
        
        # Get target configuration
        target_url = self.get_input("Target URL", default="http://localhost:8080")
        
        # Execute enhanced attack
        self.display_progress("Setting up ngrok tunnels...")
        self.display_progress("Initializing obfuscation engine...")
        
        try:
            result = execute_enhanced_browser_attack(
                target_url=target_url,
                callback_port=4444
            )
            
            # Display enhanced results
            self._display_enhanced_results(result)
            
        except Exception as e:
            self.display_error(f"Enhanced attack failed: {e}")
    
    def _display_enhanced_results(self, result: Dict[str, Any]):
        """Display results from enhanced attack"""
        print(f"\n{Colors.CYAN}Enhanced Attack Results:{Colors.END}")
        print("=" * 60)
        
        if result.get('success'):
            self.display_success("Enhanced browser exploitation completed!")
        else:
            self.display_error("Enhanced exploitation failed")
        
        # Show obfuscation report
        if 'obfuscation_report' in result:
            report = result['obfuscation_report']
            print(f"\n{Colors.YELLOW}Obfuscation Report:{Colors.END}")
            print(f"  Payloads obfuscated: {report.get('total_payloads_obfuscated', 0)}")
            print(f"  Obfuscation time: {report.get('obfuscation_time', 0):.2f}s")
            print(f"  Average size increase: {report.get('average_size_increase', 0):.1%}")
            
            print(f"\n{Colors.CYAN}Techniques used:{Colors.END}")
            for technique in report.get('techniques_used', []):
                print(f"  ✓ {technique}")
        
        # Show ngrok tunnels
        if 'ngrok_tunnels' in result:
            tunnels = result['ngrok_tunnels']
            print(f"\n{Colors.GREEN}Ngrok Tunnels Created:{Colors.END}")
            for name, url in tunnels.items():
                print(f"  {name}: {url}")
        
        # Show enhanced features
        if 'enhanced_features' in result:
            features = result['enhanced_features']
            print(f"\n{Colors.BLUE}Enhanced Features:{Colors.END}")
            for feature, enabled in features.items():
                status = "✓" if enabled else "✗"
                print(f"  {status} {feature.replace('_', ' ').title()}")
        
        # Standard chain results
        if 'chain_result' in result:
            chain_result = result['chain_result']
            print(f"\n{Colors.CYAN}Chain Execution:{Colors.END}")
            print(f"  Status: {chain_result.status.value}")
            print(f"  Steps: {chain_result.successful_steps}/{chain_result.total_steps} successful")
            print(f"  Time: {chain_result.execution_time:.2f}s")
        
        self.wait_for_key()
    
    def chrome_focused_attack(self):
        """Execute Chrome-specific attack chain"""
        self.clear_screen()
        self.display_header("⚡ Chrome-Focused Attack Chain")
        
        print(f"\n{Colors.CYAN}Chrome-specific exploitation using 3 CVEs:{Colors.END}")
        print("1. CVE-2025-4664 - Chrome Reconnaissance")
        print("2. CVE-2025-2857 - OAuth Token Theft")
        print("3. CVE-2025-2783 - Sandbox Escape")
        
        if not self.confirm("\nExecute Chrome-focused attack?"):
            return
        
        config = self._get_default_config()
        
        # Create and execute
        chain_id = self.browser_chain.create_browser_chain('chrome_focused_attack', config)
        if chain_id:
            self.active_chain_id = chain_id
            result = self.browser_chain.execute_browser_chain(chain_id, async_mode=False)
            self._display_execution_results(result)
    
    def rapid_exploitation(self):
        """Execute rapid parallel exploitation"""
        self.clear_screen()
        self.display_header("🏃 Rapid Parallel Exploitation")
        
        print(f"\n{Colors.RED}Fast parallel execution of browser exploits{Colors.END}")
        print("⚠️  This mode executes exploits simultaneously")
        print("   - Higher detection risk")
        print("   - Faster completion time")
        print("   - May cause system instability")
        
        if not self.confirm("\nProceed with rapid exploitation?", danger=True):
            return
        
        config = self._get_default_config()
        config['parallel'] = True
        config['fast_mode'] = True
        
        # Create and execute
        chain_id = self.browser_chain.create_browser_chain('rapid_exploitation', config)
        if chain_id:
            self.active_chain_id = chain_id
            
            # Execute asynchronously for rapid mode
            self.display_progress("Launching parallel exploitation...")
            result = self.browser_chain.execute_browser_chain(chain_id, async_mode=True)
            
            if result['success']:
                self.display_success("Rapid exploitation started!")
                print(f"\nChain ID: {Colors.CYAN}{chain_id[:8]}...{Colors.END}")
                print(f"Use option '7' to monitor progress")
                
                # Brief real-time monitoring
                self._monitor_chain_briefly(chain_id)
    
    def stealth_exploitation(self):
        """Execute stealth browser chain"""
        self.clear_screen()
        self.display_header("🥷 Stealth Browser Exploitation")
        
        print(f"\n{Colors.BLUE}Low-profile exploitation chain:{Colors.END}")
        print("✓ Minimal network footprint")
        print("✓ Anti-forensics measures")
        print("✓ Evasion techniques enabled")
        print("✓ Silent execution mode")
        
        if not self.confirm("\nExecute stealth chain?"):
            return
        
        config = self._get_default_config()
        config.update({
            'stealth': True,
            'minimal_footprint': True,
            'anti_forensics': True,
            'silent_mode': True
        })
        
        # Create and execute
        chain_id = self.browser_chain.create_browser_chain('stealth_browser_chain', config)
        if chain_id:
            self.active_chain_id = chain_id
            result = self.browser_chain.execute_browser_chain(chain_id, async_mode=False)
            self._display_execution_results(result)
    
    def create_custom_chain(self):
        """Create custom browser exploitation chain"""
        self.clear_screen()
        self.display_header("🛠️ Create Custom Browser Chain")
        
        print("\nAvailable Browser CVEs:")
        for cve_id, info in self.browser_chain.BROWSER_CVES.items():
            print(f"\n{Colors.CYAN}{cve_id}{Colors.END} - {info['name']}")
            print(f"  Browser: {info['browser']}")
            print(f"  Type: {info['type']}")
            print(f"  Severity: {info['severity']}")
        
        print(f"\n{Colors.YELLOW}Select CVEs to include in chain:{Colors.END}")
        selected_cves = []
        
        for cve_id in self.browser_chain.BROWSER_CVES:
            if self.confirm(f"Include {cve_id}?"):
                selected_cves.append(cve_id)
        
        if not selected_cves:
            self.display_warning("No CVEs selected")
            return
        
        # Get chain name
        chain_name = self.get_input("Chain name", default="Custom Browser Chain")
        
        # Create custom chain
        chain_manager = self.browser_chain.chain_manager
        chain = chain_manager.create_chain(chain_name, "Custom browser exploitation chain")
        
        # Add selected CVEs
        config = self._get_default_config()
        for cve_id in selected_cves:
            cve_info = self.browser_chain.BROWSER_CVES[cve_id]
            chain.add_step(
                cve_id=cve_id,
                description=cve_info['description'],
                parameters=config,
                timeout=300,
                failure_action='continue'
            )
        
        self.display_success(f"Custom chain created: {chain.id[:8]}...")
        
        if self.confirm("Execute custom chain now?"):
            result = chain.execute(async_execution=False)
            self._display_execution_results({
                'success': result.status.value == 'success',
                'chain_id': chain.id,
                'chain_name': chain_name,
                'status': result.status.value,
                'statistics': {
                    'total_steps': result.total_steps,
                    'successful_steps': result.successful_steps,
                    'failed_steps': result.failed_steps
                }
            })
    
    def view_active_chains(self):
        """View all active exploitation chains"""
        self.clear_screen()
        self.display_header("📊 Active Browser Exploitation Chains")
        
        chains = self.browser_chain.get_all_chains()
        
        if not chains:
            self.display_warning("No active chains")
            return
        
        print(f"\n{Colors.CYAN}Active Chains:{Colors.END}")
        print("-" * 80)
        
        for chain in chains:
            status_color = Colors.GREEN if chain['status'] == 'success' else (
                Colors.RED if chain['status'] == 'failed' else Colors.YELLOW
            )
            
            print(f"\nID: {Colors.BLUE}{chain['id'][:8]}...{Colors.END}")
            print(f"Name: {chain['name']}")
            print(f"Template: {chain['template']}")
            print(f"Status: {status_color}{chain['status']}{Colors.END}")
            print(f"Steps: {chain['steps']}")
            print(f"Browsers: {', '.join(chain['browsers'])}")
            print(f"Created: {chain['created']}")
        
        self.wait_for_key()
    
    def view_chain_details(self):
        """View detailed status of specific chain"""
        self.clear_screen()
        self.display_header("🔍 Chain Status Details")
        
        # Get chain ID
        chain_id = self.active_chain_id
        if not chain_id:
            chain_id = self.get_input("Chain ID (or first 8 chars)")
            
            # Find matching chain
            all_chains = self.browser_chain.get_all_chains()
            for chain in all_chains:
                if chain['id'].startswith(chain_id):
                    chain_id = chain['id']
                    break
        
        if not chain_id:
            self.display_error("Chain not found")
            return
        
        # Get detailed status
        status = self.browser_chain.get_chain_status(chain_id)
        
        if 'error' in status:
            self.display_error(status['error'])
            return
        
        # Display status
        print(f"\n{Colors.CYAN}Chain Details:{Colors.END}")
        print(f"ID: {status['id']}")
        print(f"Name: {status['name']}")
        print(f"Status: {self._get_status_color(status['status'])}{status['status']}{Colors.END}")
        print(f"Progress: {status['progress']}")
        print(f"Execution Time: {status.get('execution_time', 0):.2f}s")
        
        print(f"\n{Colors.YELLOW}Exploitation Progress:{Colors.END}")
        progress = status['exploitation_progress']
        print(f"  Percentage: {progress['percentage']:.1f}%")
        print(f"  Completed: {progress['completed_steps']}/{progress['total_steps']}")
        print(f"  Successful: {Colors.GREEN}{progress['successful_steps']}{Colors.END}")
        print(f"  Failed: {Colors.RED}{progress['failed_steps']}{Colors.END}")
        
        print(f"\n{Colors.CYAN}Targeted Browsers:{Colors.END}")
        for browser in status['browsers_targeted']:
            print(f"  • {browser}")
        
        # Monitor if running
        if status['status'] == 'running':
            if self.confirm("\nMonitor chain progress?"):
                self._monitor_chain_progress(chain_id)
        
        self.wait_for_key()
    
    def stop_chain(self):
        """Stop a running exploitation chain"""
        self.clear_screen()
        self.display_header("⏹️ Stop Exploitation Chain")
        
        # Get active chains
        chains = self.browser_chain.get_all_chains()
        running_chains = [c for c in chains if c['status'] == 'running']
        
        if not running_chains:
            self.display_warning("No running chains to stop")
            return
        
        print(f"\n{Colors.YELLOW}Running Chains:{Colors.END}")
        for i, chain in enumerate(running_chains, 1):
            print(f"{i}. {chain['name']} ({chain['id'][:8]}...)")
        
        choice = self.get_input("\nSelect chain to stop (number)")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(running_chains):
                chain_id = running_chains[index]['id']
                
                if self.browser_chain.stop_browser_chain(chain_id):
                    self.display_success(f"Chain {chain_id[:8]}... stopped")
                else:
                    self.display_error("Failed to stop chain")
        except:
            self.display_error("Invalid selection")
    
    def configure_targets(self):
        """Configure target settings"""
        self.clear_screen()
        self.display_header("⚙️ Configure Browser Chain Targets")
        
        print(f"\n{Colors.CYAN}Current Configuration:{Colors.END}")
        config = self._get_default_config()
        
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        print(f"\n{Colors.YELLOW}Update Configuration:{Colors.END}")
        
        # Update each setting
        new_config = {}
        
        target_url = self.get_input("Target URL", default=config.get('target_url', 'http://localhost'))
        new_config['target_url'] = target_url
        
        callback_ip = self.get_input("Callback IP", default=config.get('callback_ip', '127.0.0.1'))
        new_config['callback_ip'] = callback_ip
        
        callback_port = self.get_input("Callback Port", default=str(config.get('callback_port', 4444)))
        try:
            new_config['callback_port'] = int(callback_port)
        except:
            new_config['callback_port'] = 4444
        
        # Save configuration
        self._save_config(new_config)
        self.display_success("Configuration updated")
    
    def export_results(self):
        """Export chain execution results"""
        self.clear_screen()
        self.display_header("📋 Export Chain Results")
        
        if not self.browser_chain.results:
            self.display_warning("No results to export")
            return
        
        print(f"\n{Colors.CYAN}Available Results:{Colors.END}")
        for i, (chain_id, result) in enumerate(self.browser_chain.results.items(), 1):
            timestamp = result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. Chain {chain_id[:8]}... - {timestamp}")
        
        choice = self.get_input("\nSelect result to export (number)")
        
        try:
            index = int(choice) - 1
            chain_ids = list(self.browser_chain.results.keys())
            
            if 0 <= index < len(chain_ids):
                chain_id = chain_ids[index]
                result = self.browser_chain.results[chain_id]
                
                # Export to file
                filename = f"browser_chain_results_{chain_id[:8]}_{int(time.time())}.json"
                
                import json
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                
                self.display_success(f"Results exported to: {filename}")
        except:
            self.display_error("Invalid selection")
        
        self.wait_for_key()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        # Try to load saved config
        try:
            import json
            with open('config/browser_chain_config.json', 'r') as f:
                return json.load(f)
        except:
            # Return defaults
            return {
                'target_url': 'http://localhost:8080',
                'callback_ip': '127.0.0.1',
                'callback_port': 4444,
                'timeout': 300
            }
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        try:
            import json
            os.makedirs('config', exist_ok=True)
            with open('config/browser_chain_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _display_execution_results(self, result: Dict[str, Any]):
        """Display chain execution results"""
        print(f"\n{Colors.CYAN}Execution Results:{Colors.END}")
        print("=" * 60)
        
        if result.get('success'):
            self.display_success("Browser exploitation chain completed successfully!")
        else:
            self.display_error("Browser exploitation chain failed")
        
        print(f"\nStatus: {self._get_status_color(result.get('status', 'unknown'))}{result.get('status', 'unknown')}{Colors.END}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\n{Colors.YELLOW}Statistics:{Colors.END}")
            print(f"  Total Steps: {stats['total_steps']}")
            print(f"  Successful: {Colors.GREEN}{stats['successful_steps']}{Colors.END}")
            print(f"  Failed: {Colors.RED}{stats['failed_steps']}{Colors.END}")
            print(f"  Skipped: {stats.get('skipped_steps', 0)}")
        
        if 'exploited_browsers' in result:
            print(f"\n{Colors.CYAN}Exploited Browsers:{Colors.END}")
            for browser in result['exploited_browsers']:
                print(f"  ✓ {browser}")
        
        if 'successful_cves' in result:
            print(f"\n{Colors.GREEN}Successful CVEs:{Colors.END}")
            for cve in result['successful_cves']:
                print(f"  ✓ {cve}")
        
        if 'failed_cves' in result:
            print(f"\n{Colors.RED}Failed CVEs:{Colors.END}")
            for cve in result['failed_cves']:
                print(f"  ✗ {cve}")
        
        if 'recommendations' in result:
            print(f"\n{Colors.YELLOW}Recommendations:{Colors.END}")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        
        if 'execution_time' in result:
            print(f"\n{Colors.BLUE}Execution Time: {result['execution_time']:.2f} seconds{Colors.END}")
        
        self.wait_for_key()
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status display"""
        status_colors = {
            'success': Colors.GREEN,
            'failed': Colors.RED,
            'running': Colors.YELLOW,
            'pending': Colors.BLUE,
            'stopped': Colors.MAGENTA,
            'partial': Colors.CYAN
        }
        return status_colors.get(status, Colors.WHITE)
    
    def _monitor_chain_briefly(self, chain_id: str, duration: int = 10):
        """Briefly monitor chain progress"""
        print(f"\n{Colors.CYAN}Monitoring chain progress for {duration} seconds...{Colors.END}")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            status = self.browser_chain.get_chain_status(chain_id)
            progress = status['exploitation_progress']
            
            print(f"\r  Progress: {progress['percentage']:.1f}% "
                  f"({progress['completed_steps']}/{progress['total_steps']} steps) "
                  f"Status: {self._get_status_color(status['status'])}{status['status']}{Colors.END}",
                  end='', flush=True)
            
            if status['status'] not in ['running', 'pending']:
                break
            
            time.sleep(1)
        
        print("\n")
    
    def _monitor_chain_progress(self, chain_id: str):
        """Monitor chain progress until completion"""
        print(f"\n{Colors.CYAN}Monitoring chain progress (Press Ctrl+C to stop)...{Colors.END}")
        
        try:
            while True:
                status = self.browser_chain.get_chain_status(chain_id)
                progress = status['exploitation_progress']
                
                # Clear and redraw
                print("\033[2J\033[H")  # Clear screen
                self.display_header("📊 Chain Progress Monitor")
                
                print(f"\nChain: {status['name']}")
                print(f"Status: {self._get_status_color(status['status'])}{status['status']}{Colors.END}")
                print(f"Progress: {progress['percentage']:.1f}%")
                
                # Progress bar
                bar_length = 50
                filled = int(bar_length * progress['percentage'] / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\n[{bar}] {progress['completed_steps']}/{progress['total_steps']}")
                
                print(f"\n✓ Successful: {Colors.GREEN}{progress['successful_steps']}{Colors.END}")
                print(f"✗ Failed: {Colors.RED}{progress['failed_steps']}{Colors.END}")
                print(f"Execution Time: {status.get('execution_time', 0):.2f}s")
                
                if status['status'] not in ['running', 'pending']:
                    print(f"\n{Colors.YELLOW}Chain completed!{Colors.END}")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped{Colors.END}")


# Module registration
def get_menu():
    """Get browser chain menu instance"""
    return BrowserChainMenu()