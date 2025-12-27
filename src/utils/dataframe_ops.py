"""
DataFrame operations utility.

Isolates pandas operations to this layer only.
"""
from typing import Any, List, Dict, Optional
from src.mixins.logging import LoggingMixin


class DataFrameOps(LoggingMixin):
    """
    Utility class for DataFrame operations.
    
    This is the ONLY place where pandas should be used.
    All pandas operations are encapsulated here.
    """
    
    def __init__(self, **kwargs):
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__, **kwargs)
        self._pandas_available = self._check_pandas()
    
    def _check_pandas(self) -> bool:
        """Check if pandas is available."""
        try:
            import pandas as pd
            return True
        except ImportError:
            self.log_warning("Pandas not available. DataFrame operations will be limited.")
            return False
    
    def to_dataframe(self, data: List[Dict[str, Any]]) -> Any:
        """
        Convert list of dictionaries to pandas DataFrame.
        
        Args:
            data: List of dictionaries
            
        Returns:
            pandas DataFrame or original data if pandas unavailable
        """
        if not self._pandas_available:
            self.log_warning("Cannot convert to DataFrame - pandas not available")
            return data
        
        import pandas as pd
        self.log_info("Converting to DataFrame", records=len(data))
        return pd.DataFrame(data)
    
    def from_dataframe(self, df: Any) -> List[Dict[str, Any]]:
        """
        Convert pandas DataFrame to list of dictionaries.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List of dictionaries
        """
        if not self._pandas_available:
            self.log_warning("Cannot convert from DataFrame - pandas not available")
            return df
        
        self.log_info("Converting from DataFrame")
        return df.to_dict('records')
    
    def aggregate(self, data: List[Dict[str, Any]], 
                  group_by: List[str],
                  aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Aggregate data by specified columns.
        
        Args:
            data: List of dictionaries to aggregate
            group_by: Columns to group by
            aggregations: Dictionary mapping column names to aggregation functions
                         (e.g., {"amount": "sum", "count": "count"})
        
        Returns:
            Aggregated data as list of dictionaries
        """
        if not self._pandas_available:
            self.log_warning("Cannot aggregate - pandas not available, returning original data")
            return data
        
        import pandas as pd
        self.log_info("Aggregating data", group_by=group_by, aggregations=aggregations)
        
        df = self.to_dataframe(data)
        
        # Build aggregation dictionary for pandas
        agg_dict = {}
        for col, func in aggregations.items():
            if func == "sum":
                agg_dict[col] = "sum"
            elif func == "mean":
                agg_dict[col] = "mean"
            elif func == "count":
                agg_dict[col] = "count"
            elif func == "max":
                agg_dict[col] = "max"
            elif func == "min":
                agg_dict[col] = "min"
            else:
                self.log_warning(f"Unknown aggregation function: {func}")
        
        grouped = df.groupby(group_by).agg(agg_dict).reset_index()
        return self.from_dataframe(grouped)
    
    def filter(self, data: List[Dict[str, Any]], 
               condition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter data based on conditions.
        
        Args:
            data: List of dictionaries to filter
            condition: Dictionary of column: value pairs to filter by
        
        Returns:
            Filtered data
        """
        if not self._pandas_available:
            # Fallback to basic filtering
            filtered = []
            for record in data:
                matches = all(record.get(k) == v for k, v in condition.items())
                if matches:
                    filtered.append(record)
            return filtered
        
        import pandas as pd
        self.log_info("Filtering data", condition=condition)
        
        df = self.to_dataframe(data)
        
        for col, value in condition.items():
            df = df[df[col] == value]
        
        return self.from_dataframe(df)
    
    def join(self, left: List[Dict[str, Any]], 
             right: List[Dict[str, Any]],
             on: str,
             how: str = "inner") -> List[Dict[str, Any]]:
        """
        Join two datasets.
        
        Args:
            left: Left dataset
            right: Right dataset
            on: Column name to join on
            how: Join type ("inner", "left", "right", "outer")
        
        Returns:
            Joined data
        """
        if not self._pandas_available:
            self.log_warning("Cannot join - pandas not available")
            return left
        
        import pandas as pd
        self.log_info("Joining datasets", on=on, how=how)
        
        df_left = self.to_dataframe(left)
        df_right = self.to_dataframe(right)
        
        df_joined = df_left.merge(df_right, on=on, how=how)
        return self.from_dataframe(df_joined)

