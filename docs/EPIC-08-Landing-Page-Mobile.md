# EPIC-08: Landing Page Mobile Responsiveness

**Status:** 📋 Planned
**Priority:** P0 (Critical for production launch)
**Timeline:** Week 6 (Post-MVP, Pre-Launch)
**Points:** 23 | **Stories:** 6

---

## 🎯 Epic Goal

Fix mobile responsiveness issues on landing page to ensure production-ready experience across all device sizes, from iPhone to desktop.

## 🔍 Problem Statement

**Current State:**
Landing page looks "fucking FIRE 🔥" on desktop and tablet, but has critical mobile UX issues:

1. **Hero mockup cut off** - Only half visible on mobile screens
2. **Table too wide** - "Old Way vs Swae Way" table has excessive gutters on iPhone
3. **Tiles squished** - "Habits & Programs" tiles cramped horizontally
4. **Two-column overflow** - Journaling, Meals, Movements sections don't adapt to mobile

**Impact:**
- Not acceptable for production deployment
- Mobile users (majority of traffic) get poor first impression
- Beautiful design undermined by layout issues

**User Feedback:**
> "still pretty sick actually but not acceptable for prod"

## 💡 Solution Overview

Optimize mobile layouts while preserving desktop/tablet beauty:

### Mobile-First Responsive Strategy

1. **Hero Section**
   - Move mockup partially below the fold (like interlinear.peleke.me)
   - Maintain visibility and impact on all screen sizes

2. **Table Optimization**
   - Keep table format but remove excessive gutters on mobile
   - Preserve desktop/tablet appearance

3. **Tile Sections Vertical Stack**
   - Convert horizontal cramped tiles to vertical stacks
   - Better use of mobile real estate
   - Strategic content reduction where needed

4. **Enhanced Visual Design**
   - Replace flat white card backgrounds with prettier colors
   - Maintain visual hierarchy and accessibility

## 📊 Success Metrics

- ✅ Hero mockup fully visible on iPhone SE (375px width)
- ✅ Table readable without horizontal scroll on iPhone
- ✅ All tiles readable without text truncation
- ✅ Card backgrounds visually appealing (not flat white)
- ✅ Zero layout regressions on desktop/tablet (768px+)
- ✅ Lighthouse mobile score >90

## 🗂️ Stories Breakdown

### Story 1: Hero Mockup Mobile Responsiveness
**Points:** 5 | **Priority:** P0 (Blocks production)

**Description:**
Fix hero section mockup image being cut off on mobile screens. Move mockup partially below the fold similar to interlinear.peleke.me reference.

**Acceptance Criteria:**
- [ ] Hero mockup fully visible on iPhone SE (375px width)
- [ ] Mockup fully visible on iPhone 14 Pro (430px width)
- [ ] Desktop/tablet hero layout unchanged
- [ ] Mockup positioned partially below fold on mobile
- [ ] Smooth transition between mobile and desktop layouts
- [ ] User will provide reference screenshots for final positioning

**Technical Notes:**
```css
/* Pseudo-code approach */
@media (max-width: 768px) {
  .hero-mockup {
    /* Adjust positioning, potentially reduce size */
    /* Move below fold while keeping visible */
  }
}
```

**Files to Update:**
- Landing page hero section component
- Responsive breakpoints configuration
- Hero section CSS/Tailwind classes

**Dependencies:**
- Waiting on user screenshots for exact positioning

**Testing:**
- [ ] iPhone SE (375px)
- [ ] iPhone 14 Pro (430px)
- [ ] iPad (768px)
- [ ] Desktop (1280px+)

---

### Story 2: Old Way vs Swae Way Table Mobile Optimization
**Points:** 3 | **Priority:** P1

**Description:**
Remove excessive gutter/margin between table columns on iPhone screens while maintaining table format and desktop appearance.

**Acceptance Criteria:**
- [ ] Table columns readable on iPhone without horizontal scroll
- [ ] Reduced gutter/margin between columns on mobile
- [ ] Desktop/tablet table appearance unchanged
- [ ] Table remains accessible (readable text, clear structure)
- [ ] Touch targets adequate for mobile (min 44px)

**Technical Notes:**
```css
/* Reduce column spacing on mobile */
@media (max-width: 640px) {
  .comparison-table {
    column-gap: 0.5rem; /* Reduced from larger desktop gap */
  }

  .table-cell {
    padding: 0.5rem; /* Tighter cell padding */
  }
}
```

**Files to Update:**
- Old Way vs Swae Way table component
- Table responsive styles

**Testing:**
- [ ] iPhone SE - No horizontal scroll
- [ ] iPhone 14 Pro - Comfortable reading
- [ ] Desktop - No regression

---

### Story 3: Habits & Programs Tiles Vertical Stack
**Points:** 3 | **Priority:** P1

**Description:**
Convert "Habits & Programs" from 4 horizontal squished tiles to 3 vertically stacked tiles with bullet text formatting.

**Acceptance Criteria:**
- [ ] 3 tiles displayed vertically on mobile (not 4)
- [ ] Text formatted with bullets
- [ ] Tiles use full mobile width effectively
- [ ] One tile strategically removed (decide which)
- [ ] Desktop/tablet horizontal layout unchanged
- [ ] Smooth responsive transition

