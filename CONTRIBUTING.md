# Contributing to AEGIS

Thank you for your interest in contributing to AEGIS! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize security and compliance
- Follow Glass Box principles (transparency, auditability)

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- spaCy en_core_web_lg model
- Access to ServiceNow Dev instance
- Azure AD credentials (for admin portal)

### Local Setup

```bash
# Clone repository
git clone https://github.com/accor/aegis.git
cd aegis

# Setup environment
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_lg

# Start services
cd docker && docker-compose up -d

# Verify
docker ps
# Should show: aegis-api, aegis-worker, redis, admin-portal
```

---

## Development Workflow

### Agile Process

We follow **Scrum** with 2-week sprints:

| Ceremony | Frequency | Duration |
|----------|-----------|----------|
| Sprint Planning | Bi-weekly (Monday) | 2 hours |
| Daily Standup | Daily | 15 min |
| Sprint Review | Bi-weekly (Friday) | 1 hour |
| Retrospective | Bi-weekly (Friday) | 1 hour |

### Branch Strategy

```
main
├── develop           # Integration branch
│   ├── feature/*     # New features
│   ├── bugfix/*      # Bug fixes
│   └── hotfix/*      # Emergency fixes
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/AEGIS-{id}-{description}` | `feature/AEGIS-42-vector-dedup` |
| Bug Fix | `bugfix/AEGIS-{id}-{description}` | `bugfix/AEGIS-99-redis-timeout` |
| Hotfix | `hotfix/AEGIS-{id}-{description}` | `hotfix/AEGIS-100-security-patch` |

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Security implications considered
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### PR Template

```markdown
## Description
Brief description of changes

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactor

## Related Issues
Closes AEGIS-{id}

## Testing Done
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security Checklist
- [ ] No secrets in code
- [ ] PII handling reviewed
- [ ] Authorization checked

## Screenshots (if UI changes)
```

### Review Requirements

| Change Type | Approvals | Reviewers |
|-------------|-----------|-----------|
| Feature | 2 | Tech Lead + Peer |
| Bug Fix | 1 | Peer |
| Security | 2 | Security + Tech Lead |
| Hotfix | 1 | Tech Lead |

---

## Coding Standards

### Python (LangGraph Pipeline)

```python
"""
Example LangGraph node structure.
Use type hints and docstrings.
"""
from typing import Dict, Any
from agents.triage_graph import TriageState

async def example_node(state: TriageState) -> TriageState:
    """
    Brief description of node function.
    
    Args:
        state: Current pipeline state
        
    Returns:
        Updated state with new data
    """
    # 1. Extract inputs
    incident = state.get("incident", {})
    
    # 2. Process
    result = await process_logic(incident)
    
    # 3. Return updated state
    return {
        **state,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Async Tool Functions

```python
async def example_tool(param: str) -> Optional[Dict[str, Any]]:
    """
    Tool functions should be async and return typed results.
    """
    try:
        result = await external_call(param)
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return None
```

### Documentation

- Use Markdown for all docs
- Include mermaid diagrams for flows
- Keep tables for structured data
- Follow existing doc structure

---

## Testing Requirements

### Test Types

| Test Type | When | How |
|-----------|------|-----|
| Unit | Every change | pytest for individual functions |
| Integration | Before merge | End-to-end pipeline test |
| Security | Any auth change | Verify role checks |

### Test Cases to Include

```markdown
| ID | Scenario | Expected | Status |
|----|----------|----------|--------|
| T01 | Happy path | Success | ☐ |
| T02 | Invalid input | Graceful error | ☐ |
| T03 | PII scrubbing | Data anonymized | ☐ |
| T04 | Duplicate detection | Blocked | ☐ |
```

### Security Testing

- [ ] Unauthorized access blocked
- [ ] PII not exposed in logs
- [ ] Kill Switch responds correctly
- [ ] Audit trail created

---

## Commit Messages

### Format

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Test additions |
| `security` | Security updates |

### Examples

```
feat(triage): add vector similarity to Storm Shield

- Replace hash-based dedup with RAG vector search
- Add 90% similarity threshold
- Include 15-minute time window

Closes AEGIS-42
```

---

## Questions?

Contact the AEGIS team or open an issue in the repository.
