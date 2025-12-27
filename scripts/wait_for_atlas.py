"""
Wait for Apache Atlas to be ready.

This script checks if Atlas is responding on localhost:21000.
It's useful for knowing when Atlas is ready to accept metadata.
"""
import sys
import time
import requests
from pathlib import Path

# Add project root to path if package not installed
try:
    pass
except ImportError:
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def check_atlas_ready(url: str = "http://localhost:21000/api/atlas/admin/version", timeout: int = 5) -> bool:
    """
    Check if Atlas is ready.
    
    Args:
        url: Atlas version endpoint
        timeout: Request timeout in seconds
        
    Returns:
        True if Atlas is ready, False otherwise
    """
    try:
        response = requests.get(url, auth=('admin', 'admin'), timeout=timeout)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False


def wait_for_atlas(
    url: str = "http://localhost:21000/api/atlas/admin/version",
    max_wait: int = 120,
    check_interval: int = 2,
    quiet: bool = False
) -> bool:
    """
    Wait for Atlas to be ready.
    
    Args:
        url: Atlas version endpoint
        max_wait: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        quiet: If True, suppress progress messages
        
    Returns:
        True if Atlas became ready, False if timeout
    """
    elapsed = 0
    
    if not quiet:
        print(f"Waiting for Atlas at {url}...")
        print(f"Maximum wait time: {max_wait} seconds")
    
    while elapsed < max_wait:
        if check_atlas_ready(url):
            if not quiet:
                print(f"✓ Atlas is ready! (waited {elapsed} seconds)")
            return True
        
        if not quiet:
            remaining = max_wait - elapsed
            print(f"Waiting for Atlas... ({remaining} seconds remaining)", end='\r')
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    if not quiet:
        print(f"\n✗ Atlas did not become ready within {max_wait} seconds")
    return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wait for Apache Atlas to be ready")
    parser.add_argument(
        "--url",
        default="http://localhost:21000/api/atlas/admin/version",
        help="Atlas version endpoint URL"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=120,
        help="Maximum time to wait in seconds (default: 120)"
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=2,
        help="Time between checks in seconds (default: 2)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    success = wait_for_atlas(
        url=args.url,
        max_wait=args.max_wait,
        check_interval=args.check_interval,
        quiet=args.quiet
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

