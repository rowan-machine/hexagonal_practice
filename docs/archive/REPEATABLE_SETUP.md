# Repeatable Pipeline Setup

This document ensures that pipeline execution, data verification, and Atlas publishing can be repeated reliably.

## Quick Verification

Run the comprehensive verification script:

```bash
python verify_pipeline_complete.py
```

This checks:
1. ✅ Data is loaded in warehouse (bronze, silver, gold tables)
2. ✅ Atlas entities are published
3. ✅ All components are working

## Step-by-Step Verification

### 1. Verify Data is Loaded

```bash
# Check SQLite (local)
python verify_data_loaded.py

# Check PostgreSQL (Docker)
python verify_data_loaded.py --postgres
```

Expected output:
- ✅ claims_bronze: 12 records
- ✅ claims_silver: 12 records
- ✅ claims_gold: 18 records
- ✅ policies_bronze: 4 records
- ✅ policies_silver: 4 records
- ✅ policies_gold: 4 records

### 2. Verify Atlas Entities

```bash
python verify_atlas_entities.py
```

If entities are missing, publish them:

```bash
# Try the fixed publishing script
python publish_atlas_fix.py

# Or use the original script
python publish_atlas_metadata.py
```

### 3. Run Pipelines (Repeatable)

```bash
# Run claims pipeline
python run_local.py claims_pipeline

# Run policies pipeline
python run_local.py policies_pipeline

# Verify after each run
python verify_pipeline_complete.py
```

## Making It Repeatable

### Pipeline Execution

Pipelines are designed to be idempotent:
- ✅ Can be run multiple times safely
- ✅ Data is upserted (not duplicated)
- ✅ Validation ensures data quality
- ✅ Metrics track execution

### Data Verification

The verification scripts are repeatable:
- ✅ Check actual record counts
- ✅ Verify table existence
- ✅ Support both SQLite and PostgreSQL
- ✅ Clear success/failure indicators

### Atlas Publishing

Atlas publishing is repeatable:
- ✅ Can be run multiple times (updates existing entities)
- ✅ Handles authentication automatically
- ✅ Provides detailed error messages
- ✅ Verifies entities after publishing

## Troubleshooting

### Data Not Loading

1. Check pipeline logs:
   ```bash
   # In Airflow UI, check task logs
   # Or check local logs if running locally
   ```

2. Verify database connection:
   ```bash
   python verify_data_loaded.py
   ```

3. Check data files exist:
   ```bash
   ls data/raw_claims.json
   ls data/raw_policies.json
   ```

### Atlas Entities Missing

1. Check Atlas is running:
   ```bash
   docker-compose ps atlas
   ```

2. Try publishing:
   ```bash
   python publish_atlas_fix.py
   ```

3. Verify entities:
   ```bash
   python verify_atlas_entities.py
   ```

4. Check Atlas logs:
   ```bash
   docker-compose logs atlas | tail -50
   ```

### Pipeline Fails in Airflow

1. Check Airflow logs:
   ```bash
   docker-compose logs airflow | tail -100
   ```

2. Verify environment variables:
   - `ATLAS_URL`
   - `ATLAS_ENABLED`
   - `WAREHOUSE_DB_HOST`
   - `WAREHOUSE_DB_PORT`

3. Check database connectivity:
   ```bash
   docker-compose exec airflow ping warehouse
   ```

## Automation

### CI/CD Integration

Add to your CI/CD pipeline:

```bash
# Run pipelines
python run_local.py claims_pipeline
python run_local.py policies_pipeline

# Verify results
python verify_pipeline_complete.py

# Exit code indicates success/failure
if [ $? -eq 0 ]; then
    echo "All verifications passed"
else
    echo "Some verifications failed"
    exit 1
fi
```

### Scheduled Verification

Create a cron job or scheduled task:

```bash
# Daily verification
0 9 * * * cd /path/to/project && python verify_pipeline_complete.py >> verify.log 2>&1
```

## Best Practices

1. **Always verify after pipeline runs**: Use `verify_pipeline_complete.py`
2. **Check data counts**: Ensure expected record counts match
3. **Verify Atlas entities**: Publish and verify metadata regularly
4. **Monitor logs**: Check Airflow and Atlas logs for errors
5. **Test repeatability**: Run pipelines multiple times to ensure idempotency

## Files

- `verify_data_loaded.py` - Verify data in warehouse
- `verify_atlas_entities.py` - Verify Atlas entities
- `verify_pipeline_complete.py` - Comprehensive verification
- `publish_atlas_fix.py` - Fixed Atlas publishing with better error handling
- `publish_atlas_metadata.py` - Original Atlas publishing script


