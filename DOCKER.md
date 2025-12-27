# Docker Guide

Complete guide for running the pipeline system with Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

## Quick Start

### 1. Start Services

```bash
# Start all services and wait for Airflow to be ready (recommended)
make docker-up-wait

# Or start services without waiting
make docker-up
# Then wait for Airflow separately:
make wait-airflow

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Note**: `make docker-up-wait` automatically waits for Airflow's webserver (gunicorn) to be ready, so you'll know when the UI is accessible.

### 2. Access Services

- **Airflow UI**: http://localhost:8080 (wait for `make docker-up-wait` to complete)
- **PostgreSQL**: localhost:5432

### 3. Run Pipelines in Docker

```bash
# Execute pipeline in Airflow container
docker-compose exec airflow python run_local.py claims_pipeline

# With custom database path
docker-compose exec airflow python run_local.py claims_pipeline --db-path /opt/airflow/warehouse.db
```

## Service Details

### PostgreSQL

- **Port**: 5432
- **Database**: airflow
- **User**: airflow
- **Password**: airflow
- **Volume**: `postgres-db-volume` (persistent)

### Airflow

- **Port**: 8080
- **Image**: apache/airflow:2.10.3
- **Volumes**:
  - `./src` → `/opt/airflow/src`
  - `./data` → `/opt/airflow/data`
  - `./pipelines_config` → `/opt/airflow/pipelines_config`
  - `./schemas` → `/opt/airflow/schemas`

## Environment Variables

Environment variables are configured in a `.env` file in the project root.

### Quick Setup

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** if you need to change any values (defaults work for local development)

3. **Start services** - Docker Compose automatically loads `.env`

### Available Variables

See **[docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)** for complete documentation.

**Key variables**:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - Airflow database
- `WAREHOUSE_DB_*` - Warehouse database connection
- `ATLAS_URL`, `ATLAS_ENABLED` - Atlas configuration
- `AIRFLOW__*` - Airflow settings

**Note**: The `.env` file is NOT committed to git (see `.gitignore`). Use `.env.example` as a template.

## Running Notebooks in Docker

### Option 1: Jupyter in Container

Add to `docker-compose.yml`:

```yaml
jupyter:
  image: jupyter/scipy-notebook:latest
  ports:
    - "8888:8888"
  volumes:
    - ./notebooks:/home/jovyan/work/notebooks
    - ./src:/home/jovyan/work/src
    - ./data:/home/jovyan/work/data
  environment:
    - JUPYTER_ENABLE_LAB=yes
  command: start-notebook.sh --NotebookApp.token='' --NotebookApp.password=''
```

Then access at http://localhost:8888

### Option 2: Local Jupyter with Docker Data

Run Jupyter locally but mount Docker volumes:

```bash
# Start services and wait for Airflow
make docker-up-wait

# Run Jupyter locally
jupyter notebook notebooks/
```

## Development Workflow

### 1. Local Development

```bash
# Develop locally
python run_local.py claims_pipeline

# Test changes
pytest
```

### 2. Docker Testing

```bash
# Test in Docker environment
docker-compose exec airflow pytest

# Run specific test
docker-compose exec airflow pytest src/tests/test_domain.py
```

### 3. Production Deployment

```bash
# Build custom image
docker build -t ringmaster-pipelines:latest .

# Run with production config
docker run -v $(pwd)/data:/app/data ringmaster-pipelines:latest
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Restart services (stops and starts fresh)
make docker-restart

# Or manually restart
docker-compose restart

# Rebuild containers
docker-compose up --build
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U airflow -d airflow
```

### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Airflow UID
export AIRFLOW_UID=$(id -u)
docker-compose up -d
```

### Volume Mount Issues

```bash
# Check volumes
docker-compose config

# Verify mounts
docker-compose exec airflow ls -la /opt/airflow/src
```

## Advanced Configuration

### Custom Database

Modify `docker-compose.yml`:

```yaml
services:
  postgres:
    environment:
      POSTGRES_DB: custom_db
      POSTGRES_USER: custom_user
      POSTGRES_PASSWORD: custom_password
```

### Resource Limits

```yaml
services:
  airflow:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Network Configuration

```yaml
services:
  airflow:
    networks:
      - pipeline-network
    depends_on:
      - postgres

networks:
  pipeline-network:
    driver: bridge
```

## Best Practices

1. **Use volumes for data persistence**: Don't store data in containers
2. **Environment variables**: Use `.env` file for configuration
3. **Health checks**: Add health checks for services
4. **Resource limits**: Set appropriate limits for production
5. **Logging**: Configure centralized logging
6. **Backups**: Regular backups of PostgreSQL volumes

## Production Deployment

For production, consider:

1. **Secrets management**: Use Docker secrets or external secret managers
2. **Orchestration**: Kubernetes or Docker Swarm
3. **Monitoring**: Prometheus, Grafana
4. **Logging**: ELK stack or similar
5. **High availability**: Multiple Airflow workers
6. **Database**: Managed PostgreSQL service

## Airflow Command Line Guide

### Running Airflow CLI Commands

All Airflow CLI commands should be run inside the Airflow container:

```bash
# Basic syntax
docker-compose exec airflow airflow <command> [options]

