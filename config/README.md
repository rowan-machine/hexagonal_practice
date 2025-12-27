# Configuration Directory

This directory contains all configuration files for the pipeline system.

## Files

### Pipeline Configurations

- **`claims_pipeline.yml`** - Claims processing pipeline configuration
- **`policies_pipeline.yml`** - Policies processing pipeline configuration

See **[PIPELINE_CONFIG_GUIDE.md](PIPELINE_CONFIG_GUIDE.md)** for complete guide to creating and managing pipeline configurations.

### Validation Configuration

- **`validation.yml`** - Data validation rules and expected counts

See **[VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)** for validation system documentation.

## Adding New Pipeline Configurations

1. **Create YAML File**: Create `config/my_new_pipeline.yml`

2. **Follow Structure**: Use the template from [PIPELINE_CONFIG_GUIDE.md](PIPELINE_CONFIG_GUIDE.md)

3. **Test Pipeline**: Run `python scripts/run_local.py my_new_pipeline`

## Next Steps

**Configuration files ready?** Continue with:

1. **[PIPELINE_CONFIG_GUIDE.md](PIPELINE_CONFIG_GUIDE.md)** → Learn to create pipeline configurations
2. **[VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)** → Set up validation rules
3. **[scripts/run_local.py](../scripts/run_local.py)** → Run your pipelines

**Want to understand the system?**

1. **[README.md](../README.md)** → Architecture overview
2. **[docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)** → Design principles
3. **[examples/README.md](../examples/README.md)** → See examples

**Ready to test?**

1. **[scripts/verify_setup.py](../scripts/verify_setup.py)** → Verify configuration
2. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Testing guidelines
3. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup

## Related Documentation

- **[PIPELINE_CONFIG_GUIDE.md](PIPELINE_CONFIG_GUIDE.md)** - Complete pipeline configuration guide
- **[VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)** - Validation system guide
- **[Getting Started](../GETTING_STARTED.md)** - Setup and installation

