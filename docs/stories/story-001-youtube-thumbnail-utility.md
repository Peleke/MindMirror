# STORY-001: YouTube Thumbnail Extraction Utility

**Story ID:** STORY-001
**Epic:** EPIC-001 (Workout Detail Visual Refactor)
**Phase:** 1A - Foundation & Utilities
**Priority:** High (Blocks STORY-004)
**Points:** 2
**Status:** Ready

---

## User Story

**As a** user tracking my workout
**I want** to see real YouTube thumbnails for exercises
**So that** I can quickly identify movements without tapping play

---

## Acceptance Criteria

### Must Have
- [ ] Create `utils/youtube.ts` utility file
- [ ] Implement `getYouTubeThumbnail(videoUrl: string): string | null` function
- [ ] Support 3 YouTube URL patterns:
  - `youtube.com/watch?v=VIDEO_ID`
  - `youtu.be/VIDEO_ID`
  - `youtube.com/embed/VIDEO_ID`
- [ ] Return `https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg` format
- [ ] Return `null` for invalid URLs or non-YouTube URLs
- [ ] Write unit tests for all 3 URL patterns + edge cases

### Should Have
- [ ] Handle URLs with query parameters (e.g., `?v=ID&t=30s`)
- [ ] Handle URLs with hash fragments
- [ ] Type-safe implementation with TypeScript strict mode

### Could Have
- [ ] Support additional YouTube URL variants (e.g., `m.youtube.com`)
- [ ] Fallback to `hqdefault.jpg` if `maxresdefault.jpg` fails to load
- [ ] Performance optimization: Memoization for repeated calls

---

## Technical Specification

### Function Signature
```typescript
/**
 * Extracts YouTube video ID from URL and returns thumbnail URL.
 *
 * @param videoUrl - Full YouTube video URL in any supported format
 * @returns YouTube thumbnail URL (maxresdefault) or null if invalid
 *
 * @example
 * getYouTubeThumbnail('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
 * // Returns: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
 */
export function getYouTubeThumbnail(videoUrl: string): string | null
```

### Implementation Pattern
```typescript
// utils/youtube.ts
export function getYouTubeThumbnail(videoUrl: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=)([^&]+)/,
    /(?:youtu\.be\/)([^?]+)/,
    /(?:youtube\.com\/embed\/)([^?]+)/,
  ]

  for (const pattern of patterns) {
    const match = videoUrl.match(pattern)
    if (match && match[1]) {
      return `https://img.youtube.com/vi/${match[1]}/maxresdefault.jpg`
    }
  }

  return null
}
```

### YouTube Thumbnail API
- **Endpoint:** `https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg`
- **Resolution:** 1920x1080 (highest quality)
- **Authentication:** None required (public API)
- **Fallback:** `hqdefault.jpg` (480x360) if maxresdefault unavailable

---

## Test Cases

### Unit Tests (`utils/__tests__/youtube.test.ts`)

```typescript
describe('getYouTubeThumbnail', () => {
  it('should extract thumbnail from youtube.com/watch URL', () => {
    const url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    expect(getYouTubeThumbnail(url)).toBe(
      'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    )
  })

  it('should extract thumbnail from youtu.be short URL', () => {
    const url = 'https://youtu.be/dQw4w9WgXcQ'
    expect(getYouTubeThumbnail(url)).toBe(
      'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    )
  })

  it('should extract thumbnail from youtube.com/embed URL', () => {
    const url = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
    expect(getYouTubeThumbnail(url)).toBe(
      'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    )
  })

  it('should handle URLs with query parameters', () => {
    const url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s'
    expect(getYouTubeThumbnail(url)).toBe(
      'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    )
  })

  it('should return null for invalid YouTube URL', () => {
    const url = 'https://www.youtube.com/invalid'
    expect(getYouTubeThumbnail(url)).toBeNull()
  })

  it('should return null for non-YouTube URL', () => {
    const url = 'https://vimeo.com/123456789'
    expect(getYouTubeThumbnail(url)).toBeNull()
  })

  it('should return null for empty string', () => {
    expect(getYouTubeThumbnail('')).toBeNull()
  })
})
```

---

## Files to Create

### New Files
- `utils/youtube.ts` - Main utility function
- `utils/__tests__/youtube.test.ts` - Unit tests

---

## Dependencies

### Internal
- None (pure utility function)

### External
- None (uses native JavaScript regex, no libraries needed)

---

## Definition of Done

- [ ] `utils/youtube.ts` file created with function implementation
- [ ] Unit tests written and passing (7 test cases minimum)
- [ ] Test coverage ≥95% for youtube.ts
- [ ] TypeScript compiles with no errors (strict mode)
- [ ] Code reviewed and follows project conventions
- [ ] Function documented with JSDoc comments
- [ ] Committed to feature branch with descriptive message

---

## Testing Instructions

### Manual Testing
1. Run unit tests: `npm test utils/youtube.test.ts`
2. Verify all 7 test cases pass
3. Check test coverage: `npm run test:coverage -- utils/youtube.ts`

### Integration Preview
```typescript
// Preview usage in TrackingMovementCard (STORY-004)
import { getYouTubeThumbnail } from '@/utils/youtube'

const thumbnailUrl = getYouTubeThumbnail(movement.videoUrl)

<Image
  source={{ uri: thumbnailUrl || 'fallback-image.png' }}
  style={styles.thumbnail}
/>
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube API changes thumbnail URL format | Medium | Document current format, add fallback logic |
| Video ID extraction regex breaks on new URL format | Low | Add test cases for edge cases, monitor YouTube URL patterns |
| maxresdefault.jpg not available for old videos | Low | Fallback to hqdefault.jpg (lower resolution but always available) |

---

## Estimated Effort

- **Implementation:** 30 minutes
- **Testing:** 30 minutes
- **Code Review:** 15 minutes
- **Total:** ~1.25 hours

---

## Related Stories

- **Blocks:** STORY-004 (TrackingMovementCard needs this utility)
- **Related:** STORY-002 (Design tokens for circular thumbnail styling)

---

**Next:** After completion, proceed to STORY-002 (Design System Tokens).
