"""
End-to-end tests for complete pipeline workflows.

Tests full pipeline execution from start to finish.
"""
import pytest
import tempfile
import os
import json
from uuid import uuid4
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline, PoliciesPipeline
from src.utils.database import DatabaseManager


class TestEndToEndClaimsPipeline:
    """End-to-end tests for claims pipeline."""
    
    def test_full_claims_pipeline_with_real_data(self):
        """Test complete claims pipeline with sample data."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Create test data file
        test_data = {
            "claims": [
                {
                    "claim_id": "E2E-001",
                    "policy_id": "POL-2024-001",
                    "member_id": "MEM-001",
                    "claim_amount": "125000.00",
                    "incurred_date": "2024-03-15T00:00:00",
                    "paid_date": "2024-04-01T00:00:00",
                    "status": "paid",
                    "claim_type": "medical"
                },
                {
                    "claim_id": "E2E-002",
                    "policy_id": "POL-2024-001",
                    "member_id": "MEM-002",
                    "claim_amount": "75000.00",
                    "incurred_date": "2024-04-10T00:00:00",
                    "status": "approved",
                    "claim_type": "medical"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            data_path = tmp_file.name
        
        try:
            # Update config to use test data
            config_loader = ConfigLoader(config_dir="config")
            
            # Manually create config with test paths
            from src.pipelines.base import PipelineConfig, ExecutionContext
            from src.pipelines.claims_pipeline import ClaimsBronzeStep, ClaimsSilverStep, ClaimsGoldStep
            from src.transforms import ValidationStep
            
            steps = [
                ClaimsBronzeStep(source_path=data_path, db_path=db_path),
                ClaimsSilverStep(approval_threshold=100000.00, db_path=db_path),
                ValidationStep(name="claims_validation", data_key="silver_data"),
                ClaimsGoldStep(db_path=db_path)
            ]
            
            context = ExecutionContext(
                pipeline_name="e2e_claims_pipeline",
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
            assert results["steps_executed"] == 4
            assert results["steps_failed"] == 0
            
            # Verify data in database
            db = DatabaseManager(db_path=db_path)
            
            # Check bronze
            bronze = db.query("SELECT COUNT(*) as count FROM claims_bronze")
            assert bronze[0]["count"] == 2
            
            # Check silver
            silver = db.query("SELECT COUNT(*) as count FROM claims_silver")
            assert silver[0]["count"] == 2
            
            # Check gold (aggregated by policy)
            gold = db.query("SELECT COUNT(*) as count FROM claims_gold")
            assert gold[0]["count"] >= 1
            
            # Verify claim data
            claims = db.query("SELECT * FROM claims_silver WHERE claim_id = 'E2E-001'")
            assert len(claims) == 1
            assert float(claims[0]["claim_amount"]) == 125000.00
            
        finally:
            os.unlink(data_path)
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling and recovery."""
        # Create pipeline with invalid step
        from src.pipelines.base import PipelineConfig, ExecutionContext
        from src.pipelines.claims_pipeline import ClaimsBronzeStep
        
        steps = [
            ClaimsBronzeStep(source_path="nonexistent_file.json")
        ]
        
        context = ExecutionContext(
            pipeline_name="error_test",
            run_id=str(uuid4())
        )
        
        config = PipelineConfig(
            steps=steps,
            context=context,
            stop_on_error=True
        )
        
        from src.pipelines import ClaimsPipeline
        pipeline = ClaimsPipeline(config)
        
        # Should raise error
        with pytest.raises(Exception):
            pipeline.run()


class TestEndToEndPoliciesPipeline:
    """End-to-end tests for policies pipeline."""
    
    def test_full_policies_pipeline_with_real_data(self):
        """Test complete policies pipeline with sample data."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Create test data file
        test_data = {
            "policies": [
                {
                    "policy_id": "POL-E2E-001",
                    "employer_id": "EMP-001",
                    "effective_date": "2024-01-01T00:00:00",
                    "expiration_date": "2024-12-31T23:59:59",
                    "stop_loss_limit": "2000000.00",
                    "aggregate_deductible": "100000.00",
                    "specific_deductible": "50000.00",
                    "status": "active"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            data_path = tmp_file.name
        
        try:
            from src.pipelines.base import PipelineConfig, ExecutionContext
            from src.pipelines.policies_pipeline import PoliciesBronzeStep, PoliciesSilverStep, PoliciesGoldStep
            
            steps = [
                PoliciesBronzeStep(source_path=data_path, db_path=db_path),
                PoliciesSilverStep(db_path=db_path),
                PoliciesGoldStep(db_path=db_path)
            ]
            
            context = ExecutionContext(
                pipeline_name="e2e_policies_pipeline",
                run_id=str(uuid4())
            )
            
            config = PipelineConfig(
                steps=steps,
                context=context,
                stop_on_error=True
            )
            
            # Run pipeline
            pipeline = PoliciesPipeline(config)
            results = pipeline.run()
            
            # Verify execution
            assert results["steps_executed"] == 3
            assert results["steps_failed"] == 0
            
            # Verify data in database
            db = DatabaseManager(db_path=db_path)
            
            bronze = db.query("SELECT COUNT(*) as count FROM policies_bronze")
            assert bronze[0]["count"] == 1
            
            silver = db.query("SELECT COUNT(*) as count FROM policies_silver")
            assert silver[0]["count"] == 1
            
        finally:
            os.unlink(data_path)
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestEndToEndSDKWorkflow:
    """End-to-end tests for SDK workflows."""
    
    def test_complete_analyst_workflow(self):
        """Test complete analyst workflow from database load to analysis."""
        from src.sdk import StopLossAnalyst
        from src.utils.database import DatabaseManager
        from decimal import Decimal
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Initialize database (schema is created automatically in __init__)
            db = DatabaseManager(db_path=db_path)
            
            # Insert test data
            test_claim = {
                "claim_id": "SDK-001",
                "policy_id": "POL-SDK-001",
                "member_id": "MEM-001",
                "claim_amount": 150000.00,
                "incurred_date": "2024-01-15T00:00:00",
                "paid_date": None,
                "status": "approved",
                "claim_type": "medical"
            }
            db.insert_claims_silver([test_claim])
            
            test_policy = {
                "policy_id": "POL-SDK-001",
                "employer_id": "EMP-001",
                "effective_date": "2024-01-01T00:00:00",
                "expiration_date": "2024-12-31T23:59:59",
                "stop_loss_limit": 2000000.00,
                "aggregate_deductible": 100000.00,
                "specific_deductible": 50000.00,
                "status": "active"
            }
            db.insert_policies_silver([test_policy])
            
            # Create analyst with test database
            analyst = StopLossAnalyst(db_path=db_path, approval_threshold=Decimal("100000.00"))
            
            # Get summary (loads from database internally)
            summary = analyst.get_claims_by_policy_summary()
            assert "POL-SDK-001" in summary
            
            # Calculate utilization (loads from database internally)
            utilization = analyst.get_coverage_utilization()
            assert len(utilization) == 1
            assert utilization[0]["policy_id"] == "POL-SDK-001"
            assert utilization[0]["utilization_percent"] > 0
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

