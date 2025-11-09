# STORY-009.4: Collapsible Blocks & Visual Polish

**Epic:** EPIC-009 Workout Template Redesign
**Story Points:** 5
**Priority:** High
**Assignee:** TBD
**Status:** Ready for Development

---

## User Story

**As a** coach building complex multi-exercise templates
**I want** collapsible block sections with polished visual design
**So that** I can focus on one phase at a time and navigate templates easily

---

## Acceptance Criteria

### Collapsible Block Sections
- [ ] Three blocks: Warmup, Workout, Cooldown
- [ ] Each block has header showing: Name, exercise count, set count
- [ ] Clicking header toggles expand/collapse
- [ ] Chevron icon indicates state (▾ expanded, ▸ collapsed)
- [ ] Collapse state persists across app restarts (AsyncStorage)
- [ ] Smooth animation (200ms ease-in-out)
- [ ] Empty blocks start collapsed

### Block Header Design
- [ ] Format: "▾ Warmup (2 exercises, 6 sets)"
- [ ] Different accent colors per block:
  - Warmup: Yellow (`border-l-4 border-amber-400`)
  - Workout: Blue (`border-l-4 border-blue-500`)
  - Cooldown: Green (`border-l-4 border-green-400`)
- [ ] Header is 44pt minimum height (touchable)
- [ ] Tapping anywhere on header toggles collapse

### Visual Polish
- [ ] Hevy-inspired card shadows and borders
- [ ] Consistent 16pt padding on all cards
- [ ] 12pt border radius on cards
- [ ] Proper spacing between blocks (16pt gap)
- [ ] Dark mode optimized colors
- [ ] Smooth transitions on all interactions

### Exercise Card Improvements
- [ ] Drag handle (≡) visible when 2+ exercises
- [ ] Delete button (🗑️) with confirmation
- [ ] Equipment label below exercise name
- [ ] Rest timer displayed prominently
- [ ] Card background differentiates from screen background

---

## Technical Implementation

### Components to Create

#### 1. `CollapsibleBlockSection.tsx`
```typescript
interface CollapsibleBlockSectionProps {
  blockType: 'warmup' | 'workout' | 'cooldown'
  title: string
  exerciseCount: number
  totalSets: number
  isCollapsed?: boolean
  onToggleCollapse: () => void
  onAddExercise: () => void
  children: React.ReactNode
}

const CollapsibleBlockSection: React.FC<Props> = ({
  blockType,
  title,
  exerciseCount,
  totalSets,
  isCollapsed,
  onToggleCollapse,
  children
}) => {
  const accentColor = {
    warmup: 'border-amber-400',
    workout: 'border-blue-500',
    cooldown: 'border-green-400'
  }[blockType]

  return (
    <VStack className={`rounded-xl bg-background-50 dark:bg-background-900 border-l-4 ${accentColor}`}>
      <TouchableOpacity
        onPress={onToggleCollapse}
        className="flex-row items-center justify-between p-4 min-h-[44px]"
      >
        <HStack gap={2}>
          <Text className="text-xl">{isCollapsed ? '▸' : '▾'}</Text>
          <Text className="font-semibold">
            {title} ({exerciseCount} exercises, {totalSets} sets)
          </Text>
        </HStack>
      </TouchableOpacity>

      {!isCollapsed && (
        <Animated.View entering={FadeIn} exiting={FadeOut}>
          <VStack className="px-4 pb-4 gap-3">
            {children}
            <Button onPress={onAddExercise}>＋ Add Movement</Button>
          </VStack>
        </Animated.View>
      )}
    </VStack>
  )
}
```

#### 2. Collapse State Persistence
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage'

const COLLAPSE_STATE_KEY = 'workout_template_block_collapse_state'

