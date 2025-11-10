/**
 * TrackingMovementCard Component Tests
 *
 * @module components/workout/__tests__/TrackingMovementCard
 * @see docs/stories/story-004-tracking-movement-card.md
 */

import React from 'react'
import { render, fireEvent } from '@testing-library/react-native'
import { TrackingMovementCard, TrackingMovementCardProps, Set } from '../TrackingMovementCard'

describe('TrackingMovementCard', () => {
  const mockSets: Set[] = [
    { setNumber: 1, value: '12', load: '135lb', rest: '90', completed: true },
    { setNumber: 2, value: '10', load: '145lb', rest: '90', completed: true },
    { setNumber: 3, value: '8', load: '155lb', rest: '90', completed: false },
  ]

  const defaultProps: TrackingMovementCardProps = {
    movementName: 'Barbell Back Squat',
    description: 'Keep chest up, knees tracking toes',
    videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    sets: mockSets,
    metricUnit: 'reps',
    onSetComplete: jest.fn(),
    onUpdateSet: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Movement Display', () => {
    it('should display movement name', () => {
      const { getByText } = render(<TrackingMovementCard {...defaultProps} />)
      expect(getByText('Barbell Back Squat')).toBeTruthy()
    })

    it('should display completion counter with correct progress', () => {
      const { getByText } = render(<TrackingMovementCard {...defaultProps} />)
      expect(getByText('2/3 sets complete')).toBeTruthy()
    })

    it('should update completion counter when sets change', () => {
      const allCompletedSets = mockSets.map((s) => ({ ...s, completed: true }))
      const { getByText } = render(
        <TrackingMovementCard {...defaultProps} sets={allCompletedSets} />
      )
      expect(getByText('3/3 sets complete')).toBeTruthy()
    })

    it('should handle zero completed sets', () => {
      const noCompletedSets = mockSets.map((s) => ({ ...s, completed: false }))
      const { getByText } = render(
        <TrackingMovementCard {...defaultProps} sets={noCompletedSets} />
      )
      expect(getByText('0/3 sets complete')).toBeTruthy()
    })
  })

  describe('YouTube Thumbnail', () => {
    it('should display YouTube thumbnail when videoUrl provided', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const thumbnail = getByTestId('movement-thumbnail')
      expect(thumbnail.props.source.uri).toContain('img.youtube.com')
    })

    it('should display play overlay when videoUrl provided', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      expect(getByTestId('play-overlay')).toBeTruthy()
    })

    it('should use placeholder when no videoUrl provided', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} videoUrl={undefined} />)
      const thumbnail = getByTestId('movement-thumbnail')
      expect(thumbnail.props.source.uri).toContain('placeholder')
    })

    it('should not show play overlay when no videoUrl', () => {
      const { queryByTestId } = render(
        <TrackingMovementCard {...defaultProps} videoUrl={undefined} />
      )
      expect(queryByTestId('play-overlay')).toBeNull()
    })
  })

  describe('Collapse/Expand Functionality', () => {
    it('should initially collapse description', () => {
      const { queryByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      expect(queryByTestId('movement-description')).toBeNull()
    })

    it('should expand description when toggle pressed', () => {
      const { getByTestId, queryByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      // Initially collapsed
      expect(queryByTestId('movement-description')).toBeNull()
      expect(getByTestId('chevron-down-icon')).toBeTruthy()

      // Expand
      fireEvent.press(getByTestId('collapse-toggle'))
      expect(getByTestId('movement-description')).toBeTruthy()
      expect(getByTestId('chevron-up-icon')).toBeTruthy()
    })

    it('should collapse description when toggle pressed again', () => {
      const { getByTestId, queryByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      // Expand
      fireEvent.press(getByTestId('collapse-toggle'))
      expect(getByTestId('movement-description')).toBeTruthy()

      // Collapse
      fireEvent.press(getByTestId('collapse-toggle'))
      expect(queryByTestId('movement-description')).toBeNull()
    })

    it('should not render description section if no description provided', () => {
      const { getByTestId, queryByTestId } = render(
        <TrackingMovementCard {...defaultProps} description={undefined} />
      )

      // Expand
      fireEvent.press(getByTestId('collapse-toggle'))

      // Should still not show description
      expect(queryByTestId('movement-description')).toBeNull()
    })
  })

  describe('Set Table Display', () => {
    it('should display correct metric unit label for reps', () => {
      const { getByText } = render(<TrackingMovementCard {...defaultProps} metricUnit="reps" />)
      expect(getByText('Reps')).toBeTruthy()
    })

    it('should display correct metric unit label for duration', () => {
      const { getByText } = render(
        <TrackingMovementCard {...defaultProps} metricUnit="duration" />
      )
      expect(getByText('Sec')).toBeTruthy()
    })

    it('should display correct metric unit label for distance', () => {
      const { getByText } = render(
        <TrackingMovementCard {...defaultProps} metricUnit="distance" />
      )
      expect(getByText('Dist')).toBeTruthy()
    })

    it('should render all set rows', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      expect(getByTestId('set-row-0')).toBeTruthy()
      expect(getByTestId('set-row-1')).toBeTruthy()
      expect(getByTestId('set-row-2')).toBeTruthy()
    })

    it('should display set numbers correctly', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      expect(getByTestId('set-number-0').children[0]).toBe('1')
      expect(getByTestId('set-number-1').children[0]).toBe('2')
      expect(getByTestId('set-number-2').children[0]).toBe('3')
    })
  })

  describe('Completion Checkmarks', () => {
    it('should show green checkmarks for completed sets', () => {
      const { getAllByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const checkCircles = getAllByTestId('check-circle-icon')
      expect(checkCircles.length).toBe(2) // Sets 1 and 2 are completed
    })

    it('should show gray circles for incomplete sets', () => {
      const { getAllByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const circles = getAllByTestId('circle-icon')
      expect(circles.length).toBe(1) // Set 3 is incomplete
    })

    it('should call onSetComplete when checkbox pressed', () => {
      const onSetComplete = jest.fn()
      const { getByTestId } = render(
        <TrackingMovementCard {...defaultProps} onSetComplete={onSetComplete} />
      )

      fireEvent.press(getByTestId('checkbox-0'))
      expect(onSetComplete).toHaveBeenCalledWith(0, false) // Toggle to incomplete
    })

    it('should toggle completion state correctly', () => {
      const onSetComplete = jest.fn()
      const { getByTestId } = render(
        <TrackingMovementCard {...defaultProps} onSetComplete={onSetComplete} />
      )

      // Press completed set checkbox (set 0 is completed)
      fireEvent.press(getByTestId('checkbox-0'))
      expect(onSetComplete).toHaveBeenCalledWith(0, false)

      // Press incomplete set checkbox (set 2 is incomplete)
      fireEvent.press(getByTestId('checkbox-2'))
      expect(onSetComplete).toHaveBeenCalledWith(2, true)
    })
  })

  describe('Completed Sets Styling', () => {
    it('should gray out completed set rows', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      const completedRow = getByTestId('set-row-0')
      const incompleteRow = getByTestId('set-row-2')

      // Check opacity style is applied to completed rows
      // Style is an array, so we need to check if setRowCompleted style is present
      const completedStyle = Array.isArray(completedRow.props.style)
        ? completedRow.props.style
        : [completedRow.props.style]

      const hasCompletedStyle = completedStyle.some((s: any) => s && s.opacity === 0.6)
      expect(hasCompletedStyle).toBe(true)

      // Incomplete row should not have opacity
      const incompleteStyle = Array.isArray(incompleteRow.props.style)
        ? incompleteRow.props.style
        : [incompleteRow.props.style]

      const hasOpacity = incompleteStyle.some((s: any) => s && s.opacity === 0.6)
      expect(hasOpacity).toBe(false)
    })
  })

  describe('Input Editability', () => {
    it('should disable inputs for completed sets', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      // Set 0 is completed - inputs should be disabled
      expect(getByTestId('input-value-0').props.editable).toBe(false)
      expect(getByTestId('input-load-0').props.editable).toBe(false)
      expect(getByTestId('input-rest-0').props.editable).toBe(false)
    })

    it('should enable inputs for incomplete sets', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      // Set 2 is incomplete - inputs should be enabled
      expect(getByTestId('input-value-2').props.editable).toBe(true)
      expect(getByTestId('input-load-2').props.editable).toBe(true)
      expect(getByTestId('input-rest-2').props.editable).toBe(true)
    })

    it('should call onUpdateSet when value input changes', () => {
      const onUpdateSet = jest.fn()
      const { getByTestId } = render(
        <TrackingMovementCard {...defaultProps} onUpdateSet={onUpdateSet} />
      )

      fireEvent.changeText(getByTestId('input-value-2'), '10')
      expect(onUpdateSet).toHaveBeenCalledWith(2, 'value', '10')
    })

    it('should call onUpdateSet when load input changes', () => {
      const onUpdateSet = jest.fn()
      const { getByTestId } = render(
        <TrackingMovementCard {...defaultProps} onUpdateSet={onUpdateSet} />
      )

      fireEvent.changeText(getByTestId('input-load-2'), '165lb')
      expect(onUpdateSet).toHaveBeenCalledWith(2, 'load', '165lb')
    })

    it('should call onUpdateSet when rest input changes', () => {
      const onUpdateSet = jest.fn()
      const { getByTestId } = render(
        <TrackingMovementCard {...defaultProps} onUpdateSet={onUpdateSet} />
      )

      fireEvent.changeText(getByTestId('input-rest-2'), '120')
      expect(onUpdateSet).toHaveBeenCalledWith(2, 'rest', '120')
    })

    it('should display current input values', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)

      expect(getByTestId('input-value-0').props.value).toBe('12')
      expect(getByTestId('input-load-0').props.value).toBe('135lb')
      expect(getByTestId('input-rest-0').props.value).toBe('90')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty sets array', () => {
      const { getByText } = render(<TrackingMovementCard {...defaultProps} sets={[]} />)
      expect(getByText('0/0 sets complete')).toBeTruthy()
    })

    it('should handle single set', () => {
      const singleSet = [mockSets[0]]
      const { getByTestId, getByText } = render(<TrackingMovementCard {...defaultProps} sets={singleSet} />)
      expect(getByTestId('set-row-0')).toBeTruthy()
      expect(getByText('1/1 sets complete')).toBeTruthy()
    })

    it('should handle very long movement names', () => {
      const longName = 'Barbell Back Squat with Resistance Bands and Heavy Load Protocol'
      const { getByText } = render(<TrackingMovementCard {...defaultProps} movementName={longName} />)
      expect(getByText(longName)).toBeTruthy()
    })

    it('should handle empty string inputs', () => {
      const emptySet: Set = { setNumber: 1, value: '', load: '', rest: '', completed: false }
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} sets={[emptySet]} />)
      expect(getByTestId('input-value-0').props.value).toBe('')
      expect(getByTestId('input-load-0').props.value).toBe('')
      expect(getByTestId('input-rest-0').props.value).toBe('')
    })
  })

  describe('Accessibility', () => {
    it('should have accessible button role for collapse toggle', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const toggle = getByTestId('collapse-toggle')
      expect(toggle.props.accessibilityRole).toBe('button')
    })

    it('should have accessible labels for checkboxes', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const checkbox = getByTestId('checkbox-0')
      expect(checkbox.props.accessibilityLabel).toContain('Set 1')
      expect(checkbox.props.accessibilityLabel).toContain('completed')
    })

    it('should have descriptive collapse toggle labels', () => {
      const { getByTestId } = render(<TrackingMovementCard {...defaultProps} />)
      const toggle = getByTestId('collapse-toggle')
      expect(toggle.props.accessibilityLabel).toBe('Expand details')

      fireEvent.press(toggle)
      expect(toggle.props.accessibilityLabel).toBe('Collapse details')
    })
  })
})
