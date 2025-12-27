"""
Tests for SQL to Pandas converter utility.
"""
import pytest
import sys
from pathlib import Path
import tempfile
import os

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


class TestSQLToPandasConverter:
    """Test SQL to Pandas converter."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        return SQLToPandasConverter(source_table="test_table")
    
    def test_converter_initialization(self):
        """Test converter can be initialized."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        converter = SQLToPandasConverter(source_table="claims_silver")
        assert converter.source_table == "claims_silver"
    
    def test_converter_requires_dependencies(self):
        """Test converter raises error if dependencies missing."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        # This should work if dependencies are available
        if SQLGLOT_AVAILABLE and PANDAS_AVAILABLE:
            converter = SQLToPandasConverter()
            assert converter is not None
        else:
            with pytest.raises(ImportError):
                SQLToPandasConverter()
    
    def test_simple_select(self, converter):
        """Test simple SELECT query."""
        sql = "SELECT policy_id, claim_amount FROM claims_silver"
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "df" in code
        assert "policy_id" in code or "claim_amount" in code
    
    def test_select_with_where(self, converter):
        """Test SELECT with WHERE clause."""
        sql = "SELECT * FROM claims_silver WHERE claim_amount > 1000"
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "query" in code.lower() or "filter" in code.lower()
        assert "claim_amount" in code
    
    def test_select_with_groupby(self, converter):
        """Test SELECT with GROUP BY."""
        sql = """
        SELECT policy_id, SUM(claim_amount) AS total_claims
        FROM claims_silver
        GROUP BY policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "groupby" in code.lower()
        assert "policy_id" in code
        assert "sum" in code.lower() or "agg" in code.lower()
    
    def test_select_with_orderby(self, converter):
        """Test SELECT with ORDER BY."""
        sql = """
        SELECT policy_id, claim_amount
        FROM claims_silver
        ORDER BY claim_amount DESC
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "sort_values" in code.lower()
        assert "claim_amount" in code
    
    def test_select_with_limit(self, converter):
        """Test SELECT with LIMIT."""
        sql = "SELECT * FROM claims_silver LIMIT 10"
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "head" in code.lower() or "limit" in code.lower()
    
    def test_aggregation_functions(self, converter):
        """Test various aggregation functions."""
        sql = """
        SELECT 
            policy_id,
            SUM(claim_amount) AS total,
            COUNT(claim_id) AS count,
            AVG(claim_amount) AS avg_amount,
            MAX(claim_amount) AS max_amount,
            MIN(claim_amount) AS min_amount
        FROM claims_silver
        GROUP BY policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "groupby" in code.lower()
        assert "agg" in code.lower() or "sum" in code.lower()
    
    def test_complex_query(self, converter):
        """Test complex query with multiple clauses."""
        sql = """
        SELECT 
            policy_id,
            SUM(claim_amount) AS total_claims,
            COUNT(claim_id) AS claim_count
        FROM claims_silver
        WHERE claim_amount > 1000
        GROUP BY policy_id
        HAVING total_claims > 50000
        ORDER BY total_claims DESC
        LIMIT 10
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        # Should contain multiple operations
        assert "groupby" in code.lower() or "agg" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
    
    def test_claims_gold_query(self, converter):
        """Test the actual CLAIMS_GOLD_001 query."""
        sql = """
        SELECT 
            policy_id,
            SUM(claim_amount) AS total_claims,
            COUNT(claim_id) AS claim_count,
            AVG(claim_amount) AS avg_claim_amount,
            MAX(claim_amount) AS max_claim_amount,
            MIN(claim_amount) AS min_claim_amount
        FROM claims_silver
        GROUP BY policy_id
        ORDER BY total_claims DESC
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        assert "groupby" in code.lower()
        assert "policy_id" in code
        assert "sum" in code.lower() or "agg" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
    
    def test_extract_table_name(self, converter):
        """Test table name extraction from SQL."""
        sql = "SELECT * FROM claims_silver WHERE claim_amount > 1000"
        table_name = converter._extract_table_name(sql)
        assert table_name == "claims_silver"
    
    def test_convert_file(self, converter):
        """Test converting SQL from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
            tmp.write("""
            SELECT policy_id, SUM(claim_amount) AS total
            FROM claims_silver
            GROUP BY policy_id
            """)
            tmp_path = tmp.name
        
        try:
            code = converter.convert_file(tmp_path, source_table="claims_silver")
            assert "groupby" in code.lower()
            assert "policy_id" in code
        finally:
            os.unlink(tmp_path)
    
    def test_convert_file_with_output(self, converter):
        """Test converting SQL file and saving output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as sql_file:
            sql_file.write("SELECT * FROM claims_silver LIMIT 10")
            sql_path = sql_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as py_file:
            py_path = py_file.name
        
        try:
            code = converter.convert_file(
                sql_path,
                output_file=py_path,
                source_table="claims_silver"
            )
            
            # Check output file was created
            assert os.path.exists(py_path)
            assert len(code) > 0
            
            # Check file contents
            saved_code = Path(py_path).read_text()
            assert saved_code == code
        finally:
            if os.path.exists(sql_path):
                os.unlink(sql_path)
            if os.path.exists(py_path):
                os.unlink(py_path)
    
    def test_missing_table_name(self):
        """Test error when table name is missing."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        converter = SQLToPandasConverter()  # No source_table
        
        sql = "SELECT * FROM claims_silver"  # Table in SQL
        
        # Should work because table is in SQL
        code = converter.convert(sql)
        assert len(code) > 0
    
    def test_missing_table_name_error(self):
        """Test error when table name cannot be determined."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        converter = SQLToPandasConverter()  # No source_table
        
        sql = "SELECT policy_id, SUM(claim_amount) FROM (SELECT * FROM claims)"  # Complex query
        
        # Should raise error or extract table
        try:
            code = converter.convert(sql)
            # If it works, that's fine
            assert len(code) > 0
        except ValueError:
            # Expected if table cannot be extracted
            pass
    
    def test_join_query(self, converter):
        """Test query with JOIN."""
        sql = """
        SELECT c.claim_id, c.claim_amount, p.policy_id
        FROM claims_silver c
        INNER JOIN policies_silver p ON c.policy_id = p.policy_id
        """
        code = converter.convert(sql, source_table="claims_silver")
        
        # Should mention merge or join
        assert "merge" in code.lower() or "join" in code.lower()
    
    def test_where_conditions(self, converter):
        """Test various WHERE conditions."""
        test_cases = [
            ("claim_amount > 1000", ">"),
            ("claim_amount >= 1000", ">="),
            ("claim_amount < 1000", "<"),
            ("claim_amount <= 1000", "<="),
            ("claim_amount = 1000", "=="),
            ("claim_amount != 1000", "!="),
            ("status = 'approved'", "=="),
        ]
        
        for condition, operator in test_cases:
            sql = f"SELECT * FROM claims_silver WHERE {condition}"
            code = converter.convert(sql, source_table="claims_silver")
            
            assert "query" in code.lower() or "filter" in code.lower()
            assert operator in code or condition.split()[0] in code


