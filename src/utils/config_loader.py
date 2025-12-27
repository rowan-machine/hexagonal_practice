"""
Configuration loader for YAML-based pipeline configuration.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.pipelines.base import PipelineConfig, ExecutionContext
# Note: Pipeline step imports are done lazily in methods to avoid circular dependencies
from src.transforms import ValidationStep, AggregationStep
from src.domain.claims import ClaimsProcessor
from src.domain.policies import PolicyProcessor
from src.mixins.logging import LoggingMixin
from decimal import Decimal


class ConfigLoader(LoggingMixin):
    """Loads and parses YAML pipeline configurations."""
    
    def __init__(self, config_dir: str = "pipelines_config"):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.config_dir = Path(config_dir)
    
    def load_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Load pipeline configuration from YAML file.
        
        Args:
            pipeline_name: Name of the pipeline (e.g., "claims_pipeline")
            
        Returns:
            Parsed configuration dictionary
        """
        config_path = self.config_dir / f"{pipeline_name}.yml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Pipeline config not found: {config_path}")
        
        self.log_info(f"Loading pipeline config", path=str(config_path))
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def create_pipeline_config(self, pipeline_name: str, run_id: Optional[str] = None, db_path: str = "warehouse.db") -> PipelineConfig:
        """
        Create PipelineConfig from YAML file.
        
        Args:
            pipeline_name: Name of the pipeline
            run_id: Optional run ID (generated if not provided)
            db_path: Path to SQLite database
            
        Returns:
            PipelineConfig instance
        """
        from uuid import uuid4
        
        yaml_config = self.load_pipeline_config(pipeline_name)
        pipeline_config = yaml_config.get("pipeline", {})
        
        # Create execution context
        context = ExecutionContext(
            pipeline_name=pipeline_config.get("name", pipeline_name),
            run_id=run_id or str(uuid4()),
            metadata={
                "description": pipeline_config.get("description", ""),
                "config_source": f"{pipeline_name}.yml",
                "db_path": db_path
            }
        )
        
        # Store context for step creation
        self.context = context
        
        # Create steps from configuration
        steps = self._create_steps_from_config(pipeline_config.get("steps", []))
        
        # Get execution settings
        execution = pipeline_config.get("execution", {})
        
        return PipelineConfig(
            steps=steps,
            context=context,
            stop_on_error=execution.get("stop_on_error", True),
            skip_completed=execution.get("skip_completed", False)
        )
    
    def _create_steps_from_config(self, steps_config: List[Dict[str, Any]]) -> List:
        """
        Create pipeline steps from configuration.
        
        Args:
            steps_config: List of step configurations
            
        Returns:
            List of PipelineStep instances
        """
        steps = []
        
        for step_config in steps_config:
            step_type = step_config.get("type")
            step_name = step_config.get("name")
            config = step_config.get("config", {})
            
            if step_type == "bronze":
                step = self._create_bronze_step(step_name, step_config)
            elif step_type == "silver":
                step = self._create_silver_step(step_name, step_config)
            elif step_type == "gold":
                step = self._create_gold_step(step_name, step_config)
            elif step_type == "validation":
                step = self._create_validation_step(step_name, step_config)
            elif step_type == "aggregation":
                step = self._create_aggregation_step(step_name, step_config)
            else:
                self.log_warning(f"Unknown step type: {step_type}, skipping")
                continue
            
            steps.append(step)
        
        return steps
    
    def _create_bronze_step(self, name: str, step_config: Dict[str, Any]) -> Any:
        """Create a bronze step from configuration."""
        # Lazy import to avoid circular dependencies
        from src.pipelines.claims_pipeline import ClaimsBronzeStep
        from src.pipelines.policies_pipeline import PoliciesBronzeStep
        
        source = step_config.get("source", {})
        source_path = source.get("path", "")
        db_path = self.context.metadata.get("db_path", "warehouse.db") if hasattr(self, 'context') else "warehouse.db"
        
        # Determine which bronze step to create based on pipeline name
        if "claims" in name.lower():
            return ClaimsBronzeStep(source_path=source_path, db_path=db_path)
        elif "policies" in name.lower():
            return PoliciesBronzeStep(source_path=source_path, db_path=db_path)
        else:
            from src.transforms.bronze import BronzeStep
            return BronzeStep(name=name, source_path=source_path)
    
    def _create_silver_step(self, name: str, step_config: Dict[str, Any]) -> Any:
        """Create a silver step from configuration."""
        # Lazy import to avoid circular dependencies
        from src.pipelines.claims_pipeline import ClaimsSilverStep
        from src.pipelines.policies_pipeline import PoliciesSilverStep
        
        domain_handler_name = step_config.get("domain_handler", "")
        config = step_config.get("config", {})
        db_path = self.context.metadata.get("db_path", "warehouse.db") if hasattr(self, 'context') else "warehouse.db"
        
        # Create appropriate silver step
        if domain_handler_name == "ClaimsProcessor":
            approval_threshold = config.get("approval_threshold", 100000.00)
            return ClaimsSilverStep(approval_threshold=approval_threshold, db_path=db_path)
        elif domain_handler_name == "PolicyProcessor":
            return PoliciesSilverStep(db_path=db_path)
        else:
            from src.transforms.silver import SilverStep
            return SilverStep(name=name, domain_handler=None)
    
    def _create_gold_step(self, name: str, step_config: Dict[str, Any]) -> Any:
        """Create a gold step from configuration."""
        # Lazy import to avoid circular dependencies
        from src.pipelines.claims_pipeline import ClaimsGoldStep
        from src.pipelines.policies_pipeline import PoliciesGoldStep
        
        aggregation_config = step_config.get("aggregation", {})
        db_path = self.context.metadata.get("db_path", "warehouse.db") if hasattr(self, 'context') else "warehouse.db"
        
        # Determine which gold step to create
        if "claims" in name.lower():
            return ClaimsGoldStep(aggregation_config=aggregation_config, db_path=db_path)
        elif "policies" in name.lower():
            return PoliciesGoldStep(aggregation_config=aggregation_config, db_path=db_path)
        else:
            from src.transforms.gold import GoldStep
            return GoldStep(name=name, aggregation_config=aggregation_config)
    
    def _create_validation_step(self, name: str, step_config: Dict[str, Any]) -> ValidationStep:
        """Create a validation step from configuration."""
        data_key = step_config.get("data_key", "silver_data")
        return ValidationStep(name=name, data_key=data_key)
    
    def _create_aggregation_step(self, name: str, step_config: Dict[str, Any]) -> AggregationStep:
        """Create an aggregation step from configuration."""
        aggregation = step_config.get("aggregation", {})
        return AggregationStep(
            name=name,
            source_data_key=step_config.get("source_data_key", "silver_data"),
            aggregation_type=aggregation.get("type", "summary")
        )

