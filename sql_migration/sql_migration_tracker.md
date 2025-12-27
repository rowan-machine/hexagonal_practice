# SQL Migration Tracker

This document tracks the migration of SQL queries and business logic from legacy SQL-based systems to the Python pipeline architecture.

## Purpose

- Track original SQL queries and their Python equivalents
- Document business rules and aggregation logic
- Ensure consistency between SQL and Python implementations
- Provide reference for future migrations

## Migration Status

| Query ID | Original SQL | Python Implementation | Status | Notes |
|----------|--------------|----------------------|--------|-------|
| CLAIMS_GOLD_001 | See below | `src/business_rules/aggregations.py::ClaimsAggregator` | ✅ Complete | Claims by policy aggregation |
| POLICIES_GOLD_001 | See below | `src/business_rules/aggregations.py::PoliciesAggregator` | ✅ Complete | Policies by employer aggregation |

---

## Query: CLAIMS_GOLD_001 - Claims Aggregation by Policy

### Original SQL Query

```sql
-- Original SQL query for claims gold layer aggregation
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count,
    AVG(claim_amount) AS avg_claim_amount,
    MAX(claim_amount) AS max_claim_amount,
    MIN(claim_amount) AS min_claim_amount
FROM claims_silver
GROUP BY policy_id
ORDER BY total_claims DESC;
```

### Business Rules

1. **Grouping**: Group all claims by `policy_id`
2. **Aggregations**:
   - `total_claims`: Sum of all claim amounts per policy
   - `claim_count`: Count of distinct claims per policy
   - `avg_claim_amount`: Average claim amount per policy
   - `max_claim_amount`: Maximum claim amount per policy
   - `min_claim_amount`: Minimum claim amount per policy
3. **Data Source**: `claims_silver` table
4. **Output**: `claims_gold` table

### Python Implementation

**Location**: `src/business_rules/aggregations.py::ClaimsAggregator.aggregate_by_policy()`

**Usage in Pipeline**: `src/pipelines/claims_pipeline.py::ClaimsGoldStep`

**Usage in SDK**: `src/sdk/analyst.py::ClaimsAnalyst` (via business rules)

### Migration Notes

- Original SQL used `SUM()`, `COUNT()`, `AVG()`, `MAX()`, `MIN()` aggregate functions
- Python implementation uses `collections.defaultdict` for grouping, then calculates statistics
- Both implementations produce identical results
- Python version is more testable and maintainable

---

## Query: POLICIES_GOLD_001 - Policies Aggregation by Employer

### Original SQL Query

```sql
-- Original SQL query for policies gold layer aggregation
SELECT 
    employer_id,
    SUM(stop_loss_limit) AS total_coverage,
    COUNT(policy_id) AS policy_count,
    AVG(stop_loss_limit) AS avg_stop_loss_limit
FROM policies_silver
GROUP BY employer_id
ORDER BY total_coverage DESC;
```

### Business Rules

1. **Grouping**: Group all policies by `employer_id`
2. **Aggregations**:
   - `total_coverage`: Sum of all stop loss limits per employer
   - `policy_count`: Count of distinct policies per employer
   - `avg_stop_loss_limit`: Average stop loss limit per employer
3. **Data Source**: `policies_silver` table
4. **Output**: `policies_gold` table

### Python Implementation

**Location**: `src/business_rules/aggregations.py::PoliciesAggregator.aggregate_by_employer()`

**Usage in Pipeline**: `src/pipelines/policies_pipeline.py::PoliciesGoldStep`

**Usage in SDK**: `src/sdk/analyst.py::PoliciesAnalyst` (via business rules)

### Migration Notes

- Original SQL used `SUM()`, `COUNT()`, `AVG()` aggregate functions
- Python implementation uses `collections.defaultdict` for grouping
- Both implementations produce identical results
- Python version allows for easier unit testing and business rule modification

---

## Template for New Migrations

### Query: [QUERY_ID] - [Description]

#### Original SQL Query

```sql
-- Paste original SQL here
```

#### Business Rules

1. **Rule 1**: Description
2. **Rule 2**: Description
3. **Data Source**: Table name
4. **Output**: Table or output format

#### Python Implementation

**Location**: `path/to/implementation.py::ClassName.method_name()`

**Usage in Pipeline**: `path/to/pipeline.py::StepClass`

**Usage in SDK**: `path/to/sdk.py::AnalystClass` (via business rules)

#### Migration Notes

- Notes about the migration
- Differences or improvements
- Testing approach

---

## Migration Checklist

- [ ] Original SQL query documented
- [ ] Business rules extracted and documented
- [ ] Python implementation created in `src/business_rules/`
- [ ] Unit tests written for business rules
- [ ] Pipeline step updated to use business rules
- [ ] SDK updated to use business rules
- [ ] Integration tests verify SQL and Python produce same results
- [ ] Documentation updated
- [ ] Migration marked as complete in status table

