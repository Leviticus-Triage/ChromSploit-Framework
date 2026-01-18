#!/usr/bin/env python3
"""
ChromSploit Framework Asciinema Concatenation Tool
Combines multiple .cast files into a single comprehensive demo
"""

import json
import os
import glob
from typing import List, Dict, Any

def load_cast_file(filename: str) -> Dict[str, Any]:
 """Load and parse asciinema .cast file"""
 with open(filename, 'r') as f:
 lines = f.readlines()
 
 # First line is header, rest are events
 header = json.loads(lines[0])
 events = [json.loads(line) for line in lines[1:]]
 
 return {
 'header': header,
 'events': events,
 'filename': filename
 }

def create_transition_event(timestamp: float, text: str) -> List[Any]:
 """Create transition text between recordings"""
 transition_text = f"\n\n{'='*60}\n{text}\n{'='*60}\n\n"
 return [timestamp, "o", transition_text]

def concatenate_recordings(cast_files: List[str], output_file: str):
 """Concatenate multiple .cast files into one"""
 
 all_recordings = []
 for cast_file in sorted(cast_files):
 recording = load_cast_file(cast_file)
 all_recordings.append(recording)
 print(f" Loaded: {os.path.basename(cast_file)} ({len(recording['events'])} events)")
 
 if not all_recordings:
 print(" No recordings found!")
 return
 
 # Use first recording's header as base
 final_header = all_recordings[0]['header'].copy()
 final_header['title'] = "ChromSploit Framework - Complete Demo"
 final_header['env']['TERM'] = 'xterm-256color'
 
 # Concatenate all events with transitions
 final_events = []
 current_time = 0.0
 
 for i, recording in enumerate(all_recordings):
 # Add transition text (except for first recording)
 if i > 0:
 transition_titles = [
 " ChromSploit Framework Startup",
 " CVE Exploit Modules", 
 " Advanced Features",
 " CVE-2025-2783 Mojo IPC Exploit",
 " CVE-2025-30397 WebAssembly JIT",
 " CVE-2025-24813 Tomcat RCE", 
 " CVE-2024-32002 Git RCE",
 " Framework Overview"
 ]
 
 title = transition_titles[i] if i < len(transition_titles) else f"Demo Part {i+1}"
 transition_event = create_transition_event(current_time + 1.0, f"Next: {title}")
 final_events.append(transition_event)
 current_time += 3.0
 
 # Add events from this recording, adjusting timestamps
 for event in recording['events']:
 adjusted_event = [event[0] + current_time, event[1], event[2]]
 final_events.append(adjusted_event)
 
 # Update current time to end of this recording
 if recording['events']:
 current_time = final_events[-1][0] + 2.0 # Add 2 second pause
 
 # Calculate total duration
 total_duration = final_events[-1][0] if final_events else 0
 final_header['duration'] = total_duration
 final_header['command'] = 'ChromSploit Framework Demo'
 
 print(f"\n Concatenation Summary:")
 print(f" - Total recordings: {len(all_recordings)}")
 print(f" - Total events: {len(final_events)}")
 print(f" - Total duration: {total_duration:.2f} seconds")
 
 # Write concatenated file
 with open(output_file, 'w') as f:
 # Write header
 f.write(json.dumps(final_header) + '\n')
 
 # Write all events
 for event in final_events:
 f.write(json.dumps(event) + '\n')
 
 print(f" Combined recording saved to: {output_file}")

def create_playlist_file():
 """Create a playlist file with all recordings"""
 cast_files = glob.glob('*.cast')
 cast_files.sort()
 
 playlist = {
 "title": "ChromSploit Framework Demo Playlist",
 "description": "Complete demonstration of ChromSploit Framework capabilities",
 "recordings": []
 }
 
 titles = [
 "Framework Startup & Introduction",
 "CVE Exploit Modules Overview", 
 "Advanced Framework Features",
 "CVE-2025-2783: Chrome Mojo IPC Exploit",
 "CVE-2025-30397: WebAssembly JIT Type Confusion",
 "CVE-2025-24813: Apache Tomcat RCE",
 "CVE-2024-32002: Git Remote Code Execution",
 "Framework Features Summary"
 ]
 
 descriptions = [
 "Introduction to ChromSploit Framework and basic startup process",
 "Overview of available CVE exploit modules and capabilities",
 "Advanced features including AI integration, monitoring, and obfuscation",
 "Demonstration of Chrome Mojo IPC sandbox escape exploitation",
 "WebAssembly JIT type confusion exploit with multi-stage execution",
 "Apache Tomcat RCE via malicious WAR file deployment",
 "Git RCE exploitation using symbolic links and malicious repositories",
 "Complete overview of framework capabilities and educational focus"
 ]
 
 for i, cast_file in enumerate(cast_files):
 if os.path.exists(cast_file):
 recording_info = {
 "file": cast_file,
 "title": titles[i] if i < len(titles) else f"Demo Part {i+1}",
 "description": descriptions[i] if i < len(descriptions) else f"ChromSploit demonstration part {i+1}",
 "duration": "auto",
 "order": i + 1
 }
 playlist["recordings"].append(recording_info)
 
 with open('playlist.json', 'w') as f:
 json.dump(playlist, f, indent=2)
 
 print(f" Playlist created with {len(playlist['recordings'])} recordings")

def main():
 """Main function"""
 print(" ChromSploit Framework Asciinema Concatenation Tool")
 print("=" * 55)
 
 # Change to asciinema directory
 os.chdir('/home/danii/github-projects/ChromSploit-Framework/asciinema')
 
 # Find all .cast files
 cast_files = glob.glob('*.cast')
 
 if not cast_files:
 print(" No .cast files found in current directory!")
 return
 
 print(f" Found {len(cast_files)} .cast files:")
 for cast_file in sorted(cast_files):
 print(f" - {cast_file}")
 
 # Create concatenated version
 print("\n Creating concatenated demo...")
 concatenate_recordings(cast_files, 'chromsploit_complete_demo.cast')
 
 # Create playlist
 print("\n Creating playlist...")
 create_playlist_file()
 
 print("\n All files created successfully!")
 print("\n Available files:")
 print(" - chromsploit_complete_demo.cast (combined demo)")
 print(" - playlist.json (playlist metadata)")
 print(" - Individual .cast files for separate viewing")

if __name__ == '__main__':
 main()