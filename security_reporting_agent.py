"""
Security Reporting & Summary AI Agent

This module implements an AI agent that aggregates and summarizes findings from 
analyzer agents, producing clear reports with technical details, risk scoring, 
executive summary, and prioritized remediation actions.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field


class SeverityLevel(Enum):
    """Security finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(Enum):
    """Security finding categories"""
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    COMPLIANCE = "compliance"
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    NETWORK_SECURITY = "network_security"


@dataclass
class SecurityFinding:
    """Represents a security finding from an analyzer agent"""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    category: FindingCategory
    affected_assets: List[str]
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    remediation: Optional[str] = None
    discovered_at: Optional[datetime] = None
    source_analyzer: Optional[str] = None
    technical_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass
class RemediationAction:
    """Represents a prioritized remediation action"""
    id: str
    title: str
    description: str
    priority: int  # 1 = highest priority
    estimated_effort: str  # e.g., "2 hours", "1 day", "1 week"
    related_findings: List[str]  # Finding IDs
    steps: List[str]
    impact: str


class SecurityReport(BaseModel):
    """Complete security report model"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = Field(default_factory=datetime.now)
    summary: Dict[str, Any] = Field(default_factory=dict)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    remediation_actions: List[Dict[str, Any]] = Field(default_factory=list)
    risk_score: float = Field(default=0.0)
    executive_summary: str = Field(default="")


class SecurityReportingAgent:
    """
    AI Agent for Security Reporting & Summary
    
    Aggregates and summarizes security findings from analyzer agents,
    producing comprehensive reports with risk scoring and remediation guidance.
    """
    
    def __init__(self, agent_name: str = "SecurityReportingAgent"):
        self.agent_name = agent_name
        self.findings: List[SecurityFinding] = []
    
    def add_finding(self, finding: SecurityFinding) -> None:
        """Add a security finding to the agent's knowledge base"""
        self.findings.append(finding)
    
    def add_findings(self, findings: List[SecurityFinding]) -> None:
        """Add multiple security findings"""
        self.findings.extend(findings)
    
    def calculate_risk_score(self) -> float:
        """
        Calculate overall risk score based on findings
        
        Returns a score from 0-100 where 100 is highest risk
        """
        if not self.findings:
            return 0.0
        
        severity_weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 7.5,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 1.0
        }
        
        total_score = 0.0
        for finding in self.findings:
            base_score = severity_weights.get(finding.severity, 1.0)
            
            # Factor in CVSS score if available
            if finding.cvss_score:
                cvss_multiplier = finding.cvss_score / 10.0
                base_score *= cvss_multiplier
            
            total_score += base_score
        
        # Normalize to 0-100 scale
        max_possible_score = len(self.findings) * 10.0
        normalized_score = min(100.0, (total_score / max_possible_score) * 100) if max_possible_score > 0 else 0.0
        
        return round(normalized_score, 2)
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary of security findings"""
        if not self.findings:
            return "No security findings to report."
        
        total_findings = len(self.findings)
        severity_counts = {}
        category_counts = {}
        
        for finding in self.findings:
            severity_counts[finding.severity.value] = severity_counts.get(finding.severity.value, 0) + 1
            category_counts[finding.category.value] = category_counts.get(finding.category.value, 0) + 1
        
        risk_score = self.calculate_risk_score()
        
        # Risk level assessment
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        summary = f"""
EXECUTIVE SUMMARY - Security Assessment Report

Risk Level: {risk_level} (Score: {risk_score}/100)

Total Findings: {total_findings}

