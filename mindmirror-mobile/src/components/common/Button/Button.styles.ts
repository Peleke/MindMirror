import { StyleSheet } from 'react-native'
import { colors, typography, spacing, shadows } from '@/theme'

export const styles = StyleSheet.create({
  // Base styles
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    flexDirection: 'row',
  },

  // Variants
  primary: {
    backgroundColor: colors.primary[600],
    ...shadows.sm,
  },
  secondary: {
    backgroundColor: colors.secondary[600],
    ...shadows.sm,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.medium,
  },
  ghost: {
    backgroundColor: 'transparent',
  },

  // Sizes
  small: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 32,
  },
  medium: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    minHeight: 44,
  },
  large: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    minHeight: 56,
  },

  // Text styles
  text: {
    fontFamily: typography.fonts.medium,
    textAlign: 'center',
  },

  // Variant text styles
  primaryText: {
    color: colors.text.inverse,
  },
  secondaryText: {
    color: colors.text.inverse,
  },
  outlineText: {
    color: colors.text.primary,
  },
  ghostText: {
    color: colors.primary[600],
  },

  // Size text styles
  smallText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
  },
  mediumText: {
    fontSize: typography.sizes.base,
    fontWeight: typography.weights.medium,
  },
  largeText: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
  },

  // Disabled styles
  disabled: {
    backgroundColor: colors.gray[200],
    borderColor: colors.gray[200],
    ...shadows.none,
  },
  disabledText: {
    color: colors.text.disabled,
  },
}) 