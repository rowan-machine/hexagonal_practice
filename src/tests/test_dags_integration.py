"""
Integration Tests for DAG Task Interactions.

Tests how tasks interact, ensuring data flows correctly and dependencies are met.

Note: These tests require Apache Airflow to be installed.
Install with: pip install apache-airflow==2.10.3
Or run tests in Docker where Airflow is available.
"""
import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Try to import Airflow, skip tests if not available
try:
    from airflow.models import DagBag, Variable
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


class TestDAGTaskIntegration:
    """Integration tests for DAG task interactions."""
    
    @pytest.fixture
    def dag_bag(self):
        """Create DagBag instance."""
        dag_folder = Path(__file__).parent.parent.parent / "airflow" / "dags"
        from airflow.models import DagBag
        return DagBag(dag_folder=str(dag_folder), include_examples=False)
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_claims_pipeline_task_dependencies(self, dag_bag):
        """Test that claims_pipeline task has correct dependencies."""
        dag = dag_bag.get_dag(dag_id='claims_pipeline')
        task = dag.get_task('run_claims_pipeline')
        
        # Single task DAG should have no upstream dependencies
        assert len(task.upstream_task_ids) == 0, "Claims pipeline task should have no upstream dependencies"
        assert len(task.downstream_task_ids) == 0, "Claims pipeline task should have no downstream dependencies"
    
    def test_policies_pipeline_task_dependencies(self, dag_bag):
        """Test that policies_pipeline task has correct dependencies."""
        dag = dag_bag.get_dag(dag_id='policies_pipeline')
        task = dag.get_task('run_policies_pipeline')
        
        # Single task DAG should have no upstream dependencies
        assert len(task.upstream_task_ids) == 0, "Policies pipeline task should have no upstream dependencies"
        assert len(task.downstream_task_ids) == 0, "Policies pipeline task should have no downstream dependencies"
    
    def test_claims_pipeline_task_execution_flow(self, dag_bag, temp_db):
        """Test that claims_pipeline task executes correctly with real components."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        # Use real ConfigLoader and Pipeline (with mocked Atlas)
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            # This should work with real components
            result = run_claims_pipeline(**context)
            
            assert result['status'] == 'success'
            assert result['steps_executed'] > 0
    
    def test_policies_pipeline_task_execution_flow(self, dag_bag, temp_db):
        """Test that policies_pipeline task executes correctly with real components."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import run_policies_pipeline
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            result = run_policies_pipeline(**context)
            
            assert result['status'] == 'success'
            assert result['steps_executed'] > 0
    
    def test_backfill_task_uses_execution_date(self, dag_bag):
        """Test that backfill tasks use execution_date correctly."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_backfill_dag import run_claims_backfill
        
        execution_date = datetime(2024, 1, 15, 10, 30, 0)
        context = {
            'execution_date': execution_date,
            'ds': '2024-01-15',
            'dag_run': Mock(conf={}),
        }
        
        with patch('claims_backfill_dag.ConfigLoader') as mock_loader, \
             patch('claims_backfill_dag.ClaimsPipeline') as mock_pipeline, \
             patch('claims_backfill_dag.Variable') as mock_variable:
            
            mock_variable.get.return_value = 'warehouse.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_claims_backfill(**context)
            
            # Verify execution_date is used in run_id
            assert execution_date.strftime('%Y%m%d') in result['run_id']
            assert result['execution_date'] == execution_date.isoformat()
    
    def test_task_parameter_propagation(self, dag_bag):
        """Test that parameters propagate correctly through task execution."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        
        custom_db_path = '/test/path.db'
        custom_run_id = 'test-run-123'
        
        mock_dag_run = Mock()
        mock_dag_run.conf = {
            'db_path': custom_db_path,
            'run_id': custom_run_id,
        }
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': mock_dag_run,
        }
        
        with patch('claims_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('claims_pipeline_dag.ClaimsPipeline') as mock_pipeline, \
             patch('claims_pipeline_dag.Variable') as mock_variable:
            
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_claims_pipeline(**context)
            
            # Verify parameters were used
            call_kwargs = mock_loader.return_value.create_pipeline_config.call_args[1]
            assert call_kwargs['db_path'] == custom_db_path
            assert call_kwargs['run_id'] == custom_run_id


class TestDAGVariableIntegration:
    """Test DAG integration with Airflow Variables."""
    
    def test_claims_pipeline_uses_airflow_variable(self):
        """Test that claims_pipeline uses Airflow Variable for db_path."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        from airflow.models import Variable
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': Mock(conf={}),  # No conf, should use Variable
        }
        
        with patch('claims_pipeline_dag.Variable') as mock_variable, \
             patch('claims_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('claims_pipeline_dag.ClaimsPipeline') as mock_pipeline:
            
            mock_variable.get.return_value = 'variable-db-path.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_claims_pipeline(**context)
            
            # Verify Variable.get was called
            mock_variable.get.assert_called_once_with('WAREHOUSE_DB_PATH', default_var='warehouse.db')
            
            # Verify the variable value was used
            call_kwargs = mock_loader.return_value.create_pipeline_config.call_args[1]
            assert call_kwargs['db_path'] == 'variable-db-path.db'
    
    def test_policies_pipeline_uses_airflow_variable(self):
        """Test that policies_pipeline uses Airflow Variable for db_path."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import run_policies_pipeline
        from airflow.models import Variable
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': Mock(conf={}),
        }
        
        with patch('policies_pipeline_dag.Variable') as mock_variable, \
             patch('policies_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('policies_pipeline_dag.PoliciesPipeline') as mock_pipeline:
            
            mock_variable.get.return_value = 'variable-db-path.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_policies_pipeline(**context)
            
            mock_variable.get.assert_called_once_with('WAREHOUSE_DB_PATH', default_var='warehouse.db')
            
            call_kwargs = mock_loader.return_value.create_pipeline_config.call_args[1]
            assert call_kwargs['db_path'] == 'variable-db-path.db'

