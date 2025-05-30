#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework - Session Manager
Manages sessions from various C2 frameworks (Sliver, Metasploit, etc.)
"""

import os
import json
import time
import threading
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

from core.enhanced_logger import get_logger
from core.colors import Colors
from core.utils import Utils
from core.path_utils import PathUtils


class Session:
    """Represents a single session from any C2 framework"""
    
    def __init__(self, session_id: str, framework: str, target_ip: str, 
                 session_type: str, username: str = None, hostname: str = None):
        self.id = session_id
        self.framework = framework  # 'sliver', 'metasploit', etc.
        self.target_ip = target_ip
        self.session_type = session_type  # 'shell', 'meterpreter', 'beacon', etc.
        self.username = username or "unknown"
        self.hostname = hostname or target_ip
        self.created_at = datetime.now()
        self.last_checkin = datetime.now()
        self.active = True
        self.commands_history = []
        self.metadata = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'framework': self.framework,
            'target_ip': self.target_ip,
            'session_type': self.session_type,
            'username': self.username,
            'hostname': self.hostname,
            'created_at': self.created_at.isoformat(),
            'last_checkin': self.last_checkin.isoformat(),
            'active': self.active,
            'commands_count': len(self.commands_history),
            'metadata': self.metadata
        }


class C2Framework(ABC):
    """Abstract base class for C2 framework integrations"""
    
    @abstractmethod
    def get_sessions(self) -> List[Session]:
        """Get all active sessions from the framework"""
        pass
    
    @abstractmethod
    def execute_command(self, session_id: str, command: str) -> Tuple[bool, str]:
        """Execute a command in a specific session"""
        pass
    
    @abstractmethod
    def open_shell(self, session_id: str) -> bool:
        """Open an interactive shell for a session"""
        pass
    
    @abstractmethod
    def check_connection(self) -> bool:
        """Check if the framework is available and connected"""
        pass


class SliverC2Framework(C2Framework):
    """Sliver C2 framework integration"""
    
    def __init__(self):
        self.logger = get_logger()
        self.server_host = "localhost"
        self.server_port = 31337
        self.mtls_config = PathUtils.get_data_path("sliver/configs/client.cfg")
        
    def get_sessions(self) -> List[Session]:
        """Get all active Sliver sessions"""
        sessions = []
        
        try:
            # Try to get sessions using sliver-client
            cmd = ["sliver-client", "--config", self.mtls_config, "--json", "sessions"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                session_data = json.loads(result.stdout)
                
                for s in session_data.get('sessions', []):
                    session = Session(
                        session_id=s['ID'],
                        framework='sliver',
                        target_ip=s['RemoteAddress'].split(':')[0],
                        session_type='beacon' if s.get('IsBeacon') else 'session',
                        username=s.get('Username', 'unknown'),
                        hostname=s.get('Hostname', 'unknown')
                    )
                    session.metadata = {
                        'os': s.get('OS', 'unknown'),
                        'arch': s.get('Arch', 'unknown'),
                        'pid': s.get('PID', 0),
                        'process': s.get('ProcessName', 'unknown')
                    }
                    sessions.append(session)
                    
        except Exception as e:
            self.logger.error(f"Failed to get Sliver sessions: {e}")
            
        return sessions
    
    def execute_command(self, session_id: str, command: str) -> Tuple[bool, str]:
        """Execute a command in a Sliver session"""
        try:
            cmd = [
                "sliver-client", "--config", self.mtls_config, "--json",
                "use", session_id, "--", command
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
    
    def open_shell(self, session_id: str) -> bool:
        """Open an interactive shell for a Sliver session"""
        try:
            # Launch sliver-client in a new terminal
            terminal_cmd = self._get_terminal_command()
            cmd = f"{terminal_cmd} 'sliver-client --config {self.mtls_config} use {session_id}'"
            
            subprocess.Popen(cmd, shell=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open Sliver shell: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if Sliver server is available"""
        try:
            # Try to connect to Sliver server
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.server_host, self.server_port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def _get_terminal_command(self) -> str:
        """Get the terminal command based on the environment"""
        if os.environ.get('DISPLAY'):
            # GUI environment
            for term in ['gnome-terminal --', 'konsole -e', 'xterm -e', 'terminator -e']:
                if Utils.is_tool_available(term.split()[0]):
                    return term
        
        # Fallback to screen/tmux
        if Utils.is_tool_available('tmux'):
            return 'tmux new-window'
        elif Utils.is_tool_available('screen'):
            return 'screen -t sliver'
        
        return 'bash -c'


