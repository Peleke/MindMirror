/**
 * SectionHeader Component
 *
 * Visual section headers for workout phases (warmup/workout/cooldown).
 * Provides pacing context with gradient background and emoji icons.
 *
 * @module components/workout/SectionHeader
 * @see docs/stories/story-005-section-header.md
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { colors, spacing, borderRadius } from '@/utils/design-tokens'

export interface SectionHeaderProps {
  title: 'WARMUP' | 'WORKOUT' | 'COOLDOWN'
  icon: string // Emoji
}

export function SectionHeader({ title, icon }: SectionHeaderProps) {
  return (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionHeaderContent} testID="section-header-content">
        <Text style={styles.sectionHeaderText} testID="section-header-text">
          {icon} {title}
        </Text>
        <View style={styles.sectionHeaderLine} testID="section-header-line" />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  sectionHeader: {
    marginVertical: spacing.md,
  },
  sectionHeaderContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.primary[50], // Indigo gradient start
    borderRadius: borderRadius.md,
  },
  sectionHeaderText: {
    fontSize: 14,
    fontWeight: 'bold' as const,
    letterSpacing: 1.5,
    color: colors.primary[900],
    marginRight: spacing.sm,
  },
  sectionHeaderLine: {
    flex: 1,
    height: 2,
    backgroundColor: colors.primary[300],
  },
})
