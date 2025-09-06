#!/usr/bin/env python3
"""
Example usage of the Security Reporting & Summary AI Agent

This script demonstrates how to integrate the security reporting agent
with findings from various analyzer agents.
"""

from security_reporting_agent import (
    SecurityReportingAgent, 
    SecurityFinding, 
    SeverityLevel, 
    FindingCategory
)
from datetime import datetime


def simulate_analyzer_findings():
    """Simulate findings from different analyzer agents"""
    findings = []
    
    # Vulnerability scanner findings
    findings.append(SecurityFinding(
        id="VULN-2024-001",
        title="Remote Code Execution in Web Framework",
        description="Deserialization vulnerability allows remote code execution",
        severity=SeverityLevel.CRITICAL,
        category=FindingCategory.VULNERABILITY,
        affected_assets=["web-server", "api-gateway"],
        cvss_score=9.9,
        cve_id="CVE-2024-12345",
        remediation="Update framework to latest version and validate input",
        source_analyzer="VulnScanner_Pro"
    ))
    
    # Configuration analyzer findings
    findings.append(SecurityFinding(
        id="CONFIG-2024-001",
        title="Database Exposed to Internet",
        description="Database server accessible from public internet",
        severity=SeverityLevel.HIGH,
        category=FindingCategory.MISCONFIGURATION,
        affected_assets=["database-server"],
        cvss_score=8.1,
        remediation="Configure firewall to restrict database access",
        source_analyzer="ConfigAuditor"
    ))
    
    # Compliance checker findings
    findings.append(SecurityFinding(
        id="COMP-2024-001",
        title="PCI DSS Compliance Violation",
        description="Credit card data stored without encryption",
        severity=SeverityLevel.HIGH,
        category=FindingCategory.COMPLIANCE,
        affected_assets=["payment-system"],
        cvss_score=7.8,
        remediation="Implement encryption for cardholder data",
        source_analyzer="ComplianceChecker"
    ))
    
    return findings


def main():
    print("Security Reporting Agent - Integration Example")
    print("=" * 50)
    
    # Create the reporting agent
    agent = SecurityReportingAgent("Production_Security_Agent")
    
    # Simulate receiving findings from analyzer agents
    print("Simulating findings from analyzer agents...")
    findings = simulate_analyzer_findings()
    
    # Add findings to the reporting agent
    agent.add_findings(findings)
    
    print(f"Processed {len(findings)} security findings")
    print(f"Overall Risk Score: {agent.calculate_risk_score()}/100")
    
    # Generate and export reports
    print("\nExporting security reports...")
    export_paths = agent.export_report(format_type="both", output_dir="./reports")
    
    print("Reports generated:")
    for format_type, path in export_paths.items():
        print(f"  {format_type}: {path}")
    
    # Show executive summary
    print("\n" + "=" * 50)
    print("EXECUTIVE SUMMARY")
    print("=" * 50)
    print(agent.generate_executive_summary())


if __name__ == "__main__":
    main()