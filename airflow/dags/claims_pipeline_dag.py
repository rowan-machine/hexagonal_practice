"""
Parameterized Airflow DAG for claims pipeline.

Supports:
- Scheduled runs
- Manual triggers with parameters
- Backfill operations
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from typing import Dict, Any

from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline


# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_claims_pipeline(**context) -> Dict[str, Any]:
    """
    Run claims pipeline with optional parameters.
    
    Parameters can be passed via Airflow UI or DAG run config:
    - execution_date: Override execution date (for backfill)
    - db_path: Custom database path
    - run_id: Custom run ID
    """
    # Get parameters from context or use defaults
    execution_date = context.get('execution_date') or context.get('ds') or datetime.now()
    if isinstance(execution_date, str):
        execution_date = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
    
    # Get DAG run config parameters
    dag_run = context.get('dag_run')
    conf = dag_run.conf if dag_run else {}
    
    db_path = conf.get('db_path', Variable.get('WAREHOUSE_DB_PATH', default_var='warehouse.db'))
    run_id = conf.get('run_id') or f"claims_{execution_date.strftime('%Y%m%d_%H%M%S')}"
    
    # Create pipeline config
    config_loader = ConfigLoader(config_dir="config")
    pipeline_config = config_loader.create_pipeline_config(
        pipeline_name="claims_pipeline",
        run_id=run_id,
        db_path=db_path
    )
    
    # Run pipeline
    pipeline = ClaimsPipeline(pipeline_config)
    results = pipeline.run()
    
    return {
        'status': 'success',
        'run_id': run_id,
        'execution_date': execution_date.isoformat(),
        'steps_executed': results.get('steps_executed', 0),
        'steps_failed': results.get('steps_failed', 0),
    }


# Create the DAG
dag = DAG(
    'claims_pipeline',
    default_args=default_args,
    description='Stop loss insurance claims processing pipeline',
    schedule_interval=timedelta(hours=1),  # Run hourly
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Set to True for backfill
    max_active_runs=1,
    tags=['stop-loss', 'insurance', 'claims', 'data-pipelines'],
    params={
        'db_path': 'warehouse.db',
        'run_id': None,  # Auto-generated if not provided
    },
)


# Claims pipeline task
claims_task = PythonOperator(
    task_id='run_claims_pipeline',
    python_callable=run_claims_pipeline,
    dag=dag,
)

