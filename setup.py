"""
Setup configuration for editable installation.

Install with: pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name="ringmaster-pipelines",
    version="0.0.1",
    description="Clean, interface-driven Python data pipelines for stop loss insurance",
    author="Ringmaster Technologies",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "types-python-dateutil>=2.8.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
        ],
    },
)

