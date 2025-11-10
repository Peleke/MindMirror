# STORY-007: Integrate WorkoutTimerBar into Workout Detail Screen

**Story ID:** STORY-007
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1C - Integration
**Priority:** High
**Points:** 2
**Status:** Ready
**Dependencies:** STORY-003 (WorkoutTimerBar Component)

---

## User Story

**As a** user tracking my workout
**I want** the sticky timer bar integrated into my workout screen
**So that** I can always see elapsed time and progress

---

## Acceptance Criteria

### Must Have
- [ ] Import WorkoutTimerBar component into `workout/[id].tsx`
- [ ] Position at top of ScrollView (sticky behavior)
- [ ] Wire up props: `elapsedSeconds`, `isRunning`, `completedSets`, `totalSets`, `currentMovementName`, `onToggleTimer`
- [ ] Calculate `completedSets` from trackingData state
- [ ] Calculate `totalSets` from workout plan
- [ ] Determine `currentMovementName` (first incomplete movement)
- [ ] Connect `onToggleTimer` to existing timer logic (lines 142-170)
- [ ] Timer bar updates in real-time as sets complete

### Should Have
- [ ] Timer bar z-index above ScrollView content
- [ ] Smooth scroll-to-top when timer bar tapped
- [ ] Progress bar animates when sets complete

### Could Have
- [ ] Haptic feedback when timer toggled
- [ ] Timer bar fades in on workout start

---

## Technical Specification

### Integration Location
```typescript
// In app/(app)/workout/[id].tsx
import { WorkoutTimerBar } from '@/components/workout/WorkoutTimerBar'

export default function WorkoutDetailScreen() {
  // ... existing state ...

  // Calculate stats for timer bar
  const completedSets = trackingData.filter(t => t.completed).length
  const totalSets = workoutPlan.movements.reduce(
    (sum, m) => sum + m.sets.length,
    0
  )
  const currentMovement = workoutPlan.movements
    .flatMap(m => m.sets.map(() => m.name))
    .find((_, i) => !trackingData[i]?.completed) || 'All complete'

  return (
    <View style={styles.container}>
      {/* Sticky Timer Bar */}
      <WorkoutTimerBar
        elapsedSeconds={elapsedSeconds}
        isRunning={isRunning}
        completedSets={completedSets}
        totalSets={totalSets}
        currentMovementName={currentMovement}
        onToggleTimer={handleToggleTimer}
      />

      {/* Scrollable Content */}
      <ScrollView>
        {/* ... existing content ... */}
      </ScrollView>
    </View>
  )
}
```

### State Calculations
```typescript
// Calculate completed sets
const completedSets = useMemo(() => {
  return trackingData.filter(t => t.completed).length
}, [trackingData])

// Calculate total sets
const totalSets = useMemo(() => {
  return workoutPlan.movements.reduce(
    (sum, movement) => sum + movement.sets.length,
    0
  )
}, [workoutPlan])

// Find current movement name
const currentMovementName = useMemo(() => {
  const allSets = workoutPlan.movements.flatMap(movement =>
    movement.sets.map(() => movement.name)
  )
  const firstIncompleteIndex = trackingData.findIndex(t => !t.completed)
  return firstIncompleteIndex >= 0
    ? allSets[firstIncompleteIndex]
    : 'All complete'
}, [trackingData, workoutPlan])
```

### Timer Logic Connection
```typescript
// Existing timer logic (lines 142-170) - NO CHANGES
const handleToggleTimer = useCallback(() => {
  if (isRunning) {
    // Pause timer
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  } else {
    // Start timer
    timerRef.current = setInterval(() => {
      setElapsedSeconds(prev => prev + 1)
    }, 1000)
  }
  setIsRunning(!isRunning)
}, [isRunning])
```

---

## Test Cases

### Integration Tests (`app/(app)/workout/__tests__/[id].test.tsx`)

```typescript
describe('WorkoutDetailScreen - Timer Bar Integration', () => {
  it('should display timer bar at top of screen', () => {
    const { getByTestId } = render(<WorkoutDetailScreen />)
    const timerBar = getByTestId('workout-timer-bar')
    expect(timerBar).toBeTruthy()
  })

  it('should calculate completed sets correctly', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    // Assuming 2 sets completed out of 12
    expect(getByText('2/12')).toBeTruthy()
  })

  it('should show first incomplete movement as current', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    // Assuming first 2 movements complete, 3rd is "Barbell Squat"
    expect(getByText('Barbell Squat')).toBeTruthy()
  })

  it('should toggle timer when play/pause pressed', () => {
    const { getByRole, getByText } = render(<WorkoutDetailScreen />)
    const timerText = getByText('00:00')

    // Press play
    fireEvent.press(getByRole('button', { name: /play/ }))

    // Wait 2 seconds
    act(() => {
      jest.advanceTimersByTime(2000)
    })

    // Verify timer updated
    expect(getByText('00:02')).toBeTruthy()
  })

  it('should update progress when set completed', () => {
    const { getByText, getAllByRole } = render(<WorkoutDetailScreen />)

    // Initial: 2/12
    expect(getByText('2/12')).toBeTruthy()

    // Complete another set
    fireEvent.press(getAllByRole('checkbox')[2])

    // Updated: 3/12
    expect(getByText('3/12')).toBeTruthy()
  })
})
```

---

## Files to Modify

### Modified Files
- `app/(app)/workout/[id].tsx` - Add WorkoutTimerBar import and integration

### Changes Required
1. **Import:** Add `import { WorkoutTimerBar } from '@/components/workout/WorkoutTimerBar'`
2. **Calculations:** Add `useMemo` hooks for completedSets, totalSets, currentMovementName
3. **Render:** Add WorkoutTimerBar above ScrollView
4. **Styling:** Adjust container layout for sticky timer bar

---

## Dependencies

### Internal
- STORY-003 (WorkoutTimerBar Component)
- Existing timer state (`elapsedSeconds`, `isRunning`)
- Existing tracking state (`trackingData`)
- Existing workout plan data

### External
- None

---

## Definition of Done

- [ ] WorkoutTimerBar imported and rendered at top of screen
- [ ] All props correctly wired to state and calculations
- [ ] Timer starts/stops when play/pause pressed
- [ ] Progress updates when sets completed
- [ ] Current movement name updates as user progresses
- [ ] Sticky positioning works (stays at top when scrolling)
- [ ] Unit tests passing (5 test cases minimum)
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing
1. Open workout detail screen
2. Verify timer bar appears at top
3. Press play, verify timer starts counting
4. Complete a set, verify progress updates (e.g., 2/12 → 3/12)
5. Complete all sets in a movement, verify current movement name changes
6. Scroll down, verify timer bar stays sticky at top

### Functional Testing
- Start timer → Timer counts up
- Pause timer → Timer stops
- Complete set → Progress increments
- Complete all movements → Current movement shows "All complete"

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Timer bar covers important content | Medium | Test scroll behavior, adjust z-index if needed |
| Performance issue with useMemo calculations | Low | Profile with React DevTools, optimize if needed |
| Current movement calculation breaks with complex plans | Medium | Add unit tests for edge cases (empty plan, all complete) |

---

## Estimated Effort

- **Implementation:** 1.5 hours
- **Testing:** 1 hour
- **Code Review:** 30 minutes
- **Total:** ~3 hours

---

## Related Stories

- **Depends On:** STORY-003 (WorkoutTimerBar Component)
- **Related:** STORY-008, STORY-009, STORY-010 (Other integration stories)
- **Enables:** STORY-012 (Progress bar animation enhancement)

---

**Next:** STORY-008 (Replace Movement Display with TrackingMovementCard)
