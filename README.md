# Ringmaster Technologies - Data Pipeline System v0.0.1

Clean, interface-driven Python data pipelines for stop loss insurance marketplace operations.

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

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

3. **Verify installation:**
   ```bash
   python run_local.py --list
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

3. **Verify installation:**
   ```bash
   python -c "from src.sdk import ClaimsAnalyst; print('SDK imported successfully')"
   ```

### Docker Setup

See [Docker Guide](#running-with-docker) below.

## Running Locally

### Running Pipelines

#### Command Line

```bash
# List available pipelines
python run_local.py --list

# Run claims pipeline
python run_local.py claims_pipeline

# Run with custom database path
python run_local.py claims_pipeline --db-path warehouse.db

# Run with custom run ID
python run_local.py claims_pipeline --run-id my-run-123
```

#### Python Script

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load configuration from YAML
config_loader = ConfigLoader(config_dir="pipelines_config")
config = config_loader.create_pipeline_config("claims_pipeline", db_path="warehouse.db")

# Run pipeline
pipeline = ClaimsPipeline(config)
results = pipeline.run()

print(f"Steps executed: {results['steps_executed']}")
print(f"Steps failed: {results['steps_failed']}")
```

### Using the SDK

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

# Initialize analyst
analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))

# Load claims
claims = analyst.load_claims("data/raw_claims.json")

# Calculate totals
total = analyst.get_total_claims(claims)
print(f"Total: ${total:,.2f}")

# Filter high-value claims
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# Convert to DataFrame
df = analyst.to_dataframe(claims)
```

### Database Inspection

After running pipelines, data is stored in `warehouse.db`. You can inspect it:

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Query silver claims
claims = db.query("SELECT * FROM claims_silver LIMIT 10")
for claim in claims:
    print(claim)
```

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Access Airflow UI:**
   - Open http://localhost:8080
   - Default credentials: admin/admin (if authentication is disabled)

3. **Run pipelines in Docker:**
   ```bash
   # Execute pipeline in container
   docker-compose exec airflow python run_local.py claims_pipeline
   ```

### Docker Services

- **PostgreSQL**: Database for Airflow metadata
- **Airflow**: Orchestration service with web UI

### Environment Variables

Create a `.env` file (optional):
```env
AIRFLOW_UID=50000
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

## Usage Examples

### YAML Configuration

Pipelines are configured via YAML files in `pipelines_config/`:

**pipelines_config/claims_pipeline.yml:**
```yaml
pipeline:
  name: claims_pipeline
  description: "Stop loss insurance claims processing pipeline"
  
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
        format: "json"
    
    - name: claims_silver
      type: silver
      domain_handler: ClaimsProcessor
      config:
        approval_threshold: 100000.00
    
    - name: claims_validation
      type: validation
      data_key: silver_data
    
    - name: claims_gold
      type: gold
      aggregation:
        type: by_policy
        group_by: [policy_id]
        aggregations:
          claim_amount: sum
  
  execution:
    stop_on_error: true
    skip_completed: false
```

### SDK Usage

See the [Notebooks](#notebooks) section for detailed SDK examples.

## Notebooks

The `notebooks/` directory contains Jupyter notebooks for analysis and validation:

### Analyst Notebooks (SDK Usage)

- **`analyst_claims_analysis.ipynb`**: Claims analysis using ClaimsAnalyst SDK
- **`analyst_policies_analysis.ipynb`**: Policies analysis using PoliciesAnalyst SDK
- **`analyst_combined_analysis.ipynb`**: Combined claims and policies analysis

### Validation Notebooks

- **`claims_validation.ipynb`**: Inspect claims data from warehouse database
- **`policy_validation.ipynb`**: Inspect policies data from warehouse database

### Running Notebooks

1. **Install Jupyter:**
   ```bash
   pip install jupyter
   ```

2. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

3. **Navigate to notebooks directory and open desired notebook**

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/test_domain.py

# Run specific test
pytest src/tests/test_domain.py::TestClaim::test_claim_creation
```

### Test Structure

- **Unit Tests** (`src/tests/test_*.py`): Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete pipeline execution

### Writing Tests

See `src/tests/` for examples. Tests should:
- Be isolated (no external dependencies)
- Use descriptive names
- Test one thing at a time
- Include both positive and negative cases

## Project Structure

```
.
├── pipelines_config/     # YAML pipeline configurations
│   ├── claims_pipeline.yml
│   └── policies_pipeline.yml
├── schemas/              # Data schemas
│   ├── claims.yml
│   └── policies.yml
├── data/                 # Sample data files
│   ├── raw_claims.json
│   └── raw_policies.json
├── notebooks/           # Jupyter notebooks
│   ├── analyst_claims_analysis.ipynb
│   ├── analyst_policies_analysis.ipynb
│   ├── analyst_combined_analysis.ipynb
│   ├── claims_validation.ipynb
│   └── policy_validation.ipynb
├── src/
│   ├── domain/          # Pure business logic
│   │   ├── claims.py
│   │   └── policies.py
│   ├── pipelines/      # Orchestration
│   │   ├── base.py
│   │   ├── claims_pipeline.py
│   │   └── policies_pipeline.py
│   ├── transforms/     # Data transformation
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold.py
│   ├── sdk/            # Analyst interfaces
│   │   └── analyst.py
│   ├── utils/          # Utilities
│   │   ├── io.py
│   │   ├── dataframe_ops.py
│   │   ├── config_loader.py
│   │   └── database.py
│   └── mixins/         # Reusable behaviors
│       ├── logging.py
│       ├── metrics.py
│       └── validation.py
├── src/tests/          # Test suite
│   ├── test_domain.py
│   ├── test_pipelines.py
│   └── test_transforms.py
├── run_local.py        # Local pipeline runner
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
├── docker-compose.yml  # Docker configuration
└── README.md          # This file
```

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints for all public APIs
- Write docstrings for all classes and public methods
- Keep functions small and focused

### Adding New Features

1. **Domain Logic**: Add to `src/domain/` (no I/O)
2. **Pipeline Steps**: Add to `src/transforms/` or create custom step
3. **SDK Methods**: Add to `src/sdk/analyst.py`
4. **Configuration**: Update YAML files in `pipelines_config/`

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

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure you're in the project root
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database locked:**
- Close any open database connections
- Restart the application

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Notebook import errors:**
- Ensure you're running notebooks from the `notebooks/` directory
- Check that `sys.path.insert(0, str(Path('..').resolve()))` is in the setup cell

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit a pull request

## License

[Add your license here]

## Support

For questions or issues, please [create an issue] or contact the development team.
