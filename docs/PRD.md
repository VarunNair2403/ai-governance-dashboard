# PRD: AI Governance Dashboard

**Author:** Varun Nair
**Status:** v1.0 — Complete
**Last Updated:** April 2026

---

## Problem Statement

Financial institutions are deploying AI systems at an unprecedented pace. LLMs are being used for customer service, research, compliance, and internal tooling. But the governance frameworks to oversee these systems have not kept pace with deployment velocity.

Three specific failure modes are emerging:

1. **PII leakage** — users submit prompts containing social security numbers, email addresses, and financial account numbers. Without input screening, this data flows into LLM context windows, training pipelines, and logs, creating GDPR, CCPA, and GLBA violations.

2. **Adversarial inputs** — prompt injection and jailbreak attempts are increasingly common. Without detection, bad actors can manipulate AI systems to bypass safety controls, exfiltrate system prompts, or generate harmful outputs.

3. **No audit trail** — regulators including the SEC, OCC, and FRB are beginning to require evidence that AI systems have governance controls. Most firms cannot produce an audit log of what flowed through their AI systems.

The NIST AI Risk Management Framework provides a structured approach to addressing these risks, but most teams lack tooling that operationalizes the framework in real time. This project builds that tooling.

---

## Target Users

- **AI Governance Officers** — need real-time visibility into what is flowing through AI systems and evidence of controls for regulators
- **Chief Risk Officers** — need a dashboard view of AI risk exposure across severity levels with actionable reports
- **Compliance Teams** — need findings mapped to specific regulations (GDPR, CCPA, GLBA) with documented mitigations
- **AI Engineering Teams** — need a screening layer they can integrate into their LLM pipelines without building governance from scratch
- **Internal Audit** — need a tamper-evident audit log of all AI governance events for regulatory submissions

---

## Goals

**Primary Goals**
- Screen LLM inputs and outputs in real time for PII, toxicity, policy violations, and bias
- Map every finding to the NIST AI RMF framework with severity classification
- Generate plain-English governance reports using Claude that are suitable for senior stakeholder review
- Maintain a full audit log of every governance event for regulatory auditability

**Secondary Goals**
- Expose governance capabilities as a REST API for integration into existing AI pipelines
- Demonstrate a production-ready governance architecture that maps to regulatory requirements
- Use Claude intentionally — Anthropic's Constitutional AI principles make it the right model for a governance tool

**Non-Goals for v1**
- Real-time streaming input screening at sub-millisecond latency
- Output screening (only input screening in v1)
- Fine-tuned governance models
- RBAC and multi-user access control
- Integration with enterprise SIEM systems
- Automated regulatory report generation

---

## Success Metrics

- **Detection accuracy** — PII, toxicity, policy violations, and bias correctly flagged across test cases
- **NIST mapping correctness** — every finding maps to the correct NIST AI RMF function and category
- **Report quality** — Claude-generated reports reference correct regulations and provide actionable mitigations
- **Audit completeness** — every governance event logged with no data loss
- **API response time** — /screen endpoint returns in under 8 seconds including Claude call
- **False positive rate** — clean inputs correctly pass with LOW severity and no findings

---

## Scope — What Is In v1

- Four governance checks: toxicity, PII, policy violation, bias
- NIST AI RMF mapping for all four checks across GOVERN, MAP, MEASURE, MANAGE functions
- Severity classification: CRITICAL, HIGH, MEDIUM, LOW
- Claude-powered governance report generation with Executive Summary, Risks, Mitigations, Compliance Implications, and Sign-off
- SQLite audit log with timestamp, severity, findings, and full report
- Audit statistics: total events, flagged count, avg risk score, severity breakdown
- Interactive CLI with history and stats commands
- FastAPI REST API with /health, /screen, /audit, and /stats endpoints

## Scope — What Is Out of v1

- LLM output screening
- Real-time streaming screening
- RBAC and user authentication
- SIEM integration
- Automated regulatory report generation
- Fine-tuned governance model
- Multi-modal screening (images, audio)
- Frontend dashboard UI

---

## Feature Breakdown