Severity Breakdown:
"""
        
        for severity, count in sorted(severity_counts.items(), 
                                    key=lambda x: ['critical', 'high', 'medium', 'low', 'info'].index(x[0])):
            summary += f"  • {severity.upper()}: {count}\n"
        
        summary += "\nTop Categories:\n"
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for category, count in sorted_categories:
            summary += f"  • {category.replace('_', ' ').title()}: {count}\n"
        
        # Recommendations
        critical_findings = severity_counts.get('critical', 0)
        high_findings = severity_counts.get('high', 0)
        
        if critical_findings > 0:
            summary += f"\nIMMEDIATE ACTION REQUIRED: {critical_findings} critical findings need urgent attention."
        elif high_findings > 0:
            summary += f"\nPRIORITY ACTION: {high_findings} high-severity findings should be addressed promptly."
        else:
            summary += "\nNo critical issues identified. Continue monitoring and address medium/low priority items."
        
        return summary.strip()
    
    def generate_remediation_actions(self) -> List[RemediationAction]:
        """Generate prioritized remediation actions based on findings"""
        actions = []
        
        # Group findings by severity and category for better remediation planning
        critical_findings = [f for f in self.findings if f.severity == SeverityLevel.CRITICAL]
        high_findings = [f for f in self.findings if f.severity == SeverityLevel.HIGH]
        
        action_id = 1
        
        # Critical findings get immediate action items
        for finding in critical_findings:
            action = RemediationAction(
                id=f"REM-{action_id:03d}",
                title=f"Address Critical Issue: {finding.title}",
                description=f"Immediately resolve critical security finding: {finding.description}",
                priority=action_id,
                estimated_effort="Immediate",
                related_findings=[finding.id],
                steps=[
                    "Assess immediate impact and risk",
                    "Implement temporary mitigation if needed",
                    "Develop and test permanent fix",
                    "Deploy fix and verify resolution",
                    "Document changes and update procedures"
                ],
                impact="Eliminates critical security risk"
            )
            actions.append(action)
            action_id += 1
        
        # High findings get priority actions
        for finding in high_findings:
            action = RemediationAction(
                id=f"REM-{action_id:03d}",
                title=f"Resolve High Priority: {finding.title}",
                description=f"Address high-priority security finding: {finding.description}",
                priority=action_id,
                estimated_effort="1-3 days",
                related_findings=[finding.id],
                steps=[
                    "Review finding details and impact",
                    "Plan remediation approach",
                    "Implement fix with testing",
                    "Validate resolution",
                    "Update security documentation"
                ],
                impact="Reduces significant security risk"
            )
            actions.append(action)
            action_id += 1
        
        # Add general security improvement actions
        if len(self.findings) > 5:
            action = RemediationAction(
                id=f"REM-{action_id:03d}",
                title="Implement Security Monitoring Enhancement",
                description="Enhance security monitoring and detection capabilities",
                priority=action_id,
                estimated_effort="1 week",
                related_findings=[f.id for f in self.findings[:5]],
                steps=[
                    "Review current monitoring capabilities",
                    "Identify gaps in detection coverage",
                    "Implement additional monitoring rules",
                    "Set up alerting for similar issues",
                    "Train team on new monitoring tools"
                ],
                impact="Improves overall security posture and early detection"
            )
            actions.append(action)
        
        return actions
    
    def generate_human_readable_report(self) -> str:
        """Generate human-readable security report"""
        risk_score = self.calculate_risk_score()
        executive_summary = self.generate_executive_summary()
        remediation_actions = self.generate_remediation_actions()
        
        report = f"""
===============================================================================
                    SECURITY ASSESSMENT REPORT
===============================================================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Agent: {self.agent_name}

{executive_summary}

===============================================================================
                           DETAILED FINDINGS
===============================================================================

