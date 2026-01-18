#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Asciinema Terminal Recording Manager

This module provides terminal recording functionality using asciinema
with web playback interface.
"""

import os
import subprocess
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

from core.enhanced_logger import get_logger
from core.error_handler import handle_errors, ErrorContext
from core.colors import Colors

class AsciinemaWebHandler(SimpleHTTPRequestHandler):
 """Custom HTTP handler for asciinema web interface"""
 
 def __init__(self, *args, recordings_dir=None, **kwargs):
 self.recordings_dir = recordings_dir
 super().__init__(*args, **kwargs)
 
 def do_GET(self):
 """Handle GET requests"""
 if self.path == '/':
 self.send_recording_list()
 elif self.path.startswith('/play/'):
 recording_id = self.path.split('/')[-1]
 self.send_player_page(recording_id)
 elif self.path.startswith('/rec/'):
 recording_file = self.path.split('/')[-1]
 self.send_recording_file(recording_file)
 elif self.path == '/style.css':
 self.send_css()
 else:
 super().do_GET()
 
 def send_recording_list(self):
 """Send list of available recordings"""
 recordings = []
 if self.recordings_dir and os.path.exists(self.recordings_dir):
 for file in os.listdir(self.recordings_dir):
 if file.endswith('.cast'):
 filepath = os.path.join(self.recordings_dir, file)
 stat = os.stat(filepath)
 recordings.append({
 'id': file[:-5], # Remove .cast extension
 'filename': file,
 'size': stat.st_size,
 'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
 })
 
 html = f"""
<!DOCTYPE html>
<html>
<head>
 <title>ChromSploit Framework - Terminal Recordings</title>
 <link rel="stylesheet" href="/style.css">
 <meta charset="utf-8">
</head>
<body>
 <div class="container">
 <h1> ChromSploit Framework - Terminal Recordings</h1>
 <div class="info">
 <p>Available recordings: {len(recordings)}</p>
 </div>
 
 <div class="recordings-list">
"""
 
 if recordings:
 for rec in recordings:
 html += f"""
 <div class="recording-item">
 <h3>{rec['id']}</h3>
 <div class="recording-meta">
 <span> {rec['created']}</span>
 <span> {rec['size']} bytes</span>
 </div>
 <a href="/play/{rec['id']}" class="play-button">▶ Play Recording</a>
 </div>
"""
 else:
 html += """
 <div class="no-recordings">
 <p>No recordings available yet.</p>
 <p>Start a recording with: <code>starte asciinema</code></p>
 </div>
"""
 
 html += """
 </div>
 </div>
</body>
</html>
"""
 
 self.send_response(200)
 self.send_header('Content-type', 'text/html')
 self.end_headers()
 self.wfile.write(html.encode('utf-8'))
 
 def send_player_page(self, recording_id: str):
 """Send asciinema player page for specific recording"""
 html = f"""
<!DOCTYPE html>
<html>
<head>
 <title>ChromSploit Recording: {recording_id}</title>
 <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.6.0/dist/bundle/asciinema-player.css" />
 <link rel="stylesheet" href="/style.css">
 <meta charset="utf-8">
</head>
<body>
 <div class="container">
 <h1> ChromSploit Framework Recording</h1>
 <div class="recording-header">
 <h2>{recording_id}</h2>
 <a href="/" class="back-button">← Back to List</a>
 </div>
 
 <div class="player-container">
 <div id="player"></div>
 </div>
 
 <div class="controls">
 <p>Use the player controls to play, pause, and seek through the recording.</p>
 </div>
 </div>
 
 <script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.6.0/dist/bundle/asciinema-player.min.js"></script>
 <script>
 AsciinemaPlayer.create('/rec/{recording_id}.cast', document.getElementById('player'), {{
 autoPlay: false,
 theme: 'monokai',
 fontSize: '14px',
 fit: 'width',
 controls: true
 }});
 </script>
