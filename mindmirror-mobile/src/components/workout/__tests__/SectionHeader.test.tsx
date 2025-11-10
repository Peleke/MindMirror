/**
 * SectionHeader Component Tests
 *
 * @module components/workout/__tests__/SectionHeader
 * @see docs/stories/story-005-section-header.md
 */

import React from 'react'
import { render } from '@testing-library/react-native'
import { SectionHeader } from '../SectionHeader'

describe('SectionHeader', () => {
  describe('Title Display', () => {
    it('should display WARMUP title with icon', () => {
      const { getByText } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      expect(getByText('🔥 WARMUP')).toBeTruthy()
    })

    it('should display WORKOUT title with icon', () => {
      const { getByText } = render(<SectionHeader title="WORKOUT" icon="💪" />)
      expect(getByText('💪 WORKOUT')).toBeTruthy()
    })

    it('should display COOLDOWN title with icon', () => {
      const { getByText } = render(<SectionHeader title="COOLDOWN" icon="🧘" />)
      expect(getByText('🧘 COOLDOWN')).toBeTruthy()
    })
  })

  describe('Structure and TestIDs', () => {
    it('should render section header content container', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      expect(getByTestId('section-header-content')).toBeTruthy()
    })

    it('should render section header text', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      const text = getByTestId('section-header-text')
      expect(text).toBeTruthy()
      expect(text.props.children).toEqual(['🔥', ' ', 'WARMUP'])
    })

    it('should render section header line', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      expect(getByTestId('section-header-line')).toBeTruthy()
    })
  })

  describe('Styling', () => {
    it('should have gradient background on content container', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      const content = getByTestId('section-header-content')

      const style = Array.isArray(content.props.style)
        ? content.props.style.flat()
        : [content.props.style]

      const hasGradientBg = style.some((s: any) => s && s.backgroundColor === '#EEF2FF')
      expect(hasGradientBg).toBe(true)
    })

    it('should have bold uppercase text', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      const text = getByTestId('section-header-text')

      const style = Array.isArray(text.props.style)
        ? text.props.style.flat()
        : [text.props.style]

      const hasBold = style.some((s: any) => s && s.fontWeight === 'bold')
      expect(hasBold).toBe(true)
    })

    it('should have horizontal line with correct styling', () => {
      const { getByTestId } = render(<SectionHeader title="WARMUP" icon="🔥" />)
      const line = getByTestId('section-header-line')

      const style = Array.isArray(line.props.style)
        ? line.props.style.flat()
        : [line.props.style]

      const hasFlex1 = style.some((s: any) => s && s.flex === 1)
      const hasHeight = style.some((s: any) => s && s.height === 2)

      expect(hasFlex1).toBe(true)
      expect(hasHeight).toBe(true)
    })
  })

  describe('Edge Cases', () => {
    it('should handle emoji icons correctly', () => {
      const emojis = ['🔥', '💪', '🧘', '🏃', '🤸']

      emojis.forEach((emoji) => {
        const { getByText } = render(<SectionHeader title="WARMUP" icon={emoji} />)
        expect(getByText(`${emoji} WARMUP`)).toBeTruthy()
      })
    })

    it('should handle multiple word emojis', () => {
      const { getByText } = render(<SectionHeader title="WARMUP" icon="🔥💪" />)
      expect(getByText('🔥💪 WARMUP')).toBeTruthy()
    })
  })
})
