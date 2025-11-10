# Workout Detail Page - UX Design Specification

**Date:** 2025-01-09
**Author:** Sally (UX Expert)
**Feature:** Workout Detail Page Visual Refactor
**Goal:** Surface-level visual polish to match workout-template-create design language

---

## Executive Summary

Transform the 787-line workout tracking screen (`app/(app)/workout/[id].tsx`) to match the professional visual design of the newly shipped workout template builder, while preserving 100% of tracking functionality.

**Scope:** Phase 1 (Visual Polish) + Phase 4 (Animations) ONLY
**Out of Scope:** Architectural refactors, state management changes, performance optimization
**Target Outcome:** Friends load it up and say "HOLY BUTTHOLE!" 🔥

---

## Design Principles

1. **Preserve ALL Tracking Functionality** - Timer, rest tracking, set completion MUST work identically
2. **Visual Consistency** - Match template-create's indigo accent color scheme and component styling
3. **Surface-Level Only** - No architectural changes, just visual improvements
4. **Mobile-First** - User is mid-workout, sweaty, focused - make it EFFORTLESS
5. **Delight in Details** - Smooth animations, satisfying micro-interactions

---

## Current State Analysis

### Pain Points
- Visual inconsistency with new template builder
- No real YouTube thumbnails (just play button placeholder)
- Timer not always visible (requires scrolling)
- Progress not prominent (hard to see X/Y sets complete)
- No satisfying completion feedback (checkmarks feel flat)

### What's Already Great (DON'T TOUCH!)
- ✅ Timer logic (lines 142-170) - SOLID
- ✅ Rest timer modal (lines 254-354) - PERFECT
- ✅ Completion flow (line 356-365) - SIMPLE
- ✅ GraphQL query/mutations - NO CHANGES

---

## Visual Design Improvements

### 1. YouTube Thumbnail Extraction (NEW FEATURE!)

**Problem:** Circular thumbnails show generic play button placeholder
**Solution:** Extract real YouTube thumbnails via YouTube's image API

**Implementation:**
```typescript
// New utility: utils/youtube.ts
function getYouTubeThumbnail(videoUrl: string): string | null {
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

**Impact:** Immediate visual upgrade - users see actual exercise demonstrations

---

### 2. Sticky Timer Bar (NEW COMPONENT)

**Problem:** Timer not visible when scrolling through movements
**Solution:** Sticky header bar always showing timer, progress, current movement

**Visual Design:**
```
┌─────────────────────────────────────────────────┐
│ ⏱️ 12:34 [⏸️]  |  📈 5/12  |  💪 Push-ups       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ← Progress bar
└─────────────────────────────────────────────────┘
```

**Component Spec:**
- **Position:** Sticky at top, z-index above scroll content
- **Background:** White with subtle shadow
- **Timer:** Monospace font, indigo clock icon, circular play/pause button
- **Progress:** Green trending-up icon, "X/Y" format
- **Current Movement:** Truncated movement name, dumbbell icon
- **Progress Bar:** Animated green gradient fill underneath stats

**User Impact:** Always know elapsed time and progress without scrolling

---

### 3. TrackingMovementCard (NEW COMPONENT)

**Problem:** Current MovementFrozen component doesn't match template-create styling
**Solution:** Create new component based on MovementCard with tracking features

**Visual Features:**
- Circular thumbnail with **real YouTube image** + play overlay
- Completion counter: "2/3 sets complete" under movement name
- Collapse toggle for video/description (ChevronDown/Up icon)
- Set table with completion checkmarks (green CheckCircle)
- Completed sets grayed out (opacity 0.6, lighter inputs)
- Clean borders, rounded corners, subtle shadows

**Set Row States:**
```
INCOMPLETE:
[ ] 1 | [10] | [45] | [60]  ← White inputs, dark text

