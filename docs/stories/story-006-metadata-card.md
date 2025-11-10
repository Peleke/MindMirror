# STORY-006: MetadataCard Component

**Story ID:** STORY-006
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1B - Core Components
**Priority:** Medium
**Points:** 1
**Status:** Ready
**Dependencies:** STORY-002 (Design Tokens)

---

## User Story

**As a** user viewing my workout details
**I want** a professional metadata card with icon-driven stats
**So that** I can quickly see workout summary information

---

## Acceptance Criteria

### Must Have
- [ ] Create inline `MetadataCard` component in `workout/[id].tsx`
- [ ] Display date with calendar icon (e.g., "Jan 9, 2025")
- [ ] Display elapsed time with clock icon (e.g., "00:00")
- [ ] Display movements/sets count with dumbbell icon (e.g., "3 • 12 sets")
- [ ] Vertical dividers between stats
- [ ] Collapsible description with Markdown rendering
- [ ] Rounded card with border and shadow
- [ ] Use design tokens from STORY-002

### Should Have
- [ ] Collapse description by default (expandable with button)
- [ ] Icon-driven design matching SummaryStatsHeader pattern
- [ ] Dark mode compatible

### Could Have
- [ ] Smooth expand/collapse animation
- [ ] Tap stats to see detailed breakdown

---

## Technical Specification

### Component Props
```typescript
interface MetadataCardProps {
  date: string  // ISO date string
  duration: number  // Seconds
  movementsCount: number
  setsCount: number
  description?: string
}
```

### Visual Layout
```
┌────────────────────────────────────────────┐
│ 📅 Jan 9, 2025 | ⏱️ 00:00 | 💪 3 • 12 sets │
│ [+ Description]                            │
│                                            │
│ "Full body strength training..."          │ ← Collapsed by default
└────────────────────────────────────────────┘
```

### Component Structure (Inline)
```typescript
// In workout/[id].tsx
import { Calendar, Clock, Dumbbell, ChevronDown, ChevronUp } from 'lucide-react-native'

function MetadataCard({
  date,
  duration,
  movementsCount,
  setsCount,
  description,
}: MetadataCardProps) {
  const [descriptionExpanded, setDescriptionExpanded] = useState(false)
  const formattedDate = formatDate(date)
  const formattedDuration = formatDuration(duration)

  return (
    <View style={styles.metadataCard}>
      {/* Stats Row */}
      <View style={styles.statsRow}>
        {/* Date */}
        <View style={styles.stat}>
          <Calendar size={14} color={colors.primary[600]} />
          <Text style={styles.statText}>{formattedDate}</Text>
        </View>

        <View style={styles.divider} />

        {/* Duration */}
        <View style={styles.stat}>
          <Clock size={14} color={colors.primary[600]} />
          <Text style={styles.statText}>{formattedDuration}</Text>
        </View>

        <View style={styles.divider} />

        {/* Movements & Sets */}
        <View style={styles.stat}>
          <Dumbbell size={14} color={colors.primary[600]} />
          <Text style={styles.statText}>
            {movementsCount} • {setsCount} sets
          </Text>
        </View>
      </View>

      {/* Description Toggle */}
      {description && (
        <>
          <TouchableOpacity
            style={styles.descriptionToggle}
            onPress={() => setDescriptionExpanded(!descriptionExpanded)}
          >
            <Text style={styles.descriptionToggleText}>
              {descriptionExpanded ? '- Hide' : '+ Show'} Description
            </Text>
            {descriptionExpanded ? (
              <ChevronUp size={14} color={colors.gray[600]} />
            ) : (
              <ChevronDown size={14} color={colors.gray[600]} />
            )}
          </TouchableOpacity>

          {descriptionExpanded && (
            <View style={styles.descriptionContent}>
              <Text style={styles.descriptionText}>{description}</Text>
            </View>
          )}
        </>
      )}
    </View>
  )
}

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const styles = StyleSheet.create({
  metadataCard: {
    backgroundColor: 'white',
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.gray[300],
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  statText: {
    ...typography.stats,
    color: colors.gray[600],
  },
  divider: {
    width: 1,
    height: 16,
    backgroundColor: colors.gray[300],
    marginHorizontal: spacing.sm,
  },
  descriptionToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray[300],
  },
  descriptionToggleText: {
    fontSize: 12,
    color: colors.primary[600],
    marginRight: spacing.xs,
  },
  descriptionContent: {
    marginTop: spacing.sm,
  },
  descriptionText: {
    fontSize: 14,
    color: colors.gray[600],
    lineHeight: 20,
  },
})
```

