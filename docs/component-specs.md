# Workout UI Component Specifications
## Alpha Validation - Hevy-Inspired Design

**Version:** v1.0 (Alpha)
**Last Updated:** 2025-10-15
**Designer:** Sally (UX Expert)
**Implementation File:** `mindmirror-mobile/app/(app)/client/[id].tsx`

---

## 📋 Table of Contents

1. [Exercise Card Component](#1-exercise-card-component)
2. [Set Table Component](#2-set-table-component)
3. [Rest Timer Modal](#3-rest-timer-modal)
4. [Notes Input Modal](#4-notes-input-modal)
5. [Video Player Modal](#5-video-player-modal)
6. [Auto-Save Behavior](#6-auto-save-behavior)

---

## 1. Exercise Card Component

### Visual Reference (Hevy)

From Hevy screenshots analysis:
- Clean card layout with exercise name prominently displayed
- Video thumbnail centered (or top-aligned)
- Target sets/reps shown below in secondary text
- Minimal borders, subtle shadow for depth
- Plenty of breathing room (padding)

### Layout Structure

```
┌─────────────────────────────────────────────┐
│  EXERCISE CARD                              │
│  ┌───────────────────────────────────────┐  │
│  │ [Video Thumbnail 120x120px]           │  │ ← Centered, rounded corners
│  │                                       │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Barbell Back Squat                        │ ← Display typography (24px bold)
│                                             │
│  3 sets × 8 reps                           │ ← Body Small typography (14px)
│                                             │
│  ▼ Exercise Notes (if present)             │ ← Collapsed accordion
│                                             │
└─────────────────────────────────────────────┘
```

### Component Breakdown

#### Container
```typescript
{
  backgroundColor: colors.light.bgElevated, // Light: #F5F5F5, Dark: #1E1E1E
  borderRadius: 12,
  padding: spacing.md, // 16px
  marginBottom: spacing.lg, // 24px between cards
  // Light mode shadow
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.08,
  shadowRadius: 8,
  elevation: 3, // Android
  // Dark mode: add subtle border
  borderWidth: Platform.OS === 'ios' ? 0 : 1, // Or use theme hook
  borderColor: colors.dark.border, // #3A3A3A in dark mode
}
```

#### Video Thumbnail
```typescript
{
  width: 120,
  height: 120,
  borderRadius: 8,
  backgroundColor: colors.light.bgSubtle, // Placeholder bg while loading
  alignSelf: 'center',
  marginBottom: spacing.sm, // 8px gap to exercise name
  // If video URL exists, show poster frame
  // Else show placeholder icon (dumbbell icon or "No video available")
}
```

**Interaction:**
- **Tap thumbnail** → Opens Video Player Modal (Component #5)
- **Loading state:** Show skeleton shimmer (gray box with subtle animation)
- **No video:** Show icon placeholder + text "Video unavailable"

**Accessibility:**
- `accessibilityLabel`: "Watch demo for [exercise name]"
- `accessibilityRole`: "button"

#### Exercise Name
```typescript
{
  ...typography.display, // 24px, bold, -0.5 letter spacing
  color: colors.light.textPrimary, // Light: #212121, Dark: #FFFFFF
  marginBottom: spacing.xs, // 4px gap to target sets/reps
  textAlign: 'center',
}
```

#### Target Sets/Reps
```typescript
{
  ...typography.bodySmall, // 14px, regular
  color: colors.light.textSecondary, // Light: #616161, Dark: #B0B0B0
  textAlign: 'center',
  marginBottom: spacing.sm, // 8px gap to accordion (if present)
}
```

**Format:** `{sets} sets × {reps} reps` (e.g., "3 sets × 8 reps")

#### Exercise Notes Accordion (Optional - if notes exist)

**Collapsed State:**
```
▼ Exercise Notes
```

**Expanded State:**
```
▲ Exercise Notes

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Focus on depth and tempo control.
```

```typescript
// Accordion Header (tappable)
{
  flexDirection: 'row',
  alignItems: 'center',
  paddingVertical: spacing.sm,
  borderTopWidth: 1,
  borderTopColor: colors.light.borderSubtle, // Subtle divider
  marginTop: spacing.sm,
}

// Icon (chevron down/up)
{
  marginRight: spacing.xs,
  color: colors.light.primary, // Teal/Indigo
  fontSize: 16,
}

// Accordion Body (when expanded)
{
  paddingTop: spacing.sm,
  ...typography.bodySmall,
  color: colors.light.textSecondary,
  lineHeight: 20,
}
```

**Interaction:**
- Tap header → Toggle expanded/collapsed
- Smooth height animation (250ms ease-in-out)

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **No video URL** | Show placeholder icon (dumbbell) + "Video unavailable" text |
| **Video loading error** | Show error icon + "Failed to load video" |
| **Long exercise name** | Allow 2 lines max, then ellipsize with "..." |
| **No notes** | Don't render accordion at all |
| **Very long notes** | Expandable, no max height (user can scroll full card if needed) |

---

### Interaction States

| State | Visual Change |
|-------|--------------|
| **Default** | As specified above |
| **Video thumbnail hover** | Subtle scale (1.02), 150ms ease-in-out |
| **Video thumbnail press** | Scale (0.98), slight opacity reduction (0.9) |
| **Loading** | Skeleton shimmer on thumbnail area |

---

## 2. Set Table Component

### Visual Reference (Hevy)

From Hevy screenshots:
- Clean table layout with clear column headers
- Minimal borders (subtle dividers between rows)
- Numeric inputs with +/- stepper buttons
- Completion checkbox fills row with success color
- Compact but not cramped spacing

### Layout Structure (Simplified for Alpha)

```
┌──────────────────────────────────────────────────────────┐
│  SET TABLE                                               │
│  ┌────┬────────┬────────┬──────┬───────┐                │
│  │ #  │ Target │ Weight │ Reps │   ✓   │ ← Header Row   │
│  ├────┼────────┼────────┼──────┼───────┤                │
│  │ 1  │ 185×8  │ [___]  │ [__] │  ☐    │ ← Data Row     │
│  ├────┼────────┼────────┼──────┼───────┤                │
│  │ 2  │ 185×8  │ [___]  │ [__] │  ☐    │                │
│  ├────┼────────┼────────┼──────┼───────┤                │
│  │ 3  │ 185×8  │ [185]  │ [8]  │  ☑    │ ← Completed    │
│  └────┴────────┴────────┴──────┴───────┘                │
└──────────────────────────────────────────────────────────┘
```

**Note:** No "Previous" column for alpha (deferred to post-alpha per user decision)

### Component Breakdown

#### Table Container
```typescript
{
  marginTop: spacing.md, // 16px gap from exercise card
  marginBottom: spacing.lg, // 24px gap to next exercise
  borderRadius: 8,
  overflow: 'hidden', // Clips rounded corners
  // Optional: subtle border
  borderWidth: 1,
  borderColor: colors.light.borderSubtle,
}
```

#### Header Row
```typescript
{
  flexDirection: 'row',
  backgroundColor: colors.light.bgSubtle, // Light: #ECEFF1, Dark: #2C2C2C
  paddingVertical: spacing.sm, // 8px
  borderBottomWidth: 1,
  borderBottomColor: colors.light.border, // #CFD8DC
}
```

**Column Headers:**
```typescript
// Shared style for all headers
{
  ...typography.bodySmall, // 14px
  fontWeight: '600', // Semibold
  color: colors.light.textSecondary,
  textAlign: 'center',
}

// Column widths
{
  setNumber: { width: 40 },   // "#"
  target: { width: 80 },      // "Target"
  weight: { flex: 1 },        // "Weight" (flexible)
  reps: { width: 80 },        // "Reps"
  checkbox: { width: 48 },    // "✓"
}
```

#### Data Row (Default State)
```typescript
{
  flexDirection: 'row',
  paddingVertical: spacing.sm, // 8px
  minHeight: 48, // Ensures 44px+ touch target for inputs/checkbox
  alignItems: 'center',
  borderBottomWidth: 1,
  borderBottomColor: colors.light.borderSubtle, // Very subtle divider
  backgroundColor: 'transparent', // Default (no row background)
}
```

#### Data Row (Completed State)
```typescript
{
  // Inherits from Data Row, overrides background:
  backgroundColor: '#E8F5E9', // Light green tint (light mode)
  // Dark mode: '#1B3A1F' (dark green tint)
}
```

**Transition:** When checkbox toggled ON, animate background color over 250ms ease-in-out

---

### Column Components

#### Set Number Column
```typescript
// Container
{
  width: 40,
  justifyContent: 'center',
  alignItems: 'center',
}

// Text
{
  ...typography.body, // 16px
  fontWeight: '600', // Semibold
  color: colors.light.textPrimary,
}
```

**Format:** `1`, `2`, `3`, etc. (just the number, no "#")

---

#### Target Column (Read-Only)
```typescript
// Container
{
  width: 80,
  justifyContent: 'center',
  alignItems: 'center',
}

// Text
{
  ...typography.bodySmall, // 14px
  color: colors.light.textTertiary, // Greyed out (de-emphasized)
}
```

**Format:** `185×8` (weight × reps from program prescription)

**Edge Case:** If no target prescribed, show `—` (em dash)

---

#### Weight Input Column (Numeric Stepper)

**Layout:**
```
┌─────────────────────────┐
│  [-]  [185]  [+]        │
│   ↑    ↑     ↑          │
│  Minus Input Plus       │
└─────────────────────────┘
```

```typescript
// Container
{
  flex: 1,
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  paddingHorizontal: spacing.xs, // 4px
}

// Minus Button
{
  width: 32,
  height: 32,
  borderRadius: 6,
  backgroundColor: colors.light.primary50, // Light teal tint
  justifyContent: 'center',
  alignItems: 'center',
  marginRight: spacing.xs, // 4px gap to input
}

// Input Field
{
  width: 60,
  height: 36,
  backgroundColor: colors.light.bgSubtle,
  borderWidth: 1,
  borderColor: colors.light.border,
  borderRadius: 6,
  textAlign: 'center',
  ...typography.body, // 16px (prevents iOS zoom)
  color: colors.light.textPrimary,
  paddingHorizontal: spacing.xs,
}

// Plus Button (same as Minus)
{
  width: 32,
  height: 32,
  borderRadius: 6,
  backgroundColor: colors.light.primary50,
  justifyContent: 'center',
  alignItems: 'center',
  marginLeft: spacing.xs, // 4px gap from input
}
```

**Interaction:**
- **Tap Minus:** Decrement weight by 5 (or custom increment)
- **Tap Plus:** Increment weight by 5
- **Tap Input:** Focus input, show numeric keyboard (iOS/Android native)
- **On Change:** Fire auto-save mutation (see Section 6)

**Accessibility:**
- Minus button: `accessibilityLabel`: "Decrease weight", `accessibilityRole`: "button"
- Plus button: `accessibilityLabel`: "Increase weight", `accessibilityRole`: "button"
- Input: `keyboardType`: "numeric", `returnKeyType`: "next" (advances to reps)

**Edge Cases:**
- Negative weight: Prevent (min value 0 or 1)
- Empty input: Allow temporarily, default to 0 on blur
- Very large numbers (999+): Allow, ensure input width handles up to 4 digits

---

#### Reps Input Column (Numeric Stepper)

**Same layout as Weight Input, but narrower:**

```typescript
// Container: Same as Weight, but width: 80 instead of flex: 1
// Input width: 48px (smaller than weight)
// Stepper buttons: Same 32x32 size
```

**Interaction:**
- Same as Weight Input
- Decrement/increment by 1 (not 5)
- `returnKeyType`: "done" (last input in row, dismisses keyboard)
- **On Change:** Fire auto-save mutation

**Auto-Advance Focus (Keyboard Flow):**
1. User completes weight input → presses "Next"
2. Focus automatically moves to Reps input
3. User completes reps → presses "Done"
4. Keyboard dismisses, focus moves to checkbox (or next set's weight input)

---

#### Completion Checkbox Column

```typescript
// Container
{
  width: 48,
  justifyContent: 'center',
  alignItems: 'center',
}

// Checkbox
{
  width: 28,
  height: 28,
  borderRadius: 6,
  borderWidth: 2,
  borderColor: colors.light.border, // Unchecked: gray border
  backgroundColor: 'transparent', // Unchecked: empty
  justifyContent: 'center',
  alignItems: 'center',
}

// Checkbox (Checked State)
{
  borderColor: colors.light.primary, // Teal/Indigo
  backgroundColor: colors.light.primary, // Filled
}

// Checkmark Icon (when checked)
{
  color: '#FFFFFF', // White checkmark
  fontSize: 18,
}
```

**Interaction:**
- **Tap checkbox:** Toggle checked/unchecked
- **On Check:**
  1. Trigger light haptic feedback (`Haptics.impactAsync(Light)`)
  2. Animate row background to success green (250ms)
  3. Open Rest Timer Modal (Component #3) if not last set
  4. Fire auto-save mutation
- **On Uncheck:**
  1. Remove row background tint (animate back to transparent)
  2. Fire auto-save mutation

**Accessibility:**
- `accessibilityRole`: "checkbox"
- `accessibilityLabel`: "Mark set {number} complete"
- `accessibilityState`: `{ checked: true/false }`

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **Empty weight/reps** | Allow user to complete set with 0 (failure), but show warning toast: "Set logged with 0 weight/reps" |
| **User unchecks completed set** | Remove row tint, allow re-editing weight/reps |
| **Network failure during save** | Show toast: "Offline - changes will sync when connected", queue mutation for retry |
| **Very long set list (>10 sets)** | Use FlatList with virtualization (render only visible rows) |

---

## 3. Rest Timer Modal

### Visual Reference (Hevy)

From Hevy screenshots:
- Centered modal overlay
- Large circular progress ring
- Bold countdown timer inside ring
- Action buttons below: Skip, Add 30s
- Dimmed background (modal overlay)

### Layout Structure

```
┌───────────────────────────────────────┐
│  DIMMED OVERLAY (rgba(0,0,0,0.75))    │
│                                       │
│    ┌───────────────────────────┐     │
│    │  REST TIMER               │     │
│    │                           │     │
│    │     ╭─────────────╮       │     │
│    │    │   ██████     │       │     │ ← Circular progress
│    │    │  ██  90 ██   │       │     │
│    │    │   ██████     │       │     │
│    │     ╰─────────────╯       │     │
│    │                           │     │
│    │   [Skip]    [Add 30s]    │     │
│    │                           │     │
│    └───────────────────────────┘     │
│                                       │
└───────────────────────────────────────┘
```

### Component Breakdown

#### Overlay (Modal Background)
```typescript
{
  flex: 1,
  backgroundColor: 'rgba(0, 0, 0, 0.75)', // Dim background
  justifyContent: 'center',
  alignItems: 'center',
}
```

**Interaction:**
- **Tap outside modal:** Does NOT dismiss (force user to interact with Skip/Add 30s)
- Use `Modal` component with `onRequestClose` disabled (Android back button also blocked)

---

#### Modal Container
```typescript
{
  backgroundColor: colors.light.bgElevated, // Light: #F5F5F5, Dark: #1E1E1E
  borderRadius: 16,
  padding: spacing.xl, // 32px
  width: '80%',
  maxWidth: 400,
  alignItems: 'center',
  // Prominent shadow
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 8 },
  shadowOpacity: 0.3,
  shadowRadius: 16,
  elevation: 12, // Android
}
```

---

#### Circular Progress Ring

**Library Recommendation:** `react-native-svg` + `react-native-reanimated` for smooth animation

**Specs:**
```typescript
{
  diameter: 160,
  strokeWidth: 12,
  strokeColor: colors.light.primary, // Teal/Indigo
  backgroundColor: colors.light.bgSubtle, // Track color (light gray)
  strokeLinecap: 'round', // Rounded ends
}
```

**Animation:**
- Progress decreases from 100% → 0% over timer duration (e.g., 90 seconds)
- Smooth linear animation (no stepping)
- When timer reaches 10 seconds: Change stroke color to `warning` (orange)
- When timer reaches 0: Fill entire ring with `success` green, trigger heavy haptic

---

#### Countdown Text (Inside Ring)
```typescript
{
  position: 'absolute', // Positioned over circular progress
  fontSize: 56,
  fontWeight: '700',
  color: colors.light.textPrimary, // Light: #212121, Dark: #FFFFFF
  letterSpacing: -1, // Tighten for large numerals
}
```

**Format:** `90`, `89`, `88`, ... `0` (just the number, no "seconds" label)

**Color Changes:**
- 90-11 seconds: `textPrimary` (black/white)
- 10-6 seconds: `warning` (orange) - matches ring color change
- 5-0 seconds: `error` (red) - urgency

---

#### Action Buttons Row
```typescript
// Container
{
  flexDirection: 'row',
  marginTop: spacing.lg, // 24px gap from progress ring
  gap: spacing.md, // 16px between buttons (or use marginRight on first button)
}

// Skip Button (Secondary style)
{
  flex: 1,
  backgroundColor: 'transparent',
  borderWidth: 1.5,
  borderColor: colors.light.textSecondary, // Gray border
  borderRadius: 8,
  paddingVertical: spacing.sm,
  paddingHorizontal: spacing.md,
  minHeight: 44,
}

// Skip Button Text
{
  ...typography.button, // 16px, semibold
  color: colors.light.textSecondary,
  textAlign: 'center',
}

// Add 30s Button (Ghost style)
{
  flex: 1,
  backgroundColor: 'transparent',
  borderRadius: 8,
  paddingVertical: spacing.sm,
  paddingHorizontal: spacing.md,
  minHeight: 44,
}

// Add 30s Button Text
{
  ...typography.button,
  color: colors.light.primary, // Teal/Indigo
  textAlign: 'center',
}
```

**Interaction:**
- **Tap Skip:** Dismiss modal immediately, continue to next set
- **Tap Add 30s:** Add 30 seconds to current timer, update progress ring, continue countdown

---

### Haptic Feedback Schedule

| Timer State | Haptic Type | Trigger |
|-------------|-------------|---------|
| 10 seconds remaining | Medium impact | Once at 10s |
| 5 seconds remaining | Medium impact | Once at 5s |
| 0 seconds (complete) | Heavy impact | Once at 0s |

**Implementation:**
```typescript
import * as Haptics from 'expo-haptics';

// At 10s, 5s:
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

// At 0s:
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
```

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **User backgrounds app** | Timer continues in background, resume on foreground (use `AppState` listener) |
| **User adds 30s multiple times** | Allow unlimited additions (some users prefer long rest periods) |
| **Timer reaches 0** | Play completion sound (optional), show success state (green ring), auto-dismiss after 2 seconds OR wait for user tap |
| **Last set of exercise** | Don't show rest timer (no rest needed after final set) |

---

## 4. Notes Input Modal

### Layout Structure

**Mobile (Full-Screen):**
```
┌───────────────────────────────────┐
│  ← Workout Notes          [Save]  │ ← Header
│  ────────────────────────────────│
│                                   │
│  [Multiline text input area]     │
│  Felt good today, increased       │
│  weight on squats. Left knee      │
│  was stable.                      │
│                                   │
│                                   │
│  150/200 characters               │ ← Character counter
│                                   │
│  [Cancel]                         │ ← Footer
└───────────────────────────────────┘
```

**Tablet (60% Width Centered):**
```
       ┌───────────────────────┐
       │  Workout Notes [Save] │
       │  ─────────────────────│
       │                       │
       │  [Multiline input]    │
       │                       │
       │  150/200              │
       │  [Cancel]             │
       └───────────────────────┘
```

### Component Breakdown

#### Modal Container (Mobile)
```typescript
{
  flex: 1,
  backgroundColor: colors.light.bg, // Light: #FFFFFF, Dark: #121212
  paddingTop: Platform.OS === 'ios' ? 50 : 20, // Account for status bar
}
```

#### Modal Container (Tablet)
```typescript
{
  width: '60%',
  maxWidth: 600,
  backgroundColor: colors.light.bgElevated, // #F5F5F5 / #1E1E1E
  borderRadius: 12,
  padding: spacing.md,
  alignSelf: 'center',
  marginTop: 100, // Vertically centered-ish
}
```

---

#### Header Row
```typescript
{
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderBottomWidth: 1,
  borderBottomColor: colors.light.borderSubtle,
}

// Back Button (mobile only, left side)
{
  width: 40,
  height: 40,
  justifyContent: 'center',
  alignItems: 'center',
}

// Title
{
  ...typography.title, // 18px, semibold
  color: colors.light.textPrimary,
}

// Save Button (right side)
{
  backgroundColor: colors.light.primary, // Teal/Indigo
  borderRadius: 8,
  paddingVertical: spacing.xs,
  paddingHorizontal: spacing.md,
  minHeight: 36,
}

// Save Button Text
{
  ...typography.button,
  fontSize: 14,
  color: '#FFFFFF',
}
```

**Interaction:**
- **Back button (mobile):** Dismiss modal without saving, show confirmation if text entered
- **Save button:** Save notes to `workout.notes` field, dismiss modal, show toast "Notes saved"
- **Save button disabled state:** If input is empty, button is 40% opacity and non-interactive

---

#### Text Input
```typescript
{
  backgroundColor: colors.light.bgSubtle, // #ECEFF1 / #2C2C2C
  borderRadius: 8,
  padding: spacing.md,
  marginHorizontal: spacing.md,
  marginTop: spacing.md,
  fontSize: 16,
  color: colors.light.textPrimary,
  minHeight: 120,
  maxHeight: 240, // Prevent excessive expansion, allow scroll if needed
  textAlignVertical: 'top', // Start cursor at top-left (not centered)
  // For React Native
  multiline: true,
  numberOfLines: 6,
  maxLength: 200, // Hard limit (enforced)
}
```

**Placeholder Text:** `"Add notes about this workout (e.g., pain level, energy, adjustments made)"`

**Accessibility:**
- `accessibilityLabel`: "Workout notes input"
- `returnKeyType`: "default" (allows line breaks)

---

#### Character Counter
```typescript
{
  ...typography.caption, // 12px
  color: colors.light.textTertiary,
  textAlign: 'right',
  marginHorizontal: spacing.md,
  marginTop: spacing.xs, // 4px gap from input
}
```

**Format:** `{current}/200` (e.g., `150/200`)

**Color Logic:**
- 0-180 characters: `textTertiary` (gray)
- 181-195 characters: `warning` (orange) - getting close
- 196-200 characters: `error` (red) - at limit

---

#### Cancel Button (Footer, Mobile Only)
```typescript
{
  marginTop: spacing.lg,
  marginHorizontal: spacing.md,
  borderWidth: 1.5,
  borderColor: colors.light.textSecondary,
  borderRadius: 8,
  paddingVertical: spacing.sm,
  minHeight: 44,
  alignItems: 'center',
}

// Cancel Button Text
{
  ...typography.button,
  color: colors.light.textSecondary,
}
```

**Interaction:**
- **Tap Cancel:** Dismiss modal, discard changes
- If user has typed text, show confirmation alert: "Discard notes?" [Cancel] [Discard]

---

### Auto-Save Behavior

**For Alpha:** Notes save when user taps "Save" button (manual save)

**Post-Alpha:** Consider auto-save on blur (when keyboard dismisses)

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **User dismisses modal with unsaved text** | Show confirmation: "Discard notes?" [Cancel] [Discard] |
| **User exceeds 200 characters** | Hard limit enforced by `maxLength` prop (cannot type more) |
| **Empty notes field** | Save button disabled (40% opacity, non-interactive) |
| **Network failure** | Show toast: "Failed to save notes. Try again." Keep modal open, allow retry |

---

## 5. Video Player Modal

### Layout Structure

**Mobile (Full-Screen):**
```
┌───────────────────────────────────┐
│  [X]                              │ ← Close button (top-right)
│                                   │
│  ┌─────────────────────────────┐ │
│  │                             │ │
│  │   [Video Player Area]       │ │ ← YouTube/Vimeo embed or native player
│  │                             │ │
│  └─────────────────────────────┘ │
│                                   │
│  Barbell Back Squat               │ ← Exercise name
│                                   │
│  [Short Demo]  [Full Tutorial]   │ ← Toggle buttons (if both URLs exist)
│                                   │
└───────────────────────────────────┘
```

**Tablet (Centered, 80% Width):**
```
       ┌─────────────────────┐
       │ [X]                 │
       │                     │
       │  [Video Player]     │
       │                     │
       │  Exercise Name      │
       │  [Short] [Full]     │
       └─────────────────────┘
```

### Component Breakdown

#### Modal Container
```typescript
{
  flex: 1,
  backgroundColor: '#000000', // Black background for video player aesthetic
  justifyContent: 'center',
  alignItems: 'center',
}
```

**On Tablet:**
```typescript
{
  width: '80%',
  maxWidth: 800,
  aspectRatio: 16/9, // Maintain video aspect ratio
  backgroundColor: '#000000',
  borderRadius: 12,
  overflow: 'hidden',
}
```

---

#### Close Button
```typescript
{
  position: 'absolute',
  top: Platform.OS === 'ios' ? 50 : 20, // Account for status bar
  right: spacing.md,
  width: 40,
  height: 40,
  borderRadius: 20, // Circular button
  backgroundColor: 'rgba(255, 255, 255, 0.2)', // Semi-transparent white
  justifyContent: 'center',
  alignItems: 'center',
  zIndex: 10, // Ensure it's above video player
}

// Icon (X)
{
  color: '#FFFFFF',
  fontSize: 24,
}
```

**Interaction:**
- **Tap:** Dismiss modal, return to workout screen
- **Swipe down (optional iOS gesture):** Dismiss modal (use `react-native-gesture-handler`)

---

#### Video Player Area

**For YouTube/Vimeo Embeds:**
```typescript
import { WebView } from 'react-native-webview';

<WebView
  source={{ uri: videoUrl }} // e.g., "https://www.youtube.com/embed/abcd123"
  style={{ flex: 1, backgroundColor: '#000' }}
  allowsFullscreenVideo={true}
  mediaPlaybackRequiresUserAction={false} // Auto-play on iOS
/>
```

**For MP4 Direct URLs:**
```typescript
import { Video } from 'expo-av';

<Video
  source={{ uri: videoUrl }} // e.g., "https://cdn.example.com/squat.mp4"
  style={{ width: '100%', aspectRatio: 16/9 }}
  useNativeControls={true} // Show play/pause, scrubber
  resizeMode="contain"
  shouldPlay={true} // Auto-play on mount
/>
```

**Decision Logic:**
```typescript
if (videoUrl.includes('youtube.com') || videoUrl.includes('vimeo.com')) {
  // Use WebView
} else {
  // Use Video (native player)
}
```

---

#### Exercise Name Label (Below Video)
```typescript
{
  ...typography.title, // 18px, semibold
  color: '#FFFFFF', // White text on black background
  textAlign: 'center',
  marginTop: spacing.md,
  marginHorizontal: spacing.md,
}
```

---

#### Video Toggle Buttons (If Both short_video_url AND long_video_url Exist)

```typescript
// Container
{
  flexDirection: 'row',
  marginTop: spacing.sm,
  gap: spacing.sm,
  paddingHorizontal: spacing.md,
}

// Short Demo Button (Active State)
{
  flex: 1,
  backgroundColor: colors.light.primary, // Teal/Indigo
  borderRadius: 8,
  paddingVertical: spacing.sm,
  alignItems: 'center',
}

// Short Demo Button (Inactive State)
{
  flex: 1,
  backgroundColor: 'rgba(255, 255, 255, 0.2)', // Semi-transparent
  borderRadius: 8,
  paddingVertical: spacing.sm,
  alignItems: 'center',
}

// Button Text (Active)
{
  ...typography.button,
  fontSize: 14,
  color: '#FFFFFF',
}

// Button Text (Inactive)
{
  ...typography.button,
  fontSize: 14,
  color: 'rgba(255, 255, 255, 0.7)', // Semi-transparent white
}
```

**Interaction:**
- **Tap Short Demo:** Switch video player to `short_video_url`, update active button style
- **Tap Full Tutorial:** Switch video player to `long_video_url`, update active button style
- Smooth transition (fade out old video, fade in new video - 250ms)

**If Only One Video URL Exists:**
- Don't render toggle buttons at all
- Just show the single video

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **No video URL** | Don't open modal (button disabled on Exercise Card) |
| **Video fails to load** | Show error message in player area: "Failed to load video" + [Retry] button |
| **User backgrounds app** | Pause video playback, resume on foreground |
| **Only short_video_url exists** | Show that video, hide toggle buttons |
| **Only long_video_url exists** | Show that video, hide toggle buttons |
| **User rotates device** | Support landscape orientation for better viewing (use `react-native-orientation-locker`) |

---

### Accessibility

- Close button: `accessibilityLabel`: "Close video", `accessibilityRole`: "button"
- Video player: `accessibilityLabel`: "Video demonstration for [exercise name]"
- Toggle buttons: `accessibilityRole`: "button", `accessibilityState`: `{ selected: true/false }`

---

## 6. Auto-Save Behavior

### Mutation Trigger Points

Per user decision (Option A), we fire an auto-save mutation whenever user modifies workout state:

| User Action | Mutation Trigger | Mutation Fields |
|-------------|-----------------|-----------------|
| **Logs weight** | On input blur or +/- button press | `set_id`, `weight` |
| **Logs reps** | On input blur or +/- button press | `set_id`, `reps` |
| **Completes set** | On checkbox toggle | `set_id`, `completed` |
| **Opens rest timer** | When rest timer modal opens | `last_activity_timestamp` (optional) |
| **Every 15 seconds** | Timer tick | `duration` (elapsed time) |

### Implementation Strategy

**Optimistic UI Updates:**
1. User types weight → UI updates immediately (no spinner)
2. Fire mutation in background
3. If mutation fails → Show toast, revert UI (or queue for retry)

**Debouncing for Text Inputs:**
```typescript
// Don't fire mutation on every keystroke
// Wait 500ms after user stops typing, then save
const debouncedSave = debounce((setId, field, value) => {
  updateWorkoutSetMutation({ setId, [field]: value });
}, 500);
```

**Duration Auto-Save (Every 15 Seconds):**
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    updateWorkoutDurationMutation({ workoutId, duration: elapsedSeconds });
  }, 15000); // 15 seconds

  return () => clearInterval(interval);
}, [elapsedSeconds]);
```

### GraphQL Mutation Example

```graphql
mutation UpdateWorkoutSet(
  $setId: ID!
  $weight: Float
  $reps: Int
  $completed: Boolean
) {
  updateWorkoutSet(
    setId: $setId
    weight: $weight
    reps: $reps
    completed: $completed
  ) {
    id
    weight
    reps
    completed
    updatedAt
  }
}
```

**Backend Requirements:**
- `updateWorkoutSet` mutation must handle partial updates (only update fields provided)
- Must support saving incomplete sets (weight = null, reps = null) for in-progress workouts
- `practice_instance` (or workout model) needs `duration` field for elapsed time tracking

### Network Failure Handling

**Offline Queue:**
1. Mutation fails → Store in AsyncStorage queue
2. Show toast: "Offline - changes will sync when connected"
3. On network reconnect → Flush queue, retry mutations in order
4. On success → Remove from queue, show toast: "Changes synced"

**Library Recommendation:** `@apollo/client` has built-in retry/queue logic for mutations

---

### Edge Cases

| Case | Behavior |
|------|----------|
| **User edits set after completion** | Allow (uncheck checkbox, modify weight/reps, re-complete) |
| **Mutation fails 3 times** | Stop retrying, show persistent banner: "Unable to save. Check connection." |
| **User navigates away mid-workout** | State persists (already auto-saved), can resume later |
| **User closes app mid-workout** | State persists, duration paused, resumes on next open |

---

## 🚀 Implementation Checklist

### Phase 1: Foundation (Day 1)
- [ ] Set up design system constants file (`src/theme/constants.ts`)
- [ ] Create theme context for light/dark mode switching
- [ ] Test color palette on both iOS and Android (ensure contrast ratios)

### Phase 2: Exercise Card (Day 2)
- [ ] Implement Exercise Card component layout
- [ ] Add video thumbnail with tap-to-play interaction
- [ ] Implement collapsible notes accordion
- [ ] Test with long exercise names, missing videos, missing notes

### Phase 3: Set Table (Days 2-3)
- [ ] Implement table header row with column labels
- [ ] Create numeric stepper inputs for weight/reps
- [ ] Add completion checkbox with haptic feedback
- [ ] Implement row background tint on completion
- [ ] Wire up auto-save mutations for all inputs
- [ ] Test with 10+ sets (virtualization)

### Phase 4: Rest Timer Modal (Day 3)
- [ ] Implement circular progress ring animation
- [ ] Add countdown timer with color changes (orange at 10s, red at 5s)
- [ ] Wire up haptic feedback (10s, 5s, 0s)
- [ ] Add Skip and Add 30s buttons
- [ ] Test timer accuracy, background/foreground behavior

### Phase 5: Notes & Video Modals (Day 4)
- [ ] Implement Notes Input Modal (full-screen mobile, centered tablet)
- [ ] Add character counter with color logic
- [ ] Wire up save mutation for `workout.notes` field
- [ ] Implement Video Player Modal with YouTube/Vimeo/MP4 support
- [ ] Add short/long video toggle (if both URLs exist)
- [ ] Test video playback, rotation, error states

### Phase 6: Auto-Save & Polish (Day 5)
- [ ] Implement debounced auto-save for text inputs
- [ ] Add duration auto-save (every 15 seconds)
- [ ] Implement offline queue for failed mutations
- [ ] Add loading skeletons for initial workout load
- [ ] Test full workout flow end-to-end (log sets, rest, complete, save notes)
- [ ] QA on both light and dark modes

---

## 📱 Testing Scenarios

### Happy Path
1. User opens workout screen
2. Video thumbnail loads, user taps → plays video
3. User logs weight (185 lbs) → auto-saves
4. User logs reps (8) → auto-saves
5. User checks completion checkbox → row turns green, rest timer opens
6. User waits 90 seconds (or skips) → modal dismisses
7. User repeats for 3 sets
8. User taps notes button → adds workout notes → saves
9. User navigates away → state persists

### Edge Cases to Test
- [ ] No video URL (show placeholder)
- [ ] Video fails to load (show error message)
- [ ] User logs 0 weight/reps (allow, show warning)
- [ ] Network failure mid-workout (queue mutations, show offline toast)
- [ ] User backgrounds app during rest timer (timer continues)
- [ ] User rotates device during video playback (maintain orientation)
- [ ] Very long exercise name (truncate with ellipsis)
- [ ] 10+ sets in table (virtualization works)
- [ ] User closes app mid-workout (state persists on reopen)

---

## 🎨 Visual QA Checklist

### Light Mode
- [ ] Teal primary color (#00BCD4) used consistently
- [ ] Orange-red accent (#FF5722) used for PR badges (if applicable)
- [ ] White background (#FFFFFF), off-white cards (#F5F5F5)
- [ ] Black text (#212121) has 16:1 contrast on white
- [ ] Completed set rows have light green tint (#E8F5E9)

### Dark Mode
- [ ] Indigo primary color (#5C6BC0) used consistently
- [ ] Yellow-orange accent (#FFB300) used for PR badges
- [ ] True black background (#121212), dark gray cards (#1E1E1E)
- [ ] White text (#FFFFFF) has 21:1 contrast on black
- [ ] Completed set rows have dark green tint (#1B3A1F)

### Spacing & Touch Targets
- [ ] All interactive elements ≥44px tall (iOS) / 48px (Android)
- [ ] Consistent 16px padding on cards
- [ ] 24px spacing between exercise cards
- [ ] 8px spacing between related elements (set # and inputs)

---

**End of Component Specifications**

*For questions or clarification, contact UX Expert Sally or reference the Design System document (`docs/design-system.md`).*