</body>
</html>
"""
 
 self.send_response(200)
 self.send_header('Content-type', 'text/html')
 self.end_headers()
 self.wfile.write(html.encode('utf-8'))
 
 def send_recording_file(self, filename: str):
 """Send recording file"""
 if not filename.endswith('.cast'):
 filename += '.cast'
 
 filepath = os.path.join(self.recordings_dir, filename)
 
 if os.path.exists(filepath):
 self.send_response(200)
 self.send_header('Content-type', 'application/json')
 self.end_headers()
 
 with open(filepath, 'rb') as f:
 self.wfile.write(f.read())
 else:
 self.send_error(404, "Recording not found")
 
 def send_css(self):
 """Send CSS stylesheet"""
 css = """
body {
 font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
 margin: 0;
 padding: 20px;
 background-color: #1a1a1a;
 color: #ffffff;
 line-height: 1.6;
}

.container {
 max-width: 1200px;
 margin: 0 auto;
 padding: 20px;
}

h1 {
 color: #00ff00;
 text-align: center;
 margin-bottom: 30px;
 text-shadow: 0 0 10px #00ff0040;
}

h2 {
 color: #ffffff;
 margin-bottom: 15px;
}

.info {
 background-color: #2a2a2a;
 padding: 15px;
 border-radius: 8px;
 margin-bottom: 30px;
 border-left: 4px solid #00ff00;
}

.recordings-list {
 display: grid;
 gap: 20px;
}

