# Design Principles

Detailed design principles and architectural patterns for the Ringmaster Pipelines system.

## Hexagonal Architecture (Ports and Adapters)

This project follows **Hexagonal Architecture** (also known as **Ports and Adapters**), a software architecture pattern introduced by Alistair Cockburn. The name "hexagonal" comes from the visual representation where the core application is at the center, surrounded by adapters on all sides (forming a hexagon shape).

### Core Concept

Hexagonal architecture separates the **core business logic** (the "hexagon") from **external dependencies** (adapters). The core application doesn't know or care about:
- Where data comes from (files, databases, APIs)
- Where data goes (databases, message queues, web services)
- How it's accessed (CLI, web UI, scheduled jobs)

Instead, the core defines **ports** (interfaces) that external systems must implement via **adapters**.

### Why Hexagonal Architecture?

**Traditional Approach (Tightly Coupled)**:
```python
# Business logic mixed with I/O
def process_claim():
    data = read_file("claims.json")  # Hard-coded file I/O
    claim = Claim(**data)
    result = calculate_total(claim)
    write_to_database(result)  # Hard-coded database
    return result
```

**Problems**:
- Hard to test (requires real files/databases)
- Hard to change (switching databases requires code changes)
- Business logic tied to infrastructure

**Hexagonal Approach (Loosely Coupled)**:
```python
# Core (domain) - Pure business logic
class ClaimsProcessor:
    def process(self, claim: Claim) -> ProcessedClaim:
        # Pure business logic, no I/O
        return ProcessedClaim(
            total=claim.amount * claim.multiplier,
            status=self._determine_status(claim)
        )

# Adapter - Handles I/O
class FileClaimsAdapter:
    def load_claims(self, path: str) -> List[Claim]:
        # I/O isolated here
        data = read_file(path)
        return [Claim(**item) for item in data]
```

**Benefits**:
- ✅ Easy to test (business logic is pure functions/classes)
- ✅ Easy to change (swap adapters without touching core)
- ✅ Business logic independent of infrastructure

### Architecture Layers in This Project

```
┌─────────────────────────────────────────────────────────┐
│                    External World                        │
│  (Files, Databases, APIs, CLI, Web UI, Scheduled Jobs)  │
└─────────────────────────────────────────────────────────┘
                        ↕ (Adapters)
┌─────────────────────────────────────────────────────────┐
│                    Adapter Layer                         │
│  • File Readers/Writers (src/utils/file_loader.py)      │
│  • Database Managers (src/utils/database.py)            │
│  • Atlas Publishers (src/utils/atlas.py)                  │
│  • Config Loaders (src/utils/config_loader.py)          │
└─────────────────────────────────────────────────────────┘
                        ↕ (Ports/Interfaces)
┌─────────────────────────────────────────────────────────┐
│                    Core Application                      │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Domain Layer (src/domain/)                     │   │
│  │  • Pure business logic                          │   │
│  │  • No I/O dependencies                          │   │
│  │  • Claim, Policy models                        │   │
│  │  • ClaimsProcessor, PolicyProcessor            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Pipeline Layer (src/pipelines/)                │   │
│  │  • Orchestration                                │   │
│  │  • Step coordination                            │   │
│  │  • Execution context                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Transform Layer (src/transforms/)              │   │
│  │  • Data transformations                        │   │
│  │  • Bronze/Silver/Gold steps                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  SDK Layer (src/sdk/)                           │   │
│  │  • Analyst-friendly interfaces                  │   │
│  │  • High-level abstractions                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Ports and Adapters in Practice

#### Ports (Interfaces)

Ports define **what** the core needs, not **how** it's provided:

```python
# Port: Interface for data storage
class DatabasePort(ABC):
    @abstractmethod
    def save_claim(self, claim: Claim) -> None:
        pass
    
    @abstractmethod
    def get_claim(self, claim_id: str) -> Claim:
        pass
```

#### Adapters (Implementations)

Adapters implement ports for specific technologies:

```python
# Adapter: SQLite implementation
class SQLiteDatabaseAdapter(DatabasePort):
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
    
    def save_claim(self, claim: Claim) -> None:
        # SQLite-specific implementation
        self.conn.execute("INSERT INTO claims ...", ...)

# Adapter: PostgreSQL implementation
class PostgreSQLDatabaseAdapter(DatabasePort):
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def save_claim(self, claim: Claim) -> None:
        # PostgreSQL-specific implementation
        self.conn.execute("INSERT INTO claims ...", ...)
