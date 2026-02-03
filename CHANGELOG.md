# Changelog

All notable changes to AEGIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Enhanced vector embeddings for KB articles
- AWS SSM integration for auto-remediation
- Approval workflow via Teams

---

## [2.1.0] - 2026-02-03

### Added - LangGraph Architecture
- **🔄 LangGraph Pipeline** - Replaced 7-agent CrewAI swarm with 4-node state machine
  - `agents/triage_graph.py` - Guardrails, Enrichment, LLM, Executor nodes
  - Single LLM call per ticket (vs 7 with CrewAI)
- **🔒 PII Scrubber** - Microsoft Presidio integration
  - `utils/pii_scrubber.py` - GDPR/CCPA compliant data protection
  - Scrubs PII before any LLM call
- **🛡️ Vector Dedup** - Semantic similarity for Storm Shield
  - `agents/tools/redis_tools.py` - 90% similarity threshold
  - 15-minute time window for intelligent dedup
- **📦 Redis Queue** - Reliable task processing
  - `workers/triage_worker.py` - BRPOPLPUSH pattern
  - Dead letter queue for failed items
- **🖥️ Admin Portal** - React + Vite management UI
  - `admin-portal/` - Full admin dashboard
  - Kill switch, mode control, thresholds

### Changed
- **Removed CrewAI** - All 7 agents replaced by LangGraph nodes
- **Removed LangFlow** - Visual pipelines replaced by code
- **API Server** - Webhooks push to Redis queue
- **Tools** - Converted from CrewAI BaseTool to async functions

### Performance
| Metric | v2.0 | v2.1 |
|--------|------|------|
| LLM Calls | 7/ticket | 1/ticket |
| Latency | 15-35s | 2-5s |
| Cost (15k/mo) | ~$5,000 | ~$700 |

---

## [2.0.0] - 2026-02-02

### Added - CrewAI + LangFlow Stack
- **🤖 CrewAI Agent Framework** - 7 agents with crew orchestration
- **🎨 LangFlow Visual Pipelines** - Master triage and Storm Shield flows
- **⚡ FastAPI Server** - Webhooks and governance APIs
- **📖 Setup Guide** - Comprehensive deployment guide

### Changed
- **License:** Fully open source (MIT)
- **Docker Compose:** Updated for CrewAI stack

---

## [1.2.0] - 2026-01-28

### Added - Enterprise Readiness
- **📊 Executive Pack** - CXO-ready documentation
- **🏛️ EA Pack** - Architecture Review Board documentation
- **3-Tier Documentation Structure** - Executive, EA, Technical packs

---

## [1.1.1] - 2026-01-28

### Added
- **🧠 Custom RAG Service** - Intelligent Knowledge Retrieval
  - ChromaDB vector database for KB, tickets, SOPs
- **Technical Architecture Document (TAD)**

---

## [1.1.0] - 2026-01-XX

### Added
- 7 specialized agents (GUARDIAN, SHERLOCK, ROUTER, etc.)
- Redis governance layer (Kill Switch, thresholds)

---

## [1.0.0] - 2026-01-XX

### Added
- Initial AEGIS platform
- ServiceNow integration
- Microsoft Teams notifications

---

*Document maintained by AEGIS Team*
