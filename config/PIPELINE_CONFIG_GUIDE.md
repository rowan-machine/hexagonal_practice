# Pipeline Configuration Guide

Complete guide to creating and managing YAML pipeline configurations.

> **Note:** This guide was consolidated from `pipelines_config/README.md` into the `config/` directory for better organization.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Pipeline Metadata](#pipeline-metadata)
- [Step Types](#step-types)
- [Execution Settings](#execution-settings)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)
- [Step-by-Step Guide](#step-by-step-guide)
- [Troubleshooting](#troubleshooting)
- [Reference Schema](#reference-schema)

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

### 2. Silver Step (`type: silver`)

**Purpose**: Apply business logic and domain rules

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: silver               # Required: Step type
  config:                   # Optional: Step-specific configuration
    approval_threshold: 100000.00  # Optional: Business rule threshold
    # ... other business rule parameters ...
```

**Example:**
```yaml
- name: claims_silver
  type: silver
  config:
    approval_threshold: 100000.00
```

### 3. Gold Step (`type: gold`)

**Purpose**: Aggregation and summarization

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: gold                 # Required: Step type
  config:                   # Optional: Aggregation configuration
    aggregation_key: "policy_id"  # Optional: Key for grouping
    # ... other aggregation parameters ...
```

**Example:**
```yaml
- name: claims_gold
  type: gold
  config:
    aggregation_key: "policy_id"
```

### 4. Validation Step (`type: validation`)

**Purpose**: Validate data quality and counts

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: validation            # Required: Step type
  config:                    # Required: Validation configuration
    validation_file: "config/validation.yml"  # Path to validation config
    expected_count: 12        # Optional: Expected record count
```

**Example:**
```yaml
- name: claims_validation
  type: validation
  config:
    validation_file: "config/validation.yml"
    expected_count: 12
```

### 5. Aggregation Step (`type: aggregation`)

**Purpose**: Custom aggregation logic

**Configuration Options:**

```yaml
- name: <step_name>          # Required: Unique step identifier
  type: aggregation          # Required: Step type
  config:                   # Required: Aggregation configuration
    aggregation_function: "sum"  # Aggregation function
    group_by: "policy_id"    # Grouping key
```

## Execution Settings

### Stop on Error

```yaml
execution:
  stop_on_error: true  # Stop pipeline if any step fails (default: true)
```

### Skip Completed Steps

```yaml
execution:
  skip_completed: false  # Skip steps that already completed (default: false)
```

## Complete Examples

### Claims Pipeline

```yaml
pipeline:
  name: claims_pipeline
  description: "Stop loss insurance claims processing pipeline"
  
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
        format: "json"
    
    - name: claims_silver
      type: silver
      config:
        approval_threshold: 100000.00
    
    - name: claims_gold
      type: gold
      config:
        aggregation_key: "policy_id"
    
    - name: claims_validation
      type: validation
      config:
        validation_file: "config/validation.yml"
  
  execution:
    stop_on_error: true
    skip_completed: false
```

### Policies Pipeline

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
    
    - name: policies_silver
      type: silver
    
    - name: policies_gold
      type: gold
      config:
        aggregation_key: "employer_id"
  
  execution:
    stop_on_error: true
```

## Best Practices

1. **Naming Convention**: Use descriptive names (e.g., `claims_pipeline`, not `pipeline1`)
2. **Descriptions**: Always include a description for documentation
3. **Step Names**: Use consistent naming (e.g., `{entity}_{layer}`)
4. **File Organization**: Keep all configs in `config/` directory
5. **Validation**: Include validation steps for data quality
6. **Error Handling**: Configure `stop_on_error` appropriately
7. **Documentation**: Document any custom business rules in config comments

## Step-by-Step Guide

### Creating a New Pipeline

1. **Create YAML File**: Create `config/my_new_pipeline.yml`

2. **Define Pipeline Metadata**:
   ```yaml
   pipeline:
     name: my_new_pipeline
     description: "Description of what this pipeline does"
   ```

3. **Add Bronze Step**:
   ```yaml
   steps:
     - name: my_bronze
       type: bronze
       source:
         path: "data/my_data.json"
   ```

4. **Add Silver Step**:
   ```yaml
     - name: my_silver
       type: silver
       config:
         # Add business rule parameters
   ```

5. **Add Gold Step** (if needed):
   ```yaml
     - name: my_gold
       type: gold
       config:
         aggregation_key: "my_key"
   ```

6. **Add Validation** (recommended):
   ```yaml
     - name: my_validation
       type: validation
       config:
         validation_file: "config/validation.yml"
   ```

7. **Configure Execution**:
   ```yaml
   execution:
     stop_on_error: true
   ```

8. **Test Pipeline**:
   ```bash
   python scripts/run_local.py my_new_pipeline
   ```

## Troubleshooting

### Pipeline Not Found

**Error:** `FileNotFoundError: Pipeline config not found`

**Solution:**
- Check file is in `config/` directory
- Verify filename matches pipeline name (e.g., `claims_pipeline.yml` for `claims_pipeline`)
- Check file extension is `.yml` (not `.yaml`)

### Invalid Configuration

**Error:** `KeyError` or validation errors

**Solution:**
- Verify YAML syntax is correct
- Check all required fields are present
- Validate against reference schema below

### Step Execution Fails

**Error:** Step fails during execution

**Solution:**
- Check step configuration matches step type requirements
- Verify source data files exist (for bronze steps)
- Check business rule parameters are valid

## Reference Schema

### Complete Pipeline Schema

```yaml
pipeline:
  name: string              # Required: Pipeline identifier
  description: string        # Optional: Pipeline description
  
  steps:
    - name: string          # Required: Step identifier
      type: string          # Required: bronze|silver|gold|validation|aggregation
      source:              # Required for bronze steps
        path: string       # Required: Source file path
        format: string     # Optional: File format (default: "json")
      config:              # Optional: Step-specific configuration
        # ... step-specific options ...
  
  execution:
    stop_on_error: boolean  # Optional: Stop on error (default: true)
    skip_completed: boolean # Optional: Skip completed steps (default: false)
```

### Step Type Requirements

- **bronze**: Requires `source.path`
- **silver**: Optional `config` for business rules
- **gold**: Optional `config` for aggregation settings
- **validation**: Requires `config.validation_file`
- **aggregation**: Requires `config` with aggregation parameters

## Next Steps

**Created your pipeline?** Continue with:

1. **[examples/README.md](../examples/README.md)** → See pipeline examples in action
2. **[VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)** → Add validation to your pipeline
3. **[scripts/README.md](../scripts/README.md)** → Run your pipeline with scripts

**Want to understand the architecture?**

1. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Learn design patterns
2. **[README.md](../README.md)** → Architecture overview
3. **[docs/BEST_PRACTICES.md](../docs/BEST_PRACTICES.md)** → Follow best practices

**Ready to test?**

1. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Testing guidelines
2. **[scripts/verify_setup.py](../scripts/verify_setup.py)** → Verify your configuration

## Related Documentation

- **[Validation Guide](VALIDATION_GUIDE.md)** - Data validation system
- **[Getting Started](../GETTING_STARTED.md)** - Setup and installation
- **[Examples](../examples/README.md)** - Code examples
- **[Design Principles](../docs/DESIGN_PRINCIPLES.md)** - Architecture details

