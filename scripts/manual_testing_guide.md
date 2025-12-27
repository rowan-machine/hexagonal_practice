# Manual Testing Guide

Complete guide for manual testing before release.

## Quick Test Script

Run the automated release readiness check:
```bash
python scripts/test_release_readiness.py
```

**Expected**: All 9 checks should pass.

## Manual Testing Steps

### 1. Test Package Installation

```bash
# Clean environment test
python -m venv test_env
test_env\Scripts\activate  # Windows
# or
source test_env/bin/activate  # Linux/Mac

pip install -e ".[dev]"
python -c "from src.sdk import ClaimsAnalyst; print('OK')"
```

**Expected**: Package installs and imports work.

### 2. Run Test Suite

```bash
# Run all tests
pytest src/tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Check coverage threshold (should be 70%+)
```

**Expected**: All tests pass, coverage meets threshold.

### 3. Test Pipeline Execution

```bash
# Run claims pipeline
python scripts/run_local.py claims_pipeline

# Run policies pipeline
python scripts/run_local.py policies_pipeline

# Verify data loaded
python scripts/verify_data_loaded.py
```

**Expected**: 
- Pipelines complete without errors
- Data exists in bronze, silver, and gold tables
- Verification script confirms data

### 4. Test Examples

```bash
# Pipeline example
python examples/pipeline_example.py

# SDK example
python examples/sdk_example.py
```

**Expected**: Examples run without errors and produce output.

### 5. Test SDK Methods

```python
from src.sdk import ClaimsAnalyst, PoliciesAnalyst
from decimal import Decimal

# Test ClaimsAnalyst
analyst = ClaimsAnalyst(db_path="warehouse.db")
claims = analyst.load_from_database(layer="silver")
print(f"Loaded {len(claims)} claims")

# Test PoliciesAnalyst
policies_analyst = PoliciesAnalyst(db_path="warehouse.db")
policies = policies_analyst.load_from_database(layer="silver")
print(f"Loaded {len(policies)} policies")
```

**Expected**: SDK methods work correctly.

### 6. Test Code Quality Tools

```bash
# Linting
ruff check src/ scripts/ examples/

# Formatting check
black --check src/ scripts/ examples/

# Type checking
mypy src/ --ignore-missing-imports
```

**Expected**: All checks pass (or only acceptable warnings).

### 7. Test Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

**Expected**: All hooks pass.

### 8. Test Docker (if applicable)

```bash
# Validate compose file
docker-compose config

# Start services and wait for Airflow to be ready (recommended)
make docker-up-wait

# Or start without waiting
make docker-up
make wait-airflow

# Check status
docker-compose ps

# Run pipeline in container
docker-compose exec airflow python scripts/run_local.py claims_pipeline

# Stop services
docker-compose down
```

**Expected**: Docker services start and pipelines run.

### 9. Test Documentation

- [ ] All markdown files render correctly
- [ ] All code examples work
- [ ] All links are valid
- [ ] No broken references

### 10. Test Notebooks (if Jupyter available)

```bash
# Start Jupyter
jupyter notebook

# Open and run:
# - notebooks/analyst_claims_analysis.ipynb
# - notebooks/analyst_policies_analysis.ipynb
# - notebooks/analyst_combined_analysis.ipynb
```

**Expected**: Notebooks execute without errors.

## Test Results Template

```
Manual Testing Results
======================

Date: ___________
Tester: ___________

[ ] Package Installation: PASS / FAIL
[ ] Test Suite: PASS / FAIL (X tests, Y% coverage)
[ ] Pipeline Execution: PASS / FAIL
[ ] Examples: PASS / FAIL
[ ] SDK Methods: PASS / FAIL
[ ] Code Quality: PASS / FAIL
[ ] Pre-commit Hooks: PASS / FAIL
[ ] Docker: PASS / FAIL / N/A
[ ] Documentation: PASS / FAIL
[ ] Notebooks: PASS / FAIL / N/A

Issues Found:
1. 
2. 
3. 

Overall Status: READY / NOT READY
```

## Common Issues and Solutions

### Issue: ModuleNotFoundError
**Solution**: Run `pip install -e .` first

### Issue: Tests fail
**Solution**: Check Python version (3.8+), ensure dependencies installed

### Issue: Pipeline fails
**Solution**: Check data files exist, database permissions

### Issue: Docker won't start
**Solution**: Check Docker Desktop is running, ports available

## Next Steps

After manual testing:
1. Document any issues found
2. Fix critical issues
3. Re-run automated checks
4. Proceed with release if all pass

