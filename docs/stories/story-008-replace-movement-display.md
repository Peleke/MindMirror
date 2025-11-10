# STORY-008: Replace Movement Display with TrackingMovementCard

**Story ID:** STORY-008
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1C - Integration
**Priority:** High (Core visual transformation)
**Points:** 5
**Status:** Ready
**Dependencies:** STORY-004 (TrackingMovementCard Component)

---

## User Story

**As a** user tracking my workout
**I want** professional movement cards with real thumbnails replacing the old display
**So that** I see a modern, visually consistent workout interface

---

## Acceptance Criteria

### Must Have
- [ ] Replace `MovementFrozen` component with `TrackingMovementCard`
- [ ] Map workout plan data to TrackingMovementCard props
- [ ] Connect set completion callbacks (`onSetComplete`, `onUpdateSet`)
- [ ] Preserve 100% of existing tracking functionality
- [ ] Display real YouTube thumbnails for movements with video URLs
- [ ] Maintain existing GraphQL mutations (no changes)
- [ ] All tracking logic works identically (timer, rest modal, completion)

### Should Have
- [ ] Incremental migration: Replace one movement card first, verify, then all
- [ ] Proper error handling for missing video URLs
- [ ] Loading states for YouTube thumbnails

### Could Have
- [ ] Skeleton loader while thumbnails load
- [ ] Video playback inline (instead of browser redirect)

---

## Technical Specification

### Current Implementation (Lines ~400-600)
```typescript
// OLD: MovementFrozen component
{movements.map((movement, index) => (
  <MovementFrozen
    key={index}
    name={movement.name}
    sets={movement.sets}
    // ... existing props
  />
))}
```

### New Implementation
```typescript
// NEW: TrackingMovementCard component
import { TrackingMovementCard } from '@/components/workout/TrackingMovementCard'

{movements.map((movement, index) => (
  <TrackingMovementCard
    key={movement.id}
    movementName={movement.name}
    description={movement.description}
    videoUrl={movement.videoUrl}
    sets={movement.sets.map((set, setIndex) => ({
      setNumber: setIndex + 1,
      value: trackingData[movement.id]?.[setIndex]?.value || set.targetValue,
      load: trackingData[movement.id]?.[setIndex]?.load || set.targetLoad,
      rest: trackingData[movement.id]?.[setIndex]?.rest || set.restSeconds,
      completed: trackingData[movement.id]?.[setIndex]?.completed || false,
    }))}
    metricUnit={movement.metricType}
    onSetComplete={(setIndex, completed) =>
      handleSetComplete(movement.id, setIndex, completed)
    }
    onUpdateSet={(setIndex, field, value) =>
      handleUpdateSet(movement.id, setIndex, field, value)
    }
  />
))}
```

### State Management Integration
```typescript
// Existing trackingData structure (NO CHANGES)
interface TrackingData {
  [movementId: string]: {
    [setIndex: number]: {
      value: string
      load: string
      rest: string
      completed: boolean
    }
  }
}

// Handler: Set completion (existing logic, wire to new component)
const handleSetComplete = useCallback((movementId: string, setIndex: number, completed: boolean) => {
  setTrackingData(prev => ({
    ...prev,
    [movementId]: {
      ...prev[movementId],
      [setIndex]: {
        ...prev[movementId]?.[setIndex],
        completed,
      },
    },
  }))

  // Trigger rest modal if completing (existing logic - lines 254-354)
  if (completed) {
    showRestModal(movementId, setIndex)
  }
}, [showRestModal])

// Handler: Set field update (existing logic, wire to new component)
const handleUpdateSet = useCallback(
  (movementId: string, setIndex: number, field: 'value' | 'load' | 'rest', value: string) => {
    setTrackingData(prev => ({
      ...prev,
      [movementId]: {
        ...prev[movementId],
        [setIndex]: {
          ...prev[movementId]?.[setIndex],
          [field]: value,
        },
      },
    }))
  },
  []
)
```

### Migration Strategy (Incremental)
```typescript
// STEP 1: Replace first movement only (validation)
{movements[0] && (
  <TrackingMovementCard
    key={movements[0].id}
    {...mapMovementToCardProps(movements[0])}
  />
)}
{movements.slice(1).map(movement => (
  <MovementFrozen key={movement.id} {...movement} />
))}

// STEP 2: After validation, replace all movements
{movements.map(movement => (
  <TrackingMovementCard
    key={movement.id}
    {...mapMovementToCardProps(movement)}
  />
))}
```

---

## Test Cases

### Integration Tests (`app/(app)/workout/__tests__/[id].test.tsx`)

