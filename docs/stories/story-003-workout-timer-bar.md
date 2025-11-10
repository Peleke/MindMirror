# STORY-003: WorkoutTimerBar Component (Sticky Header)

**Story ID:** STORY-003
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1B - Core Components
**Priority:** High
**Points:** 3
**Status:** Ready
**Dependencies:** STORY-002 (Design Tokens)

---

## User Story

**As a** user tracking my workout
**I want** a sticky timer bar always visible at the top
**So that** I can see elapsed time and progress without scrolling

---

## Acceptance Criteria

### Must Have
- [ ] Create `components/workout/WorkoutTimerBar.tsx` component
- [ ] Sticky positioning at top of screen (stays visible when scrolling)
- [ ] Display elapsed time in MM:SS format (monospace font)
- [ ] Display play/pause button (circular, indigo accent)
- [ ] Display progress counter (e.g., "5/12" sets complete)
- [ ] Display current movement name (truncated if too long)
- [ ] Animated progress bar underneath stats (green gradient fill)
- [ ] Use design tokens from STORY-002

### Should Have
- [ ] Timer pulses when running (subtle scale animation)
- [ ] Progress bar animates smoothly when updated
- [ ] Icons for timer, progress, movement (Clock, TrendingUp, Dumbbell)
- [ ] Responsive layout (handles long movement names gracefully)

### Could Have
- [ ] Tap timer to toggle play/pause
- [ ] Tap progress to see detailed breakdown
- [ ] Background color changes based on workout phase (warmup/workout/cooldown)

---

## Technical Specification

### Component Props
```typescript
interface WorkoutTimerBarProps {
  elapsedSeconds: number
  isRunning: boolean
  completedSets: number
  totalSets: number
  currentMovementName: string
  onToggleTimer: () => void
}
```

### Visual Layout
```
┌─────────────────────────────────────────────────┐
│ ⏱️ 12:34 [⏸️]  |  📈 5/12  |  💪 Push-ups       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ← Progress bar
└─────────────────────────────────────────────────┘
```

### Component Structure
```typescript
import React from 'react'
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'
import { Clock, TrendingUp, Dumbbell, Play, Pause } from 'lucide-react-native'
import { colors, spacing, borderRadius, shadows, typography } from '@/utils/design-tokens'

export function WorkoutTimerBar({
  elapsedSeconds,
  isRunning,
  completedSets,
  totalSets,
  currentMovementName,
  onToggleTimer,
}: WorkoutTimerBarProps) {
  const formattedTime = formatElapsedTime(elapsedSeconds)
  const progressPercentage = (completedSets / totalSets) * 100

  return (
    <View style={styles.container}>
      {/* Top bar with stats */}
      <View style={styles.statsRow}>
        {/* Timer */}
        <View style={styles.stat}>
          <Clock size={16} color={colors.primary[600]} />
          <Text style={styles.timerText}>{formattedTime}</Text>
          <TouchableOpacity onPress={onToggleTimer} style={styles.playButton}>
            {isRunning ? (
              <Pause size={16} color={colors.primary[600]} />
            ) : (
              <Play size={16} color={colors.primary[600]} />
            )}
          </TouchableOpacity>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Progress */}
        <View style={styles.stat}>
          <TrendingUp size={16} color={colors.success[600]} />
          <Text style={styles.statText}>{completedSets}/{totalSets}</Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Current Movement */}
        <View style={[styles.stat, styles.movementStat]}>
          <Dumbbell size={16} color={colors.gray[600]} />
          <Text style={styles.movementText} numberOfLines={1}>
            {currentMovementName}
          </Text>
        </View>
      </View>

      {/* Progress bar */}
      <View style={styles.progressBarContainer}>
        <View style={[styles.progressBar, { width: `${progressPercentage}%` }]} />
      </View>
    </View>
  )
}

function formatElapsedTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
```

### Styling
```typescript
const styles = StyleSheet.create({
  container: {
    position: 'sticky',
    top: 0,
    zIndex: 10,
    backgroundColor: 'white',
    ...shadows.sm,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  movementStat: {
    flex: 1,
  },
  divider: {
    width: 1,
    height: 20,
    backgroundColor: colors.gray[300],
    marginHorizontal: spacing.sm,
  },
  timerText: {
    ...typography.timer,
    color: colors.primary[600],
  },
  statText: {
    ...typography.stats,
    color: colors.success[600],
  },
  movementText: {
    ...typography.stats,
    color: colors.gray[600],
    flex: 1,
  },
  playButton: {
    width: 28,
    height: 28,
    borderRadius: borderRadius.full,
    backgroundColor: colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressBarContainer: {
    height: 3,
    backgroundColor: colors.gray[300],
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.success[600],
  },
})
```

