"""
Example: Configuration-driven pipeline execution using YAML.

Demonstrates how to run pipelines from YAML configuration files.
"""
import sys
from pathlib import Path

# Add project root to path if package not installed
try:
    from src.utils.config_loader import ConfigLoader
    from src.pipelines import ClaimsPipeline, PoliciesPipeline
except ImportError:
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.utils.config_loader import ConfigLoader
    from src.pipelines import ClaimsPipeline, PoliciesPipeline


def run_claims_pipeline_from_yaml():
    """Example: Run claims pipeline from YAML configuration."""
    
    # Load configuration from YAML
    config_loader = ConfigLoader(config_dir="config")
    config = config_loader.create_pipeline_config("claims_pipeline")
    
    # Create and run pipeline
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    
    print(f"Pipeline completed: {results['pipeline_name']}")
    print(f"Steps executed: {results['steps_executed']}")
    print(f"Steps failed: {results['steps_failed']}")
    
    return results


def run_policies_pipeline_from_yaml():
    """Example: Run policies pipeline from YAML configuration."""
    
    # Load configuration from YAML
    config_loader = ConfigLoader(config_dir="config")
    config = config_loader.create_pipeline_config("policies_pipeline")
    
    # Create and run pipeline
    pipeline = PoliciesPipeline(config)
    results = pipeline.run()
    
    print(f"Pipeline completed: {results['pipeline_name']}")
    print(f"Steps executed: {results['steps_executed']}")
    print(f"Steps failed: {results['steps_failed']}")
    
    return results


def run_pipeline_with_custom_run_id():
    """Example: Run pipeline with a custom run ID."""
    
    config_loader = ConfigLoader(config_dir="config")
    config = config_loader.create_pipeline_config(
        "claims_pipeline",
        run_id="custom-run-12345"
    )
    
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    
    print(f"Run ID: {results['run_id']}")
    return results


if __name__ == "__main__":
    print("Running claims pipeline from YAML...")
    run_claims_pipeline_from_yaml()
    
    print("\nRunning policies pipeline from YAML...")
    run_policies_pipeline_from_yaml()
    
    print("\nRunning with custom run ID...")
    run_pipeline_with_custom_run_id()
