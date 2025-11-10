# STORY-005: SectionHeader Component

**Story ID:** STORY-005
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1B - Core Components
**Priority:** Medium
**Points:** 1
**Status:** Ready
**Dependencies:** STORY-002 (Design Tokens)

---

## User Story

**As a** user tracking my workout
**I want** clear visual section headers for workout phases
**So that** I can understand pacing context (warmup/workout/cooldown)

---

## Acceptance Criteria

### Must Have
- [ ] Create inline `SectionHeader` component in `workout/[id].tsx`
- [ ] Gradient background with indigo fade (`from-indigo-50 to-transparent`)
- [ ] Bold typography with letter-spacing
- [ ] Emoji icons for personality (🔥 Warmup, 💪 Workout, 😌 Cooldown)
- [ ] Extending horizontal line to the right
- [ ] Use design tokens from STORY-002

### Should Have
- [ ] Responsive width (full width on all screen sizes)
- [ ] Dark mode compatible gradient
- [ ] Semantic props for phase type

### Could Have
- [ ] Animation on first appearance (fade in)
- [ ] Different gradient colors per phase

---

## Technical Specification

### Component Props
```typescript
interface SectionHeaderProps {
  title: 'WARMUP' | 'WORKOUT' | 'COOLDOWN'
  icon: string  // Emoji
}
```

### Visual Layout
```
┌─────────────────────────────────────────────────┐
│ 🔥 WARMUP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ← Indigo gradient fade
└─────────────────────────────────────────────────┘
```

### Component Structure (Inline)
```typescript
// In workout/[id].tsx
function SectionHeader({ title, icon }: SectionHeaderProps) {
  return (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionHeaderContent}>
        <Text style={styles.sectionHeaderText}>
          {icon} {title}
        </Text>
        <View style={styles.sectionHeaderLine} />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  sectionHeader: {
    marginVertical: spacing.md,
  },
  sectionHeaderContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.primary[50],  // Gradient start
    borderRadius: borderRadius.md,
  },
  sectionHeaderText: {
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1.5,
    color: colors.primary[900],
    marginRight: spacing.sm,
  },
  sectionHeaderLine: {
    flex: 1,
    height: 2,
    backgroundColor: colors.primary[300],
  },
})
```

### Usage Pattern
```typescript
// In workout/[id].tsx render
<SectionHeader title="WARMUP" icon="🔥" />
{warmupMovements.map(...)}

<SectionHeader title="WORKOUT" icon="💪" />
{workoutMovements.map(...)}

<SectionHeader title="COOLDOWN" icon="😌" />
{cooldownMovements.map(...)}
```

---

## Test Cases

### Component Tests (Inline in `workout/[id].test.tsx`)

```typescript
describe('SectionHeader', () => {
  it('should display title with icon', () => {
    const { getByText } = render(<SectionHeader title="WARMUP" icon="🔥" />)
    expect(getByText('🔥 WARMUP')).toBeTruthy()
  })

  it('should render horizontal line', () => {
    const { getByTestId } = render(<SectionHeader title="WORKOUT" icon="💪" />)
    const line = getByTestId('section-header-line')
    expect(line.props.style.height).toBe(2)
  })

  it('should apply gradient background', () => {
    const { getByTestId } = render(<SectionHeader title="COOLDOWN" icon="😌" />)
    const container = getByTestId('section-header-content')
    expect(container.props.style.backgroundColor).toBe(colors.primary[50])
  })
})
```

---

## Files to Modify

### Modified Files
- `app/(app)/workout/[id].tsx` - Add inline SectionHeader component

---

## Dependencies

### Internal
- `utils/design-tokens.ts` (STORY-002)

### External
- None (inline component using React Native core)

---

## Definition of Done

- [ ] Inline SectionHeader component created in `workout/[id].tsx`
- [ ] Gradient background applied (indigo-50)
- [ ] Bold typography with letter-spacing
- [ ] Emoji icons display correctly
- [ ] Horizontal line extends to right edge
- [ ] Used in 3 places: WARMUP, WORKOUT, COOLDOWN sections
- [ ] Unit tests passing (3 test cases minimum)
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing
1. Render SectionHeader with each phase type
2. Verify gradient background color
3. Check text styling (bold, letter-spacing)
4. Verify emoji icons display correctly
5. Test on both iOS and Android

### Visual Regression
- Compare with UX spec mockup (section header design)
- Verify indigo-50 background matches template-create
- Check line color (indigo-300)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Emoji rendering varies by platform | Low | Test on iOS/Android, use consistent emoji set |
| Gradient not visible in dark mode | Medium | Test dark mode, adjust background color if needed |
| Line doesn't extend properly on small screens | Low | Use `flex: 1` for responsive width |

---

## Estimated Effort

- **Implementation:** 30 minutes
- **Testing:** 20 minutes
- **Code Review:** 10 minutes
- **Total:** ~1 hour

---

## Related Stories

- **Depends On:** STORY-002 (Design Tokens)
- **Blocks:** STORY-009 (Integration - add section headers to workout phases)
- **Related:** None

---

**Next:** STORY-006 (MetadataCard Component)
