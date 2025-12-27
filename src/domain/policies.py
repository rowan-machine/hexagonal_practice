"""
Domain logic for stop loss insurance policies.

Pure business logic with no I/O dependencies.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from src.mixins.validation import ValidationMixin


@dataclass
class Policy:
    """Represents a stop loss insurance policy."""
    policy_id: str
    employer_id: str
    effective_date: datetime
    expiration_date: datetime
    stop_loss_limit: Decimal
    aggregate_deductible: Decimal
    specific_deductible: Decimal
    status: str = "active"
    
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        now = datetime.now()
        return (self.status == "active" and 
                self.effective_date <= now <= self.expiration_date)
    
    def is_expired(self) -> bool:
        """Check if policy has expired."""
        return datetime.now() > self.expiration_date
    
    def calculate_coverage(self, claim_amount: Decimal) -> Decimal:
        """
        Calculate coverage amount for a claim.
        
        Args:
            claim_amount: Amount of the claim
            
        Returns:
            Amount covered by the policy
        """
        # Specific deductible applies first
        if claim_amount <= self.specific_deductible:
            return Decimal("0.00")
        
        # Coverage after specific deductible
        covered = claim_amount - self.specific_deductible
        
        # Cannot exceed stop loss limit
        return min(covered, self.stop_loss_limit)


class PolicyProcessor(ValidationMixin):
    """
    Processes stop loss insurance policies.
    
    Encapsulates business logic for policy validation and management.
    """
    
    def __init__(self):
        ValidationMixin.__init__(self)
        self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> None:
        """Setup validation rules for policies."""
        self.add_rule(
            name="stop_loss_limit_positive",
            check=lambda p: p.stop_loss_limit > 0,
            error_message="Stop loss limit must be positive",
            severity="error"
        )
        self.add_rule(
            name="deductibles_positive",
            check=lambda p: p.aggregate_deductible >= 0 and p.specific_deductible >= 0,
            error_message="Deductibles must be non-negative",
            severity="error"
        )
        self.add_rule(
            name="expiration_after_effective",
            check=lambda p: p.expiration_date > p.effective_date,
            error_message="Expiration date must be after effective date",
            severity="error"
        )
        self.add_rule(
            name="effective_date_valid",
            check=lambda p: p.effective_date <= datetime.now(),
            error_message="Effective date cannot be in the future",
            severity="warning"
        )
    
    def process(self, raw_policies: List[Dict[str, Any]]) -> List[Policy]:
        """
        Process raw policy data into Policy objects.
        
        Args:
            raw_policies: List of raw policy dictionaries
            
        Returns:
            List of Policy objects
        """
        processed = []
        
        for raw_policy in raw_policies:
            try:
                policy = self._create_policy_from_dict(raw_policy)
                
                # Validate policy
                if self.validate(policy):
                    processed.append(policy)
                else:
                    # Log validation failures but continue processing
                    validation_results = self.get_validation_results()
                    # In production, would log these properly
                    pass
                    
            except Exception as e:
                # Log error and continue processing other policies
                # In production, would use proper logging
                continue
        
        return processed
    
    def _create_policy_from_dict(self, data: Dict[str, Any]) -> Policy:
        """Create a Policy object from a dictionary."""
        return Policy(
            policy_id=str(data.get("policy_id", "")),
            employer_id=str(data.get("employer_id", "")),
            effective_date=self._parse_date(data.get("effective_date")),
            expiration_date=self._parse_date(data.get("expiration_date")),
            stop_loss_limit=Decimal(str(data.get("stop_loss_limit", 0))),
            aggregate_deductible=Decimal(str(data.get("aggregate_deductible", 0))),
            specific_deductible=Decimal(str(data.get("specific_deductible", 0))),
            status=str(data.get("status", "active"))
        )
    
    def _parse_date(self, date_value: Any) -> datetime:
        """Parse date from various formats."""
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            # Simple parsing - in production would handle multiple formats
            return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        raise ValueError(f"Cannot parse date from: {date_value}")
    
    def filter_active(self, policies: List[Policy]) -> List[Policy]:
        """Filter active policies."""
        return [p for p in policies if p.is_active()]
    
    def filter_by_employer(self, policies: List[Policy], employer_id: str) -> List[Policy]:
        """Filter policies by employer ID."""
        return [p for p in policies if p.employer_id == employer_id]
    
    def find_policy(self, policies: List[Policy], policy_id: str) -> Optional[Policy]:
        """Find a policy by ID."""
        for policy in policies:
            if policy.policy_id == policy_id:
                return policy
        return None
    
    def calculate_total_coverage(self, policies: List[Policy]) -> Decimal:
        """Calculate total stop loss coverage across all policies."""
        return sum(p.stop_loss_limit for p in policies)

