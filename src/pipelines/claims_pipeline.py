"""
Claims processing pipeline.

Configuration-driven pipeline for processing stop loss insurance claims.
"""
from typing import List, Dict, Any
from uuid import uuid4
from src.pipelines.base import BasePipeline, PipelineConfig, ExecutionContext, PipelineStep
from src.transforms.bronze import BronzeStep
from src.transforms.silver import SilverStep
from src.transforms.gold import GoldStep, ValidationStep, AggregationStep
from src.domain.claims import ClaimsProcessor
from src.utils.io import FileReader, FileWriter
from src.utils.database import DatabaseManager
from src.mixins.logging import LoggingMixin
from src.mixins.metrics import MetricsMixin
from time import time
from decimal import Decimal


class ClaimsBronzeStep(BronzeStep):
    """Bronze step specifically for claims data."""
    
    def __init__(self, source_path: str = "", db_path: str = "warehouse.db"):
        super().__init__(name="claims_bronze", source_path=source_path)
        self.reader = FileReader(source_path, file_format="json") if source_path else None
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def _load_raw_data(self) -> Any:
        """Load raw claims data."""
        if self.reader:
            raw_data = self.reader.read()
            # Handle dictionary with "claims" key
            if isinstance(raw_data, dict) and "claims" in raw_data:
                return raw_data["claims"]
            return raw_data
        # For testing/demo purposes, return empty list
        return []
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write bronze data to database after execution."""
        super().after_execute(context, result)
        bronze_data = result.get("data", [])
        
        # Handle dictionary with "claims" key
        if isinstance(bronze_data, dict):
            if "claims" in bronze_data:
                bronze_data = bronze_data["claims"]
            else:
                bronze_data = [bronze_data]
        
        if bronze_data and isinstance(bronze_data, list) and len(bronze_data) > 0:
            # Ensure data is in correct format
            if isinstance(bronze_data[0], dict):
                self.db_manager.insert_claims_bronze(bronze_data)


class ClaimsSilverStep(SilverStep):
    """Silver step specifically for claims data."""
    
    def __init__(self, approval_threshold: float = 100000.00, db_path: str = "warehouse.db"):
        processor = ClaimsProcessor(approval_threshold=Decimal(str(approval_threshold)))
        super().__init__(name="claims_silver", domain_handler=processor)
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def _apply_business_logic(self, bronze_data: Any) -> Any:
        """Apply claims-specific business logic."""
        # Ensure data is a list
        if isinstance(bronze_data, dict):
            if "claims" in bronze_data:
                bronze_data = bronze_data["claims"]
            else:
                bronze_data = [bronze_data]
        
        # Process through domain handler
        if self.domain_handler:
            claims = self.domain_handler.process(bronze_data)
            # Convert Claim objects to dictionaries for downstream processing
            return [self._claim_to_dict(claim) for claim in claims]
        
        return bronze_data
    
    def _claim_to_dict(self, claim) -> Dict[str, Any]:
        """Convert Claim object to dictionary."""
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
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write silver data to database after execution."""
        super().after_execute(context, result)
        silver_data = result.get("data", [])
        
        # Handle dictionary format
        if isinstance(silver_data, dict):
            silver_data = [silver_data]
        
        if silver_data and isinstance(silver_data, list) and len(silver_data) > 0:
            if isinstance(silver_data[0], dict):
                self.db_manager.insert_claims_silver(silver_data)


