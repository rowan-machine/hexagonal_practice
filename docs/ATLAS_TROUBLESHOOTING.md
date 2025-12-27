# Atlas Troubleshooting

## Quick Setup and Verification

**Recommended**: Use the Makefile command for complete Atlas setup:

```bash
# After docker-compose up, run:
make atlas-setup
```

This will:
1. Publish all metadata to Atlas
2. Verify entities were published
3. Query Atlas to show results

**Individual commands**:
```bash
make atlas-publish        # Publish metadata
make atlas-verify        # Verify entities
make atlas-query         # Query entities
make atlas-query-curl    # Query via curl
make atlas-debug-payload # Debug payload structure
```

## Issue: Atlas Shows "Other Stuff" But Not Policies/Claims

**Problem**: Atlas UI shows default/example entities but not your policies and claims entities.

**Cause**: Metadata hasn't been published to Atlas yet.

**Solution**: Publish metadata:

```bash
# Recommended: Complete setup
make atlas-setup

# Or manually:
python scripts/publish_atlas_metadata.py --atlas-url http://localhost:21000
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

## Issue: "Invalid/Not Found" GUID Error in Atlas UI

**Error**: `Given instance guid ca68cccf-bc75-4c0b-a6de-522414e0779e is invalid/not found`

**Problem**: Browser or Atlas has cached a reference to an entity that was deleted or recreated.

**Solutions**:

1. **Quick Fix (Recommended)**:
   ```bash
   # Fix stale entities automatically
   make atlas-fix-stale
   
   # Or manually:
   python scripts/fix_atlas_stale_entities.py
   ```
   This will:
   - Delete all warehouse-related entities
   - Re-publish them with fresh GUIDs
   - Clear stale references

2. **Clear Browser Cache**:
   - Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
   - Clear cached images and files
   - Refresh Atlas UI

3. **Restart Atlas** (if error persists):
   ```bash
   docker-compose restart atlas
   # Wait 30 seconds, then:
   make atlas-fix-stale
   ```

4. **Manual Fix**:
   ```bash
   # Clear only (don't re-publish)
   python scripts/fix_atlas_stale_entities.py --clear-only
   
   # Re-publish only (don't clear first)
   python scripts/fix_atlas_stale_entities.py --republish-only
   ```

**Prevention**: 
- Always use `make atlas-fix-stale` after restarting Atlas
- Clear browser cache if you see GUID errors
- Re-publish entities if you modify the schema

## Issue: Default Entities Clutter the View

**Problem**: Atlas shows many default entities that aren't relevant.

**Solution**: 
- Default entities come with Atlas installation
- Use search to find your specific entities
- Filter by qualified name pattern: `warehouse.*`
- Filter by type: `hive_table` or `Process`

## Quick Verification

### Using Makefile (Recommended)

```bash
# Complete verification
make atlas-setup

# Or individual steps:
make atlas-verify      # Verify entities
make atlas-query       # Query entities
make atlas-query-curl  # Query via curl
```

### Using Scripts

```bash
# Verify entities
python scripts/verify_atlas_entities.py

# Query entities
python scripts/query_atlas_entities.py --search warehouse

# Query via curl
curl -u admin:admin "http://localhost:21000/api/atlas/v2/search/basic?query=warehouse"
```

### Using Python Code

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
            params={"attr:qualifiedName": entity},
            auth=("admin", "admin")
        )
        if response.status_code == 200:
            print(f"✓ Found: {entity}")
        else:
            print(f"✗ Not found: {entity} (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error checking {entity}: {e}")
```

## Debugging Payload Structure

If entities aren't publishing, inspect the payload structure:

```bash
# View payload structure (policies example)
make atlas-debug-payload

# This shows the exact JSON being sent to Atlas
```

**What to check**:
- Required fields are present (`typeName`, `attributes`, `qualifiedName`)
- Entity references use correct format (`uniqueAttributes`)
- No null or empty values in required fields
- Payload matches Atlas API v2 format

## Best Practices

1. **Use Makefile commands**: `make atlas-setup` for complete setup
2. **Publish after initial setup**: Run `make atlas-publish` once after Docker starts
3. **Verify after publishing**: Always run `make atlas-verify` to confirm
4. **Debug payloads**: Use `make atlas-debug-payload` if entities don't publish
5. **Pipelines auto-publish**: Metadata is published automatically when pipelines run
6. **Use search in UI**: Don't rely on default views
7. **Check logs**: Review Atlas logs if entities don't appear
8. **Mock for development**: Use `mock_atlas.py` for local testing

## Complete Workflow

After starting Docker:

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services to be ready
make wait-airflow

# 3. Setup Atlas (publish, verify, query)
make atlas-setup

# 4. View in browser
# Open http://localhost:21000
# Login: admin/admin
# Search for: warehouse, fact_policies, fact_claims
```


