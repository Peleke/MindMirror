# EPIC-006: Issue & PR Automation

**Phase:** 2 (Important - Post-Launch)
**Priority:** 🟡 Important
**Estimated Duration:** 3 days
**Status:** Not Started

## Overview

Automate repetitive issue and PR management tasks to reduce manual work and keep repository clean and organized.

## Business Value

- **Developer Time Savings**: Automated tasks free up hours per week
- **Repo Hygiene**: Stale issues don't clutter backlog
- **Faster Merges**: Auto-merge for safe changes (dependencies)
- **Consistency**: Automated processes never forget steps
- **Team Focus**: More time for features, less for process

## Current State

- ❌ Manual issue labeling
- ❌ Manual PR assignment
- ❌ Stale issues accumulate
- ❌ Manual dependency updates
- ❌ No auto-linking of PRs to issues
- ✅ Automated deployment issues (to be removed - Issue #104)

## Target State

- ✅ Auto-label issues and PRs
- ✅ Auto-assign reviewers via CODEOWNERS
- ✅ Auto-close stale issues/PRs
- ✅ Auto-merge dependabot PRs after tests
- ✅ Auto-link PRs to issues
- ✅ Auto-comment test results on PRs
- ✅ Auto-request re-review after changes

## Technical Approach

### 1. Auto-Labeling
```yaml
# .github/workflows/auto-label.yml
- Label by changed files:
  - mobile/** → label: mobile
  - backend/** → label: backend
  - .github/workflows/** → label: ci/cd
- Label by PR size:
  - < 10 lines → size: XS
  - 10-100 lines → size: S
  - 100-500 lines → size: M
  - 500-1000 lines → size: L
  - > 1000 lines → size: XL
```

### 2. Stale Issue Management
```yaml
# .github/workflows/stale.yml
- Mark stale after 60 days of inactivity
- Close after 7 days if still no activity
- Exempt labels: pinned, security, roadmap
- Friendly message asking for updates
```

### 3. Dependabot Auto-Merge
```yaml
# .github/workflows/dependabot-auto-merge.yml
- Auto-merge if:
  - Dependabot PR
  - All tests pass
  - Minor or patch version update
  - Security update (any version)
- Require manual approval for major updates
```

### 4. PR-Issue Linking
```yaml
# Auto-link PRs to issues via:
- "Fixes #123" in PR description
- PR title contains issue number
- Comment on issue when PR opens
- Update issue status when PR merges
```

### 5. Test Results Bot
```yaml
# Comment on PRs with:
- Test pass/fail status
- Code coverage change
- Performance benchmark comparison
- Security scan results
```

## Success Criteria

- [ ] 90%+ of PRs auto-labeled correctly
- [ ] Stale issues closed automatically
- [ ] Dependabot PRs auto-merged (safe ones)
- [ ] PRs auto-linked to issues
- [ ] Test results visible on PRs
- [ ] Zero manual labeling needed

## Dependencies

- EPIC-005: Issue & PR Templates (CODEOWNERS file)
- EPIC-003: Quality Gates (test results to comment)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-merge breaks production | High | Only auto-merge after all tests pass |
| Stale bot closes active issues | Medium | Exempt important labels, review exemptions |
| Labeling errors cause confusion | Low | Tune label rules based on feedback |
| Bot spam in PRs | Low | Consolidate bot comments |

## Stories

- STORY-032: Implement auto-labeling workflow
- STORY-033: Set up stale issue bot
- STORY-034: Configure dependabot auto-merge
- STORY-035: Add PR-issue auto-linking
- STORY-036: Create test results comment bot
- STORY-037: Remove automated deployment issues (Issue #104)

## Related Epics

- EPIC-005: Issue & PR Templates (enables automation)
- EPIC-003: Quality Gates (test results for auto-merge)

## Acceptance Criteria

**Epic is complete when:**
1. Auto-labeling works for 90% of PRs
2. First stale issue successfully closed
3. First dependabot PR auto-merged
4. Test results commented on all PRs
5. Automated deployment issues removed
6. Team satisfied with automation balance
