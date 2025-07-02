import { StyleSheet } from 'react-native'
import { colors, spacing, shadows } from '@/theme'

export const styles = StyleSheet.create({
  // Base styles
  base: {
    backgroundColor: colors.background.primary,
    borderRadius: 12,
  },

  // Variants
  default: {
    ...shadows.sm,
  },
  elevated: {
    ...shadows.lg,
  },
  outlined: {
    borderWidth: 1,
    borderColor: colors.border.medium,
    ...shadows.none,
  },

  // Padding variants
  paddingNone: {
    padding: 0,
  },
  paddingSmall: {
    padding: spacing.sm,
  },
  paddingMedium: {
    padding: spacing.md,
  },
  paddingLarge: {
    padding: spacing.lg,
  },
}) 