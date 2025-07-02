import { StyleSheet } from 'react-native'
import { colors, typography, spacing } from '@/theme'

export const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
  },
  screen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background.primary,
  },
  text: {
    marginTop: spacing.md,
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    fontFamily: typography.fonts.regular,
    textAlign: 'center',
  },
}) 