"""
Metrics mixin for tracking pipeline performance.
"""
from typing import Dict, Any, Optional, List
from time import time
from dataclasses import dataclass, field


@dataclass
class Metric:
    """Represents a single metric measurement."""
    name: str
    value: float
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)


class MetricsMixin:
    """Mixin providing metrics collection capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics: List[Metric] = []
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def record_timing(self, name: str, duration_seconds: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing metric."""
        self.record_metric(name, duration_seconds, unit="seconds", tags=tags)
    
    def record_count(self, name: str, count: int, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a count metric."""
        self.record_metric(name, float(count), unit="count", tags=tags)
    
    def get_metrics(self) -> List[Metric]:
        """Get all recorded metrics."""
        return self.metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()

