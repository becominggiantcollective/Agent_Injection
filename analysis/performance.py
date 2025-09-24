"""
Performance analysis and insights.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .metrics import MetricsCollector, Metric


class PerformanceAnalyzer:
    """Analyzes performance metrics and provides insights."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize performance analyzer."""
        self.metrics_collector = metrics_collector
    
    def analyze_agent_performance(self, agent_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze performance of a specific agent."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Get agent-specific metrics
        agent_metrics = self.metrics_collector.get_metrics(
            start_time=start_time,
            end_time=end_time
        )
        agent_metrics = [m for m in agent_metrics if m.tags.get("agent_id") == agent_id]
        
        if not agent_metrics:
            return {"agent_id": agent_id, "status": "no_data"}
        
        # Analyze different metric types
        task_completion_metrics = [m for m in agent_metrics if "task_completion" in m.name]
        execution_time_metrics = [m for m in agent_metrics if "execution_time" in m.name]
        error_metrics = [m for m in agent_metrics if "error" in m.name]
        
        analysis = {
            "agent_id": agent_id,
            "time_window": f"{time_window_hours} hours",
            "total_metrics": len(agent_metrics),
            "task_completion": self._analyze_task_completion(task_completion_metrics),
            "execution_performance": self._analyze_execution_time(execution_time_metrics),
            "error_analysis": self._analyze_errors(error_metrics),
            "overall_score": 0.0
        }
        
        # Calculate overall performance score
        analysis["overall_score"] = self._calculate_performance_score(analysis)
        
        return analysis
    
    def analyze_strategy_performance(self, strategy_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze performance of a specific strategy."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        strategy_metrics = self.metrics_collector.get_metrics(
            start_time=start_time,
            end_time=end_time
        )
        strategy_metrics = [m for m in strategy_metrics if m.tags.get("strategy_id") == strategy_id]
        
        if not strategy_metrics:
            return {"strategy_id": strategy_id, "status": "no_data"}
        
        return {
            "strategy_id": strategy_id,
            "time_window": f"{time_window_hours} hours",
            "total_executions": len([m for m in strategy_metrics if "execution" in m.name]),
            "success_rate": self._calculate_success_rate(strategy_metrics),
            "average_execution_time": self._calculate_average_execution_time(strategy_metrics),
            "resource_efficiency": self._calculate_resource_efficiency(strategy_metrics)
        }
    
    def analyze_campaign_performance(self, campaign_name: str) -> Dict[str, Any]:
        """Analyze performance of a specific campaign."""
        campaign_metrics = [m for m in self.metrics_collector.metrics if m.tags.get("campaign") == campaign_name]
        
        if not campaign_metrics:
            return {"campaign": campaign_name, "status": "no_data"}
        
        return {
            "campaign": campaign_name,
            "total_tasks": len([m for m in campaign_metrics if "task" in m.name]),
            "completion_rate": self._calculate_completion_rate(campaign_metrics),
            "average_task_time": self._calculate_average_task_time(campaign_metrics),
            "agent_utilization": self._analyze_agent_utilization(campaign_metrics)
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        recent_metrics = self.metrics_collector.get_metrics(
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(set(m.tags.get("agent_id") for m in recent_metrics if m.tags.get("agent_id"))),
            "recent_activity": len(recent_metrics),
            "error_rate": self._calculate_error_rate(recent_metrics),
            "average_response_time": self._calculate_average_response_time(recent_metrics),
            "system_load": self._calculate_system_load(recent_metrics)
        }
    
    def _analyze_task_completion(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze task completion metrics."""
        if not metrics:
            return {"status": "no_data"}
        
        completed_tasks = len([m for m in metrics if m.value == 1.0])
        total_tasks = len(metrics)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0.0
        }
    
    def _analyze_execution_time(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze execution time metrics."""
        if not metrics:
            return {"status": "no_data"}
        
        times = [m.value for m in metrics]
        
        return {
            "count": len(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times)
        }
    
    def _analyze_errors(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze error metrics."""
        error_count = len(metrics)
        
        return {
            "error_count": error_count,
            "error_rate": error_count / max(1, len(self.metrics_collector.metrics))
        }
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)."""
        score = 0.0
        
        # Task completion score (40%)
        completion_data = analysis.get("task_completion", {})
        if completion_data.get("status") != "no_data":
            completion_rate = completion_data.get("completion_rate", 0.0)
            score += completion_rate * 40
        
        # Execution performance score (30%)
        exec_data = analysis.get("execution_performance", {})
        if exec_data.get("status") != "no_data":
            # Assume faster is better, normalize against some baseline
            avg_time = exec_data.get("average_time", 10.0)
            exec_score = max(0, min(30, 30 * (10.0 / max(avg_time, 1.0))))
            score += exec_score
        
        # Error rate score (30%)
        error_data = analysis.get("error_analysis", {})
        error_rate = error_data.get("error_rate", 0.0)
        error_score = max(0, 30 * (1.0 - error_rate))
        score += error_score
        
        return round(score, 2)
    
    def _calculate_success_rate(self, metrics: List[Metric]) -> float:
        """Calculate success rate from metrics."""
        success_metrics = [m for m in metrics if "success" in m.name and m.value == 1.0]
        total_metrics = [m for m in metrics if "execution" in m.name]
        
        return len(success_metrics) / max(1, len(total_metrics))
    
    def _calculate_average_execution_time(self, metrics: List[Metric]) -> float:
        """Calculate average execution time."""
        time_metrics = [m for m in metrics if "execution_time" in m.name]
        if not time_metrics:
            return 0.0
        
        return sum(m.value for m in time_metrics) / len(time_metrics)
    
    def _calculate_resource_efficiency(self, metrics: List[Metric]) -> float:
        """Calculate resource efficiency score."""
        # Simplified efficiency calculation
        return 0.85  # Placeholder
    
    def _calculate_completion_rate(self, metrics: List[Metric]) -> float:
        """Calculate completion rate."""
        completion_metrics = [m for m in metrics if "completion" in m.name]
        if not completion_metrics:
            return 0.0
        
        return sum(m.value for m in completion_metrics) / len(completion_metrics)
    
    def _calculate_average_task_time(self, metrics: List[Metric]) -> float:
        """Calculate average task execution time."""
        task_time_metrics = [m for m in metrics if "task_time" in m.name]
        if not task_time_metrics:
            return 0.0
        
        return sum(m.value for m in task_time_metrics) / len(task_time_metrics)
    
    def _analyze_agent_utilization(self, metrics: List[Metric]) -> Dict[str, int]:
        """Analyze agent utilization in campaign."""
        agent_usage = {}
        for metric in metrics:
            agent_id = metric.tags.get("agent_id")
            if agent_id:
                agent_usage[agent_id] = agent_usage.get(agent_id, 0) + 1
        
        return agent_usage
    
    def _calculate_error_rate(self, metrics: List[Metric]) -> float:
        """Calculate error rate."""
        error_metrics = [m for m in metrics if "error" in m.name]
        return len(error_metrics) / max(1, len(metrics))
    
    def _calculate_average_response_time(self, metrics: List[Metric]) -> float:
        """Calculate average response time."""
        response_time_metrics = [m for m in metrics if "response_time" in m.name]
        if not response_time_metrics:
            return 0.0
        
        return sum(m.value for m in response_time_metrics) / len(response_time_metrics)
    
    def _calculate_system_load(self, metrics: List[Metric]) -> float:
        """Calculate system load."""
        # Simplified system load calculation
        return min(1.0, len(metrics) / 100.0)