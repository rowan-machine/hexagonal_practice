# Repository Structure: Ringmaster Pipelines v0.0.1

Complete guide to the repository structure and file organization.

---

## 📁 Directory Structure

```
hexagonal_practice/
├── src/                          # Source code
│   ├── business_rules/           # Centralized business logic
│   ├── domain/                   # Domain models and processors
│   ├── mixins/                   # Reusable mixins (logging, metrics, validation)
│   ├── pipelines/                # Pipeline implementations
│   ├── sdk/                      # Analyst-facing SDK
│   ├── tests/                    # Test suite
│   ├── transforms/               # Data transformation layers
│   └── utils/                    # Utility modules
│
├── docs/                         # Documentation
│   ├── MIGRATION_GUIDE.md        # ⭐ Agile migration guide
│   ├── DOCUMENTATION_INDEX.md    # Complete documentation index
│   └── ATLAS_*.md                # Atlas documentation
│
├── pipelines_config/             # YAML pipeline configurations
├── schemas/                      # Data schema definitions
├── config/                       # Configuration files
├── data/                         # Sample data files
├── notebooks/                    # Jupyter notebooks
├── examples/                     # Code examples
├── airflow/                      # Airflow DAGs
├── docker/                       # Docker initialization scripts
├── sql_migration/                # SQL migration tracking
├── metadata/                     # Metadata definitions (Atlas)
│
├── *.py                          # Root-level scripts
├── *.md                          # Documentation files
├── *.yml                         # Configuration files
└── requirements*.txt             # Dependencies
```

---

## 📂 Core Directories

### `src/` - Source Code

#### `src/business_rules/`
**Purpose**: Centralized business logic used by both pipelines and SDK.

**Files**:
- `aggregations.py` - Claims and policies aggregation rules
- `__init__.py` - Package initialization

**Key Classes**:
- `ClaimsAggregator` - Claims aggregation business rules
- `PoliciesAggregator` - Policies aggregation business rules

**Usage**: Used by `ClaimsGoldStep`, `PoliciesGoldStep`, and SDK analysts.

---

#### `src/domain/`
**Purpose**: Pure domain models and business logic processors.

**Files**:
- `claims.py` - Claim domain model and ClaimsProcessor
- `policies.py` - Policy domain model and PoliciesProcessor
- `__init__.py` - Package initialization

**Key Classes**:
- `Claim` - Claim domain model (dataclass)
- `ClaimsProcessor` - Claims business logic
- `Policy` - Policy domain model (dataclass)
- `PoliciesProcessor` - Policies business logic

**Usage**: Used by Silver steps for business rule application.

---

#### `src/mixins/`
**Purpose**: Reusable cross-cutting concerns.

**Files**:
- `logging.py` - LoggingMixin for structured logging
- `metrics.py` - MetricsMixin for performance metrics
- `validation.py` - ValidationMixin for data validation
- `__init__.py` - Package initialization

**Usage**: Mixed into pipeline classes and domain processors.

---

#### `src/pipelines/`
**Purpose**: Pipeline orchestration and step implementations.

**Files**:
- `base.py` - BasePipeline and PipelineStep base classes
- `claims_pipeline.py` - Claims pipeline implementation
- `policies_pipeline.py` - Policies pipeline implementation
- `__init__.py` - Package initialization

**Key Classes**:
- `BasePipeline` - Core pipeline orchestration
- `PipelineStep` - Base class for all steps
- `ClaimsPipeline` - Claims processing pipeline
- `PoliciesPipeline` - Policies processing pipeline

**Usage**: Main entry points for pipeline execution.

---

#### `src/sdk/`
**Purpose**: Analyst-facing interfaces.

**Files**:
- `analyst.py` - Analyst SDK classes
- `__init__.py` - Package initialization

**Key Classes**:
- `ClaimsAnalyst` - Claims analysis interface
- `PoliciesAnalyst` - Policies analysis interface
- `StopLossAnalyst` - Combined analysis interface

**Usage**: Used by analysts in Jupyter notebooks.

---

#### `src/tests/`
**Purpose**: Test suite.

**Files**:
- `test_domain.py` - Domain logic unit tests
- `test_pipelines.py` - Pipeline unit tests
- `test_transforms.py` - Transform unit tests
- `test_integration.py` - Integration tests
- `test_e2e.py` - End-to-end tests
- `__init__.py` - Package initialization

**Usage**: Run with `pytest`.

