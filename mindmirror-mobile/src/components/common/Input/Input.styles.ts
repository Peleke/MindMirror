import { StyleSheet } from 'react-native'
import { colors, typography, spacing, shadows } from '@/theme'

export const styles = StyleSheet.create({
  // Container styles
  container: {
    marginBottom: spacing.md,
  },

  // Variants
  default: {
    // Default variant has no special styling
  },
  outlined: {
    // Outlined variant styling is handled in input styles
  },
  filled: {
    // Filled variant styling is handled in input styles
  },

  // Sizes
  small: {
    // Small size styling
  },
  medium: {
    // Medium size styling
  },
  large: {
    // Large size styling
  },

  // Label styles
  label: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.text.primary,
    marginBottom: spacing.xs,
    fontFamily: typography.fonts.medium,
  },

  // Input styles
  input: {
    borderWidth: 1,
    borderColor: colors.border.medium,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.background.primary,
    fontFamily: typography.fonts.regular,
    color: colors.text.primary,
  },

  // Variant input styles
  defaultInput: {
    // Default input styling
  },
  outlinedInput: {
    borderWidth: 2,
    borderColor: colors.border.medium,
  },
  filledInput: {
    backgroundColor: colors.background.secondary,
    borderColor: 'transparent',
  },

  // Size input styles
  smallInput: {
    paddingVertical: spacing.sm,
    fontSize: typography.sizes.sm,
    minHeight: 36,
  },
  mediumInput: {
    paddingVertical: spacing.md,
    fontSize: typography.sizes.base,
    minHeight: 44,
  },
  largeInput: {
    paddingVertical: spacing.lg,
    fontSize: typography.sizes.lg,
    minHeight: 52,
  },

  // Error styles
  error: {
    // Error container styling
  },
  errorInput: {
    borderColor: colors.error[500],
  },
  errorText: {
    fontSize: typography.sizes.xs,
    color: colors.error[600],
    marginTop: spacing.xs,
    fontFamily: typography.fonts.regular,
  },
}) 