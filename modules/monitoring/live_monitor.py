import threading
import time
import json
import os
from datetime import datetime
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Callable, Deque
from enum import Enum
import logging

class EventType(Enum):
    EXPLOIT_START = "exploit_start"
    EXPLOIT_SUCCESS = "exploit_success"
    EXPLOIT_FAIL = "exploit_fail"
    PAYLOAD_SENT = "payload_sent"
    CALLBACK_RECEIVED = "callback_received"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    NETWORK_ACTIVITY = "network_activity"
    SYSTEM_EVENT = "system_event"

class EventPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class MonitorEvent:
    def __init__(self, event_type: EventType, message: str, 
                 priority: EventPriority = EventPriority.MEDIUM,
                 data: Dict[str, Any] = None):
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.message = message
        self.priority = priority
        self.data = data or {}
        self.id = f"{self.timestamp.timestamp()}_{event_type.value}"
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'type': self.event_type.value,
            'message': self.message,
            'priority': self.priority.value,
            'data': self.data
        }

class LiveMonitor:
    def __init__(self, max_events: int = 1000):
        self.events: Deque[MonitorEvent] = deque(maxlen=max_events)
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.monitoring_active = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'events_by_priority': defaultdict(int),
            'start_time': datetime.now()
        }
        
        # Real-time filters
        self.filters = {
            'types': None,  # None means all types
            'min_priority': EventPriority.LOW,
            'search_term': None
        }
        
        # Alerting
        self.alert_conditions: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable] = []
        
    def start(self):
        """Start live monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log_event(EventType.SYSTEM_EVENT, "Live monitoring started", EventPriority.LOW)
        
    def stop(self):
        """Stop live monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
        self.log_event(EventType.SYSTEM_EVENT, "Live monitoring stopped", EventPriority.LOW)
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            # Process any queued tasks
            # This is where we'd integrate with other systems
            time.sleep(0.1)
            
    def log_event(self, event_type: EventType, message: str, 
                  priority: EventPriority = EventPriority.MEDIUM,
                  data: Dict[str, Any] = None):
        """Log a monitoring event"""
        event = MonitorEvent(event_type, message, priority, data)
        
        # Add to events queue
        self.events.append(event)
        
        # Update statistics
        self.stats['total_events'] += 1
        self.stats['events_by_type'][event_type.value] += 1
        self.stats['events_by_priority'][priority.value] += 1
        
        # Check alert conditions
        self._check_alerts(event)
        
        # Call event handlers
        for handler in self.event_handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
                
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type].append(handler)
        
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister an event handler"""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            
    def get_events(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get recent events with filtering"""
        filtered_events = []
        
        for event in reversed(self.events):
            # Apply filters
            if self.filters['types'] and event.event_type not in self.filters['types']:
                continue
                
            if event.priority.value < self.filters['min_priority'].value:
                continue
                
            if self.filters['search_term']:
                search_term = self.filters['search_term'].lower()
                if search_term not in event.message.lower():
                    # Also check data
                    data_str = json.dumps(event.data).lower()
                    if search_term not in data_str:
                        continue
                        
            filtered_events.append(event.to_dict())
            
        # Apply pagination
        return filtered_events[offset:offset + limit]
        
    def set_filter(self, filter_type: str, value: Any):
        """Set a filter for event viewing"""
        if filter_type == 'types':
            self.filters['types'] = value
        elif filter_type == 'min_priority':
            self.filters['min_priority'] = value
        elif filter_type == 'search_term':
            self.filters['search_term'] = value
            
    def clear_filters(self):
        """Clear all filters"""
        self.filters = {
            'types': None,
            'min_priority': EventPriority.LOW,
            'search_term': None
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'total_events': self.stats['total_events'],
            'events_by_type': dict(self.stats['events_by_type']),
            'events_by_priority': dict(self.stats['events_by_priority']),
            'uptime_seconds': uptime.total_seconds(),
            'events_per_minute': self.stats['total_events'] / (uptime.total_seconds() / 60) if uptime.total_seconds() > 0 else 0,
            'active_filters': {
                'types': [t.value for t in self.filters['types']] if self.filters['types'] else None,
                'min_priority': self.filters['min_priority'].name,
                'search_term': self.filters['search_term']
            }
        }
        
    def add_alert_condition(self, name: str, condition: Dict[str, Any], 
                           callback: Callable = None):
        """Add an alert condition"""
        alert = {
            'name': name,
            'condition': condition,
            'callback': callback,
            'triggered_count': 0,
            'last_triggered': None
        }
        
        self.alert_conditions.append(alert)
        
        if callback:
            self.alert_callbacks.append(callback)
            
    def _check_alerts(self, event: MonitorEvent):
        """Check if event triggers any alerts"""
        for alert in self.alert_conditions:
            condition = alert['condition']
            
            # Check event type condition
            if 'event_type' in condition:
                if event.event_type != condition['event_type']:
                    continue
                    
            # Check priority condition
            if 'min_priority' in condition:
                if event.priority.value < condition['min_priority']:
                    continue
                    
            # Check message pattern
            if 'message_contains' in condition:
                if condition['message_contains'] not in event.message:
                    continue
                    
            # Check data conditions
            if 'data_match' in condition:
                match = True
                for key, value in condition['data_match'].items():
                    if event.data.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
                    
            # Alert triggered
            alert['triggered_count'] += 1
            alert['last_triggered'] = datetime.now()
            
            if alert['callback']:
                try:
                    alert['callback'](event, alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
                    
    def export_events(self, filepath: str, format: str = 'json'):
        """Export events to file"""
        events_data = [event.to_dict() for event in self.events]
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(events_data, f, indent=2)
        elif format == 'csv':
            import csv
            with open(filepath, 'w', newline='') as f:
                if events_data:
                    writer = csv.DictWriter(f, fieldnames=events_data[0].keys())
                    writer.writeheader()
                    writer.writerows(events_data)
                    
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        self.stats['total_events'] = 0
        self.stats['events_by_type'].clear()
        self.stats['events_by_priority'].clear()
        
    def get_event_timeline(self, minutes: int = 60) -> Dict[str, List[int]]:
        """Get event timeline for visualization"""
        timeline = defaultdict(lambda: [0] * minutes)
        now = datetime.now()
        
        for event in self.events:
            # Calculate minutes ago
            delta = now - event.timestamp
            minutes_ago = int(delta.total_seconds() / 60)
            
            if minutes_ago < minutes:
                timeline[event.event_type.value][minutes - minutes_ago - 1] += 1
                
        return dict(timeline)

class ExploitMonitor:
    """Specialized monitor for exploit execution"""
    
    def __init__(self, live_monitor: LiveMonitor):
        self.monitor = live_monitor
        self.active_exploits: Dict[str, Dict[str, Any]] = {}
        
    def exploit_start(self, exploit_id: str, target: str, exploit_type: str):
        """Log exploit start"""
        self.active_exploits[exploit_id] = {
            'target': target,
            'type': exploit_type,
            'start_time': datetime.now(),
            'status': 'running'
        }
        
        self.monitor.log_event(
            EventType.EXPLOIT_START,
            f"Started {exploit_type} exploit against {target}",
            EventPriority.HIGH,
            {
                'exploit_id': exploit_id,
                'target': target,
                'type': exploit_type
            }
        )
        
    def exploit_success(self, exploit_id: str, result: Any = None):
        """Log exploit success"""
        if exploit_id in self.active_exploits:
            exploit_data = self.active_exploits[exploit_id]
            exploit_data['status'] = 'success'
            exploit_data['end_time'] = datetime.now()
            
            duration = (exploit_data['end_time'] - exploit_data['start_time']).total_seconds()
            
            self.monitor.log_event(
                EventType.EXPLOIT_SUCCESS,
                f"Exploit {exploit_id} succeeded in {duration:.2f}s",
                EventPriority.CRITICAL,
                {
                    'exploit_id': exploit_id,
                    'duration': duration,
                    'result': str(result) if result else None
                }
            )
            
    def exploit_fail(self, exploit_id: str, error: str):
        """Log exploit failure"""
        if exploit_id in self.active_exploits:
            exploit_data = self.active_exploits[exploit_id]
            exploit_data['status'] = 'failed'
            exploit_data['end_time'] = datetime.now()
            exploit_data['error'] = error
            
            self.monitor.log_event(
                EventType.EXPLOIT_FAIL,
                f"Exploit {exploit_id} failed: {error}",
                EventPriority.HIGH,
                {
                    'exploit_id': exploit_id,
                    'error': error
                }
            )
            
    def payload_sent(self, exploit_id: str, payload_size: int):
        """Log payload delivery"""
        self.monitor.log_event(
            EventType.PAYLOAD_SENT,
            f"Payload sent for exploit {exploit_id} ({payload_size} bytes)",
            EventPriority.MEDIUM,
            {
                'exploit_id': exploit_id,
                'payload_size': payload_size
            }
        )
        
    def callback_received(self, exploit_id: str, source: str):
        """Log callback received"""
        self.monitor.log_event(
            EventType.CALLBACK_RECEIVED,
            f"Callback received from {source}",
            EventPriority.CRITICAL,
            {
                'exploit_id': exploit_id,
                'source': source
            }
        )

# Singleton instances
_live_monitor = None
_exploit_monitor = None

def get_live_monitor() -> LiveMonitor:
    """Get the global live monitor instance"""
    global _live_monitor
    if _live_monitor is None:
        _live_monitor = LiveMonitor()
    return _live_monitor

def get_exploit_monitor() -> ExploitMonitor:
    """Get the global exploit monitor instance"""
    global _exploit_monitor
    if _exploit_monitor is None:
        _exploit_monitor = ExploitMonitor(get_live_monitor())
    return _exploit_monitor