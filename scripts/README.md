# Helper Scripts

This directory contains utility scripts for running pipelines, verification, and maintenance tasks.

## Scripts

### Git Setup

#### `setup_git_branches.sh` / `setup_git_branches.ps1`

Setup script to create `develop` and `test` branches for the Git workflow.

**Usage:**
```bash
# Bash (Linux/Mac/Git Bash)
bash scripts/setup_git_branches.sh

# PowerShell (Windows)
powershell -ExecutionPolicy Bypass -File scripts/setup_git_branches.ps1

# Or use Makefile
make setup-branches
```

**What it does:**
- Creates `develop` branch if it doesn't exist
- Creates `test` branch if it doesn't exist
- Pushes branches to remote
- Returns to original branch

**See also:** [docs/GIT_WORKFLOW.md](../docs/GIT_WORKFLOW.md)

## Scripts

### Pipeline Execution

#### `run_local.py`

Main script for executing pipelines locally from YAML configuration.

**Usage:**
```bash
# List available pipelines
python scripts/run_local.py --list

# Run a pipeline
python scripts/run_local.py claims_pipeline

# Run with custom database path
python scripts/run_local.py claims_pipeline --db-path custom.db

# Run with custom run ID
python scripts/run_local.py claims_pipeline --run-id my-run-123
```

**Options:**
- `--list`: List all available pipelines
- `--db-path`: Path to SQLite database (default: `warehouse.db`)
- `--run-id`: Custom run ID for this execution
- `--config-dir`: Directory containing pipeline configs (default: `config`)

### Verification Scripts

#### `verify_setup.py`

Verifies that the system is properly set up and all dependencies are available.

**Usage:**
```bash
python scripts/verify_setup.py
```

**Checks:**
- All key imports work
- Database can be initialized
- Required data files exist
- Configuration files are valid

#### `verify_data_loaded.py`

Verifies that data has been loaded into the warehouse database.

**Usage:**
```bash
# Check SQLite database
python scripts/verify_data_loaded.py

# Check PostgreSQL (Docker)
python scripts/verify_data_loaded.py --postgres
```

**Checks:**
- Data exists in bronze, silver, and gold tables
- Record counts match expectations
- Data quality checks

#### `verify_atlas_entities.py`

Verifies that metadata has been published to Apache Atlas.

**Usage:**
```bash
python scripts/verify_atlas_entities.py
```

**Checks:**
- All expected entities exist in Atlas
- Entity relationships are correct
- Metadata is complete

#### `verify_pipeline_complete.py`

Comprehensive verification script that checks all aspects of pipeline execution.

**Usage:**
```bash
python scripts/verify_pipeline_complete.py
```

**Checks:**
- Setup verification
- Data loading verification
- Atlas entity verification
- Pipeline execution status

### Atlas Scripts

#### `publish_atlas_metadata.py`

Publishes all metadata to Apache Atlas for data lineage and governance.

**Usage:**
```bash
# Default Atlas URL (http://localhost:21000)
python scripts/publish_atlas_metadata.py

# Custom Atlas URL
python scripts/publish_atlas_metadata.py --atlas-url http://atlas.example.com:21000

# Dry run (validate without publishing)
python scripts/publish_atlas_metadata.py --dry-run
```

**Options:**
- `--atlas-url`: Custom Atlas server URL
- `--dry-run`: Validate payloads without publishing
- `--username`: Atlas username (default: admin)
- `--password`: Atlas password (default: admin)

#### `publish_atlas_fix.py`

Fixed version of Atlas publishing with improved error handling and authentication.

**Usage:**
```bash
python scripts/publish_atlas_fix.py
```

**Features:**
- Automatic retry with default credentials
- Better error messages
- Improved authentication handling

#### `mock_atlas.py`

Mock Apache Atlas server for local testing and development.

**Usage:**
```bash
# Start mock server (default: localhost:21000)
python scripts/mock_atlas.py

# Custom host and port
python scripts/mock_atlas.py --host localhost --port 21000
```

**Features:**
- Simulates Atlas API endpoints
- Prints received metadata to console
- Useful for testing without Atlas server

## Running Scripts

### From Project Root

All scripts should be run from the project root directory:

```bash
# From project root
python scripts/run_local.py claims_pipeline
```

### In Docker

When running in Docker containers:

```bash
# Execute script in Airflow container
docker-compose exec airflow python scripts/run_local.py claims_pipeline

# With custom database path
docker-compose exec airflow python scripts/run_local.py claims_pipeline --db-path /opt/airflow/warehouse.db
```

## Script Organization

Scripts are organized by purpose:
- **Pipeline execution**: `run_local.py`
- **Verification**: `verify_*.py`
- **Atlas**: `publish_*.py`, `mock_atlas.py`

## Adding New Scripts

When adding new scripts:

1. **Place in `scripts/` directory**
2. **Add shebang** (if executable): `#!/usr/bin/env python`
3. **Add docstring** with usage examples
4. **Update this README** with script documentation
5. **Follow naming conventions**: Use descriptive names with underscores

## Best Practices

1. **Error Handling**: All scripts should handle errors gracefully
2. **Logging**: Use logging mixin for consistent logging
3. **Documentation**: Include usage examples in docstrings
4. **CLI Arguments**: Use `argparse` for command-line arguments
5. **Exit Codes**: Return appropriate exit codes (0 for success, non-zero for errors)

## Next Steps

**Scripts working?** Continue with:

1. **[examples/README.md](../examples/README.md)** → Learn to use the SDK and pipelines
2. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create your own pipelines
3. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup guide

**Running in Docker?**

1. **[DOCKER.md](../DOCKER.md)** → Complete Docker guide
2. **[docs/ATLAS_GUIDE.md](../docs/ATLAS_GUIDE.md)** → Set up Apache Atlas
3. **[airflow/dags/README.md](../airflow/dags/README.md)** → Airflow DAGs

**Troubleshooting?**

1. **[DOCKER.md](../DOCKER.md)** → Troubleshooting section
2. **[docs/ATLAS_TROUBLESHOOTING.md](../docs/ATLAS_TROUBLESHOOTING.md)** → Atlas issues
3. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Troubleshooting section

## Related Documentation

- **[Getting Started](../GETTING_STARTED.md)** - Setup and installation
- **[Docker Guide](../DOCKER.md)** - Running in Docker
- **[Atlas Guide](../docs/ATLAS_GUIDE.md)** - Apache Atlas documentation

