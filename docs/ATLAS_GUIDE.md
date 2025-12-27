# Apache Atlas Guide

This guide explains how to use Apache Atlas for data lineage and governance in the pipeline system.

## Overview

Apache Atlas provides data lineage tracking and governance for the warehouse. It documents:
- **Databases**: Warehouse database structure
- **Tables**: Fact and gold tables with schemas
- **Processes**: ETL processes and their input/output lineage
- **Lineage**: Data flow from source to destination

## Quick Start

### 1. Using Mock Atlas (Local Development)

For local development without a full Atlas installation:

```bash
# Start mock Atlas server
python mock_atlas.py
```

The mock server will:
- Listen on `http://localhost:21000`
- Accept POST requests to `/api/atlas/v2/entity`
- Print received payloads to console
- Return success responses

### 2. Using Real Atlas (Docker)

With Docker Compose:

```bash
# Start all services including Atlas
docker-compose up -d

# Atlas will be available at
# http://localhost:21000
```

### 3. Publishing Metadata

```python
from src.utils.atlas import AtlasClient
from src.utils.atlas_payloads import build_policies_table_payload

# Initialize client
client = AtlasClient(
    base_url="http://localhost:21000",
    enabled=True
)

# Build and publish payload
payload = build_policies_table_payload()
client.publish(payload)
```

## Viewing Atlas Documentation

### Option 1: Atlas Web UI (Production)

1. **Access UI**: Navigate to `http://localhost:21000` (or your Atlas URL)
2. **Login**: Default credentials (if configured)
3. **Search**: Use search bar to find entities
4. **Browse**: Navigate to databases, tables, and processes
5. **Lineage**: Click on entities to view data lineage graphs

### Option 2: Mock Atlas Console (Development)

When using `mock_atlas.py`, metadata is printed to console:

```
============================================================
Atlas Payload Received - 2024-01-15 10:30:45
============================================================

📦 Entities: 3

  Entity 1:
    Type: hive_db
    Name: warehouse
    Qualified Name: warehouse@postgres

  Entity 2:
    Type: hive_table
    Name: fact_policies
    Qualified Name: warehouse.fact_policies@postgres

  Entity 3:
    Type: Process
    Name: policies_fact_etl
    Qualified Name: policies_fact_etl@airflow
    Inputs: 0
    Outputs: 1
      - warehouse.fact_policies@postgres

📄 Full Payload JSON:
{
  "entities": [...]
}
============================================================
```

### Option 3: Manifest File (Reference)

The `metadata/atlas_manifest.yml` file documents all entities:

```yaml
fact_policies:
  name: fact_policies
  qualifiedName: warehouse.fact_policies@postgres
  type: hive_table
  columns:
    - name: policy_id
      type: string
```

View with:
```bash
cat metadata/atlas_manifest.yml
# or
less metadata/atlas_manifest.yml
```

### Option 4: Atlas API (Programmatic)

Query Atlas API directly:

```python
import requests

# Get entity by qualified name
response = requests.get(
    "http://localhost:21000/api/atlas/v2/entity/uniqueAttribute/type/hive_table",
    params={"attr:qualifiedName": "warehouse.fact_policies@postgres"}
)

entity = response.json()
print(json.dumps(entity, indent=2))
```

## Available Entities

### Databases

- **warehouse**: Main data warehouse database
  - Qualified Name: `warehouse@postgres`

### Fact Tables

- **fact_policies**: Row-level policies data
  - Qualified Name: `warehouse.fact_policies@postgres`
- **fact_claims**: Row-level claims data
  - Qualified Name: `warehouse.fact_claims@postgres`

### Gold Tables

- **gold_policies_by_customer**: Aggregated policies by customer
  - Qualified Name: `warehouse.gold_policies_by_customer@postgres`
- **gold_claims_by_policy**: Aggregated claims by policy
  - Qualified Name: `warehouse.gold_claims_by_policy@postgres`

### ETL Processes

