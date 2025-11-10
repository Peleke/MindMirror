# EPIC-009: Workout Template Create Screen UX Redesign

**Epic Owner:** Frontend Team
**Priority:** High
**Status:** In Progress
**Target Release:** v1.1.0
**Spec Reference:** `docs/front-end-spec-workout-template-redesign.md`

---

## Executive Summary

Redesign the Workout Template Create screen to eliminate usability pain points by replacing horizontal scrolling tables with touch-friendly card-based inputs, matching industry standards from Hevy.

**Goals:**
- 50% reduction in template creation time
- 90%+ user satisfaction on new set editor
- Zero critical bugs in first week
- Improved accessibility with 44pt touch targets

---

## Business Value

**Problem:**
- Current horizontal scrolling table makes set entry tedious (5+ taps per set)
- Small touch targets (32pt) cause tap accuracy issues
- No quick entry patterns (copy sets, defaults)
- Lacks visual hierarchy for complex templates

**Impact:**
- Coaches take 3-5 minutes to create templates (target: <2 minutes)
- Mobile users struggle with cramped inputs
- Low adoption of workout template features

**Success Metrics:**
- Template creation time: 3-5 min → <2 min
- User satisfaction: Current 60% → 90%+
- Templates created per coach: +50%

---

## Scope

### In Scope (Phase 1 - Frontend Only)
✅ Card-based set editor (replace horizontal table)
✅ Increment/decrement buttons (±5 lb, ±1 rep)
✅ "Copy Last Set" functionality
✅ Auto-default new sets to previous values
✅ Real-time summary stats (duration, exercise count, sets)
✅ Improved empty states with clear CTAs
✅ Collapsible block sections (Warmup/Workout/Cooldown)
✅ 44pt minimum touch targets (iOS HIG compliance)
✅ Hevy-inspired visual styling

### Out of Scope (Phase 2 - Backend Required)
❌ Set type badges (Warmup, Failure, Drop)
❌ Rep range support (8-12 reps)
❌ Template duplication
❌ Template versioning/history
❌ Natural Language Parsing (AI-powered)
❌ Volume/tonnage calculations
❌ Muscle group visualization
❌ Smart defaults based on exercise type

---

## Technical Architecture

### Frontend Components (New)
- `EmptyStateCard.tsx` - Inspiring empty state
- `SummaryStatsHeader.tsx` - Real-time template stats
- `CollapsibleBlockSection.tsx` - Warmup/Workout/Cooldown sections
- `ExerciseCard.tsx` - Refactored exercise container
- `SetEditorCard.tsx` - Card-based set input
- `SetRow.tsx` - Individual set row with increments
- `IncrementButton.tsx` - ±1 quick adjustment

### State Management
- No new GraphQL schema changes required ✅
- Uses existing `SetDraft`, `MovementDraft`, `PrescriptionDraft` types
- Derived state calculations for summary stats (client-side)
- AsyncStorage for collapse state persistence

### Backend Dependencies
**NONE** - Phase 1 is fully frontend-only

---

## User Stories

### Epic Stories
1. **STORY-009.1:** Card-Based Set Editor
2. **STORY-009.2:** Increment Buttons & Quick Entry
3. **STORY-009.3:** Summary Stats & Empty States
4. **STORY-009.4:** Collapsible Blocks & Visual Polish
5. **STORY-009.5:** Testing & Accessibility

See individual story files in `docs/stories/` for detailed acceptance criteria.

---

## Implementation Timeline

```
Week 1 (Jan 20-26):
- STORY-009.1: Card-based set editor
- STORY-009.2: Increment buttons

Week 2 (Jan 27-Feb 2):
- STORY-009.3: Summary stats + empty states
- STORY-009.4: Collapsible blocks

Week 3 (Feb 3-9):
- STORY-009.5: Testing + QA
- Visual polish
- Bug fixes

Week 4 (Feb 10):
- Ship to production
```

---

## Dependencies

### Blockers
None

### Related Epics
- EPIC-002: Rollback Mechanism (for safe deployment)
- EPIC-004: Monitoring & Observability (track usage metrics)

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance degradation with many sets | Medium | Low | Test with 50+ set templates |
| Keyboard covering inputs on small devices | High | Medium | Use `KeyboardAvoidingView` (already implemented) |
| Collapse state bugs causing data loss | High | Low | Comprehensive state management tests |
| Dark mode contrast issues | Low | Low | WCAG AAA compliance testing |

---

## Success Criteria

### Quality Gates
- [ ] All touch targets ≥44pt
- [ ] Summary stats update in real-time
- [ ] Copy last set duplicates all values
- [ ] Cannot delete only set in exercise
- [ ] Collapsible state persists across restarts
- [ ] Dark mode colors pass WCAG AA
- [ ] Zero critical bugs in first week
- [ ] <5% increase in app crash rate

### User Acceptance
- [ ] 90%+ user satisfaction (post-release survey)
- [ ] 50% reduction in template creation time
- [ ] 40% increase in templates created per coach

---

## Phase 2 Roadmap

After Phase 1 ships and metrics are validated:

**Phase 2A (Quick Wins):**
- Set type badges
- Template duplication
- Rep range support

**Phase 2B (AI Integration - Priority #1):**
- Natural Language Parsing with Claude API
- Text-to-template generation
- Clipboard detection

See `docs/front-end-spec-workout-template-redesign.md` Section 4.5 for full AI parsing specification.

---

## References

- **Spec:** `docs/front-end-spec-workout-template-redesign.md`
- **Current Implementation:** `app/(app)/workout-template-create.tsx`
- **Design Reference:** Hevy screenshots in `docs/images/IMG_2935.PNG` - `IMG_2941.PNG`
- **Issue Tracker:** GitHub Issues with `epic:workout-template-redesign` label
