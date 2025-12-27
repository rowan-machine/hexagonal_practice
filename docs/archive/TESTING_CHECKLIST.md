# Complete Testing Checklist

This checklist ensures all components of the system are working correctly.

## Prerequisites

- [ ] Virtual environment activated (`.venv`)
- [ ] Package installed: `pip install -e .`
- [ ] Dev dependencies installed: `pip install -e ".[dev]"` (optional)
- [ ] Docker Desktop running (for Docker tests)

---

## 1. Unit & Integration Tests

### Run All Tests
```bash
# In virtual environment
pytest src/tests/ -v
```

**Expected**: 30 tests passing

### Test Categories
- [ ] Domain logic tests (`test_domain.py`) - 9 tests
- [ ] Pipeline orchestration tests (`test_pipelines.py`) - 5 tests
- [ ] Transform layer tests (`test_transforms.py`) - 6 tests
- [ ] Integration tests (`test_integration.py`) - 5 tests
- [ ] End-to-end tests (`test_e2e.py`) - 4 tests

---

## 2. Local Pipeline Execution

### Claims Pipeline
```bash
python run_local.py claims_pipeline
```

**Verify**:
- [ ] Pipeline completes without errors
- [ ] Database file `warehouse.db` is created
- [ ] Data exists in `claims_bronze` table
- [ ] Data exists in `claims_silver` table
- [ ] Data exists in `claims_gold` table

### Policies Pipeline
```bash
python run_local.py policies_pipeline
```

**Verify**:
- [ ] Pipeline completes without errors
- [ ] Data exists in `policies_bronze` table
- [ ] Data exists in `policies_silver` table
- [ ] Data exists in `policies_gold` table

### List Available Pipelines
```bash
python run_local.py --list
```

**Expected**: Shows `claims_pipeline` and `policies_pipeline`

---

## 3. Database Verification

### Check Database Schema
```bash
# Using Python
python -c "from src.utils.database import DatabaseManager; db = DatabaseManager(); print('Database initialized')"
```

### Query Database Directly
```python
from src.utils.database import DatabaseManager

db = DatabaseManager("warehouse.db")

# Check claims
claims_bronze = db.query("SELECT COUNT(*) as count FROM claims_bronze")
claims_silver = db.query("SELECT COUNT(*) as count FROM claims_silver")
claims_gold = db.query("SELECT COUNT(*) as count FROM claims_gold")

print(f"Claims Bronze: {claims_bronze[0]['count']}")
print(f"Claims Silver: {claims_silver[0]['count']}")
print(f"Claims Gold: {claims_gold[0]['count']}")

# Check policies
policies_bronze = db.query("SELECT COUNT(*) as count FROM policies_bronze")
policies_silver = db.query("SELECT COUNT(*) as count FROM policies_silver")
policies_gold = db.query("SELECT COUNT(*) as count FROM policies_gold")

print(f"Policies Bronze: {policies_bronze[0]['count']}")
print(f"Policies Silver: {policies_silver[0]['count']}")
print(f"Policies Gold: {policies_gold[0]['count']}")
```

**Verify**:
- [ ] All tables exist
- [ ] Bronze tables have data (12 claims, 4 policies from JSON files)
- [ ] Silver tables have processed data
- [ ] Gold tables have aggregated data

---

## 4. SDK Usage (Analyst Interface)

### ClaimsAnalyst SDK
```python
from decimal import Decimal
from src.sdk import ClaimsAnalyst

# Initialize
analyst = ClaimsAnalyst(db_path="warehouse.db", approval_threshold=Decimal("100000.00"))

# Load from database
claims = analyst.load_from_database(layer="silver")
print(f"Loaded {len(claims)} claims")

# Get summary statistics
stats = analyst.get_summary_statistics(claims)
print(f"Total claims: {stats['total_claims']}")
print(f"Total amount: ${stats['total_amount']:,.2f}")

# Filter claims
approved = analyst.get_approved_claims(claims)
high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))

# Get policy aggregations
policy_aggs = analyst.get_policy_aggregations()
print(f"Aggregations for {len(policy_aggs)} policies")
```

