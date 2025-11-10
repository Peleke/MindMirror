# STORY-009.5: Testing & Accessibility

**Epic:** EPIC-009 Workout Template Redesign
**Story Points:** 5
**Priority:** Critical Path
**Assignee:** TBD
**Status:** Ready for Development
**Depends On:** STORY-009.1, STORY-009.2, STORY-009.3, STORY-009.4

---

## User Story

**As a** QA engineer and accessibility specialist
**I want** comprehensive test coverage and WCAG AA compliance
**So that** we ship a high-quality, accessible feature to all users

---

## Acceptance Criteria

### Unit Test Coverage
- [ ] All new components have ≥80% test coverage
- [ ] Edge cases covered (delete only set, max values, etc.)
- [ ] State management tests (collapse persistence, set updates)
- [ ] Snapshot tests for visual regression

### Integration Test Coverage
- [ ] Full template creation flow (add 5 exercises, save)
- [ ] Quick entry flow (copy last set 10 times)
- [ ] Collapse/expand with persistence across restarts
- [ ] Summary stats update in real-time

### Accessibility (WCAG AA)
- [ ] All touch targets ≥44pt verified
- [ ] Color contrast ratios ≥4.5:1 for text
- [ ] Screen reader labels for all interactive elements
- [ ] Keyboard navigation works (web)
- [ ] Focus indicators visible
- [ ] No color-only information

### Performance
- [ ] Template with 50 sets renders in <500ms
- [ ] Rapid increment button taps (10/sec) handled smoothly
- [ ] Collapse animation <200ms
- [ ] No memory leaks during extended use

### Dark Mode
- [ ] All colors have dark mode variants
- [ ] Contrast ratios maintained in dark mode
- [ ] No white flashes during transitions

### Cross-Platform
- [ ] iOS testing (iPhone SE, iPhone 15 Pro Max)
- [ ] Android testing (Pixel 5, Galaxy S23)
- [ ] Both orientations (portrait + landscape)

---

## Testing Checklist

### Unit Tests

#### `SetEditorCard.test.tsx`
```typescript
describe('SetEditorCard', () => {
  it('should render all sets', () => { /* ... */ })
  it('should call onUpdateSet when input changes', () => { /* ... */ })
  it('should prevent deleting only set', () => { /* ... */ })
  it('should add set with previous values', () => { /* ... */ })
  it('should copy last set', () => { /* ... */ })
})
```

#### `IncrementButton.test.tsx`
```typescript
describe('IncrementButton', () => {
  it('should call onPress when tapped', () => { /* ... */ })
  it('should not call onPress when disabled', () => { /* ... */ })
  it('should show correct icon for direction', () => { /* ... */ })
})
```

#### `SummaryStatsHeader.test.tsx`
```typescript
describe('SummaryStatsHeader', () => {
  it('should calculate duration correctly', () => { /* ... */ })
  it('should update in real-time', () => { /* ... */ })
  it('should format stats correctly', () => { /* ... */ })
})
```

#### `EmptyStateCard.test.tsx`
```typescript
describe('EmptyStateCard', () => {
  it('should render template-level variant', () => { /* ... */ })
  it('should render block-level variant', () => { /* ... */ })
  it('should call onCTAPress', () => { /* ... */ })
})
```

#### `CollapsibleBlockSection.test.tsx`
```typescript
describe('CollapsibleBlockSection', () => {
  it('should toggle collapse state', () => { /* ... */ })
  it('should persist state to AsyncStorage', () => { /* ... */ })
  it('should hide children when collapsed', () => { /* ... */ })
})
```

### Integration Tests

