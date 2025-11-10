# STORY-009.1: Card-Based Set Editor

**Epic:** EPIC-009 Workout Template Redesign
**Story Points:** 8
**Priority:** Critical Path
**Assignee:** TBD
**Status:** Ready for Development

---

## User Story

**As a** coach creating workout templates
**I want** a card-based set editor with clear column layout
**So that** I can easily input reps, load, and rest without horizontal scrolling

---

## Acceptance Criteria

### Core Functionality
- [ ] Set editor displays as vertical card (no horizontal scroll)
- [ ] 3-column layout: LOAD | REPS/DUR | REST
- [ ] Set number column shows position (1, 2, 3...)
- [ ] All inputs are editable with numeric keyboard
- [ ] Tab/Return moves to next field in row
- [ ] Invalid input shows red border + inline error
- [ ] Cannot delete last remaining set (minimum 1 required)

### Visual Requirements
- [ ] Column headers always visible at top of card
- [ ] Column widths: Set 15%, Load 35%, Reps 30%, Rest 20%
- [ ] Card has 12pt border radius (`rounded-xl`)
- [ ] 16pt padding on all sides
- [ ] Dark mode support with proper contrast

### Touch Targets
- [ ] All inputs have 44pt minimum touch target height
- [ ] Row height accommodates 44pt targets
- [ ] Inputs are easy to tap accurately on mobile

### Error Handling
- [ ] Non-numeric input rejected with toast
- [ ] Attempting to delete only set shows warning
- [ ] Keyboard doesn't cover active input (`KeyboardAvoidingView`)

---

## Technical Implementation

### Components to Create

#### 1. `SetEditorCard.tsx`
```typescript
interface SetEditorCardProps {
  sets: SetDraft[]
  metricUnit: 'iterative' | 'temporal' | 'breath' | 'other'
  onUpdateSet: (index: number, updates: Partial<SetDraft>) => void
  onAddSet: () => void
  onDeleteSet: (index: number) => void
  onCopyLastSet: () => void
}
```

**Responsibilities:**
- Render column headers
- Map over sets and render `SetRow` for each
- Handle "Add Set" button press
- Handle "Copy Last Set" button press

#### 2. `SetRow.tsx`
```typescript
interface SetRowProps {
  set: SetDraft
  setNumber: number
  isWarmup?: boolean
  metricUnit: 'iterative' | 'temporal'
  onUpdate: (updates: Partial<SetDraft>) => void
  onDelete: () => void
  canDelete: boolean
}
```

**Responsibilities:**
- Display set number badge (1, 2, 3 or W for warmup - Phase 2)
- Render Load input with unit selector
- Render Reps/Duration input (based on `metricUnit`)
- Render Rest input
- Handle delete action (if `canDelete`)

### State Management
- Uses existing `SetDraft` type (no schema changes)
- Parent component manages sets array
- Row updates bubble up via `onUpdate` callback

### Layout Code
```typescript
const columnWidths = {
  set: '15%',
  load: '35%',
  reps: '30%',
  rest: '20%'
}

// Example row layout
<View className="flex-row items-center gap-2">
  <View style={{ width: columnWidths.set }}>
    <Text>{setNumber}</Text>
  </View>
  <View style={{ width: columnWidths.load }}>
    <TextInput keyboardType="numeric" />
  </View>
  <View style={{ width: columnWidths.reps }}>
    <TextInput keyboardType="numeric" />
  </View>
  <View style={{ width: columnWidths.rest }}>
    <TextInput keyboardType="numeric" />
  </View>
</View>
```

---

## Design Reference

### Visual Mockup
```
┌─────────────────────────────────────┐
│ SET    LOAD         REPS        REST│ ← Column headers
├─────────────────────────────────────┤
│  1    135 lb       10           90s │
│  2    135 lb       10           90s │
│  3    135 lb       10           90s │
│                                      │
│ [Copy Last Set]         [Add Set]   │
└─────────────────────────────────────┘
```

### Color Palette
- Card background: `bg-background-50 dark:bg-background-900`
- Border: `border border-outline-200 dark:border-outline-700`
- Input focus: `border-primary-500`
- Error state: `border-error-500`

---

## Testing Requirements

### Unit Tests
```typescript
describe('SetEditorCard', () => {
  it('should render all sets with correct columns', () => {
    const { getAllByRole } = render(<SetEditorCard sets={mockSets} />)
    expect(getAllByRole('textinput')).toHaveLength(mockSets.length * 3)
  })

  it('should call onUpdateSet when input changes', () => {
    const mockUpdate = jest.fn()
    const { getByTestId } = render(<SetEditorCard onUpdateSet={mockUpdate} />)
    fireEvent.changeText(getByTestId('set-0-load'), '155')
    expect(mockUpdate).toHaveBeenCalledWith(0, { loadValue: 155 })
  })

  it('should prevent deleting only set', () => {
    const { getByTestId, getByText } = render(<SetEditorCard sets={[mockSet]} />)
    fireEvent.press(getByTestId('delete-set-0'))
    expect(getByText(/must have at least 1 set/i)).toBeTruthy()
  })
})
```

### Integration Tests
- [ ] Full flow: add exercise → add 5 sets → edit values → save
- [ ] Tab navigation moves between fields correctly
- [ ] Keyboard avoidance works on small screens

### Accessibility Tests
- [ ] VoiceOver announces set number and field type
- [ ] All inputs have `accessibilityLabel`
- [ ] Color contrast meets WCAG AA

---

## Dependencies

### Blocked By
None

### Blocks
- STORY-009.2 (needs SetRow component)
- STORY-009.4 (needs SetEditorCard for ExerciseCard)

---

## Definition of Done

- [ ] Code implemented and reviewed
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Accessibility tests passing
- [ ] Dark mode tested
- [ ] QA approval on TestFlight
- [ ] No horizontal scrolling in set editor
- [ ] All touch targets ≥44pt verified

---

## Notes

- Reuse existing `TextInput` components from `@/components/ui/`
- Follow NativeWind/Tailwind styling conventions
- Ensure keyboard type is `numeric` for all number inputs
- Consider using `react-hook-form` for input validation (optional)

---

## Related Files

- `app/(app)/workout-template-create.tsx` - Parent screen (update)
- `components/ui/text-input.tsx` - Existing input component
- `mindmirror-mobile/types/workout.ts` - `SetDraft` type definition
