# STORY-009.3: Summary Stats & Empty States

**Epic:** EPIC-009 Workout Template Redesign
**Story Points:** 5
**Priority:** High
**Assignee:** TBD
**Status:** Ready for Development

---

## User Story

**As a** coach reviewing my workout template
**I want** real-time summary statistics and inspiring empty states
**So that** I can quickly understand template scope and get started easily

---

## Acceptance Criteria

### Summary Stats Header
- [ ] Header displays 3 stats: Est Duration, Exercise Count, Total Sets
- [ ] Stats update in real-time as exercises/sets are added/removed
- [ ] Duration calculation: (total rest time) + (20s per set)
- [ ] Format: "⏱️ Est 45min | 💪 5 exercises | 📈 16 sets"
- [ ] Header appears above block sections
- [ ] Animates on value change (subtle fade)
- [ ] Dark mode support

### Empty State (Template Level)
- [ ] Shows when template has zero exercises
- [ ] Large dumbbell icon (60pt, neutral gray)
- [ ] Title: "No exercises yet"
- [ ] Subtitle: "Get started by adding an exercise to your template"
- [ ] Prominent "＋ Add Exercise" button (44pt height)
- [ ] Button opens exercise search modal
- [ ] Inspiring, not discouraging tone

### Empty State (Block Level)
- [ ] Shows when specific block (Warmup/Workout/Cooldown) is empty
- [ ] Smaller icon (40pt)
- [ ] Title: "No {block} exercises"
- [ ] Subtitle: "Add a {block} exercise to get started"
- [ ] "＋ Add Movement" button
- [ ] Different accent color per block (yellow/blue/green)

---

## Technical Implementation

### Components to Create

#### 1. `SummaryStatsHeader.tsx`
```typescript
interface SummaryStatsHeaderProps {
  exerciseCount: number
  totalSets: number
  estimatedDuration: number  // minutes
  loading?: boolean
}

// Calculation logic
const estimatedDuration = useMemo(() => {
  const sets = prescriptions
    .flatMap(p => p.movements)
    .flatMap(m => m.sets)

  const totalRest = sets.reduce((sum, s) => sum + (s.restDuration || 60), 0)
  const workTime = sets.length * 20  // 20s per set

  return Math.ceil((totalRest + workTime) / 60)  // minutes
}, [prescriptions])

const exerciseCount = prescriptions
  .flatMap(p => p.movements).length

const totalSets = prescriptions
  .flatMap(p => p.movements)
  .flatMap(m => m.sets).length
```

**Layout:**
```tsx
<HStack className="bg-background-100 dark:bg-background-800 p-4 rounded-lg gap-3">
  <StatItem icon="⏱️" label="Est" value={`${estimatedDuration}min`} />
  <Divider orientation="vertical" />
  <StatItem icon="💪" label="" value={`${exerciseCount} exercises`} />
  <Divider orientation="vertical" />
  <StatItem icon="📈" label="" value={`${totalSets} sets`} />
</HStack>
```

#### 2. `EmptyStateCard.tsx`
```typescript
interface EmptyStateCardProps {
  title?: string
  subtitle?: string
  icon?: React.ReactNode
  ctaLabel?: string
  onCTAPress: () => void
  variant?: 'template' | 'block'
  accentColor?: 'yellow' | 'blue' | 'green'
}

// Default props
const defaultProps = {
  title: 'No exercises yet',
  subtitle: 'Get started by adding an exercise to your template.',
  ctaLabel: '＋ Add Exercise',
  variant: 'template'
}
```

**Layout:**
```tsx
<VStack className="items-center py-12 px-6 gap-4">
  <Icon size={variant === 'template' ? 60 : 40} color="#9ca3af" />
  <VStack gap={2} className="items-center">
    <Text className="text-lg font-semibold text-center">{title}</Text>
    <Text className="text-sm text-gray-500 text-center">{subtitle}</Text>
  </VStack>
  <Button
    onPress={onCTAPress}
    className="min-h-[44px] px-6"
    variant="primary"
  >
    {ctaLabel}
  </Button>
</VStack>
```

### State Derivation (No new state needed)
```typescript
// In workout-template-create.tsx
const showTemplateEmptyState = prescriptions.every(p => p.movements.length === 0)
const showWarmupEmptyState = warmupPrescription.movements.length === 0
const showWorkoutEmptyState = workoutPrescription.movements.length === 0
const showCooldownEmptyState = cooldownPrescription.movements.length === 0
```

### Animation
```typescript
import Animated, { FadeIn, FadeOut } from 'react-native-reanimated'

<Animated.View entering={FadeIn} exiting={FadeOut}>
  <EmptyStateCard {...props} />
</Animated.View>
```