COMPLETE:
[✓] 1 | [10] | [45] | [60]  ← Gray inputs, light text, green check
```

**User Impact:** Modern, professional look matching template builder

---

### 4. Section Headers (VISUAL UPDATE)

**Current:** Plain text headers "WARMUP" / "WORKOUT" / "COOLDOWN"
**New:** Gradient background with emoji icons

**Visual Design:**
```
┌─────────────────────────────────────────────────┐
│ 🔥 WARMUP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ← Indigo gradient fade
└─────────────────────────────────────────────────┘
```

**Styling:**
- Gradient background: `from-indigo-50 to-transparent`
- Bold typography with letter-spacing
- Emoji icons for personality (🔥 Warmup, 💪 Workout, 😌 Cooldown)
- Extending horizontal line to the right

**User Impact:** Clear phase context, visual rhythm for pacing

---

### 5. Metadata Card (VISUAL UPDATE)

**Current:** Basic stats display
**New:** Icon-driven card matching SummaryStatsHeader pattern

**Visual Design:**
```
┌────────────────────────────────────────────┐
│ 📅 Jan 9, 2025 | ⏱️ 00:00 | 💪 3 • 12 sets │
│ [+ Description]                            │
│                                            │
│ "Full body strength training..."          │ ← Collapsed by default
└────────────────────────────────────────────┘
```

**Features:**
- Icons: Calendar, Clock, Dumbbell
- Vertical dividers between stats
- Collapsible description with Markdown rendering
- Rounded card with border and shadow

---

## Animation Specifications (Phase 4)

### 1. Checkmark Bounce (Set Completion)

**Trigger:** User taps checkbox to complete set
**Animation:** Spring bounce (scale 1.0 → 1.3 → 1.0)
**Duration:** 300ms
**Library:** React Native Animated API

```typescript
Animated.sequence([
  Animated.spring(scaleAnim, { toValue: 1.3, speed: 50 }),
  Animated.spring(scaleAnim, { toValue: 1.0, speed: 50 })
])
```

**User Impact:** Satisfying completion feedback, dopamine hit

---

### 2. Progress Bar Smooth Fill

**Trigger:** Set completion updates progress
**Animation:** Width transition with easing
**Duration:** 400ms
**Library:** React Native Animated API

```typescript
Animated.timing(progressWidth, {
  toValue: (completedSets / totalSets) * 100,
  duration: 400,
  useNativeDriver: false,
})
```

**User Impact:** Visual momentum, clear progress tracking

---

### 3. Timer Pulse (When Running)

**Trigger:** Timer is actively running
**Animation:** Subtle scale pulse (1.0 → 1.05 → 1.0), loops
**Duration:** 1000ms per cycle
**Library:** React Native Animated API

```typescript
Animated.loop(
  Animated.sequence([
    Animated.timing(pulseAnim, { toValue: 1.05, duration: 500 }),
    Animated.timing(pulseAnim, { toValue: 1.0, duration: 500 })
  ])
)
```

**User Impact:** Alive feeling, reinforces timer is active

---

### 4. Workout Completion Celebration

**Trigger:** All sets completed, user taps "Complete Workout"
**Option A:** Confetti cannon (requires `react-native-confetti-cannon`)
**Option B:** Toast notification with emoji

**Toast Implementation (Simpler):**
```tsx
<Box className="absolute top-20 px-6 py-3 rounded-full bg-green-600 shadow-lg">
  <Text className="text-white font-bold text-lg">🎉 Workout Complete!</Text>
</Box>
```

**Duration:** 2000ms, auto-dismiss
**User Impact:** Achievement recognition, celebration moment

---

## Design System Tokens

### Color Palette
```typescript
primary: {
  50: '#EEF2FF',   // Indigo-50 (chip backgrounds)
  300: '#A5B4FC',  // Indigo-300 (borders, thumbnails)
  600: '#4F46E5',  // Indigo-600 (primary buttons, accents)
  900: '#312E81',  // Indigo-900 (dark mode chips)
}

success: {
  600: '#16A34A',  // Green-600 (completion checkmarks, progress)
}

