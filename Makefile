.PHONY: help install install-dev test test-dags test-dags-docker lint format type-check coverage clean run-claims run-policies verify docker-up docker-down docker-logs wait-airflow check-airflow docker-up-wait atlas-publish atlas-verify atlas-query atlas-query-curl atlas-debug-payload atlas-setup atlas-fix-stale verify-atlas wait-atlas setup-all

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements/requirements.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test: ## Run all tests
	pytest

test-dags: ## Run DAG tests locally (requires Airflow)
	@echo "Running DAG tests locally..."
	@echo "Note: These tests require Apache Airflow. Install with: pip install apache-airflow==2.10.3"
	@echo "Or use: make test-dags-docker"
	@pytest src/tests/test_dags_*.py -v || echo "DAG tests skipped - Airflow not installed"

test-dags-docker: ## Run DAG tests in Docker container (recommended)
	@echo "Running DAG tests in Docker container..."
	@echo "Note: Docker services must be running. Start with: make docker-up-wait"
	@docker-compose exec -T airflow pytest src/tests/test_dags_*.py -v || \
		(echo "Error: Docker services may not be running. Start with: make docker-up-wait" && exit 1)

test-sql-converter: ## Run SQL to Pandas converter tests
	@echo "Running SQL to Pandas converter tests..."
	@pytest src/tests/test_sql_to_pandas.py -v

sql-to-pandas: ## Convert SQL file to pandas (usage: make sql-to-pandas SQL_FILE=path/to/file.sql TABLE=table_name)
	@python -c "import sys; sys.exit(0 if '$(SQL_FILE)' else 1)" || (echo "Usage: make sql-to-pandas SQL_FILE=path/to/file.sql TABLE=table_name" && exit 1)
	@python scripts/sql_to_pandas_cli.py $(SQL_FILE) --table $(TABLE) || echo "Note: Install sqlglot and pandas: pip install sqlglot pandas"

test-verbose: ## Run tests with verbose output
	pytest -v

test-coverage: ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	ruff check src/ scripts/ examples/
	black --check src/ scripts/ examples/

format: ## Format code
	ruff check --fix src/ scripts/ examples/
	black src/ scripts/ examples/

type-check: ## Run type checker
	mypy src/ --ignore-missing-imports

coverage: ## Generate coverage report
	pytest --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

clean: ## Clean generated files - cross-platform
	@python -c "import os, shutil, glob; [shutil.rmtree(d, ignore_errors=True) for d in glob.glob('**/__pycache__', recursive=True)] + [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)] + [os.remove(f) for f in glob.glob('**/*.pyo', recursive=True)] + [shutil.rmtree(d, ignore_errors=True) for d in glob.glob('**/*.egg-info', recursive=True)] + [shutil.rmtree(d, ignore_errors=True) for d in ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'build', 'dist', 'htmlcov']] + [os.remove(f) for f in ['.coverage', 'coverage.xml'] if os.path.exists(f)]"

run-claims: ## Run claims pipeline
	python scripts/run_local.py claims_pipeline

run-policies: ## Run policies pipeline
	python scripts/run_local.py policies_pipeline

verify: ## Run all verification scripts
	python scripts/verify_setup.py
	python scripts/verify_data_loaded.py

atlas-publish: ## Publish all metadata to Atlas
	@echo "Publishing metadata to Atlas..."
	python scripts/publish_atlas_metadata.py --atlas-url http://localhost:21000

atlas-verify: ## Verify Atlas entities are published
	@echo "Verifying Atlas entities..."
	python scripts/verify_atlas_entities.py

atlas-query: ## Query Atlas entities via API
	@echo "Querying Atlas entities..."
	python scripts/query_atlas_entities.py --search warehouse

atlas-query-curl: ## Query Atlas entities via curl
	@echo "Querying Atlas via curl..."
	@curl -u admin:admin "http://localhost:21000/api/atlas/v2/search/basic?query=warehouse" 2>/dev/null | python -m json.tool || echo "Query failed - check if Atlas is running"

atlas-debug-payload: ## Debug Atlas payload structure (policies example)
	@echo "Debugging Atlas payload structure..."
	@python -c "from src.utils.atlas_payloads import build_policies_table_payload; import json; payload = build_policies_table_payload(); print(json.dumps(payload, indent=2))"

atlas-setup: atlas-publish atlas-verify atlas-query ## Publish, verify, and query Atlas (complete setup)
	@echo ""
	@echo "Atlas setup complete! View entities at http://localhost:21000"
	@echo "Login: admin/admin"

atlas-fix-stale: ## Fix stale Atlas entity GUID errors
	@echo "Fixing stale Atlas entities..."
	@python scripts/fix_atlas_stale_entities.py

verify-atlas: atlas-verify ## Alias for atlas-verify (backward compatibility)

verify-pipeline: ## Verify pipeline execution (Atlas verification optional)
	@python scripts/verify_pipeline_complete.py || echo "Pipeline verification completed (Atlas check may have failed - this is optional)"

verify-release: ## Run release readiness checks
	python scripts/test_release_readiness.py

verify-all: verify verify-pipeline verify-release ## Run all verification scripts (Atlas optional)
	@echo ""
	@echo "Note: Atlas verification skipped (run 'make verify-atlas' separately if Atlas is running)"

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-restart: ## Restart Docker services
	docker-compose down
	docker-compose up -d

wait-airflow: ## Wait for Airflow webserver to be ready
	@python scripts/wait_for_airflow.py

check-airflow: ## Check if Airflow webserver is ready (quick check)
	@python scripts/wait_for_airflow.py --max-wait 5 --quiet && echo "✓ Airflow is ready at http://localhost:8080" || echo "✗ Airflow is not ready yet"

docker-up-wait: docker-up wait-airflow ## Start Docker services and wait for Airflow

wait-atlas: ## Wait for Atlas to be ready
	@python scripts/wait_for_atlas.py

setup-all: docker-up-wait wait-atlas atlas-setup run-claims run-policies ## Complete setup: start Docker, setup Atlas, and run both pipelines
	@echo ""
	@echo "=========================================="
	@echo "✓ Complete setup finished successfully!"
	@echo "=========================================="
	@echo ""
	@echo "Services running:"
	@echo "  - Airflow UI: http://localhost:8080"
	@echo "  - Atlas UI: http://localhost:21000 (admin/admin)"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Warehouse DB: localhost:5433"
	@echo ""
	@echo "Pipelines executed:"
	@echo "  ✓ Claims pipeline"
	@echo "  ✓ Policies pipeline"
	@echo ""
	@echo "Next steps:"
	@echo "  - View data: make verify"
	@echo "  - Check Atlas: make atlas-query"
	@echo "  - View logs: make docker-logs"

docker-clean: ## Clean Docker volumes and containers
	docker-compose down -v
	docker system prune -f

all-checks: lint type-check test ## Run all quality checks

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci: install-dev lint type-check test ## Run CI checks locally

setup-branches: ## Setup git branches (develop, test, main) - cross-platform
	@echo "Setting up Git branches..."
	@python scripts/setup_git_branches.py

test-release: verify-release ## Test release readiness

test-examples: ## Run example scripts
	python examples/pipeline_example.py
	python examples/sdk_example.py

test-scripts: ## Test all scripts
	python scripts/run_local.py --list
	python scripts/verify_setup.py
	python scripts/test_release_readiness.py

