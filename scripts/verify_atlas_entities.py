"""
Script to verify that entities are published in Atlas.

Checks if policies and claims entities exist in Atlas.
"""
import sys
import requests
from typing import List, Dict, Any


def check_entity(atlas_url: str, entity_type: str, qualified_name: str) -> bool:
    """
    Check if an entity exists in Atlas.
    
    Args:
        atlas_url: Atlas API URL
        entity_type: Entity type (e.g., "hive_table", "Process", "hive_db")
        qualified_name: Qualified name of the entity
        
    Returns:
        True if entity exists, False otherwise
    """
    try:
        url = f"{atlas_url}/api/atlas/v2/entity/uniqueAttribute/type/{entity_type}"
        params = {"attr:qualifiedName": qualified_name}
        
        # Try without auth first
        response = requests.get(url, params=params, timeout=5)
        
        # If 401, try with auth
        if response.status_code == 401:
            response = requests.get(url, params=params, timeout=5, auth=("admin", "admin"))
        
        return response.status_code == 200
    except Exception:
        return False


def verify_all_entities(atlas_url: str = "http://localhost:21000") -> Dict[str, Any]:
    """
    Verify all expected entities exist in Atlas.
    
    Returns:
        Dictionary with verification results
    """
    print("=" * 60)
    print("Verifying Atlas Entities")
    print("=" * 60)
    print(f"Atlas URL: {atlas_url}")
    print()
    
    # Expected entities
    entities = [
        ("warehouse@postgres", "hive_db", "Warehouse Database"),
        ("warehouse.fact_policies@postgres", "hive_table", "Fact Policies Table"),
        ("warehouse.fact_claims@postgres", "hive_table", "Fact Claims Table"),
        ("warehouse.gold_policies_by_customer@postgres", "hive_table", "Gold Policies Table"),
        ("warehouse.gold_claims_by_policy@postgres", "hive_table", "Gold Claims Table"),
        ("policies_fact_etl@airflow", "Process", "Policies Fact ETL"),
        ("policies_aggregates_etl@airflow", "Process", "Policies Aggregates ETL"),
        ("claims_fact_etl@airflow", "Process", "Claims Fact ETL"),
        ("claims_aggregates_etl@airflow", "Process", "Claims Aggregates ETL"),
    ]
    
    found = []
    missing = []
    
    for qualified_name, entity_type, description in entities:
        exists = check_entity(atlas_url, entity_type, qualified_name)
        if exists:
            found.append((qualified_name, description))
            print(f"  [OK] {description}: {qualified_name}")
        else:
            missing.append((qualified_name, description))
            print(f"  [MISSING] {description}: {qualified_name}")
    
    print()
    print("=" * 60)
    print(f"Summary: {len(found)} found, {len(missing)} missing")
    print("=" * 60)
    
    if missing:
        print("\nMissing entities. Publish metadata using:")
        print("  python publish_atlas_metadata.py")
        return {"found": len(found), "missing": len(missing), "status": "incomplete"}
    else:
        print("\nAll entities found in Atlas!")
        return {"found": len(found), "missing": len(missing), "status": "complete"}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify entities in Atlas")
    parser.add_argument(
        "--atlas-url",
        default="http://localhost:21000",
        help="Atlas API URL"
    )
    
    args = parser.parse_args()
    
    result = verify_all_entities(atlas_url=args.atlas_url)
    
    if result["status"] == "complete":
        sys.exit(0)
    else:
        sys.exit(1)


