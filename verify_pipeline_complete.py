"""
Comprehensive verification script for pipeline execution.

Verifies:
1. Data is loaded in warehouse (bronze, silver, gold tables)
2. Atlas entities are published
3. All components are working

Usage:
    python verify_pipeline_complete.py
    
    # Check PostgreSQL instead of SQLite
    python verify_pipeline_complete.py --postgres
"""
import sys
from typing import Tuple
import subprocess
from pathlib import Path


def run_script(script_name: str, *args) -> Tuple[bool, str]:
    """Run a verification script and return (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, script_name] + list(args),
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def main():
    """Main verification."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify pipeline execution is complete")
    parser.add_argument(
        "--postgres",
        action="store_true",
        help="Use PostgreSQL instead of SQLite"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Pipeline Execution Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 1. Verify data is loaded
    print("1. Verifying data is loaded in warehouse...")
    print("-" * 60)
    if args.postgres:
        success, output = run_script("verify_data_loaded.py", "--postgres")
    else:
        success, output = run_script("verify_data_loaded.py")
    
    print(output)
    if not success:
        all_passed = False
        print("[FAILED] Data verification failed")
    else:
        print("[OK] Data verification passed")
    print()
    
    # 2. Verify Atlas entities
    print("2. Verifying Atlas entities are published...")
    print("-" * 60)
    success, output = run_script("verify_atlas_entities.py")
    print(output)
    if not success:
        all_passed = False
        print("[FAILED] Atlas verification failed")
        print("\nTo publish Atlas metadata, run:")
        print("  python publish_atlas_metadata.py")
    else:
        print("[OK] Atlas verification passed")
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] All verifications passed!")
        print("=" * 60)
        return 0
    else:
        print("[FAILED] Some verifications failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

