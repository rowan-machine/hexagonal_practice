"""
Database connection utility for analysts.

Provides a simple, analyst-friendly interface for connecting to the warehouse database.
Analysts should use this instead of directly importing DatabaseManager.
"""
from typing import Optional
from pathlib import Path
from src.utils.database import DatabaseManager
from src.mixins.logging import LoggingMixin


def get_db_connection(db_path: Optional[str] = None) -> DatabaseManager:
    """
    Get a database connection for analysts.
    
    This is the PRIMARY way analysts should connect to the database.
    It handles all the complexity internally.
    
    Args:
        db_path: Path to SQLite database. If None, uses default "warehouse.db"
                 in the current directory or project root.
    
    Returns:
        DatabaseManager instance ready to use
    
    Example:
        ```python
        from src.utils.db_connection import get_db_connection
        
        # Simple connection (uses default warehouse.db)
        db = get_db_connection()
        
        # Custom path
        db = get_db_connection(db_path="../warehouse.db")
        
        # Query data
        results = db.query("SELECT * FROM claims_silver LIMIT 10")
        ```
    
    Note:
        Analysts should prefer using SDK classes (ClaimsAnalyst, PoliciesAnalyst)
        over direct database access. This function is for cases where SDK doesn't
        provide the needed functionality.
    """
    if db_path is None:
        # Try to find warehouse.db in common locations
        current_dir = Path.cwd()
        possible_paths = [
            current_dir / "warehouse.db",
            current_dir.parent / "warehouse.db",
            current_dir / ".." / "warehouse.db",
        ]
        
        for path in possible_paths:
            if path.exists():
                db_path = str(path.resolve())
                break
        
        if db_path is None:
            # Default to warehouse.db in current directory
            db_path = "warehouse.db"
    
    return DatabaseManager(db_path=db_path)


def connect_to_warehouse(db_path: Optional[str] = None) -> DatabaseManager:
    """
    Alias for get_db_connection() for even simpler usage.
    
    Example:
        ```python
        from src.utils.db_connection import connect_to_warehouse
        
        db = connect_to_warehouse()
        results = db.query("SELECT * FROM claims_silver")
        ```
    """
    return get_db_connection(db_path)

