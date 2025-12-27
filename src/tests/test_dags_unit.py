"""
Unit Tests for DAG Components.

Tests individual DAG components in isolation using mocking.

Note: These tests require Apache Airflow to be installed.
Install with: pip install apache-airflow==2.10.3
Or run tests in Docker where Airflow is available.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Try to import Airflow, skip tests if not available
try:
    from airflow.models import Variable
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


class TestClaimsPipelineDAGUnit:
    """Unit tests for claims pipeline DAG components."""
    
    def test_run_claims_pipeline_function_signature(self):
        """Test that run_claims_pipeline function accepts context."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        
        # Create mock context
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={}),
        }
        
        # Mock dependencies
        with patch('claims_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('claims_pipeline_dag.ClaimsPipeline') as mock_pipeline, \
             patch('claims_pipeline_dag.Variable') as mock_variable:
            
            # Setup mocks
            mock_variable.get.return_value = 'warehouse.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {
                'steps_executed': 4,
                'steps_failed': 0,
            }
            mock_pipeline.return_value = mock_pipeline_instance
            
            # Call function
            result = run_claims_pipeline(**context)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert 'status' in result
            assert 'run_id' in result
            assert 'execution_date' in result
            assert 'steps_executed' in result
            assert 'steps_failed' in result
            assert result['status'] == 'success'
            assert result['steps_executed'] == 4
            assert result['steps_failed'] == 0
    
    def test_run_claims_pipeline_with_custom_params(self):
        """Test run_claims_pipeline with custom parameters."""
        from airflow.dags.claims_pipeline_dag import run_claims_pipeline
        
        # Create mock context with custom parameters
        mock_dag_run = Mock()
        mock_dag_run.conf = {
            'db_path': '/custom/path.db',
            'run_id': 'custom-run-123',
        }
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
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
            
            # Verify custom parameters were used
            mock_loader.return_value.create_pipeline_config.assert_called_once()
            call_args = mock_loader.return_value.create_pipeline_config.call_args
            assert call_args[1]['db_path'] == '/custom/path.db'
            assert call_args[1]['run_id'] == 'custom-run-123'
    
    def test_run_claims_pipeline_handles_missing_dag_run(self):
        """Test run_claims_pipeline handles missing dag_run gracefully."""
        from airflow.dags.claims_pipeline_dag import run_claims_pipeline
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': None,  # Missing dag_run
        }
        
        with patch('claims_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('claims_pipeline_dag.ClaimsPipeline') as mock_pipeline, \
             patch('claims_pipeline_dag.Variable') as mock_variable:
            
            mock_variable.get.return_value = 'warehouse.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            # Should not raise an error
            result = run_claims_pipeline(**context)
            assert result['status'] == 'success'


class TestPoliciesPipelineDAGUnit:
    """Unit tests for policies pipeline DAG components."""
    
    def test_run_policies_pipeline_function_signature(self):
        """Test that run_policies_pipeline function accepts context."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import run_policies_pipeline
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={}),
        }
        
        with patch('policies_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('policies_pipeline_dag.PoliciesPipeline') as mock_pipeline, \
             patch('policies_pipeline_dag.Variable') as mock_variable:
            
            mock_variable.get.return_value = 'warehouse.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {
                'steps_executed': 4,
                'steps_failed': 0,
            }
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_policies_pipeline(**context)
            
            assert isinstance(result, dict)
            assert result['status'] == 'success'
            assert result['steps_executed'] == 4
    
    def test_run_policies_pipeline_with_custom_params(self):
        """Test run_policies_pipeline with custom parameters."""
        from airflow.dags.policies_pipeline_dag import run_policies_pipeline
        
        mock_dag_run = Mock()
        mock_dag_run.conf = {
            'db_path': '/custom/path.db',
            'run_id': 'custom-run-456',
        }
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': mock_dag_run,
        }
        
        with patch('policies_pipeline_dag.ConfigLoader') as mock_loader, \
             patch('policies_pipeline_dag.PoliciesPipeline') as mock_pipeline, \
             patch('policies_pipeline_dag.Variable') as mock_variable:
            
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_policies_pipeline(**context)
            
            call_args = mock_loader.return_value.create_pipeline_config.call_args
            assert call_args[1]['db_path'] == '/custom/path.db'
            assert call_args[1]['run_id'] == 'custom-run-456'


class TestBackfillDAGUnit:
    """Unit tests for backfill DAG components."""
    
    def test_run_claims_backfill_function(self):
        """Test run_claims_backfill function."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_backfill_dag import run_claims_backfill
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
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
            
            assert result['status'] == 'success'
            assert 'backfill' in result['run_id'] or 'claims' in result['run_id']
    
    def test_run_policies_backfill_function(self):
        """Test run_policies_backfill function."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_backfill_dag import run_policies_backfill
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={}),
        }
        
        with patch('policies_backfill_dag.ConfigLoader') as mock_loader, \
             patch('policies_backfill_dag.PoliciesPipeline') as mock_pipeline, \
             patch('policies_backfill_dag.Variable') as mock_variable:
            
            mock_variable.get.return_value = 'warehouse.db'
            mock_config = Mock()
            mock_loader.return_value.create_pipeline_config.return_value = mock_config
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.run.return_value = {'steps_executed': 4, 'steps_failed': 0}
            mock_pipeline.return_value = mock_pipeline_instance
            
            result = run_policies_backfill(**context)
            
            assert result['status'] == 'success'
            assert 'backfill' in result['run_id'] or 'policies' in result['run_id']


class TestDAGDefaultArgs:
    """Test DAG default arguments."""
    
    def test_claims_pipeline_default_args(self):
        """Test claims_pipeline default arguments."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import default_args
        
        assert default_args['owner'] == 'data-engineering'
        assert default_args['depends_on_past'] is False
        assert default_args['email_on_failure'] is False
        assert default_args['retries'] == 1
    
    def test_policies_pipeline_default_args(self):
        """Test policies_pipeline default arguments."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import default_args
        
        assert default_args['owner'] == 'data-engineering'
        assert default_args['depends_on_past'] is False
        assert default_args['email_on_failure'] is False
        assert default_args['retries'] == 1
    
    def test_backfill_default_args(self):
        """Test backfill DAG default arguments."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_backfill_dag import default_args
        
        assert default_args['owner'] == 'data-engineering'
        assert default_args['depends_on_past'] is False
        assert default_args['retries'] == 1

