# 📚 API Reference

## Core Framework APIs

### Module Loader API

The Module Loader provides dynamic loading of framework components with dependency resolution and fallback handling.

#### `ModuleLoader`

Central class for dynamic module loading with dependency management.

```python
from core.module_loader import get_module_loader

loader = get_module_loader()  # Singleton instance
```

**Methods:**

##### `load_module(module_name: str, force: bool = False) -> Optional[Any]`

Loads a module with dependency checking and fallback handling.

```python
# Load a specific module
browser_chain = loader.load_module('browser_exploit_chain')

# Force reload an already loaded module
obfuscation = loader.load_module('obfuscation', force=True)
```

**Parameters:**
- `module_name` (str): Name of the module to load
- `force` (bool): Force reload if module already loaded

**Returns:** Module instance or None if loading fails

##### `check_dependencies(module_name: str) -> Tuple[bool, List[str]]`

Checks if all module dependencies are available.

```python
deps_ok, missing = loader.check_dependencies('browser_exploit_chain')
if not deps_ok:
    print(f"Missing dependencies: {missing}")
```

**Returns:** Tuple of (dependencies_satisfied, missing_dependencies)

##### `get_loaded_modules() -> Dict[str, Any]`

Returns dictionary of currently loaded modules.

```python
loaded = loader.get_loaded_modules()
for name, module in loaded.items():
    print(f"Loaded: {name}")
```

### Exploit Chain API

Manages multi-step exploit execution with dependency resolution and state sharing.

#### `ExploitChain`

```python
from core.exploit_chain import ExploitChain

chain = ExploitChain("MyChain", "Description of exploit chain")
```

**Methods:**

##### `add_step(exploit_id: str, parameters: Dict[str, Any], dependencies: List[str] = None) -> str`

Adds an exploit step to the chain.

```python
step_id = chain.add_step(
    exploit_id="cve_2025_4664",
    parameters={
        "target_url": "http://example.com",
        "simulation_mode": True
    },
    dependencies=[]  # No dependencies for first step
)

# Add dependent step
second_step = chain.add_step(
    exploit_id="cve_2025_2783",
    parameters={
        "target_url": "http://example.com",
        "callback_port": 8080
    },
    dependencies=[step_id]  # Depends on first step
)
```

**Parameters:**
- `exploit_id` (str): CVE identifier or exploit module name
- `parameters` (Dict): Configuration parameters for the exploit
- `dependencies` (List[str]): List of step IDs this step depends on

**Returns:** Unique step identifier

##### `execute(parallel: bool = False, callback: Callable = None) -> Dict[str, Any]`

Executes the exploit chain with optional progress tracking.

```python
def progress_callback(step, status, result):
    print(f"Step {step.id}: {status}")
    if status == 'completed' and result.get('success'):
        print(f"✓ {step.cve_id} successful")

result = chain.execute(
    parallel=False,  # Sequential execution
    callback=progress_callback
)

if result['success']:
    print(f"Chain completed: {len(result['executed_steps'])} steps")
else:
    print(f"Chain failed: {result['error']}")
```

**Parameters:**
- `parallel` (bool): Execute independent steps in parallel
- `callback` (Callable): Progress callback function

**Returns:** Chain execution result with metadata

## Browser Multi-Exploit Chain APIs

### BrowserExploitChain

Basic browser exploit chain functionality.

```python
from modules.browser_exploit_chain import BrowserExploitChain

browser_chain = BrowserExploitChain()
```

**Methods:**

##### `execute_template(template_name: str, target_config: Dict[str, Any]) -> Dict[str, Any]`

Executes a predefined exploit chain template.

```python
target_config = {
    'target_url': 'http://target.example.com',
    'simulation_mode': True,
    'callback_port': 8080
}

result = browser_chain.execute_template('full_browser_compromise', target_config)
```

**Available Templates:**
- `full_browser_compromise`: All 4 browser CVEs in sequence
- `chrome_focused_attack`: Chrome-specific exploits (CVE-2025-4664, CVE-2025-2783)
- `rapid_exploitation`: Fast execution with minimal delays
- `stealth_browser_chain`: Low-detection exploitation

