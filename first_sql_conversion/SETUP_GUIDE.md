# Simplified SQL Conversion - Complete Setup Guide

This is a **dumbed-down, standalone version** of the full repository. It demonstrates converting SQL to Python with minimal dependencies and complexity.

## 🎯 What This Is

A complete, working example that shows:
- How to convert SQL queries to Python
- How to set up a simple data pipeline
- How to test your conversion
- How to use the results

**No complex architecture, no Docker, no Airflow** - just the core concepts.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (comes with Python)

That's it! No other dependencies required.

## 🚀 Quick Setup

### Option 1: Using venv (Standard Python)

```bash
# 1. Navigate to this directory
cd first_sql_conversion

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies (none required - uses only standard library!)
# Actually, we don't need to install anything for the basic version!

# 5. Run the test
python test_conversion.py
```

### Option 2: Using Pipenv (Recommended for Dependency Management)

```bash
# 1. Navigate to this directory
cd first_sql_conversion

# 2. Install pipenv (if not already installed)
pip install pipenv

# 3. Install dependencies (creates virtual environment automatically)
pipenv install

# 4. Activate the environment
pipenv shell

# 5. Run the test
python test_conversion.py
```

**Note:** For this simplified version, we don't actually need any external dependencies - it uses only Python's standard library! But Pipenv is useful if you want to add dependencies later.

## 📁 What's Included

```
first_sql_conversion/
├── SETUP_GUIDE.md              # This file
├── README.md                   # Overview and next steps
├── CLAIMS_GOLD_001.sql        # Original SQL query
├── simple_aggregator.py       # Python business logic (converts SQL)
├── simple_database.py         # Simple database operations
├── test_conversion.py          # Test script
├── run_pipeline.py            # Complete pipeline example
├── sample_data.py             # Generate sample data
├── requirements.txt           # Dependencies (empty for basic version)
├── Pipfile                     # Pipenv configuration
└── example_warehouse.db       # SQLite database (created automatically)
```

## 🧪 Testing the Conversion

### Step 1: Generate Sample Data

```bash
python sample_data.py
```

This creates sample claims data in the database.

### Step 2: Run the Conversion Test

```bash
python test_conversion.py
```

This will:
1. Load data from the database
2. Run the SQL query (for comparison)
3. Run the Python conversion
4. Compare results
5. Show you the output

### Step 3: Run the Complete Pipeline

```bash
python run_pipeline.py
```

This demonstrates a complete pipeline:
1. Load data
2. Process/aggregate
3. Save results
4. Verify output

## 📊 Understanding the Conversion

### The SQL Query

```sql
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count,
    AVG(claim_amount) AS avg_claim_amount,
    MAX(claim_amount) AS max_claim_amount,
    MIN(claim_amount) AS min_claim_amount
FROM claims_silver
GROUP BY policy_id
ORDER BY total_claims DESC;
```

### The Python Equivalent

```python
from simple_aggregator import SimpleClaimsAggregator

aggregator = SimpleClaimsAggregator()
result = aggregator.aggregate_by_policy(claims)
```

**Key Concepts:**
- `GROUP BY policy_id` → Group claims by policy in Python
- `SUM(claim_amount)` → `sum()` function
- `COUNT(claim_id)` → Count items in group
- `AVG/MAX/MIN` → Python built-in functions
- `ORDER BY` → `sorted()` function

## 🔍 What Each File Does

### `simple_aggregator.py`
- Contains the business logic
- Converts SQL aggregation to Python
- No dependencies (uses only standard library)

### `simple_database.py`
- Handles database operations
- Creates tables
- Inserts/retrieves data
- Uses SQLite (no setup required)

### `test_conversion.py`
- Tests the conversion
- Compares SQL vs Python results
- Shows you the output

### `run_pipeline.py`
- Complete pipeline example
- Shows end-to-end flow
- Demonstrates best practices

### `sample_data.py`
- Generates test data
- Populates the database
- Makes testing easy

## 🎓 Learning Path

1. **Start Here**: Run `test_conversion.py` to see the conversion in action
2. **Understand**: Read `simple_aggregator.py` to see how SQL maps to Python
3. **Experiment**: Modify the code, add your own SQL queries
4. **Extend**: Use `run_pipeline.py` as a template for your own pipelines

## 🐛 Troubleshooting

### "No module named 'simple_aggregator'"

**Solution**: Make sure you're in the `first_sql_conversion` directory:
```bash
cd first_sql_conversion
python test_conversion.py
```

### "Database is locked"

**Solution**: Close any other programs using the database, or delete `example_warehouse.db` and run again.

### "Permission denied" (venv activation)

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
chmod +x .venv/bin/activate
```

## 📚 Next Steps

**Ready to learn more?**

1. **[README.md](README.md)** → Overview and concepts
2. **[sql_migration/README.md](../sql_migration/README.md)** → Full migration process
3. **[docs/MIGRATION_GUIDE.md](../docs/MIGRATION_GUIDE.md)** → Complete migration strategy

**Want to use the full system?**

1. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Full system setup
2. **[examples/README.md](../examples/README.md)** → More examples
3. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Architecture details

## 💡 Tips

- **Start simple**: Understand this example before moving to the full system
- **Experiment**: Modify the code to see how it works
- **Compare**: Run both SQL and Python to verify they match
- **Extend**: Add your own SQL queries and convert them

## ✅ Verification

After setup, verify everything works:

```bash
# Test 1: Generate data
python sample_data.py

# Test 2: Run conversion
python test_conversion.py

# Test 3: Run pipeline
python run_pipeline.py
```

All three should complete without errors!

