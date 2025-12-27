# Testing Guide

Comprehensive guide to testing in the pipeline system.

## Test Structure

```
src/tests/
├── test_domain.py      # Unit tests for domain logic
├── test_pipelines.py   # Unit tests for pipeline orchestration
├── test_transforms.py  # Unit tests for transform layers
├── test_integration.py # Integration tests
└── test_e2e.py         # End-to-end tests
```

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/test_domain.py

# Run specific test
pytest src/tests/test_domain.py::TestClaim::test_claim_creation
```

### Test Categories

```bash
# Unit tests only
pytest src/tests/test_domain.py src/tests/test_transforms.py

# Integration tests
pytest src/tests/test_integration.py

# End-to-end tests
pytest src/tests/test_e2e.py

# All tests
pytest src/tests/
```

## Writing Tests

### Unit Tests

Test individual components in isolation:

```python
import pytest
from src.domain.claims import Claim
from datetime import datetime
from decimal import Decimal

def test_claim_creation():
    """Test creating a claim."""
    claim = Claim(
        claim_id="CLM001",
        policy_id="POL001",
        member_id="MEM001",
        claim_amount=Decimal("50000.00"),
        incurred_date=datetime.now()
    )
    
    assert claim.claim_id == "CLM001"
    assert claim.claim_amount == Decimal("50000.00")
```

### Integration Tests

Test interactions between components:

```python
import pytest
from src.pipelines import ClaimsPipeline, PipelineConfig, ExecutionContext
from src.pipelines.claims_pipeline import ClaimsBronzeStep, ClaimsSilverStep

def test_pipeline_integration():
    """Test pipeline with multiple steps."""
    steps = [
        ClaimsBronzeStep(source_path="test_data.json"),
        ClaimsSilverStep()
    ]
    
    context = ExecutionContext(
        pipeline_name="test",
        run_id="test-123"
    )
    
    config = PipelineConfig(steps=steps, context=context)
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    
    assert results["steps_executed"] == 2
```

### End-to-End Tests

Test complete workflows:

```python
import pytest
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

def test_e2e_claims_pipeline():
    """Test complete claims pipeline from config to database."""
    config_loader = ConfigLoader()
    config = config_loader.create_pipeline_config("claims_pipeline")
    
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    
    # Verify execution
    assert results["steps_executed"] > 0
    
    # Verify database
    from src.utils.database import DatabaseManager
    db = DatabaseManager("warehouse.db")
    claims = db.query("SELECT COUNT(*) as count FROM claims_silver")
    assert claims[0]["count"] > 0
```

## Test Fixtures

### Common Fixtures

```python
import pytest
from decimal import Decimal
from datetime import datetime
from src.domain.claims import Claim

@pytest.fixture
def sample_claim():
    """Create a sample claim for testing."""
    return Claim(
        claim_id="TEST-001",
        policy_id="POL-001",
        member_id="MEM-001",
        claim_amount=Decimal("50000.00"),
        incurred_date=datetime.now()
    )

@pytest.fixture
def sample_claims(sample_claim):
    """Create multiple sample claims."""
    return [sample_claim]
```

### Database Fixtures

```python
import pytest
import tempfile
import os
from src.utils.database import DatabaseManager

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db = DatabaseManager(db_path=db_path)
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Don't rely on test execution order
- Clean up after tests (use fixtures)

### 2. Descriptive Names

```python
# ✓ Good
def test_claim_exceeds_threshold_when_amount_is_greater():
    ...

# ✗ Bad
def test_claim():
    ...
```

### 3. Arrange-Act-Assert

```python
def test_calculate_total():
    # Arrange
    claims = [Claim(...), Claim(...)]
    processor = ClaimsProcessor()
    
    # Act
    total = processor.calculate_total_claims(claims)
    
    # Assert
    assert total == Decimal("100000.00")
```

### 4. Test Edge Cases

```python
def test_empty_claims_list():
    """Test handling of empty claims list."""
    processor = ClaimsProcessor()
    total = processor.calculate_total_claims([])
    assert total == Decimal("0.00")

def test_none_claim_amount():
    """Test handling of None claim amount."""
    # Should raise error or handle gracefully
    ...
```

### 5. Mock External Dependencies

```python
from unittest.mock import Mock, patch

def test_load_claims_with_mock_reader():
    """Test loading claims with mocked file reader."""
    with patch('src.utils.io.FileReader') as mock_reader:
        mock_reader.return_value.read.return_value = {"claims": [...]}
        
        analyst = ClaimsAnalyst()
        claims = analyst.load_claims("dummy_path.json")
        
        assert len(claims) > 0
```

## Coverage Goals

- **Unit Tests**: 80%+ coverage for domain logic
- **Integration Tests**: Cover all major component interactions
- **E2E Tests**: Cover critical user workflows

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Debugging Tests

### Run with Debugger

```bash
# Run with pdb
pytest --pdb

# Run specific test with pdb
pytest src/tests/test_domain.py::TestClaim::test_claim_creation --pdb
```

### Print Statements

```python
def test_something():
    result = do_something()
    print(f"Result: {result}")  # Will show in test output with -s flag
    assert result is not None

# Run with: pytest -s
```

### Verbose Output

```bash
# Show all print statements
pytest -s

# Show test names
pytest -v

# Show local variables on failure
pytest -l
```

## Common Issues

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Database Locked

```python
# Use temporary databases for tests
@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        yield DatabaseManager(tmp.name)
```

### Missing Dependencies

```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

## Test Examples

See `src/tests/` for complete test examples:
- `test_domain.py`: Domain model tests
- `test_pipelines.py`: Pipeline orchestration tests
- `test_transforms.py`: Transform layer tests
- `test_integration.py`: Integration tests
- `test_e2e.py`: End-to-end tests