##### `get_available_templates() -> List[str]`

Returns list of available exploit chain templates.

```python
templates = browser_chain.get_available_templates()
for template in templates:
    print(f"Available: {template}")
```

### EnhancedBrowserExploitChain

Advanced browser chain with obfuscation and ngrok integration.

```python
from modules.browser_exploit_chain_enhanced import EnhancedBrowserExploitChain

enhanced_chain = EnhancedBrowserExploitChain()
```

**Methods:**

##### `execute_enhanced_template(template_name: str, target_config: Dict[str, Any], obfuscation_level: str = 'STANDARD') -> Dict[str, Any]`

Executes enhanced chain with automatic obfuscation and tunneling.

```python
result = enhanced_chain.execute_enhanced_template(
    'full_browser_compromise',
    target_config,
    obfuscation_level='ADVANCED'
)

# Check obfuscation statistics
if 'obfuscation_stats' in result:
    stats = result['obfuscation_stats']
    print(f"Obfuscated {stats['payloads_processed']} payloads")
```

**Obfuscation Levels:**
- `BASIC`: Simple string encoding
- `STANDARD`: Control flow obfuscation + encoding
- `ADVANCED`: Anti-debugging + encryption
- `EXTREME`: Full steganography and evasion

## Exploit Implementation APIs

### CVE Exploit Interface

All CVE exploits follow a standardized interface for consistency.

#### Base Exploit Pattern

```python
from exploits.cve_2025_4664 import CVE2025_4664_Exploit

# Class-based interface (recommended)
exploit = CVE2025_4664_Exploit()
exploit.set_parameter('target_url', 'http://example.com')
exploit.set_parameter('simulation_mode', True)

result = exploit.execute()
```

#### Legacy Function Interface

```python
from exploits.cve_2025_4664 import execute_exploit

# Function-based interface (legacy compatibility)
parameters = {
    'target_url': 'http://example.com',
    'simulation_mode': True,
    'timeout': 30
}

result = execute_exploit(parameters)
```

### Standard Exploit Methods

All exploit classes implement these methods:

##### `set_parameter(name: str, value: Any) -> None`

Configure exploit parameters.

```python
exploit.set_parameter('target_url', 'http://target.com')
exploit.set_parameter('timeout', 60)
exploit.set_parameter('obfuscation_enabled', True)
```

##### `execute(target_url: Optional[str] = None) -> Dict[str, Any]`

Execute the exploit with current configuration.

```python
result = exploit.execute('http://optional-target.com')

# Standard result format
{
    'success': bool,           # Exploitation success
    'cve_id': str,            # CVE identifier
    'target': str,            # Target URL
    'artifacts': dict,        # Collected artifacts
    'metadata': dict,         # Execution metadata
    'message': str,           # Human-readable result
    'execution_time': float   # Time taken in seconds
}
```

##### `validate_target(target_url: str) -> bool`

Check if target is accessible and potentially vulnerable.

```python
if exploit.validate_target('http://example.com'):
    result = exploit.execute()
else:
    print("Target not accessible or not vulnerable")
```

## Obfuscation APIs

### PayloadObfuscator

Multi-level payload obfuscation for various exploit types.

```python
from modules.obfuscation.payload_obfuscator import PayloadObfuscator

obfuscator = PayloadObfuscator()
```

**Methods:**

##### `obfuscate_javascript(code: str, level: str = 'STANDARD') -> str`

Obfuscate JavaScript payloads.

```python
original_js = """
function exploit() {
    fetch('/api/data', {
        method: 'POST',
        body: JSON.stringify({cmd: 'whoami'})
    });
}
"""

obfuscated = obfuscator.obfuscate_javascript(original_js, 'ADVANCED')
```

##### `obfuscate_http_payload(payload: Dict[str, Any], level: str = 'STANDARD') -> Dict[str, Any]`

Obfuscate HTTP request payloads.

```python
http_payload = {
    'method': 'POST',
    'headers': {'Content-Type': 'application/json'},
    'data': {'exploit': 'payload_data'}
}

obfuscated_payload = obfuscator.obfuscate_http_payload(http_payload, 'STANDARD')
```

