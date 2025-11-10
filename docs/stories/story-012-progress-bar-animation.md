# STORY-012: Progress Bar Smooth Fill Animation

**Story ID:** STORY-012
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 4 - Animations & Polish
**Priority:** Medium
**Points:** 2
**Status:** Ready
**Dependencies:** STORY-007 (WorkoutTimerBar Integration)

---

## User Story

**As a** user tracking my workout
**I want** a smooth animated progress bar that fills as I complete sets
**So that** I see visual momentum and clear progress tracking

---

## Acceptance Criteria

### Must Have
- [ ] Implement smooth width transition animation on progress bar
- [ ] Animation triggers when completedSets prop updates
- [ ] Duration: 400ms
- [ ] Easing: Ease-out curve for natural deceleration
- [ ] Use React Native Animated API

### Should Have
- [ ] Animation runs at 60fps on device
- [ ] Progress bar color matches design tokens (success green)
- [ ] Smooth animation even when multiple sets completed rapidly

### Could Have
- [ ] Pulse effect at milestone percentages (25%, 50%, 75%, 100%)
- [ ] Color gradient shift as progress increases

---

## Technical Specification

### Animation Implementation
```typescript
// In WorkoutTimerBar.tsx
import { Animated } from 'react-native'

function WorkoutTimerBar({ completedSets, totalSets, ... }) {
  const progressAnim = useRef(new Animated.Value(0)).current
  const targetPercentage = (completedSets / totalSets) * 100

  useEffect(() => {
    Animated.timing(progressAnim, {
      toValue: targetPercentage,
      duration: 400,
      easing: Easing.out(Easing.ease),
      useNativeDriver: false,  // Width animations require layout driver
    }).start()
  }, [targetPercentage, progressAnim])

  const progressWidthInterpolation = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  })

  return (
    <View style={styles.container}>
      {/* ... stats row ... */}

      {/* Animated Progress Bar */}
      <View style={styles.progressBarContainer}>
        <Animated.View
          style={[
            styles.progressBar,
            { width: progressWidthInterpolation },
          ]}
        />
      </View>
    </View>
  )
}
```

### Styling
```typescript
const styles = StyleSheet.create({
  progressBarContainer: {
    height: 3,
    backgroundColor: colors.gray[300],
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.success[600],
  },
})
```

---

## Test Cases

```typescript
describe('WorkoutTimerBar - Progress Bar Animation', () => {
  it('should animate progress bar width on completedSets update', () => {
    const { rerender } = render(
      <WorkoutTimerBar completedSets={2} totalSets={12} {...props} />
    )

    // Update completedSets
    rerender(<WorkoutTimerBar completedSets={3} totalSets={12} {...props} />)

    // Verify Animated.timing called with correct target
    expect(Animated.timing).toHaveBeenCalledWith(
      expect.any(Animated.Value),
      expect.objectContaining({
        toValue: 25,  // 3/12 = 25%
        duration: 400,
      })
    )
  })

  it('should calculate correct progress percentage', () => {
    const { getByTestId } = render(
      <WorkoutTimerBar completedSets={6} totalSets={12} {...props} />
    )
    const progressBar = getByTestId('progress-bar')

    // 6/12 = 50%
    expect(progressBar.props.style.width).toBe('50%')
  })

  it('should handle rapid completions smoothly', async () => {
    const { rerender } = render(
      <WorkoutTimerBar completedSets={0} totalSets={12} {...props} />
    )

    // Rapidly complete 5 sets
    for (let i = 1; i <= 5; i++) {
      rerender(<WorkoutTimerBar completedSets={i} totalSets={12} {...props} />)
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 50))
      })
    }

    // Verify final animation called
    expect(Animated.timing).toHaveBeenLastCalledWith(
      expect.any(Animated.Value),
      expect.objectContaining({ toValue: 41.67 })  // 5/12
    )
  })
})
```

---

## Definition of Done

- [ ] Progress bar animation implemented in WorkoutTimerBar
- [ ] Width transitions smoothly (400ms, ease-out)
- [ ] Animation updates when completedSets changes
- [ ] Runs at 60fps on physical device
- [ ] Unit tests passing (3 test cases)
- [ ] TypeScript compiles with no errors
- [ ] Committed to feature branch

---

## Estimated Effort: ~2 hours

---

**Next:** STORY-013 (Timer Pulse Animation)
