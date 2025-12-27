# Publishing Metadata to Atlas

This guide explains how to publish policies and claims metadata to Apache Atlas so it appears in the Atlas UI.

## Why Atlas Shows "Other Stuff"

Atlas comes with default/example entities from its installation. Your policies and claims entities won't appear until you explicitly publish them.

## Quick Publish (Recommended)

Use the provided script to publish all metadata at once:

```bash
python publish_atlas_metadata.py
```

This will publish:
- Warehouse database
- Fact tables (fact_policies, fact_claims)
- Gold tables (gold_policies_by_customer, gold_claims_by_policy)
- ETL processes with lineage

## Automatic Publishing

Metadata is automatically published when pipelines run (if `ATLAS_ENABLED=true`):

```bash
# Run pipelines - metadata is published automatically
python run_local.py claims_pipeline
python run_local.py policies_pipeline
```

## Manual Publishing

### Option 1: Using the Script

```bash
# Publish to local Atlas
python publish_atlas_metadata.py

# Publish to Docker Atlas
python publish_atlas_metadata.py --atlas-url http://localhost:21000

# Dry run (see what would be published)
python publish_atlas_metadata.py --dry-run
```

### Option 2: Using Python

```python
from src.utils.atlas import AtlasClient
from src.utils.atlas_payloads import (
    build_policies_table_payload,
    build_policies_aggregates_payload,
    build_claims_table_payload,
    build_claims_aggregates_payload
)

# Initialize client
client = AtlasClient(base_url="http://localhost:21000", enabled=True)

# Publish policies metadata
payload = build_policies_table_payload()
client.publish(payload)

payload = build_policies_aggregates_payload()
client.publish(payload)

# Publish claims metadata
payload = build_claims_table_payload()
client.publish(payload)

payload = build_claims_aggregates_payload()
client.publish(payload)
```

## What Gets Published

### Database
- `warehouse@postgres` - Main warehouse database

### Fact Tables
- `warehouse.fact_policies@postgres` - Policies fact table
- `warehouse.fact_claims@postgres` - Claims fact table

### Gold Tables
- `warehouse.gold_policies_by_customer@postgres` - Policies aggregations
- `warehouse.gold_claims_by_policy@postgres` - Claims aggregations

### ETL Processes
- `policies_fact_etl@airflow` - Policies fact ETL
- `policies_aggregates_etl@airflow` - Policies aggregation ETL
- `claims_fact_etl@airflow` - Claims fact ETL
- `claims_aggregates_etl@airflow` - Claims aggregation ETL

## Viewing in Atlas UI

1. **Access Atlas UI**: http://localhost:21000
2. **Search for entities**:
   - Search: `warehouse.fact_policies`
   - Search: `warehouse.fact_claims`
   - Search: `policies_fact_etl`
   - Search: `claims_fact_etl`
3. **View lineage**: Click on any entity to see data lineage graphs

## Troubleshooting

### Entities Don't Appear

1. **Check if published**:
   ```bash
   python publish_atlas_metadata.py --dry-run
   ```

2. **Check Atlas logs**:
   ```bash
   docker-compose logs atlas
   ```

3. **Verify Atlas is accessible**:
   ```bash
   curl http://localhost:21000/api/atlas/admin/version
   ```

### See Only Default Entities

- Default entities come with Atlas installation
- Your entities appear after publishing
- Use search to find your entities (they won't be in default views)

### Publishing Fails

- Check Atlas URL is correct
- Verify Atlas service is running: `docker-compose ps atlas`
- Check network connectivity
- Review error messages in logs

## Best Practices

1. **Publish after pipeline runs**: Metadata is automatically published
2. **Publish manually for initial setup**: Use `publish_atlas_metadata.py` once
3. **Verify in UI**: Always check Atlas UI after publishing
4. **Use search**: Search for qualified names to find your entities
5. **Check lineage**: Verify data lineage graphs show correct relationships

## Updating Metadata

If you change table schemas or ETL processes:

1. Update payload builders in `src/utils/atlas_payloads.py`
2. Re-publish metadata:
   ```bash
   python publish_atlas_metadata.py
   ```

Atlas will update existing entities or create new ones as needed.


