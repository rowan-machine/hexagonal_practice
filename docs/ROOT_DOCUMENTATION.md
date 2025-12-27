# Root Directory Documentation Organization

This document explains the organization of documentation files between the root directory and `docs/`.

## Root Directory Files (Essential Only)

These files stay in root as they are standard project entry points:

### Core Project Files
- **`README.md`** - Main project entry point, overview, quick start, architecture summary
- **`CHANGELOG.md`** - Version history (standard location)
- **`CONTRIBUTING.md`** - Contribution guidelines (standard location)
- **`LICENSE`** - Project license (standard location)
- **`SECURITY.md`** - Security policy (standard location)

### Getting Started
- **`GETTING_STARTED.md`** - Step-by-step setup guide for new developers

### Infrastructure
- **`DOCKER.md`** - Complete Docker and Docker Compose guide

## Documentation Directory (`docs/`)

All detailed documentation lives in `docs/`:

### Navigation
- **`docs/README.md`** - ⭐ Documentation index and navigation hub

### Guides
- **`docs/DEVELOPER_ONBOARDING.md`** - Complete developer onboarding
- **`docs/DESIGN_PRINCIPLES.md`** - Architecture and design details
- **`docs/MIGRATION_GUIDE.md`** - SQL migration guide
- **`docs/PIPENV_GUIDE.md`** - Pipenv usage guide
- **`docs/ENVIRONMENT_VARIABLES.md`** - Environment variable reference

### Specialized Documentation
- **`docs/ATLAS_*.md`** - Atlas guides (Guide, Publishing, Troubleshooting, Viewing, Quick Reference)
- **`docs/SDK_API_REFERENCE.md`** - SDK documentation
- **`docs/BEST_PRACTICES.md`** - Best practices
- **`docs/GIT_WORKFLOW.md`** - Git workflow
- **`docs/CI_CD_SETUP.md`** - CI/CD setup

### Release Documentation
- **`docs/RELEASE_READINESS_CHECKLIST.md`** - Release checklist
- **`docs/RELEASE_SUMMARY.md`** - Release summary
- **`docs/archive/`** - Archived release-specific and consolidated docs

## Directory-Specific READMEs

Each major directory has its own README:
- **`examples/README.md`** - Examples documentation
- **`notebooks/ANALYST_GUIDE.md`** - Analyst guide
- **`scripts/README.md`** - Scripts documentation
- **`config/README.md`** - Configuration guide
- **`schemas/README.md`** - Schema documentation
- **`sql_migration/README.md`** - Migration documentation
- **`airflow/dags/README.md`** - DAG documentation

## Organization Principles

1. **Root**: Only essential, standard project files (README, CHANGELOG, LICENSE, etc.)
2. **`docs/`**: All detailed documentation and guides
3. **Subdirectories**: READMEs for directory-specific content
4. **`docs/archive/`**: Old, release-specific, or consolidated documentation

## Files Moved to Archive

The following files were moved to `docs/archive/` as they are:
- Release-specific (v0.0.1)
- Consolidated into other documents
- Superseded by newer documentation

- `ARCHITECTURE.md` → Consolidated into README.md and DESIGN_PRINCIPLES.md
- `EXAMPLES.md` → Consolidated into examples/README.md
- `DOCUMENTATION_INDEX.md` → Duplicate of docs/README.md
- `DOCKER_SETUP.md` → Consolidated into DOCKER.md
- `DOCKER_TROUBLESHOOTING.md` → Consolidated into DOCKER.md
- `README_DATABASE.md` → Consolidated into GETTING_STARTED.md
- `README_UPDATE.md` → Old update notes
- `TESTING.md` → Moved to docs/archive (superseded by src/tests/TESTING.md)
- `TESTING_CHECKLIST.md` → Moved to docs/archive
- `VALIDATION_GUIDE.md` → Moved to docs/archive (consolidated into config/VALIDATION_GUIDE.md)
- `VERIFICATION_SUMMARY.md` → Old summary
- `SUMMARY.md` → Old summary
- `REPEATABLE_SETUP.md` → Old documentation
- Release-specific files (v0.0.1_*)

## Scripts Organization

All scripts moved to `scripts/` directory:
- `verify_*.py` → `scripts/verify_*.py`
- `publish_atlas_*.py` → `scripts/publish_atlas_*.py`
- `mock_atlas.py` → `scripts/mock_atlas.py`

## Why This Structure?

- **Clean root**: Easy to find essential files
- **Organized docs**: All documentation in one place
- **Standard locations**: Follows Python project conventions
- **Easy navigation**: Clear separation of concerns
- **No duplication**: Single source of truth for each topic

## Next Steps

- **[README.md](../README.md)** → Main project documentation
- **[docs/README.md](README.md)** → Complete documentation index
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Setup guide
