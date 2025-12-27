"""
Fixed script to publish Atlas metadata with better error handling.

This script attempts multiple authentication methods and provides
detailed error messages.
"""
import sys
from pathlib import Path
from typing import Tuple, List, Optional
import requests

# Add project root to path if package not installed
try:
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
    from src.utils.atlas_payloads import (
        build_policies_table_payload,
        build_policies_aggregates_payload,
        build_claims_table_payload,
        build_claims_aggregates_payload
    )


def publish_with_auth(url: str, payload: dict, auth_methods: Optional[List] = None) -> Tuple[bool, str]:
    """
    Try publishing with multiple authentication methods.
    
    Returns:
        (success: bool, message: str)
    """
    if auth_methods is None:
        auth_methods = [
            None,  # No auth
            ("admin", "admin"),  # Default credentials
            ("admin", ""),  # Admin with empty password
        ]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for auth in auth_methods:
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers=headers,
                auth=auth
            )
            
            if response.status_code == 200:
                return True, f"Success (auth: {auth or 'none'})"
            elif response.status_code == 401:
                continue  # Try next auth method
            else:
                return False, f"Status {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.RequestException as e:
            if auth == auth_methods[-1]:  # Last attempt
                return False, f"Request failed: {str(e)}"
            continue
    
    return False, "All authentication methods failed (401 Unauthorized)"


def main():
    """Main entry point."""
    atlas_url = "http://localhost:21000"
    url = f"{atlas_url}/api/atlas/v2/entity"
    
    print("=" * 60)
    print("Publishing Atlas Metadata (Fixed)")
    print("=" * 60)
    print(f"Atlas URL: {atlas_url}")
    print(f"Endpoint: {url}")
    print()
    
    # Test Atlas connectivity first
    try:
        test_response = requests.get(f"{atlas_url}/api/atlas/admin/version", timeout=5)
        print(f"[OK] Atlas is reachable (version check: {test_response.status_code})")
    except Exception as e:
        print(f"[ERROR] Cannot reach Atlas: {e}")
        print("\nIs Atlas running? Try:")
        print("  docker-compose ps atlas")
        print("  docker-compose logs atlas")
        return 1
    
    print()
    
    # Publish all payloads
    payloads = [
        ("Policies Fact Table", build_policies_table_payload),
        ("Policies Aggregates", build_policies_aggregates_payload),
        ("Claims Fact Table", build_claims_table_payload),
        ("Claims Aggregates", build_claims_aggregates_payload),
    ]
    
    success_count = 0
    fail_count = 0
    
    for name, payload_builder in payloads:
        print(f"Publishing {name}...")
        try:
            payload = payload_builder()
            entity_count = len(payload.get("entities", []))
            print(f"  Entities: {entity_count}")
            
            success, message = publish_with_auth(url, payload)
            
            if success:
                print(f"  [OK] {message}")
                success_count += entity_count
            else:
                print(f"  [FAILED] {message}")
                fail_count += 1
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            fail_count += 1
        
        print()
    
    print("=" * 60)
    print(f"Summary: {success_count} entities published, {fail_count} failed")
    print("=" * 60)
    
    if fail_count > 0:
        print("\nTroubleshooting:")
        print("1. Check Atlas is running: docker-compose ps atlas")
        print("2. Check Atlas logs: docker-compose logs atlas")
        print("3. Try accessing Atlas UI: http://localhost:21000")
        print("4. Check authentication requirements in Atlas config")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

