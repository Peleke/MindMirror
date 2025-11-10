# STORY-002: Design System Tokens Setup

**Story ID:** STORY-002
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1A - Foundation & Utilities
**Priority:** High (Blocks all visual components)
**Points:** 1
**Status:** Ready

---

## User Story

**As a** developer implementing visual components
**I want** centralized design tokens matching template-create
**So that** all components have consistent colors, typography, and spacing

---

## Acceptance Criteria

### Must Have
- [ ] Create design token constants (colors, typography, spacing, shadows)
- [ ] Match template-create color scheme (indigo accents)
- [ ] Document all tokens with usage examples
- [ ] Export tokens for reuse across components
- [ ] TypeScript type definitions for token objects

### Should Have
- [ ] Dark mode color variants
- [ ] Semantic token names (e.g., `primary.600` not `indigo.600`)
- [ ] Inline code comments explaining usage context

### Could Have
- [ ] Design token visualization in Storybook
- [ ] Auto-sync with Tailwind config
- [ ] Figma integration for design handoff

---

## Technical Specification

### File Structure
```
utils/
  design-tokens.ts        # Main design token exports
  __tests__/
    design-tokens.test.ts # Validation tests
```

### Token Categories

#### 1. Color Palette
```typescript
export const colors = {
  primary: {
    50: '#EEF2FF',   // Indigo-50 (chip backgrounds)
    300: '#A5B4FC',  // Indigo-300 (borders, thumbnails)
    600: '#4F46E5',  // Indigo-600 (primary buttons, accents)
    900: '#312E81',  // Indigo-900 (dark mode chips)
  },
  success: {
    600: '#16A34A',  // Green-600 (completion checkmarks, progress)
  },
  gray: {
    300: '#D1D5DB',  // Uncompleted checkmarks
    600: '#4B5563',  // Secondary text
  },
} as const
```

#### 2. Typography
```typescript
export const typography = {
  timer: {
    fontSize: 18,
    fontFamily: 'monospace',
    fontWeight: 'bold' as const,
  },
  movementName: {
    fontSize: 16,
    fontWeight: '600' as const,
  },
  setData: {
    fontSize: 14,
    fontWeight: 'normal' as const,
  },
  stats: {
    fontSize: 12,
    fontWeight: '600' as const,
  },
} as const
```

#### 3. Spacing
```typescript
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  cardPadding: 12,  // p-3 equivalent
} as const
```

#### 4. Border Radius
```typescript
export const borderRadius = {
  sm: 6,   // rounded-md for inputs
  md: 8,   // rounded-lg for buttons
  lg: 12,  // rounded-xl for cards
  full: 9999,  // rounded-full for circular elements
} as const
```

#### 5. Shadows
```typescript
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,  // Android
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
} as const
```

---

## Implementation

### `utils/design-tokens.ts`
```typescript
/**
 * Design System Tokens
 *
 * Centralized design values matching workout-template-create visual design.
 * Use these tokens for all new components in workout detail refactor.
 *
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

// Color Palette
export const colors = {
  primary: {
    50: '#EEF2FF',   // Chip backgrounds, section header gradients
    300: '#A5B4FC',  // Thumbnail borders, inactive states
    600: '#4F46E5',  // Primary buttons, active accents
    900: '#312E81',  // Dark mode chip text
  },
  success: {
    600: '#16A34A',  // Checkmarks, progress bars, success states
  },
  gray: {
    300: '#D1D5DB',  // Uncompleted checkboxes, dividers
    600: '#4B5563',  // Secondary text, metadata
  },
} as const

// Typography
export const typography = {
  timer: {
    fontSize: 18,
    fontFamily: 'monospace',
    fontWeight: 'bold' as const,
  },
  movementName: {
    fontSize: 16,
    fontWeight: '600' as const,
  },
  setData: {
    fontSize: 14,
    fontWeight: 'normal' as const,
  },
  stats: {
    fontSize: 12,
    fontWeight: '600' as const,
    letterSpacing: 0.5,
  },
} as const

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  cardPadding: 12,  // 3 * 4 (Tailwind p-3)
} as const

// Border Radius
export const borderRadius = {
  sm: 6,   // Inputs, small buttons
  md: 8,   // Standard buttons
  lg: 12,  // Cards, large containers
  full: 9999,  // Circular thumbnails, checkboxes
} as const

// Shadows
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
} as const

// Type exports for strict typing
export type ColorToken = typeof colors
export type TypographyToken = typeof typography
export type SpacingToken = typeof spacing
export type BorderRadiusToken = typeof borderRadius
export type ShadowToken = typeof shadows
```

---

## Test Cases

### `utils/__tests__/design-tokens.test.ts`
```typescript
import { colors, typography, spacing, borderRadius, shadows } from '../design-tokens'

describe('Design Tokens', () => {
  describe('Colors', () => {
    it('should have primary indigo palette', () => {
      expect(colors.primary[600]).toBe('#4F46E5')
      expect(colors.primary[50]).toBe('#EEF2FF')
    })

    it('should have success green', () => {
      expect(colors.success[600]).toBe('#16A34A')
    })
  })

  describe('Typography', () => {
    it('should have timer monospace font', () => {
      expect(typography.timer.fontFamily).toBe('monospace')
      expect(typography.timer.fontSize).toBe(18)
    })

    it('should have movement name semibold', () => {
      expect(typography.movementName.fontWeight).toBe('600')
    })
  })

  describe('Spacing', () => {
    it('should have consistent scale', () => {
      expect(spacing.sm).toBe(8)
      expect(spacing.md).toBe(16)
      expect(spacing.cardPadding).toBe(12)
    })
  })

  describe('Shadows', () => {
    it('should have elevation for Android', () => {
      expect(shadows.sm.elevation).toBe(1)
      expect(shadows.md.elevation).toBe(3)
    })
  })
})
```

---

## Files to Create

### New Files
- `utils/design-tokens.ts` - Main token exports
- `utils/__tests__/design-tokens.test.ts` - Validation tests

---

## Dependencies

### Internal
- None (pure constants)

### External
- None

---

## Definition of Done

- [ ] `utils/design-tokens.ts` created with all 5 token categories
- [ ] TypeScript types exported for strict typing
- [ ] JSDoc comments added for all tokens
- [ ] Unit tests passing (5 test suites minimum)
- [ ] Code reviewed and follows project conventions
- [ ] Tokens match template-create color scheme exactly
- [ ] Committed to feature branch

---

## Usage Examples

### In Components
```typescript
import { colors, spacing, borderRadius, shadows } from '@/utils/design-tokens'

// WorkoutTimerBar styling
const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.primary[50],
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  timer: {
    color: colors.primary[600],
  },
})
```

### In TrackingMovementCard
```typescript
import { colors, borderRadius } from '@/utils/design-tokens'

const thumbnailStyle = {
  borderWidth: 2,
  borderColor: colors.primary[300],
  borderRadius: borderRadius.full,
}
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token values don't match template-create | High | Manual verification against reference file |
| Dark mode colors clash with light mode | Medium | Test on both themes before integration |
| TypeScript type inference fails | Low | Use `as const` assertion for all objects |

---

## Estimated Effort

- **Implementation:** 20 minutes
- **Testing:** 15 minutes
- **Code Review:** 10 minutes
- **Total:** ~45 minutes

---

## Related Stories

- **Blocks:** STORY-003, STORY-004, STORY-005, STORY-006 (all components need tokens)
- **Related:** STORY-001 (YouTube utility is also foundation)

---

**Next:** After completion, all visual components can be built using these tokens.
