"""
Analyst-facing SDK for stop loss insurance data pipelines.

This is the PUBLIC API layer. Analysts should only interact with these classes.
All data access, business logic, and complexity is encapsulated here.

Architecture Layers:
1. Data Persistence: Database, file I/O (hidden from analysts)
2. Domain: Business logic (hidden from analysts)
3. Pipeline: Orchestration (hidden from analysts)
4. SDK/Interface: This module (analyst-facing)

Analysts should:
- Load data from database (via SDK methods)
- Use simple analysis methods
- Convert to DataFrames for visualization
- NOT access database directly
- NOT load from files directly
- NOT implement business logic
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from src.domain.claims import ClaimsProcessor, Claim
from src.domain.policies import PolicyProcessor, Policy
from src.utils.database import DatabaseManager
from src.utils.dataframe_ops import DataFrameOps
from src.mixins.logging import LoggingMixin


class ClaimsAnalyst(LoggingMixin):
    """
    Public API for claims analysis.
    
    Analysts use this class to analyze claims data. All complexity is hidden:
    - Database access is abstracted
    - Business logic is encapsulated
    - Data transformation is handled internally
    
    Usage:
        ```python
        from ringmaster.sdk import ClaimsAnalyst
        
        analyst = ClaimsAnalyst(db_path="warehouse.db")
        claims = analyst.load_from_database()  # Load from database
        total = analyst.get_total_claims(claims)
        df = analyst.to_dataframe(claims)
        ```
    
    Attributes:
        processor: ClaimsProcessor for business logic (internal)
        df_ops: DataFrameOps for pandas operations (internal)
        db_manager: DatabaseManager for data access (internal)
    """
    
    def __init__(self, db_path: str = "warehouse.db", approval_threshold: Optional[Decimal] = None):
        """
        Initialize ClaimsAnalyst.
        
        Args:
            db_path: Path to SQLite database (default: "warehouse.db")
            approval_threshold: Threshold for claim approval (default: $100,000.00)
        """
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        threshold = approval_threshold or Decimal("100000.00")
        self.processor = ClaimsProcessor(approval_threshold=threshold)
        self.df_ops = DataFrameOps()
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def load_from_database(self, layer: str = "silver", limit: Optional[int] = None) -> List[Claim]:
        """
        Load claims from database.
        
        This is the PRIMARY method analysts should use to load data.
        Data comes from the warehouse database, not files.
        
        Args:
            layer: Data layer to load from ("bronze", "silver", or "gold"). Default: "silver"
            limit: Maximum number of records to load (None for all)
            
        Returns:
            List of Claim domain objects
            
        Example:
            ```python
            # Load all silver claims
            claims = analyst.load_from_database()
            
            # Load first 100 bronze claims
            claims = analyst.load_from_database(layer="bronze", limit=100)
            ```
        """
        self.log_info(f"Loading claims from database", layer=layer, limit=limit)
        
        # Build query based on layer
        if layer == "bronze":
            table = "claims_bronze"
        elif layer == "silver":
            table = "claims_silver"
        elif layer == "gold":
            # Gold is aggregated, return empty for now (analysts use silver)
            self.log_warning("Gold layer is aggregated. Use silver layer for individual claims.")
            return []
        else:
            raise ValueError(f"Invalid layer: {layer}. Must be 'bronze', 'silver', or 'gold'")
        
        # Query database
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"SELECT * FROM {table} ORDER BY created_at DESC {limit_clause}"
        rows = self.db_manager.query(query)
        
        # Convert to Claim objects
        claims = []
        for row in rows:
            try:
                claim_dict = row  # query() already returns dictionaries
                # Convert to format expected by processor
                claim_data = {
                    "claim_id": claim_dict["claim_id"],
                    "policy_id": claim_dict["policy_id"],
                    "member_id": claim_dict["member_id"],
                    "claim_amount": str(claim_dict["claim_amount"]),
                    "incurred_date": claim_dict["incurred_date"],
                    "paid_date": claim_dict.get("paid_date"),
                    "status": claim_dict["status"],
                    "claim_type": claim_dict.get("claim_type", "medical")
                }
                # Process through domain layer for validation
                processed = self.processor.process([claim_data])
                if processed:
                    claims.append(processed[0])
            except Exception as e:
                self.log_warning(f"Failed to process claim {row.get('claim_id', 'unknown')}", error=e)
                continue
        
        self.log_info(f"Loaded {len(claims)} claims from {layer} layer")
        return claims
    
    def get_total_claims(self, claims: List[Claim]) -> Decimal:
        """
        Calculate total claim amount.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            Total amount as Decimal
        """
        return self.processor.calculate_total_claims(claims)
    
    def get_approved_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Filter approved claims.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            List of approved claims
        """
        return self.processor.filter_by_status(claims, "approved")
    
    def get_paid_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Filter paid claims.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            List of paid claims
        """
        return [c for c in claims if c.is_paid()]
    
    def get_pending_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Filter pending claims.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            List of pending claims
        """
        return self.processor.filter_by_status(claims, "pending")
    
    def get_high_value_claims(self, claims: List[Claim], 
                              threshold: Optional[Decimal] = None) -> List[Claim]:
        """
        Filter claims exceeding a threshold.
        
        Args:
            claims: List of Claim objects
            threshold: Amount threshold (uses default if None)
            
        Returns:
            List of high-value claims
        """
        return self.processor.filter_exceeding_threshold(claims, threshold)
    
    def aggregate_by_policy(self, claims: List[Claim]) -> Dict[str, List[Claim]]:
        """
        Group claims by policy ID.
        
        Uses domain processor for grouping (returns Claim objects).
        For aggregation statistics, use get_summary_statistics().
        
        Args:
            claims: List of Claim objects
            
        Returns:
            Dictionary mapping policy_id to list of claims
        """
        return self.processor.aggregate_by_policy(claims)
    
    def get_policy_aggregations(self, claims: List[Claim]) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics by policy (same logic as gold layer).
        
        Uses centralized business rules to ensure consistency with pipeline.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            List of aggregated dictionaries with policy statistics
        """
        from src.business_rules.aggregations import ClaimsAggregator
        
        # Convert Claims to dictionaries
        claim_dicts = [self._claim_to_dict(claim) for claim in claims]
        
        # Use centralized aggregator
        aggregator = ClaimsAggregator()
        return aggregator.aggregate_by_policy(claim_dicts)
    
    def aggregate_by_member(self, claims: List[Claim]) -> Dict[str, List[Claim]]:
        """
        Group claims by member ID.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            Dictionary mapping member_id to list of claims
        """
        return self.processor.aggregate_by_member(claims)
    
    def get_summary_statistics(self, claims: List[Claim]) -> Dict[str, Any]:
        """
        Calculate summary statistics for claims.
        
        Business logic is encapsulated here - analysts just call this method.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not claims:
            return {
                "total_claims": 0,
                "total_amount": 0.0,
                "average_amount": 0.0,
                "by_status": {},
                "by_type": {}
            }
        
        total = self.get_total_claims(claims)
        
        # Status distribution
        by_status = {}
        for claim in claims:
            by_status[claim.status] = by_status.get(claim.status, 0) + 1
        
        # Type distribution
        by_type = {}
        for claim in claims:
            by_type[claim.claim_type] = by_type.get(claim.claim_type, 0) + 1
        
        return {
            "total_claims": len(claims),
            "total_amount": float(total),
            "average_amount": float(total / len(claims)),
            "by_status": by_status,
            "by_type": by_type
        }
    
    def to_dataframe(self, claims: List[Claim]) -> Any:
        """
        Convert claims to pandas DataFrame.
        
        Args:
            claims: List of Claim objects
            
        Returns:
            pandas DataFrame
        """
        data = [self._claim_to_dict(claim) for claim in claims]
        return self.df_ops.to_dataframe(data)
    
    def _claim_to_dict(self, claim: Claim) -> Dict[str, Any]:
        """Internal: Convert Claim to dictionary."""
        return {
            "claim_id": claim.claim_id,
            "policy_id": claim.policy_id,
            "member_id": claim.member_id,
            "claim_amount": float(claim.claim_amount),
            "incurred_date": claim.incurred_date.isoformat(),
            "paid_date": claim.paid_date.isoformat() if claim.paid_date else None,
            "status": claim.status,
            "claim_type": claim.claim_type
        }