---

#### `src/transforms/`
**Purpose**: Data transformation layers.

**Files**:
- `bronze.py` - BronzeStep for data ingestion
- `silver.py` - SilverStep for data transformation
- `gold.py` - GoldStep for data aggregation
- `__init__.py` - Package initialization

**Key Classes**:
- `BronzeStep` - Data ingestion step
- `SilverStep` - Data transformation step
- `GoldStep` - Data aggregation step

**Usage**: Used by pipeline steps.

---

#### `src/utils/`
**Purpose**: Utility modules for infrastructure concerns.

**Files**:
- `atlas.py` - Apache Atlas client
- `atlas_payloads.py` - Atlas metadata payload builders
- `config_loader.py` - YAML configuration loader
- `database.py` - Database operations (SQLite)
- `db_bootstrap.py` - Database schema initialization
- `db_connection.py` - Analyst database connection utilities
- `dataframe_ops.py` - Pandas operations (isolated)
- `io.py` - I/O operations
- `validation_loader.py` - Validation configuration loader
- `__init__.py` - Package initialization

**Usage**: Infrastructure utilities used throughout the system.

---

## 📄 Configuration Files

### `pipelines_config/`
**Purpose**: YAML pipeline configuration files.

**Files**:
- `claims_pipeline.yml` - Claims pipeline configuration
- `policies_pipeline.yml` - Policies pipeline configuration

**Usage**: Loaded by `ConfigLoader` to create pipeline instances.

---

### `schemas/`
**Purpose**: Data schema definitions.

**Files**:
- `claims.yml` - Claims data schema
- `policies.yml` - Policies data schema

**Usage**: Schema validation and documentation.

---

### `config/`
**Purpose**: System configuration files.

**Files**:
- `validation.yml` - Data validation rules

**Usage**: Loaded by `ValidationLoader`.

---

## 📊 Data Files

### `data/`
**Purpose**: Sample data files.

**Files**:
- `raw_claims.json` - Sample claims data (12 records)
- `raw_policies.json` - Sample policies data (4 records)

**Usage**: Test data for pipeline execution.

---

## 📓 Notebooks

### `notebooks/`
**Purpose**: Jupyter notebooks for analysis and validation.

**Files**:
- `analyst_claims_analysis.ipynb` - Claims analysis example
- `analyst_policies_analysis.ipynb` - Policies analysis example
- `analyst_combined_analysis.ipynb` - Combined analysis example
- `claims_validation.ipynb` - Claims validation workflow
- `policy_validation.ipynb` - Policies validation workflow
- `db_connection_example.ipynb` - Database connection example

**Usage**: Examples for analysts, validation workflows.

---

## 💻 Examples

### `examples/`
**Purpose**: Code examples.

**Files**:
- `pipeline_example.py` - Pipeline usage example
- `sdk_example.py` - SDK usage example

**Usage**: Reference implementations.

---

## 🐳 Infrastructure

### `docker/`
**Purpose**: Docker initialization scripts.

**Files**:
- `postgres/init.sql` - PostgreSQL (Airflow) initialization
- `warehouse/init.sql` - Warehouse database initialization

**Usage**: Executed when Docker containers start.

---

### `airflow/`
**Purpose**: Airflow DAGs.

**Files**:
- `dags/pipelines_dag.py` - Pipeline orchestration DAGs
- `dags/README.md` - Airflow documentation

**Usage**: Scheduled pipeline execution.

---

## 📚 Documentation

### Root Level
**Purpose**: Main documentation files.

**Files**:
- `README.md` - Main project documentation
- `ARCHITECTURE.md` - System architecture
- `GETTING_STARTED.md` - Setup guide
- `EXAMPLES.md` - Code examples
- `TESTING.md` - Testing strategy
- `TESTING_CHECKLIST.md` - Verification checklist
- `DOCKER.md` - Docker overview
- `DOCKER_SETUP.md` - Docker setup
- `DOCKER_TROUBLESHOOTING.md` - Docker issues
- `VALIDATION_GUIDE.md` - Validation system
- `CHANGELOG.md` - Version history
- `RELEASE_NOTES_v0.0.1.md` - Release notes
- `CODE_REVIEW_v0.0.1.md` - Code review
- `REPO_STRUCTURE_v0.0.1.md` - This file
- `SUMMARY.md` - Project summary
- `VERIFICATION_SUMMARY.md` - Verification status
- `REPEATABLE_SETUP.md` - Repeatable verification

