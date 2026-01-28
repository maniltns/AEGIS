# AEGIS – Operating Model

**Document:** Operating Model & Ownership  
**Version:** 1.0 | January 2026

---

## 1. Before / After Operating Model

### Current State (Without AEGIS)

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT STATE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User → ServiceNow → L1 Agent (Manual Triage)              │
│                          │                                  │
│                          ├── Read ticket (2 min)            │
│                          ├── Search KB manually (5 min)     │
│                          ├── Categorize (3 min)             │
│                          ├── Assign to L2 (2 min)           │
│                          └── Update work notes (3 min)      │
│                                                             │
│   Time: 15+ minutes | Accuracy: 70% | Duplicates: Manual    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Future State (With AEGIS)

```
┌─────────────────────────────────────────────────────────────┐
│                    FUTURE STATE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User → ServiceNow → AEGIS (Auto Triage)                   │
│                          │                                  │
│                          ├── Storm Shield (duplicates)      │
│                          ├── RAG Search (KB + history)      │
│                          ├── AI Classification (90%+)       │
│                          ├── Auto-assign to correct team    │
│                          └── Work notes with reasoning      │
│                                                             │
│                          ↓                                  │
│                    L1 Agent (Review & Approve)              │
│                          │                                  │
│                          └── Validate AI suggestion (1 min) │
│                                                             │
│   Time: <1 minute | Accuracy: 90%+ | Duplicates: Auto-block │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Ownership Roles (RACI)

| Role | Responsibility | Name/Team |
|------|---------------|-----------|
| **Product Owner** | Roadmap, priorities, stakeholder alignment | Anilkumar MN |
| **Technical Lead** | Architecture, n8n workflows, integrations | Engineering Team |
| **Model Steward** | LLM accuracy monitoring, prompt tuning, drift detection | AI/ML Team |
| **Security Approver** | PII compliance, access reviews, kill switch authority | CISO Office |
| **Operations Owner** | Day-2 monitoring, incident response, SLA tracking | IT Ops |
| **Change Manager** | Production deployments, CAB submissions | Change Management |

### Decision Authority Matrix

| Decision Type | Authority | Approval Required |
|--------------|-----------|-------------------|
| New automation rule | Model Steward | Product Owner |
| Production deployment | Technical Lead | Change Manager + CAB |
| Kill switch activation | Security Approver | Immediate (post-audit) |
| Model/prompt changes | Model Steward | Product Owner + Testing |
| New integration | Technical Lead | Security Approver |

---

## 3. Process Ownership

### 3.1 Automation Approval Process

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Request │ →  │ Review  │ →  │ Test in │ →  │ Deploy  │
│ New     │    │ by Model│    │ Staging │    │ to Prod │
│ Rule    │    │ Steward │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     └── Requestor  └── 2 days     └── 3 days     └── CAB
```

### 3.2 Model Accuracy Review Cycle

| Frequency | Activity | Owner |
|-----------|----------|-------|
| **Daily** | Check error logs, false positives | Operations |
| **Weekly** | Accuracy metrics review | Model Steward |
| **Monthly** | Full accuracy audit, prompt tuning | Model Steward + PO |
| **Quarterly** | Model drift assessment, retraining decision | AI/ML Team |

### 3.3 Production Change Sign-Off

| Change Type | Approvers | SLA |
|-------------|-----------|-----|
| **Standard** (config) | Technical Lead | 24 hours |
| **Normal** (new workflow) | Technical Lead + Ops Owner | 5 days |
| **Emergency** (hotfix) | Product Owner + Security | 4 hours |
| **Major** (new agent) | Full CAB | 10 days |

---

## 4. Escalation Matrix

| Severity | Condition | Escalation Path | Response Time |
|----------|-----------|-----------------|---------------|
| **P1** | AEGIS down, all AI stopped | On-call → Tech Lead → PO | 15 min |
| **P2** | Single workflow failing | On-call → Tech Lead | 1 hour |
| **P3** | Accuracy degradation | Model Steward → PO | 4 hours |
| **P4** | Enhancement request | Normal queue | 5 days |

---

## 5. Support Model

### L1 Support (Operations Team)
- Monitor AEGIS dashboards
- Restart failed workflows
- Activate/deactivate kill switch
- Escalate accuracy issues

### L2 Support (Technical Team)
- Debug n8n workflow errors
- Fix integration issues
- Tune prompts for edge cases

### L3 Support (Engineering Team)
- Architecture changes
- New agent development
- Model retraining

---

## 6. Governance Cadence

| Meeting | Frequency | Attendees | Purpose |
|---------|-----------|-----------|---------|
| **Daily Standup** | Daily | Ops, Tech Lead | Status, blockers |
| **Accuracy Review** | Weekly | Model Steward, PO | Metrics, tuning |
| **Stakeholder Sync** | Bi-weekly | PO, Business | Roadmap, feedback |
| **Governance Board** | Monthly | All owners | Strategy, risks |

---

## 7. Key Metrics Ownership

| Metric | Owner | Target | Review Frequency |
|--------|-------|--------|------------------|
| MTTT (Mean Time To Triage) | Ops Owner | <60 seconds | Daily |
| Triage Accuracy | Model Steward | >90% | Weekly |
| Storm Shield Block Rate | Tech Lead | >95% duplicates | Weekly |
| System Availability | Ops Owner | 99.5% | Daily |
| Kill Switch Response | Security | <10 seconds | Monthly test |

---

*Document Owner: Anilkumar MN | Last Updated: January 28, 2026*
