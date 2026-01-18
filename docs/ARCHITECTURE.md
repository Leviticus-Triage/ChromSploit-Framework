#  Architecture Guide

## System Architecture Overview

ChromSploit Framework follows a modular, layered architecture with clear separation between UI, business logic, and exploit implementations. This design ensures maintainability, extensibility, and security.

```
┌─────────────────────────────────────────────┐
│ UI Layer │
│ (Menus, User Interaction, Display) │
├─────────────────────────────────────────────┤
│ Module Layer │
│ (Browser Chains, Obfuscation, Monitoring) │
├─────────────────────────────────────────────┤
│ Core Layer │
│ (Module Loader, Validation, Chains) │
├─────────────────────────────────────────────┤
│ Exploit Layer │
│ (CVE Implementations, Payloads) │
├─────────────────────────────────────────────┤
│ Infrastructure Layer │
│ (Logging, Error Handling, Config) │
└─────────────────────────────────────────────┘
```

## Core Components

### 1. UI Layer (`ui/`)

**Responsibilities:**
- User interaction and navigation
- Menu systems and workflows
- Results display and formatting
- Interactive tutorials and help

**Key Components:**
```python
ui/
├── main_menu.py # Primary entry point
├── browser_chain_menu.py # Multi-exploit chain management
├── exploit_menu.py # Individual exploit selection
├── reporting_menu.py # Report generation
└── enhanced_menu.py # Base menu functionality
```

**Design Patterns:**
- Menu-based navigation with breadcrumbs
- Enhanced menu inheritance (`EnhancedMenu`)
- Color-coded output with proper formatting
- Multi-language support (German UI, English logs)

### 2. Module Layer (`modules/`)

**Browser Multi-Exploit Chain** (`modules/browser_exploit_chain.py`):
```python
class BrowserExploitChain:
 """Combines multiple browser exploits automatically"""
 
 def __init__(self):
 self.exploits = []
 self.templates = {
 'full_browser_compromise': self._full_browser_template,
 'chrome_focused_attack': self._chrome_focused_template,
 'rapid_exploitation': self._rapid_template,
 'stealth_browser_chain': self._stealth_template
 }
 
 def execute_template(self, template_name, target_config):
 # Execute predefined exploit combinations
```

**Enhanced Browser Chain** (`modules/browser_exploit_chain_enhanced.py`):
```python
class EnhancedBrowserExploitChain:
 """Advanced chain with obfuscation and ngrok integration"""
 
 def __init__(self):
 self.obfuscator = PayloadObfuscator()
 self.ngrok_manager = NgrokManager()
 self.chain_statistics = ChainStatistics()
```

**Obfuscation System** (`modules/obfuscation/`):
```python
class PayloadObfuscator:
 """Multi-level payload obfuscation"""
 
 OBFUSCATION_LEVELS = {
 'BASIC': 1, # Simple string encoding
 'STANDARD': 2, # Control flow + encoding
 'ADVANCED': 3, # Anti-debugging + encryption
 'EXTREME': 4 # Full steganography
 }
 
 def obfuscate_javascript(self, code, level):
 # JavaScript-specific obfuscation
 
 def obfuscate_binary_data(self, data, level):
 # Binary payload obfuscation
```

### 3. Core Layer (`core/`)

**Module Loader** (`core/module_loader.py`):
- Dynamic module loading with dependency resolution
- Graceful fallback handling for missing dependencies
- Singleton pattern for global access

```python
class ModuleLoader:
 def __init__(self):
 self.loaded_modules = {}
 self.dependency_graph = {}
 
 def load_module(self, module_name, force=False):
 # 1. Check dependencies
 # 2. Attempt module import
 # 3. Handle fallbacks if needed
 # 4. Register in module registry
```

**Exploit Chain Engine** (`core/exploit_chain.py`):
- Sequential and parallel exploit execution
- Dependency resolution between exploits
- State sharing and progress tracking

```python
class ExploitChain:
 def __init__(self):
 self.steps = []
 self.global_state = {}
 self.callbacks = {}
 
 def add_step(self, exploit_id, parameters, dependencies=None):
 # Add exploit step with optional dependencies
 
 def execute(self, parallel=False):
 # Execute chain with progress callbacks
```

**Validation Framework** (`core/validation_framework.py`):
- Comprehensive testing suite
- Automated module validation
- Performance benchmarking

```python
class ValidationFramework:
 def __init__(self):
 self.test_suites = {
 'core': CoreTestSuite(),
 'exploits': ExploitTestSuite(),
 'modules': ModuleTestSuite(),
 'integration': IntegrationTestSuite()
 }
```

**Ngrok Manager** (`core/ngrok_manager.py`):
- Automatic tunnel creation and management
- Multi-protocol support (HTTP, TCP, WebSocket)
- Integration with exploit chains

