"""
Policies processing pipeline.

Configuration-driven pipeline for processing stop loss insurance policies.
"""
from typing import List, Dict, Any
from uuid import uuid4
from src.pipelines.base import BasePipeline, PipelineConfig, ExecutionContext, PipelineStep
from src.transforms.bronze import BronzeStep
from src.transforms.silver import SilverStep
from src.transforms.gold import GoldStep, ValidationStep, AggregationStep
from src.domain.policies import PolicyProcessor
from src.utils.io import FileReader, FileWriter
from src.utils.database import DatabaseManager
from src.mixins.logging import LoggingMixin
from src.mixins.metrics import MetricsMixin
from time import time


class PoliciesBronzeStep(BronzeStep):
    """Bronze step specifically for policies data."""
    
    def __init__(self, source_path: str = "", db_path: str = "warehouse.db"):
        super().__init__(name="policies_bronze", source_path=source_path)
        self.reader = FileReader(source_path, file_format="json") if source_path else None
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def _load_raw_data(self) -> Any:
        """Load raw policies data."""
        if self.reader:
            raw_data = self.reader.read()
            # Handle dictionary with "policies" key
            if isinstance(raw_data, dict) and "policies" in raw_data:
                return raw_data["policies"]
            return raw_data
        # For testing/demo purposes, return empty list
        return []
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write bronze data to database after execution."""
        super().after_execute(context, result)
        bronze_data = result.get("data", [])
        
        # Handle dictionary with "policies" key
        if isinstance(bronze_data, dict):
            if "policies" in bronze_data:
                bronze_data = bronze_data["policies"]
            else:
                bronze_data = [bronze_data]
        
        if bronze_data and isinstance(bronze_data, list) and len(bronze_data) > 0:
            if isinstance(bronze_data[0], dict):
                self.db_manager.insert_policies_bronze(bronze_data)


class PoliciesSilverStep(SilverStep):
    """Silver step specifically for policies data."""
    
    def __init__(self, db_path: str = "warehouse.db"):
        super().__init__(name="policies_silver", domain_handler=PolicyProcessor())
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def _apply_business_logic(self, bronze_data: Any) -> Any:
        """Apply policies-specific business logic."""
        # Ensure data is a list
        if isinstance(bronze_data, dict):
            if "policies" in bronze_data:
                bronze_data = bronze_data["policies"]
            else:
                bronze_data = [bronze_data]
        
        # Process through domain handler
        if self.domain_handler:
            policies = self.domain_handler.process(bronze_data)
            # Convert Policy objects to dictionaries for downstream processing
            return [self._policy_to_dict(policy) for policy in policies]
        
        return bronze_data
    
    def _policy_to_dict(self, policy) -> Dict[str, Any]:
        """Convert Policy object to dictionary."""
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
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write silver data to database after execution."""
        super().after_execute(context, result)
        silver_data = result.get("data", [])
        
        # Handle dictionary format
        if isinstance(silver_data, dict):
            silver_data = [silver_data]
        
        if silver_data and isinstance(silver_data, list) and len(silver_data) > 0:
            if isinstance(silver_data[0], dict):
                self.db_manager.insert_policies_silver(silver_data)