class ClaimsGoldStep(GoldStep):
    """Gold step specifically for claims data."""
    
    def __init__(self, aggregation_config: Dict[str, Any] = None, db_path: str = "warehouse.db"):
        default_config = {
            "type": "by_policy",
            "group_by": ["policy_id"],
            "aggregations": {
                "claim_amount": "sum",
                "claim_id": "count"
            }
        }
        config = aggregation_config or default_config
        super().__init__(name="claims_gold", aggregation_config=config)
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write gold data to database after execution."""
        super().after_execute(context, result)
        gold_data = result.get("data", [])
        if gold_data and isinstance(gold_data, list):
            # Calculate aggregations for database
            aggregated = self._prepare_gold_data(gold_data, context)
            self.db_manager.insert_claims_gold(aggregated)
    
    def _prepare_gold_data(self, gold_data: List[Dict[str, Any]], context: ExecutionContext = None) -> List[Dict[str, Any]]:
        """
        Prepare gold data for database insertion.
        
        Uses centralized business rules from ClaimsAggregator.
        The gold_data is already aggregated from GoldStep, but we need to format it for database.
        """
        from src.business_rules.aggregations import ClaimsAggregator
        
        aggregator = ClaimsAggregator()
        # gold_data from GoldStep.execute() is already aggregated, but we need to ensure it's in the right format
        # The GoldStep may return aggregated data in a different format, so we re-aggregate from silver_data
        # Get silver data from context to ensure we use the correct source
        if context:
            silver_data = context.get("silver_data")
            # If silver_data is available, use it; otherwise use gold_data
            if silver_data and isinstance(silver_data, list) and len(silver_data) > 0:
                aggregated = aggregator.aggregate_by_policy(silver_data)
            else:
                # If gold_data is already in the right format, use it
                aggregated = gold_data if isinstance(gold_data, list) else []
        else:
            # No context, use gold_data directly
            aggregated = gold_data if isinstance(gold_data, list) else []
        
        # Ensure format matches database schema
        result = []
        for agg in aggregated:
            result.append({
                "policy_id": agg["policy_id"],
                "total_claims": agg["total_claims"],
                "claim_count": agg["claim_count"],
                "avg_claim_amount": agg.get("avg_claim_amount", 0),
                "max_claim_amount": agg.get("max_claim_amount", 0),
                "min_claim_amount": agg.get("min_claim_amount", 0)
            })
        
        return result


class ClaimsPipeline(BasePipeline, LoggingMixin, MetricsMixin):
    """
    Claims processing pipeline.
    
    Example usage:
        config = PipelineConfig(
            steps=[
                ClaimsBronzeStep(source_path="data/raw_claims.json"),
                ClaimsSilverStep(),
                ValidationStep(name="claims_validation", data_key="silver_data"),
                ClaimsGoldStep()
            ],
            context=ExecutionContext(
                pipeline_name="claims_pipeline",
                run_id=str(uuid4())
            )
        )
        pipeline = ClaimsPipeline(config)
        results = pipeline.run()
    """
    
    def __init__(self, config: PipelineConfig):
        BasePipeline.__init__(self, config)
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        MetricsMixin.__init__(self)
    
    def before_run(self) -> None:
        """Hook called before pipeline execution."""
        self.log_info("Starting claims pipeline", 
                     pipeline_name=self.context.pipeline_name,
                     run_id=self.context.run_id)
        self.record_metric("pipeline_start_time", time(), unit="timestamp")
    
    def after_run(self, summary: Dict[str, Any]) -> None:
        """Hook called after successful pipeline execution."""
        self.log_info("Claims pipeline completed", 
                     steps_completed=summary["steps_executed"],
                     steps_failed=summary["steps_failed"])
        self.record_metric("pipeline_duration", 
                          time() - self.context.metadata.get("start_time", time()),
                          unit="seconds")
        
        # Publish metadata to Atlas
        self._publish_atlas_metadata()
    
    def _publish_atlas_metadata(self) -> None:
        """Publish claims metadata to Atlas."""
        import os
        from src.utils.atlas import AtlasClient
        from src.utils.atlas_payloads import build_claims_table_payload, build_claims_aggregates_payload
        
        # Default to localhost for local development, atlas hostname for Docker
        atlas_url = os.getenv("ATLAS_URL", "http://localhost:21000")
        atlas_enabled = os.getenv("ATLAS_ENABLED", "true").lower() == "true"
        
        if not atlas_enabled:
            self.log_info("Atlas publishing disabled, skipping")
            return
        
        try:
            client = AtlasClient(base_url=atlas_url, enabled=True)
            
            # Publish claims fact table metadata
            self.log_info("Publishing claims fact table metadata to Atlas")
            payload = build_claims_table_payload()
            client.publish(payload)
            
            # Publish claims aggregates metadata
            self.log_info("Publishing claims aggregates metadata to Atlas")
            payload = build_claims_aggregates_payload()
            client.publish(payload)
            
            self.log_info("Claims metadata published to Atlas successfully")
        except Exception as e:
            self.log_warning(f"Failed to publish claims metadata to Atlas", error=e)
    
    def on_error(self, error: Exception) -> None:
        """Hook called when pipeline execution fails."""
        self.log_error("Claims pipeline failed", error=error)

