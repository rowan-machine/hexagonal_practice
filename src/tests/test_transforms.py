"""
Unit tests for transform layers.

Tests data transformation logic and business rule application.
"""
import pytest
from src.transforms.bronze import BronzeStep
from src.transforms.silver import SilverStep
from src.transforms.gold import GoldStep
from src.pipelines import ExecutionContext
from src.domain.claims import ClaimsProcessor


class TestBronzeStep:
    """Tests for BronzeStep."""
    
    def test_bronze_step_creation(self):
        """Test creating a bronze step."""
        step = BronzeStep(name="test_bronze", source_path="test.json")
        assert step.name == "test_bronze"
        assert step.source_path == "test.json"
    
    def test_bronze_step_execution(self):
        """Test bronze step execution."""
        step = BronzeStep(name="test_bronze")
        context = ExecutionContext(pipeline_name="test", run_id="test-123")
        
        # Mock the load method
        step._load_raw_data = lambda: [{"id": 1, "value": "test"}]
        
        result = step.execute(context)
        assert "data" in result
        assert "metadata" in result
        assert context.get("bronze_data") is not None


class TestSilverStep:
    """Tests for SilverStep."""
    
    def test_silver_step_with_domain_handler(self):
        """Test silver step with domain handler."""
        processor = ClaimsProcessor()
        step = SilverStep(name="test_silver", domain_handler=processor)
        context = ExecutionContext(pipeline_name="test", run_id="test-123")
        
        # Set up bronze data
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
        context.set("bronze_data", raw_claims)
        
        result = step.execute(context)
        assert "data" in result
        assert context.get("silver_data") is not None
    
    def test_silver_step_requires_bronze_data(self):
        """Test that silver step requires bronze data."""
        step = SilverStep(name="test_silver")
        context = ExecutionContext(pipeline_name="test", run_id="test-123")
        
        with pytest.raises(ValueError, match="Bronze data not found"):
            step.execute(context)


class TestGoldStep:
    """Tests for GoldStep."""
    
    def test_gold_step_execution(self):
        """Test gold step execution."""
        step = GoldStep(name="test_gold")
        context = ExecutionContext(pipeline_name="test", run_id="test-123")
        
        # Set up silver data
        silver_data = [{"policy_id": "POL001", "amount": 1000}]
        context.set("silver_data", silver_data)
        
        result = step.execute(context)
        assert "data" in result
        assert "metadata" in result
        assert context.get("gold_data") is not None
    
    def test_gold_step_requires_silver_data(self):
        """Test that gold step requires silver data."""
        step = GoldStep(name="test_gold")
        context = ExecutionContext(pipeline_name="test", run_id="test-123")
        
        with pytest.raises(ValueError, match="Silver data not found"):
            step.execute(context)

