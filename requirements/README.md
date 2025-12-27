# Requirements Files

This directory contains Python dependency files for different environments and use cases.

## Files

### `requirements.txt`

Core production dependencies required to run the pipeline system.

**Installation:**
```bash
pip install -r requirements/requirements.txt
```

**Includes:**
- `pyyaml>=6.0` - YAML configuration parsing
- `pandas>=2.0.0` - Data processing and DataFrame operations
- `requests>=2.31.0` - HTTP client for Atlas integration

**Note:** These are the minimum dependencies. The system is designed to work with standard library for core functionality, with optional dependencies for enhanced features.

### `requirements-dev.txt`

Development dependencies for testing, linting, and code quality.

**Installation:**
```bash
pip install -r requirements/requirements-dev.txt
```

**Includes:**
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Test coverage reporting
- `mypy>=1.0.0` - Type checking
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting and import sorting
- `jupyter>=1.0.0` - Jupyter notebooks
- `ipykernel>=6.0.0` - Jupyter kernel
- `pre-commit>=3.0.0` - Pre-commit hooks

**Usage:**
```bash
# Install with editable package
pip install -e ".[dev]"

# Or install requirements directly
pip install -r requirements/requirements-dev.txt
```

### `requirements-airflow.txt`

Dependencies for running pipelines in Apache Airflow.

**Installation:**
```bash
pip install -r requirements/requirements-airflow.txt
```

**Usage:**
- Used in Docker containers for Airflow
- Includes Airflow-specific dependencies
- May include additional packages for Airflow operators

## Installation

### Production Setup

```bash
# Install core dependencies
pip install -r requirements/requirements.txt

# Install package in editable mode
pip install -e .
```

### Development Setup

```bash
# Install all dependencies (recommended)
pip install -e ".[dev]"

# Or install separately
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-dev.txt
```

### Docker Setup

Dependencies are automatically installed in Docker containers. See `DOCKER.md` for details.

## Version Management

### Version Constraints

- **Minimum versions**: Using `>=` for flexibility
- **Compatible versions**: Tested with specified minimum versions
- **Future versions**: Should be compatible with newer versions

### Pinning Versions

For production deployments, consider pinning exact versions:

```bash
# Generate pinned requirements
pip freeze > requirements/requirements-lock.txt
```

## Dependency Management

### Adding Dependencies

1. **Production**: Add to `requirements.txt`
2. **Development**: Add to `requirements-dev.txt`
3. **Airflow**: Add to `requirements-airflow.txt`
4. **Update setup.py**: Add to `install_requires` or `extras_require`

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade <package-name>

# Update requirements file
pip freeze > requirements/requirements.txt
```

## Best Practices

1. **Separate Environments**: Keep production and development dependencies separate
2. **Version Constraints**: Use minimum versions (`>=`) for flexibility
3. **Documentation**: Document why each dependency is needed
4. **Security**: Regularly update dependencies for security patches
5. **Testing**: Test with updated dependencies before deploying

## Next Steps

**Dependencies installed?** Continue with:

1. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup and run your first pipeline
2. **[examples/README.md](../examples/README.md)** → Try the examples
3. **[scripts/README.md](../scripts/README.md)** → Run verification scripts

**Setting up for development?**

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Development setup guide
2. **[docs/BEST_PRACTICES.md](../docs/BEST_PRACTICES.md)** → Development best practices
3. **[Makefile](../Makefile)** → Use `make install-dev` for convenience

**Using Docker?**

1. **[DOCKER.md](../DOCKER.md)** → Docker setup and usage
2. **[requirements-airflow.txt](requirements-airflow.txt)** → Airflow dependencies

## Related Documentation

- **[Getting Started](../GETTING_STARTED.md)** - Setup instructions
- **[Docker Guide](../DOCKER.md)** - Docker setup
- **[Contributing](../CONTRIBUTING.md)** - Development setup

