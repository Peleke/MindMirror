import { Platform } from 'react-native'
import { colors } from './colors'

export const shadows = {
  none: {
    shadowColor: 'transparent',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  
  sm: {
    shadowColor: colors.shadow.light,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: Platform.OS === 'ios' ? 0.05 : 0.1,
    shadowRadius: 2,
    elevation: Platform.OS === 'android' ? 1 : 0,
  },
  
  md: {
    shadowColor: colors.shadow.medium,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: Platform.OS === 'ios' ? 0.1 : 0.15,
    shadowRadius: 4,
    elevation: Platform.OS === 'android' ? 3 : 0,
  },
  
  lg: {
    shadowColor: colors.shadow.medium,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: Platform.OS === 'ios' ? 0.15 : 0.2,
    shadowRadius: 8,
    elevation: Platform.OS === 'android' ? 6 : 0,
  },
  
  xl: {
    shadowColor: colors.shadow.dark,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: Platform.OS === 'ios' ? 0.2 : 0.25,
    shadowRadius: 16,
    elevation: Platform.OS === 'android' ? 12 : 0,
  },
  
  '2xl': {
    shadowColor: colors.shadow.dark,
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: Platform.OS === 'ios' ? 0.25 : 0.3,
    shadowRadius: 24,
    elevation: Platform.OS === 'android' ? 16 : 0,
  },
} as const

export type ShadowToken = typeof shadows
export type ShadowKey = keyof ShadowToken

// Helper function to get shadow style
export const getShadow = (key: ShadowKey) => shadows[key]

// Common shadow combinations
export const shadowHelpers = {
  card: shadows.md,
  button: shadows.sm,
  modal: shadows.xl,
  floating: shadows.lg,
} as const 