# 🛡️ AEGIS - Autonomous IT Operations & Swarming Platform

[![Version](https://img.shields.io/badge/Version-2.0-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/Status-POC-yellow.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Stack](https://img.shields.io/badge/Stack-CrewAI%20%2B%20LangFlow-purple.svg)]()

**Client:** Accor Hotels  
**Project:** Intelligent Triage System v2.0  
**Tagline:** *"Your AI Shield Against Incident Chaos"*

---

## 📋 Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Agent Roster](#agent-roster)
- [API Reference](#api-reference)
- [Documentation](#documentation)
- [Changelog](#changelog)

---

## Overview

AEGIS transforms Accor's IT Service Management from reactive ticket queues into an intelligent, self-defending ecosystem. Supporting **5,500+ hotels across 110 countries**, AEGIS protects Accor's global service desk from alert storms, routes critical issues with contextual intelligence, and assembles expert swarms in seconds.

### Key Benefits

| Benefit | Metric | Description |
|---------|--------|-------------|
| 🚀 **Faster Triage** | <60 sec | vs 45 min manual |
| 🛡️ **Alert Suppression** | [TBD]% | Duplicate detection via Storm Shield |
| 🔒 **Glass Box AI** | 100% | Every decision auditable |
| 💰 **Cost Efficient** | Open Source | CrewAI + LangFlow (MIT Licensed) |

---

## Technology Stack

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Framework** | CrewAI | 9-agent autonomous swarm |
| **Visual Pipelines** | LangFlow | Workflow visualization & building |
| **API Server** | FastAPI | Webhooks, governance endpoints |
| **Vector Database** | ChromaDB | RAG knowledge store |
| **Cache/Governance** | Redis | Kill switch, Storm Shield |
| **LLM** | Claude/GPT-4o | AI reasoning |
| **Embeddings** | AWS Titan V2 | Vector embeddings |

### Key Features

- ✅ 9 CrewAI agents with full Python implementation
- ✅ LangFlow visual pipeline builder
- ✅ FastAPI webhook server
- ✅ Enhanced RAG with ChromaDB
- ✅ Complete governance API
- ✅ Fully open source (MIT License)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- AWS Account (for Bedrock)
- ServiceNow instance
- MS Teams Webhook

### Installation

```bash
# Clone repository
git clone https://github.com/accor/aegis-ops.git
cd aegis-ops

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start the stack
cd docker
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### Service URLs

| Service | Port | URL |
|---------|------|-----|
| AEGIS API | 8000 | http://localhost:8000 |
| LangFlow | 7860 | http://localhost:7860 |
| RAG Service | 8100 | http://localhost:8100 |
| RedisInsight | 8001 | http://localhost:8001 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AEGIS v2.0 Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 5: LLM Inference                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Claude    │  │   GPT-4o    │  │ AWS Titan   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Layer 4: AI Engine                                             │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  CrewAI (9 Agents)          │  RAG Service (FastAPI)  │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  Layer 3: Middleware (Redis, Azure AD, AWS SSM)                 │
│  Layer 2: Orchestration (LangFlow, FastAPI)                     │
│  Layer 1: Presentation (ServiceNow, MS Teams)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Roster

| Agent | Role | Purpose |
|-------|------|---------|
| 🛡️ **GUARDIAN** | Storm Shield | Duplicate detection, alert storm suppression |
| 🔍 **SCOUT** | Enrichment | Context gathering from CMDB, KB, history |
| 🕵️ **SHERLOCK** | AI Triage | Classification, root cause, confidence scoring |
| 🎯 **ROUTER** | Assignment | Skills matching, workload balancing |
| ⚖️ **ARBITER** | Governance | Kill switch, thresholds, approvals |
| 📢 **HERALD** | Notifications | Teams cards, swarm channel creation |
| 📝 **SCRIBE** | Audit | Decision logging, compliance |
| 🌉 **BRIDGE** | Case→Incident | Intelligent conversion |
| 🧹 **JANITOR** | Remediation | Safe auto-fix for known issues |

---

## API Reference

### Incident Processing

```bash
# Submit incident
POST /webhook/incident
{
  "number": "INC0012345",
  "short_description": "Cannot access Opera PMS",
  "category": "Software"
}
```

### Governance

```bash
# Kill switch (STOP all AI)
POST /governance/killswitch
{"action": "disable", "reason": "...", "operator": "admin@accor.com"}

# Resume AI
POST /governance/killswitch
{"action": "enable", "reason": "...", "operator": "admin@accor.com"}
```

---

## Documentation

### Executive Pack
- [Executive Brief](docs/executive-pack/executive-brief.md)
- [Operating Model](docs/executive-pack/operating-model.md)
- [ROI Dashboard](docs/executive-pack/roi-dashboard.md)
- [Path to Production](docs/executive-pack/path-to-production.md)

### EA Pack
- [EA Alignment](docs/ea-pack/ea-alignment.md)
- [Risk Register](docs/ea-pack/risk-register.md)
- [CrewAI vs UiPath](docs/ea-pack/crewai-vs-uipath-comparison.md)

### Technical Pack
- [Setup Guide](docs/setup-guide.md)
- [Architecture Diagrams](docs/architecture-diagrams.md)
- [RAG Service](docs/rag-service.md)

---

## Project Structure

```
aegis-ops/
├── agents/                 # CrewAI agent definitions
│   ├── crew.py            # 9 agents + crew orchestration
│   └── tools/             # Agent tools
│       ├── servicenow_tools.py
│       ├── redis_tools.py
│       ├── rag_tools.py
│       └── teams_tools.py
├── langflow/              # LangFlow pipeline configs
│   ├── master-triage-flow.json
│   └── storm-shield-flow.json
├── rag-service/           # RAG API service
├── docker/                # Docker configuration
│   ├── docker-compose.yml
│   └── Dockerfile.api
├── docs/                  # Documentation
└── api.py                 # FastAPI server
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

### v2.0.0 (February 2026)
- CrewAI + LangFlow orchestration stack
- 9 CrewAI agents with full Python implementation
- LangFlow visual pipeline builder
- Fully open source (MIT License)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built with 🛡️ by the AEGIS Team*