gray: {
  300: '#D1D5DB',  // Uncompleted checkmarks
  600: '#4B5563',  // Secondary text
}
```

### Typography
- **Timer:** Monospace, 18px, font-bold
- **Movement Name:** 16px, font-semibold
- **Set Data:** 14px, font-normal
- **Stats:** 12px, font-semibold

### Spacing
- **Card Padding:** 12px (p-3)
- **Stack Spacing:** 8px (space="sm"), 16px (space="md")
- **Border Radius:** 12px (rounded-xl for cards), 6px (rounded-md for inputs)

### Shadows
```typescript
sm: {
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 1 },
  shadowOpacity: 0.05,
  shadowRadius: 2,
  elevation: 1,
}
```

---

## Component Architecture

### New Components to Create

1. **`utils/youtube.ts`**
   - `getYouTubeThumbnail(videoUrl: string): string | null`
   - Pure function, no React

2. **`components/workout/WorkoutTimerBar.tsx`**
   - Props: `elapsedSeconds`, `isRunning`, `completedSets`, `totalSets`, `currentMovementName`, `onToggleTimer`
   - Sticky positioning
   - Animated progress bar

3. **`components/workout/TrackingMovementCard.tsx`**
   - Based on `MovementCard.tsx` (copy 90% of code)
   - Add: Completion checkmarks, collapse toggle, YouTube thumbnails
   - Props: `movementName`, `description`, `videoUrl`, `sets`, `metricUnit`, `onSetComplete`, `onUpdateSet`

4. **Inline Components** (in `workout/[id].tsx`)
   - `SectionHeader({ title, icon })`
   - `MetadataCard({ date, duration, movementsCount, setsCount, description })`
   - `CelebrationToast({ show })`

### Components to Reuse (NO CHANGES)

1. **`components/workout/SummaryStatsHeader.tsx`**
   - Already perfect for stats display
   - Use for metadata card pattern reference

2. **Rest Timer Modal** (existing in `workout/[id].tsx`)
   - Keep exact implementation
   - Only update visual styling (colors, borders)

---

## User Flows (UNCHANGED)

### Flow 1: Start Workout
1. User sees full workout plan (all sets unchecked)
2. User taps "Start Workout" button
3. Timer bar appears, starts counting
4. First uncompleted set subtly highlights

### Flow 2: Complete Set
1. User completes physical reps/duration
2. User taps checkbox on set row
3. Checkmark bounces (animation)
4. Rest timer modal pops up (existing behavior)
5. Countdown runs or user skips
6. Set row grays out, progress updates

### Flow 3: Finish Workout
1. All sets show green checks
2. Progress: 12/12 sets (100%)
3. "Complete Workout" button turns green
4. User taps button
5. Celebration toast appears (2s)
6. Navigate back to journal

---

## Success Criteria

### Quantitative
- ✅ Visual consistency: 100% match with template-create color scheme
- ✅ Functional parity: All tracking features work identically
- ✅ Performance: Animations run at 60fps on device
- ✅ YouTube thumbnails: Load within 2s on 3G connection

### Qualitative
- ✅ **"HOLY BUTTHOLE!" reaction** from friends
- ✅ Professional fitness app aesthetic
- ✅ Satisfying micro-interactions (bounce, fill, pulse)
- ✅ Clear visual hierarchy (know what to do next)

---

## Out of Scope (Phase 2+ Only)

- ❌ Architectural refactors (state management, component extraction beyond visual)
- ❌ Performance optimization (memoization, code splitting)
- ❌ Code reduction (787 → <600 lines is Phase 2)
- ❌ GraphQL query changes
- ❌ Business logic modifications

---

## Migration Strategy

### Phase 1A: Create New Components (Isolated)
- Build WorkoutTimerBar, TrackingMovementCard, utility functions
- Test in isolation (Storybook or separate test screen)
- No integration with main screen yet

### Phase 1B: Integrate Components (Incremental)
- Add WorkoutTimerBar to top of workout detail screen
- Replace one movement with TrackingMovementCard, test
- Replace all movements after single movement works
- Add SectionHeader and MetadataCard components

### Phase 4: Add Animations (Polish)
- Checkmark bounce on set completion
- Progress bar smooth fill
- Timer pulse effect
- Workout completion celebration

### Safety Net
- Git branch: `feature/workout-detail-visual-refactor`
- Commit after each sub-phase
- Test full workout flow after each integration step
- Rollback plan: Revert to previous commit if issues

---

## Files to Modify

### New Files
1. `utils/youtube.ts` - Thumbnail extraction utility
2. `components/workout/WorkoutTimerBar.tsx` - Sticky timer component
3. `components/workout/TrackingMovementCard.tsx` - Movement card with tracking

### Modified Files
1. `app/(app)/workout/[id].tsx` - Main workout detail screen
   - Add WorkoutTimerBar import and usage
   - Replace movement rendering with TrackingMovementCard
   - Add SectionHeader inline components
   - Add MetadataCard inline component
   - Add animation logic (Phase 4)

### Reference Files (NO CHANGES)
- `components/workout/MovementCard.tsx` - Copy styling patterns
- `components/workout/SummaryStatsHeader.tsx` - Reference for icon-driven stats
- `app/(app)/workout-template-create.tsx` - Visual design reference

---

## Testing Plan

### Visual Regression
- Screenshot comparison: Before vs After
- Color scheme validation (indigo accents present)
- Typography consistency check

### Functional Testing
1. Start workout → Timer starts counting
2. Complete set → Rest modal appears, set grays out
3. Edit completed set → Fields remain editable
4. Pause timer → Timer stops, can resume
5. Complete all sets → Celebration appears, can complete workout
6. Complete workout → Navigate back, data saved

### Performance Testing
- Animations run smoothly on physical device (60fps target)
- No frame drops during set completion
- YouTube thumbnails load within 2s

### Cross-Platform
- Test on iOS (Expo Go)
- Test on Android (Expo Go)
- Test dark mode on both platforms

---

## Design Decisions Log

### Decision 1: YouTube Thumbnails
**Options:** Generic play button vs Real thumbnails
**Chosen:** Real thumbnails via YouTube image API
**Rationale:** Immediate visual upgrade, helps users identify exercises

### Decision 2: Timer Placement
**Options:** Fixed header vs Floating FAB
**Chosen:** Fixed sticky header bar
**Rationale:** Always visible, no content obscuring, thumb-friendly

### Decision 3: Video Display
**Options:** Inline collapse vs "More Info" modal
**Chosen:** Inline collapse (keep current behavior)
**Rationale:** Speed matters during workout, no extra taps

### Decision 4: Section Headers
**Options:** Section headers vs Flat with badges
**Chosen:** Keep section headers, improve styling
**Rationale:** Helps user pace workout (warmup/workout/cooldown context)

### Decision 5: Completion Celebration
**Options:** Confetti cannon vs Toast notification
**Chosen:** Toast notification (simpler, no dependency)
**Rationale:** Avoid adding `react-native-confetti-cannon` dependency, toast achieves same goal

---

## Next Steps

1. **PM Agent:** Create Epic + User Stories from this spec
2. **Dev Implementation:** Build components per story breakdown
3. **QA Testing:** Validate visual and functional requirements
4. **User Testing:** Get "HOLY BUTTHOLE!" reaction from friends 🔥

---

## Appendix: Visual Mockups

### Before (Current State)
```
┌─────────────────────────────────┐
│ [Back] Workout Name             │
├─────────────────────────────────┤
│                                 │
│ Date: Today                     │
│ Duration: 00:00                 │
│ 3 Movements • 12 Sets           │
│                                 │
│ WARMUP                          │
│                                 │
│ Movement 1: Jumping Jacks       │
│ [Generic play button]           │
│                                 │
│  # | Reps | Load | Rest | ✓    │
│  1 |  30  |  BW  |  30  | [ ]  │
│  2 |  30  |  BW  |  30  | [ ]  │
│                                 │
│ [Complete Workout]              │
└─────────────────────────────────┘
```

### After (Visual Refactor)
```
┌─────────────────────────────────────┐
│ [Back] Workout Name                 │
├─────────────────────────────────────┤
│ ⏱️ 00:00 [▶] | 📈 0/12 | 💪 Current │ ← STICKY
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
├─────────────────────────────────────┤
│                                     │
│ 📊 METADATA CARD                    │
│ 📅 Jan 9 | ⏱️ 00:00 | 💪 3 • 12    │
│ [+ Description]                     │
│                                     │
│ 🔥 WARMUP ━━━━━━━━━━━━━━━━━━━━━━━ │ ← Gradient
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 🎬 Jumping Jacks          [▼]  │ │ ← Real thumbnail
│ │ 0/2 sets complete               │ │
│ │                                 │ │
│ │  ✓ | # | Reps | Load | Rest    │ │
│ │ [ ] 1  30   BW    30           │ │
│ │ [ ] 2  30   BW    30           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [✅ Complete Workout]               │
└─────────────────────────────────────┘
```

---

**End of UX Specification**