# Examples
docker-compose exec airflow airflow version
docker-compose exec airflow airflow db check
docker-compose exec airflow airflow dags list
```

### Common Airflow CLI Commands

#### Database Management

```bash
# Check database connection
docker-compose exec airflow airflow db check

# Initialize database (first time setup)
docker-compose exec airflow airflow db init

# Upgrade database schema
docker-compose exec airflow airflow db upgrade

# Reset database (WARNING: deletes all data)
docker-compose exec airflow airflow db reset

# Show database connection info
docker-compose exec airflow airflow config get-value database sql_alchemy_conn
```

#### DAG Management

```bash
# List all DAGs
docker-compose exec airflow airflow dags list

# List DAGs with details
docker-compose exec airflow airflow dags list-import-errors

# Show DAG details
docker-compose exec airflow airflow dags show <dag_id>

# Test DAG syntax
docker-compose exec airflow airflow dags test <dag_id> <execution_date>

# Backfill DAG (run historical tasks)
docker-compose exec airflow airflow dags backfill <dag_id> -s <start_date> -e <end_date>

# Trigger DAG manually
docker-compose exec airflow airflow dags trigger <dag_id>
```

#### Task Management

```bash
# List tasks in a DAG
docker-compose exec airflow airflow tasks list <dag_id>

# Test a specific task
docker-compose exec airflow airflow tasks test <dag_id> <task_id> <execution_date>

# Run a task instance
docker-compose exec airflow airflow tasks run <dag_id> <task_id> <execution_date>

# Clear task state
docker-compose exec airflow airflow tasks clear <dag_id> -t <task_id> -y
```

#### User Management

```bash
# List users
docker-compose exec airflow airflow users list

# Create user
docker-compose exec airflow airflow users create \
  --username <username> \
  --password <password> \
  --firstname <firstname> \
  --lastname <lastname> \
  --role Admin \
  --email <email>

# Delete user
docker-compose exec airflow airflow users delete --username <username>
```

#### Variables and Connections

```bash
# List variables
docker-compose exec airflow airflow variables list

# Get variable
docker-compose exec airflow airflow variables get <variable_name>

# Set variable
docker-compose exec airflow airflow variables set <variable_name> <value>

# List connections
docker-compose exec airflow airflow connections list

# Get connection
docker-compose exec airflow airflow connections get <connection_id>

# Add connection
docker-compose exec airflow airflow connections add <connection_id> \
  --conn-type <type> \
  --conn-host <host> \
  --conn-login <login> \
  --conn-password <password>
```

#### Service Management

```bash
# Check Airflow version
docker-compose exec airflow airflow version

# Show Airflow info
docker-compose exec airflow airflow info

# Check webserver health
docker-compose exec airflow curl -f http://localhost:8080/health

# View scheduler logs
docker-compose logs -f airflow | grep scheduler

# View webserver logs
docker-compose logs -f airflow | grep webserver
```

### Running Python Scripts in Airflow Container

You can run your pipeline scripts inside the Airflow container:

```bash
# Run pipeline script
docker-compose exec airflow python scripts/run_local.py claims_pipeline

# Run with custom database path
docker-compose exec airflow python scripts/run_local.py claims_pipeline \
  --db-path /opt/airflow/warehouse.db

# Run Python script with full path
docker-compose exec airflow python /opt/airflow/src/pipelines/claims_pipeline.py

# Run pytest tests
docker-compose exec airflow pytest src/tests/

# Run specific test file
docker-compose exec airflow pytest src/tests/test_domain.py -v
```

### Interactive Shell Access

```bash
# Open bash shell in Airflow container
docker-compose exec airflow bash

# Once inside, you can run Airflow commands directly:
airflow version
airflow dags list
python scripts/run_local.py claims_pipeline
```

### Checking Airflow Webserver Status

```bash
# Check if webserver (gunicorn) is running
docker-compose exec airflow curl -f http://localhost:8080/health

# Or from host machine
curl http://localhost:8080/health

# Check webserver process
docker-compose exec airflow ps aux | grep gunicorn

# View webserver logs
docker-compose logs airflow | grep -i gunicorn
```

### Example: Complete Workflow

```bash
# 1. Start services and wait for Airflow to be ready (recommended)
make docker-up-wait

# Or start services separately, then wait:
make docker-up
make wait-airflow

# 2. Check Airflow is running
docker-compose exec airflow airflow version

# 3. List DAGs
docker-compose exec airflow airflow dags list

# 4. Test a DAG
docker-compose exec airflow airflow dags test claims_pipeline 2024-01-01

# 5. Trigger a DAG run
docker-compose exec airflow airflow dags trigger claims_pipeline

# 6. Check task status
docker-compose exec airflow airflow tasks state claims_pipeline process_claims 2024-01-01T00:00:00
```

### Troubleshooting Airflow CLI

```bash
# If commands fail, check:
# 1. Container is running
docker-compose ps airflow

# 2. Database connection
docker-compose exec airflow airflow db check

# 3. DAG import errors
docker-compose exec airflow airflow dags list-import-errors

# 4. View full logs
docker-compose logs airflow

# 5. Restart Airflow services
docker-compose restart airflow
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow CLI Reference](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html)

