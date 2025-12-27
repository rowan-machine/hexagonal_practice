# Airflow DAGs

Simple Airflow DAGs for running data pipelines.

## Pattern

All DAGs follow this simple pattern:

```python
def run_pipeline():
    """Simple wrapper - all logic in pipeline class."""
    config_loader = ConfigLoader()
    pipeline_config = config_loader.create_pipeline_config("pipeline_name")
    pipeline = PipelineClass(pipeline_config)
    pipeline.run()

PythonOperator(
    task_id="run_pipeline",
    python_callable=run_pipeline,
)
```

## Principles

1. **Keep DAGs Simple**: DAGs should only orchestrate, not contain business logic
2. **All Logic in Pipelines**: Business rules, transformations, and processing live in pipeline classes
3. **Configuration-Driven**: Pipelines are configured via YAML, not hardcoded in DAGs
4. **Testable**: Pipeline logic can be tested independently of Airflow

## DAGs

- `pipelines_dag.py`: Main DAG for claims and policies pipelines

## Usage

1. Copy DAGs to your Airflow `dags/` directory
2. Ensure the `src/` package is available to Airflow (via PYTHONPATH or package installation)
3. DAGs will appear in Airflow UI automatically

