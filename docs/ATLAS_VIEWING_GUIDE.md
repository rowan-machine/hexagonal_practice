# Viewing Atlas Schemas and Entities

Complete guide for viewing published metadata in Apache Atlas UI.

## Quick Start

### Automated Setup (Recommended)

After starting Docker services, run the complete Atlas setup:

```bash
# Publish, verify, and query Atlas entities all at once
make atlas-setup
```

This command will:
1. Publish all metadata to Atlas
2. Verify entities were published successfully
3. Query Atlas to show what was found

### Manual Setup

#### 1. Publish Metadata First

**Important**: Metadata must be published before it appears in Atlas UI.

```bash
# Publish all metadata to Atlas
python scripts/publish_atlas_metadata.py --atlas-url http://localhost:21000

# Or use Makefile
make atlas-publish
```

### 2. Access Atlas UI

1. **Open Browser**: Navigate to `http://localhost:21000`
2. **Login**: 
   - Username: `admin`
   - Password: `admin`
   - (Default credentials - change in production!)

### 3. Search for Your Entities

Once logged in, use the search bar at the top:

- Search for: `warehouse` (database)
- Search for: `fact_policies` (policies fact table)
- Search for: `fact_claims` (claims fact table)
- Search for: `gold_policies` (gold policies table)
- Search for: `gold_claims` (gold claims table)

### 4. Browse by Type

1. Click **"Browse"** in the left menu
2. Select entity type:
   - `hive_db` - Databases
   - `hive_table` - Tables
   - `Process` - ETL processes
3. Browse all entities of that type

## Entity Reference

### Databases
- **Name**: `warehouse`
- **Qualified Name**: `warehouse@postgres`
- **Type**: `hive_db`

### Fact Tables
- **fact_policies**
  - Qualified Name: `warehouse.fact_policies@postgres`
  - Type: `hive_table`
- **fact_claims**
  - Qualified Name: `warehouse.fact_claims@postgres`
  - Type: `hive_table`

### Gold Tables
- **gold_policies_by_customer**
  - Qualified Name: `warehouse.gold_policies_by_customer@postgres`
  - Type: `hive_table`
- **gold_claims_by_policy**
  - Qualified Name: `warehouse.gold_claims_by_policy@postgres`
  - Type: `hive_table`

### ETL Processes
- **policies_fact_etl**
  - Qualified Name: `policies_fact_etl@airflow`
  - Type: `Process`
- **policies_aggregates_etl**
  - Qualified Name: `policies_aggregates_etl@airflow`
  - Type: `Process`
- **claims_fact_etl**
  - Qualified Name: `claims_fact_etl@airflow`
  - Type: `Process`
- **claims_aggregates_etl**
  - Qualified Name: `claims_aggregates_etl@airflow`
  - Type: `Process`

## Viewing Data Lineage

### Step-by-Step

1. **Search for Entity**: Use search bar to find a table (e.g., `fact_policies`)
2. **Click Entity**: Click on the entity name in search results
3. **View Lineage Tab**: Click "Lineage" tab in entity details
4. **Explore Graph**: 
   - See where data comes from (inputs)
   - See where data goes (outputs)
   - See transformation processes

### Example Lineage Flow

```
Source Data
    ↓
policies_fact_etl (Process)
    ↓
warehouse.fact_policies@postgres (Table)
    ↓
policies_aggregates_etl (Process)
    ↓
warehouse.gold_policies_by_customer@postgres (Table)
```

## Viewing Schema Details

1. **Find Table**: Search for table name (e.g., `fact_policies`)
2. **Click Entity**: Open entity details
3. **View Schema**: 
   - See all columns
   - See data types
   - See relationships
   - See tags and classifications

## Troubleshooting

### Entities Not Showing Up

**Step 1: Verify Publishing**
```bash
# Complete setup (publish, verify, query)
make atlas-setup

# Or step by step:
make atlas-publish    # Publish metadata
make atlas-verify     # Verify entities
make atlas-query      # Query entities

# Manual commands:
python scripts/verify_atlas_entities.py
python scripts/publish_atlas_metadata.py --atlas-url http://localhost:21000
```

**Step 2: Check Authentication**
- Atlas UI requires login (admin/admin by default)
- Make sure you're logged in before searching

**Step 3: Check Atlas is Running**
```bash
# Check container status
docker-compose ps atlas

# Check Atlas health
curl http://localhost:21000/api/atlas/admin/version
```

**Step 4: Try Different Search Terms**
- Use exact qualified names if partial search doesn't work
- Try browsing by type instead of searching
- Refresh the page after publishing

### Search Not Finding Entities

1. **Use Browse Instead**: Click "Browse" → Select type → Find your entities
2. **Try Exact Name**: Use the full qualified name
3. **Check Entity Type**: Make sure you're searching the right type
4. **Wait a Moment**: Atlas may need a moment to index new entities

### Authentication Issues

If you get 401 errors when publishing:

```bash
# Publish with explicit authentication
python scripts/publish_atlas_metadata.py \
  --atlas-url http://localhost:21000 \
  --username admin \
  --password admin
```

## Querying via API

### Using Makefile Commands

```bash
# Query via Python script (recommended)
make atlas-query

# Query via curl
make atlas-query-curl

# Debug payload structure (see what gets published)
make atlas-debug-payload
```

### Using Python Script

```bash
python scripts/query_atlas_entities.py --search warehouse
```

### Using curl

```bash
curl -u admin:admin "http://localhost:21000/api/atlas/v2/search/basic?query=warehouse"
```

### Using Python Code

```python
import requests

# Search for entities
response = requests.get(
    "http://localhost:21000/api/atlas/v2/search/basic",
    params={"query": "warehouse"},
    auth=("admin", "admin")
)

entities = response.json()
for entity in entities.get("entities", []):
    print(entity["attributes"]["qualifiedName"])
```

## Debugging Atlas Payloads

If entities aren't publishing correctly, inspect the payload structure:

```bash
# View policies table payload structure
make atlas-debug-payload

# Or manually:
python -c "from src.utils.atlas_payloads import build_policies_table_payload; import json; payload = build_policies_table_payload(); print(json.dumps(payload, indent=2))"
```

This shows the exact JSON structure being sent to Atlas, which helps debug:
- Missing required fields
- Incorrect entity references
- Payload format issues

## Next Steps

- **[ATLAS_GUIDE.md](ATLAS_GUIDE.md)** → Complete Atlas guide
- **[ATLAS_PUBLISHING.md](ATLAS_PUBLISHING.md)** → Publishing metadata
- **[ATLAS_TROUBLESHOOTING.md](ATLAS_TROUBLESHOOTING.md)** → Troubleshooting
