/**
 * TrackingMovementCard Component
 *
 * Professional movement card with real YouTube thumbnails and completion tracking.
 * Displays sets with checkmarks, progress counter, and collapsible video/description.
 *
 * @module components/workout/TrackingMovementCard
 * @see docs/stories/story-004-tracking-movement-card.md
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

import React, { useState } from 'react'
import { View, Text, Image, TouchableOpacity, TextInput, StyleSheet } from 'react-native'
import { ChevronDown, ChevronUp, CheckCircle, Circle, Play } from 'lucide-react-native'
import { getYouTubeThumbnail } from '@/utils/youtube'
import { colors, spacing, borderRadius, shadows, typography } from '@/utils/design-tokens'

export interface Set {
  setNumber: number
  value: string // Reps, duration, or distance
  load: string // Weight or resistance
  rest: string // Rest time in seconds
  completed: boolean
}

export interface TrackingMovementCardProps {
  movementName: string
  description?: string
  videoUrl?: string
  sets: Set[]
  metricUnit: 'reps' | 'duration' | 'distance'
  onSetComplete: (setIndex: number, completed: boolean) => void
  onUpdateSet: (setIndex: number, field: 'value' | 'load' | 'rest', value: string) => void
}

export function TrackingMovementCard({
  movementName,
  description,
  videoUrl,
  sets,
  metricUnit,
  onSetComplete,
  onUpdateSet,
}: TrackingMovementCardProps) {
  const [collapsed, setCollapsed] = useState(true)
  const thumbnailUrl = videoUrl ? getYouTubeThumbnail(videoUrl) : null
  const completedCount = sets.filter((s) => s.completed).length
  const totalSets = sets.length

  // Determine metric unit label
  const metricLabel = metricUnit === 'reps' ? 'Reps' : metricUnit === 'duration' ? 'Sec' : 'Dist'

  return (
    <View style={styles.card}>
      {/* Header: Thumbnail + Movement Name + Collapse */}
      <View style={styles.header}>
        <View style={styles.thumbnailContainer}>
          <Image
            source={{
              uri: thumbnailUrl || 'https://via.placeholder.com/80/A5B4FC/FFFFFF?text=No+Video',
            }}
            style={styles.thumbnail}
            accessibilityRole="image"
            testID="movement-thumbnail"
          />
          {videoUrl && (
            <TouchableOpacity style={styles.playOverlay} testID="play-overlay">
              <Play size={20} color="white" fill="white" />
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.headerText}>
          <Text style={styles.movementName}>{movementName}</Text>
          <Text style={styles.progressCounter} testID="progress-counter">
            {completedCount}/{totalSets} sets complete
          </Text>
        </View>

        <TouchableOpacity
          onPress={() => setCollapsed(!collapsed)}
          accessibilityRole="button"
          accessibilityLabel={collapsed ? 'Expand details' : 'Collapse details'}
          testID="collapse-toggle"
        >
          {collapsed ? (
            <ChevronDown size={20} color={colors.gray[600]} testID="chevron-down-icon" />
          ) : (
            <ChevronUp size={20} color={colors.gray[600]} testID="chevron-up-icon" />
          )}
        </TouchableOpacity>
      </View>

      {/* Collapsible Description */}
      {!collapsed && description && (
        <View style={styles.descriptionContainer}>
          <Text style={styles.description} testID="movement-description">
            {description}
          </Text>
        </View>
      )}

      {/* Set Table */}
      <View style={styles.setTable}>
        {/* Table Header */}
        <View style={styles.tableHeader}>
          <Text style={[styles.tableHeaderText, styles.checkCol]}>✓</Text>
          <Text style={[styles.tableHeaderText, styles.setCol]}>#</Text>
          <Text style={[styles.tableHeaderText, styles.valueCol]}>{metricLabel}</Text>
          <Text style={[styles.tableHeaderText, styles.loadCol]}>Load</Text>
          <Text style={[styles.tableHeaderText, styles.restCol]}>Rest</Text>
        </View>

        {/* Set Rows */}
        {sets.map((set, index) => (
          <View
            key={index}
            style={[styles.setRow, set.completed && styles.setRowCompleted]}
            testID={`set-row-${index}`}
          >
            {/* Completion Checkbox */}
            <TouchableOpacity
              style={styles.checkCol}
              onPress={() => onSetComplete(index, !set.completed)}
              accessibilityRole="button"
              accessibilityLabel={`Set ${set.setNumber} ${set.completed ? 'completed' : 'incomplete'}`}
              testID={`checkbox-${index}`}
            >
              {set.completed ? (
                <CheckCircle size={20} color={colors.success[600]} testID="check-circle-icon" />
              ) : (
                <Circle size={20} color={colors.gray[300]} testID="circle-icon" />
              )}
            </TouchableOpacity>

            {/* Set Number */}
            <Text style={[styles.setNumber, styles.setCol]} testID={`set-number-${index}`}>
              {set.setNumber}
            </Text>

            {/* Value (Reps/Duration/Distance) */}
            <TextInput
              style={[styles.input, styles.valueCol, set.completed && styles.inputDisabled]}
              value={set.value}
              onChangeText={(value) => onUpdateSet(index, 'value', value)}
              keyboardType="numeric"
              editable={!set.completed}
              accessibilityRole="none"
              testID={`input-value-${index}`}
            />

            {/* Load */}
            <TextInput
              style={[styles.input, styles.loadCol, set.completed && styles.inputDisabled]}
              value={set.load}
              onChangeText={(value) => onUpdateSet(index, 'load', value)}
              editable={!set.completed}
              accessibilityRole="none"
              testID={`input-load-${index}`}
            />

            {/* Rest */}
            <TextInput
              style={[styles.input, styles.restCol, set.completed && styles.inputDisabled]}
              value={set.rest}
              onChangeText={(value) => onUpdateSet(index, 'rest', value)}
              keyboardType="numeric"
              editable={!set.completed}
              accessibilityRole="none"
              testID={`input-rest-${index}`}
            />
          </View>
        ))}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.gray[300],
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  thumbnailContainer: {
    position: 'relative',
    marginRight: spacing.sm,
  },
  thumbnail: {
    width: 60,
    height: 60,
    borderRadius: borderRadius.full,
    borderWidth: 2,
    borderColor: colors.primary[300],
  },
  playOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerText: {
    flex: 1,
  },
  movementName: {
    ...typography.movementName,
    color: colors.gray[900],
  },
  progressCounter: {
    fontSize: 12,
    color: colors.success[600],
    marginTop: 2,
  },
  descriptionContainer: {
    marginBottom: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray[300],
  },
  description: {
    fontSize: 14,
    color: colors.gray[600],
    lineHeight: 20,
  },
  setTable: {
    marginTop: spacing.sm,
  },
  tableHeader: {
    flexDirection: 'row',
    paddingBottom: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray[300],
  },
  tableHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.gray[600],
    textAlign: 'center',
  },
  setRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray[300],
  },
  setRowCompleted: {
    opacity: 0.6,
  },
  checkCol: { width: 30, alignItems: 'center', justifyContent: 'center' },
  setCol: { width: 30, textAlign: 'center' as const },
  valueCol: { width: 60 },
  loadCol: { width: 70 },
  restCol: { width: 60 },
  setNumber: {
    fontSize: 14,
    color: colors.gray[900],
  },
  input: {
    ...typography.setData,
    borderWidth: 1,
    borderColor: colors.gray[300],
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.xs,
    paddingVertical: 4,
    textAlign: 'center' as const,
    backgroundColor: colors.white,
  },
  inputDisabled: {
    backgroundColor: '#f9fafb', // Lighter background for disabled state
    color: colors.gray[600],
  },
})
