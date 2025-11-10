/**
 * Design Tokens Tests
 *
 * Validates design system constants and ensures values match UX spec.
 *
 * @see src/utils/design-tokens.ts
 * @see docs/stories/story-002-design-tokens.md
 */

import { colors, typography, spacing, borderRadius, shadows } from '../design-tokens'

describe('Design Tokens', () => {
  describe('Colors', () => {
    it('should have primary indigo palette', () => {
      expect(colors.primary[50]).toBe('#EEF2FF')
      expect(colors.primary[300]).toBe('#A5B4FC')
      expect(colors.primary[600]).toBe('#4F46E5')
      expect(colors.primary[900]).toBe('#312E81')
    })

    it('should have success green', () => {
      expect(colors.success[600]).toBe('#16A34A')
    })

    it('should have gray scale', () => {
      expect(colors.gray[300]).toBe('#D1D5DB')
      expect(colors.gray[600]).toBe('#4B5563')
      expect(colors.gray[900]).toBe('#111827')
    })

    it('should have white and black', () => {
      expect(colors.white).toBe('#FFFFFF')
      expect(colors.black).toBe('#000000')
    })
  })

  describe('Typography', () => {
    it('should have timer monospace font', () => {
      expect(typography.timer.fontFamily).toBe('monospace')
      expect(typography.timer.fontSize).toBe(18)
      expect(typography.timer.fontWeight).toBe('bold')
    })

    it('should have movement name semibold', () => {
      expect(typography.movementName.fontSize).toBe(16)
      expect(typography.movementName.fontWeight).toBe('600')
    })

    it('should have set data normal weight', () => {
      expect(typography.setData.fontSize).toBe(14)
      expect(typography.setData.fontWeight).toBe('normal')
    })

    it('should have stats with letter spacing', () => {
      expect(typography.stats.fontSize).toBe(12)
      expect(typography.stats.fontWeight).toBe('600')
      expect(typography.stats.letterSpacing).toBe(0.5)
    })
  })

  describe('Spacing', () => {
    it('should have consistent 4px scale', () => {
      expect(spacing.xs).toBe(4)
      expect(spacing.sm).toBe(8)
      expect(spacing.md).toBe(16)
      expect(spacing.lg).toBe(24)
      expect(spacing.xl).toBe(32)
    })

    it('should have card padding (Tailwind p-3 equivalent)', () => {
      expect(spacing.cardPadding).toBe(12)
    })
  })

  describe('Border Radius', () => {
    it('should have size variants', () => {
      expect(borderRadius.sm).toBe(6)
      expect(borderRadius.md).toBe(8)
      expect(borderRadius.lg).toBe(12)
    })

    it('should have full (circular) radius', () => {
      expect(borderRadius.full).toBe(9999)
    })
  })

  describe('Shadows', () => {
    it('should have small shadow with Android elevation', () => {
      expect(shadows.sm.shadowColor).toBe('#000')
      expect(shadows.sm.shadowOffset).toEqual({ width: 0, height: 1 })
      expect(shadows.sm.shadowOpacity).toBe(0.05)
      expect(shadows.sm.shadowRadius).toBe(2)
      expect(shadows.sm.elevation).toBe(1)
    })

    it('should have medium shadow with Android elevation', () => {
      expect(shadows.md.shadowColor).toBe('#000')
      expect(shadows.md.shadowOffset).toEqual({ width: 0, height: 2 })
      expect(shadows.md.shadowOpacity).toBe(0.1)
      expect(shadows.md.shadowRadius).toBe(4)
      expect(shadows.md.elevation).toBe(3)
    })
  })

  describe('Type Safety', () => {
    it('should export const assertions', () => {
      // TypeScript should treat these as literal types, not just objects
      // This test verifies the `as const` assertions work correctly
      const primaryColor: '#4F46E5' = colors.primary[600]
      expect(primaryColor).toBe('#4F46E5')
    })
  })
})