### `docs/`
**Purpose**: Detailed documentation.

**Files**:
- `MIGRATION_GUIDE.md` - ⭐ Agile migration guide
- `DOCUMENTATION_INDEX.md` - Complete documentation index
- `ATLAS_GUIDE.md` - Complete Atlas guide
- `ATLAS_PUBLISHING.md` - Atlas publishing how-to
- `ATLAS_QUICK_REFERENCE.md` - Atlas quick reference
- `ATLAS_TROUBLESHOOTING.md` - Atlas troubleshooting

### `sql_migration/`
**Purpose**: SQL migration tracking.

**Files**:
- `README.md` - SQL migration overview
- `MIGRATION_PROCESS.md` - Migration process
- `sql_migration_tracker.md` - Migration tracker

---

## 🔧 Scripts

### Root Level Scripts
**Purpose**: Utility and execution scripts.

**Files**:
- `run_local.py` - Execute pipelines locally
- `verify_setup.py` - Verify system setup
- `verify_data_loaded.py` - Verify data in warehouse
- `verify_atlas_entities.py` - Verify Atlas entities
- `verify_pipeline_complete.py` - Comprehensive verification
- `publish_atlas_metadata.py` - Publish Atlas metadata
- `publish_atlas_fix.py` - Fixed Atlas publishing
- `mock_atlas.py` - Mock Atlas server

**Usage**: Command-line utilities.

---

## 📦 Dependencies

### Root Level
**Purpose**: Dependency management.

**Files**:
- `requirements.txt` - Core dependencies
- `requirements-dev.txt` - Development dependencies
- `requirements-airflow.txt` - Airflow dependencies
- `setup.py` - Package setup
- `pyproject.toml` - Project configuration

---

## 🗂️ File Organization Principles

### By Layer
- **Domain**: `src/domain/` - Business logic
- **Transforms**: `src/transforms/` - Data transformations
- **Pipelines**: `src/pipelines/` - Orchestration
- **SDK**: `src/sdk/` - Analyst interfaces
- **Utils**: `src/utils/` - Infrastructure

### By Concern
- **Business Rules**: `src/business_rules/` - Centralized logic
- **Mixins**: `src/mixins/` - Cross-cutting concerns
- **Tests**: `src/tests/` - Test suite

### By Type
- **Config**: `pipelines_config/`, `schemas/`, `config/`
- **Data**: `data/`
- **Docs**: Root level, `docs/`, `sql_migration/`
- **Infrastructure**: `docker/`, `airflow/`
- **Examples**: `examples/`, `notebooks/`

---

## 📋 File Count Summary

### Source Code
- **Business Rules**: 2 files
- **Domain**: 3 files
- **Mixins**: 4 files
- **Pipelines**: 4 files
- **SDK**: 2 files
- **Tests**: 6 files
- **Transforms**: 4 files
- **Utils**: 10 files

**Total Source Files**: ~35 files

### Documentation
- **Root Level**: ~15 files
- **docs/**: 6 files
- **sql_migration/**: 3 files

**Total Documentation Files**: ~24 files

### Configuration
- **Pipeline Configs**: 2 files
- **Schemas**: 2 files
- **Config**: 1 file

**Total Config Files**: 5 files

### Scripts
- **Root Level**: 8 files

**Total Scripts**: 8 files

---

## ✅ All Files Utilized

Every file in the repository serves a purpose:
- ✅ All source files are used
- ✅ All documentation is referenced
- ✅ All scripts are functional
- ✅ All configs are loaded
- ✅ All examples demonstrate functionality

See `CODE_REVIEW_v0.0.1.md` for detailed file utilization review.

---

## 🎯 Key Files by Purpose

### Getting Started
1. `README.md` - Start here
2. `GETTING_STARTED.md` - Setup instructions
3. `verify_setup.py` - Verify installation

### Development
1. `ARCHITECTURE.md` - Understand design
2. `EXAMPLES.md` - See code examples
3. `src/pipelines/base.py` - Core framework

### Migration
1. `docs/MIGRATION_GUIDE.md` - ⭐ Migration guide
2. `sql_migration/sql_migration_tracker.md` - Track progress

### Operations
1. `run_local.py` - Execute pipelines
2. `verify_pipeline_complete.py` - Verify execution
3. `DOCKER_SETUP.md` - Production setup

---

**Version**: 0.0.1  
**Last Updated**: December 2024


