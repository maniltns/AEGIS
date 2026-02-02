# AEGIS v2.0 - Complete Setup Guide

**Platform:** Autonomous IT Operations & Swarming Platform  
**Stack:** CrewAI + LangFlow + FastAPI  
**Last Updated:** February 2, 2026

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements](#2-system-requirements)
3. [Step-by-Step Installation](#3-step-by-step-installation)
4. [Configuration Guide](#4-configuration-guide)
5. [Starting the Services](#5-starting-the-services)
6. [Verification & Health Checks](#6-verification--health-checks)
7. [LangFlow Setup](#7-langflow-setup)
8. [ServiceNow Integration](#8-servicenow-integration)
9. [Teams Integration](#9-teams-integration)
10. [Production Deployment](#10-production-deployment)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|-----------------|---------|
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | 2.20+ | Container orchestration |
| **Python** | 3.11+ | Development & testing |
| **Git** | 2.40+ | Version control |

### Required Accounts & Access

| Service | Required Credentials | How to Obtain |
|---------|----------------------|---------------|
| **Anthropic API** | API Key | https://console.anthropic.com |
| **OpenAI API** | API Key | https://platform.openai.com |
| **AWS Account** | Access Key + Secret | https://console.aws.amazon.com |
| **ServiceNow** | Instance + Integration User | Your IT Admin |
| **MS Teams** | Webhook URL | Teams App > Connectors |

---

## 2. System Requirements

### Development Environment

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4 cores | 8 cores |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 20 GB | 50 GB SSD |
| **Network** | Internet access | Low latency |

### Production Environment (AWS)

| Workload | Instance Type | vCPU | RAM | Storage |
|----------|---------------|------|-----|---------|
| **POC (< 5K tickets/month)** | t3.large | 2 | 8 GB | 50 GB |
| **Pilot (5-15K tickets)** | t3.xlarge | 4 | 16 GB | 100 GB |
| **Production (15-30K tickets)** | c5.2xlarge | 8 | 16 GB | 200 GB |

---

## 3. Step-by-Step Installation

### Step 3.1: Install Docker (Windows)

```powershell
# Option 1: Docker Desktop for Windows
# Download and install from: https://www.docker.com/products/docker-desktop

# Option 2: Verify installation
docker --version
docker compose version
```

### Step 3.2: Install Docker (Linux/EC2)

```bash
# Update system
sudo yum update -y   # Amazon Linux
# OR
sudo apt update -y   # Ubuntu

# Install Docker
sudo yum install -y docker   # Amazon Linux
# OR
sudo apt install -y docker.io   # Ubuntu

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Step 3.3: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/maniltns/AEGIS.git
cd aegis-ops

# Verify structure
ls -la
# Should see: agents/, docker/, docs/, langflow/, api.py, etc.
```

### Step 3.4: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Open for editing
nano .env      # Linux
# OR
notepad .env   # Windows
```

---

## 4. Configuration Guide

### Step 4.1: Configure LLM API Keys

Open `.env` and set your API keys:

```bash
# =============================================================================
# LLM CONFIGURATION
# =============================================================================
# Choose your primary provider: anthropic | openai
LLM_PROVIDER=anthropic

# Anthropic API Key (Required if using Claude)
# Get from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxx

# OpenAI API Key (Required if using GPT-4)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4.2: Configure AWS for Embeddings

```bash
# =============================================================================
# AWS CONFIGURATION (for Bedrock & Titan Embeddings)
# =============================================================================
# Get from: AWS Console > IAM > Users > Security Credentials

AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=us-east-1

# Embedding model (do not change unless you know what you're doing)
AWS_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
```

> **Note:** Ensure your IAM user has `bedrock:InvokeModel` permissions.

### Step 4.3: Configure ServiceNow

```bash
# =============================================================================
# SERVICENOW CONFIGURATION
# =============================================================================
# Your ServiceNow instance URL (without https://)
SERVICENOW_INSTANCE=accordev.service-now.com

# Integration user credentials
# Request from your ServiceNow admin
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

## 5. Starting the Services

### Step 5.1: Build and Start All Services

```bash
# Navigate to project root
cd aegis-ops

# Build and start all containers
docker compose -f docker/docker-compose.yml up -d --build

# Expected output:
# ✔ Container aegis-redis       Started
# ✔ Container aegis-chromadb    Started
# ✔ Container aegis-rag         Started
# ✔ Container aegis-api         Started
# ✔ Container aegis-langflow    Started
# ✔ Container aegis-redis-init  Started
```

### Step 5.2: Verify Containers are Running

```bash
# Check container status
docker compose -f docker/docker-compose.yml ps

# Expected output:
# NAME              STATUS     PORTS
# aegis-api         Up         0.0.0.0:8000->8000/tcp
# aegis-chromadb    Up         0.0.0.0:8200->8000/tcp
# aegis-langflow    Up         0.0.0.0:7860->7860/tcp
# aegis-rag         Up         0.0.0.0:8100->8100/tcp
# aegis-redis       Up         0.0.0.0:6379->6379/tcp, 0.0.0.0:8001->8001/tcp
```

### Step 5.3: View Logs

```bash
# View all logs
docker compose -f docker/docker-compose.yml logs -f

# View specific service logs
docker compose -f docker/docker-compose.yml logs -f aegis-api
docker compose -f docker/docker-compose.yml logs -f langflow

# Exit logs: Ctrl+C
```

---

## 6. Verification & Health Checks

### Step 6.1: Check AEGIS API Health

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "redis": "connected",
    "rag": "connected"
  }
}
```

### Step 6.2: Check Governance Status

```bash
# Get current governance status
curl http://localhost:8000/status

# Expected response:
{
  "killswitch": true,
  "mode": "assist",
  "thresholds": {
    "auto_assign": 85,
    "auto_categorize": 80,
    "auto_remediate": 95
  }
}
```

### Step 6.3: Verify Redis Governance Keys

```bash
# Connect to Redis container
docker exec -it aegis-redis redis-cli

# Check governance keys
GET gov:killswitch
# Expected: "true"

GET gov:mode
# Expected: "assist"

GET gov:threshold:auto_assign
# Expected: "85"

# Exit Redis CLI
exit
```

### Step 6.4: Access Web Interfaces

Open these URLs in your browser:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **AEGIS API Docs** | http://localhost:8000/docs | None |
| **LangFlow UI** | http://localhost:7860 | admin / [LANGFLOW_PASSWORD] |
| **RedisInsight** | http://localhost:8001 | None |
| **ChromaDB** | http://localhost:8200 | None |

---

## 7. LangFlow Setup

### Step 7.1: Access LangFlow

1. Open browser: http://localhost:7860
2. Login with:
   - Username: `admin`
   - Password: `[your LANGFLOW_PASSWORD from .env]`

### Step 7.2: Import Pre-built Flows

```bash
# Flows are located in:
# aegis-ops/langflow/master-triage-flow.json
# aegis-ops/langflow/storm-shield-flow.json
```

1. Click **"Import"** in LangFlow UI
2. Select `master-triage-flow.json`
3. Click **"Load"**
4. Repeat for `storm-shield-flow.json`

### Step 7.3: Configure Flow Variables

In each flow, update these environment variables:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `SERVICENOW_INSTANCE` | Your ServiceNow URL |
| `TEAMS_WEBHOOK_URL` | Your Teams webhook |

### Step 7.4: Deploy Flows

1. Click on each flow
2. Click **"Build"** to compile
3. Click **"Deploy"** to activate

---

## 8. ServiceNow Integration

### Step 8.1: Create Integration User

In ServiceNow Admin Console:

1. Navigate to **User Administration > Users**
2. Create new user:
   - Username: `aegis_integration`
   - Email: `aegis@accor.com`
   - Active: ✓

### Step 8.2: Assign Required Roles

| Role | Purpose |
|------|---------|
| `itil` | ITSM operations |
| `rest_api_explorer` | API testing |
| `import_admin` | Custom table access |
| `catalog_admin` | RITM access |

### Step 8.3: Create Audit Log Table

```javascript
// ServiceNow > System Definition > Tables
// Create table: u_ai_audit_log

Table Label: AI Audit Log
Table Name: u_ai_audit_log

Columns:
- u_incident_number (String)
- u_action (String): categorize, assign, remediate, etc.
- u_old_value (String)
- u_new_value (String)
- u_confidence (Decimal)
- u_agent (String): SHERLOCK, ROUTER, JANITOR, etc.
- u_reasoning (String, 4000 chars)
- u_timestamp (Date/Time)
```

### Step 8.4: Configure Business Rules (Optional)

Create ServiceNow Business Rule to trigger AEGIS on new incidents:

```javascript
// Business Rule: AEGIS Trigger
// Table: incident
// When: after insert
// Script:

(function executeRule(current, previous) {
    var request = new sn_ws.RESTMessageV2();
    request.setEndpoint('https://aegis.accor.com/webhook/incident');
    request.setHttpMethod('POST');
    request.setRequestHeader('Content-Type', 'application/json');
    
    var body = {
        number: current.number.toString(),
        short_description: current.short_description.toString(),
        description: current.description.toString(),
        caller_id: current.caller_id.email.toString(),
        category: current.category.toString(),
        cmdb_ci: current.cmdb_ci.name.toString()
    };
    
    request.setRequestBody(JSON.stringify(body));
    request.executeAsync();
})(current, previous);
```

---

## 9. Teams Integration

### Step 9.1: Create Incoming Webhook

1. Open **Microsoft Teams**
2. Navigate to the channel for AEGIS notifications
3. Click **...** > **Connectors**
4. Add **Incoming Webhook**
5. Name: `AEGIS Notifications`
6. Upload AEGIS icon (optional)
7. Click **Create**
8. Copy the webhook URL

### Step 9.2: Test Webhook

```bash
# Send test notification
curl -X POST "YOUR_TEAMS_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🛡️ AEGIS Test",
    "text": "AEGIS integration is working correctly!"
  }'

# Check Teams channel for the message
```

### Step 9.3: Configure Adaptive Cards (Optional)

For approval workflows, Teams Adaptive Cards are used. Example card:

```json
{
  "type": "AdaptiveCard",
  "body": [
    {"type": "TextBlock", "text": "🧹 JANITOR: Remediation Request", "weight": "bolder"},
    {"type": "FactSet", "facts": [
      {"title": "Incident", "value": "INC0012345"},
      {"title": "Action", "value": "Restart Print Spooler"},
      {"title": "Confidence", "value": "96%"}
    ]}
  ],
  "actions": [
    {"type": "Action.Submit", "title": "✅ Approve"},
    {"type": "Action.Submit", "title": "❌ Reject"}
  ]
}
```

---

## 10. Production Deployment

### Step 10.1: AWS EC2 Setup

```bash
# Launch EC2 instance
# AMI: Amazon Linux 2023
# Instance Type: t3.xlarge (4 vCPU, 16 GB RAM)
# Storage: 100 GB gp3
# Security Group: See below

# Connect to instance
ssh -i aegis-key.pem ec2-user@your-instance-ip

# Install Docker (see Step 3.2)
# Clone repository (see Step 3.3)
# Configure environment (see Step 4)

# Start services
cd aegis-ops
docker compose -f docker/docker-compose.yml up -d --build
```

### Step 10.2: Security Group Configuration

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| HTTPS | 443 | 0.0.0.0/0 | API (via ALB) |
| SSH | 22 | Your IP | Admin access |
| Custom | 8000 | ALB SG | AEGIS API |
| Custom | 7860 | VPN/Office | LangFlow UI |
| Custom | 8001 | VPN/Office | RedisInsight |

### Step 10.3: Application Load Balancer

```bash
# Create ALB with HTTPS listener
# Certificate: *.aegis.accor.com

# Target Group: aegis-api
# Health Check: GET /health
# Port: 8000

# Route: /webhook/* -> aegis-api:8000
```

### Step 10.4: Production Checklist

- [ ] Configure HTTPS via ALB
- [ ] Set up CloudWatch logging
- [ ] Configure automated backups (Redis, ChromaDB)
- [ ] Set up monitoring alerts
- [ ] Rotate API keys monthly
- [ ] Configure VPC endpoints for AWS services
- [ ] Enable Redis password authentication
- [ ] Document disaster recovery procedure

---

## 11. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Container won't start | Port conflict | `docker ps -a` and stop conflicting containers |
| API returns 503 | Kill switch active | `redis-cli SET gov:killswitch true` |
| LangFlow won't load | Memory exhausted | Increase Docker memory limit |
| No Teams notifications | Webhook expired | Regenerate webhook in Teams |
| Redis connection refused | Container not running | `docker restart aegis-redis` |
| ChromaDB errors | Volume permissions | `docker volume rm aegis-chroma-data` |

### Reset All Services

```bash
# Stop all containers
docker compose -f docker/docker-compose.yml down

# Remove volumes (WARNING: deletes data)
docker compose -f docker/docker-compose.yml down -v

# Rebuild and start fresh
docker compose -f docker/docker-compose.yml up -d --build
```

### Reset Governance State

```bash
# Via Redis CLI
docker exec aegis-redis redis-cli SET gov:killswitch true
docker exec aegis-redis redis-cli SET gov:mode assist

# Via API
curl -X POST http://localhost:8000/governance/killswitch \
  -H "Content-Type: application/json" \
  -d '{"action": "enable", "reason": "Reset", "operator": "admin"}'
```

### View Container Logs for Debugging

```bash
# Check specific container logs
docker logs aegis-api --tail 100
docker logs aegis-langflow --tail 100
docker logs aegis-redis --tail 100

# Follow logs in real-time
docker logs -f aegis-api
```

### Contact Support

If you encounter issues not covered here:

- **Teams Channel:** #aegis-support
- **Email:** aegis-team@accor.com
- **Documentation:** [docs/implementation_plan.md](./implementation_plan.md)

---

**Document Version:** 2.0.0  
**Created by:** AEGIS Team  
**Last Updated:** February 2, 2026
