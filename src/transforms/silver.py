"""
Silver layer: Business rule application and enrichment.
"""
from typing import Any, Dict
from src.pipelines.base import PipelineStep, ExecutionContext
from src.mixins.logging import LoggingMixin
from src.mixins.metrics import MetricsMixin


class SilverStep(PipelineStep, LoggingMixin, MetricsMixin):
    """
    Silver layer step for business rule application.
    
    Responsibilities:
    - Apply business logic from domain layer
    - Enrich data with calculated fields
    - Apply business validations
    - Prepare data for gold layer aggregation
    """
    
    def __init__(self, name: str = "silver", domain_handler: Any = None, **kwargs):
        PipelineStep.__init__(self, name)
        LoggingMixin.__init__(self, logger_name=f"{self.__class__.__name__}.{name}", **kwargs)
        MetricsMixin.__init__(self, **kwargs)
        self.domain_handler = domain_handler
    
    def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute silver layer transformation.
        
        Args:
            context: Execution context (should contain bronze_data)
            
        Returns:
            Dictionary with silver data and metadata
        """
        self.log_info("Starting silver layer processing")
        
        # Get bronze data from context
        bronze_data = context.get("bronze_data")
        if bronze_data is None:
            raise ValueError("Bronze data not found in context. Run bronze step first.")
        
        # Apply business logic
        enriched_data = self._apply_business_logic(bronze_data)
        
        # Apply business validations
        validated_data = self._apply_validations(enriched_data)
        
        # Store in context for downstream steps
        context.set("silver_data", validated_data)
        context.set("silver_metadata", {
            "record_count": len(validated_data) if isinstance(validated_data, list) else 1,
            "domain_handler": self.domain_handler.__class__.__name__ if self.domain_handler else None
        })
        
        # Record metrics
        record_count = len(validated_data) if isinstance(validated_data, list) else 1
        self.record_count("silver_records_processed", record_count)
        
        self.log_info(f"Silver layer completed", records=record_count)
        
        return {
            "data": validated_data,
            "metadata": context.get("silver_metadata")
        }
    
    def _apply_business_logic(self, bronze_data: Any) -> Any:
        """
        Apply business logic from domain layer.
        
        This delegates to domain handlers for business rule application.
        """
        self.log_info("Applying business logic")
        
        if self.domain_handler:
            # Domain handler should have methods to process data
            if hasattr(self.domain_handler, "process"):
                return self.domain_handler.process(bronze_data)
        
        # Placeholder - actual implementation would use domain logic
        return bronze_data
    
    def _apply_validations(self, data: Any) -> Any:
        """
        Apply business validations.
        
        Uses validation mixin if available on domain handler.
        """
        self.log_info("Applying business validations")
        
        if self.domain_handler and hasattr(self.domain_handler, "validate"):
            is_valid = self.domain_handler.validate(data)
            if not is_valid:
                self.log_warning("Business validations failed", 
                               results=self.domain_handler.get_validation_results() 
                               if hasattr(self.domain_handler, "get_validation_results") else None)
        
        return data

