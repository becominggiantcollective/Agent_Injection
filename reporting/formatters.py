"""
Report formatting utilities.
"""

import json
import csv
from typing import Dict, Any, List
from io import StringIO
from datetime import datetime


class BaseFormatter:
    """Base class for report formatters."""
    
    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report data."""
        raise NotImplementedError


class JSONFormatter(BaseFormatter):
    """JSON report formatter."""
    
    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as JSON."""
        return json.dumps(report_data, indent=2, default=str)


class HTMLFormatter(BaseFormatter):
    """HTML report formatter."""
    
    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Injection Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background-color: #f9f9f9; padding: 8px; margin: 5px 0; border-left: 3px solid #007cba; }}
        .recommendation {{ background-color: #fff3cd; padding: 8px; margin: 5px 0; border-left: 3px solid #ffc107; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .score-good {{ color: green; font-weight: bold; }}
        .score-warning {{ color: orange; font-weight: bold; }}
        .score-poor {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Agent Injection Report</h1>
        <p><strong>Report Type:</strong> {report_data.get('report_type', 'Unknown')}</p>
        <p><strong>Generated:</strong> {report_data.get('generated_at', datetime.now().isoformat())}</p>
    </div>
"""
        
        # Add report-specific content
        if report_data.get('report_type') == 'agent_performance':
            html += self._format_agent_report(report_data)
        elif report_data.get('report_type') == 'campaign_performance':
            html += self._format_campaign_report(report_data)
        elif report_data.get('report_type') == 'system_health':
            html += self._format_system_report(report_data)
        elif report_data.get('report_type') == 'comparative_analysis':
            html += self._format_comparative_report(report_data)
        else:
            html += self._format_generic_report(report_data)
        
        html += """
</body>
</html>
"""
        return html
    
    def _format_agent_report(self, report_data: Dict[str, Any]) -> str:
        """Format agent performance report."""
        agent_id = report_data.get('agent_id', 'Unknown')
        performance = report_data.get('performance_analysis', {})
        
        html = f"""
    <div class="section">
        <h2>Agent Performance: {agent_id}</h2>
        <div class="metric">
            <strong>Overall Score:</strong> {self._format_score(performance.get('overall_score', 0))}
        </div>
    </div>
"""
        
        # Add recommendations
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            html += '<div class="section"><h3>Recommendations</h3>'
            for rec in recommendations:
                html += f'<div class="recommendation">{rec}</div>'
            html += '</div>'
        
        return html
    
    def _format_campaign_report(self, report_data: Dict[str, Any]) -> str:
        """Format campaign performance report."""
        campaign_name = report_data.get('campaign_name', 'Unknown')
        analysis = report_data.get('analysis', {})
        summary = report_data.get('summary', {})
        
        html = f"""
    <div class="section">
        <h2>Campaign: {campaign_name}</h2>
        <div class="metric">
            <strong>Total Tasks:</strong> {summary.get('total_tasks', 0)}
        </div>
        <div class="metric">
            <strong>Completion Rate:</strong> {summary.get('completion_rate', '0%')}
        </div>
        <div class="metric">
            <strong>Average Task Time:</strong> {summary.get('average_task_time', '0s')}
        </div>
    </div>
"""
        return html
    
    def _format_system_report(self, report_data: Dict[str, Any]) -> str:
        """Format system health report."""
        health = report_data.get('system_health', {})
        
        html = """
    <div class="section">
        <h2>System Health</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
"""
        
        for key, value in health.items():
            html += f"<tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>"
        
        html += """
        </table>
    </div>
"""
        return html
    
    def _format_comparative_report(self, report_data: Dict[str, Any]) -> str:
        """Format comparative analysis report."""
        rankings = report_data.get('rankings', [])
        
        html = """
    <div class="section">
        <h2>Agent Rankings</h2>
        <table>
            <tr><th>Rank</th><th>Agent ID</th><th>Score</th></tr>
"""
        
        for ranking in rankings:
            score_class = self._get_score_class(ranking.get('score', 0))
            html += f"""
            <tr>
                <td>{ranking.get('rank', 0)}</td>
                <td>{ranking.get('agent_id', 'Unknown')}</td>
                <td class="{score_class}">{ranking.get('score', 0):.1f}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
"""
        return html
    
    def _format_generic_report(self, report_data: Dict[str, Any]) -> str:
        """Format generic report data."""
        html = '<div class="section"><h2>Report Data</h2><pre>'
        html += json.dumps(report_data, indent=2, default=str)
        html += '</pre></div>'
        return html
    
    def _format_score(self, score: float) -> str:
        """Format score with appropriate styling."""
        score_class = self._get_score_class(score)
        return f'<span class="{score_class}">{score:.1f}</span>'
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score."""
        if score >= 80:
            return "score-good"
        elif score >= 60:
            return "score-warning"
        else:
            return "score-poor"


class CSVFormatter(BaseFormatter):
    """CSV report formatter."""
    
    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as CSV."""
        output = StringIO()
        
        # Handle different report types
        if report_data.get('report_type') == 'comparative_analysis':
            self._format_comparative_csv(report_data, output)
        elif report_data.get('report_type') == 'agent_performance':
            self._format_agent_csv(report_data, output)
        else:
            self._format_generic_csv(report_data, output)
        
        return output.getvalue()
    
    def _format_comparative_csv(self, report_data: Dict[str, Any], output: StringIO) -> None:
        """Format comparative report as CSV."""
        rankings = report_data.get('rankings', [])
        
        if rankings:
            writer = csv.DictWriter(output, fieldnames=['rank', 'agent_id', 'score'])
            writer.writeheader()
            writer.writerows(rankings)
    
    def _format_agent_csv(self, report_data: Dict[str, Any], output: StringIO) -> None:
        """Format agent report as CSV."""
        writer = csv.writer(output)
        writer.writerow(['Metric', 'Value'])
        
        agent_id = report_data.get('agent_id', 'Unknown')
        performance = report_data.get('performance_analysis', {})
        
        writer.writerow(['Agent ID', agent_id])
        writer.writerow(['Overall Score', performance.get('overall_score', 0)])
        writer.writerow(['Report Type', report_data.get('report_type', 'Unknown')])
        writer.writerow(['Generated At', report_data.get('generated_at', '')])
    
    def _format_generic_csv(self, report_data: Dict[str, Any], output: StringIO) -> None:
        """Format generic report as CSV."""
        writer = csv.writer(output)
        writer.writerow(['Key', 'Value'])
        
        def flatten_dict(d: Dict[str, Any], prefix: str = '') -> None:
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    flatten_dict(value, full_key)
                elif isinstance(value, list):
                    writer.writerow([full_key, f"List with {len(value)} items"])
                else:
                    writer.writerow([full_key, str(value)])
        
        flatten_dict(report_data)