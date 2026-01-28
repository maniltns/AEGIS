# AEGIS – Operating Model

**Document:** Operating Model & Ownership  
**Version:** 1.0 | January 2026

---

## 1. Before / After Operating Model

### Current State (Without AEGIS)

```mermaid
flowchart TB
    subgraph CURRENT["❌ Current State - Manual Triage"]
        direction TB
        U1["👤 User"] --> SN1["📋 ServiceNow"]
        SN1 --> L1["👨‍💻 L1 Agent"]
        
        subgraph MANUAL["Manual Process (15+ min)"]
            L1 --> M1["📖 Read Ticket<br/>2 min"]
            M1 --> M2["🔍 Search KB<br/>5 min"]
            M2 --> M3["📝 Categorize<br/>3 min"]
            M3 --> M4["🎯 Assign<br/>2 min"]
            M4 --> M5["📋 Update Notes<br/>3 min"]
        end
        
        M5 --> L2["👨‍💼 L2 Agent"]
    end
    
    style CURRENT fill:#ffebee,stroke:#c62828
    style MANUAL fill:#ffcdd2,stroke:#e57373
```

### Future State (With AEGIS)

```mermaid
flowchart TB
    subgraph FUTURE["✅ Future State - AI-Assisted Triage"]
        direction TB
        U2["👤 User"] --> SN2["📋 ServiceNow"]
        SN2 --> AEGIS["🛡️ AEGIS Platform"]
        
        subgraph AUTO["Automated Process (< 1 min)"]
            AEGIS --> A1["🛡️ Storm Shield<br/>Dedupe"]
            A1 --> A2["🔍 RAG Search<br/>KB + History"]
            A2 --> A3["🧠 AI Classify<br/>90%+ Accuracy"]
            A3 --> A4["🎯 Auto-Assign"]
            A4 --> A5["📋 Work Notes<br/>+ Reasoning"]
        end
        
        A5 --> L1R["👨‍💻 L1 Review<br/>1 min"]
        L1R --> DONE["✅ Resolved"]
    end
    
    style FUTURE fill:#e8f5e9,stroke:#2e7d32
    style AUTO fill:#c8e6c9,stroke:#66bb6a
```

---

## 2. Ownership Roles (RACI)

```mermaid
graph TB
    subgraph ROLES["🏢 AEGIS Ownership Structure"]
        PO["👔 Product Owner<br/>Anilkumar MN<br/><i>Roadmap, Priorities</i>"]
        TL["💻 Technical Lead<br/>Engineering Team<br/><i>Architecture, Workflows</i>"]
        MS["🧠 Model Steward<br/>AI/ML Team<br/><i>Accuracy, Prompts</i>"]
        SA["🔒 Security Approver<br/>CISO Office<br/><i>PII, Kill Switch</i>"]
        OO["📊 Operations Owner<br/>IT Ops<br/><i>Monitoring, SLAs</i>"]
        CM["📋 Change Manager<br/>Change Mgmt<br/><i>CAB, Deployments</i>"]
    end
    
    PO --> TL
    PO --> MS
    TL --> OO
    SA --> OO
    CM --> OO
    
    style ROLES fill:#e3f2fd,stroke:#1976d2
    style PO fill:#1976d2,stroke:#0d47a1,color:#fff
    style SA fill:#d32f2f,stroke:#b71c1c,color:#fff
```

### Decision Authority Matrix

| Decision Type | Authority | Approval Required |
|--------------|-----------|-------------------|
| New automation rule | Model Steward | Product Owner |
| Production deployment | Technical Lead | Change Manager + CAB |
| Kill switch activation | Security Approver | Immediate (post-audit) |
| Model/prompt changes | Model Steward | Product Owner + Testing |
| New integration | Technical Lead | Security Approver |

---

## 3. Process Ownership

### 3.1 Automation Approval Process

```mermaid
flowchart LR
    subgraph PROCESS["📋 Automation Approval Flow"]
        REQ["📝 Request<br/>New Rule"] --> REV["🔍 Review<br/>Model Steward<br/><i>2 days</i>"]
        REV --> TEST["🧪 Test<br/>Staging<br/><i>3 days</i>"]
        TEST --> CAB["📊 CAB<br/>Approval"]
        CAB --> DEPLOY["🚀 Deploy<br/>Production"]
    end
    
    style PROCESS fill:#fff3e0,stroke:#ff9800
    style DEPLOY fill:#4caf50,stroke:#2e7d32,color:#fff
```

### 3.2 Model Accuracy Review Cycle

