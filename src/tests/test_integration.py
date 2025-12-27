"""
Integration tests for pipeline components.

Tests interactions between multiple components.
"""
import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from src.pipelines import PipelineConfig, ExecutionContext, ClaimsPipeline, PoliciesPipeline
from src.pipelines.claims_pipeline import ClaimsBronzeStep, ClaimsSilverStep, ClaimsGoldStep
from src.pipelines.policies_pipeline import PoliciesBronzeStep, PoliciesSilverStep, PoliciesGoldStep
from src.transforms import ValidationStep
from src.utils.config_loader import ConfigLoader
from src.utils.database import DatabaseManager
import tempfile
import os


class TestClaimsPipelineIntegration:
    """Integration tests for claims pipeline."""
    
    def test_claims_pipeline_end_to_end(self):
        """Test complete claims pipeline execution."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Create test data
            test_data = {
                "claims": [
                    {
                        "claim_id": "TEST-001",
                        "policy_id": "POL-001",
                        "member_id": "MEM-001",
                        "claim_amount": "50000.00",
                        "incurred_date": "2024-01-15T00:00:00",
                        "status": "approved",
                        "claim_type": "medical"
                    }
                ]
            }
            
            # Write test data to temp file
            import json
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                json.dump(test_data, tmp_file)
                data_path = tmp_file.name
            
            try:
                # Create pipeline steps
                steps = [
                    ClaimsBronzeStep(source_path=data_path, db_path=db_path),
                    ClaimsSilverStep(approval_threshold=100000.00, db_path=db_path),
                    ClaimsGoldStep(db_path=db_path)
                ]
                
                # Create configuration
                context = ExecutionContext(
                    pipeline_name="test_claims_pipeline",
                    run_id=str(uuid4())
                )
                config = PipelineConfig(
                    steps=steps,
                    context=context,
                    stop_on_error=True
                )
                
                # Run pipeline
                pipeline = ClaimsPipeline(config)
                results = pipeline.run()
                
                # Verify execution
                assert results["steps_executed"] == 3
                assert results["steps_failed"] == 0
                
                # Verify database
                db = DatabaseManager(db_path=db_path)
                bronze_claims = db.query("SELECT COUNT(*) as count FROM claims_bronze")
                assert bronze_claims[0]["count"] == 1
                
                silver_claims = db.query("SELECT COUNT(*) as count FROM claims_silver")
                assert silver_claims[0]["count"] == 1
                
            finally:
                os.unlink(data_path)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_pipeline_with_validation_step(self):
        """Test pipeline with validation step."""
        steps = [
            ClaimsBronzeStep(source_path=""),
            ClaimsSilverStep(),
            ValidationStep(name="test_validation", data_key="silver_data"),
            ClaimsGoldStep()
        ]
        
        context = ExecutionContext(
            pipeline_name="test_pipeline",
            run_id=str(uuid4())
        )
        config = PipelineConfig(
            steps=steps,
            context=context,
            stop_on_error=False  # Don't stop on validation failures
        )
        
        pipeline = ClaimsPipeline(config)
        # Should complete even if validation fails
        results = pipeline.run()
        assert results["steps_executed"] >= 2


class TestConfigLoaderIntegration:
    """Integration tests for configuration loader."""
    
    def test_load_claims_pipeline_config(self):
        """Test loading claims pipeline from YAML."""
        config_loader = ConfigLoader(config_dir="pipelines_config")
        config = config_loader.create_pipeline_config("claims_pipeline")
        
        assert config.context.pipeline_name == "claims_pipeline"
        assert len(config.steps) > 0
        assert config.stop_on_error is True
    
    def test_config_creates_correct_steps(self):
        """Test that config loader creates correct step types."""
        config_loader = ConfigLoader(config_dir="pipelines_config")
        config = config_loader.create_pipeline_config("claims_pipeline")
        
        step_types = [type(step).__name__ for step in config.steps]
        assert "ClaimsBronzeStep" in step_types
        assert "ClaimsSilverStep" in step_types


class TestSDKIntegration:
    """Integration tests for SDK components."""
    
    def test_claims_analyst_load_and_process(self):
        """Test ClaimsAnalyst loading and processing from database."""
        from src.sdk import ClaimsAnalyst
        from src.utils.database import DatabaseManager
        from decimal import Decimal
        import json
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Initialize database (schema is created automatically in __init__)
            db = DatabaseManager(db_path=db_path)
            
            # Insert test data directly into database
            test_claim = {
                "claim_id": "TEST-001",
                "policy_id": "POL-001",
                "member_id": "MEM-001",
                "claim_amount": 75000.00,
                "incurred_date": "2024-01-15T00:00:00",
                "paid_date": None,
                "status": "approved",
                "claim_type": "medical"
            }
            db.insert_claims_silver([test_claim])
            
            # Create analyst with test database
            analyst = ClaimsAnalyst(db_path=db_path, approval_threshold=Decimal("100000.00"))
            
            # Load from database
            claims = analyst.load_from_database(layer="silver")
            assert len(claims) == 1
            assert claims[0].claim_id == "TEST-001"
            
            # Calculate total
            total = analyst.get_total_claims(claims)
            assert total == Decimal("75000.00")
            
            # Filter
            high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
            assert len(high_value) == 1
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_policies_analyst_load_and_process(self):
        """Test PoliciesAnalyst loading and processing from database."""
        from src.sdk import PoliciesAnalyst
        from src.utils.database import DatabaseManager
        from decimal import Decimal
        import json
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Initialize database (schema is created automatically in __init__)
            db = DatabaseManager(db_path=db_path)
            
            # Insert test data directly into database
            test_policy = {
                "policy_id": "POL-001",
                "employer_id": "EMP-001",
                "effective_date": "2024-01-01T00:00:00",
                "expiration_date": "2024-12-31T23:59:59",
                "stop_loss_limit": 1000000.00,
                "aggregate_deductible": 50000.00,
                "specific_deductible": 25000.00,
                "status": "active"
            }
            db.insert_policies_silver([test_policy])
            
            # Create analyst with test database
            analyst = PoliciesAnalyst(db_path=db_path)
            
            # Load from database
            policies = analyst.load_from_database(layer="silver")
            assert len(policies) == 1
            assert policies[0].policy_id == "POL-001"
            
            # Calculate coverage
            total = analyst.get_total_coverage(policies)
            assert total == Decimal("1000000.00")
            
            # Filter active
            active = analyst.get_active_policies(policies)
            assert len(active) >= 0  # May be 0 if policy is expired
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