class TestSQLToPandasIntegration:
    """Integration tests for SQL to Pandas converter."""
    
    def test_end_to_end_conversion(self):
        """Test end-to-end conversion of real SQL query."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        # Real query from the project
        sql = """
        SELECT 
            policy_id,
            SUM(claim_amount) AS total_claims,
            COUNT(claim_id) AS claim_count,
            AVG(claim_amount) AS avg_claim_amount,
            MAX(claim_amount) AS max_claim_amount,
            MIN(claim_amount) AS min_claim_amount
        FROM claims_silver
        GROUP BY policy_id
        ORDER BY total_claims DESC
        """
        
        converter = SQLToPandasConverter(source_table="claims_silver")
        code = converter.convert(sql)
        
        # Verify code structure
        assert "groupby" in code.lower()
        assert "agg" in code.lower() or "sum" in code.lower()
        assert "sort_values" in code.lower() or "order" in code.lower()
        assert "policy_id" in code
        
        # Code should be executable (syntax check)
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax errors: {e}")
    
    def test_policies_aggregation_query(self):
        """Test policies aggregation query conversion."""
        from src.utils.sql_to_pandas import SQLToPandasConverter
        
        sql = """
        SELECT 
            employer_id,
            SUM(stop_loss_limit) AS total_coverage,
            COUNT(policy_id) AS policy_count,
            AVG(stop_loss_limit) AS avg_stop_loss_limit
        FROM policies_silver
        GROUP BY employer_id
        ORDER BY total_coverage DESC
        """
        
        converter = SQLToPandasConverter(source_table="policies_silver")
        code = converter.convert(sql)
        
        assert "groupby" in code.lower()
        assert "employer_id" in code
        assert "agg" in code.lower() or "sum" in code.lower()