**1. Governance Checks (checks.py)**
Four parallel checks run on every submitted text. Toxicity detection uses the better-profanity library to flag harmful language. PII detection uses Microsoft Presidio with spaCy NLP to identify email addresses, SSNs, phone numbers, credit card numbers, and other personal identifiers. Policy violation detection uses keyword matching to catch prompt injection patterns such as "ignore previous instructions" and jailbreak attempts. Bias detection uses pattern matching to identify language associated with discriminatory or biased content. Each check returns a flagged boolean, a risk score between 0 and 1, and a plain-English detail message.

**2. NIST AI RMF Mapping (nist_mapper.py)**
Maps each flagged check to a specific NIST AI RMF function, category, and subcategory. PII maps to MAP MP-2.3 at CRITICAL severity. Policy violations map to GOVERN GV-1.1 at CRITICAL severity. Toxicity maps to MANAGE MG-2.2 at HIGH severity. Bias maps to MEASURE MS-2.5 at HIGH severity. Findings are sorted by severity and the highest severity finding determines the overall event severity.

**3. Claude Governance Report (claude_client.py + reporter.py)**
Builds a structured prompt from all NIST findings and sends it to Claude claude-haiku-4-5-20251001 with a governance officer system prompt. For flagged events the report includes Executive Summary, Identified Risks with GDPR/CCPA/GLBA regulatory implications, Recommended Mitigations broken into Immediate (0-24h), Short-term (1-2 weeks), and Medium-term (1-3 months) actions, Compliance Implications, and a Sign-off recommendation. For clean inputs the report generates a clearance confirmation.

**4. Audit Logging (audit.py)**
Logs every governance event to SQLite with timestamp, context, text, severity, risk score, NIST functions triggered, findings JSON, and full report text. Provides retrieval of the last N events and aggregate statistics for dashboard use.

**5. CLI (cli.py)**
Interactive terminal interface with a continuous input loop. Supports free text screening, history command to view recent events, and stats command to view aggregate metrics. Each screening run prints the status, severity, findings, and full governance report.

**6. REST API (api.py)**
Four endpoints via FastAPI. GET /health for liveness. POST /screen accepts text and context, runs the full governance pipeline, logs the event, and returns the complete result. GET /audit returns the last N logged events. GET /stats returns aggregate governance metrics.

---

## Technical Architecture

Data flows in one direction:

Text input → checks.py → four parallel screens → nist_mapper.py → NIST findings with severity → reporter.py → Claude prompt → claude_client.py → Anthropic API → governance report → audit.py → SQLite → cli.py or api.py → output

Stack: Python 3.11+, Anthropic Claude, Microsoft Presidio, better-profanity, spaCy, SQLite, FastAPI, Uvicorn, python-dotenv

---

## Regulatory Framework Coverage

- **GDPR** — Article 4(1) personal data definition, Article 5 data processing principles, Article 6 lawful basis, Article 32 security measures, Articles 13-14 transparency requirements
- **CCPA** — Section 1798.100 consumer rights, Section 1798.115 data disclosure, Section 1798.150 private right of action
- **GLBA** — Section 501(b) safeguards rule for financial institutions
- **NIST AI RMF** — GOVERN, MAP, MEASURE, MANAGE functions with specific category mappings

---

## Production Roadmap

- **Middleware deployment** — deploy as a sidecar service that intercepts every LLM request and response in the firm's AI infrastructure
- **Output screening** — extend checks to evaluate LLM outputs for hallucination, factual inaccuracy, and policy violations
- **SIEM integration** — pipe CRITICAL and HIGH events to Splunk or Azure Sentinel in real time
- **RBAC** — role-based access control so governance officers see full reports and engineers see summaries only
- **Alerting** — PagerDuty or Slack alerts for CRITICAL events with on-call escalation
- **Regulatory reporting** — auto-generate monthly NIST AI RMF compliance reports from audit log aggregates
- **Fine-tuning** — fine-tune Claude on firm-specific governance policies and past incident reports
- **Multi-modal** — extend PII and toxicity detection to image and audio inputs
- **Dashboard UI** — Retool or Grafana dashboard over /stats and /audit endpoints for governance officers

---

## Open Questions

1. Should output screening be added in v1.1 or does it require a separate deployment model?
2. At what event volume does SQLite need to be replaced with PostgreSQL for concurrent audit logging?
3. Should CRITICAL events trigger an automatic hold on the AI session pending human review?
4. How should the system handle false positives — for example URLs flagged as PII?
5. Should governance reports be stored in full in the audit log or summarized to reduce storage costs?