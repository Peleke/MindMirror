# STORY-009.2: Increment Buttons & Quick Entry

**Epic:** EPIC-009 Workout Template Redesign
**Story Points:** 5
**Priority:** High
**Assignee:** TBD
**Status:** Ready for Development
**Depends On:** STORY-009.1

---

## User Story

**As a** coach adjusting set parameters
**I want** increment/decrement buttons and "Copy Last Set" functionality
**So that** I can quickly modify values without typing every number

---

## Acceptance Criteria

### Increment/Decrement Buttons
- [ ] ± buttons appear next to Load and Reps inputs
- [ ] Load increment: ±5 lb (or ±2.5 kg for metric users)
- [ ] Reps increment: ±1 rep
- [ ] Rest increment: ±15 seconds
- [ ] Buttons have 44pt minimum touch target
- [ ] Disabled state when at min/max values (reps ≥1, load ≥0)
- [ ] Haptic feedback on button press (iOS/Android)

### Copy Last Set Feature
- [ ] "Copy Last Set" button visible below set rows
- [ ] Clicking copies previous set's values (load, reps, rest)
- [ ] New set position increments correctly
- [ ] Button disabled when no sets exist
- [ ] Works with both reps and duration metric types

### Auto-Default New Sets
- [ ] "Add Set" button pre-fills new set with last set's values
- [ ] First set defaults to: 10 reps, 0 load, 60s rest
- [ ] Subsequent sets copy previous set values
- [ ] Focus automatically moves to new set's reps input

---

## Technical Implementation

### Components to Create

#### 1. `IncrementButton.tsx`
```typescript
interface IncrementButtonProps {
  direction: 'up' | 'down'
  onPress: () => void
  disabled?: boolean
  size?: 'sm' | 'md'
}

// Usage
<IncrementButton
  direction="up"
  onPress={() => updateLoad(loadValue + 5)}
  disabled={loadValue >= 1000}
/>
```

**Styling:**
- Circular button with + or - icon
- 44pt × 44pt minimum size
- Primary color on press, neutral default
- Disabled state: 50% opacity

#### 2. Update `SetRow.tsx`
Add increment buttons to Load and Reps columns:
```typescript
<View className="flex-row items-center">
  <TextInput value={loadValue} />
  <VStack gap={1}>
    <IncrementButton direction="up" onPress={incrementLoad} />
    <IncrementButton direction="down" onPress={decrementLoad} />
  </VStack>
</View>
```

#### 3. Update `SetEditorCard.tsx`
Add "Copy Last Set" and "Add Set" logic:
```typescript
const handleCopyLastSet = () => {
  const lastSet = sets[sets.length - 1]
  const newSet: SetDraft = {
    ...lastSet,
    position: sets.length + 1
  }
  onAddSet(newSet)
}

const handleAddSet = () => {
  const defaultValues = sets.length > 0
    ? { ...sets[sets.length - 1], position: sets.length + 1 }
    : { position: 1, reps: 10, loadValue: 0, loadUnit: 'lb', restDuration: 60 }

  onAddSet(defaultValues)
}
```

### Increment Logic
```typescript
const incrementLoad = () => {
  const increment = loadUnit === 'kg' ? 2.5 : 5
  const newValue = Math.min(loadValue + increment, 1000) // max 1000 lb/kg
  onUpdate({ loadValue: newValue })
}

const decrementLoad = () => {
  const decrement = loadUnit === 'kg' ? 2.5 : 5
  const newValue = Math.max(loadValue - decrement, 0) // min 0
  onUpdate({ loadValue: newValue })
}

const incrementReps = () => {
  const newValue = Math.min(reps + 1, 100) // max 100 reps
  onUpdate({ reps: newValue })
}

const decrementReps = () => {
  const newValue = Math.max(reps - 1, 1) // min 1 rep
  onUpdate({ reps: newValue })
}
```

### Haptic Feedback
```typescript
import { Haptics } from 'expo-haptics'

const handleIncrement = () => {
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
  incrementValue()
}
```

---

## Design Reference

