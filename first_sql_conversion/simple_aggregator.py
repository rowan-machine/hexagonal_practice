"""
Simplified Claims Aggregator - Business Rules Only

This is a simplified version of the aggregator that converts SQL to Python.
No dependencies on logging, mixins, or complex infrastructure.

SQL Migration: CLAIMS_GOLD_001
"""
from typing import List, Dict, Any
from collections import defaultdict


class SimpleClaimsAggregator:
    """
    Simple business rules for claims aggregations.
    
    Converts this SQL:
        SELECT policy_id, SUM(claim_amount) AS total_claims,
               COUNT(claim_id) AS claim_count,
               AVG(claim_amount) AS avg_claim_amount,
               MAX(claim_amount) AS max_claim_amount,
               MIN(claim_amount) AS min_claim_amount
        FROM claims_silver
        GROUP BY policy_id
    """
    
    def aggregate_by_policy(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate claims by policy ID.
        
        Args:
            claims: List of claim dictionaries with:
                   - policy_id
                   - claim_amount
                   - claim_id (for counting)
        
        Returns:
            List of aggregated dictionaries with:
            - policy_id
            - total_claims (sum of claim_amount)
            - claim_count (count of claims)
            - avg_claim_amount
            - max_claim_amount
            - min_claim_amount
        """
        # Group by policy_id
        policy_stats = defaultdict(lambda: {"amounts": [], "count": 0})
        
        for claim in claims:
            policy_id = claim.get("policy_id")
            if not policy_id:
                continue
            
            # Extract claim amount (handle string, float, or Decimal)
            amount = claim.get("claim_amount", 0)
            if isinstance(amount, str):
                amount = float(amount)
            else:
                amount = float(amount) if amount else 0.0
            
            policy_stats[policy_id]["amounts"].append(amount)
            policy_stats[policy_id]["count"] += 1
        
        # Calculate aggregations
        aggregated = []
        for policy_id, stats in policy_stats.items():
            amounts = stats["amounts"]
            count = stats["count"]
            
            if not amounts:
                continue
            
            aggregated.append({
                "policy_id": policy_id,
                "total_claims": sum(amounts),
                "claim_count": count,
                "avg_claim_amount": sum(amounts) / len(amounts),
                "max_claim_amount": max(amounts),
                "min_claim_amount": min(amounts)
            })
        
        # Sort by total_claims DESC (matching SQL ORDER BY)
        aggregated.sort(key=lambda x: x["total_claims"], reverse=True)
        
        return aggregated


if __name__ == "__main__":
    # Simple test
    test_claims = [
        {"claim_id": "CLM-001", "policy_id": "POL-001", "claim_amount": 1000.0},
        {"claim_id": "CLM-002", "policy_id": "POL-001", "claim_amount": 2000.0},
        {"claim_id": "CLM-003", "policy_id": "POL-002", "claim_amount": 500.0},
    ]
    
    aggregator = SimpleClaimsAggregator()
    result = aggregator.aggregate_by_policy(test_claims)
    
    print("Aggregation Results:")
    for agg in result:
        print(f"  Policy {agg['policy_id']}: {agg['claim_count']} claims, "
              f"Total: ${agg['total_claims']:,.2f}, "
              f"Avg: ${agg['avg_claim_amount']:,.2f}")

