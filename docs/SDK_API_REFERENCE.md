# SDK API Reference

Complete API reference for the Ringmaster Pipelines SDK.

> **📚 This is the technical API reference. For usage guides and examples, see [notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md).**

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [ClaimsAnalyst](#claimsanalyst)
- [PoliciesAnalyst](#policiesanalyst)
- [StopLossAnalyst](#stoplossanalyst)
- [Data Types](#data-types)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

The SDK provides three main classes for data analysis:

- **`ClaimsAnalyst`** - Analyze claims data
- **`PoliciesAnalyst`** - Analyze policies data
- **`StopLossAnalyst`** - Combined claims and policies analysis

All classes follow the same pattern:
1. Initialize with database path
2. Load data from database
3. Use analysis methods
4. Convert to DataFrame for further analysis

## Installation

```python
# Import SDK classes
from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
```

**Note**: Ensure package is installed: `pip install -e .`

## Accessing Documentation

### Using Python's Built-in Help

Python provides built-in documentation access:

```python
# View class documentation
help(ClaimsAnalyst)

# View method documentation
help(ClaimsAnalyst.get_total_claims)

# View in interactive Python
from src.sdk import ClaimsAnalyst
ClaimsAnalyst.get_total_claims.__doc__
```

### Using pydoc (Command Line)

```bash
# View module documentation
python -m pydoc src.sdk.analyst

# Start web server for browsing
python -m pydoc -p 8080
# Then open http://localhost:8080 in browser
```

### Using IPython/Jupyter

```python
# In Jupyter/IPython
ClaimsAnalyst?  # View class info
ClaimsAnalyst.get_total_claims?  # View method info
ClaimsAnalyst.get_total_claims??  # View source code
```

## ClaimsAnalyst

Public API for claims analysis.

### Class Definition

```python
class ClaimsAnalyst(LoggingMixin):
    """Public API for claims analysis."""
```

### Constructor

#### `__init__(db_path: str = "warehouse.db", approval_threshold: Optional[Decimal] = None)`

Initialize ClaimsAnalyst.

**Parameters:**
- `db_path` (str, optional): Path to SQLite database. Default: `"warehouse.db"`
- `approval_threshold` (Decimal, optional): Threshold for claim approval. Default: `Decimal("100000.00")`

**Example:**
```python
from decimal import Decimal
from src.sdk import ClaimsAnalyst

# Basic initialization
analyst = ClaimsAnalyst()

# With custom database path
analyst = ClaimsAnalyst(db_path="custom.db")

# With custom approval threshold
analyst = ClaimsAnalyst(approval_threshold=Decimal("50000.00"))
```

### Methods

#### `load_from_database(layer: str = "silver", limit: Optional[int] = None) -> List[Claim]`

Load claims from database.

**Parameters:**
- `layer` (str): Data layer to load from. Options: `"bronze"`, `"silver"`, `"gold"`. Default: `"silver"`
- `limit` (int, optional): Maximum number of records to load. Default: `None` (load all)

**Returns:**
- `List[Claim]`: List of Claim domain objects

**Raises:**
- `ValueError`: If layer is not "bronze", "silver", or "gold"

**Example:**
```python
# Load all silver claims
claims = analyst.load_from_database()

# Load first 100 bronze claims
claims = analyst.load_from_database(layer="bronze", limit=100)

# Load all gold claims (returns empty - gold is aggregated)
claims = analyst.load_from_database(layer="gold")
```

**Notes:**
- This is the **primary method** analysts should use to load data
- Gold layer returns empty list (use silver for individual claims)
- Data is automatically validated through domain layer

---

#### `get_total_claims(claims: List[Claim]) -> Decimal`

Calculate total claim amount.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `Decimal`: Total amount of all claims

**Example:**
```python
claims = analyst.load_from_database()
total = analyst.get_total_claims(claims)
print(f"Total: ${total:,.2f}")
```

---

#### `get_approved_claims(claims: List[Claim]) -> List[Claim]`

Filter approved claims.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `List[Claim]`: List of approved claims

**Example:**
```python
claims = analyst.load_from_database()
approved = analyst.get_approved_claims(claims)
print(f"Approved: {len(approved)}")
```

---

#### `get_paid_claims(claims: List[Claim]) -> List[Claim]`

Filter paid claims.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `List[Claim]`: List of paid claims

**Example:**
```python
claims = analyst.load_from_database()
paid = analyst.get_paid_claims(claims)
print(f"Paid: {len(paid)}")
```

---

#### `get_pending_claims(claims: List[Claim]) -> List[Claim]`

Filter pending claims.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `List[Claim]`: List of pending claims

**Example:**
```python
claims = analyst.load_from_database()
pending = analyst.get_pending_claims(claims)
print(f"Pending: {len(pending)}")
```

---

#### `get_high_value_claims(claims: List[Claim], threshold: Optional[Decimal] = None) -> List[Claim]`

Filter claims exceeding a threshold.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects
- `threshold` (Decimal, optional): Amount threshold. If None, uses instance's approval_threshold

**Returns:**
- `List[Claim]`: List of high-value claims

**Example:**
```python
from decimal import Decimal

claims = analyst.load_from_database()
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
print(f"High-value claims: {len(high_value)}")
```

---

#### `aggregate_by_policy(claims: List[Claim]) -> Dict[str, List[Claim]]`

Group claims by policy ID.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `Dict[str, List[Claim]]`: Dictionary mapping policy_id to list of claims

**Example:**
```python
claims = analyst.load_from_database()
by_policy = analyst.aggregate_by_policy(claims)

for policy_id, policy_claims in by_policy.items():
    print(f"Policy {policy_id}: {len(policy_claims)} claims")
```

**Note:** For aggregation statistics, use `get_policy_aggregations()` instead.

---

#### `get_policy_aggregations(claims: List[Claim]) -> List[Dict[str, Any]]`

Get aggregated statistics by policy (same logic as gold layer).

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `List[Dict[str, Any]]`: List of aggregated dictionaries with policy statistics

**Example:**
```python
claims = analyst.load_from_database()
aggregations = analyst.get_policy_aggregations(claims)

for agg in aggregations:
    print(f"Policy {agg['policy_id']}: ${agg['total_claims']:,.2f}")
```

**Note:** Uses centralized business rules to ensure consistency with pipeline.

---

#### `aggregate_by_member(claims: List[Claim]) -> Dict[str, List[Claim]]`

Group claims by member ID.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `Dict[str, List[Claim]]`: Dictionary mapping member_id to list of claims

**Example:**
```python
claims = analyst.load_from_database()
by_member = analyst.aggregate_by_member(claims)

for member_id, member_claims in by_member.items():
    print(f"Member {member_id}: {len(member_claims)} claims")
```

---

#### `get_summary_statistics(claims: List[Claim]) -> Dict[str, Any]`

Calculate summary statistics for claims.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `Dict[str, Any]`: Dictionary with summary statistics:
  - `total_claims` (int): Total number of claims
  - `total_amount` (float): Total claim amount
  - `average_amount` (float): Average claim amount
  - `by_status` (Dict[str, int]): Count by status
  - `by_type` (Dict[str, int]): Count by claim type

**Example:**
```python
claims = analyst.load_from_database()
stats = analyst.get_summary_statistics(claims)

print(f"Total: {stats['total_claims']} claims")
print(f"Amount: ${stats['total_amount']:,.2f}")
print(f"Average: ${stats['average_amount']:,.2f}")
print(f"By status: {stats['by_status']}")
```

---

#### `to_dataframe(claims: List[Claim]) -> Any`

Convert claims to pandas DataFrame.

**Parameters:**
- `claims` (List[Claim]): List of Claim objects

**Returns:**
- `pandas.DataFrame`: DataFrame with claim data

**Example:**
```python
import pandas as pd

claims = analyst.load_from_database()
df = analyst.to_dataframe(claims)

# Now use pandas for analysis
df.groupby('policy_id')['claim_amount'].sum()
df[df['status'] == 'approved']
```

**DataFrame Columns:**
- `claim_id` (str)
- `policy_id` (str)
- `member_id` (str)
- `claim_amount` (float)
- `incurred_date` (str, ISO format)
- `paid_date` (str, ISO format, nullable)
- `status` (str)
- `claim_type` (str)

---

## PoliciesAnalyst

Public API for policies analysis.

### Class Definition

```python
class PoliciesAnalyst(LoggingMixin):
    """Public API for policies analysis."""
```

### Constructor

#### `__init__(db_path: str = "warehouse.db")`

Initialize PoliciesAnalyst.

**Parameters:**
- `db_path` (str, optional): Path to SQLite database. Default: `"warehouse.db"`

**Example:**
```python
from src.sdk import PoliciesAnalyst

analyst = PoliciesAnalyst()
analyst = PoliciesAnalyst(db_path="custom.db")
```

### Methods

#### `load_from_database(layer: str = "silver", limit: Optional[int] = None) -> List[Policy]`

Load policies from database.

**Parameters:**
- `layer` (str): Data layer to load from. Options: `"bronze"`, `"silver"`, `"gold"`. Default: `"silver"`
- `limit` (int, optional): Maximum number of records to load. Default: `None` (load all)

**Returns:**
- `List[Policy]`: List of Policy domain objects

**Raises:**
- `ValueError`: If layer is not "bronze", "silver", or "gold"

**Example:**
```python
policies = analyst.load_from_database()
policies = analyst.load_from_database(layer="bronze", limit=50)
```

---

#### `get_active_policies(policies: List[Policy]) -> List[Policy]`

Filter active policies.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects

**Returns:**
- `List[Policy]`: List of active policies

**Example:**
```python
policies = analyst.load_from_database()
active = analyst.get_active_policies(policies)
print(f"Active: {len(active)}")
```

---

#### `get_employer_policies(policies: List[Policy], employer_id: str) -> List[Policy]`

Filter policies by employer.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects
- `employer_id` (str): Employer identifier

**Returns:**
- `List[Policy]`: List of policies for the employer

**Example:**
```python
policies = analyst.load_from_database()
employer_policies = analyst.get_employer_policies(policies, employer_id="EMP001")
print(f"Policies for EMP001: {len(employer_policies)}")
```

---

#### `find_policy(policies: List[Policy], policy_id: str) -> Optional[Policy]`

Find a policy by ID.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects
- `policy_id` (str): Policy identifier

**Returns:**
- `Optional[Policy]`: Policy object or None if not found

**Example:**
```python
policies = analyst.load_from_database()
policy = analyst.find_policy(policies, policy_id="POL-001")
if policy:
    print(f"Found: {policy.policy_id}")
```

---

#### `get_total_coverage(policies: List[Policy]) -> Decimal`

Calculate total stop loss coverage.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects

**Returns:**
- `Decimal`: Total coverage amount

**Example:**
```python
policies = analyst.load_from_database()
total = analyst.get_total_coverage(policies)
print(f"Total coverage: ${total:,.2f}")
```

---

#### `get_employer_aggregations(policies: List[Policy]) -> List[Dict[str, Any]]`

Get aggregated statistics by employer (same logic as gold layer).

**Parameters:**
- `policies` (List[Policy]): List of Policy objects

**Returns:**
- `List[Dict[str, Any]]`: List of aggregated dictionaries with employer statistics

**Example:**
```python
policies = analyst.load_from_database()
aggregations = analyst.get_employer_aggregations(policies)

for agg in aggregations:
    print(f"Employer {agg['employer_id']}: {agg['policy_count']} policies")
```

**Note:** Uses centralized business rules to ensure consistency with pipeline.

---

#### `get_summary_statistics(policies: List[Policy]) -> Dict[str, Any]`

Calculate summary statistics for policies.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects

**Returns:**
- `Dict[str, Any]`: Dictionary with summary statistics:
  - `total_policies` (int): Total number of policies
  - `total_coverage` (float): Total coverage amount
  - `average_coverage` (float): Average coverage per policy
  - `by_status` (Dict[str, int]): Count by status
  - `by_employer` (Dict[str, int]): Count by employer

**Example:**
```python
policies = analyst.load_from_database()
stats = analyst.get_summary_statistics(policies)

print(f"Total: {stats['total_policies']} policies")
print(f"Coverage: ${stats['total_coverage']:,.2f}")
```

---

#### `to_dataframe(policies: List[Policy]) -> Any`

Convert policies to pandas DataFrame.

**Parameters:**
- `policies` (List[Policy]): List of Policy objects

**Returns:**
- `pandas.DataFrame`: DataFrame with policy data

**Example:**
```python
policies = analyst.load_from_database()
df = analyst.to_dataframe(policies)

# Use pandas for analysis
df.groupby('employer_id')['stop_loss_limit'].sum()
```

**DataFrame Columns:**
- `policy_id` (str)
- `employer_id` (str)
- `effective_date` (str, ISO format)
- `expiration_date` (str, ISO format)
- `stop_loss_limit` (float)
- `aggregate_deductible` (float)
- `specific_deductible` (float)
- `status` (str)

---

## StopLossAnalyst

Public API for combined claims and policies analysis.

### Class Definition

```python
class StopLossAnalyst(LoggingMixin):
    """Public API for combined claims and policies analysis."""
```

### Constructor

#### `__init__(db_path: str = "warehouse.db", approval_threshold: Optional[Decimal] = None)`

Initialize StopLossAnalyst.

**Parameters:**
- `db_path` (str, optional): Path to SQLite database. Default: `"warehouse.db"`
- `approval_threshold` (Decimal, optional): Threshold for claim approval. Default: `Decimal("100000.00")`

**Example:**
```python
from decimal import Decimal
from src.sdk import StopLossAnalyst

analyst = StopLossAnalyst()
analyst = StopLossAnalyst(approval_threshold=Decimal("50000.00"))
```

**Attributes:**
- `claims_analyst` (ClaimsAnalyst): Claims analyst instance
- `policies_analyst` (PoliciesAnalyst): Policies analyst instance

### Methods

#### `get_coverage_utilization() -> List[Dict[str, Any]]`

Calculate coverage utilization for all policies.

**Returns:**
- `List[Dict[str, Any]]`: List of utilization records with:
  - `policy_id` (str)
  - `employer_id` (str)
  - `stop_loss_limit` (float)
  - `total_claims` (float)
  - `utilization_percent` (float)
  - `remaining_coverage` (float)

**Example:**
```python
analyst = StopLossAnalyst()
utilization = analyst.get_coverage_utilization()

for util in utilization:
    print(f"Policy {util['policy_id']}: {util['utilization_percent']:.2f}% utilized")
```

**Note:** Automatically loads data from database.

---

#### `get_claims_by_policy_summary() -> Dict[str, Any]`

Get summary of claims grouped by policy.

**Returns:**
- `Dict[str, Any]`: Dictionary with policy summaries:
  - Key: `policy_id` (str)
  - Value: Dictionary with:
    - `policy` (Dict): Policy details
    - `claim_count` (int): Number of claims
    - `total_claim_amount` (float): Total claim amount

**Example:**
```python
analyst = StopLossAnalyst()
summary = analyst.get_claims_by_policy_summary()

for policy_id, details in summary.items():
    print(f"Policy {policy_id}: {details['claim_count']} claims, ${details['total_claim_amount']:,.2f}")
```

---

#### `get_high_utilization_policies(threshold_percent: float = 50.0) -> List[Dict[str, Any]]`

Get policies with utilization above threshold.

**Parameters:**
- `threshold_percent` (float): Utilization threshold percentage. Default: `50.0`

**Returns:**
- `List[Dict[str, Any]]`: List of high utilization policies (same format as `get_coverage_utilization()`)

**Example:**
```python
analyst = StopLossAnalyst()
high_util = analyst.get_high_utilization_policies(threshold_percent=75.0)

for policy in high_util:
    print(f"Policy {policy['policy_id']}: {policy['utilization_percent']:.2f}% utilized")
```

---

## Data Types

### Claim

Domain object representing a claim.

**Attributes:**
- `claim_id` (str): Unique claim identifier
- `policy_id` (str): Associated policy identifier
- `member_id` (str): Member identifier
- `claim_amount` (Decimal): Claim amount
- `incurred_date` (datetime): Date claim was incurred
- `paid_date` (Optional[datetime]): Date claim was paid (None if not paid)
- `status` (str): Claim status ("approved", "pending", "denied")
- `claim_type` (str): Type of claim ("medical", "dental", etc.)

**Methods:**
- `is_paid() -> bool`: Check if claim is paid

### Policy

Domain object representing a policy.

**Attributes:**
- `policy_id` (str): Unique policy identifier
- `employer_id` (str): Employer identifier
- `effective_date` (datetime): Policy effective date
- `expiration_date` (datetime): Policy expiration date
- `stop_loss_limit` (Decimal): Stop loss coverage limit
- `aggregate_deductible` (Decimal): Aggregate deductible
- `specific_deductible` (Decimal): Specific deductible
- `status` (str): Policy status ("active", "expired", "cancelled")

**Methods:**
- `is_active() -> bool`: Check if policy is active

## Error Handling

### Common Exceptions

#### `ValueError`

Raised when invalid parameters are provided.

**Example:**
```python
try:
    claims = analyst.load_from_database(layer="invalid")
except ValueError as e:
    print(f"Error: {e}")
```

#### `FileNotFoundError`

Raised when file operations fail.

**Example:**
```python
try:
    claims = analyst.load_claims("nonexistent.json")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

### Best Practices

```python
# Always handle errors gracefully
try:
    claims = analyst.load_from_database()
    total = analyst.get_total_claims(claims)
except Exception as e:
    print(f"Error loading data: {e}")
    claims = []  # Fallback
```

## Best Practices

### 1. Use Database Loading

```python
# ✅ Good - Load from database
claims = analyst.load_from_database(layer="silver")

# ❌ Avoid - Loading from files in production
claims = analyst.load_claims("data/raw_claims.json")
```

### 2. Use Silver Layer

```python
# ✅ Good - Use silver layer (processed data)
claims = analyst.load_from_database(layer="silver")

# ⚠️ Acceptable - Bronze for raw data inspection
claims = analyst.load_from_database(layer="bronze")
```

### 3. Convert to DataFrame Early

```python
# ✅ Good - Convert immediately
claims = analyst.load_from_database()
df = analyst.to_dataframe(claims)

# ❌ Avoid - Working with Claim objects when DataFrame is needed
claims = analyst.load_from_database()
# ... many operations on Claim objects ...
df = analyst.to_dataframe(claims)  # Convert at the end
```

### 4. Use Decimal for Money

```python
from decimal import Decimal

# ✅ Good
threshold = Decimal("50000.00")

# ❌ Avoid
threshold = 50000.00  # Floating point
```

### 5. Handle Empty Results

```python
claims = analyst.load_from_database()
if claims:
    total = analyst.get_total_claims(claims)
else:
    print("No claims found")
```

## Quick Reference

### ClaimsAnalyst Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_from_database()` | Load claims from database | `List[Claim]` |
| `get_total_claims()` | Calculate total amount | `Decimal` |
| `get_approved_claims()` | Filter approved claims | `List[Claim]` |
| `get_paid_claims()` | Filter paid claims | `List[Claim]` |
| `get_pending_claims()` | Filter pending claims | `List[Claim]` |
| `get_high_value_claims()` | Filter high-value claims | `List[Claim]` |
| `aggregate_by_policy()` | Group by policy | `Dict[str, List[Claim]]` |
| `get_policy_aggregations()` | Get policy statistics | `List[Dict]` |
| `aggregate_by_member()` | Group by member | `Dict[str, List[Claim]]` |
| `get_summary_statistics()` | Get summary stats | `Dict[str, Any]` |
| `to_dataframe()` | Convert to DataFrame | `pandas.DataFrame` |

### PoliciesAnalyst Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_from_database()` | Load policies from database | `List[Policy]` |
| `get_active_policies()` | Filter active policies | `List[Policy]` |
| `get_employer_policies()` | Filter by employer | `List[Policy]` |
| `find_policy()` | Find policy by ID | `Optional[Policy]` |
| `get_total_coverage()` | Calculate total coverage | `Decimal` |
| `get_employer_aggregations()` | Get employer statistics | `List[Dict]` |
| `get_summary_statistics()` | Get summary stats | `Dict[str, Any]` |
| `to_dataframe()` | Convert to DataFrame | `pandas.DataFrame` |

### StopLossAnalyst Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_coverage_utilization()` | Calculate utilization for all policies | `List[Dict]` |
| `get_claims_by_policy_summary()` | Get summary of claims grouped by policy | `Dict[str, Any]` |
| `get_high_utilization_policies()` | Filter policies with utilization above threshold | `List[Dict]` |

**Note:** The `StopLossAnalyst` class also provides access to `claims_analyst` and `policies_analyst` attributes for direct access to individual analyst classes.

## Next Steps

**Using the SDK?**

1. **[notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md)** → Complete usage guide with examples
2. **[examples/README.md](../examples/README.md)** → Runnable code examples
3. **Notebooks** → Interactive examples in `notebooks/`

**Need help?**

1. Check method docstrings: `help(ClaimsAnalyst.get_total_claims)`
2. Review [notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md) for usage patterns
3. See [examples/sdk_example.py](../examples/sdk_example.py) for code examples

**Want to understand the architecture?**

1. **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** → Architecture details
2. **[README.md](../README.md)** → Project overview

