# STORY-014: Workout Completion Celebration Toast

**Story ID:** STORY-014
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 4 - Animations & Polish
**Priority:** Low (Nice-to-have polish)
**Points:** 1
**Status:** Ready
**Dependencies:** STORY-007, STORY-008 (Integration complete)

---

## User Story

**As a** user finishing my workout
**I want** a celebration toast when I complete all sets
**So that** I feel accomplished and recognized for my effort

---

## Acceptance Criteria

### Must Have
- [ ] Display toast notification when "Complete Workout" button pressed
- [ ] Toast message: "🎉 Workout Complete!"
- [ ] Auto-dismiss after 2 seconds
- [ ] Green background with white text
- [ ] Positioned near top of screen (below timer bar)

### Should Have
- [ ] Slide-in animation from top
- [ ] Fade-out animation on dismiss
- [ ] Rounded corners, shadow for polish

### Could Have
- [ ] Confetti animation (requires external library)
- [ ] Sound effect on completion
- [ ] Haptic feedback (strong impact)

---

## Technical Specification

### Toast Implementation (Simple Approach)
```typescript
// In workout/[id].tsx
function CelebrationToast({ show }: { show: boolean }) {
  const slideAnim = useRef(new Animated.Value(-100)).current
  const opacityAnim = useRef(new Animated.Value(0)).current

  useEffect(() => {
    if (show) {
      // Slide in and fade in
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: 80,  // Below timer bar
          duration: 300,
          easing: Easing.out(Easing.back(1.5)),
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start()

      // Auto-dismiss after 2 seconds
      setTimeout(() => {
        Animated.parallel([
          Animated.timing(slideAnim, {
            toValue: -100,
            duration: 200,
            useNativeDriver: true,
          }),
          Animated.timing(opacityAnim, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
          }),
        ]).start()
      }, 2000)
    }
  }, [show, slideAnim, opacityAnim])

  if (!show) return null

  return (
    <Animated.View
      style={[
        styles.toast,
        {
          transform: [{ translateY: slideAnim }],
          opacity: opacityAnim,
        },
      ]}
    >
      <Text style={styles.toastText}>🎉 Workout Complete!</Text>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  toast: {
    position: 'absolute',
    top: 0,
    left: spacing.md,
    right: spacing.md,
    zIndex: 100,
    backgroundColor: colors.success[600],
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    ...shadows.md,
  },
  toastText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
})
```

### Integration
```typescript
// In workout/[id].tsx
export default function WorkoutDetailScreen() {
  const [showCelebration, setShowCelebration] = useState(false)

  const handleCompleteWorkout = async () => {
    // Show celebration
    setShowCelebration(true)

    // Haptic feedback
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)

    // Wait for animation to complete
    await new Promise(resolve => setTimeout(resolve, 2500))

    // Navigate back to journal
    router.back()
  }

  return (
    <View>
      <CelebrationToast show={showCelebration} />
      {/* ... rest of screen ... */}
      <Button onPress={handleCompleteWorkout}>Complete Workout</Button>
    </View>
  )
}
```

---

## Test Cases

```typescript
describe('WorkoutDetailScreen - Completion Celebration', () => {
  it('should show toast when workout completed', () => {
    const { getByText, getByRole } = render(<WorkoutDetailScreen />)

    fireEvent.press(getByRole('button', { name: /complete workout/i }))

    expect(getByText('🎉 Workout Complete!')).toBeTruthy()
  })

  it('should auto-dismiss toast after 2 seconds', async () => {
    const { getByText, queryByText } = render(<WorkoutDetailScreen />)

    fireEvent.press(getByText('Complete Workout'))

    expect(getByText('🎉 Workout Complete!')).toBeTruthy()

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 2500))
    })

    expect(queryByText('🎉 Workout Complete!')).toBeNull()
  })

  it('should trigger haptic feedback on completion', async () => {
    const { getByText } = render(<WorkoutDetailScreen />)

    fireEvent.press(getByText('Complete Workout'))

    expect(Haptics.notificationAsync).toHaveBeenCalledWith(
      Haptics.NotificationFeedbackType.Success
    )
  })
})
```

---

## Definition of Done

- [ ] CelebrationToast component created
- [ ] Toast displays on workout completion
- [ ] Auto-dismisses after 2 seconds
- [ ] Slide-in/fade-out animations work smoothly
- [ ] Haptic feedback triggers
- [ ] Unit tests passing (3 test cases)
- [ ] Committed to feature branch

---

## Estimated Effort: ~1.5 hours

---

## Alternative: Confetti Library (Optional)
If desired, can use `react-native-confetti-cannon`:
```bash
npm install react-native-confetti-cannon
```

```typescript
import ConfettiCannon from 'react-native-confetti-cannon'

<ConfettiCannon
  count={200}
  origin={{ x: width / 2, y: 0 }}
  autoStart={showCelebration}
  fadeOut
/>
```

**Trade-off:** Adds dependency, but more impressive celebration effect.

---

**Epic Complete!** 🎉 All 14 user stories created and ready for implementation.
