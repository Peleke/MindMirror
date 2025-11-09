# STORY-001: Create Initial CHANGELOG.md from Git History

**Epic:** EPIC-001 (Release Management)
**Priority:** 🔴 Critical
**Estimate:** 2 hours
**Status:** Not Started

## User Story

As a developer, I want a CHANGELOG.md file that captures all historical releases, so that we have a baseline before implementing automated changelog generation.

## Acceptance Criteria

- [ ] CHANGELOG.md file created in project root
- [ ] All existing git tags documented (v0.1.0, v0.1.1, v1.0.0)
- [ ] Grouped by release with dates
- [ ] Changes categorized: Features, Fixes, Breaking Changes
- [ ] Follows Keep a Changelog format
- [ ] Committed to main branch

## Implementation Tasks

1. **Generate initial changelog**
   ```bash
   # Get all commits since v0.1.0
   git log --oneline --no-merges v0.1.0..HEAD > /tmp/commits.txt
   ```

2. **Categorize commits manually**
   - Features (feat:, new, add)
   - Fixes (fix:, bugfix, resolve)
   - Breaking changes (BREAKING:, breaking change)
   - Other (docs, refactor, chore)

3. **Create CHANGELOG.md**
   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Keep a Changelog](https://keepachangelog.com/)

   ## [1.0.0] - 2025-01-06

   ### Added
   - Landing page for mobile app
   - Coach role assignment functionality

   ### Fixed
   - 401 error on assignRoleToUser mutation
   - Duplicate email detection in signup

   ### Security
   - Added authentication to role assignment
   ```

4. **Add unreleased section**
   ```markdown
   ## [Unreleased]

   ### Added
   - Sign-out button improvements (in progress)
   ```

## Testing

- [ ] Verify all tags are documented
- [ ] Ensure chronological order
- [ ] Check markdown formatting
- [ ] Links to tags work on GitHub

## Dependencies

None

## Notes

- This is a one-time manual effort
- Future releases will be automated via release-please
- Focus on accuracy over completeness for older releases
