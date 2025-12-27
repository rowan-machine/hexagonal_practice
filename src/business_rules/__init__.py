"""
Centralized business rules for stop loss insurance operations.

This module contains all business logic that is shared between:
- Pipeline steps (bronze, silver, gold)
- SDK/analyst interfaces
- Domain processors

All business rules should be defined here to ensure consistency.
"""
from src.business_rules.aggregations import (
    ClaimsAggregator,
    PoliciesAggregator
)

__all__ = [
    "ClaimsAggregator",
    "PoliciesAggregator"
]

