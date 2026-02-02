# Changelog

All notable changes to AEGIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- JANITOR: AWS SSM integration for Windows/Linux
- JANITOR: Opera OHIP API integration
- SHERLOCK: Enhanced vector embeddings for KB

---

## [2.0.0] - 2026-02-02

### Added - CrewAI + LangFlow Stack
- **🤖 CrewAI Agent Framework** - Full Python implementation
  - `agents/crew.py` - 9 agents with crew orchestration
  - `agents/tools/` - ServiceNow, Redis, RAG, Teams tools
- **🎨 LangFlow Visual Pipelines**
  - `langflow/master-triage-flow.json` - Main incident triage
  - `langflow/storm-shield-flow.json` - Duplicate detection
- **⚡ FastAPI Server** - `api.py` with webhooks and governance APIs
- **📋 Technology Comparison** - `docs/ea-pack/crewai-vs-uipath-comparison.md`
- **📖 Setup Guide** - `docs/setup-guide.md` comprehensive deployment guide

### Changed
- **Orchestration Stack:** CrewAI + LangFlow (MIT licensed)
- **License:** Fully open source (MIT)
- **Docker Compose:** Updated for new stack (AEGIS API, LangFlow, ChromaDB)
- **Architecture Diagrams:** Updated for 9-agent CrewAI swarm
- **README:** Complete overhaul for v2.0

### Cost Impact
- **5-Year TCO:** [TBD based on AWS sizing]
- **License Cost:** $0 (fully open source)

---

## [1.2.0] - 2026-01-28

### Added - Enterprise Readiness
- **📊 Executive Pack** - CXO-ready documentation
  - `executive-pack/executive-brief.md` - Vision, Before/After, 90-day roadmap
  - `executive-pack/operating-model.md` - RACI, ownership, governance
  - `executive-pack/roi-dashboard.md` - Metrics, TCO, business value
  - `executive-pack/path-to-production.md` - Gate criteria, KPIs
- **🏛️ EA Pack** - Architecture Review Board documentation
  - `ea-pack/ea-alignment.md` - ITIL mapping, capability map, ADRs
  - `ea-pack/risk-register.md` - Comprehensive risk register
- **3-Tier Documentation Structure** - Executive, EA, Technical packs

### Changed
- Simplified naming: "AEGIS – Autonomous IT Operations Platform"
- Architecture presented as 3 planes: Control, Intelligence, Action
- README reorganized with 3-tier documentation links

---

## [1.1.1] - 2026-01-28

### Added
- **🧠 Custom RAG Service** - Intelligent Knowledge Retrieval
  - `rag-service/main.py` - FastAPI with Titan V2 + Claude
  - `rag-service/Dockerfile` - Docker container configuration
  - ChromaDB vector database for KB, tickets, SOPs
- **Technical Architecture Document (TAD)** - `docs/TAD.md`
  - System context and layered architecture
  - Security model and deployment specs

---

## [1.1.0] - 2026-01-XX

### Added
- **🛡️ GUARDIAN Agent** (Storm Shield) - Duplicate detection
- **🧠 SHERLOCK Agent** - AI-powered root cause analysis
- **🎯 ROUTER Agent** - Intelligent assignment
- **⚖️ ARBITER Agent** - Governance & Kill Switch
- **📢 HERALD Agent** - Teams notifications
- **📝 SCRIBE Agent** - Audit logging
- **🌉 BRIDGE Agent** - Case to incident conversion
- **🧹 JANITOR Agent** - Safe auto-remediation
- Redis governance layer (Kill Switch, thresholds)

### Changed
- Architecture split into 9 specialized agents
- Enhanced confidence scoring with configurable thresholds

---

## [1.0.0] - 2026-01-XX

### Added
- Initial AEGIS platform
- ServiceNow integration
- Microsoft Teams notifications
- Basic incident triage workflow
- Docker deployment

---

*Document maintained by AEGIS Team*
