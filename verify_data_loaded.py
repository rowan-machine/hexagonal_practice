"""
Script to verify data is loaded in the warehouse database.

Verifies that pipeline execution has successfully loaded data into:
- Bronze tables (raw data)
- Silver tables (processed data)
- Gold tables (aggregated data)

Usage:
    python verify_data_loaded.py
    
    # Check specific database
    python verify_data_loaded.py --db-path warehouse.db
    
    # Check Docker PostgreSQL
    python verify_data_loaded.py --postgres
"""
import argparse
import sys
from typing import Dict, Any, Optional
import sqlite3

# Optional PostgreSQL support
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def check_sqlite(db_path: str) -> Dict[str, Any]:
    """Check data in SQLite database."""
    results = {
        "database": db_path,
        "type": "sqlite",
        "tables": {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check each table
        tables = [
            "claims_bronze", "claims_silver", "claims_gold",
            "policies_bronze", "policies_silver", "policies_gold"
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results["tables"][table] = {
                    "count": count,
                    "status": "exists" if count > 0 else "empty"
                }
            except sqlite3.OperationalError:
                results["tables"][table] = {
                    "count": 0,
                    "status": "missing"
                }
        
        conn.close()
        return results
        
    except Exception as e:
        return {
            "database": db_path,
            "type": "sqlite",
            "error": str(e),
            "tables": {}
        }


def check_postgres(
    host: str = "localhost",
    port: int = 5433,
    database: str = "warehouse",
    user: str = "warehouse",
    password: str = "warehouse"
) -> Dict[str, Any]:
    """Check data in PostgreSQL database."""
    if not HAS_PSYCOPG2:
        return {
            "database": f"{database}@{host}:{port}",
            "type": "postgres",
            "error": "psycopg2 not installed. Install with: pip install psycopg2-binary",
            "tables": {}
        }
    
    results = {
        "database": f"{database}@{host}:{port}",
        "type": "postgres",
        "tables": {}
    }
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Check each table
        tables = [
            "claims_bronze", "claims_silver", "claims_gold",
            "policies_bronze", "policies_silver", "policies_gold"
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results["tables"][table] = {
                    "count": count,
                    "status": "exists" if count > 0 else "empty"
                }
            except psycopg2.ProgrammingError:
                results["tables"][table] = {
                    "count": 0,
                    "status": "missing"
                }
        
        conn.close()
        return results
        
    except Exception as e:
        return {
            "database": f"{database}@{host}:{port}",
            "type": "postgres",
            "error": str(e),
            "tables": {}
        }


def verify_data_loaded(
    db_path: Optional[str] = None,
    use_postgres: bool = False,
    postgres_host: str = "localhost",
    postgres_port: int = 5433
) -> Dict[str, Any]:
    """
    Verify data is loaded in the warehouse.
    
    Returns:
        Dictionary with verification results
    """
    print("=" * 60)
    print("Verifying Data Loaded in Warehouse")
    print("=" * 60)
    
    if use_postgres:
        print(f"Checking PostgreSQL: {postgres_host}:{postgres_port}")
        results = check_postgres(host=postgres_host, port=postgres_port)
    else:
        db_path = db_path or "warehouse.db"
        print(f"Checking SQLite: {db_path}")
        results = check_sqlite(db_path)
    
    print()
    
    if "error" in results:
        print(f"[ERROR] {results['error']}")
        return results
    
    # Print results
    total_records = 0
    all_loaded = True
    
    for table, info in results["tables"].items():
        count = info["count"]
        status = info["status"]
        total_records += count
        
        if status == "exists":
            print(f"  [OK] {table}: {count} records")
        elif status == "empty":
            print(f"  [EMPTY] {table}: 0 records")
            all_loaded = False
        else:
            print(f"  [MISSING] {table}: table does not exist")
            all_loaded = False
    
    print()
    print("=" * 60)
    print(f"Summary: {total_records} total records across all tables")
    
    if all_loaded and total_records > 0:
        print("[SUCCESS] All tables have data loaded!")
        results["status"] = "success"
    elif total_records > 0:
        print("[PARTIAL] Some tables are missing or empty")
        results["status"] = "partial"
    else:
        print("[FAILED] No data found in any tables")
        results["status"] = "failed"
    
    print("=" * 60)
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify data is loaded in warehouse database"
    )
    parser.add_argument(
        "--db-path",
        default="warehouse.db",
        help="Path to SQLite database (default: warehouse.db)"
    )
    parser.add_argument(
        "--postgres",
        action="store_true",
        help="Use PostgreSQL instead of SQLite"
    )
    parser.add_argument(
        "--postgres-host",
        default="localhost",
        help="PostgreSQL host (default: localhost)"
    )
    parser.add_argument(
        "--postgres-port",
        type=int,
        default=5433,
        help="PostgreSQL port (default: 5433)"
    )
    
    args = parser.parse_args()
    
    results = verify_data_loaded(
        db_path=args.db_path,
        use_postgres=args.postgres,
        postgres_host=args.postgres_host,
        postgres_port=args.postgres_port
    )
    
    if results.get("status") == "success":
        sys.exit(0)
    elif results.get("status") == "partial":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

