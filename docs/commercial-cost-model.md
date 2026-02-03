# AEGIS v2.1 – Commercial Cost Model

**Document:** Comprehensive Cost Analysis  
**Version:** 2.1  
**Date:** February 3, 2026

---

## Executive Summary

| Category | Year 1 | 5-Year Total |
|----------|--------|--------------|
| **Development & Build** | $45,000 | $45,000 |
| **Infrastructure** | $6,000 | $30,000 |
| **LLM API Costs** | $8,400 | $42,000 |
| **Maintenance & Support** | $12,000 | $60,000 |
| **Training & Change Mgmt** | $5,000 | $5,000 |
| **TOTAL COST** | **$76,400** | **$182,000** |
| **vs NowAssist (50 agents)** | $96,000/yr | $555,000 |
| **NET SAVINGS** | **$19,600** | **$373,000** |

---

## 1. Development & Build Costs (One-Time)

### Initial Development

| Component | Effort | Rate | Cost |
|-----------|--------|------|------|
| LangGraph Pipeline Design | 40 hrs | $150/hr | $6,000 |
| PII Scrubber (Presidio) | 16 hrs | $150/hr | $2,400 |
| Redis Queue Worker | 24 hrs | $150/hr | $3,600 |
| API Server Refactoring | 20 hrs | $150/hr | $3,000 |
| RAG Service Integration | 32 hrs | $150/hr | $4,800 |
| ServiceNow Integration | 24 hrs | $150/hr | $3,600 |
| Teams Integration | 16 hrs | $150/hr | $2,400 |
| Admin Portal (React) | 40 hrs | $150/hr | $6,000 |
| Docker/DevOps Setup | 20 hrs | $150/hr | $3,000 |
| Testing & QA | 40 hrs | $150/hr | $6,000 |
| Documentation | 20 hrs | $100/hr | $2,000 |
| Project Management | 20 hrs | $100/hr | $2,000 |
| **Development Subtotal** | **312 hrs** | | **$44,800** |

### Build Contingency (10%)

| Item | Cost |
|------|------|
| Contingency | $4,500 |
| **Total Development** | **$49,300** |

---

## 2. Infrastructure Costs (Annual)

### AWS Hosting

| Resource | Spec | Monthly | Annual |
|----------|------|---------|--------|
| EC2 Instance | t3.xlarge (4 vCPU, 16GB) | $150 | $1,800 |
| EBS Storage | 200GB gp3 | $20 | $240 |
| ALB | Standard | $25 | $300 |
| Data Transfer | 50GB/month | $5 | $60 |
| **AWS Subtotal** | | **$200** | **$2,400** |

### AWS Managed Services

| Resource | Purpose | Monthly | Annual |
|----------|---------|---------|--------|
| Secrets Manager | 5 secrets | $2 | $24 |
| CloudWatch | Logs + Metrics | $15 | $180 |
| WAF | Security | $20 | $240 |
| **Services Subtotal** | | **$37** | **$444** |

### Self-Hosted Components

| Component | Included In | Additional Cost |
|-----------|-------------|-----------------|
| Redis | Docker | $0 |
| ChromaDB | Docker | $0 |
| RAG Service | Docker | $0 |
| Admin Portal | Docker | $0 |

### Infrastructure Total

| Item | Monthly | Annual | 5-Year |
|------|---------|--------|--------|
| AWS Compute + Storage | $200 | $2,400 | $12,000 |
| AWS Services | $37 | $444 | $2,220 |
| Docker/Container Overhead | $0 | $0 | $0 |
| **Infrastructure Total** | **$237** | **$2,844** | **$14,220** |

---

## 3. LLM API Costs

### Cost per Ticket (v2.1 LangGraph)

| Stage | Model | Input Tokens | Output Tokens | Cost |
|-------|-------|--------------|---------------|------|
| Triage LLM | Claude 3.5 Sonnet | ~2,000 | ~500 | $0.045 |
| Fallback (10%) | GPT-4o-mini | ~2,000 | ~500 | $0.003 |
| **Average/Ticket** | | | | **$0.042** |

### Monthly Volume Projections