**Technical Notes:**
```jsx
// Pseudo-code
const tiles = [
  { title: "...", content: "..." }, // Keep
  { title: "...", content: "..." }, // Keep
  { title: "...", content: "..." }, // Keep
  // { title: "...", content: "..." }, // Remove - TBD
]

// Mobile: flex-col, Desktop: flex-row
<div className="flex flex-col md:flex-row gap-4">
  {tiles.map(tile => (
    <TileCard>
      <h3>{tile.title}</h3>
      <ul className="list-disc ml-4">
        {tile.bulletPoints.map(point => <li>{point}</li>)}
      </ul>
    </TileCard>
  ))}
</div>
```

**Decision Needed:**
- Which of the 4 tiles to remove? (Least important content)

**Files to Update:**
- Habits & Programs section component
- Tile layout component

**Testing:**
- [ ] Mobile - 3 vertical tiles
- [ ] Desktop - Horizontal layout preserved

---

### Story 4: Journaling & Insights Single Column with Styled Cards
**Points:** 5 | **Priority:** P1

**Description:**
Convert Journaling & Insights from two-column to single-column on mobile, preferring card renders ("Morning gratitude" etc.) over bullet points, with prettier background colors.

**Acceptance Criteria:**
- [ ] Single column layout on mobile
- [ ] Card renders preferred over bullet points
- [ ] Card backgrounds use attractive colors (not flat white)
- [ ] Card renders: "Morning gratitude", etc. displayed prominently
- [ ] Desktop two-column layout unchanged
- [ ] Color scheme matches overall landing page design
- [ ] Accessible color contrast (WCAG AA minimum)

**Technical Notes:**
```jsx
// Card with gradient background
<div className="bg-gradient-to-br from-purple-50 to-indigo-100
                dark:from-purple-900/20 dark:to-indigo-900/20
                p-6 rounded-lg shadow-sm">
  <h4 className="font-semibold mb-2">Morning Gratitude</h4>
  <p className="text-sm text-gray-600 dark:text-gray-300">
    Start your day reflecting on what you're grateful for
  </p>
</div>

// Mobile: single column, Desktop: two columns
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  {cards.map(card => <JournalingCard {...card} />)}
</div>
```

