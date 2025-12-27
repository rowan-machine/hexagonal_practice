# Docker Guide

Complete guide for running the pipeline system with Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

## Quick Start

### 1. Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Access Services

- **Airflow UI**: http://localhost:8080
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

Create a `.env` file in the project root:

```env
# Airflow
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=false

# Database
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

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
# Start services
docker-compose up -d

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

# Restart services
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

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Airflow Documentation](https://airflow.apache.org/docs/)

