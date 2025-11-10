# STORY-002: Set up Release-Please GitHub Action

**Epic:** EPIC-001 (Release Management)
**Priority:** 🔴 Critical
**Estimate:** 4 hours
**Status:** Not Started

## User Story

As a developer, I want automated release creation via Release-Please, so that GitHub Releases and CHANGELOG updates happen automatically when I merge to main.

## Acceptance Criteria

- [ ] `.github/workflows/release-please.yml` created
- [ ] Release-Please configured for correct version strategy
- [ ] Test release created successfully
- [ ] CHANGELOG auto-updated on merge
- [ ] GitHub Release created with notes
- [ ] Version file bumped automatically

## Implementation Tasks

1. **Create release-please workflow**
   ```yaml
   # .github/workflows/release-please.yml
   name: Release Please

   on:
     push:
       branches:
         - main

   jobs:
     release-please:
       runs-on: ubuntu-latest
       steps:
         - uses: googleapis/release-please-action@v4
           with:
             release-type: simple
             package-name: mindmirror
   ```

2. **Configure release-please**
   ```json
   // release-please-config.json
   {
     "packages": {
       ".": {
         "release-type": "simple",
         "bump-minor-pre-major": true,
         "bump-patch-for-minor-pre-major": true,
         "changelog-sections": [
           {"type": "feat", "section": "Features"},
           {"type": "fix", "section": "Bug Fixes"},
           {"type": "perf", "section": "Performance"},
           {"type": "docs", "section": "Documentation"}
         ]
       }
     }
   }
   ```

3. **Test in staging**
   - Make conventional commit to staging
   - Verify PR created by release-please
   - Merge PR, verify release created

## Testing

- [ ] Workflow triggers on main merge
- [ ] Release PR created correctly
- [ ] CHANGELOG updated accurately
- [ ] GitHub Release contains correct notes
- [ ] Version bumped appropriately

## Dependencies

- STORY-001 (initial CHANGELOG)
- STORY-003 (conventional commits)

## Notes

- Release-Please creates PRs, not releases directly
- Merging the release PR creates the GitHub Release
- Supports monorepo if needed later