**Verify**:
- [ ] Can load claims from database
- [ ] Summary statistics calculated correctly
- [ ] Filtering methods work
- [ ] Policy aggregations retrieved

### PoliciesAnalyst SDK
```python
from src.sdk import PoliciesAnalyst

# Initialize
analyst = PoliciesAnalyst(db_path="warehouse.db")

# Load from database
policies = analyst.load_from_database(layer="silver")
print(f"Loaded {len(policies)} policies")

# Get summary statistics
stats = analyst.get_summary_statistics(policies)
print(f"Total policies: {stats['total_policies']}")
print(f"Total coverage: ${stats['total_coverage']:,.2f}")

# Filter policies
active = analyst.get_active_policies(policies)

# Get employer aggregations
employer_aggs = analyst.get_employer_aggregations()
print(f"Aggregations for {len(employer_aggs)} employers")
```

**Verify**:
- [ ] Can load policies from database
- [ ] Summary statistics calculated correctly
- [ ] Filtering methods work
- [ ] Employer aggregations retrieved

### StopLossAnalyst SDK
```python
from decimal import Decimal
from src.sdk import StopLossAnalyst

# Initialize
analyst = StopLossAnalyst(db_path="warehouse.db", approval_threshold=Decimal("100000.00"))

# Get coverage utilization
utilization = analyst.get_coverage_utilization()
print(f"Utilization for {len(utilization)} policies")

# Get claims by policy summary
summary = analyst.get_claims_by_policy_summary()
print(f"Summary for {len(summary)} policies")

# Get high utilization policies
high_util = analyst.get_high_utilization_policies(threshold_percent=50.0)
print(f"High utilization policies: {len(high_util)}")
```

**Verify**:
- [ ] Coverage utilization calculated
- [ ] Claims by policy summary generated
- [ ] High utilization filtering works

---

## 5. Jupyter Notebooks

### Setup
```bash
# Install jupyter in virtual environment
pip install jupyter ipykernel

# Install kernel
python -m ipykernel install --user --name=hexagonal_practice --display-name "Python (hexagonal_practice)"
```

### Run Notebooks

1. **Claims Validation** (`notebooks/claims_validation.ipynb`)
   - [ ] Notebook executes without errors
   - [ ] SDK loads data successfully
   - [ ] Data validation works

2. **Policy Validation** (`notebooks/policy_validation.ipynb`)
   - [ ] Notebook executes without errors
   - [ ] SDK loads data successfully
   - [ ] Data validation works

3. **Claims Analysis** (`notebooks/analyst_claims_analysis.ipynb`)
   - [ ] All cells execute
   - [ ] SDK methods work correctly
   - [ ] Data analysis produces expected results

4. **Policies Analysis** (`notebooks/analyst_policies_analysis.ipynb`)
   - [ ] All cells execute
   - [ ] SDK methods work correctly
   - [ ] Data analysis produces expected results

5. **Combined Analysis** (`notebooks/analyst_combined_analysis.ipynb`)
   - [ ] All cells execute
   - [ ] Combined analysis works
   - [ ] Utilization calculations correct

6. **DB Connection Example** (`notebooks/db_connection_example.ipynb`)
   - [ ] Database connection utility works
   - [ ] Can query database directly

---

## 6. Docker Services

### Start Services
```bash
# Start services and wait for Airflow to be ready
make docker-up-wait

# Or start without waiting
make docker-up
```

### Verify Services Running
```bash
docker-compose ps
```

**Expected**: All services show "Up" status:
- [ ] `postgres` (Airflow database)
- [ ] `warehouse` (PostgreSQL warehouse)
- [ ] `atlas` (Apache Atlas)
- [ ] `airflow-webserver`
- [ ] `airflow-scheduler`

### Check Service Health

#### PostgreSQL (Airflow)
```bash
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT version();"
```

