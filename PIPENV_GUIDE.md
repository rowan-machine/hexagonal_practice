# Pipenv Guide

Complete guide to using Pipenv for dependency management in this project.

> **💡 Not sure which to use?** This project supports both **Pipenv** and **venv**. See [GETTING_STARTED.md](GETTING_STARTED.md) for both options. Pipenv provides better dependency management, while venv is built into Python.

## What is Pipenv?

Pipenv is a tool that combines `pip` and `virtualenv` into a single command. It automatically manages virtual environments and dependencies using `Pipfile` and `Pipfile.lock`.

## Installation

### Install Pipenv

```bash
# Using pip
pip install pipenv

# Using homebrew (macOS)
brew install pipenv

# Using apt (Ubuntu/Debian)
sudo apt install pipenv
```

### Verify Installation

```bash
pipenv --version
```

## Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies (production + development)
pipenv install --dev

# This will:
# - Create a virtual environment automatically
# - Install all packages from Pipfile
# - Generate Pipfile.lock
```

### 2. Activate Virtual Environment

```bash
# Activate the shell
pipenv shell

# Your prompt will change to show you're in the virtual environment
# (hexagonal_practice) $
```

### 3. Install Package in Editable Mode

```bash
# After activating shell
pip install -e .

# Or run directly without activating
pipenv run pip install -e .
```

## Common Commands

### Environment Management

```bash
# Install dependencies
pipenv install              # Production dependencies only
pipenv install --dev        # Production + development dependencies

# Activate virtual environment
pipenv shell

# Exit virtual environment
exit

# Run command in virtual environment (without activating)
pipenv run <command>

# Show virtual environment path
pipenv --venv

# Remove virtual environment
pipenv --rm
```

### Dependency Management

```bash
# Install a package
pipenv install package-name

# Install development package
pipenv install --dev package-name

# Install specific version
pipenv install "package-name==1.2.3"

# Uninstall package
pipenv uninstall package-name

# Update all packages
pipenv update

# Update specific package
pipenv update package-name

# Show installed packages
pipenv graph

# Show package dependencies
pipenv graph --reverse
```

### Running Commands

```bash
# Run Python script
pipenv run python script.py

# Run pytest
pipenv run pytest

# Run make commands
pipenv run make test
pipenv run make lint

# Run Jupyter
pipenv run jupyter notebook
```

## Project-Specific Usage

### Development Workflow

```bash
# 1. Clone repository
git clone <repository-url>
cd hexagonal_practice

# 2. Install dependencies
pipenv install --dev

# 3. Activate environment
pipenv shell

# 4. Install package
pip install -e .

# 5. Run tests
pipenv run pytest

# 6. Run linting
pipenv run make lint
```

### Running Notebooks

```bash
# Start Jupyter in pipenv environment
pipenv run jupyter notebook

# Or activate shell first
pipenv shell
jupyter notebook
```

### Running Scripts

```bash
# Run pipeline script
pipenv run python scripts/run_local.py claims_pipeline

# Run examples
pipenv run python examples/sdk_example.py
```

## Pipfile Structure

The `Pipfile` contains:

```toml
[packages]
# Production dependencies
pyyaml = ">=6.0"
pandas = ">=2.0.0"
requests = ">=2.31.0"

[dev-packages]
# Development dependencies
pytest = ">=7.0.0"
black = ">=23.0.0"
jupyter = ">=1.0.0"
# ... etc

[requires]
python_version = "3.8"
```

## Benefits of Pipenv

1. **Automatic Virtual Environment**: No need to create venv manually
2. **Lock File**: `Pipfile.lock` ensures reproducible builds
3. **Security**: Automatically checks for security vulnerabilities
4. **Simple Commands**: One command for install, run, etc.
5. **Dependency Resolution**: Handles dependency conflicts automatically

## Troubleshooting

### Problem: Command not found

**Error:** `pipenv: command not found`

**Solution:**
```bash
pip install pipenv
# Or use pip3
pip3 install pipenv
```

### Problem: Virtual environment not found

**Error:** `Virtualenv was not found`

**Solution:**
```bash
# Remove old environment and recreate
pipenv --rm
pipenv install --dev
```

### Problem: Lock file out of sync

**Error:** `Pipfile.lock is out of date`

**Solution:**
```bash
# Update lock file
pipenv lock

# Or reinstall
pipenv install --dev
```

### Problem: Package installation fails

**Error:** `Could not find a version that satisfies the requirement`

**Solution:**
```bash
# Update pipenv
pip install --upgrade pipenv

# Clear cache
pipenv clear

# Try installing again
pipenv install --dev
```

## Migration from venv/pip

If you're currently using `venv` and `pip`:

1. **Install pipenv:**
   ```bash
   pip install pipenv
   ```

2. **Remove old virtual environment:**
   ```bash
   deactivate  # If activated
   rm -rf venv  # Or venv\ on Windows
   ```

3. **Install with pipenv:**
   ```bash
   pipenv install --dev
   ```

4. **Activate new environment:**
   ```bash
   pipenv shell
   ```

## Best Practices

1. **Commit Pipfile and Pipfile.lock**: Both should be in version control (they're already in this repo)
2. **Use `pipenv install` for new packages**: Don't use `pip install` directly
3. **Update regularly**: Run `pipenv update` periodically
4. **Check security**: `pipenv check` checks for vulnerabilities
5. **Use `pipenv run`**: For one-off commands without activating shell
6. **Don't commit virtual environment**: The `.venv/` directory is automatically ignored

## Integration with Make

You can use pipenv with Make commands:

```bash
# In Makefile, prefix commands with pipenv run
test:
	pipenv run pytest

lint:
	pipenv run ruff check src/
```

Or activate shell first:
```bash
pipenv shell
make test
```

## Next Steps

**Pipenv set up?** Continue with:

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** → Complete setup guide
2. **[notebooks/ANALYST_GUIDE.md](notebooks/ANALYST_GUIDE.md)** → Analyst guide
3. **[docs/DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md)** → Developer onboarding

**Need help?**

1. Check [Troubleshooting](#troubleshooting) section above
2. Visit [Pipenv documentation](https://pipenv.pypa.io/)
3. Run `pipenv --help` for command reference

