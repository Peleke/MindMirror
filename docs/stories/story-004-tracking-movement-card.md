# STORY-004: TrackingMovementCard Component

**Story ID:** STORY-004
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1B - Core Components
**Priority:** High (Core component)
**Points:** 3
**Status:** Ready
**Dependencies:** STORY-001 (YouTube Utility), STORY-002 (Design Tokens)

---

## User Story

**As a** user tracking my workout
**I want** a professional movement card with real thumbnails and completion tracking
**So that** I can see exercise demos and track set progress efficiently

---

## Acceptance Criteria

### Must Have
- [ ] Create `components/workout/TrackingMovementCard.tsx` component
- [ ] Display circular thumbnail with **real YouTube image** (using STORY-001 utility)
- [ ] Show completion counter: "2/3 sets complete" under movement name
- [ ] Collapse toggle for video/description (ChevronDown/Up icon)
- [ ] Set table with completion checkmarks (green CheckCircle)
- [ ] Completed sets grayed out (opacity 0.6, lighter inputs)
- [ ] Clean borders, rounded corners, subtle shadows from design tokens
- [ ] Use design tokens from STORY-002

### Should Have
- [ ] Play icon overlay on thumbnail (tappable to open video)
- [ ] Fallback image when YouTube URL invalid or missing
- [ ] Markdown rendering for movement description
- [ ] Smooth collapse/expand animation
- [ ] Disabled state for completed sets (prevent re-editing)

### Could Have
- [ ] Thumbnail loading skeleton while image loads
- [ ] Video playback inline (instead of opening browser)
- [ ] Haptic feedback on set completion

---

## Technical Specification

### Component Props
```typescript
interface TrackingMovementCardProps {
  movementName: string
  description?: string
  videoUrl?: string
  sets: Set[]  // Array of set data
  metricUnit: 'reps' | 'duration' | 'distance'
  onSetComplete: (setIndex: number, completed: boolean) => void
  onUpdateSet: (setIndex: number, field: 'value' | 'load' | 'rest', value: string) => void
}

interface Set {
  setNumber: number
  value: string  // Reps, duration, or distance
  load: string   // Weight or resistance
  rest: string   // Rest time in seconds
  completed: boolean
}
```

### Visual Layout
```
┌─────────────────────────────────────────────┐
│ 🎬 Barbell Back Squat              [▼]     │ ← Thumbnail + Collapse toggle
│ 2/3 sets complete                          │ ← Progress counter
│                                             │
│ [Video & Description collapsed by default] │
│                                             │
│  ✓ | # | Reps | Load | Rest               │ ← Set table header
│ [✓] 1   12    135lb   90                  │ ← Completed (grayed)
│ [✓] 2   10    145lb   90                  │ ← Completed (grayed)
│ [ ] 3   8     155lb   90                  │ ← Incomplete (active)
└─────────────────────────────────────────────┘
```

