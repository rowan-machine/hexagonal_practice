# SQL to Pandas Converter Guide

Utility for converting SQL queries to pandas operations, helping migrate SQL-based business logic to Python.

## Overview

The SQL to Pandas converter uses `sqlglot` to parse SQL queries into Abstract Syntax Trees (AST) and generates equivalent pandas code. This is particularly useful for:

- **SQL Migration**: Converting legacy SQL queries to Python/pandas
- **Code Generation**: Automatically generating pandas code from SQL
- **Learning Tool**: Understanding how SQL operations map to pandas

## Installation

The converter requires `sqlglot` and `pandas`:

```bash
pip install sqlglot pandas
```

Or install development dependencies:

```bash
pip install -r requirements/requirements-dev.txt
```

## Quick Start

### Command Line Interface

```bash
# Convert SQL file
python scripts/sql_to_pandas_cli.py queries/claims_gold.sql --table claims_silver

# Convert SQL string
python scripts/sql_to_pandas_cli.py --sql "SELECT * FROM claims_silver LIMIT 10" --table claims_silver

# Save output to file
python scripts/sql_to_pandas_cli.py queries/claims_gold.sql --output output.py --table claims_silver
```

### Python API

```python
from src.utils.sql_to_pandas import SQLToPandasConverter

# Create converter
converter = SQLToPandasConverter(source_table="claims_silver")

# Convert SQL to pandas code
sql = """
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count
FROM claims_silver
GROUP BY policy_id
ORDER BY total_claims DESC
"""

pandas_code = converter.convert(sql)
print(pandas_code)
```

### Using Makefile

```bash
# Convert SQL file
make sql-to-pandas SQL_FILE=queries/claims_gold.sql TABLE=claims_silver
```

## Examples

### Example 1: Simple SELECT

**SQL:**
```sql
SELECT policy_id, claim_amount FROM claims_silver
```

**Generated Pandas:**
```python
df = load_dataframe('claims_silver')  # Replace with actual data loading
df = df[['policy_id', 'claim_amount']]
```

### Example 2: SELECT with WHERE

**SQL:**
```sql
SELECT * FROM claims_silver WHERE claim_amount > 1000
```

**Generated Pandas:**
```python
df = load_dataframe('claims_silver')
df = df.query('claim_amount > 1000')
```

### Example 3: GROUP BY with Aggregations

**SQL:**
```sql
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count,
    AVG(claim_amount) AS avg_claim_amount
FROM claims_silver
GROUP BY policy_id
```

**Generated Pandas:**
```python
df = load_dataframe('claims_silver')
df = df.groupby(['policy_id']).agg({
    'claim_amount': 'sum',
    'claim_id': 'count',
    'claim_amount': 'mean'
}).reset_index()
df = df.rename(columns={
    'claim_amount': 'total_claims',
    'claim_id': 'claim_count',
    'claim_amount': 'avg_claim_amount'
})
```

### Example 4: Complex Query (CLAIMS_GOLD_001)

**SQL:**
```sql
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count,
    AVG(claim_amount) AS avg_claim_amount,
    MAX(claim_amount) AS max_claim_amount,
    MIN(claim_amount) AS min_claim_amount
FROM claims_silver
GROUP BY policy_id
ORDER BY total_claims DESC
```

**Generated Pandas:**
```python
df = load_dataframe('claims_silver')
df = df.groupby(['policy_id']).agg({
    'claim_amount': 'sum',
    'claim_id': 'count',
    'claim_amount': 'mean',
    'claim_amount': 'max',
    'claim_amount': 'min'
}).reset_index()
df = df.rename(columns={
    'claim_amount': 'total_claims',
    'claim_id': 'claim_count',
    'claim_amount': 'avg_claim_amount',
    'claim_amount': 'max_claim_amount',
    'claim_amount': 'min_claim_amount'
})
df = df.sort_values(by=['total_claims'], ascending=[False])
```

## Supported SQL Features

### ✅ Supported

- **SELECT**: Column selection
- **FROM**: Table specification
- **WHERE**: Filtering conditions (`=`, `!=`, `>`, `>=`, `<`, `<=`, `AND`, `OR`)
- **GROUP BY**: Grouping operations
- **Aggregations**: `SUM`, `COUNT`, `AVG`, `MAX`, `MIN`, `STD`, `VAR`
- **ORDER BY**: Sorting (ASC/DESC)
- **LIMIT**: Row limiting
- **JOIN**: Inner, Left, Right, Outer joins (basic support)
- **Aliases**: Column aliases in SELECT

### ⚠️ Limited Support

