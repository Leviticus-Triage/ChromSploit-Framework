#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analytics Dashboard
Real-time monitoring and statistics dashboard
"""

import time
from typing import Dict, List, Any, Optional
from core.menu import Menu
from core.colors import Colors
from modules.monitoring import get_exploit_monitor
from modules.detection import get_browser_detector

class AnalyticsDashboard(Menu):
    """Analytics and monitoring dashboard"""
    
    def __init__(self, parent=None):
        super().__init__("Analytics Dashboard", parent)
        self.monitor = get_exploit_monitor()
        self.detector = get_browser_detector()
        
        self.set_info_text("Real-time exploit statistics and monitoring")
        
        self.add_item("📊 Overall Statistics", self._show_overall_stats, Colors.BRIGHT_CYAN)
        self.add_item("🎯 Exploit Performance", self._show_exploit_performance, Colors.BRIGHT_GREEN)
        self.add_item("🌐 Browser Distribution", self._show_browser_distribution, Colors.BRIGHT_BLUE)
        self.add_item("📈 Recent Activity", self._show_recent_activity, Colors.BRIGHT_YELLOW)
        self.add_item("🏆 Top Exploits", self._show_top_exploits, Colors.BRIGHT_MAGENTA)
        self.add_item("⚙️ Cache Statistics", self._show_cache_stats, Colors.BRIGHT_WHITE)
        self.add_item("🔍 Export Report", self._export_report, Colors.BRIGHT_GREEN)
        self.add_item("Back", lambda: "exit", Colors.RED)
    
    def _show_overall_stats(self):
        """Show overall statistics"""
        self._clear()
        self._draw_box(80, "OVERALL STATISTICS")
        
        metrics = self.monitor.get_performance_metrics()
        
        print(f"\n{Colors.CYAN}=== Performance Metrics ==={Colors.RESET}\n")
        print(f"Total Attempts:     {Colors.GREEN}{metrics['total_attempts']}{Colors.RESET}")
        print(f"Successful:         {Colors.GREEN}{metrics['total_successful']}{Colors.RESET}")
        print(f"Failed:             {Colors.RED}{metrics['total_failed']}{Colors.RESET}")
        print(f"Success Rate:       {Colors.YELLOW}{metrics['overall_success_rate']*100:.2f}%{Colors.RESET}")
        print(f"Avg Execution Time: {Colors.CYAN}{metrics['average_execution_time']:.2f}s{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_exploit_performance(self):
        """Show exploit-specific performance"""
        self._clear()
        self._draw_box(80, "EXPLOIT PERFORMANCE")
        
        stats = self.monitor.get_statistics()
        
        if not stats:
            print(f"\n{Colors.YELLOW}No exploit statistics available yet.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}=== Exploit Statistics ==={Colors.RESET}\n")
        
        for exploit_id, stat in stats.items():
            print(f"\n{Colors.GREEN}{exploit_id}{Colors.RESET}")
            print(f"  Attempts:      {stat['total_attempts']}")
            print(f"  Successful:    {Colors.GREEN}{stat['successful_attempts']}{Colors.RESET}")
            print(f"  Failed:        {Colors.RED}{stat['failed_attempts']}{Colors.RESET}")
            print(f"  Success Rate:  {Colors.YELLOW}{stat['success_rate']*100:.2f}%{Colors.RESET}")
            print(f"  Avg Time:      {stat['average_execution_time']:.2f}s")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_browser_distribution(self):
        """Show browser distribution"""
        self._clear()
        self._draw_box(80, "BROWSER DISTRIBUTION")
        
        distribution = self.monitor.get_browser_distribution()
        
        if not distribution:
            print(f"\n{Colors.YELLOW}No browser data available yet.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}=== Browser Distribution ==={Colors.RESET}\n")
        
        total = sum(distribution.values())
        for browser, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"{browser:15} {bar:50} {count:4} ({percentage:5.1f}%)")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_recent_activity(self):
        """Show recent exploit attempts"""
        self._clear()
        self._draw_box(80, "RECENT ACTIVITY")
        
        recent = self.monitor.get_recent_attempts(10)
        
        if not recent:
            print(f"\n{Colors.YELLOW}No recent activity.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}=== Recent Exploit Attempts ==={Colors.RESET}\n")
        
        for attempt in recent:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if attempt['success'] else f"{Colors.RED}✗{Colors.RESET}"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(attempt['timestamp']))
            
            print(f"{status} {timestamp} | {attempt['exploit_id']:20} | "
                  f"{attempt['target_browser']:10} {attempt['target_version']:15} | "
                  f"{attempt['execution_time']:.2f}s")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_top_exploits(self):
        """Show top performing exploits"""
        self._clear()
        self._draw_box(80, "TOP EXPLOITS")
        
        top_exploits = self.monitor.get_top_exploits(10)
        
        if not top_exploits:
            print(f"\n{Colors.YELLOW}No exploit data available yet.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return "continue"
        
        print(f"\n{Colors.CYAN}=== Top Exploits by Success Rate ==={Colors.RESET}\n")
        
        for i, (exploit_id, success_rate) in enumerate(top_exploits, 1):
            bar = "█" * int(success_rate * 50)
            print(f"{i:2}. {exploit_id:25} {bar:50} {success_rate*100:5.1f}%")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _show_cache_stats(self):
        """Show cache statistics"""
        self._clear()
        self._draw_box(80, "CACHE STATISTICS")
        
        try:
            from modules.cache import get_exploit_cache
            cache = get_exploit_cache()
            stats = cache.get_stats()
            
            print(f"\n{Colors.CYAN}=== Cache Statistics ==={Colors.RESET}\n")
            print(f"Total Entries:      {stats['total_entries']}")
            print(f"Total Hits:         {stats['total_hits']}")
            print(f"Payload Entries:    {stats['payload_entries']}")
            print(f"Obfuscation Entries:{stats['obfuscation_entries']}")
            print(f"Detection Entries:  {stats['detection_entries']}")
            print(f"Usage:              {stats['usage_percent']:.1f}% ({stats['total_entries']}/{stats['max_size']})")
            
        except Exception as e:
            print(f"\n{Colors.RED}Error loading cache stats: {e}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
    
    def _export_report(self):
        """Export analytics report"""
        self._clear()
        self._draw_box(80, "EXPORT REPORT")
        
        report = self.monitor.generate_report()
        
        try:
            from pathlib import Path
            import json
            
            report_dir = Path(__file__).parent.parent.parent / "data" / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"analytics_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n{Colors.GREEN}Report exported to: {report_file}{Colors.RESET}")
            
        except Exception as e:
            print(f"\n{Colors.RED}Error exporting report: {e}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return "continue"
