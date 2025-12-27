"""
Centralized aggregation business rules.

These rules are used by both pipelines and SDK to ensure consistency.
All aggregation logic is defined here, not duplicated in multiple places.

SQL Migration Reference:
- CLAIMS_GOLD_001: Claims aggregation by policy
- POLICIES_GOLD_001: Policies aggregation by employer
"""
from typing import List, Dict, Any
from collections import defaultdict
from decimal import Decimal
from src.mixins.logging import LoggingMixin


class ClaimsAggregator(LoggingMixin):
    """
    Business rules for claims aggregations.
    
    These rules are used by:
    - ClaimsGoldStep (pipeline)
    - ClaimsAnalyst (SDK)
    
    Ensures both use the same aggregation logic.
    """
    
    def __init__(self):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
    
    def aggregate_by_policy(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate claims by policy ID.
        
        Business Rule (SQL Migration: CLAIMS_GOLD_001):
        - Group by policy_id
        - Calculate: total_claims (sum), claim_count (count), 
          avg_claim_amount, max_claim_amount, min_claim_amount
        
        This matches the SQL query:
            SELECT policy_id, SUM(claim_amount) AS total_claims,
                   COUNT(claim_id) AS claim_count,
                   AVG(claim_amount) AS avg_claim_amount,
                   MAX(claim_amount) AS max_claim_amount,
                   MIN(claim_amount) AS min_claim_amount
            FROM claims_silver
            GROUP BY policy_id
        
        Args:
            claims: List of claim dictionaries with at least:
                   - policy_id
                   - claim_amount (or claim_id for counting)
        
        Returns:
            List of aggregated dictionaries with:
            - policy_id
            - total_claims (sum of claim_amount)
            - claim_count (count of claims)
            - avg_claim_amount
            - max_claim_amount
            - min_claim_amount
        """
        self.log_info("Aggregating claims by policy")
        
        # Group by policy_id
        policy_stats = defaultdict(lambda: {"amounts": [], "count": 0})
        
        for claim in claims:
            policy_id = claim.get("policy_id")
            if not policy_id:
                self.log_warning("Claim missing policy_id, skipping")
                continue
            
            # Extract claim amount (handle both Decimal and float)
            amount = claim.get("claim_amount", 0)
            if isinstance(amount, Decimal):
                amount = float(amount)
            elif isinstance(amount, str):
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
                "avg_claim_amount": sum(amounts) / len(amounts) if amounts else 0.0,
                "max_claim_amount": max(amounts) if amounts else 0.0,
                "min_claim_amount": min(amounts) if amounts else 0.0
            })
        
        self.log_info(f"Aggregated {len(aggregated)} policies from {len(claims)} claims")
        return aggregated
    
    def aggregate_by_member(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate claims by member ID.
        
        Args:
            claims: List of claim dictionaries
        
        Returns:
            List of aggregated dictionaries by member
        """
        self.log_info("Aggregating claims by member")
        
        member_stats = defaultdict(lambda: {"amounts": [], "count": 0})
        
        for claim in claims:
            member_id = claim.get("member_id")
            if not member_id:
                continue
            
            amount = claim.get("claim_amount", 0)
            if isinstance(amount, Decimal):
                amount = float(amount)
            else:
                amount = float(amount) if amount else 0.0
            
            member_stats[member_id]["amounts"].append(amount)
            member_stats[member_id]["count"] += 1
        
        aggregated = []
        for member_id, stats in member_stats.items():
            amounts = stats["amounts"]
            if not amounts:
                continue
            
            aggregated.append({
                "member_id": member_id,
                "total_claims": sum(amounts),
                "claim_count": stats["count"],
                "avg_claim_amount": sum(amounts) / len(amounts),
                "max_claim_amount": max(amounts),
                "min_claim_amount": min(amounts)
            })
        
        return aggregated


class PoliciesAggregator(LoggingMixin):
    """
    Business rules for policies aggregations.
    
    These rules are used by:
    - PoliciesGoldStep (pipeline)
    - PoliciesAnalyst (SDK)
    
    Ensures both use the same aggregation logic.
    """
    
    def __init__(self):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
    
    def aggregate_by_employer(self, policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate policies by employer ID.
        
        Business Rule (SQL Migration: POLICIES_GOLD_001):
        - Group by employer_id
        - Calculate: total_coverage (sum), policy_count (count),
          avg_stop_loss_limit
        
        This matches the SQL query:
            SELECT employer_id, SUM(stop_loss_limit) AS total_coverage,
                   COUNT(policy_id) AS policy_count,
                   AVG(stop_loss_limit) AS avg_stop_loss_limit
            FROM policies_silver
            GROUP BY employer_id
        
        Args:
            policies: List of policy dictionaries with at least:
                     - employer_id
                     - stop_loss_limit
                     - policy_id (for counting)
        
        Returns:
            List of aggregated dictionaries with:
            - employer_id
            - total_coverage (sum of stop_loss_limit)
            - policy_count (count of policies)
            - avg_stop_loss_limit
        """
        self.log_info("Aggregating policies by employer")
        
        # Group by employer_id
        employer_stats = defaultdict(lambda: {"limits": [], "count": 0})
        
        for policy in policies:
            employer_id = policy.get("employer_id")
            if not employer_id:
                self.log_warning("Policy missing employer_id, skipping")
                continue
            
            # Extract stop loss limit
            limit = policy.get("stop_loss_limit", 0)
            if isinstance(limit, Decimal):
                limit = float(limit)
            elif isinstance(limit, str):
                limit = float(limit)
            else:
                limit = float(limit) if limit else 0.0
            
            employer_stats[employer_id]["limits"].append(limit)
            employer_stats[employer_id]["count"] += 1
        
        # Calculate aggregations
        aggregated = []
        for employer_id, stats in employer_stats.items():
            limits = stats["limits"]
            count = stats["count"]
            
            if not limits:
                continue
            
            aggregated.append({
                "employer_id": employer_id,
                "total_coverage": sum(limits),
                "policy_count": count,
                "avg_stop_loss_limit": sum(limits) / len(limits) if limits else 0.0
            })
        
        self.log_info(f"Aggregated {len(aggregated)} employers from {len(policies)} policies")
        return aggregated