#### Warehouse Database
```bash
docker-compose exec warehouse psql -U warehouse -d warehouse -c "\dt"
```

**Verify**:
- [ ] Can connect to warehouse database
- [ ] Tables exist (if pipelines have run)

#### Apache Atlas
```bash
curl http://localhost:21000/api/atlas/admin/version
```

**Verify**:
- [ ] Atlas responds (or returns 401/403 if auth required)

#### Airflow Web UI
```bash
# Open in browser
http://localhost:8080
```

**Verify**:
- [ ] Airflow UI loads
- [ ] Can login (default: airflow/airflow)
- [ ] DAGs are visible (if configured)

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-webserver
docker-compose logs -f warehouse
```

**Verify**:
- [ ] No critical errors in logs
- [ ] Services start successfully

---

## 7. Mock Atlas Server (Local Development)

### Start Mock Server
```bash
python mock_atlas.py
```

**In another terminal**, test publishing:
```python
from src.utils.atlas import AtlasClient
from src.utils.atlas_payloads import build_policies_table_payload

client = AtlasClient(base_url="http://localhost:21000", enabled=True)
payload = build_policies_table_payload()
client.publish(payload)
```

**Verify**:
- [ ] Mock server receives payload
- [ ] Payload is printed to console
- [ ] No errors in client

---

## 8. Configuration Files

### Pipeline Configurations
- [ ] `pipelines_config/claims_pipeline.yml` - Valid YAML
- [ ] `pipelines_config/policies_pipeline.yml` - Valid YAML

### Validation Config
- [ ] `config/validation.yml` - Valid YAML
- [ ] Expected counts match JSON files (12 claims, 4 policies)

### Schema Files
- [ ] `schemas/claims.yml` - Valid YAML
- [ ] `schemas/policies.yml` - Valid YAML

---

## 9. Data Files

### Raw Data
- [ ] `data/raw_claims.json` - Valid JSON, 12 records
- [ ] `data/raw_policies.json` - Valid JSON, 4 records

**Verify counts**:
```python
import json

with open("data/raw_claims.json") as f:
    claims = json.load(f)
    print(f"Claims: {len(claims.get('claims', []))}")

with open("data/raw_policies.json") as f:
    policies = json.load(f)
    print(f"Policies: {len(policies.get('policies', []))}")
