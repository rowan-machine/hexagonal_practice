#!/bin/bash
set -e

echo "Installing Airflow Python dependencies..."
pip install --no-cache-dir -r /requirements-airflow.txt

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
