# Documentation Structure

This document describes the final, consolidated documentation structure following software development best practices.

## Documentation Organization Principles

1. **Single Source of Truth**: Each topic has one primary document
2. **Progressive Disclosure**: Start simple, go deeper as needed
3. **Role-Based Organization**: Organized by user needs
4. **Directory-Based**: README.md in each directory is the primary doc
5. **Clear Navigation**: Easy to find what you need

## Root Level Documentation

### Primary Entry Points

- **`README.md`** - Main project documentation
  - Quick start
  - Architecture overview
  - Installation
  - Usage examples
  - Links to all other documentation

- **`GETTING_STARTED.md`** - Complete setup guide
  - Environment setup
  - Installation
  - First pipeline run
  - SDK usage
  - Database setup and usage (consolidated from README_DATABASE.md)
  - Troubleshooting

- **`DOCKER.md`** - Complete Docker guide
  - Quick start
  - Services overview
  - Configuration
  - Usage
  - Troubleshooting
  - Best practices
  - Production deployment

- **`CHANGELOG.md`** - Version history

## Directory Documentation

### `examples/README.md`

Complete examples guide (consolidated from examples/README.md + EXAMPLES.md):
- Runnable examples (pipeline_example.py, sdk_example.py)
- Code snippets and patterns
- Common use cases
- Troubleshooting

### `config/PIPELINE_CONFIG_GUIDE.md`

Pipeline configuration guide:
- YAML configuration options
- Step types and options
- Complete examples
- Best practices
- Troubleshooting

### `docs/README.md`

Complete documentation index:
- Organized by topic
- Organized by role
- Quick reference
- Links to all documentation

### `docs/` - Detailed Documentation

- **`DESIGN_PRINCIPLES.md`** - Detailed design principles and patterns
- **`MIGRATION_GUIDE.md`** - Agile/incremental migration guide
- **`ATLAS_*.md`** - Apache Atlas documentation
- **`ROOT_DOCS_ORGANIZATION.md`** - Root directory documentation organization
- **`DOCUMENTATION_STRUCTURE.md`** - This file

### `sql_migration/` - SQL Migration

- **`README.md`** - SQL migration overview
- **`sql_migration/README.md`** - Complete migration guide (consolidated)
- **`sql_migration_tracker.md`** - Migration tracker

### `first_sql_conversion/` - SQL Conversion Example

- **`README.md`** - First SQL conversion guide
- Example files and notebook

## Documentation Flow

### For New Users

```
README.md
  ↓
GETTING_STARTED.md
  ↓
examples/README.md
  ↓
docs/DESIGN_PRINCIPLES.md (if needed)
```

### For Analysts

```
README.md
  ↓
examples/README.md → SDK Examples
  ↓
GETTING_STARTED.md → Database section
  ↓
notebooks/analyst_*.ipynb
```

### For Engineers

```
README.md → Architecture Overview
  ↓
docs/DESIGN_PRINCIPLES.md
  ↓
examples/README.md → Pipeline Examples
  ↓
config/PIPELINE_CONFIG_GUIDE.md
```

### For DevOps

```
DOCKER.md
  ↓
docker-compose.yml
  ↓
airflow/dags/README.md
```

## Consolidated Files

The following files have been consolidated:

1. **`examples/EXAMPLES.md`** → **`examples/README.md`**
   - All examples documentation now in one place
   - Runnable examples + code snippets combined

2. **`README_DATABASE.md`** → **`GETTING_STARTED.md`**
   - Database setup and usage is part of getting started
   - Integrated into Step 6: Understanding the Database

3. **`DOCKER_SETUP.md` + `DOCKER_TROUBLESHOOTING.md`** → **`DOCKER.md`**
   - All Docker documentation in one comprehensive guide

4. **`ARCHITECTURE.md`** → **`README.md` + `docs/DESIGN_PRINCIPLES.md`**
   - Architecture overview in README.md
   - Detailed principles in docs/DESIGN_PRINCIPLES.md

## Best Practices Followed

1. **README.md in directories**: Primary documentation for each directory
2. **Single entry point**: README.md is the main entry point
3. **Progressive disclosure**: Quick start → Details → Deep dive
4. **No redundancy**: Each topic has one primary document
5. **Clear naming**: Standard naming conventions (README.md, not EXAMPLES.md)
6. **Logical grouping**: Related topics grouped together
7. **Role-based organization**: Easy to find docs by role

## File Naming Conventions

- **`README.md`**: Primary documentation in each directory
- **`GETTING_STARTED.md`**: Setup and installation guide
- **`DOCKER.md`**: Docker and Docker Compose guide
- **`CHANGELOG.md`**: Version history
- **`docs/*.md`**: Detailed topic-specific documentation
- **`*_GUIDE.md`**: Comprehensive guides
- **`*_TROUBLESHOOTING.md`**: Troubleshooting guides (in docs/)

## Archived Documentation

Historical and release-specific documentation is archived in:
- **`docs/archive/`** - Release-specific docs, old versions, historical references

## Quick Reference

**Start Here:**
- `README.md` - Project overview

**Setup:**
- `GETTING_STARTED.md` - Complete setup guide

**Examples:**
- `examples/README.md` - All examples and code snippets

**Docker:**
- `DOCKER.md` - Complete Docker guide

**Configuration:**
- `config/PIPELINE_CONFIG_GUIDE.md` - Pipeline configuration

**Deep Dive:**
- `docs/README.md` - Complete documentation index
- `docs/DESIGN_PRINCIPLES.md` - Design principles
- `docs/MIGRATION_GUIDE.md` - Migration strategy

## Next Steps

**Understood the structure?** Navigate to:

1. **[README.md](../README.md)** → Start with the main documentation
2. **[docs/README.md](README.md)** → Complete documentation index
3. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Begin setup

**Looking for something specific?**

- **Setup**: [GETTING_STARTED.md](../GETTING_STARTED.md)
- **Examples**: [examples/README.md](../examples/README.md)
- **Architecture**: [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- **Migration**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Best Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md)

