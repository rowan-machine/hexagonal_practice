# Environment Variables Guide

Complete guide for managing environment variables in the project.

## Overview

Environment variables are used for:
- **Docker Compose**: Service configuration (databases, Airflow, Atlas)
- **Application Code**: Runtime configuration (Atlas URL, database connections)
- **Airflow**: DAG configuration and runtime settings

## Quick Start

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your values (if needed)

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

The `.env` file is automatically loaded by Docker Compose.

## File Structure

- **`.env.example`**: Template with all available variables (committed to git)
- **`.env`**: Your local configuration (NOT committed to git)
- **`docker-compose.yml`**: Uses variables from `.env` with defaults

## Environment Variables

### PostgreSQL (Airflow Database)

```env
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

**Used by**: `postgres` service in Docker Compose

### Warehouse Database

```env
WAREHOUSE_DB_HOST=warehouse
WAREHOUSE_DB_PORT=5432
WAREHOUSE_DB_NAME=warehouse
WAREHOUSE_DB_USER=warehouse
WAREHOUSE_DB_PASSWORD=warehouse
```

**Used by**: 
- `warehouse` service in Docker Compose
- Application code for database connections
- Airflow DAGs

### Apache Atlas

```env
ATLAS_URL=http://atlas:21000
ATLAS_ENABLED=true
```

**Used by**:
- `atlas` service in Docker Compose
- Pipeline code (`src/pipelines/*.py`) for metadata publishing
- Can be disabled by setting `ATLAS_ENABLED=false`

**In Code**:
```python
import os
atlas_url = os.getenv("ATLAS_URL", "http://atlas:21000")
atlas_enabled = os.getenv("ATLAS_ENABLED", "true").lower() == "true"
```

### Airflow Configuration

```env
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__WEBSERVER__AUTHENTICATE=False
AIRFLOW__WEBSERVER__RBAC=False
AIRFLOW_UID=50000
```

**Used by**: `airflow` service in Docker Compose

**Note**: Airflow uses double underscores (`__`) to represent nested configuration. For example:
- `AIRFLOW__CORE__EXECUTOR` → `[core] executor` in `airflow.cfg`

### Python Path

```env
PYTHONPATH=/opt/airflow:/opt/airflow/src
```

**Used by**: `airflow` service for Python imports

### Atlas Server Options

```env
ATLAS_SERVER_OPTS=-server -Xms1024m -Xmx2048m
```

**Used by**: `atlas` service for JVM configuration

## Local Development (Outside Docker)

For local development, you can set environment variables:

### Windows (PowerShell)

```powershell
$env:ATLAS_URL="http://localhost:21000"
$env:ATLAS_ENABLED="true"
python scripts/publish_atlas_metadata.py
```

### Windows (CMD)

```cmd
set ATLAS_URL=http://localhost:21000
set ATLAS_ENABLED=true
python scripts/publish_atlas_metadata.py
```

### Linux/Mac

```bash
export ATLAS_URL=http://localhost:21000
export ATLAS_ENABLED=true
python scripts/publish_atlas_metadata.py
```

Or use a `.env` file with a tool like `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

## Production Deployment

**Never commit `.env` files to version control!**

For production:

1. **Use secret management services**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Kubernetes Secrets

2. **Set environment variables in deployment platform**:
   - Docker: `docker run -e VAR=value`
   - Kubernetes: ConfigMaps and Secrets
   - Cloud platforms: Environment variable configuration

3. **Use different `.env` files per environment**:
   - `.env.development`
   - `.env.staging`
   - `.env.production`

## Airflow Variables vs Environment Variables

### Environment Variables
- Set at container/service level
- Available to all processes
- Used for infrastructure configuration
- Examples: Database connections, service URLs

### Airflow Variables
- Set in Airflow UI or via CLI
- Available only to Airflow DAGs
- Used for DAG-specific configuration
- Examples: `WAREHOUSE_DB_PATH`, custom pipeline parameters

**Set Airflow Variables**:
```bash
docker-compose exec airflow airflow variables set WAREHOUSE_DB_PATH /opt/airflow/warehouse.db
```

**Use in DAGs**:
```python
from airflow.models import Variable
db_path = Variable.get('WAREHOUSE_DB_PATH', default_var='warehouse.db')
```

## Troubleshooting

### Variables Not Loading

1. **Check `.env` file exists**: `ls -la .env`
2. **Check file format**: No spaces around `=`, no quotes needed
3. **Restart Docker**: `docker-compose down && docker-compose up -d`
4. **Check Docker Compose version**: Requires Docker Compose 2.0+

### Variables Not Available in Code

1. **Check if running in Docker**: Variables are set in `docker-compose.yml`
2. **For local development**: Set variables manually or use `python-dotenv`
3. **Check variable names**: Case-sensitive, exact match required

### Security Concerns

1. **Never commit `.env`**: Already in `.gitignore`
2. **Use strong passwords**: Change default passwords in production
3. **Rotate secrets**: Regularly update passwords and tokens
4. **Limit access**: Only necessary services should have access

## Best Practices

1. **Use `.env.example`**: Template for all variables
2. **Document defaults**: Show default values in documentation
3. **Validate variables**: Check required variables on startup
4. **Use secrets management**: For production deployments
5. **Separate environments**: Different values for dev/staging/prod
6. **Minimize variables**: Only what's needed, no hardcoded values

## Next Steps

- **[DOCKER.md](../DOCKER.md)** → Docker configuration
- **[SECURITY.md](../SECURITY.md)** → Security best practices
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Setup guide