#### `workout-template-create.integration.test.tsx`
```typescript
describe('Workout Template Create Flow', () => {
  it('should create template with 5 exercises end-to-end', async () => {
    const { getByText, getByPlaceholder } = render(<WorkoutTemplateCreate />)

    // Add title
    fireEvent.changeText(getByPlaceholder('Template name'), 'Push Day')

    // Add first exercise
    fireEvent.press(getByText('＋ Add Exercise'))
    fireEvent.changeText(getByPlaceholder('Search'), 'Bench Press')
    fireEvent.press(getByText('Bench Press'))

    // Add sets
    fireEvent.press(getByText('Add Set'))
    fireEvent.press(getByText('Copy Last Set'))

    // Verify stats
    expect(getByText(/1 exercise/i)).toBeTruthy()
    expect(getByText(/3 sets/i)).toBeTruthy()

    // Save
    fireEvent.press(getByText('Save Template'))
    await waitFor(() => expect(mockMutation).toHaveBeenCalled())
  })

  it('should persist collapse state across app restarts', async () => {
    const { getByText, unmount, rerender } = render(<WorkoutTemplateCreate />)

    // Collapse warmup block
    fireEvent.press(getByText(/Warmup/i))

    // Unmount (simulate app restart)
    unmount()

    // Remount
    rerender(<WorkoutTemplateCreate />)

    // Verify still collapsed
    expect(queryByText('Add Movement')).toBeNull()
  })
})
```

### Accessibility Tests

#### Manual Testing (Screen Readers)
- [ ] **iOS VoiceOver:**
  - Enable VoiceOver
  - Navigate template create screen
  - Verify all elements have labels
  - Test exercise addition flow
  - Test set editing flow

- [ ] **Android TalkBack:**
  - Enable TalkBack
  - Same tests as VoiceOver

#### Automated Accessibility Tests
```typescript
import { axe } from 'jest-axe'

describe('Accessibility', () => {
  it('should not have WCAG violations', async () => {
    const { container } = render(<WorkoutTemplateCreate />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have 44pt touch targets', () => {
    const { getAllByRole } = render(<SetEditorCard />)
    const buttons = getAllByRole('button')
    buttons.forEach(button => {
      const { height } = button.getBoundingClientRect()
      expect(height).toBeGreaterThanOrEqual(44)
    })
  })
})
```

### Performance Tests

#### Load Testing
```typescript
describe('Performance', () => {
  it('should render 50-set template in <500ms', async () => {
    const largeTemplate = generateTemplate(10, 5) // 10 exercises, 5 sets each

    const start = performance.now()
    const { findByText } = render(<WorkoutTemplateCreate data={largeTemplate} />)
    await findByText(/50 sets/i)
    const end = performance.now()

    expect(end - start).toBeLessThan(500)
  })

  it('should handle rapid increment button taps', () => {
    const { getByTestId } = render(<SetRow />)
    const incrementButton = getByTestId('increment-load-up')

    for (let i = 0; i < 20; i++) {
      fireEvent.press(incrementButton)
    }

    expect(mockOnUpdate).toHaveBeenCalledTimes(20)
  })
})
```

### Visual Regression Tests

#### Screenshot Tests
```typescript
import { screenshot } from '@/test-utils/screenshot'

describe('Visual Regression', () => {
  it('should match empty state snapshot', async () => {
    const { container } = render(<EmptyStateCard />)
    expect(await screenshot(container)).toMatchSnapshot()
  })

  it('should match collapsed block snapshot', async () => {
    const { container } = render(
      <CollapsibleBlockSection isCollapsed={true} />
    )
    expect(await screenshot(container)).toMatchSnapshot()
  })
})
```

---

## Accessibility Requirements

### Touch Targets
- [ ] All interactive elements ≥44pt height/width
- [ ] Spacing between targets ≥8pt
- [ ] No overlapping touch areas

### Color Contrast (WCAG AA)
- [ ] Body text: ≥4.5:1 contrast ratio
- [ ] Large text (18pt+): ≥3:1
- [ ] UI components: ≥3:1
- [ ] Test with tools: Stark, Color Oracle

### Screen Reader Support
```typescript
// Example labels
<TouchableOpacity
  accessible={true}
  accessibilityLabel="Add exercise to warmup block"
  accessibilityHint="Opens exercise search modal"
  accessibilityRole="button"
>
  <Text>＋ Add Movement</Text>
</TouchableOpacity>

<TextInput
  accessible={true}
  accessibilityLabel="Set 1 load in pounds"
  accessibilityHint="Enter weight for first set"
/>
```