---

## Test Cases

### Component Tests (`components/workout/__tests__/WorkoutTimerBar.test.tsx`)

```typescript
import { render, fireEvent } from '@testing-library/react-native'
import { WorkoutTimerBar } from '../WorkoutTimerBar'

describe('WorkoutTimerBar', () => {
  const defaultProps = {
    elapsedSeconds: 754,  // 12:34
    isRunning: true,
    completedSets: 5,
    totalSets: 12,
    currentMovementName: 'Push-ups',
    onToggleTimer: jest.fn(),
  }

  it('should display formatted elapsed time', () => {
    const { getByText } = render(<WorkoutTimerBar {...defaultProps} />)
    expect(getByText('12:34')).toBeTruthy()
  })

  it('should display progress counter', () => {
    const { getByText } = render(<WorkoutTimerBar {...defaultProps} />)
    expect(getByText('5/12')).toBeTruthy()
  })

  it('should display current movement name', () => {
    const { getByText } = render(<WorkoutTimerBar {...defaultProps} />)
    expect(getByText('Push-ups')).toBeTruthy()
  })

  it('should show pause icon when running', () => {
    const { queryByTestId } = render(<WorkoutTimerBar {...defaultProps} />)
    expect(queryByTestId('pause-icon')).toBeTruthy()
  })

  it('should show play icon when paused', () => {
    const { queryByTestId } = render(
      <WorkoutTimerBar {...defaultProps} isRunning={false} />
    )
    expect(queryByTestId('play-icon')).toBeTruthy()
  })

  it('should call onToggleTimer when button pressed', () => {
    const onToggle = jest.fn()
    const { getByRole } = render(
      <WorkoutTimerBar {...defaultProps} onToggleTimer={onToggle} />
    )
    fireEvent.press(getByRole('button'))
    expect(onToggle).toHaveBeenCalledTimes(1)
  })

  it('should calculate correct progress percentage', () => {
    const { getByTestId } = render(<WorkoutTimerBar {...defaultProps} />)
    const progressBar = getByTestId('progress-bar')
    // 5/12 = 41.67%
    expect(progressBar.props.style.width).toBe('41.666666666666664%')
  })

  it('should truncate long movement names', () => {
    const longName = 'Barbell Back Squat with Resistance Bands'
    const { getByText } = render(
      <WorkoutTimerBar {...defaultProps} currentMovementName={longName} />
    )
    const textElement = getByText(longName)
    expect(textElement.props.numberOfLines).toBe(1)
  })
})
```

---

## Files to Create

### New Files
- `components/workout/WorkoutTimerBar.tsx` - Main component
- `components/workout/__tests__/WorkoutTimerBar.test.tsx` - Unit tests

---

## Dependencies

### Internal
- `utils/design-tokens.ts` (STORY-002)
- Lucide React Native icons (`Clock`, `TrendingUp`, `Dumbbell`, `Play`, `Pause`)

### External
- `react-native` (core)
- `lucide-react-native` (already installed)

---

## Definition of Done

- [ ] Component file created and implements all required props
- [ ] Sticky positioning works (stays at top when scrolling)
- [ ] Timer displays correct MM:SS format
- [ ] Play/pause button toggles correctly
- [ ] Progress counter shows X/Y format
- [ ] Current movement name truncates if too long
- [ ] Progress bar width matches completion percentage
- [ ] Unit tests passing (8 test cases minimum)
- [ ] Test coverage ≥90%
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing
1. Import component into test screen
2. Pass mock props with varying values
3. Verify sticky positioning when scrolling
4. Toggle play/pause button, verify icon changes
5. Update completedSets, verify progress bar animates
6. Test with long movement names (truncation)

### Visual Regression
- Screenshot comparison with UX spec mockup
- Verify color scheme matches template-create
- Check spacing and alignment with design tokens

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sticky positioning doesn't work on Android | High | Test early, use `position: fixed` fallback |
| Progress bar animation causes frame drops | Medium | Use `LayoutAnimation` for performant updates |
| Long movement names break layout | Low | `numberOfLines={1}` with ellipsis truncation |

---

## Estimated Effort

- **Implementation:** 2 hours
- **Testing:** 1 hour
- **Code Review:** 30 minutes
- **Total:** ~3.5 hours

---

## Related Stories

- **Depends On:** STORY-002 (Design Tokens)
- **Blocks:** STORY-007 (Integration into workout detail screen)
- **Related:** STORY-013 (Timer pulse animation will enhance this component)

---

**Next:** STORY-004 (TrackingMovementCard Component)
