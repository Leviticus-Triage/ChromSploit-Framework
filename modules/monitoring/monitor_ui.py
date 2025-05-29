import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from .live_monitor import get_live_monitor, EventType, EventPriority

class MonitorUI:
    """Terminal-based UI for live monitoring"""
    
    def __init__(self):
        self.monitor = get_live_monitor()
        self.display_active = False
        self.display_thread = None
        self.refresh_rate = 1.0  # seconds
        
        # Display settings
        self.max_events_display = 20
        self.show_stats = True
        self.color_enabled = True
        
    def start_display(self):
        """Start the live display"""
        if self.display_active:
            return
            
        self.display_active = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
    def stop_display(self):
        """Stop the live display"""
        self.display_active = False
        if self.display_thread:
            self.display_thread.join(timeout=5)
            
    def _display_loop(self):
        """Main display loop"""
        while self.display_active:
            self._refresh_display()
            time.sleep(self.refresh_rate)
            
    def _refresh_display(self):
        """Refresh the display"""
        # Clear screen
        print("\033[2J\033[H", end='')
        
        # Header
        self._print_header()
        
        # Statistics
        if self.show_stats:
            self._print_statistics()
            
        # Events
        self._print_events()
        
        # Footer
        self._print_footer()
        
    def _print_header(self):
        """Print display header"""
        print("=" * 80)
        print(f"{'ChromSploit Live Monitor':^80}")
        print(f"{'Last Update: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
        print("=" * 80)
        print()
        
    def _print_statistics(self):
        """Print monitoring statistics"""
        stats = self.monitor.get_statistics()
        
        print("STATISTICS:")
        print(f"  Total Events: {stats['total_events']}")
        print(f"  Events/Min: {stats['events_per_minute']:.2f}")
        print(f"  Uptime: {self._format_uptime(stats['uptime_seconds'])}")
        
        # Event type breakdown
        print("\n  Event Types:")
        for event_type, count in stats['events_by_type'].items():
            print(f"    {event_type}: {count}")
            
        print()
        
    def _print_events(self):
        """Print recent events"""
        events = self.monitor.get_events(limit=self.max_events_display)
        
        print(f"RECENT EVENTS (showing {len(events)} of {len(self.monitor.events)}):")
        print("-" * 80)
        
        if not events:
            print("  No events to display")
        else:
            for event in events:
                self._print_event(event)
                
        print("-" * 80)
        
    def _print_event(self, event: Dict[str, Any]):
        """Print a single event"""
        timestamp = datetime.fromisoformat(event['timestamp']).strftime('%H:%M:%S')
        event_type = event['type']
        message = event['message']
        priority = event['priority']
        
        # Color based on priority
        if self.color_enabled:
            color = self._get_priority_color(priority)
            reset = '\033[0m'
        else:
            color = ''
            reset = ''
            
        # Format event line
        print(f"{color}[{timestamp}] [{event_type:15}] {message}{reset}")
        
        # Show data if present
        if event.get('data'):
            for key, value in event['data'].items():
                print(f"            {key}: {value}")
                
    def _print_footer(self):
        """Print display footer"""
        print()
        print("=" * 80)
        print("Commands: [q]uit | [f]ilter | [c]lear | [e]xport | [s]tats toggle")
        
    def _get_priority_color(self, priority: int) -> str:
        """Get ANSI color code for priority"""
        colors = {
            1: '\033[90m',  # Low - Gray
            2: '\033[0m',   # Medium - Normal
            3: '\033[93m',  # High - Yellow
            4: '\033[91m'   # Critical - Red
        }
        return colors.get(priority, '\033[0m')
        
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable form"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def set_refresh_rate(self, rate: float):
        """Set display refresh rate"""
        self.refresh_rate = max(0.1, rate)
        
    def toggle_stats(self):
        """Toggle statistics display"""
        self.show_stats = not self.show_stats
        
    def set_max_events(self, max_events: int):
        """Set maximum events to display"""
        self.max_events_display = max(1, max_events)

class MonitorDashboard:
    """Web-based monitoring dashboard"""
    
    def __init__(self, port: int = 8889):
        self.monitor = get_live_monitor()
        self.port = port
        self.server = None
        self.server_thread = None
        
    def start(self):
        """Start the web dashboard"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        monitor = self.monitor
        
        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self._get_dashboard_html().encode())
                    
                elif self.path == '/api/events':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    events = monitor.get_events(limit=100)
                    self.wfile.write(json.dumps(events).encode())
                    
                elif self.path == '/api/stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    stats = monitor.get_statistics()
                    self.wfile.write(json.dumps(stats).encode())
                    
                elif self.path == '/api/timeline':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    timeline = monitor.get_event_timeline(60)
                    self.wfile.write(json.dumps(timeline).encode())
                    
                else:
                    self.send_response(404)
                    self.end_headers()
                    
            def log_message(self, format, *args):
                # Suppress request logging
                pass
                
            def _get_dashboard_html(self):
                return '''
<!DOCTYPE html>
<html>
<head>
    <title>ChromSploit Live Monitor</title>
    <style>
        body {
            font-family: monospace;
            background: #1a1a1a;
            color: #0f0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #0f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: #222;
            border: 1px solid #0f0;
            padding: 15px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
        }
        .events {
            background: #222;
            border: 1px solid #0f0;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
        }
        .event {
            margin-bottom: 10px;
            padding: 5px;
            border-left: 3px solid #0f0;
        }
        .event.critical {
            border-left-color: #f00;
        }
        .event.high {
            border-left-color: #ff0;
        }
        .timeline {
            margin-top: 20px;
            height: 200px;
        }
        #update-time {
            font-size: 12px;
            color: #888;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ChromSploit Live Monitor</h1>
            <div id="update-time"></div>
        </div>
        
        <div class="stats" id="stats">
            <!-- Stats will be populated here -->
        </div>
        
        <div class="events" id="events">
            <h3>Recent Events</h3>
            <div id="event-list">
                <!-- Events will be populated here -->
            </div>
        </div>
        
        <div class="timeline">
            <canvas id="timeline-chart"></canvas>
        </div>
    </div>
    
    <script>
        let chart = null;
        
        async function updateDashboard() {
            // Update stats
            const statsRes = await fetch('/api/stats');
            const stats = await statsRes.json();
            updateStats(stats);
            
            // Update events
            const eventsRes = await fetch('/api/events');
            const events = await eventsRes.json();
            updateEvents(events);
            
            // Update timeline
            const timelineRes = await fetch('/api/timeline');
            const timeline = await timelineRes.json();
            updateTimeline(timeline);
            
            // Update time
            document.getElementById('update-time').textContent = 
                'Last Update: ' + new Date().toLocaleTimeString();
        }
        
        function updateStats(stats) {
            const container = document.getElementById('stats');
            container.innerHTML = `
                <div class="stat-box">
                    <div>Total Events</div>
                    <div class="stat-value">${stats.total_events}</div>
                </div>
                <div class="stat-box">
                    <div>Events/Min</div>
                    <div class="stat-value">${stats.events_per_minute.toFixed(2)}</div>
                </div>
                <div class="stat-box">
                    <div>Uptime</div>
                    <div class="stat-value">${formatUptime(stats.uptime_seconds)}</div>
                </div>
            `;
        }
        
        function updateEvents(events) {
            const container = document.getElementById('event-list');
            container.innerHTML = events.map(event => {
                const priorityClass = event.priority >= 4 ? 'critical' : 
                                    event.priority >= 3 ? 'high' : '';
                const time = new Date(event.timestamp).toLocaleTimeString();
                return `
                    <div class="event ${priorityClass}">
                        <strong>[${time}]</strong> [${event.type}] ${event.message}
                    </div>
                `;
            }).join('');
        }
        
        function updateTimeline(timeline) {
            const ctx = document.getElementById('timeline-chart').getContext('2d');
            
            const datasets = Object.entries(timeline).map(([type, data]) => ({
                label: type,
                data: data.reverse(),
                borderColor: getColorForType(type),
                fill: false
            }));
            
            if (chart) {
                chart.data.datasets = datasets;
                chart.update();
            } else {
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: Array.from({length: 60}, (_, i) => `${59-i}m`),
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Event Timeline (Last 60 Minutes)'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }
        
        function getColorForType(type) {
            const colors = {
                'exploit_start': '#00ff00',
                'exploit_success': '#00ffff',
                'exploit_fail': '#ff0000',
                'error': '#ff00ff',
                'warning': '#ffff00',
                'info': '#ffffff'
            };
            return colors[type] || '#888888';
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        // Update every 2 seconds
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
                '''
        
        self.server = HTTPServer(('', self.port), DashboardHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
    def stop(self):
        """Stop the web dashboard"""
        if self.server:
            self.server.shutdown()
            self.server_thread.join(timeout=5)