"""
Validation mixin for data quality checks.
"""
from typing import List, Callable, Any, Optional, Dict
from dataclasses import dataclass


@dataclass
class ValidationRule:
    """Represents a validation rule."""
    name: str
    check: Callable[[Any], bool]
    error_message: str
    severity: str = "error"  # "error" or "warning"


class ValidationMixin:
    """Mixin providing validation capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_rules: List[ValidationRule] = []
        self.validation_results: List[Dict[str, Any]] = []
    
    def add_rule(self, name: str, check: Callable[[Any], bool], error_message: str, severity: str = "error") -> None:
        """Add a validation rule."""
        rule = ValidationRule(
            name=name,
            check=check,
            error_message=error_message,
            severity=severity
        )
        self.validation_rules.append(rule)
    
    def validate(self, data: Any) -> bool:
        """
        Run all validation rules against data.
        
        Returns:
            True if all validations pass, False otherwise
        """
        all_passed = True
        
        for rule in self.validation_rules:
            try:
                passed = rule.check(data)
                result = {
                    "rule_name": rule.name,
                    "passed": passed,
                    "severity": rule.severity,
                    "error_message": rule.error_message if not passed else None
                }
                self.validation_results.append(result)
                
                if not passed and rule.severity == "error":
                    all_passed = False
                    
            except Exception as e:
                result = {
                    "rule_name": rule.name,
                    "passed": False,
                    "severity": "error",
                    "error_message": f"Validation rule raised exception: {str(e)}"
                }
                self.validation_results.append(result)
                all_passed = False
        
        return all_passed
    
    def get_validation_results(self) -> List[Dict[str, Any]]:
        """Get all validation results."""
        return self.validation_results.copy()
    
    def clear_validation_results(self) -> None:
        """Clear validation results."""
        self.validation_results.clear()