class MetasploitFramework(C2Framework):
    """Metasploit framework integration"""
    
    def __init__(self):
        self.logger = get_logger()
        self.rpc_host = "localhost"
        self.rpc_port = 55553
        self.rpc_user = "msf"
        self.rpc_pass = "chromsploit"
        self.api_token = None
        
    def get_sessions(self) -> List[Session]:
        """Get all active Metasploit sessions"""
        sessions = []
        
        try:
            # Use msfconsole to list sessions
            cmd = ["msfconsole", "-q", "-x", "sessions -l -v; exit"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse session output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('Active sessions') and '===' not in line:
                        # Parse session line
                        parts = line.split()
                        if len(parts) >= 5 and parts[0].isdigit():
                            session = Session(
                                session_id=parts[0],
                                framework='metasploit',
                                target_ip=parts[2],
                                session_type=parts[1],
                                username=parts[4] if len(parts) > 4 else 'unknown'
                            )
                            sessions.append(session)
                            
        except Exception as e:
            self.logger.error(f"Failed to get Metasploit sessions: {e}")
            
        return sessions
    
    def execute_command(self, session_id: str, command: str) -> Tuple[bool, str]:
        """Execute a command in a Metasploit session"""
        try:
            # Use msfconsole to execute command
            msf_cmd = f"sessions -i {session_id}; {command}; background; exit"
            cmd = ["msfconsole", "-q", "-x", msf_cmd]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
    
    def open_shell(self, session_id: str) -> bool:
        """Open an interactive shell for a Metasploit session"""
        try:
            # Launch msfconsole in a new terminal
            terminal_cmd = self._get_terminal_command()
            cmd = f"{terminal_cmd} 'msfconsole -q -x \"sessions -i {session_id}\"'"
            
            subprocess.Popen(cmd, shell=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open Metasploit shell: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if Metasploit RPC is available"""
        try:
            # Check if msfconsole is available
            return Utils.is_tool_available('msfconsole')
            
        except Exception:
            return False
    
    def _get_terminal_command(self) -> str:
        """Get the terminal command based on the environment"""
        if os.environ.get('DISPLAY'):
            # GUI environment
            for term in ['gnome-terminal --', 'konsole -e', 'xterm -e', 'terminator -e']:
                if Utils.is_tool_available(term.split()[0]):
                    return term
        
        # Fallback to screen/tmux
        if Utils.is_tool_available('tmux'):
            return 'tmux new-window'
        elif Utils.is_tool_available('screen'):
            return 'screen -t metasploit'
        
        return 'bash -c'


class SessionManager:
    """Manages sessions from multiple C2 frameworks"""
    
    def __init__(self):
        self.logger = get_logger()
        self.frameworks: Dict[str, C2Framework] = {}
        self.sessions: Dict[str, Session] = {}
        self.update_thread = None
        self.running = False
        
        # Initialize available frameworks
        self._initialize_frameworks()
        
    def _initialize_frameworks(self):
        """Initialize available C2 frameworks"""
        # Try to initialize Sliver
        try:
            sliver = SliverC2Framework()
            if sliver.check_connection():
                self.frameworks['sliver'] = sliver
                self.logger.info("Sliver C2 framework initialized")
        except Exception as e:
            self.logger.debug(f"Sliver not available: {e}")
        
        # Try to initialize Metasploit
        try:
            msf = MetasploitFramework()
            if msf.check_connection():
                self.frameworks['metasploit'] = msf
                self.logger.info("Metasploit framework initialized")
        except Exception as e:
            self.logger.debug(f"Metasploit not available: {e}")
    
    def start_monitoring(self):
        """Start monitoring sessions"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._monitor_sessions)
            self.update_thread.daemon = True
            self.update_thread.start()
            self.logger.info("Session monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring sessions"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        self.logger.info("Session monitoring stopped")
    
    def _monitor_sessions(self):
        """Monitor sessions from all frameworks"""
        while self.running:
            try:
                all_sessions = {}
                
                # Get sessions from each framework
                for name, framework in self.frameworks.items():
                    try:
                        sessions = framework.get_sessions()
                        for session in sessions:
                            all_sessions[f"{name}_{session.id}"] = session
                    except Exception as e:
                        self.logger.error(f"Error getting sessions from {name}: {e}")
                
                # Update session list
                self.sessions = all_sessions
                
                # Mark inactive sessions
                for session_key, session in self.sessions.items():
                    if session_key not in all_sessions:
                        session.active = False
                
                # Sleep before next update
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Session monitoring error: {e}")
                time.sleep(10)
    
    def get_all_sessions(self) -> List[Session]:
        """Get all active sessions"""
        return [s for s in self.sessions.values() if s.active]
    
    def get_session(self, session_key: str) -> Optional[Session]:
        """Get a specific session"""
        return self.sessions.get(session_key)
    
    def execute_command(self, session_key: str, command: str) -> Tuple[bool, str]:
        """Execute a command in a session"""
        session = self.get_session(session_key)
        if not session:
            return False, "Session not found"
        
        framework = self.frameworks.get(session.framework)
        if not framework:
            return False, f"Framework {session.framework} not available"
        
        # Execute command
        success, output = framework.execute_command(session.id, command)
        
        # Log command in history
        if success:
            session.commands_history.append({
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'success': success
            })
            session.last_checkin = datetime.now()
        
        return success, output
    
    def open_shell(self, session_key: str) -> bool:
        """Open an interactive shell for a session"""
        session = self.get_session(session_key)
        if not session:
            self.logger.error("Session not found")
            return False
        
        framework = self.frameworks.get(session.framework)
        if not framework:
            self.logger.error(f"Framework {session.framework} not available")
            return False
        
        return framework.open_shell(session.id)
    
    def export_sessions(self, filename: str = None) -> str:
        """Export all sessions to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = PathUtils.get_output_path(f"sessions_{timestamp}.json")
        
        sessions_data = {
            'exported_at': datetime.now().isoformat(),
            'total_sessions': len(self.sessions),
            'active_sessions': len([s for s in self.sessions.values() if s.active]),
            'frameworks': list(self.frameworks.keys()),
            'sessions': [s.to_dict() for s in self.sessions.values()]
        }
        
        with open(filename, 'w') as f:
            json.dump(sessions_data, f, indent=2)
        
        return filename
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        active_sessions = [s for s in self.sessions.values() if s.active]
        
        stats = {
            'total_sessions': len(self.sessions),
            'active_sessions': len(active_sessions),
            'frameworks_connected': len(self.frameworks),
            'sessions_by_framework': {},
            'sessions_by_type': {},
            'sessions_by_os': {}
        }
        
        # Count by framework
        for session in active_sessions:
            framework = session.framework
            stats['sessions_by_framework'][framework] = stats['sessions_by_framework'].get(framework, 0) + 1
            
            # Count by type
            session_type = session.session_type
            stats['sessions_by_type'][session_type] = stats['sessions_by_type'].get(session_type, 0) + 1
            
            # Count by OS
            os_type = session.metadata.get('os', 'unknown')
            stats['sessions_by_os'][os_type] = stats['sessions_by_os'].get(os_type, 0) + 1
        
        return stats


# Singleton instance
_session_manager_instance = None


def get_session_manager() -> SessionManager:
    """Get the singleton SessionManager instance"""
    global _session_manager_instance
    if _session_manager_instance is None:
        _session_manager_instance = SessionManager()
    return _session_manager_instance