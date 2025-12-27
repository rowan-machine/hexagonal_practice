# Docker Compose Setup

This document describes the Docker Compose setup for the data pipeline system.

## Services

### 1. PostgreSQL (Airflow Database)
- **Port**: 5432
- **Database**: `airflow`
- **User**: `airflow` / `airflow`
- **Purpose**: Airflow metadata database

### 2. Warehouse (PostgreSQL)
- **Port**: 5433 (mapped from 5432)
- **Database**: `warehouse`
- **User**: `warehouse` / `warehouse`
- **Purpose**: Data warehouse for fact and gold tables
- **Tables**: Created via `db_bootstrap.py`

### 3. Apache Atlas
- **Port**: 21000
- **Purpose**: Data lineage and governance
- **URL**: `http://localhost:21000`
- **Status**: Optional (can be disabled via `ATLAS_ENABLED=false`)

### 4. Airflow
- **Port**: 8080
- **Web UI**: `http://localhost:8080`
- **Purpose**: Pipeline orchestration
- **Dependencies**: Waits for postgres and warehouse to be healthy

## Environment Variables

### Airflow Service

- `WAREHOUSE_DB_HOST`: warehouse (service name)
- `WAREHOUSE_DB_PORT`: 5432
- `WAREHOUSE_DB_NAME`: warehouse
- `WAREHOUSE_DB_USER`: warehouse
- `WAREHOUSE_DB_PASSWORD`: warehouse
- `ATLAS_URL`: http://atlas:21000
- `ATLAS_ENABLED`: "true" (set to "false" to disable)

## Usage

### Start Services

```bash
# Recommended: Start services and wait for Airflow to be ready
make docker-up-wait

# Or start services without waiting
make docker-up
# Then wait for Airflow separately:
make wait-airflow
```

**Note**: Using `make docker-up-wait` ensures Airflow's webserver (gunicorn) is ready before proceeding. This is especially useful when you need to access the Airflow UI immediately.

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow
docker-compose logs -f warehouse
```

### Access Services

- **Airflow UI**: http://localhost:8080
- **Atlas UI**: http://localhost:21000
- **PostgreSQL (Airflow)**: localhost:5432
- **PostgreSQL (Warehouse)**: localhost:5433

### Initialize Warehouse Tables

Tables are created automatically via `db_bootstrap.py` when pipelines run, or you can initialize manually:

```python
from src.utils.db_bootstrap import DatabaseBootstrap
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="warehouse",
    user="warehouse",
    password="warehouse"
)

bootstrap = DatabaseBootstrap()
bootstrap.ensure_all_tables(conn)
```

## Volumes

- `postgres-db-volume`: Airflow database persistence
- `warehouse-db-volume`: Warehouse database persistence

## Health Checks

All services include health checks to ensure proper startup order:
- PostgreSQL services wait for database to be ready
- Atlas waits for warehouse
- Airflow waits for both PostgreSQL services

## Notes

- Atlas is optional and can be disabled by setting `ATLAS_ENABLED=false`
- For local development with SQLite, you don't need Docker
- Warehouse tables match Atlas metadata definitions
- All table schemas are in `src/utils/db_bootstrap.py`

