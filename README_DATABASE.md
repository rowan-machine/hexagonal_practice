# Database Integration Guide

## Overview

The pipeline system now integrates with SQLite (`warehouse.db`) to store data at each layer (bronze, silver, gold) for inspection and validation.

## Database Schema

### Claims Tables

- **claims_bronze**: Raw claims data after initial ingestion
- **claims_silver**: Processed claims with business logic applied
- **claims_gold**: Aggregated claims by policy

### Policies Tables

- **policies_bronze**: Raw policies data after initial ingestion
- **policies_silver**: Processed policies with business logic applied
- **policies_gold**: Aggregated policies by employer

## Running Pipelines

### Command Line

```bash
# Run claims pipeline (defaults to warehouse.db)
python run_local.py claims_pipeline

# Run with custom database path
python run_local.py claims_pipeline --db-path warehouse.db

# Run policies pipeline
python run_local.py policies_pipeline
```

### Python

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

config_loader = ConfigLoader()
config = config_loader.create_pipeline_config("claims_pipeline", db_path="warehouse.db")
pipeline = ClaimsPipeline(config)
results = pipeline.run()
```

## Inspecting Data

### Using Validation Notebooks

1. **Claims Validation**: `notebooks/claims_validation.ipynb`
   - Inspect bronze, silver, and gold layers
   - Data quality checks
   - Claims by policy analysis
   - High-value claims identification

2. **Policy Validation**: `notebooks/policy_validation.ipynb`
   - Inspect bronze, silver, and gold layers
   - Data quality checks
   - Policies by employer analysis
   - Coverage analysis

### Using Python

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Query silver claims
claims = db.query("SELECT * FROM claims_silver LIMIT 10")

# Query gold aggregations
aggregations = db.query("SELECT * FROM claims_gold")
```

## Database Structure

Each table includes:
- **Bronze tables**: Raw data + `created_at` timestamp
- **Silver tables**: Processed data + `created_at` and `processed_at` timestamps
- **Gold tables**: Aggregated data + `created_at` timestamp

Indexes are created on:
- `claims_silver.policy_id`
- `claims_silver.member_id`
- `claims_silver.status`

## Data Flow

1. **Bronze Step**: Reads from JSON → Writes to `*_bronze` table
2. **Silver Step**: Reads from context → Processes with domain logic → Writes to `*_silver` table
3. **Gold Step**: Reads from context → Aggregates → Writes to `*_gold` table

## Notes

- Database is automatically initialized on first use
- Tables use `INSERT OR REPLACE` to handle re-runs
- All timestamps are automatically managed
- Database path can be configured per pipeline run

