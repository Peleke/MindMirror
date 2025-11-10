# STORY-009: Add Section Headers to Workout Phases

**Story ID:** STORY-009
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1C - Integration
**Priority:** Medium
**Points:** 1
**Status:** Ready
**Dependencies:** STORY-005 (SectionHeader Component)

---

## User Story

**As a** user tracking my workout
**I want** clear section headers for warmup, workout, and cooldown phases
**So that** I understand workout pacing and context

---

## Acceptance Criteria

### Must Have
- [ ] Add SectionHeader component before each workout phase
- [ ] WARMUP section with 🔥 emoji
- [ ] WORKOUT section with 💪 emoji
- [ ] COOLDOWN section with 😌 emoji
- [ ] Headers only display if phase has movements (conditional rendering)
- [ ] Match UX spec visual design (gradient, typography)

### Should Have
- [ ] Consistent spacing above/below headers
- [ ] Headers visually separate phases clearly

### Could Have
- [ ] Fade-in animation on first render
- [ ] Different gradient colors per phase

---

## Technical Specification

### Integration Pattern
```typescript
// In app/(app)/workout/[id].tsx
// Use inline SectionHeader component from STORY-005

<ScrollView>
  {/* WARMUP Phase */}
  {warmupMovements.length > 0 && (
    <>
      <SectionHeader title="WARMUP" icon="🔥" />
      {warmupMovements.map(movement => (
        <TrackingMovementCard key={movement.id} {...movement} />
      ))}
    </>
  )}

  {/* WORKOUT Phase */}
  {workoutMovements.length > 0 && (
    <>
      <SectionHeader title="WORKOUT" icon="💪" />
      {workoutMovements.map(movement => (
        <TrackingMovementCard key={movement.id} {...movement} />
      ))}
    </>
  )}

  {/* COOLDOWN Phase */}
  {cooldownMovements.length > 0 && (
    <>
      <SectionHeader title="COOLDOWN" icon="😌" />
      {cooldownMovements.map(movement => (
        <TrackingMovementCard key={movement.id} {...movement} />
      ))}
    </>
  )}
</ScrollView>
```

### Phase Data Grouping
```typescript
// Group movements by phase
const warmupMovements = workoutPlan.movements.filter(m => m.phase === 'warmup')
const workoutMovements = workoutPlan.movements.filter(m => m.phase === 'workout')
const cooldownMovements = workoutPlan.movements.filter(m => m.phase === 'cooldown')
```

---

## Test Cases

```typescript
describe('WorkoutDetailScreen - Section Headers', () => {
  it('should display WARMUP section header', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    expect(getByText('🔥 WARMUP')).toBeTruthy()
  })

  it('should display WORKOUT section header', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    expect(getByText('💪 WORKOUT')).toBeTruthy()
  })

  it('should display COOLDOWN section header', () => {
    const { getByText } = render(<WorkoutDetailScreen />)
    expect(getByText('😌 COOLDOWN')).toBeTruthy()
  })

  it('should hide section header if phase has no movements', () => {
    const { queryByText } = render(
      <WorkoutDetailScreen workoutPlan={{ ...plan, warmupMovements: [] }} />
    )
    expect(queryByText('🔥 WARMUP')).toBeNull()
  })
})
```

---

## Definition of Done

- [ ] SectionHeader added before each workout phase
- [ ] Conditional rendering (only show if phase has movements)
- [ ] Correct emoji icons for each phase
- [ ] Visual design matches UX spec
- [ ] Unit tests passing (4 test cases)
- [ ] Committed to feature branch

---

## Estimated Effort: ~1 hour

---

**Next:** STORY-010 (Add MetadataCard to Screen Header)