```typescript
describe('WorkoutDetailScreen - TrackingMovementCard Integration', () => {
  it('should render TrackingMovementCard for each movement', () => {
    const { getAllByTestId } = render(<WorkoutDetailScreen />)
    const cards = getAllByTestId('tracking-movement-card')
    expect(cards.length).toBe(3)  // Assuming 3 movements
  })

  it('should display YouTube thumbnail for movement with video URL', () => {
    const { getByRole } = render(<WorkoutDetailScreen />)
    const image = getByRole('image', { name: /thumbnail/i })
    expect(image.props.source.uri).toContain('img.youtube.com')
  })

  it('should handle set completion', () => {
    const { getAllByRole, getByText } = render(<WorkoutDetailScreen />)
    const checkboxes = getAllByRole('checkbox')

    // Initial: 2/3 complete
    expect(getByText('2/3 sets complete')).toBeTruthy()

    // Complete third set
    fireEvent.press(checkboxes[2])

    // Updated: 3/3 complete
    expect(getByText('3/3 sets complete')).toBeTruthy()
  })

  it('should trigger rest modal on set completion', () => {
    const { getAllByRole, getByText } = render(<WorkoutDetailScreen />)
    const checkboxes = getAllByRole('checkbox')

    // Complete a set
    fireEvent.press(checkboxes[0])

    // Rest modal should appear
    expect(getByText('Rest Timer')).toBeTruthy()
  })

  it('should update set field values', () => {
    const { getAllByRole } = render(<WorkoutDetailScreen />)
    const inputs = getAllByRole('textbox')

    // Update reps value
    fireEvent.changeText(inputs[0], '15')

    // Verify state updated
    expect(inputs[0].props.value).toBe('15')
  })

  it('should preserve existing GraphQL mutation calls', async () => {
    const mockMutation = jest.fn()
    const { getByText } = render(
      <WorkoutDetailScreen updateWorkoutMutation={mockMutation} />
    )

    // Complete workout
    fireEvent.press(getByText('Complete Workout'))

    // Verify mutation called with correct data (NO CHANGES from existing)
    expect(mockMutation).toHaveBeenCalledWith(expect.objectContaining({
      workoutId: expect.any(String),
      trackingData: expect.any(Object),
    }))
  })
})
```

---

## Files to Modify

### Modified Files
- `app/(app)/workout/[id].tsx` - Replace MovementFrozen with TrackingMovementCard

### Changes Required
1. **Import:** Replace `MovementFrozen` import with `TrackingMovementCard`
2. **Mapping:** Create helper function to map movement data to card props
3. **Handlers:** Wire up `onSetComplete` and `onUpdateSet` callbacks
4. **Render:** Replace movement rendering loop with TrackingMovementCard
5. **Cleanup:** Remove unused MovementFrozen component after validation

---

## Dependencies

### Internal
- STORY-004 (TrackingMovementCard Component)
- STORY-001 (YouTube thumbnail utility - used by TrackingMovementCard)
- Existing tracking state and logic (lines 100-400)

### External
- None

---

## Definition of Done

- [ ] MovementFrozen completely replaced with TrackingMovementCard
- [ ] All movements display with real YouTube thumbnails
- [ ] Set completion triggers rest modal (existing behavior preserved)
- [ ] Set field updates persist in state
- [ ] Completion counter shows correct progress per movement
- [ ] GraphQL mutations work identically (no changes)
- [ ] Existing timer logic unchanged
- [ ] Unit tests passing (6 test cases minimum)
- [ ] Integration tests passing (full workout flow)
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing (Critical Path)
1. Open workout detail screen
2. Verify all movements show TrackingMovementCard
3. Check YouTube thumbnails loaded
4. Complete a set → Verify rest modal appears
5. Edit set values → Verify updates persist
6. Complete all sets → Verify "Complete Workout" works
7. Complete workout → Verify navigation and data save

### Regression Testing
- [ ] Timer still works (start/pause/resume)
- [ ] Rest modal appears on set completion
- [ ] Workout completion flow unchanged
- [ ] GraphQL mutations save data correctly
- [ ] Navigation back to journal works

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaks existing tracking functionality | **CRITICAL** | Incremental migration (1 movement first), extensive testing |
| Performance degradation with many movements | Medium | Profile with React DevTools, optimize re-renders |
| YouTube thumbnails fail to load | Low | Fallback to placeholder image, graceful degradation |
| GraphQL mutation structure changes | **CRITICAL** | Preserve exact mutation shape, test data save |

---

## Estimated Effort

- **Implementation:** 3 hours
- **Testing:** 2 hours (critical path + regression)
- **Code Review:** 30 minutes
- **Total:** ~5.5 hours

---

## Related Stories

- **Depends On:** STORY-004 (TrackingMovementCard Component)
- **Related:** STORY-007 (Timer bar integration)
- **Enables:** STORY-011 (Checkmark bounce animation)

---

**CRITICAL NOTE:**
This is the highest-risk story in the Epic (changes core tracking UI). Follow incremental migration strategy:
1. Replace 1 movement → Test full workflow
2. Replace all movements → Re-test
3. Validate GraphQL mutations unchanged

---

**Next:** STORY-009 (Add Section Headers to Workout Phases)
