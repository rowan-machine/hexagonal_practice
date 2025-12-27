#!/bin/bash
set -e

echo "Installing Airflow Python dependencies..."
pip install --no-cache-dir -r /requirements-airflow.txt

echo "Waiting for Postgres..."
until airflow db check; do
  sleep 3
done

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