const useCollapseState = () => {
  const [collapseState, setCollapseState] = useState<Record<string, boolean>>({})

  useEffect(() => {
    // Load from AsyncStorage on mount
    AsyncStorage.getItem(COLLAPSE_STATE_KEY).then(saved => {
      if (saved) setCollapseState(JSON.parse(saved))
    })
  }, [])

  const toggleCollapse = (blockType: string) => {
    const newState = { ...collapseState, [blockType]: !collapseState[blockType] }
    setCollapseState(newState)
    AsyncStorage.setItem(COLLAPSE_STATE_KEY, JSON.stringify(newState))
  }

  return { collapseState, toggleCollapse }
}
```

#### 3. Update `ExerciseCard.tsx`
Add drag handle, delete confirmation, and visual polish:
```typescript
const ExerciseCard: React.FC<Props> = ({ movement, onDelete, isDraggable }) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  return (
    <VStack className="rounded-xl bg-background-100 dark:bg-background-800 p-4 border border-outline-200 dark:border-outline-700">
      <HStack className="justify-between items-center mb-2">
        <HStack gap={2}>
          {isDraggable && <Icon name="drag-handle" size={24} color="#6b7280" />}
          <Text className="text-lg font-semibold">{movement.name}</Text>
        </HStack>
        <TouchableOpacity onPress={() => setShowDeleteConfirm(true)}>
          <Icon name="trash" size={20} color="#dc2626" />
        </TouchableOpacity>
      </HStack>

      <Text className="text-sm text-gray-500 mb-2">{movement.equipment}</Text>
      <Text className="text-sm text-gray-500 mb-3">Rest Timer: {movement.restTime}</Text>

      <SetEditorCard {...setEditorProps} />

      {showDeleteConfirm && (
        <ConfirmDialog
          title="Delete Exercise?"
          message="This will remove all sets for this exercise."
          onConfirm={onDelete}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </VStack>
  )
}
```

### Visual Design Tokens
```typescript
const theme = {
  // Card shadows
  cardShadow: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },

  // Block accent colors
  blockAccents: {
    warmup: {
      border: '#fbbf24', // amber-400
      bg: '#fef3c7',     // amber-100
      bgDark: '#78350f'  // amber-900/20
    },
    workout: {
      border: '#3b82f6', // blue-500
      bg: '#dbeafe',     // blue-100
      bgDark: '#1e3a8a'  // blue-900/20
    },
    cooldown: {
      border: '#4ade80', // green-400
      bg: '#d1fae5',     // green-100
      bgDark: '#14532d'  // green-900/20
    }
  },

  // Spacing
  spacing: {
    cardGap: 12,       // gap-3
    blockGap: 16,      // gap-4
    screenPadding: 16  // px-4
  }
}
```

---

## Design Reference

### Collapsible Block (Expanded)
```
┌─────────────────────────────────────┐
│ ▾ Warmup (2 exercises, 4 sets)      │ ← Yellow accent border
├─────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐  │
│  │ Bulgarian Split Squat  [🗑️]  │  │ ← Exercise card
│  │ Barbell                       │  │
│  │ [SetEditorCard...]            │  │
│  └──────────────────────────────┘  │
│                                      │
│  [＋ Add Movement]                   │
│                                      │
└─────────────────────────────────────┘
```

### Collapsible Block (Collapsed)
```
┌─────────────────────────────────────┐
│ ▸ Workout (3 exercises, 12 sets)    │ ← Blue accent border
└─────────────────────────────────────┘
```

### Exercise Card Detail
```
┌──────────────────────────────────────┐
│ [≡] Bench Press              [🗑️]    │ ← Drag handle + delete
│ Barbell                               │ ← Equipment
│ Rest Timer: 3min                      │ ← Rest time
├───────────────────────────────────────┤
│ [SetEditorCard with sets...]          │
└───────────────────────────────────────┘
```

---

## Testing Requirements

### Unit Tests
```typescript
describe('CollapsibleBlockSection', () => {
  it('should toggle collapse state on header press', () => {
    const mockToggle = jest.fn()
    const { getByText } = render(
      <CollapsibleBlockSection
        title="Warmup"
        onToggleCollapse={mockToggle}
      />
    )
    fireEvent.press(getByText(/Warmup/i))
    expect(mockToggle).toHaveBeenCalled()
  })

  it('should hide children when collapsed', () => {
    const { queryByText } = render(
      <CollapsibleBlockSection isCollapsed={true}>
        <Text>Exercise Card</Text>
      </CollapsibleBlockSection>
    )
    expect(queryByText('Exercise Card')).toBeNull()
  })

  it('should persist collapse state to AsyncStorage', async () => {
    const { toggleCollapse } = useCollapseState()
    toggleCollapse('warmup')

    const saved = await AsyncStorage.getItem(COLLAPSE_STATE_KEY)
    expect(JSON.parse(saved)).toEqual({ warmup: true })
  })
})

describe('ExerciseCard', () => {
  it('should show drag handle when isDraggable is true', () => {
    const { getByTestId } = render(<ExerciseCard isDraggable={true} />)
    expect(getByTestId('drag-handle')).toBeTruthy()
  })

  it('should show confirmation before deleting', () => {
    const mockDelete = jest.fn()
    const { getByTestId, getByText } = render(
      <ExerciseCard onDelete={mockDelete} />
    )
    fireEvent.press(getByTestId('delete-button'))
    expect(getByText(/Delete Exercise?/i)).toBeTruthy()
    expect(mockDelete).not.toHaveBeenCalled()
  })
})
```

### Integration Tests
- [ ] Collapse block → restart app → block remains collapsed
- [ ] Add exercise to collapsed block → block auto-expands
- [ ] Delete exercise with confirmation → exercise removed

### Visual Tests
- [ ] Screenshot: All blocks expanded (light mode)
- [ ] Screenshot: All blocks collapsed (dark mode)
- [ ] Screenshot: Mixed collapse states
- [ ] Screenshot: Exercise card with drag handle

---

## Accessibility Requirements

- [ ] Block headers have `accessibilityLabel`: "Warmup section, 2 exercises, 6 sets, collapsed"
- [ ] Chevron state announced: "expanded" or "collapsed"
- [ ] Delete button requires double-tap (confirmation)
- [ ] All interactive elements ≥44pt

---

## Performance Considerations

- Collapse animation should be <200ms
- AsyncStorage writes should be debounced
- Large templates (20+ exercises) should remain smooth

---

## Dependencies

### Blocked By
- STORY-009.1 (needs SetEditorCard for ExerciseCard)

### Blocks
None

---

## Definition of Done

- [ ] Code implemented and reviewed
- [ ] Unit tests passing (>80% coverage)
- [ ] Visual tests passing
- [ ] Collapse state persists across app restarts
- [ ] Animations are smooth (<200ms)
- [ ] Delete confirmation works
- [ ] Dark mode tested
- [ ] QA approval on TestFlight

---

## Notes

- Empty blocks should default to collapsed for cleaner initial state
- Block auto-expands if exercise added while collapsed
- Consider adding "Collapse All" / "Expand All" button in Phase 2

---

## Related Files

- `components/workout/CollapsibleBlockSection.tsx` (new)
- `components/workout/ExerciseCard.tsx` (refactor)
- `app/(app)/workout-template-create.tsx` (update)
- `@react-native-async-storage/async-storage` (dependency)
