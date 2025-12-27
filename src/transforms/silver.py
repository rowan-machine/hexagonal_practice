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
        Handles both single items and lists of items.
        """
        self.log_info("Applying business validations")
        
        if self.domain_handler and hasattr(self.domain_handler, "validate"):
            # Clear previous validation results
            if hasattr(self.domain_handler, "clear_validation_results"):
                self.domain_handler.clear_validation_results()
            
            # Handle list of items
            if isinstance(data, list):
                all_valid = True
                for item in data:
                    # If item is a dict, we need to convert it back to a domain object for validation
                    # This happens when SilverStep converts domain objects to dicts
                    if isinstance(item, dict):
                        # Try to find a method to convert dict back to domain object
                        # Check for both _create_claim_from_dict and _create_policy_from_dict
                        if hasattr(self.domain_handler, "_create_claim_from_dict"):
                            domain_obj = self.domain_handler._create_claim_from_dict(item)
                        elif hasattr(self.domain_handler, "_create_policy_from_dict"):
                            domain_obj = self.domain_handler._create_policy_from_dict(item)
                        else:
                            # No conversion method found, skip validation for this item
                            self.log_warning("Cannot validate dict item: no conversion method found")
                            continue
                        
                        is_valid = self.domain_handler.validate(domain_obj)
                        if not is_valid:
                            all_valid = False
                    else:
                        # Item is already a domain object (Claim, Policy, etc.)
                        is_valid = self.domain_handler.validate(item)
                        if not is_valid:
                            all_valid = False
                
                if not all_valid:
                    self.log_warning("Business validations failed", 
                                   results=self.domain_handler.get_validation_results() 
                                   if hasattr(self.domain_handler, "get_validation_results") else None)
            else:
                # Single item validation
                # If it's a dict, convert it first
                if isinstance(data, dict):
                    if hasattr(self.domain_handler, "_create_claim_from_dict"):
                        data = self.domain_handler._create_claim_from_dict(data)
                    elif hasattr(self.domain_handler, "_create_policy_from_dict"):
                        data = self.domain_handler._create_policy_from_dict(data)
                
                is_valid = self.domain_handler.validate(data)
                if not is_valid:
                    self.log_warning("Business validations failed", 
                                   results=self.domain_handler.get_validation_results() 
                                   if hasattr(self.domain_handler, "get_validation_results") else None)
        
        return data

