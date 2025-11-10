# STORY-010: Add MetadataCard to Screen Header

**Story ID:** STORY-010
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1C - Integration
**Priority:** Medium
**Points:** 2
**Status:** Ready
**Dependencies:** STORY-006 (MetadataCard Component)

---

## User Story

**As a** user viewing my workout details
**I want** a professional metadata card at the top showing workout summary
**So that** I can quickly see key workout information

---

## Acceptance Criteria

### Must Have
- [ ] Add MetadataCard component below WorkoutTimerBar
- [ ] Display workout date (formatted as "MMM D, YYYY")
- [ ] Display elapsed time (MM:SS format, updates in real-time)
- [ ] Display movements count and total sets
- [ ] Display workout description (collapsible)
- [ ] Match UX spec visual design (icons, spacing, shadows)

### Should Have
- [ ] Description collapsed by default
- [ ] Description supports Markdown rendering
- [ ] Real-time duration updates as timer runs

### Could Have
- [ ] Tap stats to see detailed breakdown
- [ ] Edit description inline

---

## Technical Specification

### Integration Pattern
```typescript
// In app/(app)/workout/[id].tsx
import { MetadataCard } from './MetadataCard'  // Inline component from STORY-006

<View style={styles.container}>
  <WorkoutTimerBar {...timerProps} />

  <ScrollView>
    {/* Metadata Card */}
    <MetadataCard
      date={workoutPlan.scheduledDate}
      duration={elapsedSeconds}
      movementsCount={workoutPlan.movements.length}
      setsCount={totalSets}
      description={workoutPlan.description}
    />

    {/* Section Headers & Movements */}
    {/* ... */}
  </ScrollView>
</View>
```

### Real-Time Duration Update
```typescript
// Duration prop updates automatically via elapsedSeconds state
// No additional logic needed - state already updates every second
```

---

## Test Cases

```typescript
describe('WorkoutDetailScreen - MetadataCard Integration', () => {
  it('should display metadata card below timer bar', () => {
    const { getByTestId } = render(<WorkoutDetailScreen />)
    expect(getByTestId('metadata-card')).toBeTruthy()
  })

  it('should show formatted workout date', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    expect(getByText('Jan 9, 2025')).toBeTruthy()
  })

  it('should show movements and sets count', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    expect(getByText('3 • 12 sets')).toBeTruthy()
  })

  it('should update duration in real-time', () => {
    const { getByText } = render(<WorkoutDetailScreen />)

    // Initial: 00:00
    expect(getByText('00:00')).toBeTruthy()

    // Start timer, wait 5 seconds
    act(() => {
      jest.advanceTimersByTime(5000)
    })

    // Updated: 00:05
    expect(getByText('00:05')).toBeTruthy()
  })
})
```

---

## Definition of Done

- [ ] MetadataCard integrated below timer bar
- [ ] Date displays correctly formatted
- [ ] Duration updates in real-time
- [ ] Movements/sets count accurate
- [ ] Description collapses/expands
- [ ] Unit tests passing (4 test cases)
- [ ] Committed to feature branch

---

## Estimated Effort: ~1.5 hours

---

**Next:** STORY-011 (Checkmark Bounce Animation)
