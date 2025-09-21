"""
Report generation functionality.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from analysis.performance import PerformanceAnalyzer
from analysis.metrics import MetricsCollector


class ReportGenerator:
    """Generates various types of reports."""
    
    def __init__(self, metrics_collector: MetricsCollector, performance_analyzer: PerformanceAnalyzer):
        """Initialize report generator."""
        self.metrics_collector = metrics_collector
        self.performance_analyzer = performance_analyzer
    
    def generate_agent_report(self, agent_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive agent performance report."""
        performance_data = self.performance_analyzer.analyze_agent_performance(agent_id, time_window_hours)
        
        # Get recent metrics for the agent
        end_time = datetime.now()
        start_time = datetime.now().replace(hour=end_time.hour - time_window_hours)
        
        agent_metrics = [
            m for m in self.metrics_collector.get_metrics(start_time=start_time, end_time=end_time)
            if m.tags.get("agent_id") == agent_id
        ]
        
        report = {
            "report_type": "agent_performance",
            "generated_at": datetime.now().isoformat(),
            "agent_id": agent_id,
            "time_window": f"{time_window_hours} hours",
            "performance_analysis": performance_data,
            "metrics_summary": {
                "total_metrics": len(agent_metrics),
                "metric_types": list(set(m.name for m in agent_metrics)),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            },
            "recommendations": self._generate_agent_recommendations(performance_data)
        }
        
        return report
    
    def generate_campaign_report(self, campaign_name: str) -> Dict[str, Any]:
        """Generate campaign performance report."""
        campaign_analysis = self.performance_analyzer.analyze_campaign_performance(campaign_name)
        
        report = {
            "report_type": "campaign_performance",
            "generated_at": datetime.now().isoformat(),
            "campaign_name": campaign_name,
            "analysis": campaign_analysis,
            "summary": self._generate_campaign_summary(campaign_analysis),
            "recommendations": self._generate_campaign_recommendations(campaign_analysis)
        }
        
        return report
    
    def generate_system_report(self) -> Dict[str, Any]:
        """Generate overall system health and performance report."""
        system_health = self.performance_analyzer.get_system_health()
        
        # Get all unique agents and strategies from recent metrics
        recent_metrics = self.metrics_collector.get_metrics(
            start_time=datetime.now().replace(hour=datetime.now().hour - 1)
        )
        
        agents = list(set(m.tags.get("agent_id") for m in recent_metrics if m.tags.get("agent_id")))
        strategies = list(set(m.tags.get("strategy_id") for m in recent_metrics if m.tags.get("strategy_id")))
        
        report = {
            "report_type": "system_health",
            "generated_at": datetime.now().isoformat(),
            "system_health": system_health,
            "active_components": {
                "agents": len(agents),
                "strategies": len(strategies),
                "total_metrics": len(self.metrics_collector.metrics)
            },
            "performance_overview": {
                "top_performing_agents": self._get_top_performing_agents(agents),
                "system_bottlenecks": self._identify_system_bottlenecks(),
                "resource_utilization": self._calculate_resource_utilization()
            },
            "recommendations": self._generate_system_recommendations(system_health)
        }
        
        return report
    
    def generate_comparative_report(self, agent_ids: List[str], time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comparative analysis report for multiple agents."""
        agent_analyses = {}
        for agent_id in agent_ids:
            agent_analyses[agent_id] = self.performance_analyzer.analyze_agent_performance(agent_id, time_window_hours)
        
        report = {
            "report_type": "comparative_analysis",
            "generated_at": datetime.now().isoformat(),
            "agents": agent_ids,
            "time_window": f"{time_window_hours} hours",
            "individual_analyses": agent_analyses,
            "comparison": self._generate_comparison_analysis(agent_analyses),
            "rankings": self._rank_agents(agent_analyses),
            "recommendations": self._generate_comparative_recommendations(agent_analyses)
        }
        
        return report
    
    def _generate_agent_recommendations(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on agent performance."""
        recommendations = []
        
        if performance_data.get("status") == "no_data":
            recommendations.append("No recent activity detected. Consider checking agent configuration.")
            return recommendations
        
        overall_score = performance_data.get("overall_score", 0)
        
        if overall_score < 50:
            recommendations.append("Performance is below average. Review task complexity and agent capabilities.")
        
        completion_data = performance_data.get("task_completion", {})
        if completion_data.get("completion_rate", 1.0) < 0.8:
            recommendations.append("Low task completion rate. Check for recurring errors or resource constraints.")
        
        exec_data = performance_data.get("execution_performance", {})
        if exec_data.get("average_time", 0) > 30:
            recommendations.append("High execution times detected. Consider optimizing agent algorithms or increasing resources.")
        
        error_data = performance_data.get("error_analysis", {})
        if error_data.get("error_rate", 0) > 0.1:
            recommendations.append("Elevated error rate. Review error logs and improve error handling.")
        
        if not recommendations:
            recommendations.append("Agent is performing well. Continue current configuration.")
        
        return recommendations
    
    def _generate_campaign_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign summary."""
        if analysis.get("status") == "no_data":
            return {"status": "No data available for this campaign"}
        
        return {
            "total_tasks": analysis.get("total_tasks", 0),
            "completion_rate": f"{analysis.get('completion_rate', 0) * 100:.1f}%",
            "average_task_time": f"{analysis.get('average_task_time', 0):.2f}s",
            "agents_utilized": len(analysis.get("agent_utilization", {}))
        }
    
    def _generate_campaign_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate campaign recommendations."""
        recommendations = []
        
        if analysis.get("status") == "no_data":
            return ["Campaign has no recorded metrics. Ensure proper instrumentation."]
        
        completion_rate = analysis.get("completion_rate", 0)
        if completion_rate < 0.9:
            recommendations.append("Consider reviewing task definitions and agent capabilities.")
        
        avg_time = analysis.get("average_task_time", 0)
        if avg_time > 60:
            recommendations.append("Tasks are taking longer than expected. Consider parallel execution strategies.")
        
        agent_util = analysis.get("agent_utilization", {})
        if len(agent_util) > 0:
            max_usage = max(agent_util.values())
            min_usage = min(agent_util.values())
            if max_usage > min_usage * 3:
                recommendations.append("Uneven agent utilization detected. Consider load balancing.")
        
        return recommendations or ["Campaign performance is satisfactory."]
    
    def _get_top_performing_agents(self, agents: List[str]) -> List[Dict[str, Any]]:
        """Get top performing agents."""
        agent_scores = []
        
        for agent_id in agents:
            analysis = self.performance_analyzer.analyze_agent_performance(agent_id, 1)
            if analysis.get("status") != "no_data":
                score = analysis.get("overall_score", 0)
                agent_scores.append({"agent_id": agent_id, "score": score})
        
        agent_scores.sort(key=lambda x: x["score"], reverse=True)
        return agent_scores[:5]
    
    def _identify_system_bottlenecks(self) -> List[str]:
        """Identify potential system bottlenecks."""
        bottlenecks = []
        
        # Check recent error rates
        recent_metrics = self.metrics_collector.get_metrics(
            start_time=datetime.now().replace(hour=datetime.now().hour - 1)
        )
        
        error_metrics = [m for m in recent_metrics if "error" in m.name]
        if len(error_metrics) > len(recent_metrics) * 0.1:
            bottlenecks.append("High error rate detected")
        
        # Check for slow responses
        response_metrics = [m for m in recent_metrics if "response_time" in m.name]
        if response_metrics:
            avg_response = sum(m.value for m in response_metrics) / len(response_metrics)
            if avg_response > 10:
                bottlenecks.append("Slow response times detected")
        
        return bottlenecks or ["No significant bottlenecks detected"]
    
    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization metrics."""
        return {
            "cpu_usage": 0.65,  # Placeholder
            "memory_usage": 0.45,  # Placeholder
            "agent_utilization": 0.80  # Placeholder
        }
    
    def _generate_system_recommendations(self, health_data: Dict[str, Any]) -> List[str]:
        """Generate system-level recommendations."""
        recommendations = []
        
        error_rate = health_data.get("error_rate", 0)
        if error_rate > 0.05:
            recommendations.append("System error rate is elevated. Review logs and improve error handling.")
        
        response_time = health_data.get("average_response_time", 0)
        if response_time > 5:
            recommendations.append("Average response time is high. Consider scaling resources.")
        
        system_load = health_data.get("system_load", 0)
        if system_load > 0.8:
            recommendations.append("System load is high. Consider distributing workload or adding capacity.")
        
        return recommendations or ["System is operating within normal parameters."]
    
    def _generate_comparison_analysis(self, analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparative analysis between agents."""
        valid_analyses = {k: v for k, v in analyses.items() if v.get("status") != "no_data"}
        
        if not valid_analyses:
            return {"status": "No data available for comparison"}
        
        scores = [analysis.get("overall_score", 0) for analysis in valid_analyses.values()]
        
        return {
            "total_agents": len(analyses),
            "agents_with_data": len(valid_analyses),
            "score_statistics": {
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "average": sum(scores) / len(scores) if scores else 0
            }
        }
    
    def _rank_agents(self, analyses: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank agents by performance."""
        rankings = []
        
        for agent_id, analysis in analyses.items():
            if analysis.get("status") != "no_data":
                score = analysis.get("overall_score", 0)
                rankings.append({
                    "agent_id": agent_id,
                    "score": score,
                    "rank": 0  # Will be set after sorting
                })
        
        rankings.sort(key=lambda x: x["score"], reverse=True)
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1
        
        return rankings
    
    def _generate_comparative_recommendations(self, analyses: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on comparative analysis."""
        recommendations = []
        
        valid_analyses = {k: v for k, v in analyses.items() if v.get("status") != "no_data"}
        
        if len(valid_analyses) < 2:
            return ["Need at least 2 agents with data for meaningful comparison."]
        
        scores = [analysis.get("overall_score", 0) for analysis in valid_analyses.values()]
        score_range = max(scores) - min(scores)
        
        if score_range > 30:
            recommendations.append("Significant performance variance detected. Review underperforming agents.")
        
        avg_score = sum(scores) / len(scores)
        if avg_score < 60:
            recommendations.append("Overall performance is below target. Consider system-wide optimizations.")
        
        return recommendations or ["Agents are performing consistently well."]