```

#### Core Usage

The core uses ports, not adapters:

```python
# Core doesn't know about SQLite or PostgreSQL
class ClaimsPipeline:
    def __init__(self, database: DatabasePort):  # Uses port, not adapter
        self.database = database
    
    def run(self):
        claim = Claim(...)
        self.database.save_claim(claim)  # Works with any adapter
```

### Key Principles of Hexagonal Architecture

1. **Dependency Inversion**: Core depends on abstractions (ports), not concrete implementations (adapters)
2. **Isolation**: Core has no knowledge of external systems
3. **Testability**: Core can be tested with mock adapters
4. **Flexibility**: Swap adapters without changing core logic
5. **Independence**: Core can be developed independently of adapters

### How This Project Implements Hexagonal Architecture

#### 1. Domain Layer (Core)

The `src/domain/` directory contains pure business logic:

```python
# src/domain/claims.py - Pure business logic, no I/O
class Claim:
    def is_high_value(self, threshold: Decimal) -> bool:
        return self.claim_amount > threshold

class ClaimsProcessor:
    def process(self, claim: Claim) -> ProcessedClaim:
        # Pure business logic, no file I/O, no database
        return ProcessedClaim(...)
```

#### 2. Adapter Layer

The `src/utils/` directory contains adapters:

```python
# src/utils/database.py - Adapter for database operations
class DatabaseManager:
    def insert_claim(self, claim: Claim) -> None:
        # Database-specific implementation
        # Core doesn't know about this

# src/utils/file_loader.py - Adapter for file operations
class FileLoader:
    def load_json(self, path: str) -> Dict:
        # File I/O implementation
        # Core doesn't know about this
```

#### 3. Ports (Interfaces)

Interfaces are defined through abstract base classes:

```python
# src/pipelines/base.py
class PipelineStep(ABC):
    @abstractmethod
    def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        pass
```

#### 4. Dependency Injection

Adapters are injected into the core:

```python
# Pipeline receives adapters, doesn't create them
pipeline = ClaimsPipeline(
    config=config,
    database=DatabaseManager("warehouse.db"),  # Adapter injected
    file_loader=FileLoader()  # Adapter injected
)
```

### Benefits in This Project

1. **Easy Testing**: Domain logic can be tested without databases or files
   ```python
   # Test pure business logic
   processor = ClaimsProcessor()
   result = processor.process(claim)  # No I/O needed
   assert result.status == "approved"
   ```

2. **Flexible Deployment**: Swap SQLite for PostgreSQL without changing core
   ```python
   # Local: SQLite
   db = SQLiteDatabaseAdapter("warehouse.db")
   
   # Production: PostgreSQL
   db = PostgreSQLDatabaseAdapter("postgresql://...")
   
   # Same pipeline works with both
   pipeline = ClaimsPipeline(config, database=db)
   ```

3. **Independent Development**: Core and adapters can be developed separately
4. **Clear Boundaries**: Easy to see what's business logic vs. infrastructure
5. **Reusability**: Core logic can be used in different contexts (CLI, web, scheduled jobs)

### Visual Representation

```
                    ┌─────────────┐
                    │   CLI Tool   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Pipeline    │
                    │  Orchestrator│
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐
│ File Adapter │  │ Database Adapter│  │Atlas Adapter│
└───────┬──────┘  └────────┬────────┘  └─────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Domain     │
                    │   (Core)     │
                    │              │
                    │ • Claim      │
                    │ • Policy     │
                    │ • Processors │
                    └──────────────┘
