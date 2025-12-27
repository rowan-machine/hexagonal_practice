# SQL to Business Logic Migration Process

This document describes the established process for migrating SQL queries and business logic to the Python pipeline architecture.

## Overview

The migration process ensures that:
1. Original SQL logic is preserved and documented
2. Business rules are centralized in Python
3. Both pipelines and SDK use the same business logic
4. Validation ensures SQL and Python produce identical results

## Migration Process Steps

### Step 1: Document Original SQL

1. **Identify SQL Query**: Find the SQL query in the legacy system
2. **Document in Tracker**: Add entry to `sql_migration/sql_migration_tracker.md`
   - Query ID (e.g., `CLAIMS_GOLD_001`)
   - Original SQL query
   - Business rules extracted from SQL
   - Data source and output tables

**Example:**
```markdown
## Query: CLAIMS_GOLD_001 - Claims Aggregation by Policy

### Original SQL Query
```sql
SELECT policy_id, SUM(claim_amount) AS total_claims, ...
FROM claims_silver
GROUP BY policy_id
```

### Business Rules
1. Group by policy_id
2. Sum claim_amount
3. Count claims
...
```

### Step 2: Extract Business Rules

1. **Identify Business Logic**: Extract the core business rules from SQL
   - Grouping logic
   - Aggregation functions
   - Filtering conditions
   - Calculation formulas

2. **Document Rules**: Add to migration tracker with clear descriptions

### Step 3: Implement in Business Rules Module

1. **Create/Update Business Rules**: Add to `src/business_rules/aggregations.py` (or appropriate module)

2. **Follow Pattern**:
   ```python
   class ClaimsAggregator(LoggingMixin):
       def aggregate_by_policy(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
           """
           Business Rule (SQL Migration: CLAIMS_GOLD_001):
           - Group by policy_id
           - Calculate: total_claims (sum), claim_count (count), ...
           
           This matches the SQL query:
               SELECT policy_id, SUM(claim_amount) AS total_claims, ...
           """
           # Implementation matches SQL logic
   ```

3. **Add SQL Reference**: Include SQL migration ID in docstring

### Step 4: Update Pipeline Steps

1. **Refactor Pipeline Step**: Update pipeline step to use business rules
   ```python
   def _prepare_gold_data(self, gold_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
       from src.business_rules.aggregations import ClaimsAggregator
       
       aggregator = ClaimsAggregator()
       return aggregator.aggregate_by_policy(gold_data)
   ```

2. **Remove Duplicate Logic**: Ensure no business logic remains in pipeline step

### Step 5: Update SDK

1. **Add SDK Methods**: Add methods that use business rules
   ```python
   def get_policy_aggregations(self, claims: List[Claim]) -> List[Dict[str, Any]]:
       from src.business_rules.aggregations import ClaimsAggregator
       
       claim_dicts = [self._claim_to_dict(claim) for claim in claims]
       aggregator = ClaimsAggregator()
       return aggregator.aggregate_by_policy(claim_dicts)
   ```

2. **Ensure Consistency**: SDK and pipeline use same business rules

### Step 6: Create Validation

1. **SQL Estate Validation**: Create validation that simulates SQL query results
   - For now: Read expected counts from source JSON files
   - In production: Query original SQL database

2. **Update Validation Config**: Add to `config/validation.yml`
   ```yaml
   claims:
     expected_count: 12  # From SQL: SELECT COUNT(*) FROM claims_source
     source_table: "claims_source"
   ```

3. **Use ValidationLoader**: Use `ValidationLoader` to validate counts
   ```python
   from src.utils.validation_loader import ValidationLoader
   
   loader = ValidationLoader()
   result = loader.validate_claims_count(actual_count=len(claims))
   ```

### Step 7: Write Tests

1. **Unit Tests**: Test business rules independently
   ```python
   def test_claims_aggregation_matches_sql():
       # Test that Python aggregation matches SQL results
   ```

2. **Integration Tests**: Test pipeline with business rules
   ```python
   def test_pipeline_produces_same_results_as_sql():
       # Compare pipeline output with SQL query results
   ```

### Step 8: Update Migration Tracker

1. **Mark Complete**: Update status in `sql_migration_tracker.md`
2. **Add Notes**: Document any differences or improvements
3. **Link Implementation**: Add links to Python code locations

## File Locations

### Migration Documentation
- **Main Tracker**: `sql_migration/sql_migration_tracker.md`
- **Process Guide**: `sql_migration/MIGRATION_PROCESS.md` (this file)
- **README**: `sql_migration/README.md`

### Business Rules
- **Aggregations**: `src/business_rules/aggregations.py`
- **Future Rules**: Add new modules as needed

### Validation
- **Config**: `config/validation.yml`
- **Loader**: `src/utils/validation_loader.py`

### Pipeline Steps
- **Claims**: `src/pipelines/claims_pipeline.py`
- **Policies**: `src/pipelines/policies_pipeline.py`

### SDK
- **Analyst SDK**: `src/sdk/analyst.py`

## Validation Strategy

### Current (Development)
- Read expected counts from source JSON files
- Simulates SQL estate validation
- Validates against `config/validation.yml` as fallback

### Production (Future)
- Query original SQL database for expected counts
- Compare SQL results with Python pipeline results
- Ensure 100% match before decommissioning SQL

## Example: Complete Migration

### 1. Original SQL
```sql
SELECT policy_id, SUM(claim_amount) AS total_claims, COUNT(*) AS claim_count
FROM claims_silver
GROUP BY policy_id;
```

### 2. Documented in Tracker
- Added to `sql_migration_tracker.md` as `CLAIMS_GOLD_001`

### 3. Business Rules Created
- `ClaimsAggregator.aggregate_by_policy()` in `src/business_rules/aggregations.py`

### 4. Pipeline Updated
- `ClaimsGoldStep._prepare_gold_data()` uses `ClaimsAggregator`

### 5. SDK Updated
- `ClaimsAnalyst.get_policy_aggregations()` uses `ClaimsAggregator`

### 6. Validation Added
- `ValidationLoader.validate_claims_count()` reads from JSON
- Config in `config/validation.yml`

### 7. Tests Written
- Unit tests for `ClaimsAggregator`
- Integration tests for pipeline

### 8. Migration Complete
- Status updated in tracker
- All code uses centralized business rules

## Best Practices

1. **Single Source of Truth**: Business rules live in `src/business_rules/`
2. **Document Everything**: SQL queries, business rules, and Python code
3. **Test Thoroughly**: Ensure SQL and Python produce identical results
4. **Validate Continuously**: Use validation to catch regressions
5. **Incremental Migration**: Migrate one query at a time
6. **Keep SQL Accessible**: Don't delete SQL until migration is verified

## Checklist for Each Migration

- [ ] Original SQL documented in tracker
- [ ] Business rules extracted and documented
- [ ] Business rules implemented in `src/business_rules/`
- [ ] Pipeline step updated to use business rules
- [ ] SDK updated to use business rules
- [ ] Validation configured
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Results verified against SQL
- [ ] Migration marked complete in tracker
- [ ] Documentation updated

