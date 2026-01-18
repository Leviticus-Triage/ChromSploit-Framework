# Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+ (WSL2 recommended)
- **Python**: 3.8+ (3.9+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for dependencies and exploit delivery

### Recommended Requirements
- **CPU**: Multi-core processor for parallel exploit execution
- **Memory**: 16GB RAM for large-scale operations
- **Storage**: SSD with 10GB+ free space
- **Network**: High-speed connection for real-time monitoring

## Quick Installation

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework

# Install dependencies
pip3 install -r requirements.txt

# Make executable
chmod +x chromsploit.py

# Run ChromSploit
python3 chromsploit.py
```

### Method 2: Download Release

```bash
# Download latest release
wget https://github.com/Leviticus-Triage/ChromSploit-Framework/releases/latest/download/chromsploit-v2.2.tar.gz

# Extract
tar -xzf chromsploit-v2.2.tar.gz
cd ChromSploit-Framework

# Install and run
pip3 install -r requirements.txt
python3 chromsploit.py
```

---

## Linux Installation

### Ubuntu/Debian

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3 python3-pip python3-venv git curl wget

# 3. Clone repository
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verify installation
python chromsploit.py --check
```

### CentOS/RHEL/Fedora

```bash
# For CentOS/RHEL
sudo yum install -y python3 python3-pip git

# For Fedora
sudo dnf install -y python3 python3-pip git

# Continue with common steps
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-pip git

# Clone and setup
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Windows Installation

### Method 1: Windows Subsystem for Linux (Recommended)

```powershell
# 1. Enable WSL
wsl --install

# 2. Install Ubuntu
wsl --install -d Ubuntu

# 3. Follow Linux installation steps in WSL
```

### Method 2: Native Windows

```powershell
# 1. Install Python 3.9+ from python.org
# 2. Install Git from git-scm.com

# 3. Open PowerShell/Command Prompt
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework

# 4. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Run framework
python chromsploit.py --check
```

---

## macOS Installation

### Using Homebrew (Recommended)

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install python@3.9 git

# 3. Clone repository
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verify installation
python chromsploit.py --check
```

### Using MacPorts

```bash
# Install dependencies
sudo port install python39 git

# Continue with standard setup
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Docker Installation

### Quick Start with Docker

```bash
# 1. Pull the image
docker pull chromsploit/framework:v2.2

# 2. Run container
docker run -it --rm \
 --name chromsploit \
 -p 8080:8080 \
 -p 4444:4444 \
 chromsploit/framework:v2.2

# 3. Or build from source
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
docker build -t chromsploit:local .
docker run -it --rm chromsploit:local
```

### Docker Compose

```yaml
version: '3.8'
services:
 chromsploit:
 image: chromsploit/framework:v2.2
 ports:
 - "8080:8080"
 - "4444:4444"
 volumes:
 - ./reports:/app/reports
 - ./logs:/app/logs
 environment:
 - CHROMSPLOIT_MODE=safe
```

---

##  Advanced Installation

### Development Installation

```bash
# Clone with development branch
git clone -b develop https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework

# Install with development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

### Kali Linux (Specialized)

```bash
# Kali has most dependencies pre-installed
sudo apt update
sudo apt install -y python3-venv

# Clone and setup
git clone https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: Install additional tools
sudo apt install -y metasploit-framework ngrok
```

### Minimal Installation

```bash
# For environments with limited resources
git clone --depth=1 https://github.com/Leviticus-Triage/ChromSploit-Framework.git
cd ChromSploit-Framework
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r requirements-minimal.txt
```

---

## Configuration

### Initial Setup

```bash
# 1. Activate virtual environment
source venv/bin/activate # Linux/macOS
# or
venv\Scripts\activate # Windows

# 2. Run initial configuration
python chromsploit.py --configure

# 3. Test installation
python chromsploit.py --check
```

### Configuration Files

| File | Purpose | Location |
|-----------------------------|------------------------|-----------|
| `user_config.json` | User preferences | `config/` |
| `default_config.json` | Framework defaults | `config/` |
| `browser_chain_config.json` | Multi-exploit settings | `config/` |

### Environment Variables

```bash
# Optional environment variables
export CHROMSPLOIT_MODE=safe # Default execution mode
export CHROMSPLOIT_LOG_LEVEL=INFO # Logging level
export CHROMSPLOIT_DATA_DIR=/custom # Custom data directory
export CHROMSPLOIT_NGROK_TOKEN=xxx # Ngrok authentication token
```

---

## Verification

### System Check

```bash
# Comprehensive system check
python chromsploit.py --check

# Expected output:
# Python version: 3.9+
# Dependencies: All installed
# Permissions: Adequate
# Network: Available
# Storage: Sufficient
```

### Feature Test

```bash
# Test core features
python chromsploit.py --test-features

# Test specific components
python -m pytest tests/test_installation.py -v
```

### Performance Benchmark

```bash
# Run performance tests
python -m core.validation_framework --benchmark

# Expected results:
# - Memory usage: <200MB
# - Startup time: <5s
# - Module loading: <2s
```

---

## First Run

### Safe Mode (Recommended)

```bash
# Start in safe simulation mode
python chromsploit.py --simulation safe

# Navigate to: Browser Multi-Exploit Chain > Quick Full Browser Compromise
```

### Interactive Tutorial

```bash
# Launch interactive tutorial
python chromsploit.py --tutorial

# Follow guided walkthrough of features
```

### Demo Mode

```bash
# Watch pre-recorded demonstrations
cd asciinema
asciinema play chromsploit_complete_demo.cast
```

---

## Troubleshooting

### Common Issues

<details>
<summary><b> Python Version Issues</b></summary>

```bash
# Check Python version
python --version
python3 --version

# If version < 3.9, install newer Python
# Ubuntu/Debian:
sudo apt install python3.9 python3.9-venv

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```
</details>

<details>
<summary><b> Dependency Installation Failures</b></summary>

```bash
# Clear pip cache
pip cache purge

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with verbose output
pip install -r requirements.txt -v

# Alternative: Install manually
pip install requests colorama pytest click
```
</details>

<details>
<summary><b> Permission Errors</b></summary>

```bash
# Fix file permissions
chmod +x chromsploit.py
find . -name "*.py" -exec chmod +x {} \;

# Create necessary directories
mkdir -p logs reports temp

# Fix ownership (if needed)
sudo chown -R $USER:$USER .
```
</details>

<details>
<summary><b> Network Issues</b></summary>

```bash
# Test network connectivity
curl -I https://github.com

# Configure proxy (if needed)
export https_proxy=http://proxy:port
export http_proxy=http://proxy:port

# Install behind firewall
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org
```
</details>

### Getting Help

- Check [FAQ](../FAQ.md)
- Open [GitHub Issue](../../issues)
- Join [Discussions](../../discussions)

---

## Updating

### Automatic Update

```bash
# Update to latest version
python chromsploit.py --update

# Update to specific version
python chromsploit.py --update --version v2.2.1
```

### Manual Update

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migration (if needed)
python chromsploit.py --migrate
```

---

##  Uninstallation

### Complete Removal

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove directory
rm -rf ChromSploit-Framework

# 3. Clean system packages (optional)
# Ubuntu/Debian:
sudo apt autoremove python3-pip python3-venv

# 4. Remove Docker images (if used)
docker rmi chromsploit/framework:v2.2
```

---

## Installation Statistics

<div align="center">

| Platform | Success Rate | Avg. Instal Time | Disk Usage |
|---------------|--------------|------------------|------------|
| Ubuntu 20.04+ | 98% | 3-5 minutes | 450MB |
| Windows 10+ | 95% | 5-8 minutes | 520MB |
| macOS 11+ | 97% | 4-6 minutes | 480MB |
| Kali Linux | 99% | 2-3 minutes | 420MB |

</div>

---

<div align="center">

** Installation Complete! Ready to start your security research journey with ChromSploit Framework.**

 **Next Step:** [Quick Start Guide](../README.md#quick-start)

</div>