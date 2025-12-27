"""
Validation configuration loader.

Loads validation rules from YAML configuration files.
Simulates SQL estate validation by comparing processed data counts
against expected counts from source files.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import json
from src.mixins.logging import LoggingMixin


class ValidationLoader(LoggingMixin):
    """
    Loads and manages validation configurations.
    
    This simulates SQL estate validation by:
    1. Reading expected counts from source JSON files
    2. Comparing against processed data counts
    3. Validating against configuration rules
    """
    
    def __init__(self, config_path: str = "config/validation.yml"):
        """
        Initialize validation loader.
        
        Args:
            config_path: Path to validation configuration YAML file
        """
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load validation configuration from YAML file."""
        if not self.config_path.exists():
            self.log_warning(f"Validation config not found: {self.config_path}")
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.log_info(f"Loaded validation config from {self.config_path}")
        return config or {}
    
    def get_expected_count_from_json(self, json_path: str, data_key: str) -> int:
        """
        Get expected record count from source JSON file.
        
        This simulates reading expected counts from SQL estate.
        In production, this would query the original SQL database.
        
        Args:
            json_path: Path to source JSON file
            data_key: Key in JSON containing the data array (e.g., "claims", "policies")
            
        Returns:
            Expected count of records
        """
        json_file = Path(json_path)
        if not json_file.exists():
            self.log_warning(f"Source JSON file not found: {json_path}")
            return 0
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = data.get(data_key, [])
            count = len(records) if isinstance(records, list) else 0
            
            self.log_info(f"Read expected count from {json_path}", 
                         data_key=data_key, 
                         count=count)
            return count
        except Exception as e:
            self.log_error(f"Failed to read JSON file {json_path}", error=e)
            return 0
    
    def get_validation_rules(self, entity_type: str) -> Dict[str, Any]:
        """
        Get validation rules for a specific entity type.
        
        Args:
            entity_type: Type of entity ("claims" or "policies")
            
        Returns:
            Dictionary with validation rules
        """
        return self.config.get(entity_type, {})
    
    def validate_count(
        self, 
        entity_type: str, 
        actual_count: int, 
        source_json_path: Optional[str] = None,
        source_data_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate record count against expected count.
        
        This simulates SQL estate validation by comparing:
        - Actual count from processed data
        - Expected count from source JSON (simulating SQL query result)
        - Configuration expected count (fallback)
        
        Args:
            entity_type: Type of entity ("claims" or "policies")
            actual_count: Actual number of records processed
            source_json_path: Optional path to source JSON file
            source_data_key: Optional key in JSON containing data
            
        Returns:
            Validation result dictionary with:
            - passed: bool
            - actual_count: int
            - expected_count: int
            - source: str (where expected count came from)
            - message: str
        """
        # Try to get expected count from source JSON first (simulates SQL estate)
        expected_count = None
        source = "config"
        
        if source_json_path and source_data_key:
            expected_count = self.get_expected_count_from_json(source_json_path, source_data_key)
            source = "source_json"
        
        # Fallback to config if JSON not available
        if expected_count is None or expected_count == 0:
            rules = self.get_validation_rules(entity_type)
            expected_count = rules.get("expected_count", 0)
            source = "config"
        
        passed = actual_count == expected_count
        
        result = {
            "passed": passed,
            "actual_count": actual_count,
            "expected_count": expected_count,
            "source": source,
            "message": (
                f"Count validation {'passed' if passed else 'failed'}: "
                f"expected {expected_count}, got {actual_count}"
            )
        }
        
        if not passed:
            self.log_warning(
                f"Count validation failed for {entity_type}",
                actual=actual_count,
                expected=expected_count,
                source=source
            )
        else:
            self.log_info(
                f"Count validation passed for {entity_type}",
                count=actual_count
            )
        
        return result
    
    def validate_claims_count(
        self, 
        actual_count: int, 
        source_json_path: str = "data/raw_claims.json"
    ) -> Dict[str, Any]:
        """
        Validate claims count.
        
        Args:
            actual_count: Actual number of claims processed
            source_json_path: Path to source claims JSON file
            
        Returns:
            Validation result dictionary
        """
        return self.validate_count(
            entity_type="claims",
            actual_count=actual_count,
            source_json_path=source_json_path,
            source_data_key="claims"
        )
    
    def validate_policies_count(
        self, 
        actual_count: int, 
        source_json_path: str = "data/raw_policies.json"
    ) -> Dict[str, Any]:
        """
        Validate policies count.
        
        Args:
            actual_count: Actual number of policies processed
            source_json_path: Path to source policies JSON file
            
        Returns:
            Validation result dictionary
        """
        return self.validate_count(
            entity_type="policies",
            actual_count=actual_count,
            source_json_path=source_json_path,
            source_data_key="policies"
        )

