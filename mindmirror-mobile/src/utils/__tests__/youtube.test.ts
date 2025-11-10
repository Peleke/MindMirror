/**
 * YouTube Thumbnail Utility Tests
 *
 * @see src/utils/youtube.ts
 * @see docs/stories/story-001-youtube-thumbnail-utility.md
 */

import { getYouTubeThumbnail, getYouTubeThumbnailFallback } from '../youtube'

describe('getYouTubeThumbnail', () => {
  describe('Valid YouTube URLs', () => {
    it('should extract thumbnail from youtube.com/watch URL', () => {
      const url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })

    it('should extract thumbnail from youtu.be short URL', () => {
      const url = 'https://youtu.be/dQw4w9WgXcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })

    it('should extract thumbnail from youtube.com/embed URL', () => {
      const url = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })

    it('should handle URLs with query parameters', () => {
      const url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s&list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })

    it('should handle youtu.be URLs with query parameters', () => {
      const url = 'https://youtu.be/dQw4w9WgXcQ?t=30'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })
  })

  describe('Invalid URLs', () => {
    it('should return null for invalid YouTube URL', () => {
      const url = 'https://www.youtube.com/invalid'
      const result = getYouTubeThumbnail(url)

      expect(result).toBeNull()
    })

    it('should return null for non-YouTube URL', () => {
      const url = 'https://vimeo.com/123456789'
      const result = getYouTubeThumbnail(url)

      expect(result).toBeNull()
    })

    it('should return null for empty string', () => {
      const result = getYouTubeThumbnail('')

      expect(result).toBeNull()
    })

    it('should return null for null input', () => {
      const result = getYouTubeThumbnail(null as any)

      expect(result).toBeNull()
    })

    it('should return null for undefined input', () => {
      const result = getYouTubeThumbnail(undefined as any)

      expect(result).toBeNull()
    })

    it('should return null for non-string input', () => {
      const result = getYouTubeThumbnail(123 as any)

      expect(result).toBeNull()
    })
  })

  describe('Edge Cases', () => {
    it('should handle video IDs with hyphens and underscores', () => {
      const url = 'https://www.youtube.com/watch?v=dQw4-w9Wg_XcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4-w9Wg_XcQ/maxresdefault.jpg')
    })

    it('should handle youtube.com without www subdomain', () => {
      const url = 'https://youtube.com/watch?v=dQw4w9WgXcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })

    it('should handle http protocol (not https)', () => {
      const url = 'http://www.youtube.com/watch?v=dQw4w9WgXcQ'
      const result = getYouTubeThumbnail(url)

      expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg')
    })
  })
})

describe('getYouTubeThumbnailFallback', () => {
  it('should return hqdefault thumbnail for valid URL', () => {
    const url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    const result = getYouTubeThumbnailFallback(url)

    expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg')
  })

  it('should return hqdefault for youtu.be URL', () => {
    const url = 'https://youtu.be/dQw4w9WgXcQ'
    const result = getYouTubeThumbnailFallback(url)

    expect(result).toBe('https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg')
  })

  it('should return null for invalid URL', () => {
    const url = 'https://vimeo.com/123456'
    const result = getYouTubeThumbnailFallback(url)

    expect(result).toBeNull()
  })
})