### Visual Mockup
```
┌─────────────────────────────────────┐
│ SET    LOAD         REPS        REST│
├─────────────────────────────────────┤
│  1    135 lb  [+]  10  [+]      90s │
│              [-]       [-]          │
│  2    135 lb  [+]  10  [+]      90s │
│              [-]       [-]          │
│                                      │
│ [📋 Copy Last Set]     [＋ Add Set] │
└─────────────────────────────────────┘
```

### Button Styling
```typescript
// IncrementButton styles
const baseClass = "rounded-full min-w-[44px] min-h-[44px] items-center justify-center"
const upClass = "bg-primary-100 dark:bg-primary-900"
const downClass = "bg-background-200 dark:bg-background-800"
const disabledClass = "opacity-50"
```

---

## Testing Requirements

### Unit Tests
```typescript
describe('IncrementButton', () => {
  it('should call onPress when tapped', () => {
    const mockPress = jest.fn()
    const { getByRole } = render(<IncrementButton direction="up" onPress={mockPress} />)
    fireEvent.press(getByRole('button'))
    expect(mockPress).toHaveBeenCalled()
  })

  it('should not call onPress when disabled', () => {
    const mockPress = jest.fn()
    const { getByRole } = render(<IncrementButton disabled onPress={mockPress} />)
    fireEvent.press(getByRole('button'))
    expect(mockPress).not.toHaveBeenCalled()
  })
})

describe('SetEditorCard - Quick Entry', () => {
  it('should copy last set values', () => {
    const { getByText } = render(<SetEditorCard sets={mockSets} />)
    fireEvent.press(getByText('Copy Last Set'))
    expect(mockOnAddSet).toHaveBeenCalledWith(
      expect.objectContaining({
        loadValue: mockSets[mockSets.length - 1].loadValue,
        reps: mockSets[mockSets.length - 1].reps
      })
    )
  })

  it('should auto-default new set to previous values', () => {
    const { getByText } = render(<SetEditorCard sets={mockSets} />)
    fireEvent.press(getByText('Add Set'))
    expect(mockOnAddSet).toHaveBeenCalledWith(
      expect.objectContaining({
        loadValue: mockSets[mockSets.length - 1].loadValue
      })
    )
  })

  it('should increment load by 5 lb', () => {
    const { getByTestId } = render(<SetRow loadValue={135} loadUnit="lb" />)
    fireEvent.press(getByTestId('increment-load-up'))
    expect(mockOnUpdate).toHaveBeenCalledWith({ loadValue: 140 })
  })

  it('should not decrement reps below 1', () => {
    const { getByTestId } = render(<SetRow reps={1} />)
    const decrementButton = getByTestId('increment-reps-down')
    expect(decrementButton).toHaveProp('disabled', true)
  })
})
```

### Integration Tests
- [ ] Add 10 sets rapidly using "Copy Last Set" (<15 seconds)
- [ ] Adjust load from 135 → 225 using only increment buttons
- [ ] Verify haptic feedback triggers on physical device

### Accessibility Tests
- [ ] Increment buttons have `accessibilityLabel` ("Increase load by 5 pounds")
- [ ] Screen reader announces value changes
- [ ] Buttons are reachable via keyboard navigation (web)

---

## Performance Considerations

- Debounce increment button presses (prevent accidental double-taps)
- Haptic feedback should be Light impact (not Heavy)
- Button animations should be <100ms

---

## Dependencies

### Blocked By
- STORY-009.1 (needs SetRow and SetEditorCard)

### Blocks
None

---

## Definition of Done

- [ ] Code implemented and reviewed
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Haptic feedback works on iOS/Android
- [ ] All buttons ≥44pt touch target verified
- [ ] QA approval: "Copy Last Set" works for 10+ sets
- [ ] No performance issues with rapid tapping

---

## Notes

- Default increment amounts (±5 lb, ±1 rep) are hardcoded in Phase 1
- Phase 2 could make increments user-configurable
- Consider adding long-press for continuous increment (nice-to-have)

---

## Related Files

- `components/ui/IncrementButton.tsx` (new)
- `components/workout/SetRow.tsx` (update)
- `components/workout/SetEditorCard.tsx` (update)
