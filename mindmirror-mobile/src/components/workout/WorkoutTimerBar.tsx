/**
 * WorkoutTimerBar Component
 *
 * Sticky timer bar displaying elapsed time, progress, and current movement.
 * Always visible at the top of the workout detail screen for quick reference.
 *
 * @module components/workout/WorkoutTimerBar
 * @see docs/stories/story-003-workout-timer-bar.md
 * @see claudedocs/workout-detail-refactor-ux-spec.md
 */

import React from 'react'
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'
import { Clock, TrendingUp, Dumbbell, Play, Pause } from 'lucide-react-native'
import { colors, spacing, borderRadius, shadows, typography } from '@/utils/design-tokens'

export interface WorkoutTimerBarProps {
  elapsedSeconds: number
  isRunning: boolean
  completedSets: number
  totalSets: number
  currentMovementName: string
  onToggleTimer: () => void
}

/**
 * Formats elapsed time in seconds to MM:SS format
 * @param seconds - Total elapsed seconds (handles negative values by clamping to 0)
 * @returns Formatted time string (e.g., "12:34")
 */
function formatElapsedTime(seconds: number): string {
  // Defensive: clamp negative values to 0
  const safeSeconds = Math.max(0, seconds)
  const mins = Math.floor(safeSeconds / 60)
  const secs = safeSeconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

export function WorkoutTimerBar({
  elapsedSeconds,
  isRunning,
  completedSets,
  totalSets,
  currentMovementName,
  onToggleTimer,
}: WorkoutTimerBarProps) {
  const formattedTime = formatElapsedTime(elapsedSeconds)
  const progressPercentage = totalSets > 0 ? (completedSets / totalSets) * 100 : 0

  return (
    <View style={styles.container}>
      {/* Top bar with stats */}
      <View style={styles.statsRow}>
        {/* Timer */}
        <View style={styles.stat}>
          <Clock size={16} color={colors.primary[600]} />
          <Text style={styles.timerText}>{formattedTime}</Text>
          <TouchableOpacity
            onPress={onToggleTimer}
            style={styles.playButton}
            accessibilityRole="button"
            accessibilityLabel={isRunning ? 'Pause timer' : 'Play timer'}
          >
            {isRunning ? (
              <Pause size={16} color={colors.primary[600]} testID="pause-icon" />
            ) : (
              <Play size={16} color={colors.primary[600]} testID="play-icon" />
            )}
          </TouchableOpacity>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Progress */}
        <View style={styles.stat}>
          <TrendingUp size={16} color={colors.success[600]} />
          <Text style={styles.statText}>
            {completedSets}/{totalSets}
          </Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Current Movement */}
        <View style={[styles.stat, styles.movementStat]}>
          <Dumbbell size={16} color={colors.gray[600]} />
          <Text style={styles.movementText} numberOfLines={1}>
            {currentMovementName}
          </Text>
        </View>
      </View>

      {/* Progress bar */}
      <View style={styles.progressBarContainer}>
        <View
          style={[styles.progressBar, { width: `${progressPercentage}%` }]}
          testID="progress-bar"
        />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    position: 'sticky' as any, // TypeScript doesn't recognize 'sticky' but it works in RN
    top: 0,
    zIndex: 10,
    backgroundColor: colors.white,
    ...shadows.sm,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  movementStat: {
    flex: 1,
  },
  divider: {
    width: 1,
    height: 20,
    backgroundColor: colors.gray[300],
    marginHorizontal: spacing.sm,
  },
  timerText: {
    ...typography.timer,
    color: colors.primary[600],
  },
  statText: {
    ...typography.stats,
    color: colors.success[600],
  },
  movementText: {
    ...typography.stats,
    color: colors.gray[600],
    flex: 1,
  },
  playButton: {
    width: 28,
    height: 28,
    borderRadius: borderRadius.full,
    backgroundColor: colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressBarContainer: {
    height: 3,
    backgroundColor: colors.gray[300],
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.success[600],
  },
})
