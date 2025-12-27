"""
SQL to Pandas Converter Utility.

Converts SQL queries to pandas operations using sqlglot for parsing
and generating equivalent pandas code.

This utility is designed to help migrate SQL-based business logic
to Python/pandas implementations.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import re

try:
    import sqlglot
    from sqlglot import parse_one, exp
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SQLToPandasConverter:
    """
    Converts SQL queries to pandas operations.
    
    Example:
        >>> converter = SQLToPandasConverter()
        >>> sql = "SELECT policy_id, SUM(claim_amount) FROM claims GROUP BY policy_id"
        >>> pandas_code = converter.convert(sql, source_table="claims")
        >>> print(pandas_code)
        df.groupby('policy_id').agg({'claim_amount': 'sum'}).reset_index()
    """
    
    def __init__(self, source_table: Optional[str] = None):
        """
        Initialize converter.
        
        Args:
            source_table: Default source table name (can be overridden in convert())
        """
        if not SQLGLOT_AVAILABLE:
            raise ImportError(
                "sqlglot is required. Install with: pip install sqlglot"
            )
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas is required. Install with: pip install pandas"
            )
        
        self.source_table = source_table
        self._table_mapping: Dict[str, str] = {}
    
    def convert(
        self,
        sql: str,
        source_table: Optional[str] = None,
        df_name: str = "df",
        return_code: bool = True
    ) -> Union[str, pd.DataFrame]:
        """
        Convert SQL query to pandas code or execute directly.
        
        Args:
            sql: SQL query string
            source_table: Source table name (overrides default)
            df_name: Name of the pandas DataFrame variable
            return_code: If True, return code string; if False, execute and return DataFrame
            
        Returns:
            If return_code=True: Python code string
            If return_code=False: pandas DataFrame (requires source DataFrame)
            
        Raises:
            ValueError: If SQL cannot be parsed or converted
        """
        source_table = source_table or self.source_table
        if not source_table:
            # Try to extract from SQL
            source_table = self._extract_table_name(sql)
        
        if not source_table:
            raise ValueError(
                "Source table name is required. "
                "Provide via source_table parameter or set in __init__"
            )
        
        try:
            # Parse SQL into AST
            ast = parse_one(sql)
            
            # Convert AST to pandas operations
            if return_code:
                return self._generate_pandas_code(ast, source_table, df_name)
            else:
                return self._execute_pandas(ast, source_table, df_name)
        
        except Exception as e:
            raise ValueError(f"Failed to convert SQL: {str(e)}") from e
    
    def _extract_table_name(self, sql: str) -> Optional[str]:
        """Extract table name from SQL query."""
        # Simple regex extraction (fallback)
        patterns = [
            r'FROM\s+(\w+)',
            r'from\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'join\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_pandas_code(
        self,
        ast: exp.Expression,
        source_table: str,
        df_name: str
    ) -> str:
        """Generate pandas code from SQL AST."""
        operations = []
        cte_operations = []
        
        # Process CTEs (WITH clauses) first
        ctes = self._extract_ctes(ast)
        if ctes:
            # Generate code for each CTE
            for i, cte in enumerate(ctes):
                cte_name = cte['name']
                cte_query = cte['query']
                cte_df_name = f"cte_{cte_name.lower()}"
                
                # Recursively convert the CTE query
                cte_code = self._generate_pandas_code(
                    cte_query,
                    source_table,
                    cte_df_name
                )
                cte_operations.append(f"# CTE: {cte_name}")
                cte_operations.append(cte_code)
                cte_operations.append(f"{cte_name} = {cte_df_name}  # Alias for CTE")
                cte_operations.append("")
        
        # Start with DataFrame
        operations.append(f"{df_name} = pd.DataFrame()  # Load from {source_table}")
        
        # Process SELECT
        select_exprs = self._extract_select(ast)
        if select_exprs:
            operations.append(self._generate_select(select_exprs, df_name))
        
        # Process FROM - check if it references a CTE
        from_table = self._extract_from(ast) or source_table
        if from_table:
            # Check if FROM references a CTE
            if ctes and from_table in [cte['name'] for cte in ctes]:
                # Use the CTE DataFrame
                operations[0] = f"{df_name} = {from_table}.copy()  # Use CTE"
            else:
                operations[0] = f"{df_name} = load_dataframe('{from_table}')  # Replace with actual data loading"
        
        # Process WHERE
        where_expr = self._extract_where(ast)
        if where_expr:
            operations.append(self._generate_where(where_expr, df_name))
        
        # Process JOIN
        joins = self._extract_joins(ast)
        for join in joins:
            operations.append(self._generate_join(join, df_name))
        
        # Process GROUP BY
        group_by = self._extract_group_by(ast)
        if group_by:
            operations.append(self._generate_groupby(group_by, select_exprs, df_name))
        
        # Process ORDER BY
        order_by = self._extract_order_by(ast)
        if order_by:
            operations.append(self._generate_orderby(order_by, df_name))
        
        # Process LIMIT
        limit = self._extract_limit(ast)
        if limit:
            operations.append(self._generate_limit(limit, df_name))
        
        # Combine CTE operations and main query operations
        all_operations = cte_operations + operations if cte_operations else operations
        
        return "\n".join(all_operations)
    
    def _extract_select(self, ast: exp.Expression) -> List[exp.Expression]:
        """Extract SELECT expressions from AST."""
        selects = []
        for node in ast.walk():
            if isinstance(node, exp.Select):
                selects.extend(node.expressions)
        return selects
    
    def _extract_from(self, ast: exp.Expression) -> Optional[str]:
        """Extract FROM table name."""
        # Handle With expressions - extract FROM from main query
        if isinstance(ast, exp.With):
            main_query = ast.this
            if isinstance(main_query, exp.Select):
                for node in main_query.walk():
                    if isinstance(node, exp.From):
                        for table in node.expressions:
                            if isinstance(table, exp.Table):
                                return table.name
                            elif isinstance(table, exp.Identifier):
                                # Could be a CTE reference
                                return table.name
        else:
            # Regular query
            for node in ast.walk():
                if isinstance(node, exp.From):
                    for table in node.expressions:
                        if isinstance(table, exp.Table):
                            return table.name
                        elif isinstance(table, exp.Identifier):
                            # Could be a CTE reference
                            return table.name
        return None
    
    def _extract_where(self, ast: exp.Expression) -> Optional[exp.Expression]:
        """Extract WHERE expression."""
        # Handle With expressions - extract WHERE from main query
        if isinstance(ast, exp.With):
            main_query = ast.this
            if isinstance(main_query, exp.Select):
                for node in main_query.walk():
                    if isinstance(node, exp.Where):
                        return node.this
        else:
            # Regular query
            for node in ast.walk():
                if isinstance(node, exp.Where):
                    return node.this
        return None
    
    def _extract_joins(self, ast: exp.Expression) -> List[Dict[str, Any]]:
        """Extract JOIN expressions."""
        joins = []
        for node in ast.walk():
            if isinstance(node, exp.Join):
                join_info = {
                    'type': node.kind or 'INNER',
                    'table': None,
                    'condition': None
                }
                if node.this:
                    if isinstance(node.this, exp.Table):
                        join_info['table'] = node.this.name
                if node.on:
                    join_info['condition'] = node.on
                joins.append(join_info)
        return joins
    
    def _extract_group_by(self, ast: exp.Expression) -> List[str]:
        """Extract GROUP BY columns."""
        group_by = []
        # Handle With expressions - extract GROUP BY from main query
        if isinstance(ast, exp.With):
            main_query = ast.this
            if isinstance(main_query, exp.Select):
                for node in main_query.walk():
                    if isinstance(node, exp.Group):
                        for expr in node.expressions:
                            if isinstance(expr, exp.Column):
                                group_by.append(expr.name)
                            elif isinstance(expr, exp.Identifier):
                                group_by.append(expr.name)
        else:
            # Regular query
            for node in ast.walk():
                if isinstance(node, exp.Group):
                    for expr in node.expressions:
                        if isinstance(expr, exp.Column):
                            group_by.append(expr.name)
                        elif isinstance(expr, exp.Identifier):
                            group_by.append(expr.name)
        return group_by
    
    def _extract_order_by(self, ast: exp.Expression) -> List[Dict[str, Any]]:
        """Extract ORDER BY expressions."""
        order_by = []
        # Handle With expressions - extract ORDER BY from main query
        if isinstance(ast, exp.With):
            main_query = ast.this
            if isinstance(main_query, exp.Select):
                for node in main_query.walk():
                    if isinstance(node, exp.Order):
                        for expr in node.expressions:
                            order_info = {
                                'column': None,
                                'asc': True
                            }
                            if isinstance(expr, exp.Ordered):
                                if isinstance(expr.this, exp.Column):
                                    order_info['column'] = expr.this.name
                                elif isinstance(expr.this, exp.Identifier):
                                    order_info['column'] = expr.this.name
                                order_info['asc'] = expr.args.get('desc', False) is False
                            elif isinstance(expr, exp.Column):
                                order_info['column'] = expr.name
                            order_by.append(order_info)
        else:
            # Regular query
            for node in ast.walk():
                if isinstance(node, exp.Order):
                    for expr in node.expressions:
                        order_info = {
                            'column': None,
                            'asc': True
                        }
                        if isinstance(expr, exp.Ordered):
                            if isinstance(expr.this, exp.Column):
                                order_info['column'] = expr.this.name
                            elif isinstance(expr.this, exp.Identifier):
                                order_info['column'] = expr.this.name
                            order_info['asc'] = expr.args.get('desc', False) is False
                        elif isinstance(expr, exp.Column):
                            order_info['column'] = expr.name
                        order_by.append(order_info)
        return order_by
    
    def _extract_limit(self, ast: exp.Expression) -> Optional[int]:
        """Extract LIMIT value."""
        # Handle With expressions - extract LIMIT from main query
        if isinstance(ast, exp.With):
            main_query = ast.this
            if isinstance(main_query, exp.Select):
                for node in main_query.walk():
                    if isinstance(node, exp.Limit):
                        if node.expression:
                            try:
                                return int(node.expression.this)
                            except (AttributeError, ValueError):
                                pass
        else:
            # Regular query
            for node in ast.walk():
                if isinstance(node, exp.Limit):
                    if node.expression:
                        try:
                            return int(node.expression.this)
                        except (AttributeError, ValueError):
                            pass
        return None
    
    def _generate_select(self, select_exprs: List[exp.Expression], df_name: str) -> str:
        """Generate pandas code for SELECT."""
        columns = []
        aggregations = {}
        
        for expr in select_exprs:
            if isinstance(expr, exp.Alias):
                alias = expr.alias
                col_expr = expr.this
            else:
                alias = None
                col_expr = expr
            
            # Check for aggregations
            if isinstance(col_expr, exp.AggFunc):
                func_name = col_expr.sql_name().lower()
                if isinstance(col_expr.this, exp.Column):
                    col_name = col_expr.this.name
                    if alias:
                        aggregations[col_name] = (func_name, alias)
                    else:
                        aggregations[col_name] = (func_name, None)
            elif isinstance(col_expr, exp.Column):
                col_name = col_expr.name
                if alias:
                    columns.append(f"'{col_name}': '{alias}'")
                else:
                    columns.append(f"'{col_name}'")
        
        if aggregations:
            # This will be handled in groupby
            return f"# Aggregations: {aggregations}"
        
        if columns:
            return f"{df_name} = {df_name}[[{', '.join(columns)}]]"
        
        return f"# SELECT: {select_exprs}"
    
    def _generate_where(self, where_expr: exp.Expression, df_name: str) -> str:
        """Generate pandas code for WHERE clause."""
        condition = self._expression_to_pandas(where_expr)
        return f"{df_name} = {df_name}.query({condition!r})"
    
    def _generate_join(
        self,
        join_info: Dict[str, Any],
        df_name: str
    ) -> str:
        """Generate pandas code for JOIN."""
        join_type = join_info['type'].lower()
        table = join_info['table']
        condition = join_info['condition']
        
        if join_type == 'inner':
            merge_how = 'inner'
        elif join_type == 'left':
            merge_how = 'left'
        elif join_type == 'right':
            merge_how = 'right'
        elif join_type == 'outer':
            merge_how = 'outer'
        else:
            merge_how = 'inner'
        
        # Extract join keys from condition
        if condition:
            keys = self._extract_join_keys(condition)
            if keys:
                left_key, right_key = keys
                return (
                    f"{df_name} = {df_name}.merge("
                    f"load_dataframe('{table}'), "
                    f"left_on='{left_key}', right_on='{right_key}', "
                    f"how='{merge_how}')"
                )
        
        return f"# JOIN {join_type.upper()} {table} ON {condition}"
    
    def _extract_join_keys(self, condition: exp.Expression) -> Optional[tuple]:
        """Extract join keys from condition."""
        if isinstance(condition, exp.EQ):
            left = condition.this
            right = condition.expression
            
            left_key = None
            right_key = None
            
            if isinstance(left, exp.Column):
                left_key = left.name
            if isinstance(right, exp.Column):
                right_key = right.name
            
            if left_key and right_key:
                return (left_key, right_key)
        
        return None
    
    def _generate_groupby(
        self,
        group_by: List[str],
        select_exprs: List[exp.Expression],
        df_name: str
    ) -> str:
        """Generate pandas code for GROUP BY with aggregations."""
        aggregations = {}
        
        # Extract aggregations from SELECT
        for expr in select_exprs:
            if isinstance(expr, exp.Alias):
                alias = expr.alias
                col_expr = expr.this
            else:
                alias = None
                col_expr = expr
            
            if isinstance(col_expr, exp.AggFunc):
                func_name = col_expr.sql_name().lower()
                if isinstance(col_expr.this, exp.Column):
                    col_name = col_expr.this.name
                    output_name = alias or f"{col_name}_{func_name}"
                    
                    # Map SQL functions to pandas
                    pandas_func = self._map_aggregation_function(func_name)
                    aggregations[col_name] = (pandas_func, output_name)
        
        # Build aggregation dict
        agg_dict = {}
        for col, (func, alias) in aggregations.items():
            if func == 'sum':
                agg_dict[col] = 'sum'
            elif func == 'count':
                agg_dict[col] = 'count'
            elif func == 'avg' or func == 'mean':
                agg_dict[col] = 'mean'
            elif func == 'max':
                agg_dict[col] = 'max'
            elif func == 'min':
                agg_dict[col] = 'min'
            else:
                agg_dict[col] = func
        
        # Generate code
        group_cols = ", ".join([f"'{col}'" for col in group_by])
        agg_str = ", ".join([f"'{k}': '{v}'" for k, v in agg_dict.items()])
        
        code = f"{df_name} = {df_name}.groupby([{group_cols}]).agg({{{agg_str}}}).reset_index()"
        
        # Rename columns if aliases were used
        rename_dict = {}
        for col, (func, alias) in aggregations.items():
            if alias and alias != col:
                # Find the actual column name after aggregation
                if func in ['sum', 'count', 'mean', 'max', 'min']:
                    rename_dict[col] = alias
        
        if rename_dict:
            rename_str = ", ".join([f"'{k}': '{v}'" for k, v in rename_dict.items()])
            code += f"\n{df_name} = {df_name}.rename(columns={{{rename_str}}})"
        
        return code
    
    def _generate_orderby(
        self,
        order_by: List[Dict[str, Any]],
        df_name: str
    ) -> str:
        """Generate pandas code for ORDER BY."""
        if not order_by:
            return ""
        
        columns = []
        ascending = []
        
        for order_info in order_by:
            if order_info['column']:
                columns.append(f"'{order_info['column']}'")
                ascending.append(order_info['asc'])
        
        if columns:
            cols_str = ", ".join(columns)
            asc_str = ", ".join([str(asc) for asc in ascending])
            return f"{df_name} = {df_name}.sort_values(by=[{cols_str}], ascending=[{asc_str}])"
        
        return ""
    
    def _generate_limit(self, limit: int, df_name: str) -> str:
        """Generate pandas code for LIMIT."""
        return f"{df_name} = {df_name}.head({limit})"
    
    def _map_aggregation_function(self, sql_func: str) -> str:
        """Map SQL aggregation function to pandas equivalent."""
        mapping = {
            'sum': 'sum',
            'count': 'count',
            'avg': 'mean',
            'average': 'mean',
            'mean': 'mean',
            'max': 'max',
            'min': 'min',
            'std': 'std',
            'stddev': 'std',
            'variance': 'var',
            'var': 'var',
        }
        return mapping.get(sql_func.lower(), sql_func.lower())
    
    def _expression_to_pandas(self, expr: exp.Expression) -> str:
        """Convert SQL expression to pandas query string."""
        if isinstance(expr, exp.Column):
            return expr.name
        elif isinstance(expr, exp.Literal):
            return str(expr.this)
        elif isinstance(expr, exp.EQ):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} == {right}"
        elif isinstance(expr, exp.NEQ):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} != {right}"
        elif isinstance(expr, exp.GT):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} > {right}"
        elif isinstance(expr, exp.GTE):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} >= {right}"
        elif isinstance(expr, exp.LT):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} < {right}"
        elif isinstance(expr, exp.LTE):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"{left} <= {right}"
        elif isinstance(expr, exp.And):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"({left}) & ({right})"
        elif isinstance(expr, exp.Or):
            left = self._expression_to_pandas(expr.this)
            right = self._expression_to_pandas(expr.expression)
            return f"({left}) | ({right})"
        else:
            return str(expr)
    
    def _execute_pandas(
        self,
        ast: exp.Expression,
        source_table: str,
        df_name: str
    ) -> pd.DataFrame:
        """Execute pandas operations directly (requires source DataFrame)."""
        # This would require the actual DataFrame to be passed in
        # For now, we'll raise an error
        raise NotImplementedError(
            "Direct execution requires source DataFrame. "
            "Use return_code=True to get code string instead."
        )
    
    def convert_file(
        self,
        sql_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        source_table: Optional[str] = None
    ) -> str:
        """
        Convert SQL file to pandas code.
        
        Args:
            sql_file: Path to SQL file
            output_file: Optional path to save Python code
            source_table: Source table name
            
        Returns:
            Generated pandas code string
        """
        sql_path = Path(sql_file)
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        sql = sql_path.read_text()
        pandas_code = self.convert(sql, source_table=source_table)
        
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(pandas_code)
        
        return pandas_code

