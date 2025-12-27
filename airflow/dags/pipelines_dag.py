"""
Simple Airflow DAG for running data pipelines.

This DAG demonstrates the recommended pattern:
- Very simple Python functions that wrap pipeline execution
- PythonOperator with minimal code
- All business logic is in the pipeline classes, not in the DAG
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline, PoliciesPipeline


# Default arguments for the DAG
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_claims_pipeline():
    """
    Simple wrapper function to run claims pipeline.
    
    All business logic is in ClaimsPipeline, not here.
    """
    config_loader = ConfigLoader(config_dir="config")
    pipeline_config = config_loader.create_pipeline_config("claims_pipeline")
    pipeline = ClaimsPipeline(pipeline_config)
    pipeline.run()


def run_policies_pipeline():
    """
    Simple wrapper function to run policies pipeline.
    
    All business logic is in PoliciesPipeline, not here.
    """
    config_loader = ConfigLoader(config_dir="config")
    pipeline_config = config_loader.create_pipeline_config("policies_pipeline")
    pipeline = PoliciesPipeline(pipeline_config)
    pipeline.run()


# Create the DAG
dag = DAG(
    'stop_loss_pipelines',
    default_args=default_args,
    description='Stop loss insurance data pipelines',
    schedule_interval=timedelta(hours=1),  # Run hourly
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['stop-loss', 'insurance', 'data-pipelines'],
)


# Claims pipeline task
claims_task = PythonOperator(
    task_id='run_claims_pipeline',
    python_callable=run_claims_pipeline,
    dag=dag,
)


# Policies pipeline task
policies_task = PythonOperator(
    task_id='run_policies_pipeline',
    python_callable=run_policies_pipeline,
    dag=dag,
)


# Set task dependencies (if needed)
# policies_task >> claims_task  # Uncomment if policies must run before claims

