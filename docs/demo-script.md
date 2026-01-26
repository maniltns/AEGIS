# AEGIS Workshop Demo Script
## February 4, 2026 | Accor Hotels

---

## 👥 Presenters & Timing

| Time | Topic | Presenter |
|------|-------|-----------|
| 09:00-09:30 | Problem Statement & Vision | Leadership |
| 09:30-09:50 | **Live Demo: AEGIS in Action** | Anilkumar MN & Ramanathan |
| 09:50-10:20 | Architecture Deep-Dive | Anilkumar MN |
| 10:20-10:50 | Q&A & Feedback | All |
| 10:50-11:30 | Pilot Scope Discussion | Leadership |

---

## 🎬 Live Demo Script (20 minutes)

### Pre-Demo Checklist
- [ ] n8n running at http://localhost:5678
- [ ] Redis running with governance keys set
- [ ] ServiceNow Train instance accessible
- [ ] Teams channel ready for notifications
- [ ] Demo incidents pre-created

---

### Demo 1: Storm Shield (3 min)

**Scenario:** Alert storm from printer - 5 identical tickets in 2 minutes

**Steps:**
1. Show Redis is empty: `redis-cli KEYS storm:*`
2. Create first incident → Show PASS in n8n
3. Create 4 more identical incidents → Show BLOCK count
4. View work notes: "🛡️ GUARDIAN - Duplicate blocked #2, #3, #4, #5"

**Key Message:** *"Storm Shield prevents agent fatigue from alert floods"*

---

### Demo 2: AI Triage (5 min)

**Scenario:** Hotel reports "Wi-Fi not working in conference room"

**Steps:**
1. Create incident with vague description
2. Show workflow executing: GUARDIAN → SCOUT → SHERLOCK
3. Highlight SHERLOCK work notes:
   - Assessment
   - Root cause (likely AP issue)
   - KB article suggestion
   - Confidence score
   - **Glass Box reasoning**
4. Show Teams notification card

**Key Message:** *"AI explains WHY - full Glass Box transparency"*

---

### Demo 3: Case to Incident (5 min)

**Scenario:** Guest complaint → Technical issue requires L2

**Steps:**
1. Create Case with "Guest reports TV not turning on"
2. L1 flags "Needs Incident" checkbox
3. Show BRIDGE workflow:
   - SHERLOCK classifies (Technical vs Inquiry)
   - Creates incident automatically
   - Links Case ↔ Incident
4. Show work notes with reasoning

**Key Message:** *"Seamless Case → Incident handoff with AI classification"*

---

### Demo 4: Kill Switch (3 min)

**Scenario:** Emergency governance override

**Steps:**
1. Show current mode: `redis-cli GET gov:mode` → "assist"
2. Flip kill switch: `redis-cli SET gov:killswitch false`
3. Run workflow → Show "OBSERVE mode" logged
4. Demonstrate no writes occurred
5. Re-enable: `redis-cli SET gov:killswitch true`

**Key Message:** *"One command stops all AI writes - full control always"*

---

### Demo 5: RITM Finance Approval (4 min)

**Scenario:** Hotel requests transaction code change in Opera

**Steps:**
1. Show RITM in ServiceNow
2. Workflow sends Teams card to Finance channel
3. Show actionable buttons: Approve/Reject
4. Click Approve
5. Show RITM updated + audit trail

**Key Message:** *"Human-in-the-loop for business-critical actions"*

---

## 🗣️ Key Talking Points

### Glass Box (Repeat Often)
- "AI never acts in secret"
- "Every decision has reasoning attached"
- "Full audit trail for compliance"

### Value Proposition
- **MTTT Reduction:** 60% faster triage
- **Agent Fatigue:** 80% less duplicate handling
- **Accuracy:** 90%+ classification with KB backing
- **Compliance:** SOX-ready audit logging

---

## ❓ Anticipated Questions

| Question | Answer |
|----------|--------|
| What if AI is wrong? | Glass Box means humans see reasoning and can override |
| Security concerns? | All actions logged, kill switch available, Standard Change required for JANITOR |
| Cost? | GPT-4o-mini for classification, GPT-4o for complex only |
| Timeline? | Pilot Feb 5, Production Mar 3 |

---

## 📊 Success Metrics to Show

| Metric | POC Target | Current |
|--------|------------|---------|
| Triage Accuracy | >80% | Demo |
| MTTT (Mean Time To Triage) | <60 sec | Demo |
| Storm Shield Block Rate | >90% duplicates | Demo |
| Kill Switch Response | <1 sec | Demo |

---

© 2026 AEGIS × Accor | *"Your AI Shield Against Incident Chaos"*
