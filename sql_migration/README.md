# SQL Migration Documentation

This directory contains documentation for migrating SQL queries and business logic to the Python pipeline architecture.

## Purpose

- Track original SQL queries and their Python equivalents
- Document business rules and aggregation logic
- Ensure consistency between SQL and Python implementations
- Provide reference for future migrations
- Establish process for systematic migration

## Files

- **`sql_migration_tracker.md`**: Main tracking document with all migrated queries
- **`MIGRATION_PROCESS.md`**: Step-by-step process guide for migrations
- **`README.md`**: This file - overview and quick reference

## Quick Start

1. **Read the Process**: Start with `MIGRATION_PROCESS.md` for the complete workflow
2. **Document SQL**: Add entry to `sql_migration_tracker.md`
3. **Extract Rules**: Identify business rules from SQL
4. **Implement**: Create/update code in `src/business_rules/`
5. **Update Pipelines**: Refactor pipeline steps to use business rules
6. **Update SDK**: Add SDK methods using business rules
7. **Validate**: Configure validation in `config/validation.yml`
8. **Test**: Write unit and integration tests
9. **Complete**: Mark migration complete in tracker

## Adding New Migrations

1. **Document SQL**: Add entry to status table in `sql_migration_tracker.md`
   - Query ID (e.g., `CLAIMS_GOLD_001`)
   - Original SQL query
   - Business rules extracted
   - Data source and output

2. **Extract Business Rules**: Identify core logic from SQL
   - Grouping, aggregations, filters, calculations

3. **Implement Rules**: Add to `src/business_rules/`
   - Reference SQL migration ID in docstring
   - Match SQL logic exactly

4. **Update Code**: Refactor pipelines and SDK
   - Remove duplicate logic
   - Use centralized business rules

5. **Add Validation**: Configure in `config/validation.yml`
   - Expected counts from SQL estate
   - Use `ValidationLoader` for validation

6. **Write Tests**: Ensure Python matches SQL results

7. **Complete**: Update tracker status

## Business Rules Location

All centralized business rules are in `src/business_rules/`:
- **`aggregations.py`**: Aggregation business rules (used by pipelines and SDK)
- **Future**: Additional rule modules as needed (filters, calculations, etc.)

## Validation

Validation simulates SQL estate validation:
- **Development**: Reads expected counts from source JSON files
- **Production**: Will query original SQL database
- **Config**: `config/validation.yml` defines validation rules
- **Loader**: `src/utils/validation_loader.py` performs validation

## Verification

When migrating SQL to Python:
1. Extract business rules to `src/business_rules/`
2. Use rules in both pipeline steps and SDK
3. Write unit tests to verify Python matches SQL results
4. Configure validation to compare counts
5. Document in migration tracker
6. Verify results match SQL exactly before decommissioning

## Migration Status

See `sql_migration_tracker.md` for current migration status and completed queries.

