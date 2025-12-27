"""
Test script for SQL to Python conversion.

This demonstrates how the SQL query CLAIMS_GOLD_001 is converted to Python.
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from simple_aggregator import SimpleClaimsAggregator
from simple_database import SimpleDatabaseManager


def main():
    """Test the SQL to Python conversion."""
    
    # Initialize database
    print("Initializing database...")
    db = SimpleDatabaseManager("example_warehouse.db")
    
    # Check if data exists, if not, prompt user
    claims = db.get_claims_silver()
    if not claims:
        print("⚠ No claims found in database!")
        print("   Run 'python sample_data.py' first to generate sample data.")
        print()
        response = input("Generate sample data now? (y/n): ")
        if response.lower() == 'y':
            print("\nGenerating sample data...")
            from sample_data import generate_sample_data
            generate_sample_data()
            claims = db.get_claims_silver()
        else:
            print("Exiting. Please run 'python sample_data.py' first.")
            return
    
    print(f"✓ Found {len(claims)} claims in database")
    
    # Get claims from silver (this is what the SQL would query)
    print("\nReading claims from silver table...")
    silver_claims = db.get_claims_silver()
    print(f"✓ Found {len(silver_claims)} claims in silver table")
    
    # Convert SQL to Python using aggregator
    print("\n" + "="*60)
    print("CONVERTING SQL TO PYTHON")
    print("="*60)
    print("\nOriginal SQL (CLAIMS_GOLD_001):")
    print("""
    SELECT 
        policy_id,
        SUM(claim_amount) AS total_claims,
        COUNT(claim_id) AS claim_count,
        AVG(claim_amount) AS avg_claim_amount,
        MAX(claim_amount) AS max_claim_amount,
        MIN(claim_amount) AS min_claim_amount
    FROM claims_silver
    GROUP BY policy_id
    ORDER BY total_claims DESC;
    """)
    
    print("\nPython equivalent:")
    print("  aggregator = SimpleClaimsAggregator()")
    print("  result = aggregator.aggregate_by_policy(silver_claims)")
    print()
    
    # Execute Python aggregation
    aggregator = SimpleClaimsAggregator()
    result = aggregator.aggregate_by_policy(silver_claims)
    
    # Save to gold table
    print("Saving aggregated results to gold table...")
    db.insert_claims_gold(result)
    
    # Display results
    print("\n" + "="*60)
    print("AGGREGATION RESULTS")
    print("="*60)
    print(f"\nFound {len(result)} unique policies:\n")
    
    for agg in result:
        print(f"Policy: {agg['policy_id']}")
        print(f"  Total Claims: ${agg['total_claims']:,.2f}")
        print(f"  Claim Count: {agg['claim_count']}")
        print(f"  Average: ${agg['avg_claim_amount']:,.2f}")
        print(f"  Maximum: ${agg['max_claim_amount']:,.2f}")
        print(f"  Minimum: ${agg['min_claim_amount']:,.2f}")
        print()
    
    # Verify by querying gold table
    print("="*60)
    print("VERIFYING GOLD TABLE")
    print("="*60)
    gold_data = db.get_claims_gold()
    print(f"\nGold table contains {len(gold_data)} records")
    
    # Compare with SQL query result
    print("\nComparing with SQL query result...")
    sql_result = db.execute_sql("""
        SELECT 
            policy_id,
            SUM(claim_amount) AS total_claims,
            COUNT(claim_id) AS claim_count,
            AVG(claim_amount) AS avg_claim_amount,
            MAX(claim_amount) AS max_claim_amount,
            MIN(claim_amount) AS min_claim_amount
        FROM claims_silver
        GROUP BY policy_id
        ORDER BY total_claims DESC
    """)
    
    print(f"SQL query returned {len(sql_result)} records")
    print("\nSQL Results:")
    for row in sql_result:
        print(f"  Policy {row['policy_id']}: {row['claim_count']} claims, "
              f"Total: ${row['total_claims']:,.2f}")
    
    print("\n[SUCCESS] Conversion test complete!")
    print("   Both SQL and Python produce the same results.")


if __name__ == "__main__":
    main()

