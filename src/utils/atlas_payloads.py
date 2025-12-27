"""
Atlas payload builders for data lineage and governance.

These payloads describe:
- Databases
- Tables
- ETL processes
- Input / output lineage

They are intentionally static + declarative.
Runtime logic belongs in AtlasClient, not here.

SQL Migration Reference:
- These payloads document the warehouse schema and ETL processes
- Maps to tables created in db_bootstrap.py
"""
from typing import Dict, List, Any


# =============================================================================
# Helpers
# =============================================================================

def hive_db_payload(db_name: str, cluster_name: str = "postgres") -> Dict[str, Any]:
    """
    Build Atlas payload for a Hive database entity.
    
    Args:
        db_name: Database name (e.g., "warehouse")
        cluster_name: Cluster name (default: "postgres")
        
    Returns:
        Atlas entity dictionary for hive_db type
    """
    return {
        "typeName": "hive_db",
        "attributes": {
            "qualifiedName": f"{db_name}@{cluster_name}",
            "name": db_name,
            "clusterName": cluster_name,
        },
    }


def hive_table_payload(
    *,
    db_name: str,
    table_name: str,
) -> Dict[str, Any]:
    """
    Build Atlas payload for a Hive table entity.
    
    Args:
        db_name: Database name
        table_name: Table name
        
    Returns:
        Atlas entity dictionary for hive_table type
    """
    return {
        "typeName": "hive_table",
        "attributes": {
            "qualifiedName": f"{db_name}.{table_name}@postgres",
            "name": table_name,
            "db": {
                "typeName": "hive_db",
                "uniqueAttributes": {
                    "qualifiedName": f"{db_name}@postgres"
                }
            },
        },
    }


def process_payload(
    *,
    name: str,
    qualified_name: str,
    inputs: List[str],
    outputs: List[str],
) -> Dict[str, Any]:
    """
    Build Atlas payload for an ETL process entity.
    
    Args:
        name: Process name (e.g., "policies_fact_etl")
        qualified_name: Fully qualified name (e.g., "policies_fact_etl@airflow")
        inputs: List of input entity qualified names
        outputs: List of output entity qualified names
        
    Returns:
        Atlas entity dictionary for Process type
    """
    attrs = {
        "qualifiedName": qualified_name,
        "name": name,
    }
    
    # Only include inputs/outputs if they're not empty
    # Empty lists can cause "null entity" errors in Atlas
    # Atlas requires typeName in references - infer from qualified name pattern
    if inputs:
        attrs["inputs"] = []
        for qn in inputs:
            # Infer type from qualified name pattern
            if "@postgres" in qn and "." in qn:
                ref_type = "hive_table"
            elif "@postgres" in qn:
                ref_type = "hive_db"
            else:
                ref_type = "Process"
            attrs["inputs"].append({
                "typeName": ref_type,
                "uniqueAttributes": {"qualifiedName": qn}
            })
    
    if outputs:
        attrs["outputs"] = []
        for qn in outputs:
            # Infer type from qualified name pattern
            if "@postgres" in qn and "." in qn:
                ref_type = "hive_table"
            elif "@postgres" in qn:
                ref_type = "hive_db"
            else:
                ref_type = "Process"
            attrs["outputs"].append({
                "typeName": ref_type,
                "uniqueAttributes": {"qualifiedName": qn}
            })
    
    return {
        "typeName": "Process",
        "attributes": attrs,
    }


# =============================================================================
# POLICIES — FACT TABLE
# =============================================================================

def build_policies_table_payload() -> Dict[str, Any]:
    """
    Build Atlas payload for policies fact table and ETL process.
    
    Documents the fact_policies table and its ETL process.
    
    Returns:
        Atlas payload dictionary with database, table, and process entities
    """
    db = "warehouse"

    return {
        "entities": [
            hive_db_payload(db),
            hive_table_payload(
                db_name=db,
                table_name="fact_policies",
            ),
            process_payload(
                name="policies_fact_etl",
                qualified_name="policies_fact_etl@airflow",
                inputs=[],  # raw JSON / upstream systems omitted for brevity
                outputs=[f"{db}.fact_policies@postgres"],
            ),
        ]
    }


# =============================================================================
# POLICIES — AGGREGATES
# =============================================================================

def build_policies_aggregates_payload() -> Dict[str, Any]:
    """
    Build Atlas payload for policies aggregate table and ETL process.
    
    Documents the gold_policies_by_customer table and its aggregation process.
    
    Returns:
        Atlas payload dictionary with database, table, and process entities
    """
    db = "warehouse"

    return {
        "entities": [
            hive_db_payload(db),
            hive_table_payload(
                db_name=db,
                table_name="gold_policies_by_customer",
            ),
            process_payload(
                name="policies_aggregates_etl",
                qualified_name="policies_aggregates_etl@airflow",
                inputs=[
                    f"{db}.fact_policies@postgres",
                ],
                outputs=[
                    f"{db}.gold_policies_by_customer@postgres",
                ],
            ),
        ]
    }


# =============================================================================
# CLAIMS — FACT TABLE
# =============================================================================

def build_claims_table_payload() -> Dict[str, Any]:
    """
    Build Atlas payload for claims fact table and ETL process.
    
    Documents the fact_claims table and its ETL process.
    
    Returns:
        Atlas payload dictionary with database, table, and process entities
    """
    db = "warehouse"

    return {
        "entities": [
            hive_db_payload(db),
            hive_table_payload(
                db_name=db,
                table_name="fact_claims",
            ),
            process_payload(
                name="claims_fact_etl",
                qualified_name="claims_fact_etl@airflow",
                inputs=[],
                outputs=[f"{db}.fact_claims@postgres"],
            ),
        ]
    }


# =============================================================================
# CLAIMS — AGGREGATES
# =============================================================================

def build_claims_aggregates_payload() -> Dict[str, Any]:
    """
    Build Atlas payload for claims aggregate table and ETL process.
    
    Documents the gold_claims_by_policy table and its aggregation process.
    
    Returns:
        Atlas payload dictionary with database, table, and process entities
    """
    db = "warehouse"

    return {
        "entities": [
            hive_db_payload(db),
            hive_table_payload(
                db_name=db,
                table_name="gold_claims_by_policy",
            ),
            process_payload(
                name="claims_aggregates_etl",
                qualified_name="claims_aggregates_etl@airflow",
                inputs=[
                    f"{db}.fact_claims@postgres",
                ],
                outputs=[
                    f"{db}.gold_claims_by_policy@postgres",
                ],
            ),
        ]
    }
