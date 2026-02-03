# AEGIS v2.1 - Complete Setup Guide

**Platform:** Autonomous IT Operations & Swarming Platform  
**Stack:** LangGraph + FastAPI + React  
**Last Updated:** February 3, 2026

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements](#2-system-requirements)
3. [Step-by-Step Installation](#3-step-by-step-installation)
4. [Configuration Guide](#4-configuration-guide)
5. [Starting the Services](#5-starting-the-services)
6. [Verification & Health Checks](#6-verification--health-checks)
7. [Admin Portal Setup](#7-admin-portal-setup)
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

### Step 3.1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/maniltns/AEGIS.git
cd aegis-ops

# Verify structure
ls -la
```

### Step 3.2: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

### Step 3.3: Install Dependencies (Local Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model for PII scrubbing
python -m spacy download en_core_web_lg
```

---

## 4. Configuration Guide

### Step 4.1: Configure LLM API Keys

Open `.env` and set your API keys:

```bash
# =============================================================================
# LLM CONFIGURATION
# =============================================================================
LLM_PROVIDER=anthropic

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI API Key (fallback)
OPENAI_API_KEY=sk-proj-...
```

### Step 4.2: Configure ServiceNow

```bash
# =============================================================================
# SERVICENOW CONFIGURATION
# =============================================================================
SERVICENOW_INSTANCE=yourinstance.service-now.com
SERVICENOW_USER=aegis_integration
SERVICENOW_PASSWORD=your_password
```

### Step 4.3: Configure MS Teams

```bash
# =============================================================================
# MS TEAMS CONFIGURATION
# =============================================================================
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### Step 4.4: Configure AWS (for auto-remediation)

```bash
# =============================================================================
# AWS CONFIGURATION
# =============================================================================
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=eu-west-1
```

### Step 4.5: Configure Redis

```bash
# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=  # Leave empty for local dev
```

---

## 5. Starting the Services

### Option A: Docker Compose (Recommended)

```bash
cd docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check running containers
docker-compose ps
```

### Option B: Local Development

```bash
# Terminal 1: Start Redis
docker run -d -p 6379:6379 --name aegis-redis redis:7

# Terminal 2: Start API server
python api.py

# Terminal 3: Start Triage Worker
python workers/triage_worker.py

# Terminal 4: Start Admin Portal (optional)
cd admin-portal
npm install
npm run dev
```

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| AEGIS API | 8000 | http://localhost:8000 |
| Admin Portal | 3000 | http://localhost:3000 |
| RAG Service | 8100 | http://localhost:8100 |
| RedisInsight | 8001 | http://localhost:8001 |
| Redis | 6379 | redis://localhost:6379 |

---

## 6. Verification & Health Checks

### Step 6.1: Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "services": {
    "redis": "connected",
    "langgraph": "ready",
    "rag": "available"
  }
}
```

### Step 6.2: Check Queue Status

```bash
curl http://localhost:8000/status
```

Expected response:
```json
{
  "mode": "assist",
  "kill_switch_active": false,
  "queue": {
    "pending": 0,
    "processing": 0,
    "dead_letter": 0
  }
}
```

### Step 6.3: Test Incident Processing

```bash
curl -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  -d '{
    "number": "INC0000001",
    "short_description": "Test incident for setup verification",
    "description": "This is a test to verify AEGIS is working",
    "category": "Software",
    "caller_email": "test@example.com"
  }'
```

---

## 7. Admin Portal Setup

### Access the Portal

1. Navigate to http://localhost:3000
2. Login with default credentials:
   - **Username:** admin
   - **Password:** aegis2026

### Key Features

| Page | Function |
|------|----------|
| **Dashboard** | System health, queue stats, recent activity |
| **Agents** | View/manage LangGraph nodes |
| **Connectors** | Configure ITSM integrations |
| **Logs** | Real-time activity log with filtering |
| **Settings** | Kill switch, mode, thresholds |

---

## 8. ServiceNow Integration

### Step 8.1: Create Integration User

1. Login to ServiceNow as admin
2. Navigate to **User Administration > Users**
3. Create user: `aegis_integration`
4. Assign roles:
   - `itil`
   - `incident_manager`
   - `knowledge_user`

### Step 8.2: Configure Business Rule

Create a new Business Rule to send incidents to AEGIS:

```javascript
// Name: AEGIS Webhook Trigger
// Table: incident
// When: async after insert

(function executeRule(current, previous) {
    var request = new sn_ws.RESTMessageV2();
    request.setEndpoint('https://your-aegis-server:8000/webhook/incident');
    request.setHttpMethod('POST');
    request.setRequestHeader('Content-Type', 'application/json');
    
    var payload = {
        number: current.getValue('number'),
        short_description: current.getValue('short_description'),
        description: current.getValue('description'),
        category: current.getValue('category'),
        priority: current.getValue('priority'),
        caller_id: current.caller_id.email + '',
        sys_id: current.getValue('sys_id')
    };
    
    request.setRequestBody(JSON.stringify(payload));
    request.execute();
})(current, previous);
```

---

## 9. Teams Integration

### Step 9.1: Create Incoming Webhook

1. Open Microsoft Teams
2. Navigate to your target channel
3. Click **...** > **Connectors**
4. Search for **Incoming Webhook**
5. Configure and copy the webhook URL

### Step 9.2: Test Webhook

```bash
curl -X POST "$TEAMS_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "@type": "MessageCard",
    "themeColor": "0078D7",
    "summary": "AEGIS Test",
    "sections": [{
      "activityTitle": "🛡️ AEGIS: Connection Test",
      "text": "Teams integration is working!"
    }]
  }'
```

---

## 10. Production Deployment

### Step 10.1: AWS EC2 Setup

```bash
# Launch EC2 instance (Amazon Linux 2023)
# Instance type: t3.xlarge

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and configure
git clone https://github.com/maniltns/AEGIS.git
cd aegis-ops
cp .env.example .env
nano .env  # Configure production settings

# Start services
cd docker
docker-compose up -d
```

### Step 10.2: Configure ALB + SSL

1. Create Application Load Balancer
2. Configure HTTPS listener (port 443)
3. Add SSL certificate (ACM)
4. Target group: EC2 instance port 8000

### Step 10.3: Security Hardening

```bash
# Set Redis password in production
REDIS_PASSWORD=strong_password_here

# Configure AWS WAF rules
# Enable CloudWatch logging
# Set up alerting
```

---

## 11. Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| API returns 503 | Check Redis connection |
| Triage not processing | Verify worker is running |
| PII scrub fails | Ensure spaCy model is downloaded |
| Teams notifications fail | Check webhook URL validity |

### Log Locations

```bash
# API logs
docker-compose logs aegis-api

# Worker logs
docker-compose logs aegis-worker

# Redis logs
docker-compose logs redis
```

### Useful Commands

```bash
# Restart all services
docker-compose restart

# View queue depth
redis-cli LLEN aegis:queue:triage

# Clear dead letter queue
redis-cli DEL aegis:queue:dead_letter

# Check governance state
redis-cli GET gov:killswitch
redis-cli GET gov:mode
```

---

## Support

For issues or questions:
- **GitHub Issues:** https://github.com/maniltns/AEGIS/issues
- **Email:** aegis-support@accor.com

---

*AEGIS v2.1 - Built with 🛡️ by the AEGIS Team*
