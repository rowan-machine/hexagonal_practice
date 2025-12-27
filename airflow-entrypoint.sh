#!/bin/bash
set -e

echo "Installing Airflow Python dependencies..."
pip install --no-cache-dir -r /requirements-airflow.txt

echo "Installing project package in editable mode..."
# Install the project package so imports work properly
# The project root is mounted at /opt/airflow/project
if [ -f /opt/airflow/project/setup.py ] || [ -f /opt/airflow/project/pyproject.toml ]; then
    # Clean up any existing egg-info directories that might cause conflicts
    rm -rf /opt/airflow/project/src/*.egg-info 2>/dev/null || true
    rm -rf /opt/airflow/project/*.egg-info 2>/dev/null || true
    
    # Install in editable mode
    # Note: Project root is mounted (not read-only) so pip can create egg-info
    if pip install --no-cache-dir -e /opt/airflow/project; then
        echo "Project package installed successfully"
    else
        echo "WARNING: Package installation failed, but continuing..."
        echo "Imports will work via PYTHONPATH (/opt/airflow:/opt/airflow/src)"
    fi
else
    echo "WARNING: setup.py or pyproject.toml not found at /opt/airflow/project"
    echo "Relying on PYTHONPATH for imports"
fi

echo "Waiting for Postgres to be ready..."
# Wait for postgres to be available - check if hostname resolves first
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if PGPASSWORD=airflow psql -h postgres -U airflow -d airflow -c "SELECT 1" > /dev/null 2>&1; then
    echo "Postgres is ready!"
    break
  fi
  echo "Postgres is unavailable (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES) - sleeping..."
  sleep 3
  RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "ERROR: Postgres did not become available after $MAX_RETRIES attempts"
  exit 1
fi

echo "Checking Airflow DB connection..."
# Now wait for Airflow to be able to connect
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if airflow db check > /dev/null 2>&1; then
    echo "Airflow DB connection successful!"
    break
  fi
  echo "Airflow DB check failed (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES) - retrying..."
  sleep 3
  RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "ERROR: Airflow DB check failed after $MAX_RETRIES attempts"
  exit 1
fi

echo "Initializing Airflow DB..."
airflow db init

echo "Creating admin user (if not exists)..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com || true

echo "Starting Airflow..."
exec airflow webserver & exec airflow scheduler