### Focus Management
- [ ] Logical focus order (top to bottom, left to right)
- [ ] Focus visible (2pt border on focus)
- [ ] No focus traps
- [ ] Focus returns after modal close

---

## Performance Benchmarks

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Initial render | <300ms | 500ms |
| 50-set template render | <400ms | 600ms |
| Collapse animation | <200ms | 300ms |
| Increment button response | <50ms | 100ms |
| AsyncStorage write | <100ms | 200ms |

---

## Cross-Platform Testing Matrix

| Device | OS Version | Screen Size | Orientation |
|--------|------------|-------------|-------------|
| iPhone SE | iOS 17 | 4.7" | Portrait |
| iPhone 15 Pro Max | iOS 17 | 6.7" | Portrait + Landscape |
| Pixel 5 | Android 13 | 6.0" | Portrait |
| Galaxy S23 | Android 14 | 6.1" | Portrait + Landscape |

---

## Testing Tools

### Required
- Jest (unit tests)
- React Native Testing Library
- jest-axe (accessibility)
- @react-native-async-storage/async-storage (mocked)

### Recommended
- Detox (E2E tests)
- Maestro (mobile E2E)
- Percy (visual regression)
- Lighthouse (web accessibility)

---

## QA Checklist

### Functional Testing
- [ ] Add exercise via search
- [ ] Add 10 sets rapidly using "Copy Last Set"
- [ ] Edit load/reps/rest values
- [ ] Increment/decrement buttons work
- [ ] Delete set (with confirmation)
- [ ] Delete exercise (with confirmation)
- [ ] Collapse/expand blocks
- [ ] Summary stats update in real-time
- [ ] Save template successfully
- [ ] Cancel with unsaved changes (confirmation)

### Edge Cases
- [ ] Template with 0 exercises
- [ ] Exercise with 1 set (cannot delete)
- [ ] Exercise with 50+ sets
- [ ] Invalid input (letters in number field)
- [ ] Network error during save
- [ ] App restart during template creation

### Regression Testing
- [ ] Existing workout features still work
- [ ] No breaking changes to GraphQL mutations
- [ ] No performance degradation in other screens

---

## Definition of Done

- [ ] All unit tests passing (≥80% coverage)
- [ ] All integration tests passing
- [ ] Accessibility tests passing (WCAG AA)
- [ ] Performance benchmarks met
- [ ] Cross-platform testing complete
- [ ] Visual regression tests passing
- [ ] QA approval on TestFlight (iOS) and internal track (Android)
- [ ] No critical bugs
- [ ] No P1 accessibility issues

---

## Rollout Plan

### Phase 1: Internal Testing (Week 1)
- [ ] Deploy to TestFlight internal group
- [ ] Manual QA testing
- [ ] Fix critical bugs

### Phase 2: Beta Testing (Week 2)
- [ ] Deploy to external beta testers (20 coaches)
- [ ] Gather user feedback
- [ ] Monitor crash analytics

### Phase 3: Gradual Rollout (Week 3)
- [ ] 10% production rollout
- [ ] Monitor metrics (template creation time, crashes)
- [ ] 50% rollout if no issues
- [ ] 100% rollout

### Rollback Criteria
- Crash rate >5% increase
- Template creation time >3x slower
- Critical bugs affecting >10% users

---

## Success Metrics (Post-Launch)

### Technical Metrics
- Zero critical bugs in first week
- <5% increase in app crash rate
- <10% increase in API error rate

### User Metrics
- 50% reduction in template creation time
- 90%+ user satisfaction (survey)
- 40% increase in templates created per coach

### Accessibility Metrics
- Zero P1 accessibility issues
- 100% compliance with WCAG AA

---

## Related Files

- `__tests__/components/workout/` (all test files)
- `jest.config.js` (test configuration)
- `.detoxrc.js` (E2E test configuration)
