# AEGIS – Path to Production

**Gate-Based Roadmap with Entry/Exit Criteria**  
*Version 1.0 | January 2026*

---

## Overview

This document defines the formal gates, entry criteria, exit criteria, and KPIs required to progress AEGIS from proof-of-concept to production.

---

## Gate Model

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   GATE 0    │  →   │   GATE 1    │  →   │   GATE 2    │  →   │   GATE 3    │
│   POC       │      │   PILOT     │      │ PRODUCTION  │      │   SCALE     │
│   Ready     │      │   Ready     │      │   Ready     │      │   Ready     │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
    Jan 26              Feb 5               Mar 3              Apr 15
      ✅                 🟡                  ⏳                  ⏳
```

---

## Gate 0: POC Ready

**Status:** ✅ COMPLETE (January 26, 2026)

### Entry Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| n8n orchestration deployed | ✅ | Docker running |
| Redis Storm Shield configured | ✅ | Governance keys set |
| AI triage workflow functional | ✅ | master-triage.json |
| ServiceNow integration tested | ✅ | API calls working |
| Demo environment stable | ✅ | localhost:5678 |

### Exit Criteria

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Triage accuracy (test set) | >80% | 92% | ✅ Pass |
| Storm Shield block rate | >90% | 97% | ✅ Pass |
| Kill switch functional | <10 sec | 2 sec | ✅ Pass |
| Zero data leakage | 0 incidents | 0 | ✅ Pass |

### Approvers

| Role | Name | Approval |
|------|------|----------|
| Product Owner | Anilkumar MN | ✅ Approved |
| Technical Lead | Engineering | ✅ Approved |

---

## Gate 1: Pilot Ready

**Status:** 🟡 IN PROGRESS

### Entry Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| POC Gate 0 passed | ✅ | Above |
| Executive workshop completed | ⏳ | Feb 4 scheduled |
| Pilot hotels identified | ✅ | 3 hotels selected |
| Change request submitted | ⏳ | CHG pending |
| Operating model defined | ✅ | operating-model.md |
| Risk register approved | ⏳ | Pending security review |

### Exit Criteria

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| MTTT (production tickets) | <60 sec | -- | ⏳ Pending |
| Triage accuracy (live) | >85% | -- | ⏳ Pending |
| Agent satisfaction | >70% | -- | ⏳ Pending |
| Zero P1 incidents caused | 0 | -- | ⏳ Pending |
| 4 weeks stable operation | 28 days | -- | ⏳ Pending |

### Approvers

| Role | Name | Approval |
|------|------|----------|
| Product Owner | Anilkumar MN | ⏳ Pending |
| Security Approver | CISO Office | ⏳ Pending |
| Change Manager | Change Management | ⏳ Pending |
| Business Sponsor | TBD | ⏳ Pending |

---

## Gate 2: Production Ready

**Status:** ⏳ NOT STARTED (Target: March 3, 2026)

### Entry Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| Pilot Gate 1 passed | ⏳ | Pending |
| 4 weeks stable pilot | ⏳ | Metrics required |
| CAB approval obtained | ⏳ | CHG required |
| Security assessment passed | ⏳ | Penetration test |
| Operating model staffed | ⏳ | Team assignments |
| Runbook documented | ⏳ | Ops procedures |
| Rollback plan approved | ⏳ | DR plan |

### Exit Criteria

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| MTTT | <60 sec | -- | ⏳ |
| Triage accuracy | >90% | -- | ⏳ |
| System availability | >99.5% | -- | ⏳ |
| Agent productivity gain | >25% | -- | ⏳ |
| 30 days stable operation | 30 days | -- | ⏳ |
| Zero security incidents | 0 | -- | ⏳ |

### Approvers

| Role | Name | Approval |
|------|------|----------|
| Product Owner | Anilkumar MN | ⏳ |
| Security Approver | CISO Office | ⏳ |
| Operations Owner | IT Ops | ⏳ |
| Change Manager | Change Management | ⏳ |
| Executive Sponsor | TBD | ⏳ |

---

## Gate 3: Scale Ready

**Status:** ⏳ NOT STARTED (Target: April 15, 2026)

### Entry Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| Production Gate 2 passed | ⏳ | Pending |
| 30 days stable production | ⏳ | SLA compliance |
| Regional rollout plan approved | ⏳ | Deployment plan |
| Training program complete | ⏳ | L1/L2 trained |
| Support model operational | ⏳ | 24x7 coverage |

### Exit Criteria

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Hotels onboarded | 50+ | -- | ⏳ |
| Monthly ticket volume | 20,000+ | -- | ⏳ |
| Agent adoption rate | >80% | -- | ⏳ |
| ROI validated | >$200K/year | -- | ⏳ |

---

## KPI Summary by Gate

| KPI | POC | Pilot | Production | Scale |
|-----|-----|-------|------------|-------|
| Triage Accuracy | >80% | >85% | >90% | >92% |
| MTTT | <5 min | <2 min | <60 sec | <45 sec |
| System Uptime | >95% | >99% | >99.5% | >99.9% |
| Agent Satisfaction | N/A | >70% | >80% | >85% |
| Ticket Volume | 100 | 500 | 5,000 | 20,000 |

---

## Risk Gates (No-Go Conditions)

| Condition | Gate | Action |
|-----------|------|--------|
| Accuracy <70% | Any | Stop, retrain model |
| P1 caused by AEGIS | Any | Stop, root cause, fix |
| Security breach | Any | Kill switch, investigation |
| >3 false escalations/day | Pilot+ | Pause, tune thresholds |
| Model drift >10% | Prod+ | Pause, retrain |

---

## Governance Checkpoints

| Checkpoint | Frequency | Owner | Output |
|------------|-----------|-------|--------|
| Daily health check | Daily | Ops | Green/Yellow/Red |
| Weekly metrics review | Weekly | Model Steward | Accuracy report |
| Bi-weekly stakeholder | Bi-weekly | Product Owner | Status update |
| Monthly governance | Monthly | All owners | Gate assessment |

---

*Document Owner: Anilkumar MN*  
*Approved By: [Pending Workshop]*  
*Last Updated: January 28, 2026*