| Phase | Tickets/Month | LLM Cost/Month | Annual |
|-------|---------------|----------------|--------|
| Pilot (Feb) | 500 | $21 | — |
| Ramp-up (Mar-Apr) | 5,000 | $210 | — |
| Production | 15,000 | $630 | $7,560 |

### LLM Cost Comparison (v2.0 vs v2.1)

| Metric | v2.0 (CrewAI) | v2.1 (LangGraph) | Savings |
|--------|---------------|------------------|---------|
| LLM Calls/Ticket | 7 | 1 | 86% |
| Cost/Ticket | $0.30 | $0.042 | 86% |
| Monthly (15k) | $4,500 | $630 | $3,870 |
| Annual | $54,000 | $7,560 | **$46,440** |

### Embedding Costs

| Service | Model | Cost/1K Tokens | Monthly Est. |
|---------|-------|----------------|--------------|
| AWS Bedrock | Titan V2 | $0.0001 | $50 |
| **Annual Embeddings** | | | **$600** |

### LLM Total

| Item | Monthly | Annual | 5-Year |
|------|---------|--------|--------|
| Triage LLM (Claude) | $630 | $7,560 | $37,800 |
| Embeddings (Titan) | $50 | $600 | $3,000 |
| **LLM Total** | **$680** | **$8,160** | **$40,800** |

---

## 4. Tooling & Licensing

### Open Source Stack (No License Fees)

| Component | License | Cost |
|-----------|---------|------|
| LangGraph | MIT | **$0** |
| FastAPI | MIT | **$0** |
| Presidio | MIT | **$0** |
| Redis | BSD-3 | **$0** |
| ChromaDB | Apache 2.0 | **$0** |
| spaCy | MIT | **$0** |
| React | MIT | **$0** |
| Docker | Apache 2.0 | **$0** |
| **Total Licensing** | | **$0** |

### Commercial Alternatives (Not Used)

| Tool | If Used | Annual Cost |
|------|---------|-------------|
| ServiceNow NowAssist | 50 agents | $96,000 |
| UiPath Agentic | Per process | $50,000+ |
| AWS Bedrock Agents | Per invocation | Variable |

---

## 5. Maintenance & Support (Annual)

### Internal Support

| Role | Hours/Month | Rate | Monthly | Annual |
|------|-------------|------|---------|--------|
| DevOps Engineer | 8 hrs | $100/hr | $800 | $9,600 |
| L3 Support | 4 hrs | $80/hr | $320 | $3,840 |
| **Internal Total** | | | **$1,120** | **$13,440** |

### Enhancements (Annual)

| Type | Est. Hours | Cost |
|------|------------|------|
| Bug Fixes | 40 hrs | $4,000 |
| Minor Enhancements | 60 hrs | $6,000 |
| Security Patches | 20 hrs | $2,000 |
| **Enhancements Total** | | **$12,000** |

### Maintenance Total

| Item | Annual | 5-Year |
|------|--------|--------|
| Internal Support | $13,440 | $67,200 |
| Enhancements | $12,000 | $60,000 |
| **Maintenance Total** | **$25,440** | **$127,200** |

---

## 6. Training & Change Management

### One-Time Training Costs

| Activity | Audience | Cost |
|----------|----------|------|
| Admin Training (8 hrs) | 5 Admins | $1,000 |
| L1 Agent Training (4 hrs) | 50 Agents | $2,500 |
| Documentation | All | $500 |
| Change Communication | All | $500 |
| **Training Total** | | **$4,500** |

---

## 7. 5-Year Total Cost of Ownership (TCO)

### AEGIS v2.1 TCO

| Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|----------|--------|--------|--------|--------|--------|-------|
| Development | $49,300 | $0 | $0 | $0 | $0 | $49,300 |
| Infrastructure | $2,844 | $2,844 | $2,844 | $2,844 | $2,844 | $14,220 |
| LLM API | $8,160 | $8,160 | $8,160 | $8,160 | $8,160 | $40,800 |
| Maintenance | $25,440 | $25,440 | $25,440 | $25,440 | $25,440 | $127,200 |
| Training | $4,500 | $0 | $0 | $0 | $0 | $4,500 |
| **Annual Total** | **$90,244** | **$36,444** | **$36,444** | **$36,444** | **$36,444** | **$236,020** |

### NowAssist Comparison