---

## Test Cases

### Component Tests (Inline in `workout/[id].test.tsx`)

```typescript
describe('MetadataCard', () => {
  const defaultProps = {
    date: '2025-01-09T10:00:00Z',
    duration: 0,
    movementsCount: 3,
    setsCount: 12,
    description: 'Full body strength training session',
  }

  it('should display formatted date', () => {
    const { getByText } = render(<MetadataCard {...defaultProps} />)
    expect(getByText('Jan 9, 2025')).toBeTruthy()
  })

  it('should display formatted duration', () => {
    const { getByText } = render(
      <MetadataCard {...defaultProps} duration={754} />
    )
    expect(getByText('12:34')).toBeTruthy()
  })

  it('should display movements and sets count', () => {
    const { getByText } = render(<MetadataCard {...defaultProps} />)
    expect(getByText('3 • 12 sets')).toBeTruthy()
  })

  it('should collapse description by default', () => {
    const { queryByText, getByText } = render(<MetadataCard {...defaultProps} />)
    expect(queryByText('Full body strength training session')).toBeNull()
    expect(getByText('+ Show Description')).toBeTruthy()
  })

  it('should expand description when toggle pressed', () => {
    const { getByText } = render(<MetadataCard {...defaultProps} />)
    fireEvent.press(getByText('+ Show Description'))
    expect(getByText('Full body strength training session')).toBeTruthy()
    expect(getByText('- Hide Description')).toBeTruthy()
  })

  it('should render dividers between stats', () => {
    const { getAllByTestId } = render(<MetadataCard {...defaultProps} />)
    const dividers = getAllByTestId('stat-divider')
    expect(dividers.length).toBe(2)  // Between 3 stats
  })
})
```

---

## Files to Modify

### Modified Files
- `app/(app)/workout/[id].tsx` - Add inline MetadataCard component

---

## Dependencies

### Internal
- `utils/design-tokens.ts` (STORY-002)
- Lucide React Native icons (`Calendar`, `Clock`, `Dumbbell`, `ChevronDown`, `ChevronUp`)

### External
- None (inline component using React Native core)

---

## Definition of Done

- [ ] Inline MetadataCard component created in `workout/[id].tsx`
- [ ] Date displays with calendar icon (formatted as "MMM D, YYYY")
- [ ] Duration displays with clock icon (formatted as "MM:SS")
- [ ] Movements/sets count displays with dumbbell icon
- [ ] Vertical dividers between stats
- [ ] Description collapses/expands on toggle
- [ ] Rounded card with border and shadow applied
- [ ] Unit tests passing (6 test cases minimum)
- [ ] TypeScript compiles with no errors
- [ ] Code reviewed and follows project conventions
- [ ] Committed to feature branch

---

## Testing Instructions

### Manual Testing
1. Render MetadataCard with sample props
2. Verify date formatting (e.g., "Jan 9, 2025")
3. Verify duration formatting (MM:SS)
4. Toggle description, verify expand/collapse
5. Test with missing description (hide toggle)

### Visual Regression
- Compare with UX spec mockup (metadata card design)
- Verify icons match template-create style
- Check spacing and dividers

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Date formatting varies by locale | Low | Use explicit `en-US` locale format |
| Description too long (overflows card) | Medium | Add `numberOfLines` prop for truncation |
| Icons misaligned with text | Low | Use flexbox with `alignItems: center` |

---

## Estimated Effort

- **Implementation:** 45 minutes
- **Testing:** 30 minutes
- **Code Review:** 15 minutes
- **Total:** ~1.5 hours

---

## Related Stories

- **Depends On:** STORY-002 (Design Tokens)
- **Blocks:** STORY-010 (Integration - add metadata card to screen header)
- **Related:** STORY-005 (SectionHeader for phase context)

---

**Next:** STORY-007 (Integration - WorkoutTimerBar)
