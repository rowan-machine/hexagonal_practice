# Analyst Guide

Complete guide for data analysts using the Ringmaster Pipelines system.

> **🎯 This guide is for analysts who need to analyze stop loss insurance data. You don't need to understand the technical implementation - just how to use the tools provided.**

## Table of Contents

- [Quick Start](#quick-start)
- [What You Need to Know](#what-you-need-to-know)
- [Understanding the SDK](#understanding-the-sdk)
- [Working with Notebooks](#working-with-notebooks)
- [Jupyter Notebook Guide](#jupyter-notebook-guide)
- [Common Analysis Tasks](#common-analysis-tasks)
- [Data Access Patterns](#data-access-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples and Templates](#examples-and-templates)
- [Command References](#command-references)
  - [Bash Command Reference](#bash-command-reference)
  - [AWS CLI Command Reference](#aws-cli-command-reference)
  - [CI/CD Command Reference](#cicd-command-reference)

## Quick Start

### 1. Install the Package

**Option A: Using pipenv (Recommended)**

```bash
# Install pipenv if you don't have it
pip install pipenv

# Install dependencies
pipenv install --dev

# Activate virtual environment
pipenv shell

# Install package in editable mode
pipenv run pip install -e .
```

**Option B: Using pip**

```bash
# From the project root directory
pip install -e .
```

**Important:** You must install the package before using notebooks or scripts. If you get `ModuleNotFoundError: No module named 'src'`, run `pip install -e .` or `pipenv install --dev` first.

### 2. Start Jupyter

```bash
# Start Jupyter Notebook
jupyter notebook

# Or start JupyterLab
jupyter lab
```

### 3. Open a Notebook

Navigate to the `notebooks/` folder and open:
- `analyst_claims_analysis.ipynb` - For claims analysis
- `analyst_policies_analysis.ipynb` - For policies analysis
- `analyst_combined_analysis.ipynb` - For combined analysis

### 4. Run Your First Analysis

```python
from decimal import Decimal
from src.sdk import ClaimsAnalyst

# Initialize the analyst
analyst = ClaimsAnalyst(
    db_path="warehouse.db",
    approval_threshold=Decimal("100000.00")
)

# Load claims from database
claims = analyst.load_from_database(layer="silver")

# Convert to DataFrame for analysis
df = analyst.to_dataframe(claims)

# View the data
df.head()
```

## What You Need to Know

### ✅ What Analysts Should Do

- **Use the SDK** - All data access goes through the SDK classes
- **Work with DataFrames** - Convert data to pandas DataFrames for analysis
- **Use notebooks** - Jupyter notebooks are the primary tool for analysis
- **Follow business rules** - The SDK handles all business logic automatically

### ❌ What Analysts Should NOT Do

- **Don't access the database directly** - Always use SDK methods
- **Don't load files directly** - Use SDK methods to load data
- **Don't implement business logic** - It's already in the SDK
- **Don't modify pipeline code** - That's for engineers

### Key Concepts

**SDK (Software Development Kit)**: A set of tools designed for analysts. Think of it as a simplified interface that hides all the complexity.

**Data Layers**:
- **Bronze**: Raw data (as ingested)
- **Silver**: Processed data (business rules applied) ← **Use this for analysis**
- **Gold**: Aggregated data (summaries by policy/employer)

**Analyst Classes**:
- `ClaimsAnalyst` - For analyzing claims data
- `PoliciesAnalyst` - For analyzing policies data
- `StopLossAnalyst` - For combined analysis

## Understanding the SDK

### ClaimsAnalyst

Use this for analyzing claims data.

#### Initialization

```python
from decimal import Decimal
from src.sdk import ClaimsAnalyst

# Basic initialization
analyst = ClaimsAnalyst(db_path="warehouse.db")

# With custom approval threshold
analyst = ClaimsAnalyst(
    db_path="warehouse.db",
    approval_threshold=Decimal("100000.00")
)
```

#### Loading Data

```python
# Load from database (recommended)
claims = analyst.load_from_database(layer="silver")

# Load specific number of records
claims = analyst.load_from_database(layer="silver", limit=1000)

# Load from file (if needed)
claims = analyst.load_claims("data/raw_claims.json", file_format="json")
```

#### Common Methods

```python
# Calculate total claims amount
total = analyst.get_total_claims(claims)

# Get approved claims
approved = analyst.get_approved_claims(claims)

# Get high-value claims
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# Aggregate by policy
by_policy = analyst.aggregate_by_policy(claims)

# Convert to DataFrame
df = analyst.to_dataframe(claims)

# Save claims
analyst.save_claims(claims, "output/processed_claims.json")
```

### PoliciesAnalyst

Use this for analyzing policies data.

#### Initialization

```python
from src.sdk import PoliciesAnalyst

analyst = PoliciesAnalyst(db_path="warehouse.db")
```

#### Common Methods

```python
# Load from database
policies = analyst.load_from_database(layer="silver")

# Get active policies
active = analyst.get_active_policies(policies)

# Get policies for specific employer
employer_policies = analyst.get_employer_policies(policies, employer_id="EMP001")

# Get total coverage
total_coverage = analyst.get_total_coverage(policies)

# Convert to DataFrame
df = analyst.to_dataframe(policies)
```

### StopLossAnalyst

Use this for combined claims and policies analysis.

#### Initialization

```python
from decimal import Decimal
from src.sdk import StopLossAnalyst

analyst = StopLossAnalyst(
    db_path="warehouse.db",
    approval_threshold=Decimal("100000.00")
)
```

#### Common Methods

```python
# Load data
claims = analyst.claims_analyst.load_from_database()
policies = analyst.policies_analyst.load_from_database()

# Analyze claims by policy
analysis = analyst.analyze_claims_by_policy(claims, policies)

# Calculate coverage utilization
utilization = analyst.calculate_coverage_utilization(claims, policies)
```

## Working with Notebooks

### Available Notebooks

1. **`analyst_claims_analysis.ipynb`**
   - Claims analysis examples
   - Filtering and aggregating claims
   - High-value claims identification

2. **`analyst_policies_analysis.ipynb`**
   - Policies analysis examples
   - Active policies filtering
   - Employer-based analysis

3. **`analyst_combined_analysis.ipynb`**
   - Combined claims and policies analysis
   - Coverage utilization calculations
   - Cross-dataset insights

4. **`claims_validation.ipynb`**
   - Data quality checks
   - Validation reports
   - Data profiling

5. **`policy_validation.ipynb`**
   - Policy data validation
   - Coverage verification
   - Data completeness checks

### Notebook Best Practices

1. **Start with Setup Cell**
   ```python
   # Always install package first
   # pip install -e .
   
   from src.sdk import ClaimsAnalyst
   analyst = ClaimsAnalyst(db_path="warehouse.db")
   ```

2. **Load Data Once**
   ```python
   # Load data in one cell
   claims = analyst.load_from_database(layer="silver")
   print(f"Loaded {len(claims)} claims")
   ```

3. **Use Descriptive Variable Names**
   ```python
   # Good
   high_value_claims = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
   
   # Avoid
   hvc = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
   ```

4. **Add Markdown Cells**
   - Explain what each section does
   - Document assumptions
   - Note any data issues

5. **Save Results**
   ```python
   # Save analysis results
   df.to_csv("output/analysis_results.csv", index=False)
   ```

## Common Analysis Tasks

### Task 1: Calculate Total Claims by Policy

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")

# Aggregate by policy
by_policy = analyst.aggregate_by_policy(claims)

# Convert to DataFrame
df = analyst.to_dataframe(by_policy)

# View results
print(df[['policy_id', 'total_claims', 'claim_count']])
```

### Task 2: Find High-Value Claims

```python
from src.sdk import ClaimsAnalyst
from decimal import Decimal

analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")

# Get high-value claims (>$50,000)
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# Convert to DataFrame
df = analyst.to_dataframe(high_value)

# Summary statistics
print(f"Total high-value claims: {len(high_value)}")
print(f"Total amount: ${analyst.get_total_claims(high_value):,.2f}")
```

### Task 3: Analyze Coverage Utilization

```python
from src.sdk import StopLossAnalyst
from decimal import Decimal

analyst = StopLossAnalyst(db_path="warehouse.db")
claims = analyst.claims_analyst.load_from_database()
policies = analyst.policies_analyst.load_from_database()

# Calculate utilization
utilization = analyst.calculate_coverage_utilization(claims, policies)

# View results
for util in utilization:
    print(f"Policy {util['policy_id']}: {util['utilization_percent']:.2f}% utilized")
```

### Task 4: Filter Claims by Status

```python
from src.sdk import ClaimsAnalyst

analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")

# Get approved claims
approved = analyst.get_approved_claims(claims)

# Get pending claims
pending = [c for c in claims if c.status == "pending"]

# Get paid claims
paid = [c for c in claims if c.is_paid()]

print(f"Approved: {len(approved)}")
print(f"Pending: {len(pending)}")
print(f"Paid: {len(paid)}")
```

### Task 5: Export Data for External Analysis

```python
from src.sdk import ClaimsAnalyst
import pandas as pd

analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")

# Convert to DataFrame
df = analyst.to_dataframe(claims)

# Export to CSV
df.to_csv("output/claims_export.csv", index=False)

# Export to Excel
df.to_excel("output/claims_export.xlsx", index=False)

# Export to JSON
analyst.save_claims(claims, "output/claims_export.json")
```

## Data Access Patterns

### Pattern 1: Load and Analyze

```python
# 1. Initialize analyst
analyst = ClaimsAnalyst(db_path="warehouse.db")

# 2. Load data
claims = analyst.load_from_database(layer="silver")

# 3. Analyze
total = analyst.get_total_claims(claims)
df = analyst.to_dataframe(claims)

# 4. Visualize/Export
df.head()
```

### Pattern 2: Filter and Aggregate

```python
# 1. Load all data
claims = analyst.load_from_database(layer="silver")

# 2. Filter
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# 3. Aggregate
by_policy = analyst.aggregate_by_policy(high_value)

# 4. Analyze filtered/aggregated data
df = analyst.to_dataframe(by_policy)
```

### Pattern 3: Compare Layers

```python
# Load from different layers
bronze_claims = analyst.load_from_database(layer="bronze")
silver_claims = analyst.load_from_database(layer="silver")

# Compare
print(f"Bronze: {len(bronze_claims)} claims")
print(f"Silver: {len(silver_claims)} claims")
print(f"Difference: {len(bronze_claims) - len(silver_claims)} claims processed")
```

### Pattern 4: Time-Based Analysis

```python
import pandas as pd
from datetime import datetime, timedelta

# Load data
claims = analyst.load_from_database(layer="silver")
df = analyst.to_dataframe(claims)

# Convert date column
df['incurred_date'] = pd.to_datetime(df['incurred_date'])

# Filter by date range
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
recent_claims = df[(df['incurred_date'] >= start_date) & (df['incurred_date'] <= end_date)]

# Analyze
print(f"Claims in date range: {len(recent_claims)}")
print(f"Total amount: ${recent_claims['claim_amount'].sum():,.2f}")
```

## Best Practices

### 1. Always Use the SDK

✅ **Do this:**
```python
analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")
```

❌ **Don't do this:**
```python
# Don't access database directly
import sqlite3
conn = sqlite3.connect("warehouse.db")
# ... direct SQL queries ...
```

### 2. Use Silver Layer for Analysis

The silver layer has business rules applied and is the best layer for analysis.

```python
# Good - use silver layer
claims = analyst.load_from_database(layer="silver")

# Avoid - bronze is raw data
claims = analyst.load_from_database(layer="bronze")
```

### 3. Convert to DataFrame Early

DataFrames are easier to work with for analysis.

```python
# Load and convert immediately
claims = analyst.load_from_database(layer="silver")
df = analyst.to_dataframe(claims)

# Now use pandas for analysis
df.groupby('policy_id')['claim_amount'].sum()
```

### 4. Handle Large Datasets

For large datasets, use limits or chunking.

```python
# Load in chunks
for offset in range(0, 10000, 1000):
    claims = analyst.load_from_database(layer="silver", limit=1000)
    # Process chunk
    process_chunk(claims)
```

### 5. Document Your Analysis

Add markdown cells in notebooks to explain:
- What you're analyzing
- Why you're analyzing it
- What assumptions you're making
- What the results mean

### 6. Save Your Work

```python
# Save processed data
analyst.save_claims(claims, "output/my_analysis.json")

# Save DataFrames
df.to_csv("output/my_analysis.csv", index=False)
```

### 7. Use Type Hints (Optional)

```python
from typing import List
from src.domain.claims import Claim

def analyze_claims(claims: List[Claim]) -> dict:
    """Analyze claims and return summary."""
    total = analyst.get_total_claims(claims)
    return {"total": total, "count": len(claims)}
```

## Troubleshooting

### Problem: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Install the package
pip install -e .
```

### Problem: Database Not Found

**Error:**
```
FileNotFoundError: warehouse.db
```

**Solution:**
1. Make sure pipelines have been run first
2. Check the database path is correct
3. Run: `python scripts/run_local.py claims_pipeline`

### Problem: Empty Results

**Issue:** `load_from_database()` returns empty list

**Solutions:**
1. Check if pipelines have been run
2. Verify data exists in database
3. Try different layer: `layer="bronze"` or `layer="gold"`

### Problem: Import Errors

**Error:**
```
ImportError: cannot import name 'ClaimsAnalyst'
```

**Solution:**
1. Make sure you're in the project root directory
2. Run `pip install -e .`
3. Restart Jupyter kernel

### Problem: Decimal Errors

**Error:**
```
TypeError: unsupported operand type(s) for +: 'float' and 'Decimal'
```

**Solution:**
Always use `Decimal` for monetary values:
```python
from decimal import Decimal

# Good
threshold = Decimal("50000.00")

# Avoid
threshold = 50000.00
```

### Problem: Date Format Issues

**Error:**
```
ValueError: time data '2024-01-01' does not match format
```

**Solution:**
Use pandas for date conversion:
```python
import pandas as pd
df['incurred_date'] = pd.to_datetime(df['incurred_date'])
```

## Examples and Templates

### Template: Basic Claims Analysis

```python
"""
Basic Claims Analysis Template
"""
from decimal import Decimal
from src.sdk import ClaimsAnalyst
import pandas as pd

# 1. Initialize
analyst = ClaimsAnalyst(
    db_path="warehouse.db",
    approval_threshold=Decimal("100000.00")
)

# 2. Load data
claims = analyst.load_from_database(layer="silver")
print(f"Loaded {len(claims)} claims")

# 3. Convert to DataFrame
df = analyst.to_dataframe(claims)

# 4. Basic statistics
print(f"Total claims: ${analyst.get_total_claims(claims):,.2f}")
print(f"Average claim: ${df['claim_amount'].mean():,.2f}")
print(f"Max claim: ${df['claim_amount'].max():,.2f}")

# 5. Filter and analyze
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
print(f"High-value claims: {len(high_value)}")

# 6. Export results
df.to_csv("output/claims_analysis.csv", index=False)
```

### Template: Policy Coverage Analysis

```python
"""
Policy Coverage Analysis Template
"""
from src.sdk import PoliciesAnalyst
import pandas as pd

# 1. Initialize
analyst = PoliciesAnalyst(db_path="warehouse.db")

# 2. Load data
policies = analyst.load_from_database(layer="silver")
print(f"Loaded {len(policies)} policies")

# 3. Convert to DataFrame
df = analyst.to_dataframe(policies)

# 4. Active policies
active = analyst.get_active_policies(policies)
print(f"Active policies: {len(active)}")

# 5. Total coverage
total_coverage = analyst.get_total_coverage(policies)
print(f"Total coverage: ${total_coverage:,.2f}")

# 6. By employer
for employer_id in df['employer_id'].unique():
    employer_policies = analyst.get_employer_policies(policies, employer_id=employer_id)
    print(f"Employer {employer_id}: {len(employer_policies)} policies")
```

### Template: Combined Analysis

```python
"""
Combined Claims and Policies Analysis Template
"""
from decimal import Decimal
from src.sdk import StopLossAnalyst

# 1. Initialize
analyst = StopLossAnalyst(
    db_path="warehouse.db",
    approval_threshold=Decimal("100000.00")
)

# 2. Load data
claims = analyst.claims_analyst.load_from_database()
policies = analyst.policies_analyst.load_from_database()

# 3. Analyze claims by policy
analysis = analyst.analyze_claims_by_policy(claims, policies)

# 4. Calculate utilization
utilization = analyst.calculate_coverage_utilization(claims, policies)

# 5. Report
for util in utilization:
    print(f"Policy {util['policy_id']}:")
    print(f"  Coverage: ${util.get('coverage', 0):,.2f}")
    print(f"  Claims: ${util.get('total_claims', 0):,.2f}")
    print(f"  Utilization: {util['utilization_percent']:.2f}%")
```

## Jupyter Notebook Guide

Complete guide to using Jupyter notebooks for data analysis with Python and pandas.

### Jupyter Basics

#### Starting Jupyter

```bash
# Start Jupyter Notebook
jupyter notebook

# Start JupyterLab (recommended)
jupyter lab

# Start with specific port
jupyter notebook --port 8889

# Start with no browser
jupyter notebook --no-browser
```

#### Notebook Interface

- **Cells**: Individual code or markdown blocks
- **Cell Types**: Code (executable) or Markdown (documentation)
- **Kernel**: Python interpreter that runs your code
- **Output**: Results displayed below cells

#### Keyboard Shortcuts

**Command Mode (press Esc):**
- `A` - Insert cell above
- `B` - Insert cell below
- `DD` - Delete cell
- `M` - Convert to markdown
- `Y` - Convert to code
- `Shift + Enter` - Run cell and move to next
- `Ctrl + Enter` - Run cell and stay

**Edit Mode (press Enter):**
- `Tab` - Code completion
- `Shift + Tab` - Show function signature
- `Ctrl + /` - Comment/uncomment

### Python Basics for Analysis

#### Data Types

```python
# Numbers
x = 42
y = 3.14
amount = Decimal("100000.00")  # Use Decimal for money

# Strings
name = "Policy ABC"
status = 'active'

# Lists
claims = [1, 2, 3, 4, 5]
policies = ["POL-001", "POL-002"]

# Dictionaries
claim_data = {
    "claim_id": "CLM-001",
    "amount": Decimal("50000.00"),
    "status": "approved"
}

# Booleans
is_active = True
is_paid = False
```

#### Working with Lists

```python
# Create list
claims = [1, 2, 3, 4, 5]

# Access elements
first = claims[0]  # First element
last = claims[-1]  # Last element

# Slice
first_three = claims[:3]  # First 3 elements
last_two = claims[-2:]  # Last 2 elements

# List comprehension
high_values = [x for x in claims if x > 1000]

# Filter
approved = [c for c in claims if c.status == "approved"]
```

#### Working with Dictionaries

```python
# Access values
claim_id = claim_data["claim_id"]
amount = claim_data.get("amount", Decimal("0.00"))  # With default

# Add/update
claim_data["new_field"] = "value"
claim_data["amount"] = Decimal("60000.00")

# Iterate
for key, value in claim_data.items():
    print(f"{key}: {value}")
```

#### Functions

```python
def calculate_total(claims):
    """Calculate total claim amount."""
    return sum(c.claim_amount for c in claims)

# Use function
total = calculate_total(claims)
```

#### Error Handling

```python
try:
    result = analyst.load_from_database()
except Exception as e:
    print(f"Error loading data: {e}")
    result = []
```

### Pandas Basics

#### Creating DataFrames

```python
import pandas as pd

# From list of dictionaries
data = [
    {"claim_id": "CLM-001", "amount": 50000},
    {"claim_id": "CLM-002", "amount": 75000}
]
df = pd.DataFrame(data)

# From SDK
claims = analyst.load_from_database()
df = analyst.to_dataframe(claims)
```

#### Viewing Data

```python
# First few rows
df.head()  # First 5 rows
df.head(10)  # First 10 rows

# Last few rows
df.tail()  # Last 5 rows

# Basic info
df.info()  # Data types, non-null counts
df.describe()  # Statistical summary

# Shape
df.shape  # (rows, columns)

# Column names
df.columns

# Data types
df.dtypes
```

#### Selecting Data

```python
# Select column
df['claim_id']
df.claim_id  # Alternative syntax

# Select multiple columns
df[['claim_id', 'claim_amount', 'status']]

# Select rows by index
df.iloc[0]  # First row
df.iloc[0:5]  # First 5 rows

# Select rows by condition
df[df['status'] == 'approved']
df[df['claim_amount'] > 50000]

# Multiple conditions
df[(df['status'] == 'approved') & (df['claim_amount'] > 50000)]
```

#### Filtering Data

```python
# Filter by column value
approved = df[df['status'] == 'approved']

# Filter by multiple conditions
high_value_approved = df[
    (df['status'] == 'approved') & 
    (df['claim_amount'] > 50000)
]

# Filter by list of values
statuses = ['approved', 'pending']
filtered = df[df['status'].isin(statuses)]

# Filter by string contains
df[df['claim_id'].str.contains('CLM')]
```

#### Sorting Data

```python
# Sort by column
df.sort_values('claim_amount')

# Sort descending
df.sort_values('claim_amount', ascending=False)

# Sort by multiple columns
df.sort_values(['status', 'claim_amount'], ascending=[True, False])
```

#### Grouping and Aggregating

```python
# Group by column
by_policy = df.groupby('policy_id')

# Aggregate functions
by_policy['claim_amount'].sum()  # Sum
by_policy['claim_amount'].mean()  # Average
by_policy['claim_amount'].count()  # Count
by_policy['claim_amount'].max()  # Maximum
by_policy['claim_amount'].min()  # Minimum

# Multiple aggregations
by_policy.agg({
    'claim_amount': ['sum', 'mean', 'count'],
    'claim_id': 'count'
})

# Named aggregations
by_policy.agg(
    total_amount=('claim_amount', 'sum'),
    avg_amount=('claim_amount', 'mean'),
    claim_count=('claim_id', 'count')
)
```

#### Adding Columns

```python
# Add calculated column
df['amount_thousands'] = df['claim_amount'] / 1000

# Add conditional column
df['is_high_value'] = df['claim_amount'] > 50000

# Add column based on other columns
df['total'] = df['claim_amount'] + df['fee']
```

#### Working with Dates

```python
# Convert to datetime
df['incurred_date'] = pd.to_datetime(df['incurred_date'])

# Extract date parts
df['year'] = df['incurred_date'].dt.year
df['month'] = df['incurred_date'].dt.month
df['day'] = df['incurred_date'].dt.day

# Filter by date range
start_date = pd.to_datetime('2024-01-01')
end_date = pd.to_datetime('2024-12-31')
df[(df['incurred_date'] >= start_date) & (df['incurred_date'] <= end_date)]
```

#### Merging DataFrames

```python
# Merge on common column
merged = pd.merge(claims_df, policies_df, on='policy_id')

# Merge with different column names
merged = pd.merge(
    claims_df, 
    policies_df, 
    left_on='policy_id', 
    right_on='id'
)

# Left join (keep all claims)
merged = pd.merge(claims_df, policies_df, on='policy_id', how='left')
```

#### Exporting Data

```python
# Export to CSV
df.to_csv('output/claims.csv', index=False)

# Export to Excel
df.to_excel('output/claims.xlsx', index=False)

# Export to JSON
df.to_json('output/claims.json', orient='records')
```

### Notebook Best Practices

#### 1. Organize Your Notebook

```python
# Cell 1: Imports
import pandas as pd
from decimal import Decimal
from src.sdk import ClaimsAnalyst

# Cell 2: Setup
analyst = ClaimsAnalyst(db_path="warehouse.db")

# Cell 3: Load data
claims = analyst.load_from_database(layer="silver")

# Cell 4: Analysis
# ... your analysis code ...

# Cell 5: Results
# ... display results ...
```

#### 2. Use Markdown Cells

```markdown
## Analysis: High-Value Claims

This section analyzes claims over $50,000.

### Methodology
- Load claims from silver layer
- Filter by amount > $50,000
- Group by policy
```

#### 3. Document Assumptions

```python
# Assumption: Approval threshold is $100,000
# Data source: Silver layer (processed data)
# Date range: 2024-01-01 to 2024-12-31
```

#### 4. Save Intermediate Results

```python
# Save processed data
df.to_csv('intermediate/high_value_claims.csv', index=False)

# Load later
df = pd.read_csv('intermediate/high_value_claims.csv')
```

#### 5. Handle Errors Gracefully

```python
try:
    claims = analyst.load_from_database()
except Exception as e:
    print(f"Error: {e}")
    claims = []  # Fallback to empty list
```

## Command References

### Bash Command Reference

Essential bash commands for working with files, directories, and data.

#### File Operations

```bash
# List files
ls                    # List current directory
ls -l                 # Detailed list
ls -la                # Include hidden files
ls *.py               # List Python files

# Change directory
cd /path/to/directory
cd ..                 # Go up one level
cd ~                  # Go to home directory

# Create directory
mkdir new_folder
mkdir -p path/to/nested/folders  # Create nested directories

# Remove files/directories
rm file.txt           # Remove file
rm -r folder          # Remove directory recursively
rm -f file.txt       # Force remove (no confirmation)

# Copy files
cp source.txt dest.txt
cp -r source_dir dest_dir  # Copy directory

# Move/rename files
mv old_name.txt new_name.txt
mv file.txt /path/to/destination/
```

#### File Viewing

```bash
# View file contents
cat file.txt          # Display entire file
less file.txt         # View file (scrollable)
head file.txt         # First 10 lines
head -n 20 file.txt   # First 20 lines
tail file.txt         # Last 10 lines
tail -f file.txt     # Follow file (watch for changes)
```

#### Searching

```bash
# Search in files
grep "pattern" file.txt
grep -r "pattern" directory/  # Recursive search
grep -i "pattern" file.txt     # Case insensitive

# Find files
find . -name "*.py"            # Find Python files
find . -name "*.csv"           # Find CSV files
find . -type f -name "*.txt"   # Find text files
```

#### Text Processing

```bash
# Count lines/words/characters
wc file.txt           # Lines, words, characters
wc -l file.txt        # Line count only

# Sort lines
sort file.txt
sort -n file.txt      # Numeric sort

# Remove duplicates
uniq file.txt
sort file.txt | uniq  # Sort then remove duplicates

# Extract columns (CSV)
cut -d',' -f1,3 file.csv  # Extract columns 1 and 3
```

#### Environment Variables

```bash
# Set variable
export VAR_NAME="value"

# View variable
echo $VAR_NAME

# Use in command
python script.py --db-path $VAR_NAME
```

#### Pipes and Redirection

```bash
# Pipe output to next command
ls | grep ".py"       # List files, filter Python files
cat file.txt | wc -l  # Count lines in file

# Redirect output
python script.py > output.txt        # Write to file
python script.py >> output.txt       # Append to file
python script.py 2> error.txt        # Redirect errors
python script.py > output.txt 2>&1    # Redirect both
```

### AWS CLI Command Reference

Essential AWS CLI commands for working with S3, EC2, and other AWS services.

#### Installation and Configuration

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Set profile
export AWS_PROFILE=my-profile

# Verify configuration
aws sts get-caller-identity
```

#### S3 Operations

```bash
# List buckets
aws s3 ls

# List objects in bucket
aws s3 ls s3://bucket-name/
aws s3 ls s3://bucket-name/path/  # List in path

# Copy file to S3
aws s3 cp file.txt s3://bucket-name/
aws s3 cp file.txt s3://bucket-name/path/file.txt

# Copy file from S3
aws s3 cp s3://bucket-name/file.txt ./file.txt

# Copy directory
aws s3 cp ./local-dir/ s3://bucket-name/remote-dir/ --recursive

# Sync directories
aws s3 sync ./local-dir/ s3://bucket-name/remote-dir/

# Remove object
aws s3 rm s3://bucket-name/file.txt

# Remove directory
aws s3 rm s3://bucket-name/path/ --recursive

# Presigned URL (temporary access)
aws s3 presign s3://bucket-name/file.txt
aws s3 presign s3://bucket-name/file.txt --expires-in 3600  # 1 hour
```

#### EC2 Operations

```bash
# List instances
aws ec2 describe-instances

# List running instances
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"

# Start instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Stop instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Get instance details
aws ec2 describe-instances --instance-ids i-1234567890abcdef0
```

#### IAM Operations

```bash
# List users
aws iam list-users

# Get user details
aws iam get-user --user-name username

# List roles
aws iam list-roles

# List policies
aws iam list-policies
```

#### CloudWatch Operations

```bash
# List log groups
aws logs describe-log-groups

# Get log events
aws logs get-log-events --log-group-name /aws/lambda/function-name

# Create log stream
aws logs create-log-stream --log-group-name group-name --log-stream-name stream-name
```

#### Common Patterns

```bash
# Download data from S3 for analysis
aws s3 cp s3://bucket-name/data/claims.csv ./data/

# Upload results to S3
aws s3 cp ./output/results.csv s3://bucket-name/results/

# Sync local data with S3
aws s3 sync ./data/ s3://bucket-name/data/ --exclude "*.tmp"

# Check if file exists
aws s3 ls s3://bucket-name/file.txt
```

### CI/CD Command Reference

Essential commands for continuous integration and deployment workflows.

#### GitHub Actions

```bash
# View workflow runs
gh run list

# View specific workflow run
gh run view <run-id>

# Rerun failed workflow
gh run rerun <run-id>

# Cancel workflow
gh run cancel <run-id>

# View workflow logs
gh run view <run-id> --log
```

#### Git Operations for CI/CD

```bash
# Create feature branch
git checkout -b feature/my-feature

# Commit changes
git add .
git commit -m "Add feature"

# Push to remote
git push origin feature/my-feature

# Create pull request
gh pr create --title "Add feature" --body "Description"

# Check CI status
gh pr checks
```

#### Docker in CI/CD

```bash
# Build image
docker build -t my-image:tag .

# Tag image
docker tag my-image:tag registry/my-image:tag

# Push to registry
docker push registry/my-image:tag

# Pull from registry
docker pull registry/my-image:tag

# Run container
docker run -d my-image:tag
```

#### Testing Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_file.py::test_function

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

#### Linting and Formatting

```bash
# Lint code
ruff check src/

# Format code
black src/
ruff format src/

# Type check
mypy src/

# Run all checks
make ci
```

#### Deployment Commands

```bash
# Build package
python setup.py sdist bdist_wheel

# Install package
pip install dist/package-name-version.tar.gz

# Deploy to PyPI (example)
twine upload dist/*
```

## Next Steps

**Ready to start analyzing?**

1. **[examples/README.md](../examples/README.md)** → More code examples
2. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup guide
3. **Notebooks in this folder** → Run the example notebooks

**Need help?**

1. Check [Troubleshooting](#troubleshooting) section above
2. Review [examples/sdk_example.py](../examples/sdk_example.py)
3. Check notebook examples in this folder

**Want to understand more?**

1. **[docs/SDK_API_REFERENCE.md](../docs/SDK_API_REFERENCE.md)** → ⭐ Complete API reference
2. **[README.md](../README.md)** → Project overview
3. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Architecture details (for engineers)

---

**Remember:** As an analyst, you should focus on using the SDK tools provided. The technical implementation details are handled by engineers. If you need new functionality, talk to the engineering team.