```mermaid
gantt
    title Model Review Cadence
    dateFormat  X
    axisFormat %s
    
    section Daily
    Error Logs & False Positives    :active, 1, 2
    
    section Weekly
    Accuracy Metrics Review         :3, 4
    
    section Monthly
    Full Audit & Prompt Tuning      :5, 6
    
    section Quarterly
    Model Drift Assessment          :7, 8
```

| Frequency | Activity | Owner |
|-----------|----------|-------|
| **Daily** | Check error logs, false positives | Operations |
| **Weekly** | Accuracy metrics review | Model Steward |
| **Monthly** | Full accuracy audit, prompt tuning | Model Steward + PO |
| **Quarterly** | Model drift assessment, retraining decision | AI/ML Team |

### 3.3 Production Change Sign-Off

| Change Type | Approvers | SLA |
|-------------|-----------|-----|
| **Standard** (config) | Technical Lead | 24 hours |
| **Normal** (new workflow) | Technical Lead + Ops Owner | 5 days |
| **Emergency** (hotfix) | Product Owner + Security | 4 hours |
| **Major** (new agent) | Full CAB | 10 days |

---

## 4. Escalation Matrix

```mermaid
flowchart TB
    subgraph ESC["⚠️ Escalation Paths"]
        P1["🔴 P1<br/>AEGIS Down"] --> OC1["On-Call"] --> TL1["Tech Lead"] --> PO1["Product Owner"]
        P2["🟠 P2<br/>Workflow Fail"] --> OC2["On-Call"] --> TL2["Tech Lead"]
        P3["🟡 P3<br/>Accuracy Drop"] --> MS1["Model Steward"] --> PO2["Product Owner"]
        P4["🟢 P4<br/>Enhancement"] --> Q["Normal Queue"]
    end
    
    style P1 fill:#f44336,stroke:#c62828,color:#fff
    style P2 fill:#ff9800,stroke:#ef6c00,color:#fff
    style P3 fill:#ffeb3b,stroke:#f9a825
    style P4 fill:#4caf50,stroke:#2e7d32,color:#fff
```

| Severity | Condition | Response Time |
|----------|-----------|---------------|
| **P1** | AEGIS down, all AI stopped | 15 min |
| **P2** | Single workflow failing | 1 hour |
| **P3** | Accuracy degradation | 4 hours |
| **P4** | Enhancement request | 5 days |

---

## 5. Support Model

```mermaid
graph TB
    subgraph SUPPORT["🛠️ Support Tiers"]
        direction LR
        L1S["🟢 L1 Support<br/>Operations Team"] --> L2S["🟡 L2 Support<br/>Technical Team"] --> L3S["🔴 L3 Support<br/>Engineering Team"]
    end
    
    subgraph L1D["L1 Responsibilities"]
        L1A["Monitor dashboards"]
        L1B["Restart workflows"]
        L1C["Kill switch"]
        L1D2["Escalate issues"]
    end
    
    subgraph L2D["L2 Responsibilities"]
        L2A["Debug n8n errors"]
        L2B["Fix integrations"]
        L2C["Tune prompts"]
    end
    
    subgraph L3D["L3 Responsibilities"]
        L3A["Architecture changes"]
        L3B["New agents"]
        L3C["Model retraining"]
    end
    
    L1S --> L1D
    L2S --> L2D
    L3S --> L3D
    
    style L1S fill:#4caf50,stroke:#2e7d32,color:#fff
    style L2S fill:#ff9800,stroke:#ef6c00,color:#fff
    style L3S fill:#f44336,stroke:#c62828,color:#fff
```

---

## 6. Governance Cadence

```mermaid
timeline
    title Governance Meeting Schedule
    section Daily
        Standup : Ops, Tech Lead
    section Weekly
        Accuracy Review : Model Steward, PO
    section Bi-weekly
        Stakeholder Sync : PO, Business
    section Monthly
        Governance Board : All Owners
```

---

## 7. Key Metrics Ownership

```mermaid
pie title Metrics by Owner
    "Ops Owner" : 40
    "Model Steward" : 25
    "Tech Lead" : 20
    "Security" : 15
```

| Metric | Owner | Target | Review |
|--------|-------|--------|--------|
| MTTT | Ops Owner | <60 sec | Daily |
| Triage Accuracy | Model Steward | >90% | Weekly |
| Storm Shield Block | Tech Lead | >95% | Weekly |
| System Availability | Ops Owner | 99.5% | Daily |
| Kill Switch Response | Security | <10 sec | Monthly |

---

*Document Owner: Anilkumar MN | Last Updated: January 28, 2026*
