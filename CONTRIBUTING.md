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
- Node.js 18+ (for local n8n development)
- Access to ServiceNow Dev instance
- Azure AD credentials (for Kill Switch testing)

### Local Setup

```bash
# Clone repository
git clone https://github.com/accor/aegis.git
cd aegis

# Setup environment
cp .env.example .env
cp docker/security-config.env.example docker/security-config.env

# Start services
cd docker && docker-compose up -d

# Verify
docker ps
# Should show: aegis-redis, aegis-n8n
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
| Feature | `feature/AEGIS-{id}-{description}` | `feature/AEGIS-42-kill-switch-2fa` |
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

### Workflow JSON Files

- Use descriptive node names with emoji prefixes (e.g., `📝 SCRIBE - Log Event`)
- Include workflow tags for categorization
- Add comments in Code nodes explaining complex logic
- Use environment variables for all secrets

### JavaScript (n8n Code Nodes)

```javascript
/**
 * Example code node structure
 * Always include JSDoc comments
 */

// 1. Extract inputs
const input = $json.field || 'default';

// 2. Process
const result = processLogic(input);

// 3. Return structured output
return {
  json: {
    success: true,
    result: result,
    timestamp: new Date().toISOString()
  }
};
```

### Documentation

- Use Markdown for all docs
- Include mermaid diagrams for flows
- Keep tables for structured data
- Follow existing doc structure

---

## Testing Requirements

### Workflow Testing

| Test Type | When | How |
|-----------|------|-----|
| Unit | Every change | Test individual nodes |
| Integration | Before merge | End-to-end workflow |
| Security | Any auth change | Verify role checks |

### Test Cases to Include

```markdown
| ID | Scenario | Expected | Status |
|----|----------|----------|--------|
| T01 | Happy path | Success | ☐ |
| T02 | Invalid input | Graceful error | ☐ |
| T03 | Auth failure | Access denied | ☐ |
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
feat(janitor): add Azure AD verification to Kill Switch

- Integrate with Microsoft Graph API
- Add PIN challenge workflow
- Log all authorization attempts

Closes AEGIS-42
```

---

## Questions?

Contact the AEGIS team or open an issue in the repository.