| Category | AEGIS v2.1 | NowAssist | Savings |
|----------|------------|-----------|---------|
| 5-Year Licensing | $0 | $480,000 | $480,000 |
| Infrastructure | $14,220 | $0 | -$14,220 |
| Implementation | $49,300 | $50,000 | $700 |
| LLM/API | $40,800 | $25,000 | -$15,800 |
| Support | $127,200 | $25,000 | -$102,200 |
| **5-Year Total** | **$236,020** | **$580,000** | **$343,980** |

### UiPath Agentic Comparison

> UiPath Agentic is an AI-powered process automation platform that can be used for ITSM automation.

#### UiPath Agentic Cost Estimate (Same Use Case)

| Category | AEGIS v2.1 | UiPath Agentic | Savings |
|----------|------------|----------------|---------|
| **Platform Licensing** | $0 | $120,000/yr | $120,000/yr |
| - Robot Licenses (5 unattended) | — | $50,000/yr | — |
| - Orchestrator | — | $30,000/yr | — |
| - AI Center | — | $25,000/yr | — |
| - Insights | — | $15,000/yr | — |
| **Implementation** | $49,300 | $80,000 | $30,700 |
| - Process Development | — | $50,000 | — |
| - Integration Setup | — | $20,000 | — |
| - Training | — | $10,000 | — |
| **Infrastructure** | $14,220 | $25,000 | $10,780 |
| - Orchestrator Hosting | — | $15,000 | — |
| - Robot VMs | — | $10,000 | — |
| **LLM/AI** | $40,800 | $60,000 | $19,200 |
| - AI Center calls | — | $40,000 | — |
| - External LLM | — | $20,000 | — |
| **Maintenance** | $127,200 | $60,000 | -$67,200 |

#### 5-Year TCO Comparison (All Solutions)

| Solution | Year 1 | Years 2-5 | 5-Year Total |
|----------|--------|-----------|--------------|
| **AEGIS v2.1** | $90,244 | $145,776 | **$236,020** |
| **NowAssist** | $146,000 | $434,000 | **$580,000** |
| **UiPath Agentic** | $285,000 | $540,000 | **$825,000** |

#### Key Differentiators

| Feature | AEGIS v2.1 | NowAssist | UiPath Agentic |
|---------|------------|-----------|----------------|
| **Licensing** | $0 (Open Source) | $96,000/yr | $120,000/yr |
| **LLM Calls/Ticket** | 1 | 2-3 | 3-5 |
| **PII Protection** | Presidio | ServiceNow | UiPath DLP |
| **Deployment** | Self-hosted | ServiceNow | Self-hosted |
| **Customization** | Full | Limited | Medium |
| **Vendor Lock-in** | None | High | Medium |
| **Time to Deploy** | 4-6 weeks | 8-12 weeks | 10-16 weeks |

---

## 8. ROI Summary

### Value Creation (Annual @ 15k tickets/month)

| Benefit | Calculation | Annual Value |
|---------|-------------|--------------|
| Agent Time Saved | 13.5 min × 180k tickets × $0.50/min | $1,215,000 |
| MTTR Reduction | 40% faster × $50/incident | $360,000 |
| Duplicate Blocking | 95% × 10% duplicates saved | $90,000 |
| Escalation Reduction | 20% fewer escalations | $72,000 |
| **Total Annual Value** | | **$1,737,000** |

### ROI Calculation

| Metric | Value |
|--------|-------|
| 5-Year Investment | $236,020 |
| 5-Year Value | $8,685,000 |
| **Net Benefit** | **$8,448,980** |
| **ROI** | **3,579%** |
| **Payback Period** | **~2 months** |

---

## 9. Cost Assumptions

| Assumption | Value | Notes |
|------------|-------|-------|
| Ticket Volume | 15,000/month | Accor production estimate |
| LLM Token Pricing | Claude: $3/$15 per M tokens | Current Anthropic pricing |
| Developer Rate | $150/hr | Contract rate |
| Support Rate | $100/hr | Internal rate |
| Agent Salary Cost | $45,000/year | L1 agent fully loaded |
| Working Hours/Year | 1,880 | Standard calculation |

---

*Document Owner: AEGIS Team*  
*Last Updated: February 3, 2026*