```python
class NgrokManager:
 def create_tunnel(self, tunnel_type, local_port, options=None):
 # Create and manage ngrok tunnels
 
 def get_public_url(self, tunnel_id):
 # Retrieve public URL for callbacks
```

### 4. Exploit Layer (`exploits/`)

**CVE Implementations:**

All exploits follow a standardized interface:

```python
class CVE20XX_XXXXX_Exploit:
 def __init__(self):
 self.cve_id = "CVE-20XX-XXXXX"
 self.description = "Vulnerability description"
 self.requirements = []
 self.config = {}
 
 def set_parameter(self, name, value):
 self.config[name] = value
 
 def execute(self, target_url=None):
 return {
 'success': bool,
 'cve_id': str,
 'artifacts': dict,
 'metadata': dict
 }

# Legacy compatibility function
def execute_exploit(parameters: Dict[str, Any]) -> Dict[str, Any]:
 exploit = CVE20XX_XXXXX_Exploit()
 # Configure and execute
```

**Implemented Exploits:**
- **CVE-2025-4664**: Chrome Data Leak via Link Header Referrer Policy
- **CVE-2025-2783**: Chrome Mojo IPC Sandbox Escape
- **CVE-2025-30397**: Edge WebAssembly JIT Type Confusion
- **CVE-2025-24813**: Apache Tomcat RCE via WAR Deployment
- **CVE-2024-32002**: Git RCE via Symbolic Links

### 5. Infrastructure Layer

**Enhanced Logger** (`core/enhanced_logger.py`):
```python
class EnhancedLogger:
 def __init__(self):
 self.log_analyzers = []
 self.structured_data = {}
 
 def log(self, level, message, context=None):
 # Structured logging with analysis
 
 def analyze_logs(self):
 # AI-powered log analysis
```

**Error Handler** (`core/error_handler.py`):
```python
class ErrorHandler:
 ERROR_CATEGORIES = {
 'NETWORK': NetworkErrorCategory(),
 'DEPENDENCY': DependencyErrorCategory(),
 'EXPLOIT': ExploitErrorCategory(),
 'SYSTEM': SystemErrorCategory()
 }
 
 def handle_error(self, error, context):
 # Categorize and provide recovery suggestions
```

## Data Flow Patterns

### Exploit Execution Flow

```
User Input → UI Menu → Parameter Collection
 ↓
 Module Loader → Load Exploit Module
 ↓
 Validation → Check Requirements & Dependencies
 ↓
 Obfuscation → Apply Payload Obfuscation (if enabled)
 ↓
 Ngrok Setup → Create Tunnels (if needed)
 ↓
 Execution → Monitor Progress & Events
 ↓
 Collection → Gather Results & Artifacts
 ↓
 Reporting → Generate Structured Reports
```

### Browser Multi-Exploit Chain Flow

```
Template Selection → Load Chain Configuration
 ↓
Exploit Discovery → Scan Available CVE Modules
 ↓
Dependency Check → Resolve Inter-exploit Dependencies
 ↓
Obfuscation Prep → Apply Per-exploit Obfuscation
 ↓
Tunnel Creation → Setup Ngrok for Callbacks
 ↓
Chain Execution → Sequential/Parallel Execution
 ↓
State Sharing → Pass Results Between Exploits
 ↓
Final Report → Aggregate All Results
```

### Event-Driven Communication

```python
# Publisher Pattern
monitor.log_event(EventType.EXPLOIT_START, {
 'cve_id': 'CVE-2025-2783',
 'target': target_url,
 'timestamp': datetime.now()
}, EventPriority.HIGH)

# Subscriber Pattern
monitor.register_handler(EventType.EXPLOIT_START, handle_exploit_start)
monitor.register_handler(EventType.EXPLOIT_COMPLETE, handle_exploit_complete)
```

## Security Architecture

### Simulation Engine

The framework includes comprehensive simulation capabilities:

```python
class SimulationEngine:
 SIMULATION_MODES = {
 'safe': 'No real exploitation, safe demonstrations',
 'demo': 'Educational mode with explanations',
 'fast': 'Quick simulation without delays'
 }
 
 def simulate_exploit(self, exploit, target):
 # Generate realistic results without actual exploitation
 # Educational content generation
 # Security boundary enforcement
```

### Safety Mechanisms

1. **Parameter Validation**: All inputs validated before processing
2. **Simulation Checks**: Exploits check for simulation mode
3. **Error Boundaries**: Comprehensive error handling prevents crashes
4. **Audit Logging**: All actions logged for security auditing
5. **Permission Checks**: Administrative operations require confirmation

## Performance Optimizations

### Lazy Loading Strategy

```python
class LazyModule:
 def __init__(self, module_name):
 self._module_name = module_name
 self._module = None
 
 def __getattr__(self, name):
 if self._module is None:
 self._module = importlib.import_module(self._module_name)
 return getattr(self._module, name)
```

### Asynchronous Operations

