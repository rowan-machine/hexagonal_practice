# Contributing to Ringmaster Pipelines

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/rowan-machine/hexagonal_practice.git
   cd hexagonal_practice
   ```

2. **Create a virtual environment**

   **Choose one option:**

   **Option A: Using venv (Standard Python)**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Activate (Linux/Mac)
   source .venv/bin/activate
   
   # Install dependencies
   pip install -e ".[dev]"
   ```

   **Option B: Using Pipenv (Recommended for Dependency Management)**
   ```bash
   # Install pipenv (if not installed)
   pip install pipenv
   
   # Install dependencies (creates virtual environment automatically)
   pipenv install --dev
   
   # Activate environment
   pipenv shell
   
   # Install package in editable mode
   pipenv run pip install -e .
   ```

   **Note:** Both options work equally well. Pipenv provides better dependency management and lock files, while venv is built into Python. Choose based on your preference or team standards.

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Code Style

We follow PEP 8 and use automated tools to ensure code quality:

- **Ruff**: Linting and import sorting
- **Black**: Code formatting (line length: 100)
- **MyPy**: Type checking (optional, not strict)

### Running Code Quality Checks

```bash
# Using Make (recommended)
make format      # Format code
make lint        # Lint code
make type-check  # Type check
make ci          # Run all checks

# Or manually
black src/ tests/
ruff check src/ tests/
mypy src/
```

See [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) for detailed guidelines.

## Testing

- Write tests for all new features
- Ensure all tests pass: `pytest`
- Aim for 80%+ code coverage
- Run tests with coverage: `pytest --cov=src --cov-report=html`

### Test Structure

- `test_domain.py` - Domain logic tests
- `test_pipelines.py` - Pipeline orchestration tests
- `test_transforms.py` - Transform layer tests
- `test_integration.py` - Integration tests
- `test_e2e.py` - End-to-end tests

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   # Run all checks
   pre-commit run --all-files
   
   # Run tests
   pytest
   ```

4. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```
   - Use clear, descriptive commit messages
   - Reference issues if applicable

5. **Push and create a Pull Request**
   - Push to your fork
   - Create a PR with a clear description
   - Link any related issues

## Code Review Guidelines

- All PRs require at least one approval
- Address review comments promptly
- Keep PRs focused and reasonably sized
- Update documentation for user-facing changes

## Documentation

- Update `README.md` for significant changes
- Add docstrings to all public APIs
- Update `CHANGELOG.md` for user-facing changes
- Keep examples up to date

## Questions?

- Open an issue for bugs or feature requests
- Check existing documentation first
- Ask questions in discussions

## Next Steps

**Ready to contribute?** Follow this path:

1. **[docs/DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md)** → ⭐ Understand all project files and tools
2. **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** → Review best practices
3. **[src/tests/TESTING.md](src/tests/TESTING.md)** → Learn testing patterns
4. **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** → Understand architecture

**Making your first contribution?**

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** → Set up your environment
2. **[docs/DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md)** → Learn about project files and workflow
3. **[examples/README.md](examples/README.md)** → Run examples to understand the system
4. **[docs/README.md](docs/README.md)** → Find relevant documentation

**Submitting a PR?**

1. Review [Code Review Guidelines](#code-review-guidelines) above
2. **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** → Ensure code follows best practices
3. **[SECURITY.md](SECURITY.md)** → Check security considerations
4. Run `make ci` to verify all checks pass

Thank you for contributing! 🎉

