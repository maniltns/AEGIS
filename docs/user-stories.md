# AEGIS User Stories (Product Backlog)

**Last Updated:** January 27, 2026  
**Product Owner:** Anilkumar MN

---

## Epic 1: Intelligent Triage

### US-001: AI-Powered Ticket Classification
**As a** L1 Support Agent  
**I want** tickets to be automatically classified with AI  
**So that** I can start working on issues faster without manual categorization

**Acceptance Criteria:**
- [ ] AI correctly classifies category in >85% of cases
- [ ] Classification completes in <30 seconds
- [ ] Work notes show AI reasoning

**Story Points:** 8  
**Status:** ✅ Done (v1.0)

---

### US-002: Knowledge Base Recommendations
**As a** L1 Support Agent  
**I want** relevant KB articles suggested for each ticket  
**So that** I can resolve issues faster using existing documentation

**Acceptance Criteria:**
- [ ] Top 3 KB articles shown in work notes
- [ ] Links are clickable and valid
- [ ] Confidence score displayed

**Story Points:** 5  
**Status:** ✅ Done (v1.0)

---

### US-003: VIP Caller Prioritization
**As a** Service Desk Manager  
**I want** VIP callers identified and flagged automatically  
**So that** high-value guests receive priority support

**Acceptance Criteria:**
- [ ] VIP flag pulled from caller record
- [ ] Priority suggested as P1 for VIP
- [ ] Teams notification includes VIP badge

**Story Points:** 3  
**Status:** ✅ Done (v1.0)

---

## Epic 2: Storm Protection

### US-004: Duplicate Detection (Storm Shield)
**As a** L1 Support Agent  
**I want** duplicate tickets blocked automatically  
**So that** I don't waste time on the same issue multiple times

**Acceptance Criteria:**
- [ ] Same CI + error pattern detected within 15 min
- [ ] Duplicate ticket gets work note explaining block
- [ ] Original ticket referenced

**Story Points:** 5  
**Status:** ✅ Done (v1.0)

---

### US-005: Alert Storm Suppression
**As a** Service Desk Manager  
**I want** monitoring alert storms suppressed  
**So that** agents aren't overwhelmed during outages

**Acceptance Criteria:**
- [ ] Threshold: 5+ similar alerts in 15 min
- [ ] Only first ticket processed
- [ ] Dashboard shows storm count

**Story Points:** 5  
**Status:** ✅ Done (v1.0)

---

## Epic 3: Governance & Safety

### US-006: Kill Switch (Basic)
**As a** Service Desk Manager  
**I want** an emergency stop for all AI actions  
**So that** I can immediately halt automation if issues arise

**Acceptance Criteria:**
- [ ] Redis command stops all writes
- [ ] System enters observe-only mode
- [ ] Resume requires CAB approval

**Story Points:** 3  
**Status:** ✅ Done (v1.0)

---

### US-007: Kill Switch with Verification
**As a** Security Administrator  
**I want** Kill Switch activation to require verification  
**So that** only authorized personnel can trigger emergency stops

**Acceptance Criteria:**
- [ ] Azure AD role check (Team Lead/Manager/Security)
- [ ] 6-digit PIN verification
- [ ] All attempts logged to audit trail
- [ ] Teams notification to stakeholders

**Story Points:** 8  
**Status:** ✅ Done (v1.1)

---

### US-008: Glass Box Audit Trail
**As a** Compliance Officer  
**I want** every AI decision logged with reasoning  
**So that** we can audit and explain all automated actions

**Acceptance Criteria:**
- [ ] JSON reasoning in work notes
- [ ] Custom table (u_ai_audit_log) populated
- [ ] 7-year retention for GDPR

**Story Points:** 5  
**Status:** ✅ Done (v1.0)

---

## Epic 4: Auto-Remediation (JANITOR)

### US-009: Password Reset Automation
**As a** L1 Support Agent  
**I want** password resets automated with approval  
**So that** common issues resolve faster

**Acceptance Criteria:**
- [ ] Identity validation (caller = ticket creator)
- [ ] Standard Change template required
- [ ] Human approval via Teams card
- [ ] ARS Portal automation

**Story Points:** 13  
**Status:** 🔄 In Progress

---

### US-010: Service Restart Automation
**As a** L2 Support Engineer  
**I want** service restarts triggered via SSM  
**So that** common fixes execute without manual RDP

**Acceptance Criteria:**
- [ ] AWS SSM Run Command integration
- [ ] Pre/post screenshots
- [ ] Rollback capability

**Story Points:** 8  
**Status:** 📋 Backlog

---

### US-011: PMS Opera Automation
**As a** Hotel Operations Manager  
**I want** transaction code updates automated  
**So that** finance changes complete faster with approval

**Acceptance Criteria:**
- [ ] Finance team approval via Teams
- [ ] Opera OHIP API or Selenium
- [ ] Audit trail with hotel code

**Story Points:** 13  
**Status:** 📋 Backlog

---

## Epic 5: GDPR & Security

### US-012: PII Anonymization
**As a** Data Protection Officer  
**I want** PII removed before AI processing  
**So that** we comply with GDPR Article 5

**Acceptance Criteria:**
- [ ] Email, phone, SSN detected and redacted
- [ ] Redaction logged to audit table
- [ ] AI only sees sanitized text

**Story Points:** 5  
**Status:** ✅ Done (v1.1)

---

### US-013: Data Retention Automation
**As a** Compliance Officer  
**I want** automatic data expiry per policy  
**So that** we comply with storage limitation principle

**Acceptance Criteria:**
- [ ] Redis TTL for cache data (15 min)
- [ ] Redis TTL for audit data (7 days)
- [ ] ServiceNow archival after 90 days

**Story Points:** 5  
**Status:** 📋 Backlog

---

## Backlog Summary

| Status | Count | Story Points |
|--------|-------|--------------|
| ✅ Done | 9 | 47 |
| 🔄 In Progress | 1 | 13 |
| 📋 Backlog | 3 | 26 |
| **Total** | **13** | **86** |

---

## Velocity Tracking

| Sprint | Points Completed |
|--------|-----------------|
| Sprint 1 (Jan 20-26) | 42 |
| Sprint 2 (Jan 27-Feb 2) | TBD |
