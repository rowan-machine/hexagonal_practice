"""
Generate Sample Data for Testing

This script creates sample claims data in the database so you can
test the SQL to Python conversion.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from simple_database import SimpleDatabaseManager


def generate_sample_data(num_claims: int = 20):
    """Generate sample claims data."""
    print("=" * 60)
    print("Generating Sample Data")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database...")
    db = SimpleDatabaseManager("example_warehouse.db")
    print("✓ Database initialized")
    print()
    
    # Sample data
    policies = ["POL-001", "POL-002", "POL-003"]
    members = [f"MEM-{i:03d}" for i in range(1, 11)]
    statuses = ["approved", "pending", "paid"]
    claim_types = ["medical", "dental", "vision"]
    
    # Generate claims
    print(f"Generating {num_claims} sample claims...")
    claims = []
    
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(1, num_claims + 1):
        claim_id = f"CLM-{i:03d}"
        policy_id = random.choice(policies)
        member_id = random.choice(members)
        claim_amount = round(random.uniform(100, 10000), 2)
        incurred_date = (base_date + timedelta(days=random.randint(0, 90))).isoformat()
        
        # Some claims are paid
        if random.random() > 0.5:
            paid_date = (datetime.fromisoformat(incurred_date) + 
                        timedelta(days=random.randint(1, 30))).isoformat()
            status = "paid"
        else:
            paid_date = None
            status = random.choice(["approved", "pending"])
        
        claim_type = random.choice(claim_types)
        
        claims.append({
            "claim_id": claim_id,
            "policy_id": policy_id,
            "member_id": member_id,
            "claim_amount": claim_amount,
            "incurred_date": incurred_date,
            "paid_date": paid_date,
            "status": status,
            "claim_type": claim_type
        })
    
    # Insert into database
    print("Inserting claims into database...")
    db.insert_claims_silver(claims)
    print(f"✓ Inserted {len(claims)} claims")
    print()
    
    # Show summary
    print("Data Summary:")
    print(f"  Total Claims: {len(claims)}")
    print(f"  Policies: {len(set(c['policy_id'] for c in claims))}")
    print(f"  Members: {len(set(c['member_id'] for c in claims))}")
    print(f"  Total Amount: ${sum(c['claim_amount'] for c in claims):,.2f}")
    print()
    
    # Show by policy
    print("Claims by Policy:")
    for policy in policies:
        policy_claims = [c for c in claims if c['policy_id'] == policy]
        total = sum(c['claim_amount'] for c in policy_claims)
        print(f"  {policy}: {len(policy_claims)} claims, ${total:,.2f}")
    print()
    
    print("=" * 60)
    print("Sample Data Generated Successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run 'python test_conversion.py' to test the conversion")
    print("2. Run 'python run_pipeline.py' to see the complete pipeline")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample claims data")
    parser.add_argument(
        "--num-claims",
        type=int,
        default=20,
        help="Number of claims to generate (default: 20)"
    )
    
    args = parser.parse_args()
    
    try:
        generate_sample_data(args.num_claims)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

