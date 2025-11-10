/**
 * MetadataCard Component
 *
 * Professional metadata card with icon-driven stats for workout summary.
 * Displays date, duration, movements/sets count with collapsible description.
 *
 * @module components/workout/MetadataCard
 * @see docs/stories/story-006-metadata-card.md
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

import React, { useState } from 'react'
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'
import { Calendar, Clock, Dumbbell, ChevronDown, ChevronUp } from 'lucide-react-native'
import { colors, spacing, borderRadius, shadows, typography } from '@/utils/design-tokens'

export interface MetadataCardProps {
  date: string // ISO date string
  duration: number // Seconds
  movementsCount: number
  setsCount: number
  description?: string
}

/**
 * Formats ISO date string to "MMM D, YYYY" format
 * @param isoDate - ISO date string (e.g., "2025-01-09T10:00:00Z")
 * @returns Formatted date (e.g., "Jan 9, 2025")
 */
function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/**
 * Formats elapsed time in seconds to MM:SS format
 * @param seconds - Total elapsed seconds
 * @returns Formatted time string (e.g., "12:34")
 */
function formatDuration(seconds: number): string {
  const safeSeconds = Math.max(0, seconds)
  const mins = Math.floor(safeSeconds / 60)
  const secs = safeSeconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

export function MetadataCard({
  date,
  duration,
  movementsCount,
  setsCount,
  description,
}: MetadataCardProps) {
  const [descriptionExpanded, setDescriptionExpanded] = useState(false)
  const formattedDate = formatDate(date)
  const formattedDuration = formatDuration(duration)

  return (
    <View style={styles.metadataCard}>
      {/* Stats Row */}
      <View style={styles.statsRow}>
        {/* Date */}
        <View style={styles.stat}>
          <Calendar size={14} color={colors.primary[600]} />
          <Text style={styles.statText} testID="date-text">
            {formattedDate}
          </Text>
        </View>

        <View style={styles.divider} testID="stat-divider" />

        {/* Duration */}
        <View style={styles.stat}>
          <Clock size={14} color={colors.primary[600]} />
          <Text style={styles.statText} testID="duration-text">
            {formattedDuration}
          </Text>
        </View>

        <View style={styles.divider} testID="stat-divider" />

        {/* Movements & Sets */}
        <View style={styles.stat}>
          <Dumbbell size={14} color={colors.primary[600]} />
          <Text style={styles.statText} testID="movements-sets-text">
            {movementsCount} • {setsCount} sets
          </Text>
        </View>
      </View>

      {/* Description Toggle */}
      {description && (
        <>
          <TouchableOpacity
            style={styles.descriptionToggle}
            onPress={() => setDescriptionExpanded(!descriptionExpanded)}
            accessibilityRole="button"
            accessibilityLabel={descriptionExpanded ? 'Hide description' : 'Show description'}
            testID="description-toggle"
          >
            <Text style={styles.descriptionToggleText}>
              {descriptionExpanded ? '- Hide' : '+ Show'} Description
            </Text>
            {descriptionExpanded ? (
              <ChevronUp size={14} color={colors.gray[600]} />
            ) : (
              <ChevronDown size={14} color={colors.gray[600]} />
            )}
          </TouchableOpacity>

          {descriptionExpanded && (
            <View style={styles.descriptionContent}>
              <Text style={styles.descriptionText} testID="description-content">
                {description}
              </Text>
            </View>
          )}
        </>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  metadataCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.gray[300],
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap' as const,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  statText: {
    ...typography.stats,
    color: colors.gray[600],
  },
  divider: {
    width: 1,
    height: 16,
    backgroundColor: colors.gray[300],
    marginHorizontal: spacing.sm,
  },
  descriptionToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray[300],
  },
  descriptionToggleText: {
    fontSize: 12,
    color: colors.primary[600],
    marginRight: spacing.xs,
    flex: 1,
  },
  descriptionContent: {
    marginTop: spacing.sm,
  },
  descriptionText: {
    fontSize: 14,
    color: colors.gray[600],
    lineHeight: 20,
  },
})
