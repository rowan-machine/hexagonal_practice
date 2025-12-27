# Examples

Complete guide to using the Ringmaster Pipelines system with runnable examples and code snippets.

## Table of Contents

- [Quick Start](#quick-start)
- [Runnable Examples](#runnable-examples)
- [Code Examples](#code-examples)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

## Quick Start

> **📊 Are you an analyst?** See [notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md) for a complete guide tailored to analysts.  
> **📖 Need API details?** See [docs/SDK_API_REFERENCE.md](../docs/SDK_API_REFERENCE.md) for complete SDK API reference.

1. **Install the package:**
   ```bash
   # From the project root directory
   pip install -e .
   ```
   
   **Important:** Examples require the package to be installed so they can import from `src`. If you get `ModuleNotFoundError: No module named 'src'`, run `pip install -e .` first.

2. **Run an example:**
   ```bash
   # From the project root directory
   python examples/pipeline_example.py
   # or
   python examples/sdk_example.py
   ```

## Runnable Examples

### Pipeline Example (`pipeline_example.py`)

Demonstrates how to run pipelines using YAML configuration files.

**What it shows:**
- Loading pipeline configuration from YAML
- Running claims and policies pipelines
- Using custom run IDs

**Usage:**
```bash
python examples/pipeline_example.py
```

**What you'll see:**
- Claims pipeline execution
- Policies pipeline execution
- Pipeline results (steps executed, steps failed)

**Prerequisites:**
- `config/claims_pipeline.yml` must exist
- `config/policies_pipeline.yml` must exist
- `data/raw_claims.json` and `data/raw_policies.json` should exist (or pipeline will run with empty data)

**Code Structure:**
```python
# 1. Load configuration
config_loader = ConfigLoader(config_dir="config")
config = config_loader.create_pipeline_config("claims_pipeline")

# 2. Create pipeline
pipeline = ClaimsPipeline(config)

# 3. Run pipeline
results = pipeline.run()
```

**Customization:**
- Change `config_dir` to use different configuration directory
- Add `run_id` parameter for custom run IDs
- Modify `db_path` to use different database

### SDK Example (`sdk_example.py`)

Demonstrates how analysts can use the SDK for data analysis.

**What it shows:**
- Loading claims and policies data
- Filtering and aggregating data
- Converting to DataFrames
- Saving processed data

**Usage:**
```bash
python examples/sdk_example.py
```

**What you'll see:**
- Claims analysis (totals, approved claims, high-value claims)
- Policies analysis (active policies, employer policies, coverage)
- Combined analysis (claims by policy, coverage utilization)

**Prerequisites:**
- `data/raw_claims.json` must exist
- `data/raw_policies.json` must exist

**Code Structure:**
```python
# 1. Create analyst
analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))

# 2. Load data
claims = analyst.load_claims("data/raw_claims.json")

# 3. Analyze
total = analyst.get_total_claims(claims)
approved = analyst.get_approved_claims(claims)
by_policy = analyst.aggregate_by_policy(claims)

# 4. Convert to DataFrame
df = analyst.to_dataframe(claims)
```

**Customization:**
- Adjust `approval_threshold` for different approval criteria
- Change file paths to use different data sources
- Modify thresholds for high-value claims filtering

## Code Examples

### Pipeline Execution

#### Run Pipeline from YAML

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load configuration
config_loader = ConfigLoader(config_dir="config")
config = config_loader.create_pipeline_config("claims_pipeline", db_path="warehouse.db")

# Run pipeline
pipeline = ClaimsPipeline(config)
results = pipeline.run()

print(f"Steps executed: {results['steps_executed']}")
print(f"Steps failed: {results['steps_failed']}")
```

#### Create Custom Pipeline

```python
from src.pipelines.base import PipelineConfig, ExecutionContext
from src.pipelines.claims_pipeline import ClaimsBronzeStep, ClaimsSilverStep
from src.pipelines import ClaimsPipeline
from uuid import uuid4

# Define steps
steps = [
    ClaimsBronzeStep(source_path="data/raw_claims.json"),
    ClaimsSilverStep(approval_threshold=100000.00)
]

# Create context
context = ExecutionContext(
    pipeline_name="my_custom_pipeline",
    run_id=str(uuid4())
)

# Create config
config = PipelineConfig(
    steps=steps,
    context=context,
    stop_on_error=True
)

# Run
pipeline = ClaimsPipeline(config)
results = pipeline.run()
```

### SDK Usage

#### Claims Analysis

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

# Initialize
analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))

# Load claims
claims = analyst.load_claims("data/raw_claims.json")

# Calculate totals
total = analyst.get_total_claims(claims)
print(f"Total: ${total:,.2f}")

# Filter
approved = analyst.get_approved_claims(claims)
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# Aggregate
by_policy = analyst.aggregate_by_policy(claims)
by_member = analyst.aggregate_by_member(claims)

# Convert to DataFrame
df = analyst.to_dataframe(claims)

# Save
analyst.save_claims(approved, "output/approved_claims.json")
```

#### Policies Analysis

```python
from src.sdk import PoliciesAnalyst

# Initialize
analyst = PoliciesAnalyst()

# Load policies
policies = analyst.load_policies("data/raw_policies.json")

# Filter
active = analyst.get_active_policies(policies)
employer_policies = analyst.get_employer_policies(policies, "EMP-001")

# Calculate
total_coverage = analyst.get_total_coverage(policies)

# Convert to DataFrame
df = analyst.to_dataframe(policies)
```

#### Combined Analysis

```python
from src.sdk import StopLossAnalyst
from decimal import Decimal

# Initialize
analyst = StopLossAnalyst(approval_threshold=Decimal("100000.00"))

# Load data
claims = analyst.claims_analyst.load_claims("data/raw_claims.json")
policies = analyst.policies_analyst.load_policies("data/raw_policies.json")

# Analyze
analysis = analyst.analyze_claims_by_policy(claims, policies)
utilization = analyst.calculate_coverage_utilization(claims, policies)
```

### Database Operations

#### Query Data

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Query all claims
claims = db.query("SELECT * FROM claims_silver")

# Query with parameters
claims = db.query(
    "SELECT * FROM claims_silver WHERE status = ?",
    ("approved",)
)

# Count records
count = db.query("SELECT COUNT(*) as count FROM claims_silver")
print(f"Total claims: {count[0]['count']}")
```

#### Insert Data

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Insert claims
claims_data = [
    {
        "claim_id": "CLM-001",
        "policy_id": "POL-001",
        "member_id": "MEM-001",
        "claim_amount": 50000.00,
        "incurred_date": "2024-01-15T00:00:00",
        "status": "approved",
        "claim_type": "medical"
    }
]

db.insert_claims_silver(claims_data)
```

### Custom Steps

#### Create a Custom Bronze Step

```python
from src.transforms.bronze import BronzeStep
from src.pipelines.base import ExecutionContext
from typing import Any, Dict

class MyCustomBronzeStep(BronzeStep):
    def __init__(self, source_path: str = ""):
        super().__init__(name="my_bronze", source_path=source_path)
    
    def _load_raw_data(self) -> Any:
        # Custom loading logic
        # Could load from API, database, etc.
        return []
    
    def _apply_basic_cleaning(self, raw_data: Any) -> Any:
        # Custom cleaning logic
        return raw_data
```

#### Create a Custom Silver Step

```python
from src.transforms.silver import SilverStep
from src.pipelines.base import ExecutionContext
from typing import Any

class MyCustomSilverStep(SilverStep):
    def __init__(self):
        super().__init__(name="my_silver", domain_handler=None)
    
    def _apply_business_logic(self, bronze_data: Any) -> Any:
        # Custom business logic
        processed = []
        for item in bronze_data:
            # Process each item
            processed.append(item)
        return processed
```

#### Create a Custom Gold Step

```python
from src.transforms.gold import GoldStep
from src.pipelines.base import ExecutionContext
from typing import Any, Dict, List

class MyCustomGoldStep(GoldStep):
    def __init__(self):
        super().__init__(name="my_gold", aggregation_config={})
    
    def _apply_aggregations(self, silver_data: Any) -> Any:
        # Custom aggregation logic
        # Group, sum, average, etc.
        return silver_data
    
    def _create_summary_stats(self, data: Any) -> Dict[str, Any]:
        # Custom summary statistics
        return {"total": len(data)}
```

### Testing

#### Unit Test Example

```python
import pytest
from src.domain.claims import Claim, ClaimsProcessor
from datetime import datetime
from decimal import Decimal

def test_claim_creation():
    claim = Claim(
        claim_id="TEST-001",
        policy_id="POL-001",
        member_id="MEM-001",
        claim_amount=Decimal("50000.00"),
        incurred_date=datetime.now()
    )
    
    assert claim.claim_id == "TEST-001"
    assert claim.claim_amount == Decimal("50000.00")

def test_claims_processor():
    processor = ClaimsProcessor()
    raw_claims = [{"claim_id": "CLM-001", ...}]
    
    claims = processor.process(raw_claims)
    assert len(claims) == 1
```

#### Integration Test Example

```python
import pytest
from src.pipelines import ClaimsPipeline, PipelineConfig, ExecutionContext
from src.pipelines.claims_pipeline import ClaimsBronzeStep, ClaimsSilverStep
from uuid import uuid4

def test_pipeline_integration():
    steps = [
        ClaimsBronzeStep(source_path="test_data.json"),
        ClaimsSilverStep()
    ]
    
    context = ExecutionContext(
        pipeline_name="test",
        run_id=str(uuid4())
    )
    
    config = PipelineConfig(steps=steps, context=context)
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    
    assert results["steps_executed"] == 2
```

## Common Use Cases

### Running a Pipeline Programmatically

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load and run
config_loader = ConfigLoader()
config = config_loader.create_pipeline_config("claims_pipeline")
pipeline = ClaimsPipeline(config)
results = pipeline.run()

# Check results
if results['steps_failed'] == 0:
    print("Pipeline succeeded!")
else:
    print(f"Pipeline had {results['steps_failed']} failures")
```

### Analyzing Claims Data

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

# Initialize
analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))

# Load from file
claims = analyst.load_claims("data/raw_claims.json")

# Or load from database
claims = analyst.load_from_database()

# Analyze
stats = analyst.get_summary_statistics(claims)
print(f"Total claims: {stats['total_claims']}")
print(f"Total amount: ${stats['total_amount']:,.2f}")
```

### Working with Policies

```python
from src.sdk import PoliciesAnalyst

# Initialize
analyst = PoliciesAnalyst()

# Load policies
policies = analyst.load_policies("data/raw_policies.json")

# Filter
active = analyst.get_active_policies(policies)
employer_policies = analyst.get_employer_policies(policies, "EMP-001")

# Calculate
total_coverage = analyst.get_total_coverage(policies)
```

### Common Patterns

#### Error Handling

```python
try:
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
except Exception as e:
    print(f"Pipeline failed: {e}")
    # Handle error
```

#### Logging

```python
from src.mixins.logging import LoggingMixin

class MyClass(LoggingMixin):
    def __init__(self):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
    
    def do_something(self):
        self.log_info("Starting operation")
        try:
            # Do work
            self.log_info("Operation completed")
        except Exception as e:
            self.log_error("Operation failed", error=e)
```

#### Metrics

```python
from src.mixins.metrics import MetricsMixin
import time

class MyClass(MetricsMixin):
    def process_data(self, data):
        start_time = time.time()
        
        # Process data
        result = process(data)
        
        duration = time.time() - start_time
        self.record_timing("process_duration", duration)
        self.record_count("records_processed", len(data))
        
        return result
```

### Tips and Tricks

#### Working with Decimals

```python
from decimal import Decimal

# Always use Decimal for money
amount = Decimal("100000.00")  # ✓ Correct
amount = 100000.00  # ✗ Avoid (floating point)

# Calculations
total = amount1 + amount2
percentage = (amount / total) * 100
```

#### Working with Dates

```python
from datetime import datetime

# Parse ISO format
date = datetime.fromisoformat("2024-01-15T00:00:00")

# Format for display
formatted = date.strftime("%Y-%m-%d")

# Compare dates
if date1 < date2:
    print("date1 is earlier")
```

#### DataFrame Operations

```python
import pandas as pd

# Convert to DataFrame
df = analyst.to_dataframe(claims)

# Filter
filtered = df[df['claim_amount'] > 50000]

# Group by
grouped = df.groupby('policy_id')['claim_amount'].sum()

# Save
df.to_csv("output.csv", index=False)
```

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Install package in editable mode (from project root)
pip install -e .

# Verify installation
python -c "import src; print('Package installed successfully')"
```

**Note:** You must run `pip install -e .` from the project root directory before running any examples.

### File Not Found Errors

**Error:** `FileNotFoundError: data/raw_claims.json`

**Solution:**
- Ensure data files exist in the `data/` directory
- Or modify the file paths in the example to point to your data

### Database Errors

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
- Close any open database connections
- Ensure no other process is using the database
- Try using a different database path

## Next Steps

**Examples working?** Continue learning:

1. **[notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md)** → ⭐ Complete guide for analysts
2. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Understand the architecture patterns you just saw
3. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create your own pipeline configurations
4. **[schemas/README.md](../schemas/README.md)** → Define data schemas for your data

**Ready to build something?**

1. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create a new pipeline
2. **[config/VALIDATION_GUIDE.md](../config/VALIDATION_GUIDE.md)** → Add validation to your pipeline
3. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Write tests for your code

**Want to go deeper?**

1. **[docs/BEST_PRACTICES.md](../docs/BEST_PRACTICES.md)** → Follow best practices
2. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Start contributing
3. **[sql_migration/README.md](../sql_migration/README.md)** → Migrate SQL to Python

## Related Documentation

- **[notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md)** - ⭐ Complete guide for analysts
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Setup and installation guide
- **[README.md](../README.md)** - Project overview and architecture
- **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** - Detailed design principles
- **[docs/README.md](../docs/README.md)** - Complete documentation index
- **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** - Pipeline configuration guide
