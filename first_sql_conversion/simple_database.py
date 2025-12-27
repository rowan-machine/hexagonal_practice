"""
Simplified Database Manager - SQLite Operations Only

This is a simplified version that just handles basic database operations.
No complex logging or connection pooling.
"""
import sqlite3
from typing import List, Dict, Any
from pathlib import Path


class SimpleDatabaseManager:
    """Simple SQLite database manager."""
    
    def __init__(self, db_path: str = "example_warehouse.db"):
        self.db_path = Path(db_path)
        self._initialize_schema()
    
    def _initialize_schema(self) -> None:
        """Create tables if they don't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Claims silver table (input for aggregation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims_silver (
                claim_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                claim_amount REAL NOT NULL,
                incurred_date TEXT NOT NULL,
                paid_date TEXT,
                status TEXT NOT NULL,
                claim_type TEXT
            )
        """)
        
        # Claims gold table (output of aggregation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims_gold (
                policy_id TEXT NOT NULL,
                total_claims REAL NOT NULL,
                claim_count INTEGER NOT NULL,
                avg_claim_amount REAL,
                max_claim_amount REAL,
                min_claim_amount REAL,
                PRIMARY KEY (policy_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_claims_silver(self, claims: List[Dict[str, Any]]) -> None:
        """Insert claims into silver table."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for claim in claims:
            cursor.execute("""
                INSERT OR REPLACE INTO claims_silver 
                (claim_id, policy_id, member_id, claim_amount, 
                 incurred_date, paid_date, status, claim_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim.get("claim_id"),
                claim.get("policy_id"),
                claim.get("member_id"),
                float(claim.get("claim_amount", 0)),
                claim.get("incurred_date"),
                claim.get("paid_date"),
                claim.get("status"),
                claim.get("claim_type")
            ))
        
        conn.commit()
        conn.close()
    
    def get_claims_silver(self) -> List[Dict[str, Any]]:
        """Get all claims from silver table."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM claims_silver")
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert to list of dictionaries
        return [dict(row) for row in rows]
    
    def insert_claims_gold(self, aggregated: List[Dict[str, Any]]) -> None:
        """Insert aggregated claims into gold table."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for agg in aggregated:
            cursor.execute("""
                INSERT OR REPLACE INTO claims_gold 
                (policy_id, total_claims, claim_count, 
                 avg_claim_amount, max_claim_amount, min_claim_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agg.get("policy_id"),
                float(agg.get("total_claims", 0)),
                int(agg.get("claim_count", 0)),
                float(agg.get("avg_claim_amount", 0)),
                float(agg.get("max_claim_amount", 0)),
                float(agg.get("min_claim_amount", 0))
            ))
        
        conn.commit()
        conn.close()
    
    def get_claims_gold(self) -> List[Dict[str, Any]]:
        """Get all aggregated claims from gold table."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM claims_gold ORDER BY total_claims DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]

