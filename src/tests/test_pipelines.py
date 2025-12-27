"""
Unit tests for pipeline orchestration.

Tests pipeline execution logic and step coordination.
"""
import pytest
from uuid import uuid4
from src.pipelines import BasePipeline, PipelineConfig, ExecutionContext, PipelineStep
from src.pipelines.base import StepStatus


class MockStep(PipelineStep):
    """Mock step for testing."""
    
    def __init__(self, name: str, should_fail: bool = False, return_value: any = None):
        super().__init__(name)
        self.should_fail = should_fail
        self.return_value = return_value
    
    def execute(self, context: ExecutionContext) -> any:
        """Execute mock step."""
        if self.should_fail:
            raise ValueError(f"Step {self.name} failed")
        return self.return_value or {"step": self.name}


class MockPipeline(BasePipeline):
    """Mock pipeline implementation for testing."""
    
    def before_run(self) -> None:
        """Hook before run."""
        self.context.set("before_run_called", True)
    
    def after_run(self, summary: dict) -> None:
        """Hook after run."""
        self.context.set("after_run_called", True)
        self.context.set("summary", summary)


class TestPipelineExecution:
    """Tests for pipeline execution."""
    
    def test_pipeline_runs_steps(self):
        """Test that pipeline executes all steps."""
        steps = [
            MockStep("step1"),
            MockStep("step2"),
            MockStep("step3")
        ]
        config = PipelineConfig(
            steps=steps,
            context=ExecutionContext(pipeline_name="test", run_id=str(uuid4()))
        )
        pipeline = MockPipeline(config)
        results = pipeline.run()
        
        assert results["steps_executed"] == 3
        assert results["steps_failed"] == 0
        assert all(step.status == StepStatus.COMPLETED for step in steps)
    
    def test_pipeline_stops_on_error(self):
        """Test that pipeline stops on error when configured."""
        steps = [
            MockStep("step1"),
            MockStep("step2", should_fail=True),
            MockStep("step3")
        ]
        config = PipelineConfig(
            steps=steps,
            context=ExecutionContext(pipeline_name="test", run_id=str(uuid4())),
            stop_on_error=True
        )
        pipeline = MockPipeline(config)
        
        with pytest.raises(ValueError):
            pipeline.run()
        
        assert steps[0].status == StepStatus.COMPLETED
        assert steps[1].status == StepStatus.FAILED
        assert steps[2].status == StepStatus.PENDING
    
    def test_pipeline_continues_on_error(self):
        """Test that pipeline continues on error when configured."""
        steps = [
            MockStep("step1"),
            MockStep("step2", should_fail=True),
            MockStep("step3")
        ]
        config = PipelineConfig(
            steps=steps,
            context=ExecutionContext(pipeline_name="test", run_id=str(uuid4())),
            stop_on_error=False
        )
        pipeline = MockPipeline(config)
        results = pipeline.run()
        
        assert results["steps_executed"] == 2  # step1 and step3
        assert results["steps_failed"] == 1  # step2
        assert steps[2].status == StepStatus.COMPLETED
    
    def test_pipeline_lifecycle_hooks(self):
        """Test that lifecycle hooks are called."""
        steps = [MockStep("step1")]
        context = ExecutionContext(pipeline_name="test", run_id=str(uuid4()))
        config = PipelineConfig(steps=steps, context=context)
        pipeline = MockPipeline(config)
        pipeline.run()
        
        assert context.get("before_run_called") is True
        assert context.get("after_run_called") is True
        assert context.get("summary") is not None
    
    def test_get_step(self):
        """Test getting a step by name."""
        steps = [
            MockStep("step1"),
            MockStep("step2"),
            MockStep("step3")
        ]
        config = PipelineConfig(
            steps=steps,
            context=ExecutionContext(pipeline_name="test", run_id=str(uuid4()))
        )
        pipeline = MockPipeline(config)
        
        step = pipeline.get_step("step2")
        assert step is not None
        assert step.name == "step2"
        
        step = pipeline.get_step("nonexistent")
        assert step is None

