# 🛡️ AEGIS - Autonomous Expert for Governance, Intelligence & Swarming

**Client:** Accor Hotels  
**Version:** 1.1 (Enterprise Swarm Edition)  
**Tagline:** *"Your AI Shield Against Incident Chaos"*

---

## 📚 Documentation

| Document | Location |
|----------|----------|
| **Implementation Plan** | [docs/implementation_plan.md](docs/implementation_plan.md) |
| **Demo Script** | [docs/demo-script.md](docs/demo-script.md) |

---

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd d:\AI-Ops\AISwarnOps

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials

# 3. Start Docker stack
cd docker
docker-compose up -d

# 4. Initialize Redis governance
docker exec aegis-redis redis-cli SET gov:killswitch true
docker exec aegis-redis redis-cli SET gov:mode assist

# 5. Access n8n
# Open http://localhost:5678
# Login: admin / aegis2026

# 6. Import workflows (6 total)
# Import all JSON files from /workflows folder
```

---

## 📂 Project Structure

```
aegis/
├── docker/
│   ├── docker-compose.yml      # Redis Stack + n8n
│   └── init-redis.sh           # Governance key init
├── workflows/
│   ├── storm-shield.json       # 🛡️ GUARDIAN - Deduplication
│   ├── kill-switch.json        # ⚖️ ARBITER - Governance
│   ├── kb-search.json          # 📚 KB Lookup for SHERLOCK
│   ├── master-triage.json      # Full triage pipeline
│   ├── case-to-incident.json   # 🌉 BRIDGE - Case conversion
│   └── ritm-finance.json       # 💰 Hotel Finance approval
├── docs/
│   ├── implementation_plan.md  # Full project plan
│   └── demo-script.md          # Workshop demo script
└── .env.example                # Environment template
```

---

## 🤖 Agent Roster

| Agent | Icon | Role | Workflow |
|-------|------|------|----------|
| GUARDIAN | 🛡️ | Storm Shield | storm-shield.json |
| SCOUT | 🔍 | Context Enrichment | master-triage.json |
| SHERLOCK | 🕵️ | RCA & Triage | master-triage.json |
| ROUTER | 🚦 | Assignment | master-triage.json |
| ARBITER | ⚖️ | Governance | kill-switch.json |
| HERALD | 📢 | Notifications | master-triage.json |
| SCRIBE | 📝 | Audit Logging | master-triage.json |
| BRIDGE | 🌉 | Case→Incident | case-to-incident.json |
| JANITOR | 🧹 | Auto-Remediation | *Phase 2* |

---

## 🔧 Configuration

### Redis Governance Keys

```bash
# Kill Switch
SET gov:killswitch true   # System enabled
SET gov:killswitch false  # EMERGENCY STOP

# Mode
SET gov:mode observe   # Log only
SET gov:mode assist    # Write + human review
SET gov:mode execute   # Autonomous (future)
```

---

## 🛡️ Glass Box Principles

| # | Principle | Implementation |
|---|-----------|----------------|
| 1 | Transparency | SHERLOCK outputs JSON with reasoning |
| 2 | Human-in-Loop | ARBITER gates all writes |
| 3 | Auditability | SCRIBE logs to `u_ai_audit_log` |
| 4 | Reversibility | Work notes capture pre/post state |
| 5 | Explainability | KB references + confidence scores |

---

## 📊 Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| n8n | http://localhost:5678 | Workflow orchestration |
| RedisInsight | http://localhost:8001 | Redis monitoring |

---

© 2026 AEGIS × Accor | Powered by n8n + Redis Stack