class PoliciesAnalyst(LoggingMixin):
    """
    Public API for policies analysis.
    
    Analysts use this class to analyze policies data. All complexity is hidden.
    
    Usage:
        ```python
        from ringmaster.sdk import PoliciesAnalyst
        
        analyst = PoliciesAnalyst(db_path="warehouse.db")
        policies = analyst.load_from_database()
        active = analyst.get_active_policies(policies)
        ```
    """
    
    def __init__(self, db_path: str = "warehouse.db"):
        """
        Initialize PoliciesAnalyst.
        
        Args:
            db_path: Path to SQLite database (default: "warehouse.db")
        """
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.processor = PolicyProcessor()
        self.df_ops = DataFrameOps()
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def load_from_database(self, layer: str = "silver", limit: Optional[int] = None) -> List[Policy]:
        """
        Load policies from database.
        
        This is the PRIMARY method analysts should use to load data.
        
        Args:
            layer: Data layer to load from ("bronze", "silver", or "gold"). Default: "silver"
            limit: Maximum number of records to load (None for all)
            
        Returns:
            List of Policy domain objects
        """
        self.log_info(f"Loading policies from database", layer=layer, limit=limit)
        
        # Build query based on layer
        if layer == "bronze":
            table = "policies_bronze"
        elif layer == "silver":
            table = "policies_silver"
        elif layer == "gold":
            self.log_warning("Gold layer is aggregated. Use silver layer for individual policies.")
            return []
        else:
            raise ValueError(f"Invalid layer: {layer}. Must be 'bronze', 'silver', or 'gold'")
        
        # Query database
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"SELECT * FROM {table} ORDER BY created_at DESC {limit_clause}"
        rows = self.db_manager.query(query)
        
        # Convert to Policy objects
        policies = []
        for row in rows:
            try:
                policy_dict = dict(row)
                policy_data = {
                    "policy_id": policy_dict["policy_id"],
                    "employer_id": policy_dict["employer_id"],
                    "effective_date": policy_dict["effective_date"],
                    "expiration_date": policy_dict["expiration_date"],
                    "stop_loss_limit": str(policy_dict["stop_loss_limit"]),
                    "aggregate_deductible": str(policy_dict["aggregate_deductible"]),
                    "specific_deductible": str(policy_dict["specific_deductible"]),
                    "status": policy_dict["status"]
                }
                processed = self.processor.process([policy_data])
                if processed:
                    policies.append(processed[0])
            except Exception as e:
                self.log_warning(f"Failed to process policy {row.get('policy_id', 'unknown')}", error=e)
                continue
        
        self.log_info(f"Loaded {len(policies)} policies from {layer} layer")
        return policies
    
    def get_active_policies(self, policies: List[Policy]) -> List[Policy]:
        """
        Filter active policies.
        
        Args:
            policies: List of Policy objects
            
        Returns:
            List of active policies
        """
        return self.processor.filter_active(policies)
    
    def get_employer_policies(self, policies: List[Policy], employer_id: str) -> List[Policy]:
        """
        Filter policies by employer.
        
        Args:
            policies: List of Policy objects
            employer_id: Employer identifier
            
        Returns:
            List of policies for the employer
        """
        return self.processor.filter_by_employer(policies, employer_id)
    
    def find_policy(self, policies: List[Policy], policy_id: str) -> Optional[Policy]:
        """
        Find a policy by ID.
        
        Args:
            policies: List of Policy objects
            policy_id: Policy identifier
            
        Returns:
            Policy object or None if not found
        """
        return self.processor.find_policy(policies, policy_id)
    
    def get_total_coverage(self, policies: List[Policy]) -> Decimal:
        """
        Calculate total stop loss coverage.
        
        Args:
            policies: List of Policy objects
            
        Returns:
            Total coverage as Decimal
        """
        return self.processor.calculate_total_coverage(policies)
    
    def get_employer_aggregations(self, policies: List[Policy]) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics by employer (same logic as gold layer).
        
        Uses centralized business rules to ensure consistency with pipeline.
        
        Args:
            policies: List of Policy objects
            
        Returns:
            List of aggregated dictionaries with employer statistics
        """
        from src.business_rules.aggregations import PoliciesAggregator
        
        # Convert Policies to dictionaries
        policy_dicts = [self._policy_to_dict(policy) for policy in policies]
        
        # Use centralized aggregator
        aggregator = PoliciesAggregator()
        return aggregator.aggregate_by_employer(policy_dicts)
    
    def get_summary_statistics(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Calculate summary statistics for policies.
        
        Args:
            policies: List of Policy objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not policies:
            return {
                "total_policies": 0,
                "total_coverage": 0.0,
                "average_coverage": 0.0,
                "by_status": {},
                "by_employer": {}
            }
        
        total_coverage = self.get_total_coverage(policies)
        
        # Status distribution
        by_status = {}
        for policy in policies:
            by_status[policy.status] = by_status.get(policy.status, 0) + 1
        
        # Employer distribution
        by_employer = {}
        for policy in policies:
            by_employer[policy.employer_id] = by_employer.get(policy.employer_id, 0) + 1
        
        return {
            "total_policies": len(policies),
            "total_coverage": float(total_coverage),
            "average_coverage": float(total_coverage / len(policies)),
            "by_status": by_status,
            "by_employer": by_employer
        }
    
    def to_dataframe(self, policies: List[Policy]) -> Any:
        """
        Convert policies to pandas DataFrame.
        
        Args:
            policies: List of Policy objects
            
        Returns:
            pandas DataFrame
        """
        data = [self._policy_to_dict(policy) for policy in policies]
        return self.df_ops.to_dataframe(data)
    
    def _policy_to_dict(self, policy: Policy) -> Dict[str, Any]:
        """Internal: Convert Policy to dictionary."""
        return {
            "policy_id": policy.policy_id,
            "employer_id": policy.employer_id,
            "effective_date": policy.effective_date.isoformat(),
            "expiration_date": policy.expiration_date.isoformat(),
            "stop_loss_limit": float(policy.stop_loss_limit),
            "aggregate_deductible": float(policy.aggregate_deductible),
            "specific_deductible": float(policy.specific_deductible),
            "status": policy.status
        }


class StopLossAnalyst(LoggingMixin):
    """
    Public API for combined claims and policies analysis.
    
    Provides high-level methods that combine claims and policies data.
    All business logic is encapsulated here.
    
    Usage:
        ```python
        from ringmaster.sdk import StopLossAnalyst
        
        analyst = StopLossAnalyst(db_path="warehouse.db")
        utilization = analyst.get_coverage_utilization()
        ```
    """
    
    def __init__(self, db_path: str = "warehouse.db", approval_threshold: Optional[Decimal] = None):
        """
        Initialize StopLossAnalyst.
        
        Args:
            db_path: Path to SQLite database
            approval_threshold: Threshold for claim approval
        """
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.claims_analyst = ClaimsAnalyst(db_path=db_path, approval_threshold=approval_threshold)
        self.policies_analyst = PoliciesAnalyst(db_path=db_path)
        self.db_path = db_path
    
    def get_coverage_utilization(self) -> List[Dict[str, Any]]:
        """
        Calculate coverage utilization for all policies.
        
        This method encapsulates all business logic. Analysts just call it.
        
        Returns:
            List of utilization records with policy details and utilization percentages
        """
        self.log_info("Calculating coverage utilization")
        
        # Load data from database
        claims = self.claims_analyst.load_from_database(layer="silver")
        policies = self.policies_analyst.load_from_database(layer="silver")
        
        # Aggregate claims by policy
        claims_by_policy = self.claims_analyst.aggregate_by_policy(claims)
        
        # Calculate utilization
        utilization = []
        for policy in policies:
            policy_claims = claims_by_policy.get(policy.policy_id, [])
            total_claims = self.claims_analyst.get_total_claims(policy_claims)
            
            utilization_pct = (total_claims / policy.stop_loss_limit * 100) if policy.stop_loss_limit > 0 else 0
            
            utilization.append({
                "policy_id": policy.policy_id,
                "employer_id": policy.employer_id,
                "stop_loss_limit": float(policy.stop_loss_limit),
                "total_claims": float(total_claims),
                "utilization_percent": float(utilization_pct),
                "remaining_coverage": float(policy.stop_loss_limit - total_claims)
            })
        
        return utilization
    
    def get_claims_by_policy_summary(self) -> Dict[str, Any]:
        """
        Get summary of claims grouped by policy.
        
        Returns:
            Dictionary with policy summaries
        """
        self.log_info("Generating claims by policy summary")
        
        # Load data
        claims = self.claims_analyst.load_from_database(layer="silver")
        policies = self.policies_analyst.load_from_database(layer="silver")
        
        # Aggregate
        claims_by_policy = self.claims_analyst.aggregate_by_policy(claims)
        
        # Build summary
        summary = {}
        for policy_id, policy_claims in claims_by_policy.items():
            policy = self.policies_analyst.find_policy(policies, policy_id)
            
            total_claims = self.claims_analyst.get_total_claims(policy_claims)
            
            summary[policy_id] = {
                "policy": self.policies_analyst._policy_to_dict(policy) if policy else None,
                "claim_count": len(policy_claims),
                "total_claim_amount": float(total_claims),
            }
        
        return summary
    
    def get_high_utilization_policies(self, threshold_percent: float = 50.0) -> List[Dict[str, Any]]:
        """
        Get policies with utilization above threshold.
        
        Args:
            threshold_percent: Utilization threshold percentage
            
        Returns:
            List of high utilization policies
        """
        utilization = self.get_coverage_utilization()
        return [u for u in utilization if u["utilization_percent"] > threshold_percent]

