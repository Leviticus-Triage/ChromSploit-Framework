#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Setup and installation script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()
optional_requirements = (this_directory / "requirements-optional.txt").read_text().splitlines()

setup(
    name="chromsploit-framework",
    version="2.0.0",
    author="Leviticus-Triage",
    author_email="",
    description="A modular educational framework for learning about browser security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leviticus-Triage/ChromSploit-Framework",
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "optional": optional_requirements,
    },
    entry_points={
        "console_scripts": [
            "chromsploit=chromsploit:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
        "config": ["*.json"],
        "docs": ["*.md", "*.txt"],
    },
    zip_safe=False,
)