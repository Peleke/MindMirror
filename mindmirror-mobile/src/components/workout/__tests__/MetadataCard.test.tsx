/**
 * MetadataCard Component Tests
 *
 * @module components/workout/__tests__/MetadataCard
 * @see docs/stories/story-006-metadata-card.md
 */

import React from 'react'
import { render, fireEvent } from '@testing-library/react-native'
import { MetadataCard, MetadataCardProps } from '../MetadataCard'

describe('MetadataCard', () => {
  const defaultProps: MetadataCardProps = {
    date: '2025-01-09T10:00:00Z',
    duration: 3661, // 1 hour, 1 minute, 1 second
    movementsCount: 5,
    setsCount: 15,
    description: 'Focus on form and breathing',
  }

  describe('Stats Display', () => {
    it('should display formatted date', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)
      const dateText = getByTestId('date-text')
      expect(dateText.props.children).toBe('Jan 9, 2025')
    })

    it('should display formatted duration in MM:SS', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)
      const durationText = getByTestId('duration-text')
      expect(durationText.props.children).toBe('61:01') // 61 minutes, 1 second
    })

    it('should display movements and sets count', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)
      const movementsSetsText = getByTestId('movements-sets-text')
      expect(movementsSetsText.props.children).toEqual([5, ' • ', 15, ' sets'])
    })

    it('should render stat dividers', () => {
      const { getAllByTestId } = render(<MetadataCard {...defaultProps} />)
      const dividers = getAllByTestId('stat-divider')
      expect(dividers.length).toBe(2) // Two dividers between three stats
    })
  })

  describe('Date Formatting', () => {
    it('should format different dates correctly', () => {
      const testDates = [
        { input: '2025-01-09T12:00:00Z', expected: 'Jan 9, 2025' },
        { input: '2024-12-25T12:00:00Z', expected: 'Dec 25, 2024' },
        { input: '2025-07-04T12:30:00Z', expected: 'Jul 4, 2025' },
      ]

      testDates.forEach(({ input, expected }) => {
        const { getByTestId } = render(<MetadataCard {...defaultProps} date={input} />)
        expect(getByTestId('date-text').props.children).toBe(expected)
      })
    })
  })

  describe('Duration Formatting', () => {
    it('should format zero seconds as 00:00', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={0} />)
      expect(getByTestId('duration-text').props.children).toBe('00:00')
    })

    it('should format seconds without minutes', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={45} />)
      expect(getByTestId('duration-text').props.children).toBe('00:45')
    })

    it('should format minutes without extra seconds', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={180} />)
      expect(getByTestId('duration-text').props.children).toBe('03:00')
    })

    it('should format hours correctly (>60 minutes)', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={7200} />)
      expect(getByTestId('duration-text').props.children).toBe('120:00') // 120 minutes
    })

    it('should handle single-digit minutes and seconds', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={65} />)
      expect(getByTestId('duration-text').props.children).toBe('01:05')
    })

    it('should handle negative duration safely', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} duration={-100} />)
      expect(getByTestId('duration-text').props.children).toBe('00:00') // Should clamp to 0
    })
  })

  describe('Movements and Sets Count', () => {
    it('should display zero movements', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} movementsCount={0} />)
      const text = getByTestId('movements-sets-text')
      expect(text.props.children).toEqual([0, ' • ', 15, ' sets'])
    })

    it('should display single movement', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} movementsCount={1} />)
      const text = getByTestId('movements-sets-text')
      expect(text.props.children).toEqual([1, ' • ', 15, ' sets'])
    })

    it('should display large movement count', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} movementsCount={20} />)
      const text = getByTestId('movements-sets-text')
      expect(text.props.children).toEqual([20, ' • ', 15, ' sets'])
    })

    it('should display zero sets', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} setsCount={0} />)
      const text = getByTestId('movements-sets-text')
      expect(text.props.children).toEqual([5, ' • ', 0, ' sets'])
    })
  })

  describe('Description Toggle', () => {
    it('should initially hide description', () => {
      const { queryByTestId } = render(<MetadataCard {...defaultProps} />)
      expect(queryByTestId('description-content')).toBeNull()
    })

    it('should show description when toggle pressed', () => {
      const { getByTestId, queryByTestId } = render(<MetadataCard {...defaultProps} />)

      // Initially hidden
      expect(queryByTestId('description-content')).toBeNull()

      // Press toggle
      fireEvent.press(getByTestId('description-toggle'))

      // Now visible
      expect(getByTestId('description-content')).toBeTruthy()
      expect(getByTestId('description-content').props.children).toBe('Focus on form and breathing')
    })

    it('should hide description when toggle pressed again', () => {
      const { getByTestId, queryByTestId } = render(<MetadataCard {...defaultProps} />)

      // Expand
      fireEvent.press(getByTestId('description-toggle'))
      expect(getByTestId('description-content')).toBeTruthy()

      // Collapse
      fireEvent.press(getByTestId('description-toggle'))
      expect(queryByTestId('description-content')).toBeNull()
    })

    it('should not render description toggle if no description provided', () => {
      const { queryByTestId } = render(<MetadataCard {...defaultProps} description={undefined} />)
      expect(queryByTestId('description-toggle')).toBeNull()
    })

    it('should not render description toggle for empty string', () => {
      const { queryByTestId } = render(<MetadataCard {...defaultProps} description="" />)
      expect(queryByTestId('description-toggle')).toBeNull()
    })

    it('should display correct toggle text when collapsed', () => {
      const { getByText } = render(<MetadataCard {...defaultProps} />)
      expect(getByText('+ Show Description')).toBeTruthy()
    })

    it('should display correct toggle text when expanded', () => {
      const { getByTestId, getByText } = render(<MetadataCard {...defaultProps} />)

      fireEvent.press(getByTestId('description-toggle'))

      expect(getByText('- Hide Description')).toBeTruthy()
    })
  })

  describe('Accessibility', () => {
    it('should have accessible button role for description toggle', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)
      const toggle = getByTestId('description-toggle')
      expect(toggle.props.accessibilityRole).toBe('button')
    })

    it('should have accessible label for collapsed state', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)
      const toggle = getByTestId('description-toggle')
      expect(toggle.props.accessibilityLabel).toBe('Show description')
    })

    it('should have accessible label for expanded state', () => {
      const { getByTestId } = render(<MetadataCard {...defaultProps} />)

      fireEvent.press(getByTestId('description-toggle'))

      const toggle = getByTestId('description-toggle')
      expect(toggle.props.accessibilityLabel).toBe('Hide description')
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long descriptions', () => {
      const longDescription = 'This is a very long description '.repeat(20)
      const { getByTestId } = render(<MetadataCard {...defaultProps} description={longDescription} />)

      fireEvent.press(getByTestId('description-toggle'))

      expect(getByTestId('description-content').props.children).toBe(longDescription)
    })

    it('should handle multi-line descriptions', () => {
      const multiLine = 'Line 1\nLine 2\nLine 3'
      const { getByTestId } = render(<MetadataCard {...defaultProps} description={multiLine} />)

      fireEvent.press(getByTestId('description-toggle'))

      expect(getByTestId('description-content').props.children).toBe(multiLine)
    })

    it('should handle special characters in description', () => {
      const specialChars = 'Focus on form & breathing! 💪 @#$%'
      const { getByTestId } = render(<MetadataCard {...defaultProps} description={specialChars} />)

      fireEvent.press(getByTestId('description-toggle'))

      expect(getByTestId('description-content').props.children).toBe(specialChars)
    })
  })
})
