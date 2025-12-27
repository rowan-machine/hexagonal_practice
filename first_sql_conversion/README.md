# First SQL Conversion Example - Simplified & Standalone

This directory contains a **complete, dumbed-down, standalone version** of the full repository. It demonstrates converting SQL to Python with minimal complexity - perfect for learning and testing!

## 🎯 What This Is

A **simplified, self-contained example** that shows:
- ✅ How to convert SQL queries to Python
- ✅ How to set up a simple data pipeline
- ✅ How to test your conversion
- ✅ How to verify results match SQL

**No complex architecture, no Docker, no Airflow** - just the core concepts!

## 📋 Prerequisites

- Python 3.8 or higher
- pip (comes with Python)

That's it! No other dependencies required.

## 🚀 Quick Start

### Step 1: Choose Your Virtual Environment

**Option A: Using venv (Standard Python)**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

**Option B: Using Pipenv (Recommended for Dependency Management)**
```bash
# Install pipenv (if not installed)
pip install pipenv

# Install dependencies (creates virtual environment automatically)
pipenv install

# Activate environment
pipenv shell
```

**Note:** This simplified version uses only Python's standard library - no external dependencies needed! But virtual environments are still recommended for best practices.

### Step 2: Generate Sample Data

```bash
python sample_data.py
```

This creates sample claims data in the database.

### Step 3: Test the Conversion

```bash
python test_conversion.py
```

This will:
1. Load data from the database
2. Run the SQL query (for comparison)
3. Run the Python conversion
4. Compare results
5. Show you the output

### Step 4: Run the Complete Pipeline

```bash
python run_pipeline.py
```

This demonstrates a complete pipeline from start to finish.

## 📁 Files

- **`QUICK_START.md`** - ⭐ 5-minute quick start guide
- **`SETUP_GUIDE.md`** - ⭐ Complete setup guide with both venv and pipenv options
- **`CLAIMS_GOLD_001.sql`** - The original SQL query
- **`simple_aggregator.py`** - Python business logic (converts SQL)
- **`simple_database.py`** - Simple database operations (SQLite)
- **`test_conversion.py`** - Test script demonstrating the conversion
- **`run_pipeline.py`** - Complete pipeline example
- **`sample_data.py`** - Generate sample data for testing
- **`sql_to_pandas_conversion.ipynb`** - Jupyter notebook (step-by-step)
- **`requirements.txt`** - Dependencies (empty - uses standard library!)
- **`Pipfile`** - Pipenv configuration

## 📖 What This Demonstrates

This example shows how to convert SQL aggregation queries to Python.

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

### Key Concepts

1. **SQL GROUP BY** → Python `defaultdict` or grouping logic
2. **SQL SUM/COUNT/AVG/MAX/MIN** → Python built-in functions (`sum()`, `len()`, etc.)
3. **SQL ORDER BY** → Python `sorted()` function
4. **SQL SELECT** → Python dictionary/list operations

## 🎓 Learning Path

1. **Quick Start (5 min)**: Read `QUICK_START.md` to get running fast
2. **Complete Setup**: Read `SETUP_GUIDE.md` for detailed instructions
3. **Generate Data**: Run `python sample_data.py` to create test data
4. **Test Conversion**: Run `python test_conversion.py` to see SQL vs Python
5. **Run Pipeline**: Run `python run_pipeline.py` to see complete workflow
6. **Explore Code**: Read `simple_aggregator.py` to understand the conversion
7. **Experiment**: Modify the code and see what happens!

## Next Steps

**Understood the example?** Continue migrating:

1. **[sql_migration/README.md](../sql_migration/README.md)** → Follow the complete migration process
2. **[docs/MIGRATION_GUIDE.md](../docs/MIGRATION_GUIDE.md)** → Agile migration strategy
3. **[config/VALIDATION_GUIDE.md](../config/VALIDATION_GUIDE.md)** → Set up validation for your migrations

**Ready to migrate more SQL?**

1. **[sql_migration/sql_migration_tracker.md](../sql_migration/sql_migration_tracker.md)** → Document your SQL queries
2. **[schemas/README.md](../schemas/README.md)** → Document data schemas
3. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create pipeline configurations

**Want to understand the implementation?**

1. **[src/business_rules/aggregations.py](../src/business_rules/aggregations.py)** → See the full implementation
2. **[src/pipelines/claims_pipeline.py](../src/pipelines/claims_pipeline.py)** → See how it's used in pipelines
3. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Understand the architecture

