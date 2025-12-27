# Pipeline Configuration Guide

This directory contains YAML configuration files that define data pipelines. This guide explains all available options for creating new pipeline configurations.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Pipeline Metadata](#pipeline-metadata)
- [Step Types](#step-types)
- [Execution Settings](#execution-settings)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

## Basic Structure

Every pipeline configuration file follows this structure:

```yaml
pipeline:
  name: <pipeline_name>
  description: "<optional description>"
  
  steps:
    - name: <step_name>
      type: <step_type>
      # ... step-specific configuration ...
  
  execution:
    # ... execution settings ...
```

## Pipeline Metadata

### Required Fields

- **`name`** (string): Unique identifier for the pipeline
  - Used to load the config: `ConfigLoader().create_pipeline_config("pipeline_name")`
  - Should match the filename (without `.yml` extension)
  - Example: `"claims_pipeline"`, `"policies_pipeline"`

### Optional Fields

- **`description`** (string): Human-readable description of the pipeline
  - Used for documentation and logging
  - Example: `"Stop loss insurance claims processing pipeline"`

## Step Types

### 1. Bronze Step (`type: bronze`)

**Purpose**: Raw data ingestion and basic cleaning

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: bronze               # Required: Step type
  source:                    # Required: Data source configuration
    path: "<file_path>"      # Required: Path to source data file
    format: "json"           # Optional: File format (default: "json")
  config:                    # Optional: Step-specific configuration
    basic_cleaning: true     # Optional: Enable basic data cleaning (default: true)
```

**Example:**
```yaml
- name: claims_bronze
  type: bronze
  source:
    path: "data/raw_claims.json"
    format: "json"
  config:
    basic_cleaning: true
```

**Notes:**
- The step name should indicate the data type (e.g., `claims_bronze`, `policies_bronze`)
- Supported formats: `"json"` (others may be added in future)
- Paths are relative to the project root directory

---

### 2. Silver Step (`type: silver`)

**Purpose**: Business rule application and data enrichment

**Configuration Options:**

```yaml
- name: <step_name>                    # Required: Unique step identifier
  type: silver                         # Required: Step type
  domain_handler: <ProcessorClass>     # Optional: Domain processor class name
  config:                              # Optional: Step-specific configuration
    approval_threshold: <number>        # Optional: Approval threshold (for ClaimsProcessor)
    # ... other domain-specific config ...
```

**Available Domain Handlers:**
- `ClaimsProcessor`: Processes claims data
  - Requires `approval_threshold` in config (float)
- `PolicyProcessor`: Processes policies data
  - No additional config required

**Example:**
```yaml
- name: claims_silver
  type: silver
  domain_handler: ClaimsProcessor
  config:
    approval_threshold: 100000.00

# Or for policies:
- name: policies_silver
  type: silver
  domain_handler: PolicyProcessor
  config: {}
```

**Notes:**
- If `domain_handler` is omitted, step will run without business logic processing
- Config options depend on the domain handler used

---

### 3. Gold Step (`type: gold`)

**Purpose**: Data aggregation and summary statistics

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: gold                 # Required: Step type
  aggregation:               # Required: Aggregation configuration
    type: <aggregation_type> # Required: Type of aggregation
    group_by:                # Required: Fields to group by
      - <field_name>
    aggregations:            # Required: Aggregation operations
      <field_name>: <operation>  # Field and operation (sum, count, avg, max, min)
```

**Aggregation Types:**
- `by_policy`: Group by policy_id (for claims)
- `by_employer`: Group by employer_id (for policies)
- `by_member`: Group by member_id
- Custom: Any field name can be used

**Aggregation Operations:**
- `sum`: Sum of values
- `count`: Count of records
- `avg`: Average value
- `max`: Maximum value
- `min`: Minimum value

**Example:**
```yaml
- name: claims_gold
  type: gold
  aggregation:
    type: by_policy
    group_by:
      - policy_id
    aggregations:
      claim_amount: sum
      claim_id: count

# Or for policies:
- name: policies_gold
  type: gold
  aggregation:
    type: by_employer
    group_by:
      - employer_id
    aggregations:
      stop_loss_limit: sum
      policy_id: count
```

**Notes:**
- The step name should indicate the data type (e.g., `claims_gold`, `policies_gold`)
- Multiple fields can be grouped by (list format)
- Multiple aggregations can be specified

---

### 4. Validation Step (`type: validation`)

**Purpose**: Data quality checks and constraint validation

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: validation           # Required: Step type
  data_key: <data_key>       # Optional: Key in context to validate (default: "silver_data")
  config:                    # Optional: Validation rules
    rules:                   # Optional: List of validation rules
      - name: <rule_name>    # Required: Name of validation rule
        severity: <level>    # Required: Severity level (error, warning, info)
```

**Data Keys:**
- `silver_data`: Validate silver layer data (most common)
- `bronze_data`: Validate bronze layer data
- `gold_data`: Validate gold layer data

**Severity Levels:**
- `error`: Pipeline stops if validation fails
- `warning`: Pipeline continues but logs warning
- `info`: Pipeline continues, logs information

**Example:**
```yaml
- name: claims_validation
  type: validation
  data_key: silver_data
  config:
    rules:
      - name: claim_amount_positive
        severity: error
      - name: claim_has_policy
        severity: error
      - name: claim_has_member
        severity: error
```

**Notes:**
- Validation rules are defined in the validation system
- Common rule names: `claim_amount_positive`, `claim_has_policy`, `stop_loss_limit_positive`, `expiration_after_effective`
- See `config/validation.yml` for available validation rules

---

### 5. Aggregation Step (`type: aggregation`)

**Purpose**: Additional aggregation operations (alternative to gold step)

**Configuration Options:**

```yaml
- name: <step_name>              # Required: Unique step identifier
  type: aggregation              # Required: Step type
  source_data_key: <data_key>    # Optional: Source data key (default: "silver_data")
  aggregation:                   # Required: Aggregation configuration
    type: <aggregation_type>     # Required: Type of aggregation
```

**Example:**
```yaml
- name: summary_aggregation
  type: aggregation
  source_data_key: silver_data
  aggregation:
    type: summary
```

**Notes:**
- Less commonly used than gold step
- Used for additional aggregations beyond the main gold layer

---

## Execution Settings

The `execution` section controls how the pipeline runs:

```yaml
execution:
  stop_on_error: <boolean>      # Optional: Stop pipeline on error (default: true)
  skip_completed: <boolean>     # Optional: Skip already completed steps (default: false)
  enable_metrics: <boolean>     # Optional: Enable performance metrics (default: true)
  enable_logging: <boolean>     # Optional: Enable structured logging (default: true)
```

**Options:**

- **`stop_on_error`** (boolean): If `true`, pipeline stops immediately when a step fails. If `false`, pipeline continues and logs errors.
  - Default: `true`
  - Recommended: `true` for production, `false` for debugging

- **`skip_completed`** (boolean): If `true`, steps that have already completed successfully are skipped on re-run.
  - Default: `false`
  - Useful for resuming failed pipelines

- **`enable_metrics`** (boolean): Enable performance metrics collection.
  - Default: `true`
  - Metrics include execution time, record counts, etc.

- **`enable_logging`** (boolean): Enable structured logging.
  - Default: `true`
  - Logs include step execution, errors, warnings

**Example:**
```yaml
execution:
  stop_on_error: true
  skip_completed: false
  enable_metrics: true
  enable_logging: true
```

---

## Complete Examples

### Example 1: Claims Pipeline

```yaml
pipeline:
  name: claims_pipeline
  description: "Stop loss insurance claims processing pipeline"
  
  steps:
    # Step 1: Ingest raw claims data
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
        format: "json"
      config:
        basic_cleaning: true
    
    # Step 2: Apply business rules
    - name: claims_silver
      type: silver
      domain_handler: ClaimsProcessor
      config:
        approval_threshold: 100000.00
    
    # Step 3: Validate data quality
    - name: claims_validation
      type: validation
      data_key: silver_data
      config:
        rules:
          - name: claim_amount_positive
            severity: error
          - name: claim_has_policy
            severity: error
    
    # Step 4: Aggregate by policy
    - name: claims_gold
      type: gold
      aggregation:
        type: by_policy
        group_by:
          - policy_id
        aggregations:
          claim_amount: sum
          claim_id: count
  
  execution:
    stop_on_error: true
    skip_completed: false
    enable_metrics: true
    enable_logging: true
```

### Example 2: Policies Pipeline

```yaml
pipeline:
  name: policies_pipeline
  description: "Stop loss insurance policies processing pipeline"
  
  steps:
    - name: policies_bronze
      type: bronze
      source:
        path: "data/raw_policies.json"
        format: "json"
      config:
        basic_cleaning: true
    
    - name: policies_silver
      type: silver
      domain_handler: PolicyProcessor
      config: {}
    
    - name: policies_validation
      type: validation
      data_key: silver_data
      config:
        rules:
          - name: stop_loss_limit_positive
            severity: error
          - name: expiration_after_effective
            severity: error
    
    - name: policies_gold
      type: gold
      aggregation:
        type: by_employer
        group_by:
          - employer_id
        aggregations:
          stop_loss_limit: sum
          policy_id: count
  
  execution:
    stop_on_error: true
    skip_completed: false
    enable_metrics: true
    enable_logging: true
```

### Example 3: Minimal Pipeline

```yaml
pipeline:
  name: simple_pipeline
  
  steps:
    - name: data_bronze
      type: bronze
      source:
        path: "data/raw_data.json"
    
    - name: data_silver
      type: silver
  
  execution:
    stop_on_error: true
```

---

## Best Practices

### 1. Naming Conventions

- **Pipeline names**: Use lowercase with underscores (e.g., `claims_pipeline`)
- **Step names**: Include data type and layer (e.g., `claims_bronze`, `policies_silver`)
- **File names**: Match pipeline name (e.g., `claims_pipeline.yml`)

### 2. Step Order

Recommended order:
1. **Bronze** - Ingest raw data
2. **Silver** - Apply business rules
3. **Validation** - Validate data quality
4. **Gold** - Aggregate data

### 3. Validation Rules

- Always include validation steps after silver processing
- Use `severity: error` for critical validations
- Use `severity: warning` for non-critical issues

### 4. Aggregation Design

- Group by meaningful business keys (policy_id, employer_id, etc.)
- Include both counts and sums for comprehensive analysis
- Consider multiple aggregation levels if needed

### 5. Error Handling

- Set `stop_on_error: true` for production pipelines
- Use `stop_on_error: false` only for debugging
- Always enable logging for troubleshooting

### 6. Configuration Management

- Keep configs in version control
- Document any custom configurations
- Use descriptive descriptions for each pipeline

---

## Creating a New Pipeline

### Step-by-Step Guide

1. **Create the YAML file:**
   ```bash
   # Create new file: pipelines_config/my_new_pipeline.yml
   ```

2. **Define pipeline metadata:**
   ```yaml
   pipeline:
     name: my_new_pipeline
     description: "Description of what this pipeline does"
   ```

3. **Add bronze step:**
   ```yaml
   steps:
     - name: my_data_bronze
       type: bronze
       source:
         path: "data/raw_my_data.json"
         format: "json"
   ```

4. **Add silver step (if needed):**
   ```yaml
     - name: my_data_silver
       type: silver
       domain_handler: ClaimsProcessor  # or PolicyProcessor, or omit
       config:
         approval_threshold: 100000.00  # if using ClaimsProcessor
   ```

5. **Add validation step:**
   ```yaml
     - name: my_data_validation
       type: validation
       data_key: silver_data
       config:
         rules:
           - name: <validation_rule_name>
             severity: error
   ```

6. **Add gold step (if aggregating):**
   ```yaml
     - name: my_data_gold
       type: gold
       aggregation:
         type: by_policy  # or by_employer, by_member, etc.
         group_by:
           - policy_id
         aggregations:
           amount: sum
           record_id: count
   ```

7. **Add execution settings:**
   ```yaml
   execution:
     stop_on_error: true
     skip_completed: false
     enable_metrics: true
     enable_logging: true
   ```

8. **Test the pipeline:**
   ```bash
   python run_local.py my_new_pipeline
   ```

---

## Troubleshooting

### Common Issues

**Issue: Pipeline config not found**
- Ensure filename matches pipeline name: `{pipeline_name}.yml`
- Check file is in `pipelines_config/` directory

**Issue: Step type not recognized**
- Verify step type is one of: `bronze`, `silver`, `gold`, `validation`, `aggregation`
- Check spelling and indentation

**Issue: Domain handler not found**
- Ensure domain handler name matches exactly: `ClaimsProcessor` or `PolicyProcessor`
- Check that handler is available in the codebase

**Issue: Validation rule not found**
- Check `config/validation.yml` for available rules
- Verify rule name spelling matches exactly

**Issue: Aggregation fails**
- Ensure `group_by` fields exist in the data
- Verify aggregation operations are valid: `sum`, `count`, `avg`, `max`, `min`

---

## Related Documentation

- **[README.md](../README.md)** - Project overview
- **[examples/README.md](../examples/README.md)** - Code examples
- **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** - Design principles
- **[examples/pipeline_example.py](../examples/pipeline_example.py)** - Example usage

---

## Reference: Complete Configuration Schema

```yaml
pipeline:
  name: string                    # Required
  description: string             # Optional
  
  steps:
    - name: string                # Required
      type: bronze|silver|gold|validation|aggregation  # Required
      
      # Bronze step options:
      source:
        path: string              # Required for bronze
        format: string            # Optional (default: "json")
      config:
        basic_cleaning: boolean   # Optional (default: true)
      
      # Silver step options:
      domain_handler: string      # Optional (ClaimsProcessor|PolicyProcessor)
      config:
        approval_threshold: number # Optional (for ClaimsProcessor)
      
      # Gold step options:
      aggregation:
        type: string              # Required for gold
        group_by:                 # Required for gold
          - string
        aggregations:             # Required for gold
          field_name: operation   # sum|count|avg|max|min
      
      # Validation step options:
      data_key: string            # Optional (default: "silver_data")
      config:
        rules:                    # Optional
          - name: string          # Required
            severity: string      # Required (error|warning|info)
      
      # Aggregation step options:
      source_data_key: string     # Optional (default: "silver_data")
      aggregation:
        type: string              # Required
  
  execution:
    stop_on_error: boolean        # Optional (default: true)
    skip_completed: boolean       # Optional (default: false)
    enable_metrics: boolean       # Optional (default: true)
    enable_logging: boolean       # Optional (default: true)
```

