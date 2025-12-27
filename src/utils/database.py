"""
Database utilities for SQLite warehouse operations.

Encapsulates database operations to keep them out of domain logic.
"""
import sqlite3
from typing import Any, List, Dict, Optional
from pathlib import Path
from contextlib import contextmanager
from src.mixins.logging import LoggingMixin


class DatabaseManager(LoggingMixin):
    """Manages SQLite database connections and schema."""
    
    def __init__(self, db_path: str = "warehouse.db"):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.db_path = Path(db_path)
        self._initialize_schema()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.log_error("Database operation failed", error=e)
            raise
        finally:
            conn.close()
    
    def _initialize_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        self.log_info("Initializing database schema", db_path=str(self.db_path))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Claims table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claims_bronze (
                    claim_id TEXT PRIMARY KEY,
                    policy_id TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    claim_amount REAL NOT NULL,
                    incurred_date TEXT NOT NULL,
                    paid_date TEXT,
                    status TEXT NOT NULL,
                    claim_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claims_silver (
                    claim_id TEXT PRIMARY KEY,
                    policy_id TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    claim_amount REAL NOT NULL,
                    incurred_date TEXT NOT NULL,
                    paid_date TEXT,
                    status TEXT NOT NULL,
                    claim_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claims_gold (
                    policy_id TEXT NOT NULL,
                    total_claims REAL NOT NULL,
                    claim_count INTEGER NOT NULL,
                    avg_claim_amount REAL,
                    max_claim_amount REAL,
                    min_claim_amount REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (policy_id, created_at)
                )
            """)
            
            # Policies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies_bronze (
                    policy_id TEXT PRIMARY KEY,
                    employer_id TEXT NOT NULL,
                    effective_date TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    stop_loss_limit REAL NOT NULL,
                    aggregate_deductible REAL NOT NULL,
                    specific_deductible REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies_silver (
                    policy_id TEXT PRIMARY KEY,
                    employer_id TEXT NOT NULL,
                    effective_date TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    stop_loss_limit REAL NOT NULL,
                    aggregate_deductible REAL NOT NULL,
                    specific_deductible REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies_gold (
                    employer_id TEXT NOT NULL,
                    total_coverage REAL NOT NULL,
                    policy_count INTEGER NOT NULL,
                    avg_stop_loss_limit REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (employer_id, created_at)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_claims_policy 
                ON claims_silver(policy_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_claims_member 
                ON claims_silver(member_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_claims_status 
                ON claims_silver(status)
            """)
            
            self.log_info("Database schema initialized")
    
    def insert_claims_bronze(self, claims: List[Dict[str, Any]]) -> None:
        """Insert claims into bronze table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO claims_bronze 
                (claim_id, policy_id, member_id, claim_amount, incurred_date, 
                 paid_date, status, claim_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    c.get("claim_id"),
                    c.get("policy_id"),
                    c.get("member_id"),
                    float(c.get("claim_amount", 0)),
                    c.get("incurred_date"),
                    c.get("paid_date"),
                    c.get("status"),
                    c.get("claim_type", "medical")
                )
                for c in claims
            ])
            self.log_info(f"Inserted {len(claims)} claims into bronze table")
    
    def insert_claims_silver(self, claims: List[Dict[str, Any]]) -> None:
        """Insert claims into silver table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO claims_silver 
                (claim_id, policy_id, member_id, claim_amount, incurred_date, 
                 paid_date, status, claim_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    c.get("claim_id"),
                    c.get("policy_id"),
                    c.get("member_id"),
                    float(c.get("claim_amount", 0)),
                    c.get("incurred_date"),
                    c.get("paid_date"),
                    c.get("status"),
                    c.get("claim_type", "medical")
                )
                for c in claims
            ])
            self.log_info(f"Inserted {len(claims)} claims into silver table")
    
    def insert_claims_gold(self, aggregated: List[Dict[str, Any]]) -> None:
        """
        Insert aggregated claims into gold table.
        
        Uses INSERT OR REPLACE to ensure idempotency - running the pipeline
        multiple times will update existing records rather than creating duplicates.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for agg in aggregated:
                cursor.execute("""
                    INSERT OR REPLACE INTO claims_gold 
                    (policy_id, total_claims, claim_count, avg_claim_amount, 
                     max_claim_amount, min_claim_amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    agg.get("policy_id"),
                    float(agg.get("total_claims", 0)),
                    int(agg.get("claim_count", 0)),
                    float(agg.get("avg_claim_amount", 0)) if agg.get("avg_claim_amount") else None,
                    float(agg.get("max_claim_amount", 0)) if agg.get("max_claim_amount") else None,
                    float(agg.get("min_claim_amount", 0)) if agg.get("min_claim_amount") else None
                ))
            self.log_info(f"Inserted/updated {len(aggregated)} aggregated claims into gold table")
    
    def insert_policies_bronze(self, policies: List[Dict[str, Any]]) -> None:
        """Insert policies into bronze table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO policies_bronze 
                (policy_id, employer_id, effective_date, expiration_date, 
                 stop_loss_limit, aggregate_deductible, specific_deductible, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    p.get("policy_id"),
                    p.get("employer_id"),
                    p.get("effective_date"),
                    p.get("expiration_date"),
                    float(p.get("stop_loss_limit", 0)),
                    float(p.get("aggregate_deductible", 0)),
                    float(p.get("specific_deductible", 0)),
                    p.get("status")
                )
                for p in policies
            ])
            self.log_info(f"Inserted {len(policies)} policies into bronze table")
    
    def insert_policies_silver(self, policies: List[Dict[str, Any]]) -> None:
        """Insert policies into silver table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO policies_silver 
                (policy_id, employer_id, effective_date, expiration_date, 
                 stop_loss_limit, aggregate_deductible, specific_deductible, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    p.get("policy_id"),
                    p.get("employer_id"),
                    p.get("effective_date"),
                    p.get("expiration_date"),
                    float(p.get("stop_loss_limit", 0)),
                    float(p.get("aggregate_deductible", 0)),
                    float(p.get("specific_deductible", 0)),
                    p.get("status")
                )
                for p in policies
            ])
            self.log_info(f"Inserted {len(policies)} policies into silver table")
    
    def insert_policies_gold(self, aggregated: List[Dict[str, Any]]) -> None:
        """
        Insert aggregated policies into gold table.
        
        Uses INSERT OR REPLACE to ensure idempotency - running the pipeline
        multiple times will update existing records rather than creating duplicates.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for agg in aggregated:
                cursor.execute("""
                    INSERT OR REPLACE INTO policies_gold 
                    (employer_id, total_coverage, policy_count, avg_stop_loss_limit)
                    VALUES (?, ?, ?, ?)
                """, (
                    agg.get("employer_id"),
                    float(agg.get("total_coverage", 0)),
                    int(agg.get("policy_count", 0)),
                    float(agg.get("avg_stop_loss_limit", 0)) if agg.get("avg_stop_loss_limit") else None
                ))
            self.log_info(f"Inserted/updated {len(aggregated)} aggregated policies into gold table")
    
    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

