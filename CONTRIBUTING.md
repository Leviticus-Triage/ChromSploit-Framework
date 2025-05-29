# 🤝 Contributing to ChromSploit Framework

Thank you for your interest in contributing to ChromSploit Framework! This guide will help you get started with contributing effectively and responsibly.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Security Considerations](#security-considerations)
- [Community](#community)

## 📜 Code of Conduct

### Our Commitment

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors, regardless of background, experience level, or identity.

### Expected Behavior

- **Be respectful** in all communications and interactions
- **Be collaborative** and help others learn and grow
- **Be constructive** when providing feedback or criticism
- **Focus on security research** and educational value
- **Respect responsible disclosure** principles

### Unacceptable Behavior

- Harassment, discrimination, or personal attacks
- Sharing exploits for malicious purposes
- Violating computer crime laws or terms of service
- Disclosing vulnerabilities without proper coordination
- Spamming or trolling in project communications

### Enforcement

Code of conduct violations should be reported to the project maintainers at conduct@chromsploit.org. All reports will be investigated promptly and fairly.

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.9+** installed
- **Git** knowledge and setup
- **Basic understanding** of web security concepts
- **Development environment** set up (see [Development Setup](#development-setup))

### Finding Ways to Contribute

Good first contributions include:

- 🐛 **Bug fixes** - Fix reported issues
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Tests** - Add or improve test coverage
- 🔧 **Tooling** - Enhance development workflow
- 🌐 **Translations** - Help with internationalization

Check our [Issues](https://github.com/yourusername/ChromSploit-Framework/issues) page for:
- `good first issue` - Beginner-friendly tasks
- `help wanted` - Tasks needing contributors
- `documentation` - Documentation improvements
- `enhancement` - Feature requests

## 🎯 Types of Contributions

### 1. Bug Reports

When reporting bugs:

```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.2]
- ChromSploit version: [e.g., v2.2]

**Additional Context**
Screenshots, logs, or other helpful information
```

### 2. Feature Requests

For new features:

```markdown
**Feature Description**
Clear description of the requested feature

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How would you like this implemented?

**Alternative Solutions**
Any alternative approaches considered

**Security Considerations**
How does this affect framework security?
```

### 3. CVE Exploit Contributions

When contributing new exploits:

- **Verify CVE exists** in official databases
- **Use public PoCs only** - no zero-days
- **Follow template structure** (see `exploits/template_exploit.py`)
- **Include simulation mode** implementation
- **Add comprehensive tests**
- **Document security implications**

Example exploit contribution:

```python
# exploits/cve_2025_xxxxx.py
class CVE2025_XXXXX_Exploit:
    """
    CVE-2025-XXXXX: Brief description
    
    References:
    - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-XXXXX
    - https://github.com/researcher/poc-repo
    """
    
    def __init__(self):
        self.cve_id = "CVE-2025-XXXXX"
        self.description = "Vulnerability description"
        # ... implementation following framework patterns
```

### 4. Module Contributions

For new framework modules:

- **Follow architecture patterns** (see docs/ARCHITECTURE.md)
- **Implement proper error handling**
- **Include fallback mechanisms**
- **Add comprehensive documentation**
- **Provide usage examples**

### 5. Documentation Improvements

Documentation contributions can include:

- **API documentation** improvements
- **Usage examples** and tutorials
- **Architecture** explanations
- **Security guidelines** updates
- **Translation** to other languages

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ChromSploit-Framework.git
cd ChromSploit-Framework

# Add upstream remote
git remote add upstream https://github.com/original/ChromSploit-Framework.git
```

### 2. Environment Setup

```bash
# Create development environment
python3 -m venv venv-dev
source venv-dev/bin/activate  # Linux/macOS
# venv-dev\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
python chromsploit.py --check
python -m pytest tests/ -v
```

### 3. Development Workflow

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes and test
python -m pytest tests/
python -m flake8 .
python -m black . --check

# Commit with conventional format
git commit -m "feat: add new CVE exploit implementation"

# Push to your fork
git push origin feature/my-new-feature

# Create pull request on GitHub
```

## 📝 Contribution Guidelines

### Code Style

We follow these coding standards:

#### Python Code Style

```python
# Use Black formatting (120 character line limit)
black . --line-length 120

# Follow PEP 8 with these additions:
# - Type hints for function signatures
# - Comprehensive docstrings
# - Descriptive variable names

def process_exploit_result(
    result: Dict[str, Any], 
    cve_id: str, 
    simulation_mode: bool = True
) -> Dict[str, Any]:
    """
    Process and sanitize exploit execution results.
    
    Args:
        result: Raw exploit execution result
        cve_id: CVE identifier for logging
        simulation_mode: Whether this was a simulated execution
        
    Returns:
        Processed and sanitized result dictionary
        
    Raises:
        ValidationError: If result format is invalid
    """
    # Implementation here
```

#### Import Organization

```python
# Standard library imports
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Third-party imports
import requests
from colorama import Fore, Style

# Local imports
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors
from modules.obfuscation import PayloadObfuscator
```

#### Error Handling

```python
# Use framework error handling
@handle_errors
def risky_operation():
    """Function that might raise exceptions"""
    pass

# Or explicit error handling
try:
    result = dangerous_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return {'success': False, 'error': str(e)}
```

### Testing Requirements

All contributions must include appropriate tests:

#### Test Structure

```python
# tests/test_exploits/test_cve_yyyy_xxxxx.py
import pytest
from unittest.mock import patch, MagicMock
from exploits.cve_yyyy_xxxxx import CVE20YY_XXXXX_Exploit

class TestCVE20YY_XXXXX:
    """Test suite for CVE-20YY-XXXXX exploit"""
    
    def setup_method(self):
        """Setup test environment"""
        self.exploit = CVE20YY_XXXXX_Exploit()
        self.test_target = "http://test.example.com"
    
    def test_simulation_execution(self):
        """Test simulation mode execution"""
        result = self.exploit.execute(self.test_target)
        
        assert result['success'] is True
        assert result['metadata']['simulation'] is True
        assert result['cve_id'] == "CVE-20YY-XXXXX"
    
    @patch('exploits.cve_yyyy_xxxxx.requests.post')
    def test_real_execution_mocked(self, mock_post):
        """Test real execution with mocked network calls"""
        # Mock setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test execution
        self.exploit.set_parameter('simulation_mode', False)
        result = self.exploit.execute(self.test_target)
        
        # Assertions
        assert mock_post.called
        assert result['success'] is True
```

#### Test Coverage

- **Unit tests** for individual functions/methods
- **Integration tests** for module interactions
- **Security tests** for input validation
- **Performance tests** for critical paths

Run tests with coverage:

```bash
# Run all tests with coverage
python -m pytest --cov=core --cov=exploits --cov=modules --cov-report=html

# Test specific components
python -m pytest tests/test_exploits/ -v
python -m pytest tests/test_core/ -v

# Run security tests
python -m pytest tests/test_security/ -v
```

### Documentation Standards

#### Docstring Format

```python
def complex_function(
    param1: str, 
    param2: Dict[str, Any], 
    param3: Optional[bool] = None
) -> Tuple[bool, str]:
    """
    One-line summary of function purpose.
    
    Longer description explaining the function's behavior,
    any important implementation details, and usage notes.
    
    Args:
        param1: Description of first parameter including format
        param2: Description of dictionary parameter with expected keys
        param3: Optional parameter with default behavior description
        
    Returns:
        Tuple containing:
            - bool: Success status
            - str: Result message or error description
            
    Raises:
        ValueError: If param1 is invalid format
        KeyError: If param2 missing required keys
        
    Example:
        >>> success, message = complex_function("test", {"key": "value"})
        >>> print(f"Success: {success}, Message: {message}")
        Success: True, Message: Operation completed
        
    Note:
        This function has side effects and may modify global state.
    """
    # Implementation
```

#### Markdown Documentation

```markdown
# Clear Section Headers

## Subsection with Purpose

Brief introduction explaining what this section covers.

### Code Examples

Provide working code examples:

```python
# Working example with comments
example = ExampleClass()
result = example.method(parameter="value")
```

### Important Notes

> **Warning**: Highlight security or safety considerations

> **Note**: Additional context or tips
```

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(exploits): add CVE-2025-12345 Chrome RCE exploit

Implement comprehensive Chrome remote code execution exploit
based on public PoC from security researcher. Includes:
- Mojo IPC payload generation
- Multi-stage exploitation
- Comprehensive test suite

Closes #123

fix(core): resolve module loading race condition

Fixed race condition in module loader that occurred when
multiple modules were loaded simultaneously. Added proper
locking mechanism and improved error handling.

Fixes #456

docs(api): update browser chain API documentation

Added missing parameters and improved examples for the
enhanced browser exploit chain API.
```

## 🔄 Pull Request Process

### 1. Before Creating PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Security implications considered
- [ ] CHANGELOG.md updated (if applicable)

```bash
# Pre-PR checklist commands
python -m pytest tests/ -v
python -m flake8 .
python -m black . --check
python -m mypy chromsploit.py --ignore-missing-imports
bandit -r . -x tests/
```

### 2. PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Security testing performed

## Security Considerations
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Simulation mode implemented (for exploits)
- [ ] Audit logging added

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No conflicts with main branch

## Screenshots (if applicable)
Add screenshots for UI changes or new features.

## Additional Notes
Any additional information or context.
```

### 3. Review Process

PRs will be reviewed for:

- **Code quality** and adherence to standards
- **Security implications** and safety measures
- **Test coverage** and quality
- **Documentation** completeness
- **Performance** impact
- **Breaking changes** assessment

### 4. Feedback and Iteration

- Address reviewer feedback promptly
- Make requested changes in new commits
- Engage in constructive discussion
- Update documentation as needed

## 🔒 Security Considerations

### Responsible Disclosure

When contributing security-related content:

1. **Use only public information** - no zero-days or unreported vulnerabilities
2. **Follow responsible disclosure** - coordinate with vendors when appropriate
3. **Implement simulation mode** - all exploits must have safe simulation
4. **Document security implications** - explain risks and mitigations

### Security Review Process

Security-sensitive contributions undergo additional review:

- **Security team review** for exploit contributions
- **Threat modeling** for new features
- **Penetration testing** for significant changes
- **Third-party audit** for major releases

### Security Reporting

To report security issues in contributions:

1. Email security@chromsploit.org (not GitHub issues)
2. Include detailed information
3. Allow reasonable response time
4. Follow coordinated disclosure

## 🌟 Recognition

### Contributors

All contributors are recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Annual contributor highlights**

### Types of Recognition

- **Code contributors** - Direct code contributions
- **Security researchers** - Vulnerability research and responsible disclosure
- **Documentation contributors** - Documentation improvements
- **Community supporters** - Help with issues, discussions, and community building
- **Translators** - Internationalization efforts

### Hall of Fame

Outstanding contributors may be recognized in our Hall of Fame for:

- Significant code contributions
- Important security research
- Community leadership
- Long-term project support

## 💬 Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General discussion and Q&A
- **Security Email** - security@chromsploit.org (private security issues)
- **Contributor Chat** - Discord/Slack (invitation required)

### Getting Help

If you need help contributing:

1. **Check documentation** - README, docs/, and CLAUDE.md
2. **Search existing issues** - someone may have asked already
3. **Ask in discussions** - GitHub Discussions for general questions
4. **Contact maintainers** - for specific contribution questions

### Community Events

We organize regular community events:

- **Monthly contributor calls** - Progress updates and coordination
- **Security research showcases** - Present findings and techniques
- **Documentation sprints** - Collaborative documentation improvement
- **Code review sessions** - Learn best practices

## 📄 License

By contributing to ChromSploit Framework, you agree that your contributions will be licensed under the same license as the project (MIT License). You confirm that:

- You have the right to submit the contributions
- Your contributions are your original work or properly attributed
- You understand the security and ethical implications
- You agree to the project's Code of Conduct

## 🙏 Thank You

Thank you for contributing to ChromSploit Framework! Your contributions help make security research more accessible, educational, and effective. Together, we can build a powerful tool for the security community while maintaining the highest standards of responsibility and ethics.

---

**Questions?** Feel free to reach out via GitHub Discussions or email the maintainers at contributors@chromsploit.org.