- **policies_fact_etl**: Policies fact table ETL
  - Inputs: `raw_policies_json`
  - Outputs: `warehouse.fact_policies@postgres`
- **policies_aggregates_etl**: Policies aggregation ETL
  - Inputs: `warehouse.fact_policies@postgres`
  - Outputs: `warehouse.gold_policies_by_customer@postgres`
- **claims_fact_etl**: Claims fact table ETL
  - Inputs: `raw_claims_json`
  - Outputs: `warehouse.fact_claims@postgres`
- **claims_aggregates_etl**: Claims aggregation ETL
  - Inputs: `warehouse.fact_claims@postgres`
  - Outputs: `warehouse.gold_claims_by_policy@postgres`

## Data Lineage

### Policies Lineage

```
raw_policies_json
    ↓
policies_fact_etl
    ↓
fact_policies
    ↓
policies_aggregates_etl
    ↓
gold_policies_by_customer
```

### Claims Lineage

```
raw_claims_json
    ↓
claims_fact_etl
    ↓
fact_claims
    ↓
claims_aggregates_etl
    ↓
gold_claims_by_policy
```

## Payload Builders

All payloads are built using functions in `src/utils/atlas_payloads.py`:

- `build_policies_table_payload()`: Policies fact table and ETL
- `build_policies_aggregates_payload()`: Policies aggregation
- `build_claims_table_payload()`: Claims fact table and ETL
- `build_claims_aggregates_payload()`: Claims aggregation

## Configuration

### Enable/Disable Atlas

In pipeline code:

```python
# Disable for local development
client = AtlasClient(base_url="http://atlas:21000", enabled=False)

# Enable for production
client = AtlasClient(base_url="http://atlas:21000", enabled=True)
```

Via environment variable:

```bash
# In docker-compose.yml or .env
ATLAS_ENABLED=false  # Disable
ATLAS_ENABLED=true   # Enable
```

## Testing

### Test with Mock Atlas

1. Start mock server:
   ```bash
   python mock_atlas.py
   ```

2. In another terminal, publish metadata:
   ```python
   from src.utils.atlas import AtlasClient
   from src.utils.atlas_payloads import build_policies_table_payload
   
   client = AtlasClient(base_url="http://localhost:21000", enabled=True)
   payload = build_policies_table_payload()
   client.publish(payload)
   ```

3. Check mock server console for received payload

### Test with Real Atlas

1. Start Docker services:
   ```bash
   docker-compose up -d atlas
   ```

2. Wait for Atlas to be ready (check health):
   ```bash
   curl http://localhost:21000/api/atlas/admin/version
   ```

3. Publish metadata and verify in UI

## Troubleshooting

### Atlas Not Responding

- Check if service is running: `docker-compose ps`
- Check logs: `docker-compose logs atlas`
- Verify port: `curl http://localhost:21000/health`

### Payload Not Published

- Check if Atlas is enabled: `ATLAS_ENABLED=true`
- Check logs for errors
- Verify payload format matches Atlas API requirements
- Use mock Atlas to debug payload structure

### Can't View Lineage

- Ensure all entities are published (database, tables, processes)
- Verify qualified names match between inputs/outputs
- Check Atlas UI for entity relationships

## Best Practices

1. **Publish After Pipeline Steps**: Publish metadata after each major step
2. **Use Payload Builders**: Use functions in `atlas_payloads.py` for consistency
3. **Document in Manifest**: Keep `atlas_manifest.yml` updated
4. **Test Locally**: Use mock Atlas for development
5. **Verify Lineage**: Check lineage graphs in Atlas UI
6. **Monitor Publishing**: Log all publish attempts for debugging

## References

- **Manifest**: `metadata/atlas_manifest.yml` - All entities reference
- **Payload Builders**: `src/utils/atlas_payloads.py` - Payload generation
- **Client**: `src/utils/atlas.py` - Atlas API client
- **Mock Server**: `mock_atlas.py` - Local testing server
- **Atlas Documentation**: https://atlas.apache.org/