##### `obfuscate_binary_data(data: bytes, level: str = 'STANDARD') -> bytes`

Obfuscate binary payloads and shellcode.

```python
shellcode = b"\x90\x90\x90\x90"  # Example shellcode
obfuscated_shellcode = obfuscator.obfuscate_binary_data(shellcode, 'ADVANCED')
```

## Ngrok Integration APIs

### NgrokManager

Automatic tunnel creation and management for exploit callbacks.

```python
from core.ngrok_manager import get_ngrok_manager

ngrok = get_ngrok_manager()
```

**Methods:**

##### `create_tunnel(tunnel_type: str, local_port: int, options: Dict = None) -> str`

Create an ngrok tunnel for callbacks.

```python
# HTTP tunnel
tunnel_id = ngrok.create_tunnel('http', 8080)
public_url = ngrok.get_public_url(tunnel_id)
print(f"Callback URL: {public_url}")

# TCP tunnel with custom options
tcp_tunnel = ngrok.create_tunnel('tcp', 4444, {
    'region': 'us',
    'bind_tls': True
})
```

**Tunnel Types:**
- `http`: HTTP/HTTPS tunnels
- `tcp`: Raw TCP tunnels
- `tls`: TLS-wrapped TCP tunnels

##### `get_public_url(tunnel_id: str) -> str`

Get the public URL for a tunnel.

```python
public_url = ngrok.get_public_url(tunnel_id)
# Use in exploit payload for callbacks
```

##### `close_tunnel(tunnel_id: str) -> bool`

Close a specific tunnel.

```python
success = ngrok.close_tunnel(tunnel_id)
```

## Logging and Error Handling APIs

### EnhancedLogger

Structured logging with analysis capabilities.

```python
from core.enhanced_logger import get_logger

logger = get_logger()
```

**Methods:**

##### `log(level: str, message: str, context: Dict = None)`

Log structured messages with context.

```python
logger.log('INFO', 'Starting exploit execution', {
    'cve_id': 'CVE-2025-4664',
    'target': 'http://example.com',
    'component': 'exploit_engine'
})

logger.log('ERROR', 'Exploit failed', {
    'error_type': 'NetworkError',
    'retry_count': 3
})
```

**Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

##### `analyze_logs(time_range: Optional[Tuple] = None) -> Dict[str, Any]`

Analyze log patterns and generate insights.

```python
analysis = logger.analyze_logs()
print(f"Error patterns: {analysis['error_patterns']}")
print(f"Success rate: {analysis['success_rate']}%")
```

### ErrorHandler

Categorized error handling with recovery suggestions.

```python
from core.error_handler import get_error_handler, handle_errors

error_handler = get_error_handler()

# Decorator usage
@handle_errors
def risky_operation():
    # Code that might fail
    pass

# Context manager usage
with error_handler.error_context('Operation name'):
    # Code with automatic error handling
    pass
```

## Configuration APIs

### Configuration Management

```python
from core.config import get_config_manager

config = get_config_manager()
```

**Methods:**

##### `get(key: str, default: Any = None) -> Any`

Get configuration value with dot notation.

```python
debug_mode = config.get('general.debug_mode', False)
default_port = config.get('network.default_port', 8080)
```

##### `set(key: str, value: Any) -> None`

Set configuration value.

```python
config.set('exploits.simulation_mode', True)
config.set('browser_chain.obfuscation_enabled', True)
```

##### `load_user_config(path: str) -> bool`

Load user-specific configuration.

```python
success = config.load_user_config('config/user_config.json')
```

## Validation Framework APIs

### ValidationFramework

Automated testing and validation system.

```python
from core.validation_framework import ValidationFramework

validator = ValidationFramework()
```

**Methods:**

##### `run_all_tests() -> Dict[str, List[TestResult]]`

Execute complete test suite.

```python
results = validator.run_all_tests()
for suite_name, test_results in results.items():
    passed = sum(1 for r in test_results if r.passed)
    total = len(test_results)
    print(f"{suite_name}: {passed}/{total} tests passed")
```