- **Subqueries**: Basic support, may require manual adjustment
- **Window Functions**: Not yet supported
- **CTEs (WITH)**: ✅ Supported - Common Table Expressions are converted to intermediate DataFrames
- **UNION**: Not yet supported
- **HAVING**: Not yet fully supported

### ❌ Not Supported

- **Stored Procedures**: Not applicable
- **Triggers**: Not applicable
- **Views**: Not applicable

## API Reference

### `SQLToPandasConverter`

#### Constructor

```python
SQLToPandasConverter(source_table: Optional[str] = None)
```

**Parameters:**
- `source_table`: Default source table name (can be overridden in `convert()`)

#### Methods

##### `convert()`

```python
convert(
    sql: str,
    source_table: Optional[str] = None,
    df_name: str = "df",
    return_code: bool = True
) -> Union[str, pd.DataFrame]
```

Convert SQL query to pandas code or execute directly.

**Parameters:**
- `sql`: SQL query string
- `source_table`: Source table name (overrides default)
- `df_name`: Name of the pandas DataFrame variable
- `return_code`: If `True`, return code string; if `False`, execute and return DataFrame

**Returns:**
- If `return_code=True`: Python code string
- If `return_code=False`: pandas DataFrame (requires source DataFrame)

**Raises:**
- `ValueError`: If SQL cannot be parsed or converted

##### `convert_file()`

```python
convert_file(
    sql_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    source_table: Optional[str] = None
) -> str
```

Convert SQL file to pandas code.

**Parameters:**
- `sql_file`: Path to SQL file
- `output_file`: Optional path to save Python code
- `source_table`: Source table name

**Returns:**
- Generated pandas code string

## Usage in Migration Workflow

### Step 1: Identify SQL Query

```sql
-- queries/claims_gold.sql
SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims
FROM claims_silver
GROUP BY policy_id
```

### Step 2: Convert to Pandas

```bash
python scripts/sql_to_pandas_cli.py queries/claims_gold.sql --table claims_silver --output output.py
```

### Step 3: Review and Refine

The generated code may need manual adjustments:

1. **Replace data loading**: Update `load_dataframe()` with actual data source
2. **Fix column names**: Ensure column names match your schema
3. **Optimize**: Add performance optimizations if needed
4. **Add error handling**: Add try/except blocks
5. **Add logging**: Add logging for debugging

### Step 4: Integrate into Pipeline

```python
# src/business_rules/aggregations.py
import pandas as pd
from src.utils.database import DatabaseManager

def aggregate_claims_by_policy(db_path: str) -> pd.DataFrame:
    """Aggregate claims by policy (converted from SQL)."""
    db = DatabaseManager(db_path=db_path)
    
    # Load data
    claims = db.query("SELECT * FROM claims_silver")
    df = pd.DataFrame(claims)
    
    # Apply converted pandas operations
    df = df.groupby(['policy_id']).agg({
        'claim_amount': 'sum'
    }).reset_index()
    df = df.rename(columns={'claim_amount': 'total_claims'})
    
    return df
```

## Best Practices

1. **Review Generated Code**: Always review and test generated code
2. **Test Equivalence**: Verify SQL and pandas produce same results
3. **Handle Edge Cases**: Add error handling for edge cases
4. **Performance**: Optimize for large datasets
5. **Documentation**: Document any manual changes made

## Limitations

1. **Not 100% Accurate**: Generated code may need manual adjustments
2. **Complex Queries**: Very complex SQL may not convert perfectly
3. **Data Types**: May need explicit type conversions
4. **Performance**: Generated code may not be optimized

## Troubleshooting

### "Failed to convert SQL"

**Cause**: SQL syntax error or unsupported feature

**Solution**: 
- Check SQL syntax
- Simplify query
- Use supported SQL features only

### "Source table name is required"

**Cause**: Table name not found in SQL or not provided

**Solution**:
- Provide `source_table` parameter
- Ensure SQL contains `FROM table_name`

### "Generated code has syntax errors"

**Cause**: Complex query or edge case

**Solution**:
- Review generated code
- Manually fix syntax errors
- Simplify original SQL query

## Testing

Run tests for the converter:

```bash
# Run all converter tests
pytest src/tests/test_sql_to_pandas.py -v

# Run specific test
pytest src/tests/test_sql_to_pandas.py::TestSQLToPandasConverter::test_claims_gold_query -v
```

## Next Steps

- **[sql_migration/README.md](../sql_migration/README.md)** → SQL migration process
- **[first_sql_conversion/README.md](../first_sql_conversion/README.md)** → First SQL conversion example
- **[docs/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** → Migration guide
- **[src/utils/sql_to_pandas.py](../src/utils/sql_to_pandas.py)** → Source code

