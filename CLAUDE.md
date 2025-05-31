# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ChromSploit Framework Overview

ChromSploit Framework is an educational security research tool with a modular architecture for studying browser vulnerabilities. The codebase emphasizes safety through simulation modes and professional reporting for authorized penetration testing.

## Key Commands

### Running the Framework
```bash
# Standard launch
python chromsploit.py

# With simulation mode (recommended for development)
python chromsploit.py --simulation safe    # Safe mode (default)
python chromsploit.py --simulation demo    # Demo mode with explanations
python chromsploit.py --debug              # Enable debug output
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

# Install in development mode
pip install -e .[dev]

# Create new exploit module
cp exploits/cve_2025_4664.py exploits/cve_YYYY_XXXXX.py  # Use as template
```

## Architecture

### Core System Flow
```
chromsploit.py (Entry Point)
    ├── Environment Check
    ├── Configuration Loading (config/*.json)
    ├── Module Loader (core/module_loader.py)
    ├── Enhanced Logger Initialization
    └── Main Menu System (ui/main_menu.py)
```

### Key Architectural Patterns

1. **Module Loading System** (`core/module_loader.py`):
   - Dynamic loading with graceful failure handling
   - Singleton registry for loaded modules
   - Use `get_module_loader().load_module(name)` pattern

2. **Enhanced Menu System** (`ui/*.py`):
   - Base class: `EnhancedMenu` in `core/enhanced_menu.py`
   - Keyboard shortcuts and navigation breadcrumbs
   - Consistent error handling with `@handle_errors` decorator
   - **CRITICAL**: EnhancedMenu.__init__() only accepts (title, parent) parameters
   - Use `menu.set_description()` for descriptions, not constructor parameter

3. **Exploit Implementation Pattern**:
   ```python
   class CVE20XX_XXXXX_Exploit:
       def __init__(self):
           self.config = {...}
       
       def execute(self, target_url=None):
           return {
               'success': bool,
               'cve_id': str,
               'artifacts': dict
           }
   
   # Legacy function interface (required)
   def execute_exploit(parameters: Dict[str, Any]) -> Dict[str, Any]:
       exploit = CVE20XX_XXXXX_Exploit()
       return exploit.execute()
   ```

4. **Global Instance Access Pattern**:
   ```python
   from core.enhanced_logger import get_logger
   from core.error_handler import get_error_handler
   from core.module_loader import get_module_loader
   from core.ngrok_manager import get_ngrok_manager
   ```

5. **AI Integration Pattern**:
   ```python
   # Always include graceful fallback for AI modules
   try:
       from modules.ai.ai_orchestrator import AIOrchestrator
       self.ai_orchestrator = AIOrchestrator()
       self.logger.info("AI Orchestrator loaded for [module_name]")
   except ImportError:
       self.ai_orchestrator = None
       self.logger.debug("AI Orchestrator not available")
   ```

### Safety Mechanisms
- All exploits check for `simulation_mode` in parameters
- Dangerous operations require explicit confirmation
- Complete audit trail logging
- Educational flags on all content

## Configuration

- **User Config**: `config/user_config.json` (persisted settings)
- **Default Config**: `config/default_config.json` (framework defaults)
- **Logs**: `logs/` with automatic rotation
- **Reports**: `reports/` with subdirectories by date

## Critical Implementation Details

### Menu System Requirements
When working with any menu classes:
1. **ALWAYS** inherit from `EnhancedMenu` or `Menu`
2. **NEVER** pass `description=` to EnhancedMenu constructor
3. Use `self.set_description()` method instead
4. Ensure all menu classes have `exit_menu()` and `run()` methods
5. Use `@handle_errors` decorator on all menu methods

### Logger Usage
- **Always** use `from core.enhanced_logger import get_logger`
- **Never** use `from core.logger import Logger` directly
- Initialize with `self.logger = get_logger()` in constructors
- Call as instance methods: `self.logger.info("message")`

### NgrokManager Integration
- Use `from core.ngrok_manager import get_ngrok_manager`
- Both `start_tunnel()` and `create_tunnel()` methods available
- Supports automatic CVE parameter synchronization

### Language Mix
- UI text is primarily German (menu items, user prompts)
- Technical logs and code comments are English
- Error messages support both languages

### Menu Integration
When adding new menu items:
1. Inherit from `EnhancedMenu`
2. Use `@handle_errors` decorator on methods
3. Follow the `get_*()` pattern for singletons
4. Implement both `run()` and `exit_menu()` methods
5. **CRITICAL**: Use proper constructor pattern:
   ```python
   def __init__(self):
       super().__init__(title="Menu Title")
       self.set_description("Menu description here")
   ```

### Error-Prone Patterns to Avoid
1. **Wrong**: `EnhancedMenu(title="X", description="Y")`
   **Right**: `EnhancedMenu(title="X"); menu.set_description("Y")`

2. **Wrong**: `Logger.info("message")`
   **Right**: `self.logger.info("message")`

3. **Wrong**: Missing `exit_menu()` or `run()` methods
   **Right**: Always implement both methods

4. **Wrong**: `ngrok_manager.create_tunnel()` without checking if method exists
   **Right**: Use `get_ngrok_manager().create_tunnel()` (method exists)

### Testing New Features
1. Add unit tests in `/tests` following existing patterns
2. Use `TestBase` class for common functionality
3. Mock external dependencies
4. Run validation framework after changes
5. Test all menu navigation paths

## Dependencies

- **Core**: Python 3.9+, requests, colorama, tabulate, click
- **UI**: prompt_toolkit, rich, psutil
- **Network**: scapy, dnspython, python-nmap, websockets
- **Development**: pytest, black, flake8, mypy, bandit
- **AI (Optional)**: PyTorch, transformers (graceful fallback implemented)

## Framework Integration Points

### External Tools
- **Ngrok**: Tunnel creation via `core/ngrok_manager.py`
- **Metasploit**: Integration via `tools/metasploit_integration.py`
- **OLLVM**: Binary obfuscation support

### Module Extensions
The framework supports optional modules that gracefully degrade if dependencies are missing:
```python
try:
    from optional_module import SomeFeature
    feature_available = True
except ImportError:
    feature_available = False
```

## Working with the Codebase

### Adding New Exploits
1. Use existing CVE files as templates
2. Implement both class and function interfaces
3. Include simulation mode support
4. Add comprehensive error handling
5. Update tests and documentation

### Menu Development
1. Inherit from `EnhancedMenu`
2. Implement conditional feature loading
3. Use consistent key numbering
4. Provide clear user feedback
5. Follow the established UI patterns
6. **CRITICAL**: Use proper initialization pattern shown above

### Common Debugging
- Check logs in `logs/chromsploit_errors.log` for issues
- Use `--debug` flag for verbose output
- Verify all menu classes have required methods
- Ensure proper singleton pattern usage

This framework prioritizes educational value, safety, and professional presentation for authorized security research.