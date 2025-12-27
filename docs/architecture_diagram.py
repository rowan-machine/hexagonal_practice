"""
Generate visual architecture diagram for Ringmaster Pipelines.

This script generates an architecture diagram using graphviz (dot format)
that can be rendered as PNG, SVG, or PDF.

Requirements:
    pip install graphviz

Usage:
    python docs/architecture_diagram.py
    # Output: docs/architecture_diagram.png
"""
from graphviz import Digraph
import os


def create_architecture_diagram():
    """Create visual architecture diagram."""
    
    # Create directed graph
    dot = Digraph(comment='Ringmaster Pipelines Architecture', format='png')
    dot.attr(rankdir='TB', size='16,12', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', fontname='Arial', fontsize='10')
    
    # Color scheme
    domain_color = '#E8F4F8'      # Light blue
    transform_color = '#FFF4E6'    # Light orange
    pipeline_color = '#E8F5E9'    # Light green
    sdk_color = '#F3E5F5'         # Light purple
    utils_color = '#FCE4EC'        # Light pink
    data_color = '#E0F2F1'        # Light teal
    
    # ============================================================================
    # DATA LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_data') as data_cluster:
        data_cluster.attr(label='Data Sources & Storage', style='filled', 
                         color='lightgray', fillcolor=data_color)
        data_cluster.node('raw_json', 'Raw JSON Files\n(data/)', 
                         fillcolor=data_color)
        data_cluster.node('warehouse', 'Warehouse DB\n(SQLite/PostgreSQL)', 
                         fillcolor=data_color)
        data_cluster.node('bronze', 'Bronze Tables\n(raw data)', 
                         fillcolor=data_color)
        data_cluster.node('silver', 'Silver Tables\n(processed)', 
                         fillcolor=data_color)
        data_cluster.node('gold', 'Gold Tables\n(aggregated)', 
                         fillcolor=data_color)
    
    # ============================================================================
    # DOMAIN LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_domain') as domain_cluster:
        domain_cluster.attr(label='Domain Layer (Business Logic)', 
                           style='filled', color='lightblue', 
                           fillcolor=domain_color)
        domain_cluster.node('claim_model', 'Claim\n(Dataclass)', 
                          fillcolor=domain_color)
        domain_cluster.node('policy_model', 'Policy\n(Dataclass)', 
                          fillcolor=domain_color)
        domain_cluster.node('claims_processor', 'ClaimsProcessor\n(Business Rules)', 
                          fillcolor=domain_color)
        domain_cluster.node('policies_processor', 'PoliciesProcessor\n(Business Rules)', 
                          fillcolor=domain_color)
        domain_cluster.node('aggregations', 'Aggregators\n(Centralized Rules)', 
                          fillcolor=domain_color)
    
    # ============================================================================
    # TRANSFORM LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_transform') as transform_cluster:
        transform_cluster.attr(label='Transform Layer (Data Processing)', 
                              style='filled', color='orange', 
                              fillcolor=transform_color)
        transform_cluster.node('bronze_step', 'BronzeStep\n(Ingestion)', 
                             fillcolor=transform_color)
        transform_cluster.node('silver_step', 'SilverStep\n(Transformation)', 
                             fillcolor=transform_color)
        transform_cluster.node('gold_step', 'GoldStep\n(Aggregation)', 
                             fillcolor=transform_color)
        transform_cluster.node('validation_step', 'ValidationStep\n(Quality Checks)', 
                             fillcolor=transform_color)
    
    # ============================================================================
    # PIPELINE LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_pipeline') as pipeline_cluster:
        pipeline_cluster.attr(label='Pipeline Layer (Orchestration)', 
                             style='filled', color='green', 
                             fillcolor=pipeline_color)
        pipeline_cluster.node('base_pipeline', 'BasePipeline\n(Core Orchestration)', 
                            fillcolor=pipeline_color)
        pipeline_cluster.node('pipeline_step', 'PipelineStep\n(Base Class)', 
                            fillcolor=pipeline_color)
        pipeline_cluster.node('claims_pipeline', 'ClaimsPipeline\n(Claims Workflow)', 
                            fillcolor=pipeline_color)
        pipeline_cluster.node('policies_pipeline', 'PoliciesPipeline\n(Policies Workflow)', 
                            fillcolor=pipeline_color)
        pipeline_cluster.node('config_loader', 'ConfigLoader\n(YAML → Pipeline)', 
                            fillcolor=pipeline_color)
    
    # ============================================================================
    # SDK LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_sdk') as sdk_cluster:
        sdk_cluster.attr(label='SDK Layer (Analyst Interfaces)', 
                        style='filled', color='purple', 
                        fillcolor=sdk_color)
        sdk_cluster.node('claims_analyst', 'ClaimsAnalyst\n(Analyst Interface)', 
                        fillcolor=sdk_color)
        sdk_cluster.node('policies_analyst', 'PoliciesAnalyst\n(Analyst Interface)', 
                        fillcolor=sdk_color)
        sdk_cluster.node('stoploss_analyst', 'StopLossAnalyst\n(Combined Analysis)', 
                        fillcolor=sdk_color)
    
    # ============================================================================
    # UTILITIES LAYER
    # ============================================================================
    with dot.subgraph(name='cluster_utils') as utils_cluster:
        utils_cluster.attr(label='Utilities Layer (Infrastructure)', 
                          style='filled', color='pink', 
                          fillcolor=utils_color)
        utils_cluster.node('database', 'DatabaseManager\n(SQL Operations)', 
                          fillcolor=utils_color)
        utils_cluster.node('atlas', 'AtlasClient\n(Metadata Publishing)', 
                          fillcolor=utils_color)
        utils_cluster.node('logging', 'LoggingMixin\n(Structured Logging)', 
                          fillcolor=utils_color)
        utils_cluster.node('metrics', 'MetricsMixin\n(Performance Metrics)', 
                          fillcolor=utils_color)
    
    # ============================================================================
    # DATA FLOW EDGES
    # ============================================================================
    
    # Data ingestion flow
    dot.edge('raw_json', 'bronze_step', label='Load', style='dashed')
    dot.edge('bronze_step', 'bronze', label='Write')
    dot.edge('bronze', 'silver_step', label='Read')
    dot.edge('silver_step', 'silver', label='Write')
    dot.edge('silver', 'gold_step', label='Read')
    dot.edge('gold_step', 'gold', label='Write')
    
    # Domain logic flow
    dot.edge('bronze_step', 'claim_model', label='Parse', style='dotted')
    dot.edge('claim_model', 'claims_processor', label='Process')
    dot.edge('claims_processor', 'silver_step', label='Apply Rules')
    dot.edge('silver_step', 'aggregations', label='Aggregate')
    dot.edge('aggregations', 'gold_step', label='Use Rules')
    
    # Pipeline orchestration
    dot.edge('config_loader', 'base_pipeline', label='Creates')
    dot.edge('base_pipeline', 'pipeline_step', label='Orchestrates')
    dot.edge('pipeline_step', 'bronze_step', label='Executes')
    dot.edge('pipeline_step', 'silver_step', label='Executes')
    dot.edge('pipeline_step', 'gold_step', label='Executes')
    dot.edge('pipeline_step', 'validation_step', label='Executes')
    dot.edge('base_pipeline', 'claims_pipeline', label='Inherits')
    dot.edge('base_pipeline', 'policies_pipeline', label='Inherits')
    
    # SDK access
    dot.edge('claims_analyst', 'database', label='Queries', style='dashed')
    dot.edge('claims_analyst', 'aggregations', label='Uses Rules')
    dot.edge('policies_analyst', 'database', label='Queries', style='dashed')
    dot.edge('policies_analyst', 'aggregations', label='Uses Rules')
    dot.edge('stoploss_analyst', 'claims_analyst', label='Composes')
    dot.edge('stoploss_analyst', 'policies_analyst', label='Composes')
    
    # Infrastructure
    dot.edge('base_pipeline', 'logging', label='Uses', style='dotted')
    dot.edge('base_pipeline', 'metrics', label='Uses', style='dotted')
    dot.edge('base_pipeline', 'atlas', label='Publishes', style='dotted')
    dot.edge('database', 'warehouse', label='Manages')
    
    # Save diagram
    output_path = os.path.join('docs', 'architecture_diagram')
    dot.render(output_path, cleanup=True)
    print(f"✅ Architecture diagram generated: {output_path}.png")
    print(f"   Also available as: {output_path}.pdf (if graphviz supports it)")
    
    return dot


if __name__ == "__main__":
    try:
        create_architecture_diagram()
    except ImportError:
        print("⚠️  graphviz not installed. Installing...")
        print("   Run: pip install graphviz")
        print("\n   Also install graphviz system package:")
        print("   - Windows: Download from https://graphviz.org/download/")
        print("   - Mac: brew install graphviz")
        print("   - Linux: sudo apt-get install graphviz")
    except Exception as e:
        print(f"❌ Error generating diagram: {e}")
        print("\nAlternative: Use online Mermaid editor:")
        print("   See docs/architecture_diagram.mmd for Mermaid format")


