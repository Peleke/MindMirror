# STORY-011: Checkmark Bounce Animation (Set Completion)

**Story ID:** STORY-011
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 4 - Animations & Polish
**Priority:** Medium
**Points:** 2
**Status:** Ready
**Dependencies:** STORY-008 (TrackingMovementCard Integration)

---

## User Story

**As a** user completing sets during my workout
**I want** a satisfying bounce animation when I check off a set
**So that** I feel motivated and get immediate feedback

---

## Acceptance Criteria

### Must Have
- [ ] Implement spring bounce animation on CheckCircle icon (scale 1.0 → 1.3 → 1.0)
- [ ] Animation triggers when checkbox pressed to complete set
- [ ] Duration: 300ms total
- [ ] Use React Native Animated API (built-in, no external dependencies)
- [ ] Smooth easing curve (spring physics)

### Should Have
- [ ] Animation only on completion (not on un-checking)
- [ ] Haptic feedback on completion (iOS/Android)
- [ ] Animation runs at 60fps on device

### Could Have
- [ ] Color transition animation (gray → green)
- [ ] Slight rotation during bounce
- [ ] Customizable animation parameters

---

## Technical Specification

### Animation Implementation
```typescript
// In TrackingMovementCard.tsx
import { Animated } from 'react-native'
import * as Haptics from 'expo-haptics'

function TrackingMovementCard({ ... }) {
  // Animation state for each set
  const scaleAnims = useRef(
    sets.map(() => new Animated.Value(1))
  ).current

  const handleSetComplete = useCallback((setIndex: number, completed: boolean) => {
    onSetComplete(setIndex, completed)

    // Only animate on completion (not un-checking)
    if (completed) {
      // Haptic feedback
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)

      // Bounce animation
      Animated.sequence([
        Animated.spring(scaleAnims[setIndex], {
          toValue: 1.3,
          speed: 50,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnims[setIndex], {
          toValue: 1.0,
          speed: 50,
          useNativeDriver: true,
        }),
      ]).start()
    } else {
      // Reset scale if un-checking
      scaleAnims[setIndex].setValue(1)
    }
  }, [onSetComplete, scaleAnims])

  return (
    <View>
      {sets.map((set, index) => (
        <View key={index} style={styles.setRow}>
          <TouchableOpacity onPress={() => handleSetComplete(index, !set.completed)}>
            <Animated.View style={{ transform: [{ scale: scaleAnims[index] }] }}>
              {set.completed ? (
                <CheckCircle size={20} color={colors.success[600]} />
              ) : (
                <Circle size={20} color={colors.gray[300]} />
              )}
            </Animated.View>
          </TouchableOpacity>
          {/* ... set inputs ... */}
        </View>
      ))}
    </View>
  )
}
```

### Animation Parameters
```typescript
const BOUNCE_CONFIG = {
  scaleUp: {
    toValue: 1.3,
    speed: 50,
    useNativeDriver: true,
  },
  scaleDown: {
    toValue: 1.0,
    speed: 50,
    useNativeDriver: true,
  },
}
```

---

## Test Cases

```typescript
describe('TrackingMovementCard - Checkmark Bounce Animation', () => {
  it('should trigger bounce animation on set completion', () => {
    const { getAllByRole } = render(<TrackingMovementCard {...props} />)
    const checkbox = getAllByRole('button')[0]

    // Complete set
    fireEvent.press(checkbox)

    // Verify animation started (Animated.sequence called)
    expect(Animated.sequence).toHaveBeenCalled()
  })

  it('should not animate when un-checking set', () => {
    const propsWithCompleted = {
      ...props,
      sets: [{ ...props.sets[0], completed: true }],
    }
    const { getAllByRole } = render(<TrackingMovementCard {...propsWithCompleted} />)

    // Un-check set
    fireEvent.press(getAllByRole('button')[0])

    // Verify no animation (just reset)
    expect(Animated.sequence).not.toHaveBeenCalled()
  })

  it('should trigger haptic feedback on completion', () => {
    const { getAllByRole } = render(<TrackingMovementCard {...props} />)

    fireEvent.press(getAllByRole('button')[0])

    expect(Haptics.impactAsync).toHaveBeenCalledWith(
      Haptics.ImpactFeedbackStyle.Medium
    )
  })
})
```

---

## Definition of Done

- [ ] Bounce animation implemented in TrackingMovementCard
- [ ] Animation triggers only on set completion (not un-checking)
- [ ] Haptic feedback works on iOS and Android
- [ ] Animation runs smoothly at 60fps on physical device
- [ ] Unit tests passing (3 test cases)
- [ ] TypeScript compiles with no errors
- [ ] Committed to feature branch

---

## Estimated Effort: ~2 hours

---

**Next:** STORY-012 (Progress Bar Smooth Fill Animation)
