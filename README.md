# Agent_Injection

## Security Reporting & Summary AI Agent

This repository contains an AI agent that aggregates and summarizes findings from analyzer agents, producing comprehensive security reports with technical details, risk scoring, executive summaries, and prioritized remediation actions. The agent outputs both human-readable and machine-readable formats.

### Features

- **Comprehensive Security Analysis**: Processes security findings from multiple analyzer agents
- **Risk Scoring**: Calculates overall risk scores based on severity, CVSS scores, and finding categories
- **Executive Summaries**: Generates high-level summaries for management and stakeholders
- **Prioritized Remediation**: Creates actionable remediation plans with priority ordering
- **Dual Output Formats**: Produces both human-readable reports and machine-readable JSON
- **Flexible Configuration**: Configurable risk thresholds and reporting parameters

### Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic Usage**:
   ```python
   from security_reporting_agent import SecurityReportingAgent, SecurityFinding, SeverityLevel, FindingCategory
   
   # Create agent instance
   agent = SecurityReportingAgent("MySecurityAgent")
   
   # Add security findings
   finding = SecurityFinding(
       id="VULN-001",
       title="SQL Injection Vulnerability",
       description="User input not properly sanitized",
       severity=SeverityLevel.CRITICAL,
       category=FindingCategory.VULNERABILITY,
       affected_assets=["web-app", "database"],
       cvss_score=9.8
   )
   agent.add_finding(finding)
   
   # Generate reports
   human_report = agent.generate_human_readable_report()
   machine_report = agent.generate_machine_readable_report()
   
   # Export to files
   export_paths = agent.export_report(format_type="both")
   ```

3. **Run Demo**:
   ```bash
   python security_reporting_agent.py
   ```

### Core Components

#### SecurityFinding
Represents individual security findings with:
- Unique ID and metadata
- Severity levels (Critical, High, Medium, Low, Info)
- Categories (Vulnerability, Misconfiguration, Compliance, etc.)
- CVSS scoring support
- Affected assets tracking

#### SecurityReportingAgent
Main agent class providing:
- Finding aggregation and analysis
- Risk score calculation
- Executive summary generation
- Remediation action planning
- Multi-format report export

#### Report Formats

**Human-Readable**: Detailed text reports with:
- Executive summary with risk assessment
- Findings organized by severity
- Detailed remediation actions with step-by-step guidance
- Asset impact analysis

**Machine-Readable**: JSON format with:
- Structured finding data
- Summary statistics
- Risk metrics
- Programmatic access to all report elements

### Configuration

The agent uses `config.json` for customization:
- Risk scoring weights and thresholds
- Report formatting options
- Output file settings
- Agent metadata

### Integration

The agent is designed to work with various analyzer agents:
- Vulnerability scanners
- Configuration analyzers
- Compliance checkers
- Access control auditors
- Network security tools

Simply create `SecurityFinding` objects from your analyzer results and feed them to the reporting agent.

### Example Output

The agent generates comprehensive reports including:
- Overall risk score (0-100)
- Severity distribution charts
- Category-based analysis
- Prioritized action items
- Technical details for each finding
- Remediation timelines and effort estimates

### Architecture

```
Analyzer Agents → SecurityFinding Objects → SecurityReportingAgent → Reports
     ↓                    ↓                         ↓               ↓
[Scanner A]        [Finding Data]           [Analysis Engine]  [Human Report]
[Scanner B]   →    [Risk Scoring]      →    [Report Generator] → [JSON Export]
[Scanner C]        [Categorization]         [Action Planning]  [File Export]
```

This agent serves as the central intelligence layer for security reporting, transforming raw findings into actionable security intelligence.