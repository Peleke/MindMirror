# EPIC-005: Issue & PR Templates

**Phase:** 2 (Important - Post-Launch)
**Priority:** 🟡 Important
**Estimated Duration:** 2 days
**Status:** Not Started

## Overview

Create standardized issue and PR templates to improve communication, streamline workflows, and ensure consistent quality in issue reports and pull requests.

## Business Value

- **Faster Bug Resolution**: Complete bug reports = faster fixes
- **Better Feature Planning**: Structured feature requests capture all requirements
- **Code Review Efficiency**: Consistent PR format = faster reviews
- **User Engagement**: Easy bug reporting increases user feedback
- **Developer Productivity**: Less back-and-forth asking for info

## Current State

- ❌ No issue templates
- ❌ No PR template
- ❌ Inconsistent issue quality
- ❌ Missing context in PRs
- ✅ Team writes good PR descriptions (manual)

## Target State

- ✅ Bug report template
- ✅ Feature request template
- ✅ Security vulnerability template
- ✅ PR template with checklist
- ✅ CODEOWNERS file for auto-assignment
- ✅ Auto-labeling based on templates

## Technical Approach

### 1. Issue Templates
```yaml
# .github/ISSUE_TEMPLATE/
- bug_report.yml: Structured bug reporting
- feature_request.yml: Feature proposals
- security_vulnerability.yml: Private security reports
- config.yml: Disable blank issues
```

### 2. PR Template
```markdown
# .github/pull_request_template.md
## Summary
[Brief description]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
[How was this tested?]

## Screenshots (if applicable)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG entry added
- [ ] No breaking changes (or documented)
```

### 3. CODEOWNERS
```
# Auto-assign reviewers by file path
*.md                    @username
/mobile/                @mobile-team
/backend/               @backend-team
/.github/workflows/     @devops-team
```

### 4. Automation
```yaml
# Auto-label PRs based on:
- Changed files (frontend/backend/infra)
- Size (small/medium/large)
- Template selection
```

## Success Criteria

- [ ] Bug reports include reproduction steps
- [ ] Feature requests include acceptance criteria
- [ ] PRs include type, testing, checklist
- [ ] Auto-assignment works for PR reviews
- [ ] Auto-labeling adds correct labels
- [ ] Team adoption > 90%

## Dependencies

- None (standalone epic)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Team ignores templates | Medium | Make templates helpful, not burdensome |
| Templates too rigid | Low | Allow flexibility, provide good defaults |
| External contributors confused | Low | Clear contributing guidelines |

## Stories

- STORY-026: Create bug report template
- STORY-027: Create feature request template
- STORY-028: Create PR template
- STORY-029: Add CODEOWNERS file
- STORY-030: Set up auto-labeling workflow
- STORY-031: Document template usage

## Related Epics

- EPIC-006: Issue & PR Automation (templates enable automation)
- EPIC-001: Release Management (PR template references changelog)

## Acceptance Criteria

**Epic is complete when:**
1. All template files created and committed
2. Bug reports auto-labeled `bug`
3. Feature requests auto-labeled `enhancement`
4. PRs auto-assigned to correct reviewers
5. Team uses templates for 90% of issues/PRs
6. Templates improved based on team feedback
