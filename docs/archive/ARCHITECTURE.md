# Ringmaster Technologies - Data Pipeline Architecture v0.0.1

## Overview
Clean, interface-driven Python data pipelines for stop loss insurance marketplace operations. 
Emphasizes encapsulation, abstraction, and testability over clever tricks.

## Core Principles

### 1. Separation of Concerns
- **src/domain**: Pure business logic, no I/O dependencies
- **src/pipelines**: Orchestration only, delegates to domain and transforms
- **src/transforms**: Data transformation layer (bronze, silver, gold, validation, aggregation)
- **src/sdk**: Analyst-facing convenience interfaces
- **src/utils**: Cross-cutting utilities (I/O, data operations)
- **src/mixins**: Reusable behaviors (logging, metrics, validation)

### 2. Design Patterns
- **Stateful Classes**: Pipeline state managed through class attributes, not globals
- **Configuration-Driven**: Pipelines defined by config, not copy-pasted code
- **Interface-Driven**: Clear contracts between layers via abstract base classes
- **Composable Steps**: Reusable pipeline steps (bronze, silver, gold, etc.)

### 3. Constraints
- No pandas outside transform layer
- All public APIs must be typed
- No framework-heavy dependencies (Airflow for orchestration only)
- Business logic in Python classes, not notebooks or scripts

### 4. Pipeline Structure
```
BasePipeline (abstract)
  ├── Execution context (state management)
  ├── Step registry (bronze, silver, gold, validation, aggregation)
  └── Lifecycle hooks (before_run, after_run, on_error)

Concrete Pipelines
  ├── ClaimsPipeline
  └── PoliciesPipeline
```

### 5. Domain Models
- **Claims**: Stop loss claim processing logic
- **Policies**: Policy management and validation

### 6. Transform Layers
- **Bronze**: Raw data ingestion and basic cleaning
- **Silver**: Business rule application and enrichment
- **Gold**: Aggregated, analysis-ready datasets
- **Validation**: Data quality checks and constraints
- **Aggregation**: Summary statistics and rollups

## Testing Strategy
- Unit tests for domain logic (no I/O mocking complexity)
- Integration tests for pipeline orchestration
- Transform tests verify data shape and business rules

## Usage Pattern

### YAML Configuration
Pipelines are configured via YAML files in `pipelines_config/`:

```yaml
pipeline:
  name: claims_pipeline
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
    - name: claims_silver
      type: silver
      domain_handler: ClaimsProcessor
  execution:
    stop_on_error: true
```

### Programmatic Usage
```python
# Load from YAML
from src.utils.config_loader import ConfigLoader
config_loader = ConfigLoader()
config = config_loader.create_pipeline_config("claims_pipeline")
pipeline = ClaimsPipeline(config)
pipeline.run()
```

### Command Line
```bash
python run_local.py claims_pipeline
```
