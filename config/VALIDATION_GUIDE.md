# Validation Guide

This guide explains how validation works in the pipeline system, simulating SQL estate validation.

## Overview

Validation ensures that processed data matches expected results from the SQL estate. This is critical during migration from SQL to Python pipelines.

## Validation Strategy

### Development (Current)
- **Source**: Reads expected counts from source JSON files
- **Simulates**: SQL query results (e.g., `SELECT COUNT(*) FROM claims_source`)
- **Fallback**: Uses `config/validation.yml` if JSON unavailable

### Production (Future)
- **Source**: Queries original SQL database directly
- **Validates**: Compares SQL results with Python pipeline results
- **Ensures**: 100% match before decommissioning SQL

## Configuration

### `config/validation.yml`

```yaml
claims:
  expected_count: 12  # Fallback count
  source_table: "claims_source"  # Original SQL table
  validation_type: "count_match"

policies:
  expected_count: 4  # Fallback count
  source_table: "policies_source"  # Original SQL table
  validation_type: "count_match"
```

**Note**: Expected counts in config are fallbacks. Primary source is JSON files (simulating SQL).

## Usage

### Using ValidationLoader

```python
from src.utils.validation_loader import ValidationLoader

loader = ValidationLoader()

# Validate claims count
result = loader.validate_claims_count(
    actual_count=len(processed_claims),
    source_json_path="data/raw_claims.json"
)

if result["passed"]:
    print("Validation passed!")
else:
    print(f"Validation failed: {result['message']}")
```

### In Pipeline Steps

```python
from src.utils.validation_loader import ValidationLoader

class ClaimsValidationStep(ValidationStep):
    def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        silver_data = context.get("silver_data")
        actual_count = len(silver_data) if isinstance(silver_data, list) else 0
        
        loader = ValidationLoader()
        result = loader.validate_claims_count(actual_count)
        
        if not result["passed"]:
            self.log_error("Count validation failed", result=result)
            raise ValueError(f"Validation failed: {result['message']}")
        
        return {"validation": result}
```

## Validation Results

Validation returns a dictionary with:

```python
{
    "passed": bool,           # True if validation passed
    "actual_count": int,      # Actual number of records processed
    "expected_count": int,     # Expected count from source
    "source": str,            # "source_json" or "config"
    "message": str            # Human-readable message
}
```

## How It Works

1. **Read Source JSON**: `ValidationLoader` reads the source JSON file
   - For claims: `data/raw_claims.json` → counts records in `"claims"` array
   - For policies: `data/raw_policies.json` → counts records in `"policies"` array

2. **Compare Counts**: Compares actual count vs. expected count from JSON

3. **Fallback to Config**: If JSON unavailable, uses `config/validation.yml`

4. **Log Results**: Logs validation results for monitoring

## SQL Estate Simulation

The current implementation simulates SQL estate validation:

**SQL Query (Original)**:
```sql
SELECT COUNT(*) FROM claims_source;
-- Returns: 12
```

**Python (Simulated)**:
```python
loader.get_expected_count_from_json('data/raw_claims.json', 'claims')
# Returns: 12 (from JSON file)
```

**Future (Production)**:
```python
# Will query SQL database directly
loader.get_expected_count_from_sql('claims_source')
# Returns: 12 (from SQL query)
```

## Integration with Pipelines

Validation can be integrated at any pipeline step:

1. **After Bronze**: Validate raw data count
2. **After Silver**: Validate processed data count
3. **After Gold**: Validate aggregated data count

Example pipeline configuration:
```yaml
steps:
  - name: claims_bronze
    type: bronze
  - name: claims_silver
    type: silver
  - name: claims_validation
    type: validation
    data_key: silver_data
    validation_type: count_match
    source_json: data/raw_claims.json
```

## Best Practices

1. **Always Validate**: Run validation after each major step
2. **Use Source JSON**: Prefer JSON over config for expected counts
3. **Log Results**: Always log validation results for debugging
4. **Fail Fast**: Stop pipeline if critical validations fail
5. **Document Sources**: Note where expected counts come from

## Troubleshooting

### Validation Fails

1. **Check Counts**: Verify actual vs. expected counts
2. **Check Source**: Ensure JSON file exists and is readable
3. **Check Config**: Verify fallback config is correct
4. **Check Logs**: Review validation logs for details

### Expected Count Wrong

1. **Update JSON**: Update source JSON file with correct count
2. **Update Config**: Update `config/validation.yml` as fallback
3. **Verify SQL**: In production, verify SQL query returns correct count

## Migration Context

This validation system is designed for SQL estate migration:

- **Current**: Validates against JSON files (simulating SQL)
- **Future**: Will validate against actual SQL database
- **Goal**: Ensure Python pipelines produce identical results to SQL

See `sql_migration/README.md` for complete migration workflow.

## Next Steps

**Validation configured?** Continue with:

1. **[sql_migration/README.md](../sql_migration/README.md)** → Complete SQL migration process
2. **[config/PIPELINE_CONFIG_GUIDE.md](PIPELINE_CONFIG_GUIDE.md)** → Add validation to your pipelines
3. **[examples/README.md](../examples/README.md)** → See validation in examples

**Migrating from SQL?**

1. **[docs/MIGRATION_GUIDE.md](../docs/MIGRATION_GUIDE.md)** → Agile migration strategy
2. **[first_sql_conversion/README.md](../first_sql_conversion/README.md)** → First conversion example
3. **[schemas/README.md](../schemas/README.md)** → Define data schemas

**Testing validation?**

1. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Testing guidelines
2. **[scripts/verify_data_loaded.py](../scripts/verify_data_loaded.py)** → Verify data after pipeline runs

