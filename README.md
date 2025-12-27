# Ringmaster Technologies - Data Pipeline System v0.0.1

**Status**: ✅ Production Ready | **Release Date**: December 2024

Clean, interface-driven Python data pipelines for stop loss insurance marketplace operations.

> **📚 New to this project?** Start with [GETTING_STARTED.md](GETTING_STARTED.md)  
> **🚀 Migrating from existing systems?** See [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) ⭐  
> **📖 Complete Documentation**: [docs/README.md](docs/README.md) - Documentation index

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Usage Examples](#usage-examples)
- [Notebooks](#notebooks)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
- [Documentation](#documentation)
- [Migration Guide](#migration-guide)
- [Release Information](#release-information)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Install dependencies:**
   ```bash
   pip install -r requirements/requirements.txt
   pip install -r requirements/requirements-dev.txt  # For development
   ```

3. **Verify installation:**
   ```bash
   python scripts/verify_setup.py
   ```

4. **Run a pipeline:**
   ```bash
   python scripts/run_local.py claims_pipeline
   # Or use Makefile: make run-claims
   ```

5. **Verify data:**
   ```bash
   python scripts/verify_data_loaded.py
   ```

## Architecture Overview

This system emphasizes:
- **Encapsulation**: Clear class boundaries and state management
- **Abstraction**: Interface-driven design with clear contracts
- **Testability**: Unit-testable components with minimal I/O dependencies
- **Configuration-Driven**: Pipelines defined by config, not copy-pasted code
- **Professional Design**: Object-oriented patterns over clever tricks

### Key Components

- **Domain Layer** (`src/domain/`): Pure business logic, no I/O
- **Pipeline Layer** (`src/pipelines/`): Orchestration only
- **Transform Layer** (`src/transforms/`): Data transformation (bronze, silver, gold)
- **SDK Layer** (`src/sdk/`): Analyst-facing convenience interfaces
- **Utilities** (`src/utils/`): Cross-cutting concerns (I/O, database, config)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Installation

### Local Development Setup

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install package in editable mode:**
   ```bash
   pip install -e .
   ```

4. **Verify installation:**
   ```bash
   python scripts/verify_setup.py
   ```

### Docker Setup

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker instructions.

## Running Locally

### Running Pipelines

#### Command Line

```bash
# List available pipelines
python run_local.py --list

# Run claims pipeline
python run_local.py claims_pipeline

# Run policies pipeline
python run_local.py policies_pipeline

# Run with custom database path
python run_local.py claims_pipeline --db-path custom.db
```

#### Python Script

```python
from src.utils.config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load_pipeline("claims_pipeline")
pipeline = loader.create_pipeline(config)
results = pipeline.run()
```

### Using the SDK

```python
from src.sdk import ClaimsAnalyst

# Initialize analyst
analyst = ClaimsAnalyst()

# Load data from database
claims = analyst.load_from_database()

# Get summary statistics
stats = analyst.get_summary_statistics()

# Get coverage utilization
utilization = analyst.get_coverage_utilization()
```

See [EXAMPLES.md](EXAMPLES.md) for more SDK examples.

### Database Inspection

```python
from src.utils.database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM claims_silver")
    count = cursor.fetchone()[0]
    print(f"Claims in silver: {count}")
```

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup

```bash
# Start all services and wait for Airflow to be ready (recommended)
make docker-up-wait

# Or start services without waiting
make docker-up
make wait-airflow

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Docker Services

- **PostgreSQL (Airflow)**: Port 5432
- **PostgreSQL (Warehouse)**: Port 5433
- **Apache Atlas**: Port 21000
- **Airflow**: Port 8080

### Environment Variables

See [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) for environment variable configuration.

## Usage Examples

### YAML Configuration

Pipelines are defined in YAML files:

```yaml
# pipelines_config/claims_pipeline.yml
pipeline:
  name: claims_pipeline
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
    - name: claims_silver
      type: silver
    - name: claims_gold
      type: gold
      aggregation:
        type: by_policy
```

See [examples/README.md](examples/README.md) for complete examples.

### SDK Usage

See [examples/README.md](examples/README.md) for SDK usage examples.

## Notebooks

### Analyst Notebooks (SDK Usage)

- `notebooks/analyst_claims_analysis.ipynb` - Claims analysis using SDK
- `notebooks/analyst_policies_analysis.ipynb` - Policies analysis using SDK
- `notebooks/analyst_combined_analysis.ipynb` - Combined analysis

### Validation Notebooks

- `notebooks/claims_validation.ipynb` - Claims data validation
- `notebooks/policy_validation.ipynb` - Policies data validation

### Running Notebooks

1. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

2. **Navigate to notebooks directory**

3. **Run cells sequentially**

**Note**: Ensure you've run `pip install -e .` so imports work correctly.

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest src/tests/test_domain.py

# With coverage
pytest --cov=src --cov-report=html
```

### Test Structure

- `test_domain.py` - Domain logic tests
- `test_pipelines.py` - Pipeline tests
- `test_transforms.py` - Transform tests
- `test_integration.py` - Integration tests
- `test_e2e.py` - End-to-end tests

### Writing Tests

See [src/tests/TESTING.md](src/tests/TESTING.md) for testing guidelines and examples.

## Project Structure

```
hexagonal_practice/
├── src/                    # Source code
│   ├── business_rules/     # Centralized business logic
│   ├── domain/             # Domain models
│   ├── pipelines/          # Pipeline implementations
│   ├── sdk/                # Analyst SDK
│   ├── transforms/         # Data transformations
│   └── utils/              # Utilities
├── pipelines_config/       # YAML pipeline configs
├── notebooks/              # Jupyter notebooks
├── examples/               # Code examples
└── docs/                   # Documentation
```

See [REPO_STRUCTURE_v0.0.1.md](REPO_STRUCTURE_v0.0.1.md) for complete structure.

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints for all public APIs
- Write docstrings for all public methods
- Keep functions small and focused

### Adding New Features

1. Add tests first (TDD approach)
2. Implement feature
3. Update documentation
4. Run tests and verification scripts

### Database Schema Changes

If you need to modify the database schema:
1. Update `src/utils/database.py` `_initialize_schema()` method
2. Add migration logic if needed
3. Update validation notebooks if schema changes affect them

### Best Practices

- **No pandas outside transform layer**: Isolate DataFrame operations
- **Configuration over code**: Define pipelines in YAML
- **Test everything**: Write tests for new functionality
- **Document changes**: Update README and docstrings

## Documentation

### 📚 Complete Documentation Index
See **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** for a complete guide to all documentation.

### 🚀 Quick Links by Role

**For Analysts:**
- SDK Usage: [EXAMPLES.md](EXAMPLES.md) → SDK examples
- Notebooks: `notebooks/analyst_*.ipynb`
- Database Access: [README_DATABASE.md](README_DATABASE.md)

**For Engineers:**
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Pipeline Development: [EXAMPLES.md](EXAMPLES.md) → Pipeline examples
- Testing: [TESTING.md](TESTING.md)

**For DevOps:**
- Docker Setup: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- Troubleshooting: [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- Airflow: [airflow/dags/README.md](airflow/dags/README.md)

**For Project Managers:**
- Migration Guide: [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) ⭐
- Release Notes: [RELEASE_NOTES_v0.0.1.md](RELEASE_NOTES_v0.0.1.md)
- Code Review: [CODE_REVIEW_v0.0.1.md](CODE_REVIEW_v0.0.1.md)

### 📖 Documentation Groups

**Getting Started:**
- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide
- [README.md](README.md) - This file (overview)

**Architecture & Design:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [EXAMPLES.md](EXAMPLES.md) - Code examples

**Infrastructure:**
- [DOCKER.md](DOCKER.md) - Docker overview
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker setup
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Docker issues

**Testing & Validation:**
- [TESTING.md](TESTING.md) - Testing strategy
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Verification checklist
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Validation system

**Data Governance:**
- [docs/ATLAS_GUIDE.md](docs/ATLAS_GUIDE.md) - Complete Atlas guide
- [docs/ATLAS_PUBLISHING.md](docs/ATLAS_PUBLISHING.md) - Publishing metadata
- [docs/ATLAS_TROUBLESHOOTING.md](docs/ATLAS_TROUBLESHOOTING.md) - Atlas issues

**Migration:**
- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) - ⭐ **Agile/incremental migration guide**
- [sql_migration/README.md](sql_migration/README.md) - SQL migration overview
- [sql_migration/MIGRATION_PROCESS.md](sql_migration/MIGRATION_PROCESS.md) - Migration process

## Migration Guide

### 🎯 Incremental Implementation

This system is designed for **agile, incremental adoption**. You don't need to implement everything at once.

**Start Here**: [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)

The migration guide provides:
- **8 Phases** of incremental implementation
- **Risk mitigation** strategies for each phase
- **Rollback procedures** if needed
- **Success criteria** for each phase

### Quick Migration Overview

1. **Phase 0**: Foundation (Week 1-2) - Set up local environment
2. **Phase 1**: Core Framework (Week 3-4) - Implement base pipeline classes
3. **Phase 2**: Single Pipeline (Week 5-6) - Implement one complete pipeline
4. **Phase 3**: Business Logic (Week 7-8) - Migrate SQL to Python
5. **Phase 4**: SDK (Week 9-10) - Provide analyst interfaces
6. **Phase 5**: Infrastructure (Week 11-12) - Docker & production setup
7. **Phase 6**: Governance (Week 13-14) - Atlas integration
8. **Phase 7**: Testing (Week 15-16) - Comprehensive testing
9. **Phase 8**: Documentation (Week 17-18) - Training and docs

Each phase can be implemented independently and validated before proceeding.

## Release Information

### v0.0.1 Status
**Status**: ✅ Production Ready

- **Release Notes**: Archived in [docs/archive/](docs/archive/) for v0.0.1
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

### Quick Verification
```bash
# Verify setup
python scripts/verify_setup.py

# Verify data after pipeline run
python scripts/verify_data_loaded.py

# Comprehensive verification
python scripts/verify_pipeline_complete.py
```

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure package is installed
pip install -e .

# Verify installation
python verify_setup.py
```

**Database locked:**
- Close any open database connections
- Restart the application

**Missing dependencies:**
```bash
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-dev.txt
```

**Notebook import errors:**
- Ensure `pip install -e .` has been run
- Check that notebooks use correct import paths

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit a pull request

## License

[Add your license here]

## Support

For questions or issues:
- **Documentation**: See [docs/README.md](docs/README.md) - Complete documentation index
- **Troubleshooting**: See [DOCKER.md](DOCKER.md) (Docker troubleshooting) or [docs/ATLAS_TROUBLESHOOTING.md](docs/ATLAS_TROUBLESHOOTING.md)
- **Verification**: Run `python verify_setup.py` or `python scripts/verify_pipeline_complete.py`

## Release Information

- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history and changes
- **Release Notes**: Archived in [docs/archive/](docs/archive/) for v0.0.1
