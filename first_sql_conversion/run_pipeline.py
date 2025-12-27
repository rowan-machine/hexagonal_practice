"""
Complete Pipeline Example - Simplified Version

This demonstrates a complete pipeline from start to finish:
1. Load data from database
2. Process/aggregate using Python
3. Save results back to database
4. Verify the output

This is a simplified version that shows the core concepts without
the complexity of the full system.
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from simple_database import SimpleDatabaseManager
from simple_aggregator import SimpleClaimsAggregator


def run_pipeline():
    """Run the complete pipeline."""
    print("=" * 60)
    print("Simplified Pipeline Example")
    print("=" * 60)
    print()
    
    # Step 1: Initialize database
    print("Step 1: Initializing database...")
    db = SimpleDatabaseManager("example_warehouse.db")
    print("✓ Database initialized")
    print()
    
    # Step 2: Load data from silver layer
    print("Step 2: Loading claims from silver layer...")
    claims = db.get_claims_silver()
    print(f"✓ Loaded {len(claims)} claims")
    
    if not claims:
        print("⚠ No claims found! Run 'python sample_data.py' first.")
        return
    
    # Show sample data
    print("\nSample claims:")
    for claim in claims[:3]:
        print(f"  - {claim['claim_id']}: Policy {claim['policy_id']}, "
              f"Amount: ${claim['claim_amount']:,.2f}")
    print()
    
    # Step 3: Aggregate using Python (this is the SQL conversion!)
    print("Step 3: Aggregating claims by policy (Python conversion)...")
    aggregator = SimpleClaimsAggregator()
    aggregated = aggregator.aggregate_by_policy(claims)
    print(f"✓ Aggregated into {len(aggregated)} policy summaries")
    print()
    
    # Show aggregation results
    print("Aggregation results:")
    for agg in aggregated:
        print(f"  - Policy {agg['policy_id']}:")
        print(f"      Total Claims: ${agg['total_claims']:,.2f}")
        print(f"      Claim Count: {agg['claim_count']}")
        print(f"      Average: ${agg['avg_claim_amount']:,.2f}")
        print(f"      Max: ${agg['max_claim_amount']:,.2f}")
        print(f"      Min: ${agg['min_claim_amount']:,.2f}")
    print()
    
    # Step 4: Save to gold layer
    print("Step 4: Saving aggregated results to gold layer...")
    db.insert_claims_gold(aggregated)
    print("✓ Results saved to claims_gold table")
    print()
    
    # Step 5: Verify by reading back
    print("Step 5: Verifying results...")
    gold_data = db.get_claims_gold()
    print(f"✓ Verified: {len(gold_data)} records in gold layer")
    print()
    
    # Step 6: Compare with SQL (optional)
    print("Step 6: Comparing with original SQL query...")
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
    
    print(f"✓ SQL query returned {len(sql_result)} records")
    
    # Compare results
    if len(aggregated) == len(sql_result):
        print("✓ Record counts match!")
        
        # Compare values
        matches = 0
        for py_result, sql_result_row in zip(aggregated, sql_result):
            if (abs(py_result['total_claims'] - sql_result_row['total_claims']) < 0.01 and
                py_result['claim_count'] == sql_result_row['claim_count']):
                matches += 1
        
        if matches == len(aggregated):
            print("✓ All values match perfectly!")
        else:
            print(f"⚠ {matches}/{len(aggregated)} records match exactly")
    else:
        print(f"⚠ Record counts don't match: Python={len(aggregated)}, SQL={len(sql_result)}")
    
    print()
    print("=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the code in simple_aggregator.py to understand the conversion")
    print("2. Try modifying the aggregation logic")
    print("3. Add your own SQL queries and convert them")
    print("4. See README.md for more examples and next steps")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

