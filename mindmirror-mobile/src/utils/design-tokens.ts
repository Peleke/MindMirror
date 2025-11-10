/**
 * Design System Tokens
 *
 * Centralized design values matching workout-template-create visual design.
 * Use these tokens for all new components in workout detail refactor.
 *
 * @module utils/design-tokens
 * @see docs/stories/story-002-design-tokens.md
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

// =======================
// Color Palette
// =======================

export const colors = {
  primary: {
    50: '#EEF2FF', // Chip backgrounds, section header gradients
    300: '#A5B4FC', // Thumbnail borders, inactive states
    600: '#4F46E5', // Primary buttons, active accents
    900: '#312E81', // Dark mode chip text
  },
  success: {
    600: '#16A34A', // Checkmarks, progress bars, success states
  },
  gray: {
    300: '#D1D5DB', // Uncompleted checkboxes, dividers
    600: '#4B5563', // Secondary text, metadata
    900: '#111827', // Primary text (light mode)
  },
  white: '#FFFFFF',
  black: '#000000',
} as const

// =======================
// Typography
// =======================

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

// =======================
// Spacing
// =======================

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  cardPadding: 12, // 3 * 4 (Tailwind p-3)
} as const

// =======================
// Border Radius
// =======================

export const borderRadius = {
  sm: 6, // Inputs, small buttons
  md: 8, // Standard buttons
  lg: 12, // Cards, large containers
  full: 9999, // Circular thumbnails, checkboxes
} as const

// =======================
// Shadows
// =======================

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1, // Android elevation
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3, // Android elevation
  },
} as const

// =======================
// Type Exports
// =======================

export type ColorToken = typeof colors
export type TypographyToken = typeof typography
export type SpacingToken = typeof spacing
export type BorderRadiusToken = typeof borderRadius
export type ShadowToken = typeof shadows
