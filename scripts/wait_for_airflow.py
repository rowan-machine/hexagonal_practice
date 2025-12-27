"""
Wait for Airflow webserver (gunicorn) to be ready.

This script checks if Airflow's webserver is responding on localhost:8080.
It's useful for knowing when the Airflow UI is ready to use.
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


def check_airflow_ready(url: str = "http://localhost:8080/health", timeout: int = 5) -> bool:
    """
    Check if Airflow webserver is ready.
    
    Args:
        url: Airflow health check endpoint
        timeout: Request timeout in seconds
        
    Returns:
        True if Airflow is ready, False otherwise
    """
    try:
        response = requests.get(url, timeout=timeout)
        # Airflow 2.x returns 200 OK when healthy
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False


def wait_for_airflow(
    url: str = "http://localhost:8080/health",
    max_wait: int = 400,
    interval: int = 5,
    verbose: bool = True
) -> bool:
    """
    Wait for Airflow webserver to be ready.
    
    Args:
        url: Airflow health check endpoint
        max_wait: Maximum time to wait in seconds (default: 5 minutes)
        interval: Check interval in seconds (default: 5 seconds)
        verbose: Print status messages
        
    Returns:
        True if Airflow became ready, False if timeout
    """
    start_time = time.time()
    attempt = 0
    
    if verbose:
        print(f"Waiting for Airflow webserver at {url}...")
        print(f"Maximum wait time: {max_wait} seconds")
        print(f"Check interval: {interval} seconds")
        print()
    
    while time.time() - start_time < max_wait:
        attempt += 1
        
        if check_airflow_ready(url):
            elapsed = int(time.time() - start_time)
            if verbose:
                print(f"✓ Airflow webserver is ready! (took {elapsed} seconds)")
                print(f"  Access the UI at: http://localhost:8080")
                print(f"  Default credentials: admin / admin")
            return True
        
        elapsed = int(time.time() - start_time)
        if verbose:
            print(f"  Attempt {attempt}: Airflow not ready yet... (elapsed: {elapsed}s)")
        
        time.sleep(interval)
    
    if verbose:
        print(f"✗ Timeout: Airflow webserver did not become ready after {max_wait} seconds")
        print(f"  Check logs with: docker-compose logs airflow")
        print(f"  Or check status with: docker-compose ps")
    return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Wait for Airflow webserver (gunicorn) to be ready"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8080/health",
        help="Airflow health check URL (default: http://localhost:8080/health)"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=300,
        help="Maximum time to wait in seconds (default: 300)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output (exit code only)"
    )
    
    args = parser.parse_args()
    
    success = wait_for_airflow(
        url=args.url,
        max_wait=args.max_wait,
        interval=args.interval,
        verbose=not args.quiet
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

