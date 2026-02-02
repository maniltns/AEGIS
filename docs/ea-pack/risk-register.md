# AEGIS – Risk Register

**Document:** Comprehensive Risk Assessment  
**Version:** 1.0 | January 2026

---

## Risk Summary

| Risk Level | Count | Status |
|------------|-------|--------|
| 🔴 Critical | 3 | Mitigated |
| 🟠 High | 5 | Mitigation in progress |
| 🟡 Medium | 6 | Monitored |
| 🟢 Low | 4 | Accepted |

---

## Critical Risks (Must Address)

### RISK-001: False P1 Escalation

| Attribute | Value |
|-----------|-------|
| **Risk** | AI incorrectly escalates ticket to P1, causing unnecessary paging |
| **Impact** | High – On-call fatigue, loss of trust, potential SLA breach |
| **Probability** | Medium |
| **Risk Score** | 🔴 Critical |

**Mitigation:**
- Confidence threshold: Only auto-escalate if confidence >95%
- Human approval required for all P1 escalations
- Daily review of escalation accuracy
- "Observe mode" for first 2 weeks of pilot

**Owner:** Model Steward  
**Status:** ✅ Mitigated

---

### RISK-002: VIP Misclassification

| Attribute | Value |
|-----------|-------|
| **Risk** | AI fails to identify VIP caller, routes ticket to standard queue |
| **Impact** | High – Executive dissatisfaction, reputation damage |
| **Probability** | Medium |
| **Risk Score** | 🔴 Critical |

**Mitigation:**
- VIP list integration from HR system
- Pre-enrichment check before AI triage
- VIP flag bypass: always notify L2 manager
- Weekly audit of VIP ticket handling

**Owner:** Product Owner  
**Status:** 🟡 In Progress

---

### RISK-003: Security Breach via Prompt Injection

| Attribute | Value |
|-----------|-------|
| **Risk** | Malicious ticket description causes AI to leak data or bypass controls |
| **Impact** | Critical – Data breach, compliance violation |
| **Probability** | Low |
| **Risk Score** | 🔴 Critical |

**Mitigation:**
- PII scrubber removes sensitive data before AI processing
- System prompts hardened against injection
- Rate limiting on AI calls
- Audit logging of all AI interactions
- Penetration testing before production

**Owner:** Security Approver  
**Status:** ✅ Mitigated

---

## High Risks

### RISK-004: LLM Latency During Outages

| Attribute | Value |
|-----------|-------|
| **Risk** | OpenAI/Claude API slow or unavailable during incident storms |
| **Impact** | High – Tickets queue up, MTTT degrades |
| **Probability** | Medium |
| **Risk Score** | 🟠 High |

**Mitigation:**
- Fallback to GPT-4o-mini (faster, cheaper)
- Timeout after 30 seconds, proceed without AI
- Queue mode: store tickets for batch processing
- Monitor API health, alert on degradation

**Owner:** Technical Lead  
**Status:** ✅ Mitigated

---

### RISK-005: Teams Tenant Throttling at Scale

| Attribute | Value |
|-----------|-------|
| **Risk** | MS Teams API rate limits hit during high-volume notifications |
| **Impact** | High – Notifications delayed, approvals blocked |
| **Probability** | Medium |
| **Risk Score** | 🟠 High |

**Mitigation:**
- Rate limiting: max 50 notifications/min
- Batch notifications for duplicate storms
- Priority queue: P1/P2 first, P3/P4 batched
- Fallback to email for overflow
- Monitor Teams connector health

**Owner:** Technical Lead  
**Status:** 🟡 In Progress

---

### RISK-006: Model Drift (3-6 Months)

| Attribute | Value |
|-----------|-------|
| **Risk** | AI accuracy degrades as ticket patterns change |
| **Impact** | High – Increasing false positives, agent frustration |
| **Probability** | High (certain over time) |
| **Risk Score** | 🟠 High |

**Mitigation:**
- Weekly accuracy monitoring dashboard
- Monthly model performance review
- Quarterly retraining with fresh tickets
- Automated drift detection alert (>5% drop)
- A/B testing framework for prompt changes

**Owner:** Model Steward  
**Status:** 🟡 In Progress

---

### RISK-007: Kill Switch Not Activated in Time

| Attribute | Value |
|-----------|-------|
| **Risk** | Critical issue occurs but kill switch not triggered fast enough |
| **Impact** | High – Continued AI errors compound damage |
| **Probability** | Low |
| **Risk Score** | 🟠 High |

**Mitigation:**
- 3 authorized users with kill switch access
- PIN verification <30 seconds
- Automatic kill switch on >5 false P1s in 1 hour
- Monthly kill switch drill
- Teams alert on any kill switch activation

**Owner:** Security Approver  
**Status:** ✅ Mitigated

---

### RISK-008: ServiceNow API Changes

| Attribute | Value |
|-----------|-------|
| **Risk** | ServiceNow upgrade breaks AEGIS integration |
| **Impact** | High – Complete workflow failure |
| **Probability** | Medium |
| **Risk Score** | 🟠 High |

