# EPIC-001: Release Management & Changelog Automation

**Phase:** 1 (Critical)
**Priority:** 🔴 Critical - Launch Blocker
**Estimated Duration:** 1 week
**Status:** Not Started

## Overview

Implement automated release management with changelog generation, semantic versioning, and GitHub Releases to enable professional release cadence and transparent communication with users.

## Business Value

- **User Transparency**: Users see what's new/fixed in each release
- **Developer Efficiency**: Automated changelog generation saves hours per release
- **Professional Image**: Shows we're a mature, well-run organization
- **Audit Trail**: Clear history of what changed and when
- **Marketing Asset**: Release notes can be shared with users/press

## Current State

- ❌ No `CHANGELOG.md`
- ❌ No GitHub Releases
- ❌ Manual PR descriptions only
- ✅ VERSION file exists (1.0.0)
- ✅ Git tags exist but not leveraged

## Target State

- ✅ Automated CHANGELOG.md generation from conventional commits
- ✅ GitHub Releases created automatically on main merge
- ✅ Semantic versioning automation (major/minor/patch)
- ✅ Release notes include grouped changes (features/bugs/breaking)
- ✅ Migration guides for breaking changes
- ✅ Customer-facing release notes

## Technical Approach

### 1. Conventional Commits
- Enforce commit message format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
- Breaking changes: `BREAKING CHANGE:` in commit body

### 2. Release Automation
- Use `release-please` GitHub Action
- Auto-bump version based on commit types
- Generate CHANGELOG from commits since last release
- Create GitHub Release with notes

### 3. Manual Release Process (Fallback)
- `gh release create` command template
- RELEASE_NOTES.md template
- Version bumping script

## Success Criteria

- [ ] CHANGELOG.md exists and is up-to-date
- [ ] GitHub Releases created for all versions
- [ ] Team commits follow conventional commits format
- [ ] Release notes auto-generated on main merge
- [ ] Breaking changes clearly documented
- [ ] Migration guides provided when needed

## Dependencies

- None (standalone epic)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Team doesn't follow commit conventions | Medium | Add commit-msg git hook, PR title linting |
| Breaking changes not detected | High | Manual review required for major version bumps |
| Release automation fails | Medium | Document manual release process as fallback |

## Stories

- STORY-001: Create initial CHANGELOG.md from git history
- STORY-002: Set up release-please GitHub Action
- STORY-003: Add conventional commits enforcement
- STORY-004: Create release notes templates
- STORY-005: Document release process

## Related Epics

- EPIC-006: Issue & PR Automation (PR templates mention changelog entries)
- EPIC-004: Monitoring & Observability (releases tracked in metrics)

## Acceptance Criteria

**Epic is complete when:**
1. Next production deployment auto-generates CHANGELOG entry
2. GitHub Release created automatically
3. Release notes are comprehensive and user-friendly
4. Team successfully performs 3 releases using new process
5. Documentation updated with release procedures
