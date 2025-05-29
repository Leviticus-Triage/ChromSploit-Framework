# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ChromSploit Framework Overview

ChromSploit Framework is an educational security research tool with a modular architecture for studying browser vulnerabilities. The codebase emphasizes safety through simulation modes and professional reporting for bug bounty/pentesting work.

## Key Commands

### Running the Framework
```bash
# Standard launch
python chromsploit.py

# With simulation mode (no actual exploitation)
python chromsploit.py --simulation safe    # Safe mode (default)
python chromsploit.py --simulation demo    # Demo mode with explanations
python chromsploit.py --simulation fast    # Fast mode (minimal delays)

# Other options
python chromsploit.py --debug              # Enable debug output
python chromsploit.py --log-level DEBUG    # Set logging level
python chromsploit.py --check              # Check environment only
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_enhanced_menu.py -v

# Run with coverage
python -m pytest --cov=core --cov=ui --cov=modules --cov-report=html

# Run validation framework
python -m core.validation_framework
```

### Development Tools
```bash
# Code formatting
black . --line-length 120

# Linting
flake8 . --max-line-length 120

# Type checking
mypy chromsploit.py --ignore-missing-imports

# Create new exploit module
cp exploits/template_exploit.py exploits/cve_YYYY_XXXXX.py
```

## Architecture

### Core System Flow
```
chromsploit.py (Entry)
    ├── Environment Check (dependencies, permissions)
    ├── Configuration Loading (config/*.json)
    ├── Module Loader (core/module_loader.py)
    ├── Enhanced Logger Initialization
    └── Main Menu (ui/main_menu.py)
        ├── CVE Exploits
        ├── Browser Multi-Exploit Chain ← NEW
        ├── Reconnaissance
        ├── Reporting
        └── Settings
```

### Critical Architectural Patterns

1. **Module Loading System** (`core/module_loader.py`):
   - Scans `/modules` directory for dynamic loading
   - Handles missing dependencies gracefully
   - Maintains singleton registry of loaded modules
   - Use `get_module_loader().load_module(name)` to load modules

2. **Exploit Chain System** (`core/exploit_chain.py`):
   - Manages sequential/parallel exploit execution
   - Dependency resolution between exploits
   - State sharing between chain steps
   - Progress tracking and callbacks

3. **Browser Multi-Exploit Chain** (`modules/browser_exploit_chain.py`):
   - Combines 4 browser CVEs automatically
   - Integrates obfuscation and ngrok
   - Templates: `full_browser_compromise`, `chrome_focused_attack`, `rapid_exploitation`
   - Enhanced version in `browser_exploit_chain_enhanced.py` with full obfuscation

4. **Obfuscation System** (`modules/obfuscation/`):
   - `PayloadObfuscator` for exploit-specific obfuscation
   - Supports JavaScript, HTML, WASM, binary data
   - Levels: BASIC, STANDARD, ADVANCED, EXTREME
   - Control flow, string encryption, anti-debugging

5. **Ngrok Integration** (`core/ngrok_manager.py`):
   - Automatic tunnel creation for callbacks
   - Multiple tunnel types (TCP, HTTP, HTTPS)
   - Region selection and TLS binding
   - Used by Browser Chain for auto-tunneling

### Exploit Implementation Pattern

All exploits follow this structure:
```python
class CVE20XX_XXXXX_Exploit:
    def __init__(self):
        self.config = {...}
    
    def set_parameter(self, name, value):
        # Parameter configuration
    
    def execute(self, target_url=None):
        # Main execution logic
        return {
            'success': bool,
            'cve_id': str,
            'artifacts': dict,
            'metadata': dict
        }

# Legacy function interface (required)
def execute_exploit(parameters: Dict[str, Any]) -> Dict[str, Any]:
    exploit = CVE20XX_XXXXX_Exploit()
    # Configure and execute
```

### Enhanced Components

The framework uses enhanced versions throughout:
- `EnhancedLogger` → Structured logging with analysis
- `EnhancedMenu` → Advanced UI with shortcuts and breadcrumbs  
- `ErrorHandler` → Categorized errors with recovery suggestions
- `SimulationEngine` → Safe testing without real exploitation
- `ReportGenerator` → Professional PDF/HTML/JSON reports

### Global Instance Access

Always use getter functions for singletons:
```python
from core.enhanced_logger import get_logger
from core.error_handler import get_error_handler
from core.simulation import get_simulation_engine
from core.reporting import get_report_generator
from core.module_loader import get_module_loader
from core.ngrok_manager import get_ngrok_manager
```

## Important Implementation Details

### Language Mix
- UI text is primarily **German** (menu items, user prompts)
- Technical logs and code comments are **English**
- Error messages support both languages

### Safety Mechanisms
- All exploits check for `simulation_mode` in parameters
- Real exploitation code wrapped in safety checks
- Dangerous operations require explicit confirmation
- All actions logged for audit trail

### Browser Chain Integration
When working with multi-exploit chains:
1. Use `BrowserExploitChain` for basic chains
2. Use `EnhancedBrowserExploitChain` for obfuscation + ngrok
3. Chain templates define exploit order and parameters
4. State is shared between exploits via `global_state`

### Obfuscation Integration
Exploits supporting obfuscation should:
1. Check for `obfuscation_enabled` in parameters
2. Use `payload_obfuscator` from parameters if provided
3. Apply appropriate obfuscation based on payload type
4. Update statistics for reporting

### Testing New Features
1. Add unit tests in `/tests` following existing patterns
2. Use `TestBase` class for common functionality
3. Mock external dependencies (network, filesystem)
4. Run validation framework after changes
5. Update `IMPLEMENTATION_LOG.md` with major changes

## Configuration

- **User Config**: `config/user_config.json` (persisted settings)
- **Default Config**: `config/default_config.json` (framework defaults)
- **Browser Chain Config**: `config/browser_chain_config.json` (multi-exploit settings)
- **Logs**: `logs/` with automatic rotation (max 10MB, 5 backups)
- **Reports**: `reports/` with subdirectories by date
- **Temp Files**: `/tmp/chromsploit_*` (cleaned on exit)

## Recent Additions (v2.2)

1. **Browser Multi-Exploit Chain**: Automated combination of 4 browser CVEs
2. **Enhanced Obfuscation**: Full payload obfuscation with multiple techniques
3. **Auto-Ngrok Integration**: Automatic tunnel creation for all callbacks
4. **CVE-2025-24813**: Apache Tomcat RCE (WAR deployment)
5. **CVE-2024-32002**: Git RCE (symbolic links)
6. **Asciinema Integration**: Terminal recording and playback system