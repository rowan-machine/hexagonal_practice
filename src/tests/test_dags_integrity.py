"""
DAG Integrity and Structure Tests.

Tests basic sanity checks using DagBag to catch:
- Missing dag_ids
- Wrong tags
- Import errors
- DAG structure issues

Note: These tests require Apache Airflow to be installed.
Install with: pip install apache-airflow==2.10.3
Or run tests in Docker where Airflow is available.
"""
import pytest
import sys
from pathlib import Path

# Try to import Airflow, skip tests if not available
try:
    from airflow.models import DagBag
    from airflow.utils.dag_cycle import check_cycle
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Apache Airflow not installed. Install with: pip install apache-airflow==2.10.3")


# Add project root to path if package not installed
try:
    pass
except ImportError:
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


class TestDAGIntegrity:
    """Test DAG integrity and structure."""
    
    @pytest.fixture
    def dag_bag(self):
        """Create DagBag instance for testing."""
        dag_folder = Path(__file__).parent.parent.parent / "airflow" / "dags"
        return DagBag(dag_folder=str(dag_folder), include_examples=False)
    
    def test_dag_bag_loads_without_errors(self, dag_bag):
        """Test that all DAGs load without import errors."""
        assert len(dag_bag.import_errors) == 0, f"DAG import errors: {dag_bag.import_errors}"
    
    def test_dag_ids_are_unique(self, dag_bag):
        """Test that all DAG IDs are unique."""
        dag_ids = list(dag_bag.dag_ids)
        assert len(dag_ids) == len(set(dag_ids)), f"Duplicate DAG IDs found: {dag_ids}"
    
    def test_claims_pipeline_dag_exists(self, dag_bag):
        """Test that claims_pipeline DAG exists."""
        assert 'claims_pipeline' in dag_bag.dag_ids, "claims_pipeline DAG not found"
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        assert dag is not None, "claims_pipeline DAG is None"
    
    def test_policies_pipeline_dag_exists(self, dag_bag):
        """Test that policies_pipeline DAG exists."""
        assert 'policies_pipeline' in dag_bag.dag_ids, "policies_pipeline DAG not found"
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        assert dag is not None, "policies_pipeline DAG is None"
    
    def test_claims_backfill_dag_exists(self, dag_bag):
        """Test that claims_backfill DAG exists."""
        assert 'claims_backfill' in dag_bag.dag_ids, "claims_backfill DAG not found"
        dag = dag_bag.get_dag(dag_id='claims_backfill')
        assert dag is not None, "claims_backfill DAG is None"
    
    def test_policies_backfill_dag_exists(self, dag_bag):
        """Test that policies_backfill DAG exists."""
        assert 'policies_backfill' in dag_bag.dag_ids, "policies_backfill DAG not found"
        dag = dag_bag.get_dag(dag_id='policies_backfill')
        assert dag is not None, "policies_backfill DAG is None"
    
    def test_no_dag_cycles(self, dag_bag):
        """Test that DAGs have no cycles."""
        for dag_id in dag_bag.dag_ids:
            dag = dag_bag.get_dag(dag_id=dag_id)
            check_cycle(dag)
    
    def test_claims_pipeline_has_correct_tags(self, dag_bag):
        """Test that claims_pipeline has correct tags."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        expected_tags = {'stop-loss', 'insurance', 'claims', 'data-pipelines'}
        assert set(dag.tags) == expected_tags, f"Expected tags {expected_tags}, got {dag.tags}"
    
    def test_policies_pipeline_has_correct_tags(self, dag_bag):
        """Test that policies_pipeline has correct tags."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        expected_tags = {'stop-loss', 'insurance', 'policies', 'data-pipelines'}
        assert set(dag.tags) == expected_tags, f"Expected tags {expected_tags}, got {dag.tags}"
    
    def test_claims_backfill_has_correct_tags(self, dag_bag):
        """Test that claims_backfill has correct tags."""
        dag = dag_bag.get_dag(dag_id='claims_backfill')
        expected_tags = {'stop-loss', 'insurance', 'claims', 'backfill', 'data-pipelines'}
        assert set(dag.tags) == expected_tags, f"Expected tags {expected_tags}, got {dag.tags}"
    
    def test_policies_backfill_has_correct_tags(self, dag_bag):
        """Test that policies_backfill has correct tags."""
        dag = dag_bag.get_dag(dag_id='policies_backfill')
        expected_tags = {'stop-loss', 'insurance', 'policies', 'backfill', 'data-pipelines'}
        assert set(dag.tags) == expected_tags, f"Expected tags {expected_tags}, got {dag.tags}"
    
    def test_claims_pipeline_has_correct_schedule(self, dag_bag):
        """Test that claims_pipeline has correct schedule."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        from datetime import timedelta
        assert dag.schedule_interval == timedelta(hours=1), f"Expected hourly schedule, got {dag.schedule_interval}"
    
    def test_policies_pipeline_has_correct_schedule(self, dag_bag):
        """Test that policies_pipeline has correct schedule."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        from datetime import timedelta
        assert dag.schedule_interval == timedelta(hours=1), f"Expected hourly schedule, got {dag.schedule_interval}"
    
    def test_backfill_dags_have_no_schedule(self, dag_bag):
        """Test that backfill DAGs have no schedule (manual trigger only)."""
        for dag_id in ['claims_backfill', 'policies_backfill']:
            dag = dag_bag.get_dag(dag_id=dag_id)
            assert dag.schedule_interval is None, f"{dag_id} should have no schedule (None), got {dag.schedule_interval}"
    
    def test_claims_pipeline_has_correct_owner(self, dag_bag):
        """Test that claims_pipeline has correct owner."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        assert dag.owner == 'data-engineering', f"Expected owner 'data-engineering', got '{dag.owner}'"
    
    def test_policies_pipeline_has_correct_owner(self, dag_bag):
        """Test that policies_pipeline has correct owner."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        assert dag.owner == 'data-engineering', f"Expected owner 'data-engineering', got '{dag.owner}'"
    
    def test_claims_pipeline_has_correct_max_active_runs(self, dag_bag):
        """Test that claims_pipeline has correct max_active_runs."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        assert dag.max_active_runs == 1, f"Expected max_active_runs=1, got {dag.max_active_runs}"
    
    def test_policies_pipeline_has_correct_max_active_runs(self, dag_bag):
        """Test that policies_pipeline has correct max_active_runs."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        assert dag.max_active_runs == 1, f"Expected max_active_runs=1, got {dag.max_active_runs}"
    
    def test_claims_pipeline_has_correct_task(self, dag_bag):
        """Test that claims_pipeline has correct task."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        task_ids = [task.task_id for task in dag.tasks]
        assert 'run_claims_pipeline' in task_ids, f"Expected task 'run_claims_pipeline', got {task_ids}"
    
    def test_policies_pipeline_has_correct_task(self, dag_bag):
        """Test that policies_pipeline has correct task."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        task_ids = [task.task_id for task in dag.tasks]
        assert 'run_policies_pipeline' in task_ids, f"Expected task 'run_policies_pipeline', got {task_ids}"
    
    def test_backfill_dags_have_correct_tasks(self, dag_bag):
        """Test that backfill DAGs have correct tasks."""
        claims_backfill = dag_bag.get_dag(dag_id='claims_backfill')
        policies_backfill = dag_bag.get_dag(dag_id='policies_backfill')
        
        claims_task_ids = [task.task_id for task in claims_backfill.tasks]
        policies_task_ids = [task.task_id for task in policies_backfill.tasks]
        
        assert 'run_claims_backfill' in claims_task_ids, f"Expected task 'run_claims_backfill', got {claims_task_ids}"
        assert 'run_policies_backfill' in policies_task_ids, f"Expected task 'run_policies_backfill', got {policies_task_ids}"

