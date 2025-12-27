# Data Schemas

This directory contains YAML schema definitions for data structures used throughout the pipeline system.

## Overview

Schemas define the structure, types, validation rules, and constraints for data entities (claims, policies, etc.). These schemas serve as:

- **Documentation**: Clear definition of data structures
- **Validation Reference**: Rules for data quality checks
- **Type Definitions**: Field types and constraints
- **Business Rules**: Allowed values and validation rules

## Schema Files

### `claims.yml`

Defines the schema for insurance claims data.

**Key Fields:**
- `claim_id` (string, required): Unique claim identifier
- `policy_id` (string, required): Policy identifier
- `member_id` (string, required): Member identifier
- `claim_amount` (decimal, required): Claim amount in dollars (min: 0)
- `incurred_date` (datetime, required): Date claim was incurred
- `paid_date` (datetime, optional): Date claim was paid
- `status` (string, required): Claim status (pending, approved, denied, paid)
- `claim_type` (string, optional): Type of claim (medical, pharmacy, dental, vision)

**Usage:**
```python
# Schema can be used for validation
from pathlib import Path
import yaml

schema_path = Path("schemas/claims.yml")
with open(schema_path) as f:
    schema = yaml.safe_load(f)
    
# Validate data against schema
# (Implementation depends on validation library)
```

### `policies.yml`

Defines the schema for insurance policies data.

**Key Fields:**
- `policy_id` (string, required): Unique policy identifier
- `employer_id` (string, required): Employer identifier
- `effective_date` (datetime, required): Policy effective date
- `expiration_date` (datetime, required): Policy expiration date
- `stop_loss_limit` (decimal, required): Stop loss coverage limit (min: 0)
- `aggregate_deductible` (decimal, required): Aggregate deductible amount (min: 0)
- `specific_deductible` (decimal, required): Specific deductible amount (min: 0)
- `status` (string, required): Policy status (active, inactive, expired, cancelled)

**Usage:**
```python
# Schema can be used for validation
from pathlib import Path
import yaml

schema_path = Path("schemas/policies.yml")
with open(schema_path) as f:
    schema = yaml.safe_load(f)
    
# Validate data against schema
```

## Schema Structure

Each schema file follows this structure:

```yaml
schema:
  name: <entity_name>
  version: "<version_number>"
  
  fields:
    - name: <field_name>
      type: <field_type>  # string, decimal, datetime, etc.
      required: <true|false>
      description: "<field description>"
      validation:
        min: <minimum_value>  # Optional
        max: <maximum_value>  # Optional
      allowed_values:  # Optional
        - value1
        - value2
      default: <default_value>  # Optional
```

## Field Types

Supported field types:
- **string**: Text data
- **decimal**: Numeric data with decimal precision (for money amounts)
- **datetime**: Date and time values (ISO 8601 format)
- **integer**: Whole numbers
- **boolean**: True/false values

## Validation Rules

### Required Fields
Fields marked as `required: true` must be present in the data.

### Type Validation
Fields must match their declared type. Type coercion may be applied during data loading.

### Value Constraints
- **min/max**: Numeric fields can specify minimum and maximum values
- **allowed_values**: String fields can restrict to specific allowed values
- **default**: Optional fields can specify default values

### Examples

**Decimal with minimum:**
```yaml
- name: claim_amount
  type: decimal
  required: true
  validation:
    min: 0
```

**String with allowed values:**
```yaml
- name: status
  type: string
  required: true
  allowed_values:
    - pending
    - approved
    - denied
    - paid
```

**Optional field with default:**
```yaml
- name: claim_type
  type: string
  required: false
  default: "medical"
  allowed_values:
    - medical
    - pharmacy
    - dental
    - vision
```

## Using Schemas

### In Pipeline Steps

Schemas can be referenced during data validation:

```python
from pathlib import Path
import yaml
from src.mixins.validation import ValidationMixin

class MyStep(ValidationMixin):
    def validate_data(self, data: List[Dict]) -> bool:
        schema_path = Path("schemas/claims.yml")
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        
        # Validate each record against schema
        for record in data:
            if not self._validate_record(record, schema):
                return False
        return True
```

### In SDK

Schemas can guide SDK method behavior:

```python
from pathlib import Path
import yaml

def load_claims_with_validation(file_path: str) -> List[Dict]:
    # Load schema
    schema_path = Path("schemas/claims.yml")
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    
    # Load and validate data
    claims = load_claims(file_path)
    return validate_against_schema(claims, schema)
```

### In Documentation

Schemas serve as authoritative documentation for:
- Data structure
- Field requirements
- Validation rules
- Business constraints

## Adding New Schemas

1. **Create Schema File**: Create `<entity_name>.yml` in `schemas/` directory

2. **Define Structure**:
   ```yaml
   schema:
     name: <entity_name>
     version: "1.0"
     fields:
       - name: <field_name>
         type: <type>
         required: <true|false>
         description: "<description>"
   ```

3. **Document Fields**: Include descriptions for all fields

4. **Add Validation**: Specify validation rules where applicable

5. **Update Documentation**: Reference schema in relevant documentation

## Schema Versioning

- **Version Format**: Semantic versioning (e.g., "1.0", "1.1", "2.0")
- **Breaking Changes**: Increment major version (e.g., 1.0 → 2.0)
- **Non-Breaking Changes**: Increment minor version (e.g., 1.0 → 1.1)
- **Documentation**: Document version changes in schema comments

## Next Steps

**Defined your schemas?** Continue with:

1. **[config/VALIDATION_GUIDE.md](../config/VALIDATION_GUIDE.md)** → Use schemas for validation
2. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create pipelines using these schemas
3. **[examples/README.md](../examples/README.md)** → See schemas in use

**Migrating from SQL?**

1. **[sql_migration/README.md](../sql_migration/README.md)** → Document schemas during migration
2. **[docs/MIGRATION_GUIDE.md](../docs/MIGRATION_GUIDE.md)** → Migration strategy
3. **[first_sql_conversion/README.md](../first_sql_conversion/README.md)** → First conversion example

**Want to validate data?**

1. **[config/VALIDATION_GUIDE.md](../config/VALIDATION_GUIDE.md)** → Set up validation rules
2. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Test schema validation

## Related Documentation

- **[Validation Guide](../config/VALIDATION_GUIDE.md)** - Data validation system
- **[Design Principles](../docs/DESIGN_PRINCIPLES.md)** - Architecture and design
- **[Examples](../examples/README.md)** - Code examples

## Best Practices

1. **Keep Schemas Simple**: Focus on structure and constraints
2. **Document Everything**: Include descriptions for all fields
3. **Validate Early**: Use schemas during data ingestion
4. **Version Changes**: Track schema evolution
5. **Consistency**: Ensure schemas match actual data structures
6. **Reusability**: Design schemas to be reusable across pipelines

