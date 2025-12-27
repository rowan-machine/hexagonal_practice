# Changelog

## v0.0.1 - Initial Release (Updated with YAML Configuration)

### Added
- **BasePipeline**: Centralized execution logic for all pipelines
- **Pipeline Steps**: Reusable step classes (Bronze, Silver, Gold, Validation, Aggregation)
- **Domain Models**: 
  - `ClaimsProcessor` for stop loss insurance claims processing
  - `PolicyProcessor` for stop loss insurance policies management
- **Transform Layers**: Bronze (ingestion), Silver (business rules), Gold (aggregation)
- **SDK Interfaces**: 
  - `ClaimsAnalyst` for analyst-friendly claims operations
  - `PoliciesAnalyst` for analyst-friendly policies operations
  - `StopLossAnalyst` for combined analysis
- **Mixins**: Logging, Metrics, and Validation mixins for cross-cutting concerns
- **Utilities**: 
  - I/O utilities for file operations
  - DataFrame operations (pandas isolated to this layer)
- **Configuration-Driven Pipelines**: 
  - `ClaimsPipeline` example
  - `PoliciesPipeline` example
- **Testing**: Unit test examples for domain, pipelines, and transforms
- **Documentation**: 
  - Architecture documentation
  - README with usage examples
  - Example scripts demonstrating usage

### Design Principles
- Clean, interface-driven Python
- Stateful, object-oriented design
- Configuration-driven pipeline definitions
- Clear separation of concerns (domain, transforms, pipelines, SDK)
- No pandas outside transform layer
- All public APIs typed
- Testable components with minimal I/O dependencies

### YAML Configuration Support
- **ConfigLoader**: YAML-based pipeline configuration loader
- **Pipeline Configurations**: YAML files in `pipelines_config/` directory
- **Schema Definitions**: YAML schema files in `schemas/` directory
- **Command Line Runner**: `run_local.py` for executing pipelines from YAML configs
- **Updated Examples**: All examples now use YAML configuration

### For Ringmaster Technologies
This initial release provides a foundation for stop loss insurance marketplace data pipelines with:
- Claims processing capabilities
- Policy management capabilities
- Analyst-friendly SDK interfaces
- Professional software design patterns
- YAML-driven configuration for easy pipeline management

