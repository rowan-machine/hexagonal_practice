"""
Local pipeline runner.

Loads pipeline configurations from YAML files and executes them.
"""
import argparse
import sys
from pathlib import Path
from typing import List
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline, PoliciesPipeline
from src.mixins.logging import LoggingMixin


class PipelineRunner(LoggingMixin):
    """Runs pipelines from YAML configuration."""
    
    def __init__(self, config_dir: str = "pipelines_config"):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.config_loader = ConfigLoader(config_dir=config_dir)
    
    def run_pipeline(self, pipeline_name: str, run_id: str = None, db_path: str = "warehouse.db") -> dict:
        """
        Run a pipeline from configuration.
        
        Args:
            pipeline_name: Name of the pipeline (e.g., "claims_pipeline")
            run_id: Optional run ID
            db_path: Path to SQLite database
            
        Returns:
            Pipeline execution results
        """
        self.log_info(f"Running pipeline", pipeline=pipeline_name, db_path=db_path)
        
        try:
            # Load configuration
            config = self.config_loader.create_pipeline_config(pipeline_name, run_id=run_id, db_path=db_path)
            
            # Determine which pipeline class to use
            if "claims" in pipeline_name.lower():
                pipeline = ClaimsPipeline(config)
            elif "policies" in pipeline_name.lower():
                pipeline = PoliciesPipeline(config)
            else:
                raise ValueError(f"Unknown pipeline type: {pipeline_name}")
            
            # Run pipeline
            results = pipeline.run()
            
            self.log_info(f"Pipeline completed", 
                         pipeline=pipeline_name,
                         steps_executed=results["steps_executed"],
                         steps_failed=results["steps_failed"])
            
            return results
            
        except Exception as e:
            self.log_error(f"Pipeline execution failed", 
                          pipeline=pipeline_name, 
                          error=e)
            raise
    
    def list_pipelines(self) -> List[str]:
        """List available pipeline configurations."""
        config_dir = Path(self.config_loader.config_dir)
        pipelines = []
        
        for config_file in config_dir.glob("*.yml"):
            pipeline_name = config_file.stem
            pipelines.append(pipeline_name)
        
        return pipelines


def main():
    """Main entry point for pipeline runner."""
    parser = argparse.ArgumentParser(description="Run data pipelines from YAML configuration")
    parser.add_argument(
        "pipeline",
        nargs="?",
        help="Name of the pipeline to run (e.g., claims_pipeline)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available pipelines"
    )
    parser.add_argument(
        "--config-dir",
        default="pipelines_config",
        help="Directory containing pipeline configurations (default: pipelines_config)"
    )
    parser.add_argument(
        "--run-id",
        help="Optional run ID for this execution"
    )
    parser.add_argument(
        "--db-path",
        default="warehouse.db",
        help="Path to SQLite database (default: warehouse.db)"
    )
    
    args = parser.parse_args()
    
    runner = PipelineRunner(config_dir=args.config_dir)
    
    if args.list:
        pipelines = runner.list_pipelines()
        print("Available pipelines:")
        for pipeline in pipelines:
            print(f"  - {pipeline}")
        return 0
    
    if not args.pipeline:
        print("Error: Pipeline name required. Use --list to see available pipelines.")
        parser.print_help()
        return 1
    
    try:
        results = runner.run_pipeline(args.pipeline, run_id=args.run_id, db_path=args.db_path)
        
        # Print summary
        print("\n" + "="*50)
        print(f"Pipeline: {results['pipeline_name']}")
        print(f"Run ID: {results['run_id']}")
        print(f"Steps Executed: {results['steps_executed']}")
        print(f"Steps Failed: {results['steps_failed']}")
        print(f"Steps Skipped: {results['steps_skipped']}")
        print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

