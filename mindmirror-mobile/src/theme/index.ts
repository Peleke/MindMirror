import { colors } from './colors'
import { typography, createTextStyle } from './typography'
import { spacing, getSpacing, spacingHelpers } from './spacing'
import { shadows, getShadow, shadowHelpers } from './shadows'
import { animations, animationConfigs, getPlatformAnimation } from './animations'

// Re-export all theme modules
export { colors } from './colors'
export { typography, createTextStyle } from './typography'
export { spacing, getSpacing, spacingHelpers } from './spacing'
export { shadows, getShadow, shadowHelpers } from './shadows'
export { animations, animationConfigs, getPlatformAnimation } from './animations'

// Unified theme object
export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  animations,
} as const

export type Theme = typeof theme

// Helper function to get theme value
export const getThemeValue = <T extends keyof Theme>(
  themeKey: T,
  valueKey?: keyof Theme[T]
): any => {
  if (valueKey) {
    return theme[themeKey][valueKey as keyof Theme[T]]
  }
  return theme[themeKey]
}

// Common style combinations
export const commonStyles = {
  // Card styles
  card: {
    backgroundColor: colors.background.primary,
    borderRadius: 12,
    padding: spacing.md,
    ...shadows.md,
  },
  
  // Button styles
  button: {
    primary: {
      backgroundColor: colors.primary[600],
      paddingHorizontal: spacing.lg,
      paddingVertical: spacing.md,
      borderRadius: 8,
      ...shadows.sm,
    },
    secondary: {
      backgroundColor: colors.background.primary,
      borderWidth: 1,
      borderColor: colors.border.medium,
      paddingHorizontal: spacing.lg,
      paddingVertical: spacing.md,
      borderRadius: 8,
    },
  },
  
  // Text styles
  text: {
    heading: {
      ...createTextStyle('2xl', 'bold'),
      color: colors.text.primary,
    },
    body: {
      ...createTextStyle('base', 'normal'),
      color: colors.text.primary,
    },
    caption: {
      ...createTextStyle('sm', 'normal'),
      color: colors.text.secondary,
    },
  },
  
  // Container styles
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  
  // Safe area styles
  safeArea: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
} as const 