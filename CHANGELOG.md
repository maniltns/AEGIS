# Changelog

All notable changes to AEGIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- JANITOR: AWS SSM integration for Windows/Linux
- JANITOR: Opera OHIP API integration
- SHERLOCK: Pinecone vector embeddings for KB

---

## [1.1.1] - 2026-01-28

### Added
- **🧠 Custom RAG Service** - Intelligent Knowledge Retrieval
  - `rag-service/main.py` - FastAPI with Titan V2 + Claude Sonnet 4.5
  - `rag-service/Dockerfile` - Docker container configuration
  - ChromaDB vector database for KB, tickets, SOPs
  - `workflows/rag-intelligent-triage.json` - n8n integration
  - `docs/rag-service.md` - API documentation
- **Technical Architecture Document (TAD)** - `docs/TAD.md`
  - System context and layered architecture
  - Component specifications
  - Security architecture with zones
  - Data architecture and retention
  - API and integration specs
- **Product Documentation** - `docs/product-documentation.md`
  - Feature catalog (5 categories)
  - User personas (4 roles)
  - Workflow guides
  - Configuration reference
  - Troubleshooting guide
- **Architecture Diagrams** - Comprehensive Mermaid diagrams
  - 6-Layer Architecture diagram
  - Technology Stack Architecture
  - Security Zones Deployment diagram  
  - Data Flow Architecture
  - Key Data Drivers mindmap
  - Decision Scorecard

### Changed
- `docker-compose.yml` - Added aegis-rag container
- Updated `implementation_plan.md` with Key Data Drivers and Decision Scorecard
- Standardized all diagrams to Mermaid format across docs
- Enhanced `README.md` with documentation links

---


## [1.1.0] - 2026-01-27



### Added
- **Kill Switch Enhancement** - Multi-level verification with Azure AD + PIN
  - `kill-switch-verified.json` workflow
  - Role-based access control (Team Lead/Manager/Security Admin)
  - Full audit logging of all activation attempts
  
- **Solution Comparison** - vs ServiceNow alternatives
  - Feature comparison matrix
  - 5-year TCO analysis (88% savings vs NowAssist)
  - Weighted decision scorecard
  
- **Security Framework**
  - Zero Trust security model documentation
  - Security control matrix
  - TLS 1.3, Redis password authentication
  
- **GDPR Compliance**
  - `pii-scrubber.json` workflow for PII anonymization
  - Article 5/17/30 compliance documentation
  - Data retention policies
  
- **Agile Documentation**
  - `CONTRIBUTING.md` - Development guidelines
  - `CHANGELOG.md` - Version history
  - `docs/user-stories.md` - Product backlog
  - `docs/sprint-backlog.md` - Sprint items

### Changed
- Docker Compose - Redis now requires password authentication
- Docker Compose - Ports bound to localhost only
- Implementation Plan - Added Sections 10 (Security) and 11 (GDPR)

### Security
- Redis authentication enabled by default
- Localhost-only port binding for Redis and RedisInsight
- PII scrubbing before AI processing

---

## [1.0.0] - 2026-01-26

### Added
- **Core Workflows**
  - `storm-shield.json` - GUARDIAN deduplication
  - `kill-switch.json` - ARBITER governance
  - `kb-search.json` - SCOUT KB lookup
  - `master-triage.json` - Full triage pipeline
  - `case-to-incident.json` - BRIDGE case conversion
  - `ritm-finance.json` - Hotel finance approval
  
- **JANITOR Agent**
  - `janitor-auto-remediation.json` - Auto-fix workflow
  - `janitor-approval-handler.json` - Human approval
  
- **Infrastructure**
  - Docker Compose for Redis Stack + n8n
  - Redis governance key initialization
  
- **Documentation**
  - `implementation_plan.md` - Full specification
  - `demo-script.md` - Workshop guide

### Defined
- Glass Box Principles (Transparency, Human-in-Loop, Auditability)
- Multi-Agent Architecture (9 agents)
- Redis schema for governance

---

## [0.1.0] - 2026-01-20

### Added
- Initial project structure
- POC planning documentation
- Basic n8n environment setup

---

## Version History

| Version | Date | Milestone |
|---------|------|-----------|
| 1.1.0 | Jan 27, 2026 | Security & GDPR Enhancement |
| 1.0.0 | Jan 26, 2026 | POC Complete |
| 0.1.0 | Jan 20, 2026 | Project Kickoff |
