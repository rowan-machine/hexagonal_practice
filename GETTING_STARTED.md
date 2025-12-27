# Getting Started Guide

A step-by-step guide for junior developers to get started with the pipeline system.

## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher installed
- pip (Python package manager)
- Basic understanding of Python
- Text editor or IDE (VS Code, PyCharm, etc.)

## Step 1: Setup Environment

### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### Verify Installation

```bash
# Test imports
python -c "from src.sdk import ClaimsAnalyst; print('✓ SDK works')"
python -c "from src.pipelines import ClaimsPipeline; print('✓ Pipelines work')"
```

## Step 2: Understand the Structure

### Key Directories

- `src/domain/`: Business logic (no I/O)
- `src/pipelines/`: Pipeline orchestration
- `src/transforms/`: Data transformation steps
- `src/sdk/`: Analyst-friendly interfaces
- `src/utils/`: Utility functions
- `pipelines_config/`: YAML configuration files
- `data/`: Sample data files
- `notebooks/`: Jupyter notebooks for analysis

### Key Concepts

1. **Domain Models**: Pure business logic (Claim, Policy)
2. **Pipeline Steps**: Bronze (ingestion), Silver (processing), Gold (aggregation)
3. **SDK**: High-level interfaces for analysts
4. **Configuration**: Pipelines defined in YAML files

## Step 3: Run Your First Pipeline

### Using Command Line

```bash
# List available pipelines
python run_local.py --list

# Run claims pipeline
python run_local.py claims_pipeline

# Check the output
# Data will be stored in warehouse.db
```

### Using Python

Create a file `my_first_pipeline.py`:

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load configuration
config_loader = ConfigLoader()
config = config_loader.create_pipeline_config("claims_pipeline")

# Run pipeline
pipeline = ClaimsPipeline(config)
results = pipeline.run()

print(f"Executed {results['steps_executed']} steps")
```

Run it:
```bash
python my_first_pipeline.py
```

## Step 4: Use the SDK

Create a file `analyze_claims.py`:

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

# Initialize analyst
analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))

# Load claims
claims = analyst.load_claims("data/raw_claims.json")

# Calculate total
total = analyst.get_total_claims(claims)
print(f"Total claims: ${total:,.2f}")

# Filter high-value claims
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
print(f"High-value claims: {len(high_value)}")

# Convert to DataFrame
df = analyst.to_dataframe(claims)
print(f"DataFrame shape: {df.shape}")
```

Run it:
```bash
python analyze_claims.py
```

## Step 5: Explore with Notebooks

### Install Jupyter

```bash
pip install jupyter
```

### Start Jupyter

```bash
jupyter notebook
```

### Open a Notebook

1. Navigate to `notebooks/` directory
2. Open `analyst_claims_analysis.ipynb`
3. Run cells one by one (Shift+Enter)
4. Experiment with the code

## Step 6: Inspect the Database

After running pipelines, data is stored in `warehouse.db`.

### Using Python

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Query claims
claims = db.query("SELECT * FROM claims_silver LIMIT 10")
for claim in claims:
    print(claim)
```

### Using SQLite CLI

```bash
# Open database
sqlite3 warehouse.db

# Run queries
SELECT COUNT(*) FROM claims_silver;
SELECT * FROM claims_silver LIMIT 5;
.exit
```

## Step 7: Write Your First Test

Create `src/tests/test_my_code.py`:

```python
import pytest
from src.domain.claims import Claim
from datetime import datetime
from decimal import Decimal

def test_my_first_claim():
    """Test creating a claim."""
    claim = Claim(
        claim_id="TEST-001",
        policy_id="POL-001",
        member_id="MEM-001",
        claim_amount=Decimal("50000.00"),
        incurred_date=datetime.now()
    )
    
    assert claim.claim_id == "TEST-001"
    assert claim.claim_amount == Decimal("50000.00")
    assert not claim.is_paid()
```

Run it:
```bash
pytest src/tests/test_my_code.py -v
```

## Step 8: Modify a Pipeline

### Edit Configuration

Open `pipelines_config/claims_pipeline.yml` and modify:

```yaml
steps:
  - name: claims_bronze
    type: bronze
    source:
      path: "data/raw_claims.json"  # Change this path
```

### Add a Custom Step

Create `src/pipelines/my_custom_step.py`:

```python
from src.pipelines.base import PipelineStep, ExecutionContext

class MyCustomStep(PipelineStep):
    def execute(self, context: ExecutionContext):
        # Your logic here
        data = context.get("silver_data")
        # Process data
        return {"processed": True}
```

## Common Tasks

### Load and Process Data

```python
from src.sdk import ClaimsAnalyst

analyst = ClaimsAnalyst()
claims = analyst.load_claims("data/raw_claims.json")
# Process claims...
```

### Filter Data

```python
# By status
approved = analyst.get_approved_claims(claims)

# By threshold
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# By policy
by_policy = analyst.aggregate_by_policy(claims)
```

### Save Results

```python
# Save to JSON
analyst.save_claims(claims, "output/processed_claims.json")

# Convert to DataFrame and save
df = analyst.to_dataframe(claims)
df.to_csv("output/claims.csv", index=False)
```

## Troubleshooting

### Import Errors

```bash
# Ensure you're in project root
cd /path/to/hexagonal_practice

# Check Python path
python -c "import sys; print(sys.path)"
```

### Database Errors

```bash
# Check if database exists
ls -la warehouse.db

# Delete and recreate
rm warehouse.db
python run_local.py claims_pipeline
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Read the Architecture**: See `ARCHITECTURE.md`
2. **Explore Examples**: Check `examples/` directory
3. **Read Tests**: Learn from `src/tests/`
4. **Try Notebooks**: Experiment with `notebooks/`
5. **Read Code**: Start with `src/domain/` (simplest)

## Getting Help

- Check `README.md` for detailed documentation
- Review `ARCHITECTURE.md` for design principles
- Look at test files for usage examples
- Ask questions in team channels

## Practice Exercises

1. **Exercise 1**: Load claims and calculate average claim amount
2. **Exercise 2**: Filter claims by policy and save to separate files
3. **Exercise 3**: Create a custom pipeline step that adds a calculated field
4. **Exercise 4**: Write a test for your custom step
5. **Exercise 5**: Create a notebook that visualizes claim data

Good luck! 🚀

