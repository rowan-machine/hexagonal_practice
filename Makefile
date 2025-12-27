.PHONY: help install install-dev test lint format type-check coverage clean run-claims run-policies verify docker-up docker-down docker-logs

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

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml

run-claims: ## Run claims pipeline
	python scripts/run_local.py claims_pipeline

run-policies: ## Run policies pipeline
	python scripts/run_local.py policies_pipeline

verify: ## Run all verification scripts
	python scripts/verify_setup.py
	python scripts/verify_data_loaded.py

verify-atlas: ## Verify Atlas entities
	python scripts/verify_atlas_entities.py

verify-pipeline: ## Verify pipeline execution
	python scripts/verify_pipeline_complete.py

verify-release: ## Run release readiness checks
	python scripts/test_release_readiness.py

verify-all: verify verify-atlas verify-pipeline verify-release ## Run all verification scripts

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-restart: ## Restart Docker services
	docker-compose restart

docker-clean: ## Clean Docker volumes and containers
	docker-compose down -v
	docker system prune -f

all-checks: lint type-check test ## Run all quality checks

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci: install-dev lint type-check test ## Run CI checks locally

setup-branches: ## Setup git branches (develop, test, main)
	@echo "Setting up Git branches..."
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File scripts/setup_git_branches.ps1
else
	@bash -c 'if [ -f scripts/setup_git_branches.sh ]; then bash scripts/setup_git_branches.sh; else echo "Creating branches manually..."; git checkout -b develop 2>/dev/null || git checkout develop; git checkout -b test 2>/dev/null || git checkout test; git checkout main 2>/dev/null || git checkout main; echo "Branches created. Push with: git push -u origin develop test"; fi'
endif

test-release: verify-release ## Test release readiness

test-examples: ## Run example scripts
	python examples/pipeline_example.py
	python examples/sdk_example.py

test-scripts: ## Test all scripts
	python scripts/run_local.py --list
	python scripts/verify_setup.py
	python scripts/test_release_readiness.py