```python
import threading
from concurrent.futures import ThreadPoolExecutor

class AsyncChainExecutor:
 def __init__(self, max_workers=5):
 self.executor = ThreadPoolExecutor(max_workers=max_workers)
 
 def execute_parallel_steps(self, steps):
 futures = []
 for step in steps:
 future = self.executor.submit(step.execute)
 futures.append(future)
 return [f.result() for f in futures]
```

### Caching Layer

```python
from functools import lru_cache

class ModuleCache:
 @lru_cache(maxsize=128)
 def get_exploit_metadata(self, cve_id):
 # Cache exploit metadata for faster access
 
 @lru_cache(maxsize=64)
 def get_obfuscation_template(self, payload_type, level):
 # Cache obfuscation templates
```

## Extension Architecture

### Plugin System

```python
# Plugin Registration
class PluginRegistry:
 def __init__(self):
 self.plugins = {}
 self.hooks = defaultdict(list)
 
 def register_plugin(self, plugin_class):
 plugin = plugin_class()
 self.plugins[plugin.name] = plugin
 
 # Register hooks
 for hook_name, handler in plugin.get_hooks().items():
 self.hooks[hook_name].append(handler)
```

### Hook System

```python
# Pre/Post exploit hooks
@register_hook('pre_exploit')
def custom_pre_exploit_handler(exploit_data):
 # Custom logic before exploit execution
 
@register_hook('post_exploit')
def custom_post_exploit_handler(exploit_results):
 # Custom logic after exploit completion
```

### Custom Module Development

```python
# modules/custom_module/__init__.py
def register():
 return {
 'name': 'CustomModule',
 'version': '1.0.0',
 'dependencies': ['requests', 'beautifulsoup4'],
 'fallback': custom_fallback_handler,
 'menu_integration': custom_menu_factory
 }

def custom_fallback_handler():
 # Graceful degradation when dependencies missing
 
def custom_menu_factory():
 # Return menu class for UI integration
```

## Monitoring and Observability

### Live Monitoring System

```python
class LiveMonitor:
 def __init__(self):
 self.events = deque(maxlen=1000)
 self.handlers = defaultdict(list)
 self.dashboard = MonitoringDashboard()
 
 def start_monitoring(self):
 # Start background monitoring threads
 
 def display_dashboard(self):
 # Real-time terminal dashboard
```

### Event Categories

- **SYSTEM**: Framework startup, shutdown, errors
- **EXPLOIT**: Exploit start, progress, completion
- **NETWORK**: Connection attempts, traffic analysis
- **OBFUSCATION**: Payload transformations
- **CHAIN**: Multi-exploit chain progress

## Deployment Patterns

### Standalone Deployment

```
ChromSploit Instance
├── Local Configuration (config/*.json)
├── File-based Logging (logs/)
├── Local Report Storage (reports/)
└── Embedded Dependencies
```

### Container Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080 4444
CMD ["python", "chromsploit.py"]
```

### Distributed Architecture (Future)

```
Load Balancer
 │
 ├── ChromSploit Master (API + Web UI)
 │ ├── Task Queue (Redis/RabbitMQ)
 │ ├── Central Database (PostgreSQL)
 │ └── Report Storage (S3/MinIO)
 │
 └── ChromSploit Agents
 ├── Agent 1 (Exploit Execution)
 ├── Agent 2 (Reconnaissance)
 └── Agent N (Specialized Tasks)
```

## Scalability Considerations

### Horizontal Scaling

- **Module Independence**: Modules can be deployed separately
- **Event System**: Supports multiple handlers and publishers
- **Chain Parallelization**: Exploit chains can run concurrently
- **Stateless Design**: Core components maintain minimal state

### Vertical Scaling

- **Resource Isolation**: CPU-intensive operations isolated
- **Memory Management**: Lazy loading and caching
- **I/O Optimization**: Asynchronous network operations
- **Database Optimization**: Indexed queries and connection pooling

## Configuration Management

### Configuration Hierarchy

1. **Default Config** (`config/default_config.json`): Framework defaults
2. **User Config** (`config/user_config.json`): User preferences
3. **Environment Variables**: Runtime overrides
4. **Command Line Arguments**: Session-specific settings

### Configuration Schema

```json
{
 "general": {
 "debug_mode": false,
 "simulation_mode": "safe",
 "max_threads": 10,
 "log_level": "INFO"
 },
 "network": {
 "default_port": 8080,
 "timeout": 30,
 "proxy": null
 },
 "exploits": {
 "auto_cleanup": true,
 "save_artifacts": true,
 "obfuscation_default": "STANDARD"
 },
 "browser_chain": {
 "parallel_execution": false,
 "auto_ngrok": true,
 "obfuscation_enabled": true
 }
}
```

---

**Next**: [Developer Guide](DEVELOPMENT.md) | [API Reference](API_REFERENCE.md)