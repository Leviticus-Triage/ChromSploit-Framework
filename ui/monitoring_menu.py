#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from datetime import datetime
from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors

class MonitoringMenu(EnhancedMenu):
    def __init__(self):
        super().__init__("Live Monitoring System")
        self.logger = get_logger()
        
        # Try to import monitoring modules
        try:
            from modules.monitoring import get_live_monitor, get_exploit_monitor, EventType, EventPriority
            from modules.monitoring.monitor_ui import MonitorUI, MonitorDashboard
            
            self.monitor = get_live_monitor()
            self.exploit_monitor = get_exploit_monitor()
            self.monitor_ui = MonitorUI()
            self.dashboard = MonitorDashboard()
            self.EventType = EventType
            self.EventPriority = EventPriority
            self.monitoring_available = True
        except ImportError:
            self.monitoring_available = False
            
        self._setup_menu_items()
        
    def _setup_menu_items(self):
        """Setup menu items"""
        if not self.monitoring_available:
            self.add_enhanced_item(
                "Monitoring Not Available", 
                self._show_error,
                color=Colors.RED,
                description="Monitoring modules not found"
            )
            return
            
        self.add_enhanced_item(
            "Start Monitoring", 
            self._start_monitoring,
            color=Colors.GREEN,
            description="Start live event monitoring"
        )
        
        self.add_enhanced_item(
            "Terminal Display", 
            self._terminal_display,
            color=Colors.CYAN,
            description="View live events in terminal"
        )
        
        self.add_enhanced_item(
            "Web Dashboard", 
            self._web_dashboard,
            color=Colors.BLUE,
            description="Open web-based monitoring dashboard"
        )
        
        self.add_enhanced_item(
            "View Events", 
            self._view_events,
            color=Colors.WHITE,
            description="Browse recorded events"
        )
        
        self.add_enhanced_item(
            "Configure Filters", 
            self._configure_filters,
            color=Colors.YELLOW,
            description="Set event filtering options"
        )
        
        self.add_enhanced_item(
            "Alert Configuration", 
            self._configure_alerts,
            color=Colors.ORANGE,
            description="Configure alert conditions"
        )
        
        self.add_enhanced_item(
            "Statistics", 
            self._show_statistics,
            color=Colors.PURPLE,
            description="View monitoring statistics"
        )
        
        self.add_enhanced_item(
            "Export Events", 
            self._export_events,
            color=Colors.GREEN,
            description="Export events to file"
        )
        
        self.add_enhanced_item(
            "Test Events", 
            self._test_events,
            color=Colors.MAGENTA,
            description="Generate test events"
        )
        
    @handle_errors
    def _show_error(self):
        """Show error message"""
        print(f"{Colors.RED}[!] Monitoring modules not available{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] The live monitoring system requires additional setup{Colors.RESET}")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors
    def _start_monitoring(self):
        """Start monitoring system"""
        if self.monitor.monitoring_active:
            print(f"{Colors.YELLOW}[!] Monitoring is already active{Colors.RESET}")
        else:
            self.monitor.start()
            print(f"{Colors.GREEN}[+] Monitoring started{Colors.RESET}")
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors
    def _terminal_display(self):
        """Start terminal display"""
        print(f"{Colors.CYAN}[*] Starting terminal display...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Press 'q' to quit display{Colors.RESET}")
        
        # Start monitoring if not active
        if not self.monitor.monitoring_active:
            self.monitor.start()
            
        # Start display
        self.monitor_ui.start_display()
        
        # Wait for user input
        while True:
            try:
                key = input().lower()
                if key == 'q':
                    break
                elif key == 's':
                    self.monitor_ui.toggle_stats()
                elif key == 'c':
                    self.monitor.clear_events()
                elif key == 'f':
                    self._quick_filter()
            except KeyboardInterrupt:
                break
                
        self.monitor_ui.stop_display()
        print(f"{Colors.CYAN}[*] Terminal display stopped{Colors.RESET}")
        
    @handle_errors
    def _web_dashboard(self):
        """Start web dashboard"""
        print(f"{Colors.CYAN}=== Web Dashboard ==={Colors.RESET}")
        
        # Start monitoring if not active
        if not self.monitor.monitoring_active:
            self.monitor.start()
            
        # Start dashboard
        self.dashboard.start()
        
        print(f"{Colors.GREEN}[+] Web dashboard started{Colors.RESET}")
        print(f"{Colors.BLUE}[+] Access at: http://localhost:{self.dashboard.port}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Press Enter to stop dashboard{Colors.RESET}")
        
        input()
        
        self.dashboard.stop()
        print(f"{Colors.CYAN}[*] Web dashboard stopped{Colors.RESET}")
        
    @handle_errors
    def _view_events(self):
        """View recorded events"""
        print(f"\n{Colors.CYAN}=== View Events ==={Colors.RESET}")
        
        # Get events with current filters
        events = self.monitor.get_events(limit=50)
        
        if not events:
            print(f"{Colors.YELLOW}[!] No events to display{Colors.RESET}")
        else:
            print(f"{Colors.BLUE}Showing {len(events)} events:{Colors.RESET}")
            print()
            
            for event in events:
                self._print_event(event)
                
        # Pagination
        if len(self.monitor.events) > 50:
            print(f"\n{Colors.YELLOW}[!] Showing first 50 events of {len(self.monitor.events)} total{Colors.RESET}")
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    def _print_event(self, event: dict):
        """Print a single event"""
        timestamp = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        event_type = event['type']
        message = event['message']
        priority = event['priority']
        
        # Color based on priority
        if priority >= 4:
            color = Colors.RED
        elif priority >= 3:
            color = Colors.YELLOW
        elif priority >= 2:
            color = Colors.BLUE
        else:
            color = Colors.CYAN
            
        print(f"{color}[{timestamp}] [{event_type:15}] {message}{Colors.RESET}")
        
        # Show data if present
        if event.get('data'):
            for key, value in event['data'].items():
                print(f"  {Colors.CYAN}{key}:{Colors.RESET} {value}")
                
    @handle_errors
    def _configure_filters(self):
        """Configure event filters"""
        while True:
            print(f"\n{Colors.CYAN}=== Configure Filters ==={Colors.RESET}")
            
            # Show current filters
            stats = self.monitor.get_statistics()
            filters = stats['active_filters']
            
            print(f"{Colors.BLUE}Current Filters:{Colors.RESET}")
            print(f"  Event Types: {filters['types'] or 'All'}")
            print(f"  Min Priority: {filters['min_priority']}")
            print(f"  Search Term: {filters['search_term'] or 'None'}")
            
            print(f"\n{Colors.BLUE}Options:{Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} Filter by Event Type")
            print(f"{Colors.BLUE}2.{Colors.RESET} Set Minimum Priority")
            print(f"{Colors.BLUE}3.{Colors.RESET} Set Search Term")
            print(f"{Colors.BLUE}4.{Colors.RESET} Clear All Filters")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self._filter_by_type()
            elif choice == "2":
                self._set_min_priority()
            elif choice == "3":
                self._set_search_term()
            elif choice == "4":
                self.monitor.clear_filters()
                print(f"{Colors.GREEN}[+] Filters cleared{Colors.RESET}")
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
    def _filter_by_type(self):
        """Filter by event type"""
        print(f"\n{Colors.CYAN}Select event types to show:{Colors.RESET}")
        
        event_types = list(self.EventType)
        selected = []
        
        for i, event_type in enumerate(event_types, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {event_type.value}")
            
        print(f"\n{Colors.CYAN}Enter numbers separated by commas (or 'all' for all types): {Colors.RESET}")
        selection = input().strip()
        
        if selection.lower() == 'all':
            self.monitor.set_filter('types', None)
            print(f"{Colors.GREEN}[+] Showing all event types{Colors.RESET}")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_types = [event_types[i] for i in indices if 0 <= i < len(event_types)]
                
                if selected_types:
                    self.monitor.set_filter('types', selected_types)
                    print(f"{Colors.GREEN}[+] Filter set for {len(selected_types)} event types{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] No valid types selected{Colors.RESET}")
            except (ValueError, IndexError):
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                
    def _set_min_priority(self):
        """Set minimum priority filter"""
        print(f"\n{Colors.CYAN}Select minimum priority:{Colors.RESET}")
        
        priorities = list(self.EventPriority)
        
        for i, priority in enumerate(priorities, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {priority.name} (level {priority.value})")
            
        try:
            choice = int(input(f"\n{Colors.CYAN}Select priority: {Colors.RESET}"))
            if 1 <= choice <= len(priorities):
                self.monitor.set_filter('min_priority', priorities[choice - 1])
                print(f"{Colors.GREEN}[+] Minimum priority set to {priorities[choice - 1].name}{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    def _set_search_term(self):
        """Set search term filter"""
        term = input(f"\n{Colors.CYAN}Enter search term (or empty to clear): {Colors.RESET}")
        
        if term:
            self.monitor.set_filter('search_term', term)
            print(f"{Colors.GREEN}[+] Search filter set: {term}{Colors.RESET}")
        else:
            self.monitor.set_filter('search_term', None)
            print(f"{Colors.GREEN}[+] Search filter cleared{Colors.RESET}")
            
    @handle_errors
    def _configure_alerts(self):
        """Configure alert conditions"""
        while True:
            print(f"\n{Colors.CYAN}=== Alert Configuration ==={Colors.RESET}")
            
            print(f"{Colors.BLUE}Current Alerts:{Colors.RESET}")
            if not self.monitor.alert_conditions:
                print("  No alerts configured")
            else:
                for i, alert in enumerate(self.monitor.alert_conditions, 1):
                    print(f"  {i}. {alert['name']} (triggered {alert['triggered_count']} times)")
                    
            print(f"\n{Colors.BLUE}Options:{Colors.RESET}")
            print(f"{Colors.BLUE}1.{Colors.RESET} Add Alert")
            print(f"{Colors.BLUE}2.{Colors.RESET} Remove Alert")
            print(f"{Colors.BLUE}3.{Colors.RESET} Test Alert")
            print(f"{Colors.BLUE}0.{Colors.RESET} Back")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}")
            
            if choice == "1":
                self._add_alert()
            elif choice == "2":
                self._remove_alert()
            elif choice == "3":
                self._test_alert()
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.RESET}")
                
    def _add_alert(self):
        """Add new alert condition"""
        print(f"\n{Colors.CYAN}=== Add Alert ==={Colors.RESET}")
        
        name = input(f"{Colors.CYAN}Alert name: {Colors.RESET}")
        
        # Select event type
        print(f"\n{Colors.CYAN}Select event type to monitor:{Colors.RESET}")
        event_types = list(self.EventType)
        
        for i, event_type in enumerate(event_types, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {event_type.value}")
            
        try:
            type_choice = int(input(f"\n{Colors.CYAN}Select type: {Colors.RESET}"))
            if 1 <= type_choice <= len(event_types):
                event_type = event_types[type_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Create alert
        condition = {
            'event_type': event_type,
            'min_priority': self.EventPriority.HIGH
        }
        
        def alert_callback(event, alert_info):
            print(f"\n{Colors.RED}[ALERT] {alert_info['name']}: {event.message}{Colors.RESET}")
            
        self.monitor.add_alert_condition(name, condition, alert_callback)
        print(f"{Colors.GREEN}[+] Alert '{name}' added{Colors.RESET}")
        
    def _remove_alert(self):
        """Remove alert condition"""
        if not self.monitor.alert_conditions:
            print(f"{Colors.YELLOW}[!] No alerts to remove{Colors.RESET}")
            return
            
        print(f"\n{Colors.CYAN}Select alert to remove:{Colors.RESET}")
        for i, alert in enumerate(self.monitor.alert_conditions, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {alert['name']}")
            
        try:
            choice = int(input(f"\n{Colors.CYAN}Select alert: {Colors.RESET}"))
            if 1 <= choice <= len(self.monitor.alert_conditions):
                removed = self.monitor.alert_conditions.pop(choice - 1)
                print(f"{Colors.GREEN}[+] Alert '{removed['name']}' removed{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            
    def _test_alert(self):
        """Test alert system"""
        print(f"\n{Colors.CYAN}[*] Testing alert system...{Colors.RESET}")
        
        # Generate test event
        self.monitor.log_event(
            self.EventType.EXPLOIT_SUCCESS,
            "TEST: Alert system test event",
            self.EventPriority.CRITICAL,
            {'test': True}
        )
        
        print(f"{Colors.GREEN}[+] Test event generated{Colors.RESET}")
        
    @handle_errors
    def _show_statistics(self):
        """Show monitoring statistics"""
        print(f"\n{Colors.CYAN}=== Monitoring Statistics ==={Colors.RESET}")
        
        stats = self.monitor.get_statistics()
        
        print(f"{Colors.BLUE}Overall Statistics:{Colors.RESET}")
        print(f"  Total Events: {stats['total_events']}")
        print(f"  Events/Minute: {stats['events_per_minute']:.2f}")
        print(f"  Uptime: {self._format_uptime(stats['uptime_seconds'])}")
        
        print(f"\n{Colors.BLUE}Events by Type:{Colors.RESET}")
        for event_type, count in stats['events_by_type'].items():
            print(f"  {event_type}: {count}")
            
        print(f"\n{Colors.BLUE}Events by Priority:{Colors.RESET}")
        priority_names = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
        for priority, count in stats['events_by_priority'].items():
            print(f"  {priority_names.get(priority, priority)}: {count}")
            
        # Show timeline
        print(f"\n{Colors.BLUE}Recent Activity (last 10 minutes):{Colors.RESET}")
        timeline = self.monitor.get_event_timeline(10)
        
        for event_type, counts in timeline.items():
            if sum(counts) > 0:
                print(f"  {event_type}: {counts}")
                
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours}h {minutes}m {secs}s"
        
    @handle_errors
    def _export_events(self):
        """Export events to file"""
        print(f"\n{Colors.CYAN}=== Export Events ==={Colors.RESET}")
        
        print(f"{Colors.BLUE}Export format:{Colors.RESET}")
        print(f"{Colors.BLUE}1.{Colors.RESET} JSON")
        print(f"{Colors.BLUE}2.{Colors.RESET} CSV")
        
        format_choice = input(f"\n{Colors.CYAN}Select format: {Colors.RESET}")
        
        if format_choice == "1":
            format = "json"
            ext = "json"
        elif format_choice == "2":
            format = "csv"
            ext = "csv"
        else:
            print(f"{Colors.RED}[!] Invalid format{Colors.RESET}")
            return
            
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"monitor_events_{timestamp}.{ext}"
        
        try:
            self.monitor.export_events(filename, format)
            print(f"{Colors.GREEN}[+] Events exported to {filename}{Colors.RESET}")
            print(f"{Colors.BLUE}[+] Total events: {len(self.monitor.events)}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] Export failed: {e}{Colors.RESET}")
            
    @handle_errors
    def _test_events(self):
        """Generate test events"""
        print(f"\n{Colors.CYAN}=== Generate Test Events ==={Colors.RESET}")
        
        # Start monitoring if not active
        if not self.monitor.monitoring_active:
            self.monitor.start()
            
        # Generate various test events
        test_scenarios = [
            (self.EventType.EXPLOIT_START, "Starting test exploit", self.EventPriority.HIGH),
            (self.EventType.PAYLOAD_SENT, "Sending test payload", self.EventPriority.MEDIUM),
            (self.EventType.EXPLOIT_SUCCESS, "Test exploit succeeded", self.EventPriority.CRITICAL),
            (self.EventType.CALLBACK_RECEIVED, "Test callback received", self.EventPriority.CRITICAL),
            (self.EventType.WARNING, "Test warning message", self.EventPriority.MEDIUM),
            (self.EventType.ERROR, "Test error occurred", self.EventPriority.HIGH),
        ]
        
        print(f"{Colors.CYAN}[*] Generating test events...{Colors.RESET}")
        
        for event_type, message, priority in test_scenarios:
            self.monitor.log_event(event_type, f"TEST: {message}", priority, {'test': True})
            print(f"{Colors.GREEN}[+] Generated: {event_type.value}{Colors.RESET}")
            time.sleep(0.5)
            
        # Test exploit monitor
        print(f"\n{Colors.CYAN}[*] Testing exploit monitor...{Colors.RESET}")
        
        exploit_id = "test_exploit_001"
        self.exploit_monitor.exploit_start(exploit_id, "192.168.1.100", "CVE-TEST")
        time.sleep(1)
        
        self.exploit_monitor.payload_sent(exploit_id, 1024)
        time.sleep(1)
        
        self.exploit_monitor.callback_received(exploit_id, "192.168.1.100:4444")
        time.sleep(1)
        
        self.exploit_monitor.exploit_success(exploit_id, "Shell access gained")
        
        print(f"{Colors.GREEN}[+] Test events generated successfully{Colors.RESET}")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    def _quick_filter(self):
        """Quick filter from terminal display"""
        print(f"\n{Colors.CYAN}Quick Filter:{Colors.RESET}")
        print(f"1. High Priority Only")
        print(f"2. Exploits Only")
        print(f"3. Errors Only")
        print(f"4. Clear Filters")
        
        choice = input(f"{Colors.CYAN}Select: {Colors.RESET}")
        
        if choice == "1":
            self.monitor.set_filter('min_priority', self.EventPriority.HIGH)
        elif choice == "2":
            self.monitor.set_filter('types', [
                self.EventType.EXPLOIT_START,
                self.EventType.EXPLOIT_SUCCESS,
                self.EventType.EXPLOIT_FAIL
            ])
        elif choice == "3":
            self.monitor.set_filter('types', [self.EventType.ERROR])
        elif choice == "4":
            self.monitor.clear_filters()

def main():
    """Main function for testing"""
    menu = MonitoringMenu()
    menu.display()

if __name__ == "__main__":
    main()