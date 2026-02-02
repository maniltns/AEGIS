# AEGIS v2.0 - Setup Guide

**Platform:** Autonomous IT Operations & Swarming Platform  
**Stack:** CrewAI + LangFlow  
**Version:** 2.0.0 | February 2026

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- AWS Account (for Bedrock & Titan)
- ServiceNow Instance
- Microsoft Teams Webhook

### 1. Clone & Configure

```bash
# Clone the repository
git clone https://github.com/maniltns/AEGIS.git
cd aegis-ops

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Configure Environment

```bash
# Required: LLM API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Required: ServiceNow
SERVICENOW_INSTANCE=accordev.service-now.com
SERVICENOW_USER=aegis_integration
SERVICENOW_PASSWORD=xxx

# Required: Teams Webhook
TEAMS_WEBHOOK_URL=https://accor.webhook.office.com/xxx

# Required: AWS (for embeddings)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

### 3. Start the Stack

```bash
# Start all services
cd docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f aegis-api
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Check governance status
curl http://localhost:8000/status

# Access LangFlow UI
# Open browser: http://localhost:7860
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AEGIS v2.0 Stack                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  LangFlow   │  │  AEGIS API  │  │ RAG Service │             │
│  │  :7860      │  │  :8000      │  │  :8100      │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         │    ┌───────────┴───────────┐    │                     │
│         └────┤       CrewAI          ├────┘                     │
│              │   9 Agent Swarm       │                          │
│              └───────────┬───────────┘                          │
│                          │                                      │
│  ┌─────────────┐  ┌──────┴──────┐  ┌─────────────┐             │
│  │   Redis     │  │  ChromaDB   │  │   Docker    │             │
│  │   :6379     │  │   :8200     │  │   Network   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Endpoints

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **AEGIS API** | 8000 | http://localhost:8000 | Main API, webhooks |
| **LangFlow** | 7860 | http://localhost:7860 | Visual pipeline builder |
| **RAG Service** | 8100 | http://localhost:8100 | Vector search, AI analysis |
| **ChromaDB** | 8200 | http://localhost:8200 | Vector database |
| **Redis** | 6379 | localhost:6379 | Governance, caching |
| **RedisInsight** | 8001 | http://localhost:8001 | Redis monitoring |

---

## API Reference

### Incident Processing

```bash
# Submit incident for triage
POST /webhook/incident
{
  "number": "INC0012345",
  "short_description": "Cannot access Opera PMS",
  "description": "Front desk reports timeout errors",
  "caller_id": "john.smith@accor.com",
  "category": "Software",
  "cmdb_ci": "Opera Production"
}

# Response
{
  "status": "accepted",
  "incident_number": "INC0012345",
  "triage_id": "TRG20260202180500123",
  "message": "Incident queued for AI triage"
}
```

### Governance Controls

```bash
# Activate Kill Switch (STOP all AI)
POST /governance/killswitch
{
  "action": "disable",
  "reason": "Emergency stop for investigation",
  "operator": "admin@accor.com"
}

# Deactivate Kill Switch (RESUME AI)
POST /governance/killswitch
{
  "action": "enable",
  "reason": "Issue resolved",
  "operator": "admin@accor.com"
}

# Change Operating Mode
POST /governance/mode
{
  "mode": "assist",  # auto | assist | monitor
  "reason": "Entering production phase"
}
```

### Approval Workflow

```bash
# Approve pending action
POST /approve/INC0012345
{
  "action": "approve",
  "incident": "INC0012345",
  "approver": "manager@accor.com"
}

# Reject pending action
POST /reject/INC0012345
{
  "action": "reject",
  "incident": "INC0012345",
  "approver": "manager@accor.com",
  "reason": "Requires manual review"
}
```

---

## CrewAI Agents

| Agent | Role | Tools |
|-------|------|-------|
| **GUARDIAN** | Storm Shield | Redis duplicate check, storm detection |
| **SCOUT** | Enrichment | ServiceNow CMDB, user info, KB search |
| **SHERLOCK** | AI Triage | RAG analysis, classification |
| **ROUTER** | Assignment | Group workload, skills matching |
| **ARBITER** | Governance | Kill switch, thresholds, approvals |
| **HERALD** | Notifications | Teams cards, swarm channels |
| **SCRIBE** | Audit | Decision logging, compliance |
| **BRIDGE** | Case→Incident | Case analysis, conversion |
| **JANITOR** | Remediation | Standard changes, rollback |

---

## LangFlow Pipelines

Access LangFlow UI at `http://localhost:7860`

### Pre-built Flows

| Flow | Description |
|------|-------------|
| `master-triage-flow.json` | Main incident processing pipeline |
| `storm-shield-flow.json` | Duplicate detection & storm suppression |

### Import Flows

1. Open LangFlow UI
2. Click "Import"
3. Select flow from `langflow/` directory
4. Configure environment variables
5. Deploy

---

## Monitoring

### Check System Status

```bash
# Overall health
curl http://localhost:8000/health

# Governance status
curl http://localhost:8000/status

# Redis status
redis-cli -h localhost ping
```

### View Audit Logs

```bash
# Incident-specific audit
curl http://localhost:8000/audit/incident/INC0012345

# Kill switch history
curl http://localhost:8000/audit/killswitch
```

### Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f aegis-api
docker-compose logs -f langflow
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| API returns 503 | Kill switch active - check `/status` |
| CrewAI timeout | Increase LLM timeout in tools |
| Redis connection | Verify Redis container is running |
| LangFlow not loading | Check container logs, verify port 7860 |

### Reset Governance

```bash
# Via Redis CLI
redis-cli SET gov:killswitch true
redis-cli SET gov:mode assist

# Via API
curl -X POST http://localhost:8000/governance/killswitch \
  -H "Content-Type: application/json" \
  -d '{"action": "enable", "reason": "Reset", "operator": "admin"}'
```

---

## Production Deployment

### AWS EC2 Setup

```bash
# Recommended: t3.xlarge (4 vCPU, 16 GB RAM)
# For [TBD] tickets/month

# Install Docker
sudo yum install -y docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy
cd aegis-ops
docker-compose -f docker/docker-compose.yml up -d
```

### Security Checklist

- [ ] Configure AWS Security Groups
- [ ] Enable HTTPS via ALB/nginx
- [ ] Rotate API keys monthly
- [ ] Enable VPC for container network
- [ ] Configure CloudWatch logging
- [ ] Set up automated backups for Redis/ChromaDB

---

*Document Version: 2.0.0 | Last Updated: February 2, 2026*