---

## Design Reference

### Summary Stats Header
```
┌─────────────────────────────────────┐
│ ⏱️ Est 45min  |  💪 5 exercises  |  📈 16 sets │
└─────────────────────────────────────┘
```

### Empty State (Template Level)
```
┌─────────────────────────────────────┐
│                                      │
│             🏋️ (60pt)                │
│                                      │
│        No exercises yet              │
│                                      │
│  Get started by adding an exercise  │
│      to your template.               │
│                                      │
│  ┌────────────────────────────────┐ │
│  │       ＋ Add Exercise           │ │
│  └────────────────────────────────┘ │
│                                      │
└─────────────────────────────────────┘
```

### Empty State (Block Level - Warmup)
```
┌─────────────────────────────────────┐
│ ▾ Warmup (0 exercises)              │
│                                      │
│         🏃 (40pt)                    │
│                                      │
│    No warmup exercises               │
│                                      │
│  Add a warmup exercise to get started│
│                                      │
│  [＋ Add Movement]                   │
│                                      │
└─────────────────────────────────────┘
  └─ Yellow accent border
```

### Color Scheme
```typescript
const accentColors = {
  warmup: 'border-l-4 border-amber-400',
  workout: 'border-l-4 border-blue-400',
  cooldown: 'border-l-4 border-green-400'
}
```

---

## Testing Requirements

### Unit Tests
```typescript
describe('SummaryStatsHeader', () => {
  it('should calculate estimated duration correctly', () => {
    const sets = [
      { restDuration: 90 },
      { restDuration: 90 },
      { restDuration: 90 }
    ]
    // Total: (90*3) + (20*3) = 330s = 5.5min → 6min rounded
    const { getByText } = render(<SummaryStatsHeader totalSets={3} />)
    expect(getByText(/6min/i)).toBeTruthy()
  })

  it('should update in real-time when sets added', () => {
    const { rerender, getByText } = render(
      <SummaryStatsHeader exerciseCount={1} totalSets={3} />
    )
    expect(getByText(/1 exercise/i)).toBeTruthy()

    rerender(<SummaryStatsHeader exerciseCount={2} totalSets={6} />)
    expect(getByText(/2 exercises/i)).toBeTruthy()
  })
})

describe('EmptyStateCard', () => {
  it('should render template-level empty state', () => {
    const { getByText } = render(
      <EmptyStateCard
        variant="template"
        onCTAPress={mockPress}
      />
    )
    expect(getByText(/No exercises yet/i)).toBeTruthy()
    expect(getByText(/Add Exercise/i)).toBeTruthy()
  })

  it('should render block-level empty state with accent', () => {
    const { container } = render(
      <EmptyStateCard
        variant="block"
        accentColor="yellow"
        title="No warmup exercises"
      />
    )
    expect(container).toHaveClass(/border-amber-400/)
  })

  it('should call onCTAPress when button tapped', () => {
    const mockPress = jest.fn()
    const { getByText } = render(<EmptyStateCard onCTAPress={mockPress} />)
    fireEvent.press(getByText(/Add Exercise/i))
    expect(mockPress).toHaveBeenCalled()
  })
})
```

### Integration Tests
- [ ] Empty state shows when template is first opened
- [ ] Empty state disappears after adding first exercise
- [ ] Summary stats update immediately after adding exercise
- [ ] Duration recalculates when rest time changes

### Visual Tests
- [ ] Screenshot test: Empty state on light mode
- [ ] Screenshot test: Empty state on dark mode
- [ ] Screenshot test: Summary stats with various counts

---

## Performance Considerations

- Use `useMemo` for duration calculations (can be expensive with 50+ sets)
- Debounce stats updates if performance issues arise
- Empty state animations should be <200ms

---

## Dependencies

### Blocked By
None (can be implemented in parallel with other stories)

### Blocks
None

---

## Definition of Done

- [ ] Code implemented and reviewed
- [ ] Unit tests passing (>80% coverage)
- [ ] Visual tests passing
- [ ] Stats calculate correctly for 50+ set templates
- [ ] Empty states match design spec
- [ ] Animations are smooth (<200ms)
- [ ] Dark mode tested
- [ ] QA approval on TestFlight

---

## Notes

- Duration estimate is intentionally simple (20s per set)
- Phase 2 could improve with exercise-specific estimates
- Consider adding "Est Volume" stat in Phase 2

---

## Related Files

- `components/workout/SummaryStatsHeader.tsx` (new)
- `components/workout/EmptyStateCard.tsx` (new)
- `app/(app)/workout-template-create.tsx` (update)
