# Root Directory Documentation Organization

This document explains the organization of documentation files in the root directory.

## Documentation Structure

### Core Documentation (Root Level)

These files remain in the root directory as they are the primary entry points:

**Getting Started:**
- `README.md` - Main project documentation and entry point
- `GETTING_STARTED.md` - Setup and installation guide

**Architecture & Design:**
- `README.md` → Architecture Overview section (consolidated from ARCHITECTURE.md)
- `examples/README.md` - Code examples and snippets (consolidated from EXAMPLES.md)

**Infrastructure:**
- `DOCKER.md` - Complete Docker and Docker Compose guide (consolidated from DOCKER_SETUP.md and DOCKER_TROUBLESHOOTING.md)

**Testing & Validation:**
- `TESTING.md` - Testing strategy and guidelines
- `TESTING_CHECKLIST.md` - Verification checklist
- `VALIDATION_GUIDE.md` - Data validation system

**Database:**
- `GETTING_STARTED.md` - Includes database setup and usage (consolidated from README_DATABASE.md)

**Version History:**
- `CHANGELOG.md` - Version history and changes

### Documentation in Subdirectories

**`docs/` - Detailed Documentation:**
- `README.md` - Complete documentation index
- `MIGRATION_GUIDE.md` - Agile migration guide
- `ATLAS_*.md` - Apache Atlas documentation
- `archive/` - Archived release-specific documentation

**`examples/` - Runnable Examples:**
- `README.md` - Usage instructions for examples
- `pipeline_example.py` - Pipeline execution example
- `sdk_example.py` - SDK usage example

**`sql_migration/` - SQL Migration:**
- `README.md` - SQL migration overview
- `sql_migration/README.md` - Complete migration guide (consolidated from MIGRATION_PROCESS.md)
- `sql_migration_tracker.md` - Migration tracker

**`first_sql_conversion/` - SQL Conversion Example:**
- `README.md` - First SQL conversion guide
- Example files and notebook

## Navigation Flow

1. **Start Here:** `README.md`
2. **Setup:** `GETTING_STARTED.md`
3. **Understand System:** `README.md` → Architecture Overview | `docs/DESIGN_PRINCIPLES.md`
4. **See Examples:** `examples/README.md`
5. **Deep Dive:** `docs/README.md` for complete documentation index

## Why This Organization?

- **Root level:** Primary documentation that users need immediately
- **`docs/`:** Detailed, topic-specific documentation
- **`examples/`:** Runnable code with usage instructions
- **Subdirectories:** Specialized documentation for specific topics

This follows software documentation best practices:
- Single entry point (README.md)
- Clear hierarchy
- Role-based organization
- Progressive disclosure (start simple, go deeper)

## Next Steps

**Understood the organization?** Start exploring:

1. **[README.md](../README.md)** → Main project documentation
2. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Setup guide
3. **[docs/README.md](README.md)** → Complete documentation index

**Looking for specific topics?**

- **Configuration**: [config/README.md](../config/README.md)
- **Examples**: [examples/README.md](../examples/README.md)
- **Scripts**: [scripts/README.md](../scripts/README.md)
- **Migration**: [sql_migration/README.md](../sql_migration/README.md)
- **Schemas**: [schemas/README.md](../schemas/README.md)

**Ready to contribute?**

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Contribution guidelines
2. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Best practices
3. **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** → Architecture patterns

