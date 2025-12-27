"""
Query Atlas to see what entities are actually published.

This script helps verify what's in Atlas and troubleshoot publishing issues.
"""
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path if package not installed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def query_atlas(atlas_url: str = "http://localhost:21000", username: str = "admin", password: str = "admin") -> Dict[str, Any]:
    """
    Query Atlas for all entities.
    
    Args:
        atlas_url: Atlas API URL
        username: Atlas username
        password: Atlas password
        
    Returns:
        Dictionary with search results
    """
    url = f"{atlas_url.rstrip('/')}/api/atlas/v2/search/basic"
    
    # Try with authentication
    auth = (username, password) if username and password else None
    
    try:
        # Search for all entities
        response = requests.get(
            url,
            params={"query": "*"},
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 401:
            print("Authentication required. Trying with admin/admin...")
            response = requests.get(
                url,
                params={"query": "*"},
                auth=("admin", "admin"),
                timeout=10
            )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Atlas: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text[:200]}")
        return {}


def search_entities(atlas_url: str = "http://localhost:21000", search_term: str = "warehouse") -> List[Dict[str, Any]]:
    """
    Search for specific entities in Atlas.
    
    Args:
        atlas_url: Atlas API URL
        search_term: Search term (e.g., "warehouse", "fact_policies")
        
    Returns:
        List of matching entities
    """
    url = f"{atlas_url.rstrip('/')}/api/atlas/v2/search/basic"
    
    try:
        # Try without auth first
        response = requests.get(
            url,
            params={"query": search_term},
            timeout=10
        )
        
        if response.status_code == 401:
            # Try with auth
            response = requests.get(
                url,
                params={"query": search_term},
                auth=("admin", "admin"),
                timeout=10
            )
        
        response.raise_for_status()
        results = response.json()
        return results.get("entities", [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching Atlas: {e}")
        return []


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Atlas entities")
    parser.add_argument(
        "--atlas-url",
        default="http://localhost:21000",
        help="Atlas API URL"
    )
    parser.add_argument(
        "--search",
        default="warehouse",
        help="Search term (default: warehouse)"
    )
    parser.add_argument(
        "--username",
        default="admin",
        help="Atlas username"
    )
    parser.add_argument(
        "--password",
        default="admin",
        help="Atlas password"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Querying Apache Atlas")
    print("=" * 60)
    print(f"Atlas URL: {args.atlas_url}")
    print(f"Search term: {args.search}")
    print()
    
    # Search for entities
    entities = search_entities(args.atlas_url, args.search)
    
    if entities:
        print(f"Found {len(entities)} entities matching '{args.search}':")
        print()
        for i, entity in enumerate(entities, 1):
            entity_type = entity.get("typeName", "unknown")
            attributes = entity.get("attributes", {})
            qualified_name = attributes.get("qualifiedName", "unknown")
            name = attributes.get("name", qualified_name)
            
            print(f"  {i}. {name}")
            print(f"     Type: {entity_type}")
            print(f"     Qualified Name: {qualified_name}")
            print()
    else:
        print(f"No entities found matching '{args.search}'")
        print()
        print("This could mean:")
        print("  1. Entities haven't been published yet")
        print("  2. Authentication is required (try with --username and --password)")
        print("  3. Atlas is not running or not accessible")
        print()
        print("To publish entities, run:")
        print("  python scripts/publish_atlas_metadata.py")
    
    # Also try to get all entities
    print("=" * 60)
    print("Querying all entities...")
    print("=" * 60)
    
    all_results = query_atlas(args.atlas_url, args.username, args.password)
    total_count = all_results.get("approximateCount", 0)
    
    if total_count > 0:
        print(f"Total entities in Atlas: {total_count}")
        entities_list = all_results.get("entities", [])
        if entities_list:
            print(f"\nFirst {min(10, len(entities_list))} entities:")
            for i, entity in enumerate(entities_list[:10], 1):
                entity_type = entity.get("typeName", "unknown")
                attributes = entity.get("attributes", {})
                qualified_name = attributes.get("qualifiedName", "unknown")
                name = attributes.get("name", qualified_name)
                print(f"  {i}. {name} ({entity_type})")
    else:
        print("No entities found in Atlas")
        print("\nTo view entities in Atlas UI:")
        print("  1. Open http://localhost:21000 in your browser")
        print("  2. Login with admin/admin (if required)")
        print("  3. Use the search bar to find entities")
        print("\nTo publish entities:")
        print("  python scripts/publish_atlas_metadata.py")


if __name__ == "__main__":
    main()

