/**
 * YouTube Thumbnail Extraction Utility
 *
 * Extracts YouTube video ID from URL and returns thumbnail URL.
 * Supports multiple YouTube URL formats for maximum compatibility.
 *
 * @module utils/youtube
 * @see docs/stories/story-001-youtube-thumbnail-utility.md
 */

/**
 * Extracts YouTube video ID from URL and returns thumbnail URL.
 *
 * Supports the following YouTube URL formats:
 * - youtube.com/watch?v=VIDEO_ID
 * - youtu.be/VIDEO_ID
 * - youtube.com/embed/VIDEO_ID
 *
 * @param videoUrl - Full YouTube video URL in any supported format
 * @returns YouTube thumbnail URL (maxresdefault) or null if invalid
 *
 * @example
 * ```typescript
 * getYouTubeThumbnail('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
 * // Returns: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
 *
 * getYouTubeThumbnail('https://youtu.be/dQw4w9WgXcQ')
 * // Returns: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
 *
 * getYouTubeThumbnail('https://vimeo.com/123456')
 * // Returns: null (not a YouTube URL)
 * ```
 */
export function getYouTubeThumbnail(videoUrl: string): string | null {
  if (!videoUrl || typeof videoUrl !== 'string') {
    return null
  }

  // YouTube URL patterns to match
  const patterns = [
    /(?:youtube\.com\/watch\?v=)([^&]+)/, // youtube.com/watch?v=VIDEO_ID
    /(?:youtu\.be\/)([^?]+)/, // youtu.be/VIDEO_ID
    /(?:youtube\.com\/embed\/)([^?]+)/, // youtube.com/embed/VIDEO_ID
  ]

  // Try each pattern until we find a match
  for (const pattern of patterns) {
    const match = videoUrl.match(pattern)
    if (match && match[1]) {
      const videoId = match[1]
      return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`
    }
  }

  // No valid YouTube URL pattern found
  return null
}

/**
 * Gets a fallback thumbnail URL if maxresdefault is not available.
 * Some older or lower-quality videos don't have maxresdefault.jpg.
 *
 * @param videoUrl - Full YouTube video URL
 * @returns YouTube thumbnail URL (hqdefault) or null if invalid
 *
 * @example
 * ```typescript
 * getYouTubeThumbnailFallback('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
 * // Returns: 'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg'
 * ```
 */
export function getYouTubeThumbnailFallback(videoUrl: string): string | null {
  if (!videoUrl || typeof videoUrl !== 'string') {
    return null
  }

  const patterns = [
    /(?:youtube\.com\/watch\?v=)([^&]+)/,
    /(?:youtu\.be\/)([^?]+)/,
    /(?:youtube\.com\/embed\/)([^?]+)/,
  ]

  for (const pattern of patterns) {
    const match = videoUrl.match(pattern)
    if (match && match[1]) {
      const videoId = match[1]
      // hqdefault.jpg is 480x360, always available
      return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
    }
  }

  return null
}
