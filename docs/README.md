# Documentation Index

This is the **documentation navigation hub** for the project. Use this to find specific documentation.

> **📖 New to the project?** Start with [README.md](../README.md) - Project overview and quick start  
> **🔍 Looking for something specific?** Use the sections below to find what you need

## 📖 Where to Start

**New to the project?** Follow this sequence:

1. **[README.md](../README.md)** - ⭐ **Start here!** Project overview and quick start
2. **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Setup and installation guide
3. **[DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - ⭐ Understand all project files and tools
4. **[examples/README.md](../examples/README.md)** - Code examples and usage patterns
5. **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Detailed design principles (for engineers)

> **Note**: This is a documentation **index**. For project overview, see [README.md](../README.md).

## 📚 Documentation by Topic

### Getting Started
- **[README.md](../README.md)** - Main project documentation
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Step-by-step setup guide
- **[PIPENV_GUIDE.md](PIPENV_GUIDE.md)** - Complete Pipenv usage guide

### Architecture & Design
- **[README.md](../README.md)** → Architecture Overview section
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Detailed design principles and patterns
- **[examples/README.md](../examples/README.md)** - Code examples and usage patterns

### Development
- **[DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - ⭐ Complete guide to project files and tools
- **[GIT_WORKFLOW.md](GIT_WORKFLOW.md)** - ⭐ Git branching strategy and CI/CD workflow
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - ⭐ Complete best practices guide
- **[SDK_API_REFERENCE.md](SDK_API_REFERENCE.md)** - ⭐ Complete SDK API reference
- **[TESTING.md](../src/tests/TESTING.md)** - Testing strategy and guidelines
- **[TESTING_CHECKLIST.md](../src/tests/TESTING_CHECKLIST.md)** - Verification checklist
- **[VALIDATION_GUIDE.md](../config/VALIDATION_GUIDE.md)** - Data validation system

### Infrastructure
- **[DOCKER.md](../DOCKER.md)** - ⭐ Complete Docker and Docker Compose guide (setup, usage, troubleshooting)
- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Environment variable configuration

### Data Governance
- **[ATLAS_GUIDE.md](ATLAS_GUIDE.md)** - Complete Apache Atlas guide
- **[ATLAS_PUBLISHING.md](ATLAS_PUBLISHING.md)** - How to publish metadata
- **[ATLAS_QUICK_REFERENCE.md](ATLAS_QUICK_REFERENCE.md)** - Quick reference
- **[ATLAS_TROUBLESHOOTING.md](ATLAS_TROUBLESHOOTING.md)** - Atlas troubleshooting

### Migration
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - ⭐ Agile/incremental migration guide
- **[../sql_migration/README.md](../sql_migration/README.md)** - SQL migration overview
- **[../sql_migration/README.md](../sql_migration/README.md)** - Complete SQL migration guide (consolidated)

### SQL Conversion
- **[../first_sql_conversion/README.md](../first_sql_conversion/README.md)** - First SQL conversion example

### Examples
- **[../examples/README.md](../examples/README.md)** - Complete examples guide (runnable examples + code snippets)

### Pipeline Configuration
- **[../config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** - Complete guide to creating pipeline YAML configurations

## 👥 Documentation by Role

### For Analysts
1. **[notebooks/ANALYST_GUIDE.md](../notebooks/ANALYST_GUIDE.md)** → ⭐ Complete analyst guide
2. **[SDK_API_REFERENCE.md](SDK_API_REFERENCE.md)** → ⭐ Complete SDK API reference
3. **[examples/README.md](../examples/README.md)** → SDK Examples section
4. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Database section
5. **Notebooks**: `../notebooks/analyst_*.ipynb`

### For Engineers
1. **[README.md](../README.md)** → Architecture Overview section
2. **[GIT_WORKFLOW.md](GIT_WORKFLOW.md)** → ⭐ Git workflow and CI/CD
3. **[examples/README.md](../examples/README.md)** → Pipeline Examples section
4. **[TESTING.md](../TESTING.md)** - Testing guidelines
5. **[VALIDATION_GUIDE.md](../VALIDATION_GUIDE.md)** - Validation system

### For DevOps
1. **[DOCKER.md](../DOCKER.md)** - Complete Docker guide (setup, usage, troubleshooting)
2. **[../airflow/dags/README.md](../airflow/dags/README.md)** - Airflow documentation

### For Project Managers
1. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - ⭐ Migration strategy
2. **[CHANGELOG.md](../CHANGELOG.md)** - Version history
3. **[docs/archive/](archive/)** - Release-specific documentation

## 🗂️ Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── DEVELOPER_ONBOARDING.md     # ⭐ Complete guide to project files and tools
├── GIT_WORKFLOW.md             # ⭐ Git branching strategy and CI/CD
├── MIGRATION_GUIDE.md          # ⭐ Agile migration guide
├── BEST_PRACTICES.md           # Complete best practices guide
├── SDK_API_REFERENCE.md        # Complete SDK API reference
├── DESIGN_PRINCIPLES.md        # Detailed design principles
├── ATLAS_GUIDE.md              # Complete Atlas guide
├── ATLAS_PUBLISHING.md         # Atlas publishing how-to
├── ATLAS_QUICK_REFERENCE.md    # Atlas quick reference
├── ATLAS_TROUBLESHOOTING.md    # Atlas troubleshooting
└── archive/                    # Archived release-specific docs
    ├── CODE_REVIEW_v0.0.1.md
    ├── RELEASE_NOTES_v0.0.1.md
    └── ...
```

## 🔍 Quick Reference

### Common Tasks

**Setting up locally:**
→ [GETTING_STARTED.md](../GETTING_STARTED.md) (includes database setup)

**Understanding architecture:**
→ [README.md](../README.md) → Architecture Overview

**Running pipelines:**
→ [README.md](../README.md) → Running Locally section

**Using the SDK:**
→ [examples/README.md](../examples/README.md) → SDK Examples section

**Migrating from SQL:**
→ [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

**Converting SQL to Python:**
→ [../first_sql_conversion/README.md](../first_sql_conversion/README.md)

**Setting up Docker:**
→ [DOCKER.md](../DOCKER.md)

**Troubleshooting:**
→ [DOCKER.md](../DOCKER.md) → Troubleshooting section or [ATLAS_TROUBLESHOOTING.md](ATLAS_TROUBLESHOOTING.md)

## 📝 Documentation Standards

All documentation follows these principles:
- **Single source of truth** - Each topic has one primary document
- **Clear navigation** - Easy to find what you need
- **Role-based organization** - Organized by user needs
- **Progressive disclosure** - Start simple, go deeper as needed
- **Examples included** - Code examples in every guide
- **Next Steps** - Every document links to related documentation

## Next Steps

**Found what you need?** Each document has a "Next Steps" section linking to related content.

**New to the project?** Start here:

1. **[README.md](../README.md)** → Project overview
2. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Setup guide
3. **[DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** → ⭐ Understand project files and tools
4. **[examples/README.md](../examples/README.md)** → Examples

**Looking for something specific?**

- **Project Files**: [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)
- **Architecture**: [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- **Migration**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Best Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Atlas**: [ATLAS_GUIDE.md](ATLAS_GUIDE.md)
- **Docker**: [../DOCKER.md](../DOCKER.md)

**Want to understand navigation?**

1. **[NAVIGATION_GUIDE.md](NAVIGATION_GUIDE.md)** → Complete navigation guide
2. **[ROOT_DOCUMENTATION.md](ROOT_DOCUMENTATION.md)** → Root directory organization
3. **[DOCUMENTATION_CLEANUP_SUMMARY.md](DOCUMENTATION_CLEANUP_SUMMARY.md)** → Documentation cleanup summary

