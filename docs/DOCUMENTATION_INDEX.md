# Documentation Index

Complete guide to all documentation in the Ringmaster Pipelines repository.

## 📚 Core Documentation

### Getting Started
- **[README.md](../README.md)** - Main project documentation, quick start, architecture overview
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Step-by-step setup guide for local development
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture, design principles, layer separation

### Migration & Implementation
- **[docs/MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - ⭐ **Agile/incremental migration guide** - How to implement pieces gradually
- **[sql_migration/README.md](../sql_migration/README.md)** - SQL migration overview
- **[sql_migration/MIGRATION_PROCESS.md](../sql_migration/MIGRATION_PROCESS.md)** - Step-by-step SQL migration process
- **[sql_migration/sql_migration_tracker.md](../sql_migration/sql_migration_tracker.md)** - Track SQL queries being migrated

---

## 🐳 Docker & Infrastructure

### Docker Setup
- **[DOCKER.md](../DOCKER.md)** - Docker overview and usage
- **[DOCKER_SETUP.md](../DOCKER_SETUP.md)** - Detailed Docker Compose setup
- **[DOCKER_TROUBLESHOOTING.md](../DOCKER_TROUBLESHOOTING.md)** - Common Docker issues and solutions

**Consolidated**: All Docker docs cover different aspects - keep all three

---

## 🧪 Testing & Validation

### Testing
- **[TESTING.md](../TESTING.md)** - Testing strategy and instructions
- **[TESTING_CHECKLIST.md](../TESTING_CHECKLIST.md)** - Comprehensive verification checklist
- **[VALIDATION_GUIDE.md](../VALIDATION_GUIDE.md)** - Data validation system guide

**Consolidated**: Testing.md is strategy, TESTING_CHECKLIST.md is practical steps

---

## 📊 Data Governance (Atlas)

### Atlas Documentation
- **[docs/ATLAS_GUIDE.md](./ATLAS_GUIDE.md)** - Complete Atlas guide (comprehensive)
- **[docs/ATLAS_PUBLISHING.md](./ATLAS_PUBLISHING.md)** - How to publish metadata
- **[docs/ATLAS_QUICK_REFERENCE.md](./ATLAS_QUICK_REFERENCE.md)** - Quick reference for Atlas
- **[docs/ATLAS_TROUBLESHOOTING.md](./ATLAS_TROUBLESHOOTING.md)** - Atlas troubleshooting

**Consolidated**: ATLAS_GUIDE.md is main doc, others are specialized references

---

## 💻 Development

### Examples & Code
- **[EXAMPLES.md](../EXAMPLES.md)** - Code examples and snippets
- **[examples/pipeline_example.py](../examples/pipeline_example.py)** - Pipeline usage example
- **[examples/sdk_example.py](../examples/sdk_example.py)** - SDK usage example

### Database
- **[README_DATABASE.md](../README_DATABASE.md)** - Database schema and operations

---

## 📝 Reference

### Project Information
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
- **[SUMMARY.md](../SUMMARY.md)** - Project summary
- **[VERIFICATION_SUMMARY.md](../VERIFICATION_SUMMARY.md)** - Current verification status
- **[REPEATABLE_SETUP.md](../REPEATABLE_SETUP.md)** - Repeatable verification guide

### Airflow
- **[airflow/dags/README.md](../airflow/dags/README.md)** - Airflow DAGs documentation

---

## 📖 Documentation by Role

### For Analysts
1. Start: **[GETTING_STARTED.md](../GETTING_STARTED.md)**
2. SDK Usage: **[EXAMPLES.md](../EXAMPLES.md)** → SDK examples
3. Notebooks: `notebooks/analyst_*.ipynb`
4. Database Access: **[README_DATABASE.md](../README_DATABASE.md)**

### For Engineers
1. Start: **[ARCHITECTURE.md](../ARCHITECTURE.md)**
2. Pipeline Development: **[EXAMPLES.md](../EXAMPLES.md)** → Pipeline examples
3. Testing: **[TESTING.md](../TESTING.md)**
4. Migration: **[docs/MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)**

### For DevOps
1. Docker: **[DOCKER_SETUP.md](../DOCKER_SETUP.md)**
2. Troubleshooting: **[DOCKER_TROUBLESHOOTING.md](../DOCKER_TROUBLESHOOTING.md)**
3. Airflow: **[airflow/dags/README.md](../airflow/dags/README.md)**
4. Verification: **[TESTING_CHECKLIST.md](../TESTING_CHECKLIST.md)**

### For Project Managers
1. Overview: **[README.md](../README.md)**
2. Migration Plan: **[docs/MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)**
3. Status: **[VERIFICATION_SUMMARY.md](../VERIFICATION_SUMMARY.md)**
4. History: **[CHANGELOG.md](../CHANGELOG.md)**

---

## 🗂️ Documentation Structure

```
docs/
├── MIGRATION_GUIDE.md          # ⭐ Agile migration guide
├── DOCUMENTATION_INDEX.md      # This file
├── ATLAS_GUIDE.md              # Comprehensive Atlas guide
├── ATLAS_PUBLISHING.md         # Atlas publishing how-to
├── ATLAS_QUICK_REFERENCE.md    # Atlas quick reference
└── ATLAS_TROUBLESHOOTING.md    # Atlas troubleshooting

Root/
├── README.md                   # Main documentation
├── ARCHITECTURE.md             # System architecture
├── GETTING_STARTED.md          # Setup guide
├── EXAMPLES.md                 # Code examples
├── TESTING.md                  # Testing strategy
├── TESTING_CHECKLIST.md        # Verification checklist
├── DOCKER.md                   # Docker overview
├── DOCKER_SETUP.md             # Docker setup
├── DOCKER_TROUBLESHOOTING.md   # Docker issues
├── VALIDATION_GUIDE.md         # Validation system
├── CHANGELOG.md                # Version history
└── sql_migration/              # SQL migration docs
```

---

## 🔍 Finding Documentation

### By Topic

**Setup & Installation**
- Local: `GETTING_STARTED.md`
- Docker: `DOCKER_SETUP.md`
- Verification: `verify_setup.py`

**Architecture & Design**
- Overview: `ARCHITECTURE.md`
- Examples: `EXAMPLES.md`
- Patterns: `ARCHITECTURE.md` → Design Patterns

**Pipelines**
- Development: `EXAMPLES.md` → Pipeline examples
- Configuration: `pipelines_config/*.yml`
- Execution: `run_local.py --help`

**SDK & Analyst Tools**
- Usage: `EXAMPLES.md` → SDK examples
- Notebooks: `notebooks/analyst_*.ipynb`
- Database: `README_DATABASE.md`

**Testing & Validation**
- Strategy: `TESTING.md`
- Checklist: `TESTING_CHECKLIST.md`
- Validation: `VALIDATION_GUIDE.md`

**Migration**
- Guide: `docs/MIGRATION_GUIDE.md` ⭐
- SQL Process: `sql_migration/MIGRATION_PROCESS.md`
- Tracker: `sql_migration/sql_migration_tracker.md`

**Data Governance**
- Atlas: `docs/ATLAS_GUIDE.md`
- Publishing: `docs/ATLAS_PUBLISHING.md`
- Troubleshooting: `docs/ATLAS_TROUBLESHOOTING.md`

---

## 📝 Documentation Maintenance

### When to Update
- New features added → Update relevant docs
- Architecture changes → Update `ARCHITECTURE.md`
- Migration progress → Update `sql_migration_tracker.md`
- Version release → Update `CHANGELOG.md`

### Documentation Standards
- Clear, concise language
- Code examples where helpful
- Links to related docs
- Keep up-to-date with code

---

## 🆘 Quick Help

**"How do I...?"**

- **Set up locally?** → `GETTING_STARTED.md`
- **Run a pipeline?** → `README.md` → Running Locally
- **Use the SDK?** → `EXAMPLES.md` → SDK examples
- **Migrate SQL?** → `docs/MIGRATION_GUIDE.md`
- **Set up Docker?** → `DOCKER_SETUP.md`
- **Troubleshoot?** → `DOCKER_TROUBLESHOOTING.md` or `docs/ATLAS_TROUBLESHOOTING.md`
- **Understand architecture?** → `ARCHITECTURE.md`
- **Verify everything works?** → `TESTING_CHECKLIST.md`

---

**Last Updated**: v0.0.1 Release


