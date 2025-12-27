"""Quick verification script for system setup."""
import sys
import json
from pathlib import Path

def verify_imports():
    """Verify all key imports work."""
    print("Checking imports...")
    try:
        from src.pipelines import ClaimsPipeline, PoliciesPipeline
        from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
        from src.utils.database import DatabaseManager
        from src.utils.config_loader import ConfigLoader
        print("  [OK] All imports successful")
        return True
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
        return False

def verify_database():
    """Verify database can be accessed."""
    print("Checking database...")
    try:
        from src.utils.database import DatabaseManager
        db = DatabaseManager("warehouse.db")
        # Check if tables exist
        tables = db.query("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t['name'] for t in tables]
        expected_tables = [
            'claims_bronze', 'claims_silver', 'claims_gold',
            'policies_bronze', 'policies_silver', 'policies_gold'
        ]
        print(f"  [OK] Database accessible ({len(tables)} tables found)")
        
        # Check for expected tables
        missing = [t for t in expected_tables if t not in table_names]
        if missing:
            print(f"  [WARN] Missing tables: {missing}")
        else:
            print("  [OK] All expected tables exist")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Database error: {e}")
        return False

def verify_data_files():
    """Verify data files exist."""
    print("Checking data files...")
    files = [
        "data/raw_claims.json",
        "data/raw_policies.json",
        "config/claims_pipeline.yml",
        "config/policies_pipeline.yml"
    ]
    all_exist = all(Path(f).exists() for f in files)
    if all_exist:
        print("  [OK] All data files exist")
        
        # Check JSON file counts
        try:
            with open("data/raw_claims.json") as f:
                claims_data = json.load(f)
                claims_count = len(claims_data.get("claims", []))
                print(f"  [OK] raw_claims.json: {claims_count} records")
        except Exception as e:
            print(f"  [WARN] Error reading raw_claims.json: {e}")
        
        try:
            with open("data/raw_policies.json") as f:
                policies_data = json.load(f)
                policies_count = len(policies_data.get("policies", []))
                print(f"  [OK] raw_policies.json: {policies_count} records")
        except Exception as e:
            print(f"  [WARN] Error reading raw_policies.json: {e}")
        
        return True
    else:
        missing = [f for f in files if not Path(f).exists()]
        print(f"  [ERROR] Missing files: {missing}")
        return False

def verify_sdk():
    """Verify SDK can be instantiated."""
    print("Checking SDK...")
    try:
        from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
        from decimal import Decimal
        
        claims_analyst = ClaimsAnalyst(db_path="warehouse.db")
        policies_analyst = PoliciesAnalyst(db_path="warehouse.db")
        stoploss_analyst = StopLossAnalyst(db_path="warehouse.db", approval_threshold=Decimal("100000.00"))
        
        print("  [OK] All SDK classes can be instantiated")
        return True
    except Exception as e:
        print(f"  [ERROR] SDK error: {e}")
        return False

def verify_config_loader():
    """Verify config loader works."""
    print("Checking config loader...")
    try:
        from src.utils.config_loader import ConfigLoader
        from pathlib import Path
        
        loader = ConfigLoader()
        config_dir = Path(loader.config_dir)
        pipeline_files = list(config_dir.glob("*.yml"))
        pipeline_names = [f.stem for f in pipeline_files]
        
        if "claims_pipeline" in pipeline_names and "policies_pipeline" in pipeline_names:
            print(f"  [OK] Config loader works ({len(pipeline_names)} pipelines found)")
            return True
        else:
            print(f"  [WARN] Expected pipelines not found. Found: {pipeline_names}")
            return False
    except Exception as e:
        print(f"  [ERROR] Config loader error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("System Setup Verification")
    print("=" * 60)
    print()
    
    results = [
        verify_imports(),
        verify_database(),
        verify_data_files(),
        verify_sdk(),
        verify_config_loader()
    ]
    
    print()
    print("=" * 60)
    if all(results):
        print("[SUCCESS] All checks passed! System is ready.")
        sys.exit(0)
    else:
        print("[FAILURE] Some checks failed. Please review the output above.")
        sys.exit(1)

