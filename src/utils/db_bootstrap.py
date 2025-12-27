"""
Database bootstrap utilities for creating warehouse tables.

Supports both PostgreSQL (for production) and SQLite (for local development).
All table schemas match the Atlas metadata definitions.
"""
from typing import Union, Any
import sqlite3
from src.mixins.logging import LoggingMixin

# Try to import psycopg2, but make it optional for SQLite-only usage
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None


class DatabaseBootstrap(LoggingMixin):
    """
    Bootstrap database tables for warehouse.
    
    Supports both PostgreSQL and SQLite connections.
    """
    
    def __init__(self):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
    
    def ensure_all_tables(self, conn: Union[sqlite3.Connection, Any]) -> None:
        """
        Ensure all warehouse tables exist.
        
        Args:
            conn: Database connection (sqlite3.Connection or psycopg2 connection)
        """
        self.log_info("Bootstrapping all warehouse tables")
        ensure_fact_policies_table(conn)
        ensure_fact_claims_table(conn)
        ensure_gold_policies_by_customer_table(conn)
        ensure_gold_claims_by_policy_table(conn)
        self.log_info("All warehouse tables bootstrapped")


# =============================================================================
# FACT TABLES
# =============================================================================

def ensure_fact_policies_table(conn: Union[sqlite3.Connection, Any]) -> None:
    """
    Ensure fact_policies table exists.

    Row-level, business-truth policies table.
    Matches Atlas metadata definition.
    
    Args:
        conn: Database connection (SQLite or PostgreSQL)
    """
    cur = conn.cursor()
    
    # Use appropriate SQL syntax based on connection type
    if isinstance(conn, sqlite3.Connection):
        # SQLite syntax
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_policies (
                policy_id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                line_of_business TEXT,
                effective_date TEXT,
                premium_usd REAL
            )
            """
        )
    else:
        # PostgreSQL syntax
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_policies (
                policy_id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                line_of_business TEXT,
                effective_date DATE,
                premium_usd NUMERIC
            )
            """
        )

    conn.commit()
    cur.close()


def ensure_fact_claims_table(conn: Union[sqlite3.Connection, Any]) -> None:
    """
    Ensure fact_claims table exists.

    Row-level, business-truth claims table.
    Matches Atlas metadata definition.
    
    Args:
        conn: Database connection (SQLite or PostgreSQL)
    """
    cur = conn.cursor()
    
    if isinstance(conn, sqlite3.Connection):
        # SQLite syntax
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_claims (
                claim_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                claim_amount_usd REAL,
                status TEXT,
                claim_date TEXT
            )
            """
        )
    else:
        # PostgreSQL syntax
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_claims (
                claim_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                claim_amount_usd NUMERIC,
                status TEXT,
                claim_date DATE
            )
            """
        )

    conn.commit()
    cur.close()


# =============================================================================
# GOLD AGGREGATE TABLES
# =============================================================================

def ensure_gold_policies_by_customer_table(conn: Union[sqlite3.Connection, Any]) -> None:
    """
    Ensure gold_policies_by_customer aggregate table exists.
    
    Matches Atlas metadata definition.
    
    Args:
        conn: Database connection (SQLite or PostgreSQL)
    """
    cur = conn.cursor()
    
    if isinstance(conn, sqlite3.Connection):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_policies_by_customer (
                customer TEXT PRIMARY KEY,
                premium_usd REAL
            )
            """
        )
    else:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_policies_by_customer (
                customer TEXT PRIMARY KEY,
                premium_usd NUMERIC
            )
            """
        )

    conn.commit()
    cur.close()


def ensure_gold_claims_by_policy_table(conn: Union[sqlite3.Connection, Any]) -> None:
    """
    Ensure gold_claims_by_policy aggregate table exists.
    
    Matches Atlas metadata definition and business rules aggregation.
    
    Args:
        conn: Database connection (SQLite or PostgreSQL)
    """
    cur = conn.cursor()
    
    if isinstance(conn, sqlite3.Connection):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_claims_by_policy (
                policy_id TEXT PRIMARY KEY,
                claim_amount_usd REAL,
                claim_count INTEGER
            )
            """
        )
    else:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_claims_by_policy (
                policy_id TEXT PRIMARY KEY,
                claim_amount_usd NUMERIC,
                claim_count INTEGER
            )
            """
        )

    conn.commit()
    cur.close()