```

---

## 10. End-to-End Workflow

### Complete Data Flow Test

1. **Run Claims Pipeline**
   ```bash
   python run_local.py claims_pipeline
   ```

2. **Run Policies Pipeline**
   ```bash
   python run_local.py policies_pipeline
   ```

3. **Verify Data in Database**
   ```python
   from src.utils.database import DatabaseManager
   
   db = DatabaseManager("warehouse.db")
   
   # Check all layers
   bronze = db.query("SELECT COUNT(*) as c FROM claims_bronze")[0]['c']
   silver = db.query("SELECT COUNT(*) as c FROM claims_silver")[0]['c']
   gold = db.query("SELECT COUNT(*) as c FROM claims_gold")[0]['c']
   
   print(f"Claims: Bronze={bronze}, Silver={silver}, Gold={gold}")
   ```

4. **Use SDK to Analyze**
   ```python
   from src.sdk import StopLossAnalyst
   from decimal import Decimal
   
   analyst = StopLossAnalyst(db_path="warehouse.db")
   utilization = analyst.get_coverage_utilization()
   print(f"Calculated utilization for {len(utilization)} policies")
   ```

5. **Verify Aggregations Match**
   ```python
   # Compare SDK aggregations with gold layer
   from src.sdk import ClaimsAnalyst, PoliciesAnalyst
   
   claims_analyst = ClaimsAnalyst(db_path="warehouse.db")
   policies_analyst = PoliciesAnalyst(db_path="warehouse.db")
   
   # Get from SDK
   sdk_claims_aggs = claims_analyst.get_policy_aggregations()
   
   # Get from database
   db_claims_aggs = db.query("SELECT * FROM claims_gold")
   
   print(f"SDK aggregations: {len(sdk_claims_aggs)}")
   print(f"DB aggregations: {len(db_claims_aggs)}")
   # Should match!
   ```

**Verify**:
- [ ] Data flows through all layers (bronze → silver → gold)
- [ ] SDK aggregations match database gold layer
- [ ] Business rules are consistent

---

## 11. Error Handling

### Test Error Scenarios

1. **Invalid Pipeline Name**
   ```bash
   python run_local.py invalid_pipeline
   ```
   **Expected**: Error message about pipeline not found

2. **Missing Data File**
   ```python
   from src.pipelines.claims_pipeline import ClaimsBronzeStep
   step = ClaimsBronzeStep(source_path="nonexistent.json")
   # Should handle gracefully
   ```

3. **Database Connection Error**
   ```python
   from src.utils.database import DatabaseManager
   db = DatabaseManager(db_path="/invalid/path/warehouse.db")
   # Should create database or handle error
   ```

---

## 12. Documentation

### Verify Documentation Files
- [ ] `README.md` - Setup instructions work
- [ ] `ARCHITECTURE.md` - Architecture documented
- [ ] `GETTING_STARTED.md` - Quick start guide
- [ ] `DOCKER_SETUP.md` - Docker instructions
- [ ] `TESTING.md` - Testing guide
- [ ] `EXAMPLES.md` - Code examples
- [ ] `docs/ATLAS_GUIDE.md` - Atlas documentation
- [ ] `sql_migration/README.md` - SQL migration docs

---

## 13. Code Quality

### Linting
```bash
# If using ruff
ruff check src/

# If using black
black --check src/
```

### Type Checking (Optional)
```bash
mypy src/
```

---

## 14. Performance Check

### Pipeline Execution Time
```bash
time python run_local.py claims_pipeline
time python run_local.py policies_pipeline
```

**Note**: Should complete in reasonable time (< 30 seconds for sample data)

---

## Quick Verification Script

Save this as `verify_setup.py`:

```python
"""Quick verification script for system setup."""
import sys
from pathlib import Path

def verify_imports():
    """Verify all key imports work."""
    try:
        from src.pipelines import ClaimsPipeline, PoliciesPipeline
        from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
        from src.utils.database import DatabaseManager
        from src.utils.config_loader import ConfigLoader
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def verify_database():
    """Verify database can be accessed."""
    try:
        db = DatabaseManager("warehouse.db")
        # Check if tables exist
        tables = db.query("SELECT name FROM sqlite_master WHERE type='table'")
        print(f"✓ Database accessible ({len(tables)} tables)")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def verify_data_files():
    """Verify data files exist."""
    files = [
        "data/raw_claims.json",
        "data/raw_policies.json",
        "pipelines_config/claims_pipeline.yml",
        "pipelines_config/policies_pipeline.yml"
    ]
    all_exist = all(Path(f).exists() for f in files)
    if all_exist:
        print("✓ All data files exist")
    else:
        missing = [f for f in files if not Path(f).exists()]
        print(f"✗ Missing files: {missing}")
    return all_exist

if __name__ == "__main__":
    print("Verifying system setup...\n")
    
    results = [
        verify_imports(),
        verify_database(),
        verify_data_files()
    ]
    
    if all(results):
        print("\n✓ All checks passed!")
        sys.exit(0)
    else:
        print("\n✗ Some checks failed")
        sys.exit(1)
```

Run it:
```bash
python verify_setup.py
```

---

## Summary

After completing this checklist, you should have verified:

- ✅ All tests pass
- ✅ Pipelines execute successfully
- ✅ Database contains data at all layers
- ✅ SDK methods work correctly
- ✅ Notebooks execute without errors
- ✅ Docker services are running
- ✅ Documentation is accessible
- ✅ Error handling works
- ✅ End-to-end workflow functions

If all items are checked, your system is fully functional! 🎉


