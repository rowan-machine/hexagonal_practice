"""
Setup configuration for editable installation.

This file is kept for backward compatibility.
Modern projects should use pyproject.toml (which is the primary config).
Install with: pip install -e .
"""
from setuptools import setup, find_packages

# Read version and metadata from pyproject.toml if available
# Otherwise use defaults
setup(
    name="ringmaster-pipelines",
    version="0.0.1",
    description="Clean, interface-driven Python data pipelines for stop loss insurance",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    # Dependencies are defined in pyproject.toml
    # This setup.py is minimal to avoid conflicts
)

