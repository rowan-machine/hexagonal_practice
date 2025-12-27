# Atlas Troubleshooting

## Issue: Atlas Shows "Other Stuff" But Not Policies/Claims

**Problem**: Atlas UI shows default/example entities but not your policies and claims entities.

**Cause**: Metadata hasn't been published to Atlas yet.

**Solution**: Publish metadata using the script:

```bash
python publish_atlas_metadata.py
```

## Issue: 401 Unauthorized Errors

**Error**: `401 Client Error: Unauthorized`

**Causes**:
1. Atlas requires authentication
2. Default credentials not configured
3. Atlas security settings

**Solutions**:

1. **Check if authentication is required**:
   ```bash
   curl http://localhost:21000/api/atlas/admin/version
   ```

2. **Try with default credentials** (admin/admin):
   - The Atlas client will automatically retry with basic auth
   - If this doesn't work, you may need to configure Atlas authentication

3. **Disable authentication** (for development only):
   - Check Atlas configuration
   - Some Atlas Docker images have auth disabled by default

4. **Use mock Atlas for development**:
   ```bash
   python mock_atlas.py
   # Then publish to localhost:21000
   python publish_atlas_metadata.py --atlas-url http://localhost:21000
   ```

## Issue: Entities Don't Appear in Atlas UI

**Problem**: Published metadata but can't find entities in UI.

**Solutions**:

1. **Use Search**:
   - Atlas UI search bar
   - Search for: `warehouse.fact_policies`
   - Search for: `policies_fact_etl`

2. **Check Entity Types**:
   - Look under "hive_table" type
   - Look under "Process" type
   - Look under "hive_db" type

3. **Verify Publication**:
   ```python
   import requests
   response = requests.get(
       "http://localhost:21000/api/atlas/v2/search/basic",
       params={"query": "warehouse.fact_policies"}
   )
   print(response.json())
   ```

4. **Check Atlas Logs**:
   ```bash
   docker-compose logs atlas | grep -i "entity\|error"
   ```

## Issue: Default Entities Clutter the View

**Problem**: Atlas shows many default entities that aren't relevant.

**Solution**: 
- Default entities come with Atlas installation
- Use search to find your specific entities
- Filter by qualified name pattern: `warehouse.*`
- Filter by type: `hive_table` or `Process`

## Quick Verification

Run this to verify entities are published:

```python
import requests

# Search for your entities
entities = [
    "warehouse.fact_policies@postgres",
    "warehouse.fact_claims@postgres",
    "policies_fact_etl@airflow",
    "claims_fact_etl@airflow"
]

for entity in entities:
    try:
        response = requests.get(
            f"http://localhost:21000/api/atlas/v2/entity/uniqueAttribute/type/hive_table",
            params={"attr:qualifiedName": entity}
        )
        if response.status_code == 200:
            print(f"✓ Found: {entity}")
        else:
            print(f"✗ Not found: {entity} (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error checking {entity}: {e}")
```

## Best Practices

1. **Publish after initial setup**: Run `publish_atlas_metadata.py` once
2. **Pipelines auto-publish**: Metadata is published automatically when pipelines run
3. **Use search in UI**: Don't rely on default views
4. **Check logs**: Review Atlas logs if entities don't appear
5. **Mock for development**: Use `mock_atlas.py` for local testing


