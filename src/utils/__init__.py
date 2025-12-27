"""
Utils package for cross-cutting utilities.
"""
from src.utils.io import DataReader, DataWriter, FileReader, FileWriter, DataAccessor
from src.utils.dataframe_ops import DataFrameOps
from src.utils.config_loader import ConfigLoader
from src.utils.database import DatabaseManager
from src.utils.db_connection import get_db_connection, connect_to_warehouse
from src.utils.atlas import AtlasClient
from src.utils.db_bootstrap import (
    DatabaseBootstrap,
    ensure_fact_policies_table,
    ensure_fact_claims_table,
    ensure_gold_policies_by_customer_table,
    ensure_gold_claims_by_policy_table
)
from src.utils.validation_loader import ValidationLoader

# SQL to Pandas converter (optional - requires sqlglot and pandas)
try:
    from src.utils.sql_to_pandas import SQLToPandasConverter
    __all__ = [
        "DataReader",
        "DataWriter",
        "FileReader",
        "FileWriter",
        "DataAccessor",
        "DataFrameOps",
        "ConfigLoader",
        "DatabaseManager",
        "get_db_connection",
        "connect_to_warehouse",
        "AtlasClient",
        "DatabaseBootstrap",
        "ensure_fact_policies_table",
        "ensure_fact_claims_table",
        "ensure_gold_policies_by_customer_table",
        "ensure_gold_claims_by_policy_table",
        "ValidationLoader",
        "SQLToPandasConverter",
    ]
except ImportError:
    # sqlglot or pandas not installed
    __all__ = [
        "DataReader",
        "DataWriter",
        "FileReader",
        "FileWriter",
        "DataAccessor",
        "DataFrameOps",
        "ConfigLoader",
        "DatabaseManager",
        "get_db_connection",
        "connect_to_warehouse",
        "AtlasClient",
        "DatabaseBootstrap",
        "ensure_fact_policies_table",
        "ensure_fact_claims_table",
        "ensure_gold_policies_by_customer_table",
        "ensure_gold_claims_by_policy_table",
        "ValidationLoader",
    ]