.recording-item {
 background-color: #2a2a2a;
 padding: 20px;
 border-radius: 8px;
 border: 1px solid #404040;
 transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recording-item:hover {
 transform: translateY(-2px);
 box-shadow: 0 4px 12px rgba(0, 255, 0, 0.2);
}

.recording-meta {
 color: #888;
 margin: 10px 0;
}

.recording-meta span {
 margin-right: 20px;
}

.play-button {
 display: inline-block;
 background-color: #00ff00;
 color: #000000;
 padding: 10px 20px;
 text-decoration: none;
 border-radius: 5px;
 font-weight: bold;
 transition: background-color 0.2s ease;
}

.play-button:hover {
 background-color: #00cc00;
}

.recording-header {
 display: flex;
 justify-content: space-between;
 align-items: center;
 margin-bottom: 30px;
 padding-bottom: 15px;
 border-bottom: 1px solid #404040;
}

.back-button {
 color: #00ff00;
 text-decoration: none;
 padding: 8px 16px;
 border: 1px solid #00ff00;
 border-radius: 4px;
 transition: all 0.2s ease;
}

.back-button:hover {
 background-color: #00ff00;
 color: #000000;
}

.player-container {
 background-color: #000000;
 padding: 20px;
 border-radius: 8px;
 margin-bottom: 20px;
 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.controls {
 background-color: #2a2a2a;
 padding: 15px;
 border-radius: 8px;
 color: #ccc;
 text-align: center;
}

.no-recordings {
 text-align: center;
 padding: 40px;
 background-color: #2a2a2a;
 border-radius: 8px;
 color: #888;
}

code {
 background-color: #404040;
 padding: 2px 6px;
 border-radius: 3px;
 color: #00ff00;
 font-family: 'Courier New', monospace;
}
"""
 
 self.send_response(200)
 self.send_header('Content-type', 'text/css')
 self.end_headers()
 self.wfile.write(css.encode('utf-8'))

class AsciinemaManager:
 """Manages asciinema terminal recordings"""
 
 def __init__(self, recordings_dir: str = "recordings", web_port: int = 8888):
 self.logger = get_logger()
 self.recordings_dir = Path(recordings_dir)
 self.recordings_dir.mkdir(exist_ok=True)
 self.web_port = web_port
 self.current_recording = None
 self.web_server = None
 self.web_thread = None
 self.recording_process = None
 
 self.logger.info(f"Asciinema manager initialized - recordings dir: {self.recordings_dir}")
 
 @handle_errors(context="AsciinemaManager.check_installation")
 def check_installation(self) -> bool:
 """Check if asciinema is installed"""
 try:
 result = subprocess.run(['asciinema', '--version'], 
 capture_output=True, text=True, timeout=5)
 if result.returncode == 0:
 self.logger.info(f"Asciinema version: {result.stdout.strip()}")
 return True
 else:
 return False
 except FileNotFoundError:
 return False
 except subprocess.TimeoutExpired:
 return False
 
 @handle_errors(context="AsciinemaManager.install_asciinema")
 def install_asciinema(self) -> bool:
 """Install asciinema using pip"""
 try:
 print(f"{Colors.CYAN}[*] Installing asciinema...{Colors.RESET}")
 result = subprocess.run(['pip', 'install', 'asciinema'], 
 capture_output=True, text=True, timeout=60)
 
 if result.returncode == 0:
 print(f"{Colors.GREEN}[+] Asciinema installed successfully{Colors.RESET}")
 return True
 else:
 print(f"{Colors.RED}[!] Failed to install asciinema: {result.stderr}{Colors.RESET}")
 return False
 except subprocess.TimeoutExpired:
 print(f"{Colors.RED}[!] Installation timeout{Colors.RESET}")
 return False
 
 @handle_errors(context="AsciinemaManager.start_recording")
 def start_recording(self, title: Optional[str] = None) -> bool:
 """
 Start a new terminal recording
 
 Args:
 title: Optional title for the recording
 
 Returns:
 True if recording started successfully
 """
 if self.current_recording:
 print(f"{Colors.YELLOW}[!] Recording already in progress{Colors.RESET}")
 return False
 
 if not self.check_installation():
 print(f"{Colors.RED}[!] Asciinema not installed{Colors.RESET}")
 install = input(f"{Colors.YELLOW}Install asciinema now? (y/N): {Colors.RESET}")
 if install.lower() == 'y':
 if not self.install_asciinema():
 return False
 else:
 return False
 
 # Generate recording filename
 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
 if title:
 safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
 safe_title = safe_title.replace(' ', '_')
 filename = f"{timestamp}_{safe_title}.cast"
 else:
 filename = f"chromsploit_{timestamp}.cast"
 
 recording_path = self.recordings_dir / filename
 
 try:
 # Start asciinema recording
 cmd = ['asciinema', 'rec', str(recording_path)]
 if title:
 cmd.extend(['--title', title])
 
 print(f"{Colors.GREEN}[+] Starting terminal recording...{Colors.RESET}")
 print(f"{Colors.CYAN}[*] Recording file: {recording_path.name}{Colors.RESET}")
 print(f"{Colors.YELLOW}[*] Type 'exit' or Ctrl+D to stop recording{Colors.RESET}")
 
 # Start recording process
 self.recording_process = subprocess.Popen(cmd)
 self.current_recording = {
 'filename': filename,
 'path': recording_path,
 'title': title,
 'started_at': datetime.now(),
 'process': self.recording_process
 }
 
 self.logger.info(f"Started recording: {filename}")
 return True
 
 except Exception as e:
 print(f"{Colors.RED}[!] Failed to start recording: {str(e)}{Colors.RESET}")
 return False
 
 @handle_errors(context="AsciinemaManager.stop_recording")
 def stop_recording(self) -> Optional[str]:
 """
 Stop current recording
 
 Returns:
 Path to the recording file if successful
 """
 if not self.current_recording:
 print(f"{Colors.YELLOW}[!] No recording in progress{Colors.RESET}")
 return None
 
 try:
 # Wait for recording process to finish
 if self.recording_process and self.recording_process.poll() is None:
 print(f"{Colors.CYAN}[*] Waiting for recording to finish...{Colors.RESET}")
 self.recording_process.wait(timeout=10)
 
 recording_path = self.current_recording['path']
 
 if recording_path.exists():
 duration = datetime.now() - self.current_recording['started_at']
 print(f"{Colors.GREEN}[+] Recording saved: {recording_path.name}{Colors.RESET}")
 print(f"{Colors.CYAN}[*] Duration: {duration.total_seconds():.1f} seconds{Colors.RESET}")
 
 # Start web server if not already running
 if not self.web_server:
 self.start_web_server()
 
 print(f"{Colors.BRIGHT_CYAN}[*] View recording at: http://localhost:{self.web_port}/play/{recording_path.stem}{Colors.RESET}")
 
 self.logger.info(f"Recording completed: {recording_path.name}")
 
 result = str(recording_path)
 self.current_recording = None
 self.recording_process = None
 return result
 else:
 print(f"{Colors.RED}[!] Recording file not found{Colors.RESET}")
 return None
 
 except subprocess.TimeoutExpired:
 print(f"{Colors.RED}[!] Recording process timeout{Colors.RESET}")
 return None
 except Exception as e:
 print(f"{Colors.RED}[!] Error stopping recording: {str(e)}{Colors.RESET}")
 return None
 finally:
 self.current_recording = None
 self.recording_process = None
 
 @handle_errors(context="AsciinemaManager.start_web_server")
 def start_web_server(self) -> bool:
 """Start web server for playback"""
 if self.web_server:
 return True
 
 try:
 # Create custom handler with recordings directory
 def handler_factory(*args, **kwargs):
 return AsciinemaWebHandler(*args, recordings_dir=str(self.recordings_dir), **kwargs)
 
 self.web_server = HTTPServer(('localhost', self.web_port), handler_factory)
 
 def serve():
 self.web_server.serve_forever()
 
 self.web_thread = threading.Thread(target=serve, daemon=True)
 self.web_thread.start()
 
 print(f"{Colors.GREEN}[+] Web server started at http://localhost:{self.web_port}{Colors.RESET}")
 self.logger.info(f"Web server started on port {self.web_port}")
 return True
 
 except Exception as e:
 print(f"{Colors.RED}[!] Failed to start web server: {str(e)}{Colors.RESET}")
 return False
 
 def stop_web_server(self):
 """Stop web server"""
 if self.web_server:
 self.web_server.shutdown()
 self.web_server = None
 print(f"{Colors.CYAN}[*] Web server stopped{Colors.RESET}")
 
 def list_recordings(self) -> List[Dict[str, Any]]:
 """List all available recordings"""
 recordings = []
 
 for file in self.recordings_dir.glob("*.cast"):
 stat = file.stat()
 recordings.append({
 'filename': file.name,
 'stem': file.stem,
 'size': stat.st_size,
 'created': datetime.fromtimestamp(stat.st_ctime),
 'modified': datetime.fromtimestamp(stat.st_mtime)
 })
 
 # Sort by creation time (newest first)
 recordings.sort(key=lambda x: x['created'], reverse=True)
 return recordings
 
 def get_status(self) -> Dict[str, Any]:
 """Get current status"""
 return {
 'recording_active': self.current_recording is not None,
 'current_recording': self.current_recording['filename'] if self.current_recording else None,
 'web_server_running': self.web_server is not None,
 'web_port': self.web_port,
 'recordings_count': len(list(self.recordings_dir.glob("*.cast"))),
 'recordings_dir': str(self.recordings_dir),
 'asciinema_installed': self.check_installation()
 }

# Global instance
_asciinema_manager = None

def get_asciinema_manager() -> AsciinemaManager:
 """Get or create asciinema manager instance"""
 global _asciinema_manager
 if _asciinema_manager is None:
 _asciinema_manager = AsciinemaManager()
 return _asciinema_manager

# Command shortcuts
def start_recording(title: Optional[str] = None) -> bool:
 """Start terminal recording"""
 manager = get_asciinema_manager()
 return manager.start_recording(title)

def stop_recording() -> Optional[str]:
 """Stop terminal recording"""
 manager = get_asciinema_manager()
 return manager.stop_recording()

# Example usage
if __name__ == "__main__":
 manager = AsciinemaManager()
 
 print("Asciinema Manager Test")
 print(f"Status: {manager.get_status()}")
 
 if manager.check_installation():
 print("Asciinema is installed")
 else:
 print("Asciinema not found")