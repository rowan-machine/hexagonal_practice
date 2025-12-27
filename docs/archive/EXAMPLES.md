# Code Examples and Snippets

Quick reference guide with common code examples and snippets.

## Table of Contents

- [Pipeline Execution](#pipeline-execution)
- [SDK Usage](#sdk-usage)
- [Database Operations](#database-operations)
- [Custom Steps](#custom-steps)
- [Testing](#testing)

## Pipeline Execution

### Run Pipeline from YAML

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load configuration
config_loader = ConfigLoader(config_dir="pipelines_config")
config = config_loader.create_pipeline_config("claims_pipeline", db_path="warehouse.db")

# Run pipeline
pipeline = ClaimsPipeline(config)
results = pipeline.run()

print(f"Steps executed: {results['steps_executed']}")
print(f"Steps failed: {results['steps_failed']}")
```

### Create Custom Pipeline

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

## SDK Usage

### Claims Analysis

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

### Policies Analysis

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

### Combined Analysis

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

## Database Operations

### Query Data

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

### Insert Data

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

## Custom Steps

### Create a Custom Bronze Step

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

### Create a Custom Silver Step

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

### Create a Custom Gold Step

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

## Testing

### Unit Test Example

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

### Integration Test Example

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

## Common Patterns

### Error Handling

```python
try:
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
except Exception as e:
    print(f"Pipeline failed: {e}")
    # Handle error
```

### Logging

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

### Metrics

```python
from src.mixins.metrics import MetricsMixin

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

## Tips and Tricks

### Working with Decimals

```python
from decimal import Decimal

# Always use Decimal for money
amount = Decimal("100000.00")  # ✓ Correct
amount = 100000.00  # ✗ Avoid (floating point)

# Calculations
total = amount1 + amount2
percentage = (amount / total) * 100
```

### Working with Dates

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

### DataFrame Operations

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

For more examples, see the notebooks in the `notebooks/` directory.