##### `run_exploit_tests(cve_id: str = None) -> List[TestResult]`

Test specific exploits or all exploits.

```python
# Test specific CVE
results = validator.run_exploit_tests('CVE-2025-4664')

# Test all exploits
all_results = validator.run_exploit_tests()
```

##### `benchmark_performance() -> Dict[str, float]`

Run performance benchmarks.

```python
benchmarks = validator.benchmark_performance()
print(f"Framework startup: {benchmarks['startup_time']:.2f}s")
print(f"Module loading: {benchmarks['module_load_time']:.2f}s")
```

## Data Structures

### Common Return Formats

#### Exploit Result

```python
{
    'success': bool,              # True if exploit succeeded
    'cve_id': str,               # CVE identifier
    'target': str,               # Target URL or IP
    'message': str,              # Human-readable result
    'artifacts': {               # Collected data/files
        'cookies': dict,
        'responses': list,
        'files': list
    },
    'metadata': {                # Execution metadata
        'timestamp': str,        # ISO format timestamp
        'execution_time': float, # Seconds taken
        'simulation': bool,      # Was this simulated?
        'obfuscation_applied': bool
    },
    'error': str                 # Error message if success=False
}
```

#### Chain Result

```python
{
    'success': bool,
    'chain_id': str,
    'executed_steps': list,      # List of completed steps
    'failed_steps': list,        # List of failed steps
    'total_time': float,
    'artifacts': dict,           # Combined artifacts
    'chain_statistics': {
        'total_steps': int,
        'successful_steps': int,
        'failed_steps': int,
        'parallel_execution': bool
    }
}
```

#### Module Info

```python
{
    'name': str,
    'version': str,
    'description': str,
    'dependencies': list,        # Required dependencies
    'optional_dependencies': list,
    'loaded': bool,
    'fallback_available': bool
}
```

## Example Integration Workflows

### Complete Exploit Chain Execution

```python
from core.module_loader import get_module_loader
from modules.browser_exploit_chain_enhanced import EnhancedBrowserExploitChain
from core.enhanced_logger import get_logger

# Initialize components
loader = get_module_loader()
logger = get_logger()
browser_chain = EnhancedBrowserExploitChain()

# Configure target
target_config = {
    'target_url': 'http://target.example.com',
    'simulation_mode': True,
    'callback_port': 8080,
    'ngrok_enabled': True,
    'obfuscation_enabled': True
}

# Execute enhanced browser chain
logger.log('INFO', 'Starting browser exploit chain', {'target': target_config['target_url']})

result = browser_chain.execute_enhanced_template(
    'full_browser_compromise',
    target_config,
    obfuscation_level='ADVANCED'
)

# Process results
if result['success']:
    logger.log('INFO', f"Chain completed successfully: {len(result['executed_steps'])} steps")
    
    # Extract artifacts
    for step in result['executed_steps']:
        if step['artifacts']:
            logger.log('INFO', f"Artifacts from {step['cve_id']}: {list(step['artifacts'].keys())}")
else:
    logger.log('ERROR', f"Chain failed: {result['error']}")
```

### Custom Module Development

```python
# modules/custom_recon/__init__.py
from typing import Dict, Any

class CustomReconModule:
    def __init__(self):
        self.name = "CustomRecon"
        self.version = "1.0.0"
    
    def scan_target(self, target: str) -> Dict[str, Any]:
        # Custom reconnaissance logic
        return {
            'success': True,
            'target': target,
            'findings': {'ports': [80, 443], 'services': ['http', 'https']}
        }

def register():
    return {
        'name': 'CustomRecon',
        'version': '1.0.0',
        'class': CustomReconModule,
        'dependencies': ['requests', 'socket']
    }

# Usage
from core.module_loader import get_module_loader

loader = get_module_loader()
recon_module = loader.load_module('custom_recon')
result = recon_module.scan_target('http://example.com')
```

---

**Next**: [Usage Examples](EXAMPLES.md) | [Security Guidelines](SECURITY.md)