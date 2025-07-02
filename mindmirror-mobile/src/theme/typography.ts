import { Platform } from 'react-native'

export const typography = {
  fonts: {
    regular: Platform.select({
      ios: 'System',
      android: 'Roboto',
      default: 'System',
    }),
    medium: Platform.select({
      ios: 'System',
      android: 'Roboto-Medium',
      default: 'System',
    }),
    semibold: Platform.select({
      ios: 'System',
      android: 'Roboto-Medium',
      default: 'System',
    }),
    bold: Platform.select({
      ios: 'System',
      android: 'Roboto-Bold',
      default: 'System',
    }),
    monospace: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
  },
  
  sizes: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
    '6xl': 60,
  },
  
  lineHeights: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2,
  },
  
  weights: {
    normal: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  
  letterSpacing: {
    tight: -0.5,
    normal: 0,
    wide: 0.5,
    wider: 1,
    widest: 2,
  },
} as const

export type TypographyToken = typeof typography
export type FontFamily = keyof TypographyToken['fonts']
export type FontSize = keyof TypographyToken['sizes']
export type FontWeight = keyof TypographyToken['weights']

// Helper function to create text styles
export const createTextStyle = (
  size: FontSize = 'base',
  weight: FontWeight = 'normal',
  family: FontFamily = 'regular'
) => ({
  fontSize: typography.sizes[size],
  fontFamily: typography.fonts[family],
  fontWeight: typography.weights[weight],
  lineHeight: typography.sizes[size] * typography.lineHeights.normal,
}) 