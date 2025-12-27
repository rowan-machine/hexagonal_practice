# Atlas Quick Reference

Quick reference for viewing and using Atlas documentation.

## Viewing Atlas Documentation

### 1. Mock Atlas (Development)
```bash
python mock_atlas.py
# View payloads in console output
```

### 2. Real Atlas (Production)
```bash
# Access web UI
open http://localhost:21000

# Or via Docker
docker-compose up -d atlas
# Then visit http://localhost:21000
```

### 3. Manifest File
```bash
cat metadata/atlas_manifest.yml
# or
less metadata/atlas_manifest.yml
```

### 4. API Query
```python
import requests
response = requests.get(
    "http://localhost:21000/api/atlas/v2/entity/uniqueAttribute/type/hive_table",
    params={"attr:qualifiedName": "warehouse.fact_policies@postgres"}
)
print(response.json())
```

## Common Entities

| Entity | Qualified Name | Type |
|--------|---------------|------|
| Warehouse DB | `warehouse@postgres` | hive_db |
| Fact Policies | `warehouse.fact_policies@postgres` | hive_table |
| Fact Claims | `warehouse.fact_claims@postgres` | hive_table |
| Gold Policies | `warehouse.gold_policies_by_customer@postgres` | hive_table |
| Gold Claims | `warehouse.gold_claims_by_policy@postgres` | hive_table |

## Publishing Metadata

```python
from src.utils.atlas import AtlasClient
from src.utils.atlas_payloads import build_policies_table_payload

client = AtlasClient(base_url="http://localhost:21000", enabled=True)
payload = build_policies_table_payload()
client.publish(payload)
```

## Files

- **Manifest**: `metadata/atlas_manifest.yml`
- **Payload Builders**: `src/utils/atlas_payloads.py`
- **Client**: `src/utils/atlas.py`
- **Mock Server**: `mock_atlas.py`
- **Full Guide**: `docs/ATLAS_GUIDE.md`

