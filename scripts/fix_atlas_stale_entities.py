"""
Fix stale Atlas entity references.

This script helps resolve "invalid/not found" GUID errors in Atlas UI
by re-publishing all entities and clearing stale references.
"""
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path if package not installed
try:
    from src.utils.atlas import AtlasClient
    from src.utils.atlas_payloads import (
        build_policies_table_payload,
        build_policies_aggregates_payload,
        build_claims_table_payload,
        build_claims_aggregates_payload
    )
except ImportError:
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.utils.atlas import AtlasClient
    from src.utils.atlas_payloads import (
        build_policies_table_payload,
        build_policies_aggregates_payload,
        build_claims_table_payload,
        build_claims_aggregates_payload
    )


def delete_entity_by_qualified_name(atlas_url: str, entity_type: str, qualified_name: str) -> bool:
    """
    Delete an entity by its qualified name.
    
    Args:
        atlas_url: Atlas API URL
        entity_type: Entity type (e.g., "hive_table", "Process", "hive_db")
        qualified_name: Qualified name of the entity
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        url = f"{atlas_url}/api/atlas/v2/entity/uniqueAttribute/type/{entity_type}"
        params = {"attr:qualifiedName": qualified_name}
        
        # First, get the entity to find its GUID
        response = requests.get(url, params=params, auth=("admin", "admin"), timeout=5)
        
        if response.status_code == 200:
            entity = response.json()
            guid = entity.get("entity", {}).get("guid")
            
            if guid:
                # Delete by GUID
                delete_url = f"{atlas_url}/api/atlas/v2/entity/guid/{guid}"
                delete_response = requests.delete(delete_url, auth=("admin", "admin"), timeout=5)
                return delete_response.status_code in [200, 204]
        
        return False
    except Exception as e:
        print(f"  [WARN] Error deleting {qualified_name}: {e}")
        return False


def clear_stale_entities(atlas_url: str = "http://localhost:21000") -> None:
    """
    Clear all warehouse-related entities from Atlas.
    
    This helps resolve stale GUID references.
    """
    print("=" * 60)
    print("Clearing Stale Atlas Entities")
    print("=" * 60)
    print(f"Atlas URL: {atlas_url}")
    print()
    
    # Entities to delete (in reverse dependency order: processes, tables, databases)
    entities_to_delete = [
        ("Process", "policies_fact_etl@airflow"),
        ("Process", "policies_aggregates_etl@airflow"),
        ("Process", "claims_fact_etl@airflow"),
        ("Process", "claims_aggregates_etl@airflow"),
        ("hive_table", "warehouse.gold_policies_by_customer@postgres"),
        ("hive_table", "warehouse.gold_claims_by_policy@postgres"),
        ("hive_table", "warehouse.fact_policies@postgres"),
        ("hive_table", "warehouse.fact_claims@postgres"),
        ("hive_db", "warehouse@postgres"),
    ]
    
    deleted_count = 0
    for entity_type, qualified_name in entities_to_delete:
        print(f"Deleting {entity_type}: {qualified_name}...", end=" ")
        if delete_entity_by_qualified_name(atlas_url, entity_type, qualified_name):
            print("[OK]")
            deleted_count += 1
        else:
            print("[SKIP] (not found or already deleted)")
    
    print()
    print(f"Deleted {deleted_count} entities")
    print("=" * 60)
    print()


def republish_all_entities(atlas_url: str = "http://localhost:21000") -> None:
    """
    Re-publish all entities to Atlas.
    """
    print("=" * 60)
    print("Re-publishing All Entities")
    print("=" * 60)
    print()
    
    client = AtlasClient(base_url=atlas_url)
    
    # Build and publish all payloads
    payloads = [
        build_policies_table_payload(),
        build_policies_aggregates_payload(),
        build_claims_table_payload(),
        build_claims_aggregates_payload(),
    ]
    
    for payload in payloads:
        try:
            client.publish(payload)
            print("[OK] Published payload")
        except Exception as e:
            print(f"[ERROR] Failed to publish: {e}")
    
    print()
    print("=" * 60)
    print("Re-publishing complete!")
    print("=" * 60)
    print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix stale Atlas entity references"
    )
    parser.add_argument(
        "--atlas-url",
        default="http://localhost:21000",
        help="Atlas API URL"
    )
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="Only clear entities, don't re-publish"
    )
    parser.add_argument(
        "--republish-only",
        action="store_true",
        help="Only re-publish, don't clear first"
    )
    
    args = parser.parse_args()
    
    if not args.republish_only:
        print("Step 1: Clearing stale entities...")
        print()
        clear_stale_entities(atlas_url=args.atlas_url)
    
    if not args.clear_only:
        print("Step 2: Re-publishing all entities...")
        print()
        republish_all_entities(atlas_url=args.atlas_url)
    
    print()
    print("=" * 60)
    print("Fix Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Clear your browser cache (Ctrl+Shift+Delete)")
    print("2. Refresh Atlas UI (http://localhost:21000)")
    print("3. Search for: warehouse, fact_policies, fact_claims")
    print()
    print("If the error persists:")
    print("1. Restart Atlas: docker-compose restart atlas")
    print("2. Wait 30 seconds for Atlas to restart")
    print("3. Run this script again")
    print()


if __name__ == "__main__":
    main()

