export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 96,
  '5xl': 128,
} as const

export type SpacingToken = typeof spacing
export type SpacingKey = keyof SpacingToken

// Helper function to get spacing value
export const getSpacing = (key: SpacingKey): number => spacing[key]

// Common spacing combinations
export const spacingHelpers = {
  // Padding
  p: {
    xs: { padding: spacing.xs },
    sm: { padding: spacing.sm },
    md: { padding: spacing.md },
    lg: { padding: spacing.lg },
    xl: { padding: spacing.xl },
  },
  
  // Margin
  m: {
    xs: { margin: spacing.xs },
    sm: { margin: spacing.sm },
    md: { margin: spacing.md },
    lg: { margin: spacing.lg },
    xl: { margin: spacing.xl },
  },
  
  // Horizontal spacing
  px: {
    xs: { paddingHorizontal: spacing.xs },
    sm: { paddingHorizontal: spacing.sm },
    md: { paddingHorizontal: spacing.md },
    lg: { paddingHorizontal: spacing.lg },
    xl: { paddingHorizontal: spacing.xl },
  },
  
  py: {
    xs: { paddingVertical: spacing.xs },
    sm: { paddingVertical: spacing.sm },
    md: { paddingVertical: spacing.md },
    lg: { paddingVertical: spacing.lg },
    xl: { paddingVertical: spacing.xl },
  },
  
  // Vertical spacing
  mx: {
    xs: { marginHorizontal: spacing.xs },
    sm: { marginHorizontal: spacing.sm },
    md: { marginHorizontal: spacing.md },
    lg: { marginHorizontal: spacing.lg },
    xl: { marginHorizontal: spacing.xl },
  },
  
  my: {
    xs: { marginVertical: spacing.xs },
    sm: { marginVertical: spacing.sm },
    md: { marginVertical: spacing.md },
    lg: { marginVertical: spacing.lg },
    xl: { marginVertical: spacing.xl },
  },
} as const 