"""
Script to publish all metadata to Apache Atlas.

This publishes all warehouse tables, databases, and ETL processes to Atlas
so they appear in the Atlas UI for data lineage and governance.

Usage:
    python publish_atlas_metadata.py
    
    # Or with custom Atlas URL
    python publish_atlas_metadata.py --atlas-url http://localhost:21000
"""
import argparse
import sys
from src.utils.atlas import AtlasClient
from src.utils.atlas_payloads import (
    build_policies_table_payload,
    build_policies_aggregates_payload,
    build_claims_table_payload,
    build_claims_aggregates_payload
)


def publish_all_metadata(atlas_url: str = "http://localhost:21000", enabled: bool = True):
    """
    Publish all metadata to Atlas.
    
    Args:
        atlas_url: Atlas API URL
        enabled: Whether to actually publish (False for dry-run)
    """
    client = AtlasClient(base_url=atlas_url, enabled=enabled)
    
    print("=" * 60)
    print("Publishing Metadata to Apache Atlas")
    print("=" * 60)
    print(f"Atlas URL: {atlas_url}")
    print(f"Enabled: {enabled}")
    print()
    
    # List of all payloads to publish
    payloads = [
        ("Policies Fact Table", build_policies_table_payload),
        ("Policies Aggregates", build_policies_aggregates_payload),
        ("Claims Fact Table", build_claims_table_payload),
        ("Claims Aggregates", build_claims_aggregates_payload),
    ]
    
    published_count = 0
    failed_count = 0
    
    for name, payload_builder in payloads:
        print(f"Publishing {name}...")
        try:
            payload = payload_builder()
            entity_count = len(payload.get("entities", []))
            print(f"  Entities: {entity_count}")
            
            client.publish(payload)
            published_count += entity_count
            print(f"  [OK] Published successfully")
        except Exception as e:
            failed_count += 1
            print(f"  [ERROR] Failed to publish: {e}")
        print()
    
    print("=" * 60)
    print(f"Summary: {published_count} entities published, {failed_count} failed")
    print("=" * 60)
    
    if failed_count > 0:
        print("\nSome entities failed to publish. Check the errors above.")
        return 1
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Publish metadata to Apache Atlas"
    )
    parser.add_argument(
        "--atlas-url",
        default="http://localhost:21000",
        help="Atlas API URL (default: http://localhost:21000)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually publish (default: False)"
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable publishing (same as --dry-run)"
    )
    
    args = parser.parse_args()
    
    enabled = not (args.dry_run or args.disable)
    
    exit_code = publish_all_metadata(
        atlas_url=args.atlas_url,
        enabled=enabled
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


