# Epic 8: Chat UI Implementation

**Epic ID:** EPIC-8
**Status:** Draft
**Priority:** P1 (Month 3 Feature - Post-Alpha Validation)
**Estimated Effort:** 12-16 hours
**Story Points:** 18

---

## Epic Goal

Build mobile-first chat interface with progressive onboarding flow, quick reply buttons, resume functionality, and completion screens - making conversational profiling feel natural and motivating.

---

## Business Value

**Problem:** Traditional form-based onboarding feels tedious and has low completion rates (~30%). Users want chat-native experiences (familiar with ChatGPT, AI assistants).

**Solution:** Build iMessage-style chat UI where users answer questions through natural conversation with quick reply buttons for predefined options.

**Impact:**
- Increases profile completion rate to target 80%+ (chat feels easier than forms)
- Reduces cognitive load (one question at a time vs. overwhelming form page)
- Enables mid-conversation exit + resume (users can complete at their own pace)
- Sets foundation for future chat-based features (AI coach check-ins, adaptive re-profiling)

---

## Linked Requirements

- **FR1:** Conversation Trigger Logic
- **FR2:** Vertical Selection Flow
- **FR3:** Workouts/Movement Profiling Interview
- **FR5:** Skip & Partial Profile Handling
- **FR6:** Resume Interrupted Conversation

---

## User Stories

### Story 8.1: Chat UI Component
**File:** `docs/stories/8.1-chat-ui-component.md`
**Points:** 8
**Estimate:** ~4-6 hours

**As a** mobile developer
**I want** a chat UI component for conversational onboarding
**So that** users can interact with the agent naturally

---

### Story 8.2: Onboarding Launch & Completion Screens
**File:** `docs/stories/8.2-onboarding-launch-completion.md`
**Points:** 5
**Estimate:** ~3-4 hours

**As a** mobile developer
**I want** launch and completion screens to frame the onboarding conversation
**So that** users understand what's happening and feel motivated to complete

---

### Story 8.3: Resume Functionality UI
**File:** `docs/stories/8.3-resume-functionality-ui.md`
**Points:** 5
**Estimate:** ~2-3 hours

**As a** user
**I want** to see a banner reminding me to complete my profile
**So that** I can easily resume the conversation I started

---

## Technical Assumptions

**Frontend Stack:**
- React Native with Expo (existing)
- TypeScript with fp-ts
- WebSocket client: `socket.io-client` for real-time messaging
- Chat UI: Custom implementation with FlatList or `react-native-gifted-chat` library

**Validated:**
- ✅ Expo app supports WebSocket connections
- ✅ Supabase auth SDK provides JWT for agent authentication
- ✅ Expo Notifications API supports push notifications (for reminders)

**Dependencies:**
- Modal agent service WebSocket endpoint (from Epic 6)
- Supabase auth (existing)

---

## Success Criteria

- [ ] Chat interface loads in <1 second on 4G network
- [ ] Agent messages appear on left, user messages on right (iMessage-style)
- [ ] Quick reply buttons work for predefined options (eating preferences, training modalities)
- [ ] Typing indicator shows when agent is "thinking"
- [ ] Launch screen explains "This will take 2 minutes"
- [ ] Completion screen shows confetti + personalized calorie target
- [ ] Resume banner appears in home screen for incomplete profiles
- [ ] Push notification sent 24 hours after skip

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| WebSocket connection unstable on poor networks | Medium | Medium | Implement reconnection logic; fallback to REST polling if WS fails |
| Chat UI library conflicts with existing styles | Medium | Medium | Use custom implementation if library causes issues; isolate chat styles |
| Confetti animation causes performance issues on older devices | Low | Low | Use lightweight library (`react-native-confetti-cannon`); test on low-end Android |

---

## Dependencies

**Blockers:**
- Epic 6 (requires WebSocket endpoint URL from Modal deployment)

**Blocks:**
- Epic 9 (Conversation orchestration requires chat UI for user testing)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-20 | v1.0 | Initial epic creation from Onboarding Agent PRD | Mary (Business Analyst) |
