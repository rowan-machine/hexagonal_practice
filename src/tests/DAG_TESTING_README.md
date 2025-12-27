# DAG Testing Guide

Comprehensive testing suite for Airflow DAGs covering integrity, unit, integration, and end-to-end tests.

## Overview

This testing suite provides four levels of testing for Airflow DAGs:

1. **DAG Integrity/Structure Tests** (`test_dags_integrity.py`)
2. **Unit Tests** (`test_dags_unit.py`)
3. **Integration Tests** (`test_dags_integration.py`)
4. **End-to-End/Data Tests** (`test_dags_e2e.py`)

## Prerequisites

### Option 1: Install Airflow Locally

```bash
pip install apache-airflow==2.10.3
```

### Option 2: Run Tests in Docker (Recommended)

Tests can be run inside the Airflow Docker container where Airflow is already installed:

```bash
docker-compose exec airflow pytest src/tests/test_dags_*.py -v
```

## Test Files

### 1. DAG Integrity Tests (`test_dags_integrity.py`)

**Purpose**: Basic sanity checks using DagBag to catch structural issues.

**Tests**:
- DAGs load without import errors
- DAG IDs are unique
- All expected DAGs exist (claims_pipeline, policies_pipeline, claims_backfill, policies_backfill)
- No DAG cycles
- Correct tags for each DAG
- Correct schedule intervals
- Correct owners
- Correct max_active_runs
- Correct task IDs

**Run**:
```bash
pytest src/tests/test_dags_integrity.py -v
```

### 2. Unit Tests (`test_dags_unit.py`)

**Purpose**: Test individual DAG components in isolation using mocking.

**Tests**:
- Function signatures and parameter handling
- Custom parameter propagation
- Missing dag_run handling
- Default arguments validation
- Backfill function execution

**Run**:
```bash
pytest src/tests/test_dags_unit.py -v
```

### 3. Integration Tests (`test_dags_integration.py`)

**Purpose**: Verify how tasks interact, ensuring data flows correctly.

**Tests**:
- Task dependencies
- Task execution flow with real components
- Execution date handling in backfill
- Parameter propagation
- Airflow Variable integration

**Run**:
```bash
pytest src/tests/test_dags_integration.py -v
```

### 4. End-to-End Tests (`test_dags_e2e.py`)

**Purpose**: Confirm the entire pipeline produces expected output data.

**Tests**:
- Full pipeline execution
- Data validation (bronze, silver, gold layers)
- Aggregation correctness
- Idempotent execution
- Backfill execution

**Run**:
```bash
pytest src/tests/test_dags_e2e.py -v
```

## Running All DAG Tests

```bash
# Run all DAG tests
pytest src/tests/test_dags_*.py -v

# Run with coverage
pytest src/tests/test_dags_*.py --cov=airflow/dags --cov-report=html

# Run specific test file
pytest src/tests/test_dags_integrity.py -v

# Run specific test
pytest src/tests/test_dags_integrity.py::TestDAGIntegrity::test_claims_pipeline_dag_exists -v
```

## Test Structure

### DAG Integrity Tests

```python
class TestDAGIntegrity:
    def test_dag_bag_loads_without_errors(self, dag_bag):
        """Test that all DAGs load without import errors."""
        
    def test_claims_pipeline_dag_exists(self, dag_bag):
        """Test that claims_pipeline DAG exists."""
        
    def test_no_dag_cycles(self, dag_bag):
        """Test that DAGs have no cycles."""
```

### Unit Tests

```python
class TestClaimsPipelineDAGUnit:
    def test_run_claims_pipeline_function_signature(self):
        """Test that run_claims_pipeline function accepts context."""
        
    def test_run_claims_pipeline_with_custom_params(self):
        """Test run_claims_pipeline with custom parameters."""
```

### Integration Tests

```python
class TestDAGTaskIntegration:
    def test_claims_pipeline_task_dependencies(self, dag_bag):
        """Test that claims_pipeline task has correct dependencies."""
        
    def test_claims_pipeline_task_execution_flow(self, dag_bag, temp_db):
        """Test that claims_pipeline task executes correctly."""
```

### End-to-End Tests

```python
class TestDAGE2E:
    def test_claims_pipeline_e2e_execution(self, temp_db, test_data):
        """Test end-to-end execution of claims pipeline DAG."""
        
    def test_claims_pipeline_data_validation(self, temp_db, test_data):
        """Test that claims pipeline produces valid data."""
```

## Mocking Strategy

### Unit Tests
- Mock `ConfigLoader` to avoid file I/O
- Mock `ClaimsPipeline`/`PoliciesPipeline` to avoid actual execution
- Mock `Variable` to avoid Airflow database access

### Integration Tests
- Use real `ConfigLoader` and `Pipeline` classes
- Mock `AtlasClient` to avoid external service calls
- Use temporary databases for data validation

### End-to-End Tests
- Use real pipeline execution
- Mock only external services (Atlas)
- Validate actual data in database

## Test Data

End-to-end tests create temporary test data:
- `data/raw_claims.json` - Test claims data
- `data/raw_policies.json` - Test policies data

These files are automatically created and cleaned up by pytest fixtures.

## Continuous Integration

DAG tests are included in CI/CD pipeline:

```yaml
# .github/workflows/ci.yml
- name: Test DAGs
  run: |
    pip install apache-airflow==2.10.3
    pytest src/tests/test_dags_*.py -v
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'airflow'"

**Solution**: Install Airflow or run tests in Docker:
```bash
pip install apache-airflow==2.10.3
# OR
docker-compose exec airflow pytest src/tests/test_dags_*.py -v
```

### "DAG import errors"

**Solution**: Check that DAG files are in `airflow/dags/` and have no syntax errors:
```bash
python -m py_compile airflow/dags/*.py
```

### "Tests fail with database errors"

**Solution**: Tests use temporary databases. Ensure SQLite is available and paths are writable.

## Best Practices

1. **Run integrity tests first**: Catch structural issues early
2. **Use mocking in unit tests**: Keep tests fast and isolated
3. **Use real components in integration tests**: Verify actual interactions
4. **Validate data in E2E tests**: Ensure correct output
5. **Run all tests before committing**: `pytest src/tests/test_dags_*.py`

## Next Steps

- **[TESTING.md](TESTING.md)** → General testing guide
- **[airflow/dags/README.md](../../airflow/dags/README.md)** → DAG documentation
- **[docs/DEVELOPER_ONBOARDING.md](../../docs/DEVELOPER_ONBOARDING.md)** → Developer setup