### Component Structure
```typescript
import React, { useState } from 'react'
import { View, Text, Image, TouchableOpacity, TextInput, StyleSheet } from 'react-native'
import { ChevronDown, ChevronUp, CheckCircle, Circle, Play } from 'lucide-react-native'
import { getYouTubeThumbnail } from '@/utils/youtube'
import { colors, spacing, borderRadius, shadows, typography } from '@/utils/design-tokens'

export function TrackingMovementCard({
  movementName,
  description,
  videoUrl,
  sets,
  metricUnit,
  onSetComplete,
  onUpdateSet,
}: TrackingMovementCardProps) {
  const [collapsed, setCollapsed] = useState(true)
  const thumbnailUrl = videoUrl ? getYouTubeThumbnail(videoUrl) : null
  const completedCount = sets.filter(s => s.completed).length
  const totalSets = sets.length

  return (
    <View style={styles.card}>
      {/* Header: Thumbnail + Movement Name + Collapse */}
      <View style={styles.header}>
        <View style={styles.thumbnailContainer}>
          <Image
            source={{ uri: thumbnailUrl || 'https://via.placeholder.com/80' }}
            style={styles.thumbnail}
          />
          {videoUrl && (
            <TouchableOpacity style={styles.playOverlay}>
              <Play size={20} color="white" fill="white" />
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.headerText}>
          <Text style={styles.movementName}>{movementName}</Text>
          <Text style={styles.progressCounter}>
            {completedCount}/{totalSets} sets complete
          </Text>
        </View>

        <TouchableOpacity onPress={() => setCollapsed(!collapsed)}>
          {collapsed ? (
            <ChevronDown size={20} color={colors.gray[600]} />
          ) : (
            <ChevronUp size={20} color={colors.gray[600]} />
          )}
        </TouchableOpacity>
      </View>

      {/* Collapsible Video & Description */}
      {!collapsed && description && (
        <View style={styles.descriptionContainer}>
          <Text style={styles.description}>{description}</Text>
        </View>
      )}

      {/* Set Table */}
      <View style={styles.setTable}>
        {/* Table Header */}
        <View style={styles.tableHeader}>
          <Text style={[styles.tableHeaderText, styles.checkCol]}>✓</Text>
          <Text style={[styles.tableHeaderText, styles.setCol]}>#</Text>
          <Text style={[styles.tableHeaderText, styles.valueCol]}>
            {metricUnit === 'reps' ? 'Reps' : metricUnit === 'duration' ? 'Sec' : 'Dist'}
          </Text>
          <Text style={[styles.tableHeaderText, styles.loadCol]}>Load</Text>
          <Text style={[styles.tableHeaderText, styles.restCol]}>Rest</Text>
        </View>

        {/* Set Rows */}
        {sets.map((set, index) => (
          <View
            key={index}
            style={[styles.setRow, set.completed && styles.setRowCompleted]}
          >
            {/* Completion Checkbox */}
            <TouchableOpacity
              style={styles.checkCol}
              onPress={() => onSetComplete(index, !set.completed)}
            >
              {set.completed ? (
                <CheckCircle size={20} color={colors.success[600]} />
              ) : (
                <Circle size={20} color={colors.gray[300]} />
              )}
            </TouchableOpacity>

            {/* Set Number */}
            <Text style={[styles.setNumber, styles.setCol]}>
              {set.setNumber}
            </Text>

            {/* Value (Reps/Duration/Distance) */}
            <TextInput
              style={[styles.input, styles.valueCol]}
              value={set.value}
              onChangeText={(value) => onUpdateSet(index, 'value', value)}
              keyboardType="numeric"
              editable={!set.completed}
            />

            {/* Load */}
            <TextInput
              style={[styles.input, styles.loadCol]}
              value={set.load}
              onChangeText={(value) => onUpdateSet(index, 'load', value)}
              editable={!set.completed}
            />

            {/* Rest */}
            <TextInput
              style={[styles.input, styles.restCol]}
              value={set.rest}
              onChangeText={(value) => onUpdateSet(index, 'rest', value)}
              keyboardType="numeric"
              editable={!set.completed}
            />
          </View>
        ))}
      </View>
    </View>
  )
}
```

### Styling
```typescript
const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.gray[300],
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  thumbnailContainer: {
    position: 'relative',
    marginRight: spacing.sm,
  },
  thumbnail: {
    width: 60,
    height: 60,
    borderRadius: borderRadius.full,
    borderWidth: 2,
    borderColor: colors.primary[300],
  },
  playOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerText: {
    flex: 1,
  },
  movementName: {
    ...typography.movementName,
    color: colors.gray[900],
  },
  progressCounter: {
    fontSize: 12,
    color: colors.success[600],
    marginTop: 2,
  },
  descriptionContainer: {
    marginBottom: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray[300],
  },
  description: {
    fontSize: 14,
    color: colors.gray[600],
    lineHeight: 20,
  },
  setTable: {
    marginTop: spacing.sm,
  },
  tableHeader: {
    flexDirection: 'row',
    paddingBottom: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray[300],
  },
  tableHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.gray[600],
    textAlign: 'center',
  },
  setRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray[300],
  },
  setRowCompleted: {
    opacity: 0.6,
  },
  checkCol: { width: 30 },
  setCol: { width: 30, textAlign: 'center' },
  valueCol: { width: 60 },
  loadCol: { width: 70 },
  restCol: { width: 60 },
  setNumber: {
    fontSize: 14,
    color: colors.gray[900],
  },
  input: {
    ...typography.setData,
    borderWidth: 1,
    borderColor: colors.gray[300],
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.xs,
    paddingVertical: 4,
    textAlign: 'center',
  },
})
```

---

## Test Cases

### Component Tests (`components/workout/__tests__/TrackingMovementCard.test.tsx`)