**Color Palette Ideas:**
- Soft gradients: purple-to-indigo, blue-to-cyan, pink-to-rose
- Avoid: Pure white (#FFFFFF)
- Maintain: Dark mode support

**Files to Update:**
- Journaling & Insights section component
- Card component with background styling

**Testing:**
- [ ] Mobile - Single column card renders
- [ ] Desktop - Two column preserved
- [ ] Color contrast passes WCAG AA
- [ ] Dark mode colors work

---

### Story 5: Meals Single Column with Styled Cards
**Points:** 5 | **Priority:** P1

**Description:**
Convert Meals section from two-column to single-column on mobile, preferring card renders over bullet points, with prettier background colors.

**Acceptance Criteria:**
- [ ] Single column layout on mobile
- [ ] Card renders preferred over bullet points
- [ ] Card backgrounds use attractive colors (not flat white)
- [ ] Meal cards prominently displayed
- [ ] Desktop two-column layout unchanged
- [ ] Color scheme complements Journaling section colors
- [ ] Accessible color contrast (WCAG AA minimum)

**Technical Notes:**
```jsx
// Meal card with complementary gradient
<div className="bg-gradient-to-br from-green-50 to-emerald-100
                dark:from-green-900/20 dark:to-emerald-900/20
                p-6 rounded-lg shadow-sm">
  <h4 className="font-semibold mb-2">Breakfast Ideas</h4>
  <p className="text-sm text-gray-600 dark:text-gray-300">
    Nutritious morning meals to fuel your day
  </p>
</div>
```

**Color Palette Ideas:**
- Food-related: green-to-emerald, orange-to-amber, yellow-to-lime
- Coordinate with Journaling section colors
- Different enough to distinguish sections

**Files to Update:**
- Meals section component
- Meal card component with background styling

**Testing:**
- [ ] Mobile - Single column card renders
- [ ] Desktop - Two column preserved
- [ ] Color contrast passes WCAG AA
- [ ] Dark mode colors work

---

### Story 6: Movements Bullet Points Mobile Layout
**Points:** 2 | **Priority:** P1

**Description:**
Convert Movements section from two-column to single-column bullet list on mobile. Use bullet points only (simpler than Journaling/Meals card approach).

**Acceptance Criteria:**
- [ ] Single column layout on mobile
- [ ] Bullet point format (not card renders)
- [ ] Bullets formatted with proper spacing and indentation
- [ ] Desktop two-column layout unchanged
- [ ] Clear, readable text on mobile

**Technical Notes:**
```jsx
// Simple bullet list on mobile, two columns on desktop
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div>
    <h3 className="font-semibold mb-3">Morning Movements</h3>
    <ul className="list-disc ml-5 space-y-2">
      <li>Stretching routine</li>
      <li>Light cardio</li>
      <li>Mobility exercises</li>
    </ul>
  </div>
  <div>
    <h3 className="font-semibold mb-3">Evening Movements</h3>
    <ul className="list-disc ml-5 space-y-2">
      <li>Cool-down stretches</li>
      <li>Relaxation exercises</li>
    </ul>
  </div>
</div>
```

**Files to Update:**
- Movements section component
- Bullet list styling

**Testing:**
- [ ] Mobile - Single column bullets
- [ ] Desktop - Two column preserved
- [ ] Proper list formatting

---

## 🔗 Dependencies & Risks

### External Dependencies
- **User Screenshots** - Story 1 waiting on reference images for hero positioning
- **Design Review** - Card color choices need approval (Stories 4, 5)

### Internal Dependencies
- None - All stories can proceed in parallel after dependencies resolved

### Risks

**High Risk:**
- Desktop/tablet regressions → Comprehensive responsive testing required
- Color accessibility failures → WCAG AA compliance testing mandatory

**Medium Risk:**
- Tile content removal decision (Story 3) → User/stakeholder input needed
- Color scheme conflicts → Design system review needed

**Low Risk:**
- Performance impact from new gradients → Lighthouse testing

---

## 📱 Responsive Testing Checklist

All stories must be tested on:

### Mobile Devices
- [ ] iPhone SE (375px width) - Smallest modern iPhone
- [ ] iPhone 14 Pro (430px width) - Current flagship
- [ ] Android Medium (360px width) - Common Android size

### Tablet Devices
- [ ] iPad (768px width) - Common tablet breakpoint
- [ ] iPad Pro (1024px width) - Large tablet

### Desktop
- [ ] Desktop (1280px width) - Common laptop
- [ ] Desktop XL (1920px width) - Full HD monitor

### Testing Tools
- Chrome DevTools responsive mode
- Real device testing (recommended)
- BrowserStack for cross-browser validation

---

## 🎨 Design System Integration

### Color Palette for Cards

**Journaling & Insights:**
- Light mode: `from-purple-50 to-indigo-100`
- Dark mode: `from-purple-900/20 to-indigo-900/20`

**Meals:**
- Light mode: `from-green-50 to-emerald-100`
- Dark mode: `from-green-900/20 to-emerald-900/20`

**Alternative Options:**
- Blue: `from-blue-50 to-cyan-100`
- Pink: `from-pink-50 to-rose-100`
- Orange: `from-orange-50 to-amber-100`

**Requirements:**
- WCAG AA contrast ratio (4.5:1 for text)
- Dark mode variants with reduced opacity
- Consistent with existing brand colors

---

## ✅ Definition of Done

A story is **NOT DONE** until:

1. ✅ Acceptance criteria met
2. ✅ Tested on all required device sizes
3. ✅ No desktop/tablet regressions
4. ✅ Color contrast passes WCAG AA
5. ✅ Dark mode works correctly
6. ✅ Lighthouse mobile score >90
7. ✅ Code reviewed and approved
8. ✅ User/stakeholder approval (especially colors)

---

## 📊 Story Summary

| Story | Description | Points | Priority | Dependencies |
|-------|-------------|--------|----------|--------------|
| 1 | Hero Mockup Mobile Responsiveness | 5 | P0 | User screenshots |
| 2 | Old Way vs Swae Way Table Mobile | 3 | P1 | None |
| 3 | Habits & Programs Tiles Vertical | 3 | P1 | Content decision |
| 4 | Journaling & Insights Styled Cards | 5 | P1 | Color approval |
| 5 | Meals Styled Cards | 5 | P1 | Color approval |
| 6 | Movements Bullet Points Mobile | 2 | P1 | None |

**Total: 23 points across 6 stories**

**Critical Path:** Story 1 (blocks production) → Stories 2-6 (can be parallel)

---

## 🎯 Epic Milestone

**Week 6 Complete When:**
- Hero visible on all mobile devices
- All sections responsive and readable
- Card backgrounds visually appealing
- Zero desktop/tablet regressions
- Production-ready landing page

---

## 🚀 Implementation Order

**Phase 1 (P0 - Blocks Production):**
1. Story 1: Hero Mockup (waiting on screenshots)

**Phase 2 (P1 - Can proceed in parallel):**
2. Story 2: Table optimization (no dependencies)
3. Story 3: Tiles vertical stack (need content decision)
4. Story 6: Movements bullets (simple, no dependencies)

**Phase 3 (P1 - Requires design approval):**
5. Story 4: Journaling cards (after color approval)
6. Story 5: Meals cards (after color approval)

---

## 📞 Questions or Blockers?

**For Story 1 (Hero):**
- Waiting on user screenshots for exact positioning
- Reference: interlinear.peleke.me

**For Story 3 (Tiles):**
- Which tile to remove? (Need decision)

**For Stories 4 & 5 (Cards):**
- Approve color palette
- Confirm gradient approach vs solid colors

**User Feedback:**
> "OVERALL, this is fucking FIRE I'm so impressed. amazing work."

**Goal:** Maintain that fire while making it production-ready 🔥
