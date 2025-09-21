"""
Metrics collection and tracking.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import statistics


@dataclass
class Metric:
    """Represents a single metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]


class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a metric value."""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        self.metrics.append(metric)
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        self.counters[key] = self.counters.get(key, 0) + value
        self.record_metric(f"{name}_counter", self.counters[key], tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        self.gauges[key] = value
        self.record_metric(f"{name}_gauge", value, tags)
    
    def get_metrics(self, name_filter: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Metric]:
        """Retrieve metrics with optional filtering."""
        filtered_metrics = self.metrics
        
        if name_filter:
            filtered_metrics = [m for m in filtered_metrics if name_filter in m.name]
        
        if start_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
        
        if end_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
        
        return filtered_metrics
    
    def get_metric_summary(self, name: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, float]:
        """Get statistical summary of a metric."""
        metrics = self.get_metrics(name, start_time, end_time)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0
        }
    
    def clear_metrics(self, before_time: Optional[datetime] = None) -> int:
        """Clear old metrics."""
        if before_time is None:
            count = len(self.metrics)
            self.metrics.clear()
            return count
        
        original_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp >= before_time]
        return original_count - len(self.metrics)