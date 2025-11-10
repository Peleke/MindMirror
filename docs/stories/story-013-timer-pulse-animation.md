# STORY-013: Timer Pulse Animation (When Running)

**Story ID:** STORY-013
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 4 - Animations & Polish
**Priority:** Low (Nice-to-have polish)
**Points:** 1
**Status:** Ready
**Dependencies:** STORY-007 (WorkoutTimerBar Integration)

---

## User Story

**As a** user with an active workout timer
**I want** a subtle pulse animation on the timer
**So that** I have a visual indicator that the timer is running

---

## Acceptance Criteria

### Must Have
- [ ] Implement subtle scale pulse animation on timer text (1.0 → 1.05 → 1.0)
- [ ] Animation loops continuously while timer is running
- [ ] Duration: 1000ms per cycle
- [ ] Animation stops when timer paused
- [ ] Use React Native Animated API

### Should Have
- [ ] Smooth, subtle effect (not distracting)
- [ ] Animation runs at 60fps on device
- [ ] Clean start/stop transitions

### Could Have
- [ ] Color pulse (indigo → lighter → indigo)
- [ ] Sync pulse with seconds tick

---

## Technical Specification

### Animation Implementation
```typescript
// In WorkoutTimerBar.tsx
import { Animated, Easing } from 'react-native'

function WorkoutTimerBar({ isRunning, ... }) {
  const pulseAnim = useRef(new Animated.Value(1)).current

  useEffect(() => {
    if (isRunning) {
      // Start looping pulse animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.05,
            duration: 500,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1.0,
            duration: 500,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      ).start()
    } else {
      // Stop animation and reset scale
      pulseAnim.stopAnimation()
      pulseAnim.setValue(1)
    }

    // Cleanup on unmount
    return () => {
      pulseAnim.stopAnimation()
    }
  }, [isRunning, pulseAnim])

  return (
    <View style={styles.timerContainer}>
      <Clock size={16} color={colors.primary[600]} />
      <Animated.Text
        style={[
          styles.timerText,
          { transform: [{ scale: pulseAnim }] },
        ]}
      >
        {formattedTime}
      </Animated.Text>
      {/* ... */}
    </View>
  )
}
```

---

## Test Cases

```typescript
describe('WorkoutTimerBar - Timer Pulse Animation', () => {
  it('should start pulse animation when timer running', () => {
    render(<WorkoutTimerBar isRunning={true} {...props} />)

    expect(Animated.loop).toHaveBeenCalled()
  })

  it('should stop pulse animation when timer paused', () => {
    const { rerender } = render(
      <WorkoutTimerBar isRunning={true} {...props} />
    )

    // Pause timer
    rerender(<WorkoutTimerBar isRunning={false} {...props} />)

    expect(pulseAnim.stopAnimation).toHaveBeenCalled()
  })

  it('should reset scale to 1.0 when stopped', () => {
    const { rerender } = render(
      <WorkoutTimerBar isRunning={true} {...props} />
    )

    rerender(<WorkoutTimerBar isRunning={false} {...props} />)

    expect(pulseAnim.setValue).toHaveBeenCalledWith(1)
  })
})
```

---

## Definition of Done

- [ ] Pulse animation loops while timer running
- [ ] Animation stops when timer paused
- [ ] Subtle, non-distracting effect
- [ ] Runs at 60fps on device
- [ ] Unit tests passing (3 test cases)
- [ ] Committed to feature branch

---

## Estimated Effort: ~1 hour

---

**Next:** STORY-014 (Workout Completion Celebration)