class PoliciesGoldStep(GoldStep):
    """Gold step specifically for policies data."""
    
    def __init__(self, aggregation_config: Dict[str, Any] = None, db_path: str = "warehouse.db"):
        default_config = {
            "type": "by_employer",
            "group_by": ["employer_id"],
            "aggregations": {
                "stop_loss_limit": "sum",
                "policy_id": "count"
            }
        }
        config = aggregation_config or default_config
        super().__init__(name="policies_gold", aggregation_config=config)
        self.db_manager = DatabaseManager(db_path=db_path)
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Write gold data to database after execution."""
        super().after_execute(context, result)
        gold_data = result.get("data", [])
        if gold_data and isinstance(gold_data, list):
            aggregated = self._prepare_gold_data(gold_data, context)
            self.db_manager.insert_policies_gold(aggregated)
    
    def _prepare_gold_data(self, gold_data: List[Dict[str, Any]], context: ExecutionContext = None) -> List[Dict[str, Any]]:
        """
        Prepare gold data for database insertion.
        
        Uses centralized business rules from PoliciesAggregator.
        """
        from src.business_rules.aggregations import PoliciesAggregator
        
        aggregator = PoliciesAggregator()
        # Get silver data from context if available, otherwise use gold_data
        if context:
            silver_data = context.get("silver_data")
            if silver_data and isinstance(silver_data, list) and len(silver_data) > 0:
                aggregated = aggregator.aggregate_by_employer(silver_data)
            else:
                aggregated = gold_data if isinstance(gold_data, list) else []
        else:
            aggregated = gold_data if isinstance(gold_data, list) else []
        
        # Ensure format matches database schema
        result = []
        for agg in aggregated:
            result.append({
                "employer_id": agg["employer_id"],
                "total_coverage": agg["total_coverage"],
                "policy_count": agg["policy_count"],
                "avg_stop_loss_limit": agg.get("avg_stop_loss_limit", 0)
            })
        
        return result


class PoliciesPipeline(BasePipeline, LoggingMixin, MetricsMixin):
    """
    Policies processing pipeline.
    
    Example usage:
        config = PipelineConfig(
            steps=[
                PoliciesBronzeStep(source_path="data/raw_policies.json"),
                PoliciesSilverStep(),
                ValidationStep(name="policies_validation", data_key="silver_data"),
                PoliciesGoldStep()
            ],
            context=ExecutionContext(
                pipeline_name="policies_pipeline",
                run_id=str(uuid4())
            )
        )
        pipeline = PoliciesPipeline(config)
        results = pipeline.run()
    """
    
    def __init__(self, config: PipelineConfig):
        BasePipeline.__init__(self, config)
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        MetricsMixin.__init__(self)
    
    def before_run(self) -> None:
        """Hook called before pipeline execution."""
        self.log_info("Starting policies pipeline", 
                     pipeline_name=self.context.pipeline_name,
                     run_id=self.context.run_id)
        self.context.set("start_time", time())
        self.record_metric("pipeline_start_time", time(), unit="timestamp")
    
    def after_run(self, summary: Dict[str, Any]) -> None:
        """Hook called after successful pipeline execution."""
        start_time = self.context.get("start_time", time())
        duration = time() - start_time
        
        self.log_info("Policies pipeline completed", 
                     steps_completed=summary["steps_executed"],
                     steps_failed=summary["steps_failed"],
                     duration_seconds=duration)
        self.record_timing("pipeline_duration", duration)
        
        # Publish metadata to Atlas
        self._publish_atlas_metadata()
    
    def _publish_atlas_metadata(self) -> None:
        """Publish policies metadata to Atlas."""
        import os
        from src.utils.atlas import AtlasClient
        from src.utils.atlas_payloads import build_policies_table_payload, build_policies_aggregates_payload
        
        atlas_url = os.getenv("ATLAS_URL", "http://atlas:21000")
        atlas_enabled = os.getenv("ATLAS_ENABLED", "true").lower() == "true"
        
        if not atlas_enabled:
            self.log_info("Atlas publishing disabled, skipping")
            return
        
        try:
            client = AtlasClient(base_url=atlas_url, enabled=True)
            
            # Publish policies fact table metadata
            self.log_info("Publishing policies fact table metadata to Atlas")
            payload = build_policies_table_payload()
            client.publish(payload)
            
            # Publish policies aggregates metadata
            self.log_info("Publishing policies aggregates metadata to Atlas")
            payload = build_policies_aggregates_payload()
            client.publish(payload)
            
            self.log_info("Policies metadata published to Atlas successfully")
        except Exception as e:
            self.log_warning(f"Failed to publish policies metadata to Atlas", error=e)
    
    def on_error(self, error: Exception) -> None:
        """Hook called when pipeline execution fails."""
        self.log_error("Policies pipeline failed", error=error)

