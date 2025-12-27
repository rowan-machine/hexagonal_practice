"""
Base pipeline class providing centralized execution logic.

All pipelines inherit from BasePipeline and define their steps through configuration.

This module provides:
- BasePipeline: Abstract base class for all pipelines
- PipelineStep: Abstract base class for pipeline steps
- ExecutionContext: Context object passed through pipeline execution
- PipelineConfig: Configuration object for pipeline setup

Example:
    ```python
    from src.pipelines.base import BasePipeline, PipelineConfig, ExecutionContext
    from src.pipelines.claims_pipeline import ClaimsPipeline
    
    config = PipelineConfig(
        steps=[...],
        context=ExecutionContext(pipeline_name="my_pipeline", run_id="123")
    )
    pipeline = ClaimsPipeline(config)
    results = pipeline.run()
    ```
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class StepStatus(Enum):
    """Status of a pipeline step execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionContext:
    """Context passed through pipeline execution."""
    pipeline_name: str
    run_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from metadata."""
        return self.metadata.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in metadata."""
        self.metadata[key] = value


class PipelineStep(ABC):
    """
    Abstract base class for all pipeline steps.
    
    All pipeline steps must inherit from this class and implement the execute method.
    Steps can optionally override before_execute, after_execute, and on_error hooks.
    
    Attributes:
        name: Unique name for this step
        status: Current execution status (PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
    
    Example:
        ```python
        class MyStep(PipelineStep):
            def execute(self, context: ExecutionContext) -> Dict[str, Any]:
                # Step logic here
                return {"result": "data"}
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize a pipeline step.
        
        Args:
            name: Unique name for this step (used in logging and error messages)
        """
        self.name = name
        self.status = StepStatus.PENDING
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> Any:
        """
        Execute the step logic.
        
        This method must be implemented by all concrete step classes.
        It should perform the step's work and return a result.
        
        Args:
            context: Execution context containing pipeline state and metadata.
                    Use context.get() and context.set() to access/modify state.
            
        Returns:
            Result of step execution. Can be any type (dict, list, object, etc.).
            The result is stored in the pipeline execution summary.
        
        Raises:
            Exception: Any exception raised will be caught and handled by the pipeline.
                     If stop_on_error is True, pipeline execution will stop.
        """
        pass
    
    def before_execute(self, context: ExecutionContext) -> None:
        """Hook called before step execution."""
        self.status = StepStatus.RUNNING
    
    def after_execute(self, context: ExecutionContext, result: Any) -> None:
        """Hook called after successful step execution."""
        self.status = StepStatus.COMPLETED
    
    def on_error(self, context: ExecutionContext, error: Exception) -> None:
        """
        Hook called when step execution fails.
        
        Sets the step status to FAILED. Does NOT re-raise the error.
        The pipeline's run() method handles whether to continue or stop based on stop_on_error.
        """
        self.status = StepStatus.FAILED
        # Don't raise here - let the pipeline decide whether to continue


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    steps: List[PipelineStep]
    context: ExecutionContext
    stop_on_error: bool = True
    skip_completed: bool = False


class BasePipeline(ABC):
    """
    Base class for all pipelines.
    
    Provides centralized execution logic, step management, and lifecycle hooks.
    Individual pipelines define their steps through configuration.
    
    This class handles:
    - Step execution order
    - Error handling and recovery
    - Execution logging
    - Lifecycle hooks (before_run, after_run, on_error)
    
    Attributes:
        config: Pipeline configuration
        steps: List of pipeline steps to execute
        context: Execution context passed to all steps
        execution_log: List of execution log entries
    
    Example:
        ```python
        class MyPipeline(BasePipeline):
            def before_run(self):
                # Setup logic
                pass
            
            def after_run(self, summary):
                # Cleanup logic
                pass
        ```
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.steps = config.steps
        self.context = config.context
        self.execution_log: List[Dict[str, Any]] = []
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the pipeline.
        
        Returns:
            Execution summary with status and results
        """
        try:
            self.before_run()
            
            results = {}
            for step in self.steps:
                if self._should_skip_step(step):
                    step.status = StepStatus.SKIPPED
                    continue
                
                try:
                    step.before_execute(self.context)
                    result = step.execute(self.context)
                    step.after_execute(self.context, result)
                    
                    results[step.name] = result
                    self._log_step_execution(step, result, None)
                    
                except Exception as e:
                    step.on_error(self.context, e)
                    self._log_step_execution(step, None, e)
                    
                    if self.config.stop_on_error:
                        raise
                    # If stop_on_error is False, continue to next step
                    
            summary = self._build_summary(results)
            self.after_run(summary)
            return summary
            
        except Exception as e:
            self.on_error(e)
            raise
    
    def _should_skip_step(self, step: PipelineStep) -> bool:
        """Determine if a step should be skipped."""
        if not self.config.skip_completed:
            return False
        return step.status == StepStatus.COMPLETED
    
    def _log_step_execution(self, step: PipelineStep, result: Any, error: Optional[Exception]) -> None:
        """Log step execution details."""
        log_entry = {
            "step_name": step.name,
            "status": step.status.value,
            "error": str(error) if error else None,
        }
        self.execution_log.append(log_entry)
    
    def _build_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build execution summary."""
        return {
            "pipeline_name": self.context.pipeline_name,
            "run_id": self.context.run_id,
            "steps_executed": len([s for s in self.steps if s.status == StepStatus.COMPLETED]),
            "steps_failed": len([s for s in self.steps if s.status == StepStatus.FAILED]),
            "steps_skipped": len([s for s in self.steps if s.status == StepStatus.SKIPPED]),
            "execution_log": self.execution_log,
            "results": results,
        }
    
    def before_run(self) -> None:
        """Hook called before pipeline execution."""
        pass
    
    def after_run(self, summary: Dict[str, Any]) -> None:
        """Hook called after successful pipeline execution."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Hook called when pipeline execution fails."""
        pass
    
    def get_step(self, name: str) -> Optional[PipelineStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

