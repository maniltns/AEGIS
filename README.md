# 🛡️ AEGIS - Autonomous Expert for Governance, Intelligence & Swarming

**Client:** Accor Hotels  
**Version:** 1.1 (Enterprise Swarm Edition)  
**Tagline:** *"Your AI Shield Against Incident Chaos"*

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd d:\AI-Ops\AISwarnOps

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials

# 3. Start Docker stack
cd docker
docker-compose up -d

# 4. Initialize Redis governance
docker exec aegis-redis sh /scripts/init-redis.sh

# 5. Access n8n
# Open http://localhost:5678
# Login: admin / aegis2026

# 6. Import workflows
# Import all JSON files from /workflows folder
```

---

## 📂 Project Structure

```
aegis/
├── docker/
│   ├── docker-compose.yml      # Redis Stack + n8n
│   └── init-redis.sh           # Governance key initialization
├── workflows/
│   ├── storm-shield.json       # 🛡️ GUARDIAN - Deduplication
│   ├── kill-switch.json        # ⚖️ ARBITER - Governance
│   ├── master-triage.json      # Full triage pipeline
│   ├── case-to-incident.json   # 🌉 BRIDGE - Case conversion
│   └── ritm-finance.json       # 💰 Hotel Finance approval
└── .env.example                # Environment template
```

---

## 🤖 Agent Roster

| Agent | Icon | Role |
|-------|------|------|
| GUARDIAN | 🛡️ | Storm Shield (Deduplication) |
| SCOUT | 🔍 | Context Enrichment |
| SHERLOCK | 🕵️ | RCA & Triage |
| ROUTER | 🚦 | Assignment |
| ARBITER | ⚖️ | Governance |
| HERALD | 📢 | Notifications |
| SCRIBE | 📝 | Audit Logging |
| BRIDGE | 🌉 | Case→Incident |
| JANITOR | 🧹 | Auto-Remediation |

---

## 🔧 Configuration

### Redis Keys (Governance)

```bash
# Kill Switch
SET gov:killswitch true   # System enabled
SET gov:killswitch false  # EMERGENCY STOP

# Mode
SET gov:mode observe   # Log only, no writes
SET gov:mode assist    # Write + human review
SET gov:mode execute   # Autonomous (future)
```

### Credential IDs

After importing workflows, update credential IDs:
- `REDIS_CREDENTIAL_ID` → your Redis credential
- `SNOW_CREDENTIAL_ID` → ServiceNow Accor Train  
- `OPENAI_CREDENTIAL_ID` → OpenAI API key

---

## 📊 Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| n8n | http://localhost:5678 | Workflow orchestration |
| RedisInsight | http://localhost:8001 | Redis monitoring |

---

## 🛡️ Glass Box Principles

1. **Transparency** - All AI reasoning is visible
2. **Human-in-the-Loop** - Critical actions require approval
3. **Auditability** - Complete decision trail
4. **Reversibility** - All actions can be rolled back
5. **Explainability** - AI explains WHY

---

© 2026 AEGIS × Accor | Powered by n8n + Redis Stack
