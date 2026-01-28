# AEGIS Sprint Backlog

**Sprint:** 2  
**Duration:** January 27 - February 2, 2026  
**Sprint Goal:** Complete security enhancements and prepare for Feb 4 demo

---

## Sprint 2 Board

### 📋 To Do

| ID | Story | Points | Assignee |
|----|-------|--------|----------|
| US-010 | Service Restart Automation | 8 | TBD |
| T-015 | Configure Azure AD groups | 2 | DevOps |
| T-016 | Test Kill Switch in staging | 3 | QA |

### 🔄 In Progress

| ID | Story | Points | Assignee | Started |
|----|-------|--------|----------|---------|
| US-009 | Password Reset Automation | 13 | Team | Jan 27 |

### ✅ Done (This Sprint)

| ID | Story | Points | Completed |
|----|-------|--------|-----------|
| US-007 | Kill Switch with Verification | 8 | Jan 27 |
| US-012 | PII Anonymization | 5 | Jan 27 |
| T-011 | Security Framework docs | 3 | Jan 27 |
| T-012 | GDPR Compliance docs | 3 | Jan 27 |
| T-013 | Update docker-compose security | 2 | Jan 27 |
| T-014 | Create security-config.env | 1 | Jan 27 |

---

## Tasks Breakdown

### US-009: Password Reset Automation

| Task | Status | Assignee |
|------|--------|----------|
| T-009a: Identity validation logic | ☐ To Do | |
| T-009b: ARS Portal Selenium script | ☐ To Do | |
| T-009c: Approval card design | ☐ To Do | |
| T-009d: Integration testing | ☐ To Do | |

### Demo Preparation

| Task | Status | Assignee |
|------|--------|----------|
| T-020: Update demo-script.md | ☐ To Do | |
| T-021: Prepare test data | ☐ To Do | |
| T-022: Rehearsal run | ☐ To Do | |
| T-023: Stakeholder invites | ☐ To Do | |

---

## Sprint Metrics

### Capacity

| Team Member | Available Days | Story Points |
|-------------|---------------|--------------|
| Dev 1 | 5 | 10 |
| Dev 2 | 5 | 10 |
| QA | 5 | 5 |
| **Total** | — | **25** |

### Burndown

| Day | Planned | Actual | Remaining |
|-----|---------|--------|-----------|
| Mon (Jan 27) | 25 | 22 | 3 done today |
| Tue (Jan 28) | 20 | — | — |
| Wed (Jan 29) | 15 | — | — |
| Thu (Jan 30) | 10 | — | — |
| Fri (Jan 31) | 5 | — | — |
| Mon (Feb 3) | 0 | — | — |

---

## Blockers & Risks

| ID | Blocker | Impact | Mitigation | Owner |
|----|---------|--------|------------|-------|
| B-001 | Azure AD group approval | Kill Switch test blocked | Request expedited | PM |
| R-001 | ARS Portal access | Password Reset delayed | Use mock for demo | Dev |

---

## Definition of Done

- [ ] Code complete and reviewed
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security review (if applicable)
- [ ] Documentation updated
- [ ] Work notes in ServiceNow updated
- [ ] Demo-ready

---

## Sprint 2 Retrospective Notes

*To be filled after sprint end*

### What went well?
- 

### What could improve?
- 

### Action items?
- 

---

## Previous Sprints

### Sprint 1 (Jan 20-26, 2026)
- **Goal:** Complete POC workflows
- **Velocity:** 42 points
- **Highlights:** Core triage, Storm Shield, Case→Incident complete
