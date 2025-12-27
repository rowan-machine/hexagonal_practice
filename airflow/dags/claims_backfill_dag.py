"""
Backfill DAG for claims pipeline.

Use this DAG to backfill historical claims data.
Supports parameterized date ranges and execution dates.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from typing import Dict, Any

from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline


# Default arguments for backfill
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_claims_backfill(**context) -> Dict[str, Any]:
    """
    Run claims pipeline for backfill.
    
    This function uses the execution_date from Airflow context for backfilling.
    Parameters can be passed via DAG run config:
    - db_path: Custom database path
    - run_id: Custom run ID
    """
    # Get execution date from context (Airflow provides this for backfill)
    execution_date = context.get('execution_date') or context.get('ds') or datetime.now()
    if isinstance(execution_date, str):
        execution_date = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
    
    # Get DAG run config parameters
    dag_run = context.get('dag_run')
    conf = dag_run.conf if dag_run else {}
    
    db_path = conf.get('db_path', Variable.get('WAREHOUSE_DB_PATH', default_var='warehouse.db'))
    run_id = conf.get('run_id') or f"claims_backfill_{execution_date.strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Running claims backfill for date: {execution_date}")
    print(f"Run ID: {run_id}")
    print(f"Database path: {db_path}")
    
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


# Create backfill DAG
# Note: catchup=True enables automatic backfill for missed runs
dag = DAG(
    'claims_backfill',
    default_args=default_args,
    description='Backfill DAG for claims pipeline - processes historical data',
    schedule_interval=None,  # Manual trigger only for backfill
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Set to True to automatically backfill from start_date
    max_active_runs=1,
    tags=['stop-loss', 'insurance', 'claims', 'backfill', 'data-pipelines'],
    params={
        'db_path': 'warehouse.db',
        'run_id': None,  # Auto-generated if not provided
        'start_date': None,  # Start date for backfill range
        'end_date': None,  # End date for backfill range
    },
)


# Backfill task
backfill_task = PythonOperator(
    task_id='run_claims_backfill',
    python_callable=run_claims_backfill,
    dag=dag,
)

