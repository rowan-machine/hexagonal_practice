# Documentation Index

Complete guide to all documentation in the project.

## Getting Started

- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Step-by-step guide for junior developers
- **[README.md](README.md)**: Main project documentation with overview and usage
- **[EXAMPLES.md](EXAMPLES.md)**: Code examples and snippets

## Architecture and Design

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design principles
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and changes

## Operations

- **[DOCKER.md](DOCKER.md)**: Complete Docker and Docker Compose guide
- **[README_DATABASE.md](README_DATABASE.md)**: Database integration guide

## Development

- **[TESTING.md](TESTING.md)**: Comprehensive testing guide
- **[requirements.txt](requirements.txt)**: Production dependencies
- **[requirements-dev.txt](requirements-dev.txt)**: Development dependencies

## Notebooks

All notebooks are in the `notebooks/` directory:

### Analyst SDK Notebooks
- **`analyst_claims_analysis.ipynb`**: Claims analysis using ClaimsAnalyst SDK
- **`analyst_policies_analysis.ipynb`**: Policies analysis using PoliciesAnalyst SDK
- **`analyst_combined_analysis.ipynb`**: Combined claims and policies analysis

### Validation Notebooks
- **`claims_validation.ipynb`**: Inspect claims data from warehouse database
- **`policy_validation.ipynb`**: Inspect policies data from warehouse database

## Quick Reference

### Running Pipelines

```bash
# List pipelines
python run_local.py --list

# Run pipeline
python run_local.py claims_pipeline

# With custom database
python run_local.py claims_pipeline --db-path warehouse.db
```

### Using SDK

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))
claims = analyst.load_claims("data/raw_claims.json")
total = analyst.get_total_claims(claims)
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test
pytest src/tests/test_domain.py::TestClaim::test_claim_creation
```

## Documentation by Role

### For Junior Developers
1. Start with [GETTING_STARTED.md](GETTING_STARTED.md)
2. Read [EXAMPLES.md](EXAMPLES.md) for code snippets
3. Explore notebooks in `notebooks/` directory
4. Review test files in `src/tests/`

### For Analysts
1. Read [README.md](README.md) SDK section
2. Use analyst notebooks in `notebooks/analyst_*.ipynb`
3. See [EXAMPLES.md](EXAMPLES.md) for SDK usage

### For Engineers
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for design
2. Review [TESTING.md](TESTING.md) for testing practices
3. Check [DOCKER.md](DOCKER.md) for deployment

### For DevOps
1. Read [DOCKER.md](DOCKER.md) for containerization
2. Review `docker-compose.yml` for service configuration
3. Check `requirements*.txt` for dependencies

## Code Documentation

All code includes:
- **Module docstrings**: Overview of each module
- **Class docstrings**: Purpose and usage of each class
- **Method docstrings**: Parameters, returns, and examples
- **Type hints**: All public APIs are fully typed

## Need Help?

1. Check the relevant documentation file above
2. Review code examples in [EXAMPLES.md](EXAMPLES.md)
3. Look at test files for usage patterns
4. Explore notebooks for interactive examples

