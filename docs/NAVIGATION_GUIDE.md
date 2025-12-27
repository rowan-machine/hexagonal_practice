# Documentation Navigation Guide

This guide helps you navigate the interconnected documentation structure. Every document has a "Next Steps" section that creates natural paths through the documentation.

## Navigation Principles

1. **Every document has "Next Steps"** - Clear paths to related content
2. **Role-based entry points** - Start from your role
3. **Progressive disclosure** - Start simple, go deeper
4. **Logical flow** - Natural progression through topics

## Entry Points by Role

### New Users / Getting Started

**Path:**
```
README.md
  ↓
GETTING_STARTED.md
  ↓
examples/README.md
  ↓
docs/DESIGN_PRINCIPLES.md (optional)
```

**Quick Links:**
- Start: [README.md](../README.md)
- Setup: [GETTING_STARTED.md](../GETTING_STARTED.md)
- Examples: [examples/README.md](../examples/README.md)

### Analysts

**Path:**
```
examples/README.md (SDK Examples)
  ↓
GETTING_STARTED.md (Database section)
  ↓
notebooks/analyst_*.ipynb
  ↓
schemas/README.md
```

**Quick Links:**
- SDK: [examples/README.md](../examples/README.md) → SDK Examples
- Database: [GETTING_STARTED.md](../GETTING_STARTED.md) → Database section
- Schemas: [schemas/README.md](../schemas/README.md)

### Engineers

**Path:**
```
README.md (Architecture Overview)
  ↓
docs/DESIGN_PRINCIPLES.md
  ↓
examples/README.md (Pipeline Examples)
  ↓
config/PIPELINE_CONFIG_GUIDE.md
  ↓
docs/BEST_PRACTICES.md
```

**Quick Links:**
- Architecture: [docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- Pipelines: [config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)
- Best Practices: [docs/BEST_PRACTICES.md](BEST_PRACTICES.md)

### DevOps

**Path:**
```
DOCKER.md
  ↓
docs/ATLAS_GUIDE.md
  ↓
airflow/dags/README.md
  ↓
docs/BEST_PRACTICES.md (Deployment section)
```

**Quick Links:**
- Docker: [DOCKER.md](../DOCKER.md)
- Atlas: [docs/ATLAS_GUIDE.md](ATLAS_GUIDE.md)
- Airflow: [airflow/dags/README.md](../airflow/dags/README.md)

### Project Managers / Migration Planning

**Path:**
```
docs/MIGRATION_GUIDE.md
  ↓
sql_migration/README.md
  ↓
first_sql_conversion/README.md
  ↓
config/VALIDATION_GUIDE.md
```

**Quick Links:**
- Migration: [docs/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- Process: [sql_migration/README.md](../sql_migration/README.md)
- Example: [first_sql_conversion/README.md](../first_sql_conversion/README.md)

## Common Navigation Paths

### Setting Up

```
README.md → GETTING_STARTED.md → examples/README.md
```

### Creating a Pipeline

```
config/PIPELINE_CONFIG_GUIDE.md → schemas/README.md → config/VALIDATION_GUIDE.md
```

### Migrating SQL

```
docs/MIGRATION_GUIDE.md → sql_migration/README.md → first_sql_conversion/README.md
```

### Contributing

```
CONTRIBUTING.md → docs/BEST_PRACTICES.md → src/tests/TESTING.md
```

### Setting Up Infrastructure

```
DOCKER.md → docs/ATLAS_GUIDE.md → airflow/dags/README.md
```

## How "Next Steps" Work

Every document ends with a "Next Steps" section that:

1. **Links to related content** - Natural progression
2. **Organized by intent** - "Ready to X?" sections
3. **Multiple paths** - Different options based on your goal
4. **Clear hierarchy** - Most relevant first

## Finding Documentation

### By Topic

- **Architecture**: [docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- **Migration**: [docs/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Best Practices**: [docs/BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Atlas**: [docs/ATLAS_GUIDE.md](ATLAS_GUIDE.md)
- **Docker**: [DOCKER.md](../DOCKER.md)
- **Configuration**: [config/README.md](../config/README.md)
- **Examples**: [examples/README.md](../examples/README.md)

### By Directory

- **Root**: [README.md](../README.md) - Main entry point
- **docs/**: [docs/README.md](README.md) - Complete documentation index
- **config/**: [config/README.md](../config/README.md) - Configuration files
- **scripts/**: [scripts/README.md](../scripts/README.md) - Helper scripts
- **examples/**: [examples/README.md](../examples/README.md) - Code examples
- **schemas/**: [schemas/README.md](../schemas/README.md) - Data schemas
- **sql_migration/**: [sql_migration/README.md](../sql_migration/README.md) - Migration docs

## Tips for Navigation

1. **Start with "Next Steps"** - Every document guides you forward
2. **Follow your role** - Use role-based entry points
3. **Use the index** - [docs/README.md](README.md) has everything
4. **Search by topic** - Use the topic-based organization
5. **Follow links** - Each "Next Steps" creates a path

## Related Documentation

- **[docs/README.md](README.md)** - Complete documentation index
- **[README.md](../README.md)** - Main project documentation
- **[docs/DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md)** - Documentation structure details