```typescript
import { render, fireEvent } from '@testing-library/react-native'
import { TrackingMovementCard } from '../TrackingMovementCard'

describe('TrackingMovementCard', () => {
  const mockSets = [
    { setNumber: 1, value: '12', load: '135', rest: '90', completed: true },
    { setNumber: 2, value: '10', load: '145', rest: '90', completed: true },
    { setNumber: 3, value: '8', load: '155', rest: '90', completed: false },
  ]

  const defaultProps = {
    movementName: 'Barbell Back Squat',
    description: 'Keep chest up, knees tracking toes',
    videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    sets: mockSets,
    metricUnit: 'reps' as const,
    onSetComplete: jest.fn(),
    onUpdateSet: jest.fn(),
  }

  it('should display movement name', () => {
    const { getByText } = render(<TrackingMovementCard {...defaultProps} />)
    expect(getByText('Barbell Back Squat')).toBeTruthy()
  })

  it('should display completion counter', () => {
    const { getByText } = render(<TrackingMovementCard {...defaultProps} />)
    expect(getByText('2/3 sets complete')).toBeTruthy()
  })

  it('should display YouTube thumbnail', () => {
    const { getByRole } = render(<TrackingMovementCard {...defaultProps} />)
    const image = getByRole('image')
    expect(image.props.source.uri).toContain('img.youtube.com')
  })

  it('should collapse/expand description', () => {
    const { getByText, queryByText } = render(<TrackingMovementCard {...defaultProps} />)

    // Initially collapsed
    expect(queryByText('Keep chest up, knees tracking toes')).toBeNull()

    // Expand
    fireEvent.press(getByRole('button', { name: /chevron/i }))
    expect(getByText('Keep chest up, knees tracking toes')).toBeTruthy()
  })

  it('should show checkmarks for completed sets', () => {
    const { getAllByTestId } = render(<TrackingMovementCard {...defaultProps} />)
    const checkmarks = getAllByTestId('check-circle-icon')
    expect(checkmarks.length).toBe(2)  // Sets 1 and 2 completed
  })

  it('should call onSetComplete when checkbox pressed', () => {
    const onSetComplete = jest.fn()
    const { getAllByRole } = render(
      <TrackingMovementCard {...defaultProps} onSetComplete={onSetComplete} />
    )
    fireEvent.press(getAllByRole('button')[1])  // First checkbox
    expect(onSetComplete).toHaveBeenCalledWith(0, false)  // Toggle to incomplete
  })

  it('should disable inputs for completed sets', () => {
    const { getAllByRole } = render(<TrackingMovementCard {...defaultProps} />)
    const inputs = getAllByRole('textbox')

    // First 3 inputs (set 1) should be disabled
    expect(inputs[0].props.editable).toBe(false)
    expect(inputs[1].props.editable).toBe(false)
    expect(inputs[2].props.editable).toBe(false)

    // Last 3 inputs (set 3) should be enabled
    expect(inputs[6].props.editable).toBe(true)
  })

  it('should call onUpdateSet when input changes', () => {
    const onUpdateSet = jest.fn()
    const { getAllByRole } = render(
      <TrackingMovementCard {...defaultProps} onUpdateSet={onUpdateSet} />
    )
    const inputs = getAllByRole('textbox')

    fireEvent.changeText(inputs[6], '10')  // Update value for set 3
    expect(onUpdateSet).toHaveBeenCalledWith(2, 'value', '10')
  })
})
```

---

## Files to Create

### New Files
- `components/workout/TrackingMovementCard.tsx` - Main component
- `components/workout/__tests__/TrackingMovementCard.test.tsx` - Unit tests

---

## Dependencies

### Internal
- `utils/youtube.ts` (STORY-001)
- `utils/design-tokens.ts` (STORY-002)
- Lucide React Native icons

### External
- `react-native` (core)
- `lucide-react-native` (already installed)

---

## Definition of Done

- [ ] Component file created with all required props
- [ ] YouTube thumbnails display using STORY-001 utility
- [ ] Completion counter shows correct progress
- [ ] Collapse/expand toggle works for description
- [ ] Set table displays with checkmarks
- [ ] Completed sets are grayed out (opacity 0.6)
- [ ] Inputs disabled for completed sets
- [ ] Unit tests passing (8 test cases minimum)
- [ ] Test coverage ≥90%
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing
1. Import component into test screen
2. Pass mock sets with varying completion states
3. Verify thumbnail loads from YouTube URL
4. Toggle collapse/expand, verify description shows/hides
5. Complete a set, verify gray styling and disabled inputs
6. Edit incomplete set values, verify onChange callbacks

### Visual Regression
- Compare with UX spec mockup (card design)
- Verify circular thumbnail with indigo border
- Check completion counter color (green)
- Verify completed rows have opacity 0.6

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube thumbnail fails to load | Medium | Fallback to placeholder image |
| Table layout breaks on small screens | Medium | Test on smallest supported device size |
| Completed sets remain editable | High | Strict `editable={!set.completed}` enforcement |

---

## Estimated Effort

- **Implementation:** 2.5 hours
- **Testing:** 1.5 hours
- **Code Review:** 30 minutes
- **Total:** ~4.5 hours

---

## Related Stories

- **Depends On:** STORY-001 (YouTube Utility), STORY-002 (Design Tokens)
- **Blocks:** STORY-008 (Integration into workout detail screen)
- **Related:** STORY-011 (Checkmark bounce animation will enhance this component)

---

**Next:** STORY-005 (SectionHeader Component)
