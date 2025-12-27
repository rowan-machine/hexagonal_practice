"""
Tests for SQL to Pandas converter CTE (WITH clause) support.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path if package not installed
try:
    pass
except ImportError:
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Check if dependencies are available
try:
    import sqlglot
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

if not SQLGLOT_AVAILABLE or not PANDAS_AVAILABLE:
    pytestmark = pytest.mark.skip(
        reason="sqlglot and pandas required. Install with: pip install sqlglot pandas"
    )


class TestSQLToPandasCTE:
    """Test SQL to Pandas converter CTE support."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        return SQLToPandasConverter(source_table="test_table")
    
    def test_simple_cte(self, converter):
        """Test simple CTE."""
        sql = """
        WITH filtered_claims AS (
            SELECT * FROM claims_silver WHERE claim_amount > 1000
        )
        SELECT policy_id, SUM(claim_amount) AS total
        FROM filtered_claims
        GROUP BY policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "CTE" in code or "cte_" in code.lower()
        assert "filtered_claims" in code
        assert "groupby" in code.lower()
    
    def test_multiple_ctes(self, converter):
        """Test multiple CTEs."""
        sql = """
        WITH 
            filtered_claims AS (
                SELECT * FROM claims_silver WHERE claim_amount > 1000
            ),
            aggregated AS (
                SELECT policy_id, SUM(claim_amount) AS total
                FROM filtered_claims
                GROUP BY policy_id
            )
        SELECT * FROM aggregated ORDER BY total DESC
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "filtered_claims" in code
        assert "aggregated" in code
        assert "groupby" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
    
    def test_cte_with_aggregation(self, converter):
        """Test CTE with aggregation."""
        sql = """
        WITH policy_totals AS (
            SELECT 
                policy_id,
                SUM(claim_amount) AS total_claims,
                COUNT(claim_id) AS claim_count
            FROM claims_silver
            GROUP BY policy_id
        )
        SELECT * FROM policy_totals WHERE total_claims > 50000
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "policy_totals" in code
        assert "groupby" in code.lower()
        assert "query" in code.lower() or "filter" in code.lower()
    
    def test_nested_cte(self, converter):
        """Test nested CTE (CTE that references another CTE)."""
        sql = """
        WITH 
            base_data AS (
                SELECT * FROM claims_silver WHERE status = 'approved'
            ),
            aggregated AS (
                SELECT 
                    policy_id,
                    SUM(claim_amount) AS total
                FROM base_data
                GROUP BY policy_id
            )
        SELECT * FROM aggregated ORDER BY total DESC LIMIT 10
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "base_data" in code
        assert "aggregated" in code
        assert "groupby" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
    
    def test_cte_with_join(self, converter):
        """Test CTE with JOIN."""
        sql = """
        WITH 
            claims_summary AS (
                SELECT policy_id, SUM(claim_amount) AS total_claims
                FROM claims_silver
                GROUP BY policy_id
            ),
            policies_info AS (
                SELECT policy_id, employer_id, stop_loss_limit
                FROM policies_silver
            )
        SELECT 
            c.policy_id,
            c.total_claims,
            p.employer_id,
            p.stop_loss_limit
        FROM claims_summary c
        INNER JOIN policies_info p ON c.policy_id = p.policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "claims_summary" in code
        assert "policies_info" in code
        assert "merge" in code.lower() or "join" in code.lower()
    
    def test_extract_ctes(self, converter):
        """Test CTE extraction."""
        from sqlglot import parse_one
        
        sql = """
        WITH filtered AS (
            SELECT * FROM claims_silver WHERE claim_amount > 1000
        )
        SELECT * FROM filtered
        """
        
        ast = parse_one(sql)
        ctes = converter._extract_ctes(ast)
        
        assert len(ctes) > 0
        assert ctes[0]['name'] == 'filtered'
        assert ctes[0]['query'] is not None
    
    def test_cte_in_complex_query(self, converter):
        """Test CTE in complex query with all clauses."""
        sql = """
        WITH 
            high_value_claims AS (
                SELECT 
                    policy_id,
                    claim_id,
                    claim_amount,
                    incurred_date
                FROM claims_silver
                WHERE claim_amount > 50000
            ),
            policy_summary AS (
                SELECT 
                    policy_id,
                    SUM(claim_amount) AS total_claims,
                    COUNT(claim_id) AS claim_count,
                    MAX(claim_amount) AS max_claim
                FROM high_value_claims
                GROUP BY policy_id
                HAVING total_claims > 100000
            )
        SELECT 
            policy_id,
            total_claims,
            claim_count,
            max_claim
        FROM policy_summary
        ORDER BY total_claims DESC
        LIMIT 20
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "high_value_claims" in code
        assert "policy_summary" in code
        assert "groupby" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
    
    def test_cte_with_subquery(self, converter):
        """Test CTE that contains a subquery."""
        sql = """
        WITH 
            recent_claims AS (
                SELECT * FROM claims_silver 
                WHERE incurred_date >= (
                    SELECT MAX(incurred_date) - INTERVAL '30 days' 
                    FROM claims_silver
                )
            )
        SELECT policy_id, SUM(claim_amount) AS total
        FROM recent_claims
        GROUP BY policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        # Should at least handle the CTE structure
        assert "recent_claims" in code
        assert "groupby" in code.lower()

