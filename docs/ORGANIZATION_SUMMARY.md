# Project Organization Summary

This document summarizes the recent organization improvements to the project structure.

## Changes Made

### 1. Scripts Organization

**Before:** Helper scripts were scattered in the root directory
**After:** All scripts organized in `scripts/` directory

**Moved Files:**
- `run_local.py` → `scripts/run_local.py`
- `verify_*.py` → `scripts/verify_*.py`
- `publish_*.py` → `scripts/publish_*.py`
- `mock_atlas.py` → `scripts/mock_atlas.py`

**Documentation:** `scripts/README.md` - Complete guide to all scripts

### 2. Requirements Organization

**Before:** Requirements files in root directory
**After:** All requirements files in `requirements/` directory

**Moved Files:**
- `requirements.txt` → `requirements/requirements.txt`
- `requirements-dev.txt` → `requirements/requirements-dev.txt`
- `requirements-airflow.txt` → `requirements/requirements-airflow.txt`

**Documentation:** `requirements/README.md` - Dependency management guide

### 3. Configuration Consolidation

**Before:** Pipeline configs in `pipelines_config/`, validation in `config/`
**After:** All configuration files in `config/` directory

**Moved Files:**
- `pipelines_config/claims_pipeline.yml` → `config/claims_pipeline.yml`
- `pipelines_config/policies_pipeline.yml` → `config/policies_pipeline.yml`
- `pipelines_config/README.md` → `config/PIPELINE_CONFIG_GUIDE.md` (consolidated)

**Updated:**
- Default config directory changed from `pipelines_config` to `config`
- All code references updated
- Documentation consolidated

**Documentation:**
- `config/README.md` - Configuration directory overview
- `config/PIPELINE_CONFIG_GUIDE.md` - Complete pipeline configuration guide
- `config/VALIDATION_GUIDE.md` - Validation system guide

### 4. Migration Documentation Consolidation

**Before:** Two separate migration documents
**After:** Consolidated into single comprehensive guide

**Changes:**
- `sql_migration/README.md` - Now contains complete migration guide (consolidated from README.md + MIGRATION_PROCESS.md)
- `sql_migration/MIGRATION_PROCESS.md` → Archived to `docs/archive/`

**Benefits:**
- Single source of truth for migration process
- Easier to find and follow
- Less confusion about which document to read

### 5. Schemas Documentation

**New:** `schemas/README.md` - Complete documentation for data schemas

**Includes:**
- Schema structure and format
- Field types and validation rules
- Usage examples
- Best practices

## Updated References

All documentation has been updated to reference the new locations:

- **Scripts**: `python scripts/run_local.py` (instead of `python run_local.py`)
- **Requirements**: `pip install -r requirements/requirements.txt` (instead of `pip install -r requirements.txt`)
- **Config**: `config/` directory (instead of `pipelines_config/`)
- **Migration**: `sql_migration/README.md` (single comprehensive guide)

## Benefits

1. **Cleaner Root Directory**: Only essential files in root
2. **Better Organization**: Related files grouped together
3. **Easier Navigation**: Clear directory structure
4. **Less Confusion**: Single source of truth for each topic
5. **Better Documentation**: Each directory has its own README
6. **Consolidated Config**: All configuration in one place

## Directory Structure

```
hexagonal_practice/
├── scripts/              # Helper scripts
│   ├── run_local.py
│   ├── verify_*.py
│   ├── publish_*.py
│   └── README.md
├── requirements/         # Dependency files
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── requirements-airflow.txt
│   └── README.md
├── config/               # All configuration files (CONSOLIDATED)
│   ├── claims_pipeline.yml
│   ├── policies_pipeline.yml
│   ├── validation.yml
│   ├── README.md
│   ├── PIPELINE_CONFIG_GUIDE.md
│   └── VALIDATION_GUIDE.md
├── schemas/              # Data schemas
│   ├── claims.yml
│   ├── policies.yml
│   └── README.md
├── sql_migration/       # SQL migration docs
│   ├── README.md        # CONSOLIDATED
│   └── ...
└── ...
```

## Migration Guide

If you have existing scripts or documentation referencing old paths:

1. **Scripts**: Update to use `scripts/` prefix
   - `python run_local.py` → `python scripts/run_local.py`

2. **Requirements**: Update to use `requirements/` prefix
   - `pip install -r requirements.txt` → `pip install -r requirements/requirements.txt`

3. **Config**: Update to use `config/` directory
   - `pipelines_config/` → `config/`
   - `ConfigLoader(config_dir="pipelines_config")` → `ConfigLoader(config_dir="config")`

4. **Migration Docs**: Use `sql_migration/README.md` as the single source

## Code Changes

### Default Config Directory

**Before:**
```python
ConfigLoader(config_dir="pipelines_config")
```

**After:**
```python
ConfigLoader(config_dir="config")  # Default is now "config"
```

### Pipeline Config Files

**Before:**
- `pipelines_config/claims_pipeline.yml`
- `pipelines_config/policies_pipeline.yml`

**After:**
- `config/claims_pipeline.yml`
- `config/policies_pipeline.yml`

## Next Steps

**Understood the organization?** Start using the new structure:

1. **[scripts/README.md](../scripts/README.md)** → Use organized scripts
2. **[requirements/README.md](../requirements/README.md)** → Manage dependencies
3. **[config/README.md](../config/README.md)** → Configure pipelines

**Ready to develop?**

1. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup guide
2. **[examples/README.md](../examples/README.md)** → Run examples
3. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Follow best practices

**Migrating from old structure?**

1. Review [Migration Guide](#migration-guide) section above
2. **[README.md](../README.md)** → Updated quick reference
3. **[docs/README.md](README.md)** → Complete documentation index

## Related Documentation

- **[scripts/README.md](../scripts/README.md)** - Scripts documentation
- **[requirements/README.md](../requirements/README.md)** - Requirements documentation
- **[config/README.md](../config/README.md)** - Configuration directory overview
- **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** - Pipeline configuration guide
- **[schemas/README.md](../schemas/README.md)** - Schemas documentation
- **[sql_migration/README.md](../sql_migration/README.md)** - Migration guide
