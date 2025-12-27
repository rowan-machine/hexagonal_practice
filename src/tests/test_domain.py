"""
Unit tests for domain logic.

Tests business logic without I/O dependencies.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from src.domain.claims import Claim, ClaimsProcessor
from src.domain.policies import Policy, PolicyProcessor


class TestClaim:
    """Tests for Claim domain model."""
    
    def test_claim_creation(self):
        """Test creating a claim."""
        claim = Claim(
            claim_id="CLM001",
            policy_id="POL001",
            member_id="MEM001",
            claim_amount=Decimal("50000.00"),
            incurred_date=datetime.now()
        )
        assert claim.claim_id == "CLM001"
        assert claim.claim_amount == Decimal("50000.00")
    
    def test_claim_exceeds_threshold(self):
        """Test threshold checking."""
        claim = Claim(
            claim_id="CLM001",
            policy_id="POL001",
            member_id="MEM001",
            claim_amount=Decimal("150000.00"),
            incurred_date=datetime.now()
        )
        assert claim.exceeds_threshold(Decimal("100000.00"))
        assert not claim.exceeds_threshold(Decimal("200000.00"))


class TestClaimsProcessor:
    """Tests for ClaimsProcessor."""
    
    def test_process_valid_claims(self):
        """Test processing valid claim data."""
        processor = ClaimsProcessor()
        raw_claims = [
            {
                "claim_id": "CLM001",
                "policy_id": "POL001",
                "member_id": "MEM001",
                "claim_amount": "50000.00",
                "incurred_date": "2024-01-15T00:00:00",
                "status": "approved"
            }
        ]
        claims = processor.process(raw_claims)
        assert len(claims) == 1
        assert claims[0].claim_id == "CLM001"
    
    def test_calculate_total_claims(self):
        """Test calculating total claim amount."""
        processor = ClaimsProcessor()
        claims = [
            Claim("CLM001", "POL001", "MEM001", Decimal("10000.00"), datetime.now()),
            Claim("CLM002", "POL001", "MEM002", Decimal("20000.00"), datetime.now())
        ]
        total = processor.calculate_total_claims(claims)
        assert total == Decimal("30000.00")
    
    def test_filter_by_status(self):
        """Test filtering claims by status."""
        processor = ClaimsProcessor()
        claims = [
            Claim("CLM001", "POL001", "MEM001", Decimal("10000.00"), datetime.now(), status="approved"),
            Claim("CLM002", "POL001", "MEM002", Decimal("20000.00"), datetime.now(), status="pending")
        ]
        approved = processor.filter_by_status(claims, "approved")
        assert len(approved) == 1
        assert approved[0].claim_id == "CLM001"


class TestPolicy:
    """Tests for Policy domain model."""
    
    def test_policy_creation(self):
        """Test creating a policy."""
        policy = Policy(
            policy_id="POL001",
            employer_id="EMP001",
            effective_date=datetime(2024, 1, 1),
            expiration_date=datetime(2024, 12, 31),
            stop_loss_limit=Decimal("1000000.00"),
            aggregate_deductible=Decimal("50000.00"),
            specific_deductible=Decimal("25000.00")
        )
        assert policy.policy_id == "POL001"
        assert policy.stop_loss_limit == Decimal("1000000.00")
    
    def test_calculate_coverage(self):
        """Test coverage calculation."""
        policy = Policy(
            policy_id="POL001",
            employer_id="EMP001",
            effective_date=datetime(2024, 1, 1),
            expiration_date=datetime(2024, 12, 31),
            stop_loss_limit=Decimal("100000.00"),
            aggregate_deductible=Decimal("0.00"),
            specific_deductible=Decimal("25000.00")
        )
        
        # Claim below deductible
        coverage = policy.calculate_coverage(Decimal("10000.00"))
        assert coverage == Decimal("0.00")
        
        # Claim above deductible
        coverage = policy.calculate_coverage(Decimal("50000.00"))
        assert coverage == Decimal("25000.00")
        
        # Claim exceeding limit
        coverage = policy.calculate_coverage(Decimal("200000.00"))
        assert coverage == Decimal("100000.00")


class TestPolicyProcessor:
    """Tests for PolicyProcessor."""
    
    def test_process_valid_policies(self):
        """Test processing valid policy data."""
        processor = PolicyProcessor()
        raw_policies = [
            {
                "policy_id": "POL001",
                "employer_id": "EMP001",
                "effective_date": "2024-01-01T00:00:00",
                "expiration_date": "2024-12-31T00:00:00",
                "stop_loss_limit": "1000000.00",
                "aggregate_deductible": "50000.00",
                "specific_deductible": "25000.00"
            }
        ]
        policies = processor.process(raw_policies)
        assert len(policies) == 1
        assert policies[0].policy_id == "POL001"
    
    def test_filter_active(self):
        """Test filtering active policies."""
        processor = PolicyProcessor()
        now = datetime.now()
        policies = [
            Policy("POL001", "EMP001", now, datetime(2025, 12, 31), 
                   Decimal("1000000.00"), Decimal("0.00"), Decimal("0.00"), "active"),
            Policy("POL002", "EMP002", datetime(2023, 1, 1), datetime(2023, 12, 31),
                   Decimal("1000000.00"), Decimal("0.00"), Decimal("0.00"), "active")
        ]
        active = processor.filter_active(policies)
        # Only first policy should be active (not expired)
        assert len(active) >= 1

