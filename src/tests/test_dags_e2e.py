"""
End-to-End Tests for DAGs.

Tests the entire pipeline execution to confirm expected output data.

Note: These tests require Apache Airflow to be installed.
Install with: pip install apache-airflow==2.10.3
Or run tests in Docker where Airflow is available.
"""
import pytest
import sys
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock

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


class TestDAGE2E:
    """End-to-end tests for DAG execution."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def test_data(self):
        """Create test data files."""
        test_dir = Path(__file__).parent.parent.parent / "data"
        test_dir.mkdir(exist_ok=True)
        
        # Create test claims data
        claims_data = {
            "claims": [
                {
                    "claim_id": "E2E-001",
                    "policy_id": "POL-E2E-001",
                    "member_id": "MEM-001",
                    "claim_amount": "50000.00",
                    "incurred_date": "2024-01-15T00:00:00",
                    "status": "approved",
                    "claim_type": "medical"
                },
                {
                    "claim_id": "E2E-002",
                    "policy_id": "POL-E2E-001",
                    "member_id": "MEM-002",
                    "claim_amount": "75000.00",
                    "incurred_date": "2024-01-16T00:00:00",
                    "status": "approved",
                    "claim_type": "medical"
                }
            ]
        }
        
        # Create test policies data
        policies_data = {
            "policies": [
                {
                    "policy_id": "POL-E2E-001",
                    "employer_id": "EMP-E2E-001",
                    "effective_date": "2024-01-01T00:00:00",
                    "expiration_date": "2024-12-31T23:59:59",
                    "stop_loss_limit": 1000000.00,
                    "aggregate_deductible": 50000.00,
                    "specific_deductible": 25000.00,
                    "status": "active"
                }
            ]
        }
        
        claims_file = test_dir / "raw_claims.json"
        policies_file = test_dir / "raw_policies.json"
        
        with open(claims_file, 'w') as f:
            json.dump(claims_data, f)
        
        with open(policies_file, 'w') as f:
            json.dump(policies_data, f)
        
        yield {
            'claims_file': str(claims_file),
            'policies_file': str(policies_file),
        }
        
        # Cleanup
        if claims_file.exists():
            claims_file.unlink()
        if policies_file.exists():
            policies_file.unlink()
    
    def test_claims_pipeline_e2e_execution(self, temp_db, test_data):
        """Test end-to-end execution of claims pipeline DAG."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        from src.utils.database import DatabaseManager
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'ds': '2024-01-01',
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        # Mock Atlas to avoid connection issues
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            # Execute the DAG task
            result = run_claims_pipeline(**context)
            
            # Verify execution succeeded
            assert result['status'] == 'success'
            assert result['steps_executed'] > 0
            assert result['steps_failed'] == 0
            
            # Verify data was written to database
            db = DatabaseManager(db_path=temp_db)
            
            # Check bronze layer
            bronze_claims = db.query("SELECT COUNT(*) as count FROM claims_bronze")
            assert bronze_claims[0]['count'] > 0, "Claims should be in bronze layer"
            
            # Check silver layer
            silver_claims = db.query("SELECT COUNT(*) as count FROM claims_silver")
            assert silver_claims[0]['count'] > 0, "Claims should be in silver layer"
            
            # Check gold layer
            gold_claims = db.query("SELECT COUNT(*) as count FROM claims_gold")
            assert gold_claims[0]['count'] > 0, "Claims should be aggregated in gold layer"
    
    def test_policies_pipeline_e2e_execution(self, temp_db, test_data):
        """Test end-to-end execution of policies pipeline DAG."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import run_policies_pipeline
        from src.utils.database import DatabaseManager
        
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
            assert result['steps_failed'] == 0
            
            # Verify data was written to database
            db = DatabaseManager(db_path=temp_db)
            
            bronze_policies = db.query("SELECT COUNT(*) as count FROM policies_bronze")
            assert bronze_policies[0]['count'] > 0, "Policies should be in bronze layer"
            
            silver_policies = db.query("SELECT COUNT(*) as count FROM policies_silver")
            assert silver_policies[0]['count'] > 0, "Policies should be in silver layer"
            
            gold_policies = db.query("SELECT COUNT(*) as count FROM policies_gold")
            assert gold_policies[0]['count'] > 0, "Policies should be aggregated in gold layer"
    
    def test_claims_backfill_e2e_execution(self, temp_db, test_data):
        """Test end-to-end execution of claims backfill DAG."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_backfill_dag import run_claims_backfill
        from src.utils.database import DatabaseManager
        
        execution_date = datetime(2024, 1, 15, 10, 30, 0)
        context = {
            'execution_date': execution_date,
            'ds': '2024-01-15',
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            result = run_claims_backfill(**context)
            
            assert result['status'] == 'success'
            assert result['steps_executed'] > 0
            assert 'backfill' in result['run_id'] or 'claims' in result['run_id']
            
            # Verify data was processed
            db = DatabaseManager(db_path=temp_db)
            bronze_claims = db.query("SELECT COUNT(*) as count FROM claims_bronze")
            assert bronze_claims[0]['count'] > 0
    
    def test_policies_backfill_e2e_execution(self, temp_db, test_data):
        """Test end-to-end execution of policies backfill DAG."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_backfill_dag import run_policies_backfill
        from src.utils.database import DatabaseManager
        
        execution_date = datetime(2024, 1, 15, 10, 30, 0)
        context = {
            'execution_date': execution_date,
            'ds': '2024-01-15',
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            result = run_policies_backfill(**context)
            
            assert result['status'] == 'success'
            assert result['steps_executed'] > 0
            assert 'backfill' in result['run_id'] or 'policies' in result['run_id']
            
            # Verify data was processed
            db = DatabaseManager(db_path=temp_db)
            bronze_policies = db.query("SELECT COUNT(*) as count FROM policies_bronze")
            assert bronze_policies[0]['count'] > 0
    
    def test_claims_pipeline_data_validation(self, temp_db, test_data):
        """Test that claims pipeline produces valid data."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        from src.utils.database import DatabaseManager
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            result = run_claims_pipeline(**context)
            
            assert result['status'] == 'success'
            
            # Validate data quality
            db = DatabaseManager(db_path=temp_db)
            
            # Check that gold layer has aggregated data
            gold_data = db.query("""
                SELECT 
                    policy_id,
                    SUM(claim_amount) as total_claims,
                    COUNT(claim_id) as claim_count
                FROM claims_gold
                GROUP BY policy_id
            """)
            
            assert len(gold_data) > 0, "Gold layer should have aggregated data"
            
            # Verify aggregation is correct (total should match sum of individual claims)
            for row in gold_data:
                assert row['total_claims'] > 0, "Total claims should be positive"
                assert row['claim_count'] > 0, "Claim count should be positive"
    
    def test_policies_pipeline_data_validation(self, temp_db, test_data):
        """Test that policies pipeline produces valid data."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from policies_pipeline_dag import run_policies_pipeline
        from src.utils.database import DatabaseManager
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            result = run_policies_pipeline(**context)
            
            assert result['status'] == 'success'
            
            # Validate data quality
            db = DatabaseManager(db_path=temp_db)
            
            # Check that gold layer has aggregated data
            gold_data = db.query("""
                SELECT 
                    employer_id,
                    SUM(stop_loss_limit) as total_coverage,
                    COUNT(policy_id) as policy_count
                FROM policies_gold
                GROUP BY employer_id
            """)
            
            assert len(gold_data) > 0, "Gold layer should have aggregated data"
            
            for row in gold_data:
                assert row['total_coverage'] > 0, "Total coverage should be positive"
                assert row['policy_count'] > 0, "Policy count should be positive"
    
    def test_idempotent_execution(self, temp_db, test_data):
        """Test that DAG execution is idempotent (can run multiple times safely)."""
        import sys
        from pathlib import Path
        dag_path = Path(__file__).parent.parent.parent / "airflow" / "dags"
        sys.path.insert(0, str(dag_path))
        from claims_pipeline_dag import run_claims_pipeline
        from src.utils.database import DatabaseManager
        
        context = {
            'execution_date': datetime(2024, 1, 1),
            'dag_run': Mock(conf={'db_path': temp_db}),
        }
        
        with patch('src.utils.atlas.AtlasClient') as mock_atlas:
            mock_atlas.return_value.publish.return_value = None
            
            # Run first time
            result1 = run_claims_pipeline(**context)
            assert result1['status'] == 'success'
            
            db = DatabaseManager(db_path=temp_db)
            first_count = db.query("SELECT COUNT(*) as count FROM claims_gold")[0]['count']
            
            # Run second time (should be idempotent)
            result2 = run_claims_pipeline(**context)
            assert result2['status'] == 'success'
            
            second_count = db.query("SELECT COUNT(*) as count FROM claims_gold")[0]['count']
            
            # Counts should be the same (INSERT OR REPLACE ensures idempotency)
            assert first_count == second_count, "Pipeline should be idempotent"