```

The **Domain (Core)** is at the center, completely isolated from external systems. **Adapters** handle all I/O and translate between external systems and the core.

### Common Questions

**Q: Why not just use dependency injection?**  
A: Hexagonal architecture is dependency injection applied systematically at the architectural level. It ensures the core never depends on adapters.

**Q: Does this add complexity?**  
A: Initially yes, but it pays off in testability, maintainability, and flexibility. The core stays simple because it has no I/O concerns.

**Q: What if I need to access the database from domain logic?**  
A: You don't. Domain logic receives data through method parameters. Adapters load data and pass it to the domain.

**Q: How do I know if something is core or adapter?**  
A: Ask: "Does this need to know about files/databases/APIs?" If yes, it's an adapter. If no, it's core.

## Core Principles

### 1. Separation of Concerns

Each layer has a single, well-defined responsibility:

- **`src/domain/`**: Pure business logic, no I/O dependencies
  - Domain models (Claim, Policy)
  - Business rule processors (ClaimsProcessor, PoliciesProcessor)
  - No file I/O, no database access, no external API calls

- **`src/pipelines/`**: Orchestration only
  - Coordinates execution flow
  - Manages execution context
  - Delegates to domain and transforms
  - Does not contain business logic

- **`src/transforms/`**: Data transformation layer
  - Bronze: Raw data ingestion and basic cleaning
  - Silver: Business rule application and enrichment
  - Gold: Aggregated, analysis-ready datasets
  - Validation: Data quality checks and constraints

- **`src/sdk/`**: Analyst-facing convenience interfaces
  - High-level methods for common operations
  - Hides complexity from end users
  - Uses domain and transforms internally

- **`src/utils/`**: Cross-cutting utilities
  - I/O operations (file reading/writing)
  - Database operations
  - Configuration loading
  - No business logic

- **`src/mixins/`**: Reusable behaviors
  - LoggingMixin: Structured logging
  - MetricsMixin: Performance metrics
  - ValidationMixin: Data validation helpers

### 2. Design Patterns

#### Stateful Classes
Pipeline state is managed through class attributes, not globals or singletons.

```python
class ClaimsPipeline(BasePipeline):
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.context = config.context
        # State is explicit and contained
```

#### Configuration-Driven
Pipelines are defined by YAML configuration files, not copy-pasted code.

```yaml
# config/claims_pipeline.yml
pipeline:
  name: claims_pipeline
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
```

#### Interface-Driven
Clear contracts between layers via abstract base classes.

```python
class PipelineStep(ABC):
    @abstractmethod
    def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        pass
```

#### Composable Steps
Reusable pipeline steps that can be combined in different ways.

```python
steps = [
    ClaimsBronzeStep(source_path="data/raw_claims.json"),
    ClaimsSilverStep(approval_threshold=100000.00),
    ClaimsGoldStep()
]
```

### 3. Constraints

These constraints ensure maintainability and testability:

- **No pandas outside transform layer**: DataFrame operations are isolated
- **All public APIs must be typed**: Type hints required for all public methods
- **No framework-heavy dependencies**: Airflow used only for orchestration
- **Business logic in Python classes**: Not in notebooks or scripts
- **No global state**: All state is explicit and contained in classes

### 4. Testing Strategy

- **Unit tests**: Domain logic tested in isolation (no I/O mocking complexity)
- **Integration tests**: Pipeline orchestration tested end-to-end
- **Transform tests**: Verify data shape and business rules
- **No I/O in domain tests**: Domain logic is pure, making tests simple

## Usage Patterns

### YAML Configuration

Pipelines are configured via YAML files in `config/`:

```yaml
pipeline:
  name: claims_pipeline
  steps:
    - name: claims_bronze
      type: bronze
      source:
        path: "data/raw_claims.json"
    - name: claims_silver
      type: silver
      domain_handler: ClaimsProcessor
  execution:
    stop_on_error: true
```

### Programmatic Usage

```python
from src.utils.config_loader import ConfigLoader
from src.pipelines import ClaimsPipeline

# Load from YAML
config_loader = ConfigLoader()
config = config_loader.create_pipeline_config("claims_pipeline")
pipeline = ClaimsPipeline(config)
results = pipeline.run()
```

### Command Line

```bash
python run_local.py claims_pipeline
```

## Benefits of This Architecture

1. **Testability**: Domain logic can be tested without I/O mocking
2. **Maintainability**: Clear separation makes changes easier
3. **Reusability**: Components can be composed in different ways
4. **Clarity**: Each layer has a single, well-defined purpose
5. **Flexibility**: Easy to swap implementations (e.g., different data sources)

## Next Steps

**Understanding the architecture?** Continue with:

1. **[examples/README.md](../examples/README.md)** → See these patterns in action
2. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create your own pipelines
3. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Learn testing patterns

**Ready to implement?**

1. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Follow best practices
2. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Start contributing
3. **[docs/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** → Migrate existing code

## Related Documentation

- **[README.md](../README.md)** - Architecture overview
- **[examples/README.md](../examples/README.md)** - Code examples showing these patterns
- **[docs/architecture_diagram.mmd](architecture_diagram.mmd)** - Visual architecture diagram