**Mitigation:**
- Test in ServiceNow sub-prod before upgrades
- API version pinning where possible
- Maintain compatibility matrix
- Early participation in upgrade planning

**Owner:** Technical Lead  
**Status:** 🟡 Monitored

---

## Medium Risks

### RISK-009: Redis Data Loss

| Attribute | Value |
|-----------|-------|
| **Risk** | Redis crashes, Storm Shield state lost |
| **Impact** | Medium – Temporary duplicate tickets |
| **Probability** | Low |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- AOF persistence enabled
- Daily backup to S3
- 5-minute RPO acceptable

**Owner:** Ops Owner  
**Status:** ✅ Mitigated

---

### RISK-010: Agent Workflow Failure

| Attribute | Value |
|-----------|-------|
| **Risk** | CrewAI agent code error, automation fails |
| **Impact** | Medium – Manual triage required temporarily |
| **Probability** | Low |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- Git version control for all agent code
- Automated backup before changes
- Rollback procedure documented
- Container restart within 10 minutes

**Owner:** Technical Lead  
**Status:** ✅ Mitigated

---

### RISK-011: Agent Resistance to AI

| Attribute | Value |
|-----------|-------|
| **Risk** | L1 agents distrust AI, override all recommendations |
| **Impact** | Medium – ROI not achieved |
| **Probability** | Medium |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- Glass Box transparency (show reasoning)
- Training program before rollout
- Feedback mechanism for overrides
- Gamification: accuracy leaderboard
- Executive communication on goals

**Owner:** Product Owner  
**Status:** 🟡 In Progress

---

### RISK-012: GDPR Compliance Gap

| Attribute | Value |
|-----------|-------|
| **Risk** | PII processed by AI without proper controls |
| **Impact** | Medium – Regulatory fine, reputation |
| **Probability** | Low |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- PII scrubber workflow before AI
- No PII stored in ChromaDB
- Audit log retention 7 years
- DPA with OpenAI/Anthropic
- GDPR Article 5/17/30 documented

**Owner:** Security Approver  
**Status:** ✅ Mitigated

---

### RISK-013: Vendor Lock-in (OpenAI/Anthropic)

| Attribute | Value |
|-----------|-------|
| **Risk** | Dependency on specific AI provider, pricing changes |
| **Impact** | Medium – Cost increase, migration effort |
| **Probability** | Medium |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- Multi-provider architecture (OpenAI + Claude)
- AWS Bedrock as backup
- Prompts designed for portability
- Annual vendor review

**Owner:** Product Owner  
**Status:** 🟡 Monitored

---

### RISK-014: Insufficient Monitoring

| Attribute | Value |
|-----------|-------|
| **Risk** | Issues go undetected until users complain |
| **Impact** | Medium – Delayed response, trust erosion |
| **Probability** | Medium |
| **Risk Score** | 🟡 Medium |

**Mitigation:**
- Real-time dashboard (LangFlow UI)
- RedisInsight for Storm Shield
- ServiceNow audit log queries
- Splunk integration (planned)
- Daily health check email

**Owner:** Ops Owner  
**Status:** 🟡 In Progress

---

## Low Risks (Accepted)

### RISK-015: Single EC2 Instance

| Attribute | Value |
|-----------|-------|
| **Risk** | EC2 failure causes complete outage |
| **Impact** | High but recoverable |
| **Probability** | Low |
| **Risk Score** | 🟢 Low (Accepted for POC/Pilot) |

**Mitigation:**
- AMI backup for fast recovery
- Auto-restart on failure
- Scale to HA in production phase

---

### RISK-016: Knowledge Base Outdated

| Attribute | Value |
|-----------|-------|
| **Risk** | KB articles stale, RAG returns bad suggestions |
| **Impact** | Low – Human still reviews suggestions |
| **Probability** | Medium |
| **Risk Score** | 🟢 Low |

**Mitigation:**
- KB freshness indicator
- Stale KB flagged in work notes
- Feedback loop for KB updates

---

### RISK-017: Opera PMS Integration Complexity

| Attribute | Value |
|-----------|-------|
| **Risk** | OHIP API more complex than expected |
| **Impact** | Low – Phase 2 feature, can defer |
| **Probability** | Medium |
| **Risk Score** | 🟢 Low |

**Mitigation:**
- Selenium fallback
- Phase 2 scope (not blocking pilot)

---

### RISK-018: Training Gap

| Attribute | Value |
|-----------|-------|
| **Risk** | Agents not trained properly before go-live |
| **Impact** | Low – Impacts adoption, not functionality |
| **Probability** | Low |
| **Risk Score** | 🟢 Low |

**Mitigation:**
- Training sessions in pilot phase
- Quick reference guide
- Champions program

---

## Risk Monitoring Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Risk review meeting | Monthly | Product Owner |
| Accuracy monitoring | Weekly | Model Steward |
| Security review | Quarterly | Security Approver |
| Kill switch drill | Monthly | Ops Owner |
| Vendor health check | Monthly | Technical Lead |

---

*Document Owner: Anilkumar MN*  
*Security Review: Pending*  
*Last Updated: January 28, 2026*
