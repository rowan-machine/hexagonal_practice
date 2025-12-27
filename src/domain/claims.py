"""
Domain logic for stop loss insurance claims.

Pure business logic with no I/O dependencies.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from src.mixins.validation import ValidationMixin


@dataclass
class Claim:
    """
    Represents a stop loss insurance claim.
    
    This is a domain model representing a single insurance claim.
    It contains business logic methods but no I/O operations.
    
    Attributes:
        claim_id: Unique identifier for the claim
        policy_id: Identifier of the policy this claim belongs to
        member_id: Identifier of the member making the claim
        claim_amount: Amount of the claim in dollars (Decimal for precision)
        incurred_date: Date when the claim was incurred
        paid_date: Date when the claim was paid (None if not yet paid)
        status: Current status of the claim (pending, approved, denied, paid)
        claim_type: Type of claim (medical, pharmacy, dental, vision)
    
    Example:
        ```python
        claim = Claim(
            claim_id="CLM-001",
            policy_id="POL-001",
            member_id="MEM-001",
            claim_amount=Decimal("50000.00"),
            incurred_date=datetime.now()
        )
        
        if claim.is_approved():
            print("Claim is approved")
        ```
    """
    claim_id: str
    policy_id: str
    member_id: str
    claim_amount: Decimal
    incurred_date: datetime
    paid_date: Optional[datetime] = None
    status: str = "pending"
    claim_type: str = "medical"
    
    def is_approved(self) -> bool:
        """
        Check if claim is approved.
        
        Returns:
            True if status is "approved", False otherwise
        """
        return self.status == "approved"
    
    def is_paid(self) -> bool:
        """
        Check if claim has been paid.
        
        Returns:
            True if paid_date is not None, False otherwise
        """
        return self.paid_date is not None
    
    def exceeds_threshold(self, threshold: Decimal) -> bool:
        """
        Check if claim amount exceeds a threshold.
        
        Args:
            threshold: The threshold amount to compare against
        
        Returns:
            True if claim_amount > threshold, False otherwise
        
        Example:
            ```python
            if claim.exceeds_threshold(Decimal("100000.00")):
                print("High-value claim")
            ```
        """
        return self.claim_amount > threshold


class ClaimsProcessor(ValidationMixin):
    """
    Processes stop loss insurance claims.
    
    Encapsulates business logic for claim validation, approval, and aggregation.
    """
    
    def __init__(self, approval_threshold: Decimal = Decimal("100000.00")):
        ValidationMixin.__init__(self)
        self.approval_threshold = approval_threshold
        self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> None:
        """Setup validation rules for claims."""
        self.add_rule(
            name="claim_amount_positive",
            check=lambda c: c.claim_amount > 0,
            error_message="Claim amount must be positive",
            severity="error"
        )
        self.add_rule(
            name="claim_has_policy",
            check=lambda c: bool(c.policy_id),
            error_message="Claim must have a policy ID",
            severity="error"
        )
        self.add_rule(
            name="claim_has_member",
            check=lambda c: bool(c.member_id),
            error_message="Claim must have a member ID",
            severity="error"
        )
        self.add_rule(
            name="incurred_date_valid",
            check=lambda c: c.incurred_date <= datetime.now(),
            error_message="Incurred date cannot be in the future",
            severity="error"
        )
    
    def process(self, raw_claims: List[Dict[str, Any]]) -> List[Claim]:
        """
        Process raw claim data into Claim objects.
        
        Args:
            raw_claims: List of raw claim dictionaries
            
        Returns:
            List of Claim objects
        """
        processed = []
        
        for raw_claim in raw_claims:
            try:
                claim = self._create_claim_from_dict(raw_claim)
                
                # Validate claim
                if self.validate(claim):
                    processed.append(claim)
                else:
                    # Log validation failures but continue processing
                    validation_results = self.get_validation_results()
                    # In production, would log these properly
                    pass
                    
            except Exception as e:
                # Log error and continue processing other claims
                # In production, would use proper logging
                continue
        
        return processed
    
    def _create_claim_from_dict(self, data: Dict[str, Any]) -> Claim:
        """Create a Claim object from a dictionary."""
        return Claim(
            claim_id=str(data.get("claim_id", "")),
            policy_id=str(data.get("policy_id", "")),
            member_id=str(data.get("member_id", "")),
            claim_amount=Decimal(str(data.get("claim_amount", 0))),
            incurred_date=self._parse_date(data.get("incurred_date")),
            paid_date=self._parse_date(data.get("paid_date")) if data.get("paid_date") else None,
            status=str(data.get("status", "pending")),
            claim_type=str(data.get("claim_type", "medical"))
        )
    
    def _parse_date(self, date_value: Any) -> datetime:
        """Parse date from various formats."""
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            # Simple parsing - in production would handle multiple formats
            return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        raise ValueError(f"Cannot parse date from: {date_value}")
    
    def calculate_total_claims(self, claims: List[Claim]) -> Decimal:
        """Calculate total claim amount."""
        return sum(claim.claim_amount for claim in claims)
    
    def filter_by_status(self, claims: List[Claim], status: str) -> List[Claim]:
        """Filter claims by status."""
        return [c for c in claims if c.status == status]
    
    def filter_exceeding_threshold(self, claims: List[Claim], threshold: Optional[Decimal] = None) -> List[Claim]:
        """Filter claims exceeding a threshold."""
        threshold = threshold or self.approval_threshold
        return [c for c in claims if c.exceeds_threshold(threshold)]
    
    def aggregate_by_policy(self, claims: List[Claim]) -> Dict[str, List[Claim]]:
        """Aggregate claims by policy ID."""
        aggregated = {}
        for claim in claims:
            if claim.policy_id not in aggregated:
                aggregated[claim.policy_id] = []
            aggregated[claim.policy_id].append(claim)
        return aggregated
    
    def aggregate_by_member(self, claims: List[Claim]) -> Dict[str, List[Claim]]:
        """Aggregate claims by member ID."""
        aggregated = {}
        for claim in claims:
            if claim.member_id not in aggregated:
                aggregated[claim.member_id] = []
            aggregated[claim.member_id].append(claim)
        return aggregated

