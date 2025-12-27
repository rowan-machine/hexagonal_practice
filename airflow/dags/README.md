# Airflow DAGs

Simple, parameterized Airflow DAGs for running data pipelines with backfill support.

## DAG Files

### Scheduled DAGs
- **`claims_pipeline_dag.py`**: Claims pipeline (scheduled hourly)
- **`policies_pipeline_dag.py`**: Policies pipeline (scheduled hourly)

### Backfill DAGs
- **`claims_backfill_dag.py`**: Backfill historical claims data
- **`policies_backfill_dag.py`**: Backfill historical policies data

### Legacy DAG
- **`pipelines_dag.py`**: Combined DAG (deprecated - use separate DAGs instead)

## Import Pattern

**Best Practice**: DAGs use direct imports without `sys.path` manipulation.

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline
```

This works because:
1. **Package Installation**: The project is installed in editable mode (`pip install -e /opt/airflow`) in the Docker container
2. **PYTHONPATH**: Set to `/opt/airflow:/opt/airflow/src` in `docker-compose.yml`
3. **Volume Mounts**: Project root is mounted at `/opt/airflow` in the container

**Why not `sys.path` manipulation?**
- ❌ Not Pythonic - violates "explicit is better than implicit"
- ❌ Hard to debug - imports fail silently
- ❌ Not portable - breaks in different environments
- ❌ Violates PEP 8 - imports should be at the top

**Best Practice Alternative:**
- ✅ Install package properly (`pip install -e .`)
- ✅ Use proper PYTHONPATH configuration
- ✅ Direct imports that work everywhere

## Pattern

All DAGs follow this simple pattern:

```python
def run_pipeline(**context):
    """Parameterized wrapper - all logic in pipeline class."""
    # Get parameters from context
    execution_date = context.get('execution_date')
    conf = context.get('dag_run').conf if context.get('dag_run') else {}
    
    # Create and run pipeline
    config_loader = ConfigLoader(config_dir="config")
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
4. **Parameterized**: Support runtime parameters via Airflow UI or DAG run config
5. **Testable**: Pipeline logic can be tested independently of Airflow
6. **Clean Imports**: Use proper package installation, not `sys.path` hacks

## Usage

### Scheduled Runs

DAGs run automatically on their schedule (hourly by default):

1. DAGs appear in Airflow UI automatically
2. They run on schedule without manual intervention
3. Check logs in Airflow UI for execution details

### Manual Trigger with Parameters

Trigger a DAG manually with custom parameters:

1. In Airflow UI, click on the DAG
2. Click "Trigger DAG w/ config"
3. Enter JSON configuration:
   ```json
   {
     "db_path": "/custom/path/warehouse.db",
     "run_id": "manual_run_20240101"
   }
   ```
4. Click "Trigger"

### Backfill Operations

#### Using Airflow CLI

Backfill a date range using Airflow CLI:

```bash
# Backfill claims for a date range
docker-compose exec airflow airflow dags backfill claims_backfill \
  -s 2024-01-01 \
  -e 2024-01-31

# Backfill policies for a date range
docker-compose exec airflow airflow dags backfill policies_backfill \
  -s 2024-01-01 \
  -e 2024-01-31

# Backfill with custom parameters
docker-compose exec airflow airflow dags backfill claims_backfill \
  -s 2024-01-01 \
  -e 2024-01-31 \
  --conf '{"db_path": "/custom/path/warehouse.db"}'
```

#### Using Airflow UI

1. Open the backfill DAG in Airflow UI
2. Click "Trigger DAG w/ config"
3. Enter configuration:
   ```json
   {
     "start_date": "2024-01-01",
     "end_date": "2024-01-31",
     "db_path": "warehouse.db"
   }
   ```
4. Click "Trigger"

#### Enable Automatic Backfill

To automatically backfill missed runs, set `catchup=True` in the DAG:

```python
dag = DAG(
    'claims_backfill',
    catchup=True,  # Enable automatic backfill
    start_date=datetime(2024, 1, 1),
    # ...
)
```

Then trigger the DAG once, and Airflow will create runs for all missed dates.

## Parameters

All DAGs support the following parameters (via DAG run config):

- **`db_path`**: Path to database file (default: `warehouse.db`)
- **`run_id`**: Custom run ID (default: auto-generated from execution date)
- **`start_date`**: Start date for backfill range (backfill DAGs only)
- **`end_date`**: End date for backfill range (backfill DAGs only)

### Example: Parameterized Run

```python
# In Airflow UI, trigger with config:
{
  "db_path": "/opt/airflow/data/warehouse.db",
  "run_id": "custom_run_001"
}
```

## DAG Configuration

### Schedule

Default schedule is hourly. To change:

```python
dag = DAG(
    'claims_pipeline',
    schedule_interval=timedelta(hours=6),  # Every 6 hours
    # or
    schedule_interval='0 0 * * *',  # Daily at midnight (cron)
    # ...
)
```

### Start Date

Set the start date for the DAG:

```python
dag = DAG(
    'claims_pipeline',
    start_date=datetime(2024, 1, 1),
    # ...
)
```

### Catchup

Control whether to backfill missed runs:

```python
dag = DAG(
    'claims_pipeline',
    catchup=False,  # Don't backfill (default)
    # or
    catchup=True,   # Automatically backfill missed runs
    # ...
)
```

## Environment Variables

DAGs can use Airflow Variables for configuration:

```python
from airflow.models import Variable

db_path = Variable.get('WAREHOUSE_DB_PATH', default_var='warehouse.db')
```

Set variables in Airflow UI: Admin → Variables

Or via CLI:
```bash
docker-compose exec airflow airflow variables set WAREHOUSE_DB_PATH /opt/airflow/warehouse.db
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'src'`:

1. **Check package installation**: The entrypoint script installs the package automatically
2. **Check PYTHONPATH**: Should be `/opt/airflow:/opt/airflow/src` in container
3. **Restart container**: `docker-compose restart airflow`
4. **Check logs**: `docker-compose logs airflow | grep "Installing project package"`

### DAG Not Appearing

1. Check DAG file syntax: `docker-compose exec airflow python airflow/dags/claims_pipeline_dag.py`
2. Check Airflow logs: `docker-compose logs airflow | grep -i dag`
3. Verify imports work: `docker-compose exec airflow python -c "from src.pipelines import ClaimsPipeline"`

### Backfill Not Working

1. Ensure `catchup=True` is set (for automatic backfill)
2. Check start_date is in the past
3. Verify date range: `-s` (start) must be before `-e` (end)
4. Check DAG run config for date parameters

## Best Practices

1. **Use Separate DAGs**: One DAG per data type (claims, policies)
2. **Parameterize**: Use DAG run config for runtime parameters
3. **Test Locally**: Test pipeline logic outside Airflow first
4. **Monitor Logs**: Check Airflow task logs for errors
5. **Idempotent**: Ensure pipelines can run multiple times safely
6. **Backfill Carefully**: Test backfill on small date ranges first
7. **Clean Imports**: Never use `sys.path` manipulation - install package properly

## Next Steps

- **[DOCKER.md](../../DOCKER.md)** → Complete Docker and Airflow guide
- **[config/PIPELINE_CONFIG_GUIDE.md](../../config/PIPELINE_CONFIG_GUIDE.md)** → Configure pipelines
- **[docs/SDK_API_REFERENCE.md](../../docs/SDK_API_REFERENCE.md)** → SDK usage
