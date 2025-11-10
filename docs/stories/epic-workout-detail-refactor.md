# Epic: Workout Detail Page Visual Refactor

**Epic ID:** EPIC-001
**Created:** 2025-01-09
**Status:** Planning
**Priority:** High
**Target:** Phase 1 (Visual Polish) + Phase 4 (Animations)

---

## Epic Goal

Transform the workout tracking screen to match the professional visual design of the newly shipped workout template builder, while preserving 100% of tracking functionality.

**Success Metric:** Friends load it up and say "HOLY BUTTHOLE!" 🔥

---

## Scope

### ✅ In Scope
- Visual component polish (colors, typography, spacing)
- YouTube thumbnail extraction for real exercise previews
- Sticky timer bar for always-visible progress tracking
- Smooth animations for set completion and progress
- Professional card-based design matching template-create

### ❌ Out of Scope
- Architectural refactors (state management, component extraction beyond visual)
- Performance optimization (memoization, code splitting)
- Code reduction (787 → <600 lines is Phase 2)
- GraphQL query changes
- Business logic modifications

---

## User Stories

### Phase 1A: Foundation & Utilities
1. **STORY-001**: YouTube Thumbnail Extraction Utility
2. **STORY-002**: Design System Tokens Setup

### Phase 1B: Core Components
3. **STORY-003**: WorkoutTimerBar Component (Sticky Header)
4. **STORY-004**: TrackingMovementCard Component
5. **STORY-005**: SectionHeader Component
6. **STORY-006**: MetadataCard Component

### Phase 1C: Integration
7. **STORY-007**: Integrate WorkoutTimerBar into Workout Detail Screen
8. **STORY-008**: Replace Movement Display with TrackingMovementCard
9. **STORY-009**: Add Section Headers to Workout Phases
10. **STORY-010**: Add MetadataCard to Screen Header

### Phase 4: Animations & Polish
11. **STORY-011**: Checkmark Bounce Animation (Set Completion)
12. **STORY-012**: Progress Bar Smooth Fill Animation
13. **STORY-013**: Timer Pulse Animation (When Running)
14. **STORY-014**: Workout Completion Celebration Toast

---

## Technical Context

### Target File
- `app/(app)/workout/[id].tsx` (787 lines)

### New Files to Create
- `utils/youtube.ts`
- `components/workout/WorkoutTimerBar.tsx`
- `components/workout/TrackingMovementCard.tsx`

### Reference Files (NO CHANGES)
- `components/workout/MovementCard.tsx` (styling patterns)
- `components/workout/SummaryStatsHeader.tsx` (icon-driven stats)
- `app/(app)/workout-template-create.tsx` (visual design reference)

---

## Design Principles

1. **Preserve ALL Tracking Functionality** - Timer, rest tracking, set completion MUST work identically
2. **Visual Consistency** - Match template-create's indigo accent color scheme
3. **Surface-Level Only** - No architectural changes, just visual improvements
4. **Mobile-First** - User is mid-workout, sweaty, focused - make it EFFORTLESS
5. **Delight in Details** - Smooth animations, satisfying micro-interactions

---

## Success Criteria

### Quantitative
- ✅ Visual consistency: 100% match with template-create color scheme
- ✅ Functional parity: All tracking features work identically
- ✅ Performance: Animations run at 60fps on device
- ✅ YouTube thumbnails: Load within 2s on 3G connection

### Qualitative
- ✅ **"HOLY BUTTHOLE!" reaction** from friends
- ✅ Professional fitness app aesthetic
- ✅ Satisfying micro-interactions (bounce, fill, pulse)
- ✅ Clear visual hierarchy (know what to do next)

---

## Testing Strategy

### Visual Regression
- Screenshot comparison: Before vs After
- Color scheme validation (indigo accents present)
- Typography consistency check

### Functional Testing
1. Start workout → Timer starts counting
2. Complete set → Rest modal appears, set grays out
3. Edit completed set → Fields remain editable
4. Pause timer → Timer stops, can resume
5. Complete all sets → Celebration appears, can complete workout
6. Complete workout → Navigate back, data saved

### Performance Testing
- Animations run smoothly on physical device (60fps target)
- No frame drops during set completion
- YouTube thumbnails load within 2s

---

## Dependencies

### External Dependencies
- React Native Animated API (built-in, no install needed)
- YouTube image API (no auth required, public endpoint)

### Internal Dependencies
- Existing timer logic (lines 142-170 in workout/[id].tsx)
- Existing rest modal (lines 254-354 in workout/[id].tsx)
- Existing completion flow (lines 356-365 in workout/[id].tsx)

---

## Migration Strategy

### Phase 1A: Create New Components (Isolated)
- Build WorkoutTimerBar, TrackingMovementCard, utility functions
- Test in isolation (no integration with main screen yet)

### Phase 1B: Integrate Components (Incremental)
- Add WorkoutTimerBar to top of workout detail screen
- Replace one movement with TrackingMovementCard, test
- Replace all movements after single movement works
- Add SectionHeader and MetadataCard components

### Phase 4: Add Animations (Polish)
- Checkmark bounce on set completion
- Progress bar smooth fill
- Timer pulse effect
- Workout completion celebration

### Safety Net
- Git branch: `feature/workout-detail-visual-refactor`
- Commit after each sub-phase
- Test full workout flow after each integration step
- Rollback plan: Revert to previous commit if issues

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Animations cause frame drops | Medium | Test on physical device early, optimize if needed |
| YouTube thumbnail API changes | Low | Fallback to generic play button (current behavior) |
| Visual design conflicts with dark mode | Medium | Test dark mode on both iOS/Android |
| Integration breaks existing tracking | High | Commit after each story, test full workout flow |

---

## Story Point Estimate

| Phase | Stories | Estimated Points | Complexity |
|-------|---------|------------------|------------|
| Phase 1A | 2 | 3 pts | Low (utilities) |
| Phase 1B | 4 | 8 pts | Medium (new components) |
| Phase 1C | 4 | 13 pts | High (integration) |
| Phase 4 | 4 | 8 pts | Medium (animations) |
| **Total** | **14 stories** | **32 pts** | **~2-3 days** |

---

## Acceptance Criteria (Epic Level)

### Must Have (P0)
- [ ] All 14 user stories completed and tested
- [ ] Visual design matches template-create color scheme
- [ ] All existing tracking functionality works identically
- [ ] Animations run smoothly at 60fps on device
- [ ] YouTube thumbnails display for movements with video URLs

### Should Have (P1)
- [ ] Dark mode compatibility verified
- [ ] Cross-platform tested (iOS + Android)
- [ ] No performance regressions (no frame drops)
- [ ] UX spec documented in claudedocs/

### Could Have (P2)
- [ ] "HOLY BUTTHOLE!" reaction from ≥3 friends
- [ ] Component documentation in Storybook
- [ ] Animation parameter tuning based on user feedback

---

## Related Documentation

- **UX Spec:** `claudedocs/workout-detail-refactor-ux-spec.md`
- **Target File:** `app/(app)/workout/[id].tsx`
- **Design Reference:** `app/(app)/workout-template-create.tsx`
- **Component Patterns:** `components/workout/MovementCard.tsx`

---

**Next Steps:** Begin with STORY-001 (YouTube Thumbnail Utility) - foundation for all visual improvements.