"""
        
        # Group findings by severity
        for severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM, SeverityLevel.LOW, SeverityLevel.INFO]:
            severity_findings = [f for f in self.findings if f.severity == severity]
            if not severity_findings:
                continue
                
            report += f"\n{severity.value.upper()} SEVERITY FINDINGS ({len(severity_findings)})\n"
            report += "=" * 50 + "\n"
            
            for finding in severity_findings:
                report += f"\nFinding ID: {finding.id}\n"
                report += f"Title: {finding.title}\n"
                report += f"Category: {finding.category.value.replace('_', ' ').title()}\n"
                report += f"Description: {finding.description}\n"
                
                if finding.affected_assets:
                    report += f"Affected Assets: {', '.join(finding.affected_assets)}\n"
                
                if finding.cvss_score:
                    report += f"CVSS Score: {finding.cvss_score}\n"
                
                if finding.cve_id:
                    report += f"CVE ID: {finding.cve_id}\n"
                
                if finding.source_analyzer:
                    report += f"Source: {finding.source_analyzer}\n"
                
                if finding.remediation:
                    report += f"Remediation: {finding.remediation}\n"
                
                report += f"Discovered: {finding.discovered_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                report += "-" * 40 + "\n"
        
        # Add remediation actions
        if remediation_actions:
            report += f"\n\n===============================================================================\n"
            report += "                       REMEDIATION ACTIONS\n"
            report += "===============================================================================\n"
            
            for action in remediation_actions:
                report += f"\nAction ID: {action.id}\n"
                report += f"Priority: {action.priority}\n"
                report += f"Title: {action.title}\n"
                report += f"Description: {action.description}\n"
                report += f"Estimated Effort: {action.estimated_effort}\n"
                report += f"Impact: {action.impact}\n"
                report += f"Related Findings: {', '.join(action.related_findings)}\n"
                report += "Steps:\n"
                for i, step in enumerate(action.steps, 1):
                    report += f"  {i}. {step}\n"
                report += "-" * 40 + "\n"
        
        return report
    
    def generate_machine_readable_report(self) -> Dict[str, Any]:
        """Generate machine-readable security report (JSON format)"""
        risk_score = self.calculate_risk_score()
        executive_summary = self.generate_executive_summary()
        remediation_actions = self.generate_remediation_actions()
        
        # Convert findings to dictionaries
        findings_data = []
        for finding in self.findings:
            finding_dict = asdict(finding)
            # Convert datetime to ISO format
            if finding_dict['discovered_at']:
                finding_dict['discovered_at'] = finding.discovered_at.isoformat()
            # Convert enums to strings
            finding_dict['severity'] = finding.severity.value
            finding_dict['category'] = finding.category.value
            findings_data.append(finding_dict)
        
        # Convert remediation actions to dictionaries
        actions_data = [asdict(action) for action in remediation_actions]
        
        # Create summary statistics
        severity_counts = {}
        category_counts = {}
        for finding in self.findings:
            severity_counts[finding.severity.value] = severity_counts.get(finding.severity.value, 0) + 1
            category_counts[finding.category.value] = category_counts.get(finding.category.value, 0) + 1
        
        report = SecurityReport(
            summary={
                "total_findings": len(self.findings),
                "severity_distribution": severity_counts,
                "category_distribution": category_counts,
                "agent_name": self.agent_name
            },
            findings=findings_data,
            remediation_actions=actions_data,
            risk_score=risk_score,
            executive_summary=executive_summary
        )
        
        return report.model_dump()
    
    def export_report(self, format_type: str = "both", output_dir: str = ".") -> Dict[str, str]:
        """
        Export security report in specified format(s)
        
        Args:
            format_type: "human", "machine", or "both"
            output_dir: Directory to save reports
            
        Returns:
            Dictionary with file paths of generated reports
        """
        import os
        from pathlib import Path
        
        output_paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type in ["human", "both"]:
            human_report = self.generate_human_readable_report()
            human_path = Path(output_dir) / f"security_report_{timestamp}.txt"
            with open(human_path, 'w') as f:
                f.write(human_report)
            output_paths["human_readable"] = str(human_path)
        
        if format_type in ["machine", "both"]:
            machine_report = self.generate_machine_readable_report()
            machine_path = Path(output_dir) / f"security_report_{timestamp}.json"
            with open(machine_path, 'w') as f:
                json.dump(machine_report, f, indent=2, default=str)
            output_paths["machine_readable"] = str(machine_path)
        
        return output_paths


# Example usage and demonstration
def create_sample_findings() -> List[SecurityFinding]:
    """Create sample security findings for demonstration"""
    findings = [
        SecurityFinding(
            id="VULN-001",
            title="SQL Injection Vulnerability",
            description="User input is not properly sanitized in login form",
            severity=SeverityLevel.CRITICAL,
            category=FindingCategory.VULNERABILITY,
            affected_assets=["web-app", "database"],
            cvss_score=9.8,
            cve_id="CVE-2023-12345",
            remediation="Implement parameterized queries and input validation",
            source_analyzer="SQL_Scanner_Agent"
        ),
        SecurityFinding(
            id="MISC-001",
            title="Weak SSL/TLS Configuration",
            description="Server supports deprecated TLS 1.0 protocol",
            severity=SeverityLevel.HIGH,
            category=FindingCategory.MISCONFIGURATION,
            affected_assets=["web-server"],
            cvss_score=7.4,
            remediation="Disable TLS 1.0 and 1.1, enforce TLS 1.2+",
            source_analyzer="TLS_Scanner_Agent"
        ),
        SecurityFinding(
            id="ACCESS-001",
            title="Default Admin Credentials",
            description="System still uses default administrative credentials",
            severity=SeverityLevel.CRITICAL,
            category=FindingCategory.ACCESS_CONTROL,
            affected_assets=["admin-panel"],
            cvss_score=9.8,
            remediation="Change default credentials immediately",
            source_analyzer="Credential_Scanner_Agent"
        ),
        SecurityFinding(
            id="COMP-001",
            title="Missing Security Headers",
            description="Web application missing security headers (HSTS, CSP)",
            severity=SeverityLevel.MEDIUM,
            category=FindingCategory.COMPLIANCE,
            affected_assets=["web-app"],
            remediation="Implement security headers in web server configuration",
            source_analyzer="Header_Scanner_Agent"
        )
    ]
    return findings


if __name__ == "__main__":
    # Demonstration of the Security Reporting Agent
    print("Security Reporting & Summary AI Agent Demo")
    print("=" * 50)
    
    # Create agent instance
    agent = SecurityReportingAgent("Demo_Security_Agent")
    
    # Add sample findings
    sample_findings = create_sample_findings()
    agent.add_findings(sample_findings)
    
    # Generate and display human-readable report
    print("\nGenerating Human-Readable Report...")
    human_report = agent.generate_human_readable_report()
    print(human_report)
    
    # Generate machine-readable report
    print("\n" + "=" * 50)
    print("Generating Machine-Readable Report...")
    machine_report = agent.generate_machine_readable_report()
    print(json.dumps(machine_report, indent=2, default=str))
    
    # Export reports
    print("\n" + "=" * 50)
    print("Exporting Reports...")
    export_paths = agent.export_report(format_type="both", output_dir=".")
    print(f"Reports exported:")
    for format_name, path in export_paths.items():
        print(f"  {format_name}: {path}")