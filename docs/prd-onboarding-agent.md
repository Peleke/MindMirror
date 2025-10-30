# Product Requirements Document (PRD)
## AI-Powered Onboarding Agent System

**Document Version:** v1.0
**Last Updated:** 2025-10-20
**Product Manager:** Mary (Business Analyst Agent)
**Status:** Draft - Ready for Review

---

## Table of Contents

1. [Goals and Background Context](#1-goals-and-background-context)
2. [Requirements](#2-requirements)
3. [UI Design Goals](#3-ui-design-goals)
4. [Technical Assumptions](#4-technical-assumptions)
5. [Epic List](#5-epic-list)
6. [Epic Details with User Stories](#6-epic-details-with-user-stories)
7. [Open Questions & Risks](#7-open-questions--risks)
8. [Next Steps](#8-next-steps)

---

## 1. Goals and Background Context

### 1.1 Executive Summary

The **AI-Powered Onboarding Agent System** introduces conversational, chat-native user profiling to MindMirror, replacing manual form-based data collection with an intelligent interview experience. This feature bridges the gap between signup and personalized program delivery by extracting structured user profiles through natural conversation.

**Primary Goal:** Implement a conversational onboarding agent that collects user profiles (eating preferences, movement goals) in 1-3 minutes, stores federated profile data across services, and enables personalized program recommendations and UI customization.

**Timeline:** Post-Alpha Validation (Month 3 feature as per main PRD)
- **Phase 1 (MVP):** Workouts/practices vertical only - 2-3 weeks
- **Phase 2 (Expansion):** Multi-vertical support (eating, sleep, mindfulness) - deferred

### 1.2 Problem Statement

Current MindMirror onboarding relies on voucher-based auto-enrollment where coaches/admins manually assign programs. This approach has limitations:

1. **No user personalization** - Programs assigned without knowledge of user goals, injuries, or preferences
2. **Admin bottleneck** - Manual program assignment doesn't scale beyond alpha users
3. **Generic UI experience** - App can't display personalized calorie targets, macro recommendations, or training adaptations without profile data
4. **Poor user engagement** - Users don't feel "seen" by the system; no sense of AI understanding their unique needs

### 1.3 Solution Overview

A **two-agent conversational system** that activates on first user login:

**Agent A: Profiling Bot** (Alpha Priority)
- Conducts 1-3 minute conversational interview
- Extracts structured user profiles (eating + movement for MVP)
- Stores federated profiles across microservices (users_service orchestrates)
- Enables UI personalization (calorie targets, macro recommendations)

**Agent B: Onboarding Coach** (Deferred/Lower Priority)
- Shares profiling results with user
- Provides tooltip tutorial for app navigation
- Minimal backend integration (UI-focused)

### 1.4 Target Users

**Primary:** New MindMirror users (post-signup, pre-first workout)
- Age range: 25-50
- Fitness experience: Beginner to intermediate
- Tech comfort: Expects chat-native experiences (familiar with ChatGPT, AI assistants)
- Pain points: Overwhelmed by traditional fitness app form fields; wants guidance

**Secondary:** Existing users adding new vertical domains
- Example: User started with workouts, now wants to add nutrition tracking
- Needs: Quick re-onboarding for new domain without repeating basic info (name, etc.)

### 1.5 Success Metrics

**Green Light (MVP Success):**
- 80%+ users complete onboarding conversation (not skip)
- Average completion time: 1-3 minutes
- Profile extraction accuracy: >90% (validated via spot-check of 20 conversations)
- Users can resume interrupted conversations without friction
- UI correctly displays derived values (calorie targets, macro split) based on extracted profiles

**Yellow Light (Iterate Before Scaling):**
- 60-80% completion rate
- Conversation feels stilted or robotic (qualitative feedback)
- Profile extraction accuracy: 70-90%
- Users confused about how to resume interrupted conversations

**Red Light (Redesign Required):**
- <60% completion rate
- Users prefer to skip and fill forms manually
- Profile extraction accuracy: <70%
- Technical issues (API timeouts, state management failures)

### 1.6 MVP Scope (In Scope for Phase 1)

**Core Functionality:**
- ✅ Conversational UI (chat interface in mobile app)
- ✅ Name collection + vertical selection ("What would you like to set up?")
- ✅ Workouts/practices vertical interview (eating + movement profiles)
- ✅ Profile extraction via PydanticAI (structured output)
- ✅ Federated profile storage (users_service orchestrates, domain services store)
- ✅ Skip functionality (create partial profiles with nulls)
- ✅ Resume functionality (pick up where user left off)
- ✅ Notification reminder for incomplete profiles
- ✅ Logfire observability (conversation quality, extraction accuracy)

**Eating Profile Fields (Alpha):**
- Weight, height
- Eating preferences (vegetarian, pescatarian, omnivore, etc.)
- Derived values: Calorie targets, macronutrient split (calculated server-side)

**Movement Profile Fields (Alpha):**
- Training preferences (preferred modality/sport: strength training, running, yoga, etc.)
- Goals (build muscle, lose weight, improve endurance, rehab/injury prevention)

**Deferred to Post-Alpha:**
- Injuries and movement restrictions (needs better data modeling)
- Multi-vertical onboarding (eating, sleep, mindfulness in one session)
- Agent B: Onboarding Coach tutorial
- Advanced conversation features (clarifying questions, back-tracking, conversational edits)

### 1.7 Out of Scope (Future Enhancements)

**Month 6+ Features:**
- Voice-based onboarding (speech-to-text)
- Photo-based profiling (CV analysis of user physique for goals inference)
- Adaptive re-profiling (periodic check-ins to update goals)
- Integration with wearables (auto-populate weight, activity level)
- Multi-language support

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1: Conversation Trigger Logic**
System shall automatically trigger onboarding conversation on first user login (no previous session exists).

**Acceptance Criteria:**
- User completes Supabase auth signup → opens app for first time → onboarding agent launches before main app UI
- Check for existing `user_profile` record in users_service (if exists, skip onboarding)
- Users can manually re-trigger onboarding via "Complete Profile" button in settings (if partial profile exists)
- No onboarding trigger for users with completed profiles (all required fields populated)

---

**FR2: Vertical Selection Flow**
Agent shall ask user to select which "vertical" (domain) to set up before starting domain-specific questions.

**Acceptance Criteria:**
- First question: "What's your name?" (store in user profile)
- Second question: "What would you like to set up today?" with options:
  - Workouts & Movement (only option for alpha)
  - Eating & Nutrition (disabled, "Coming soon" label)
  - Sleep & Recovery (disabled, "Coming soon" label)
  - Mindfulness & Practices (disabled, "Coming soon" label)
- User selects "Workouts & Movement" → proceeds to movement profiling questions
- Future: Multi-select enabled for post-alpha (one vertical at a time for MVP)

---

**FR3: Workouts/Movement Profiling Interview**
Agent shall conduct conversational interview to extract eating and movement profiles.

**Acceptance Criteria:**
- **Eating Profile Questions:**
  - "What's your current weight?" (numeric input with unit selection: lbs/kg)
  - "What's your height?" (numeric input with unit selection: ft+in / cm)
  - "Do you have any eating preferences?" (options: Omnivore, Vegetarian, Vegan, Pescatarian, Other)
- **Movement Profile Questions:**
  - "What type of training do you prefer?" (options: Strength training, Running, Yoga, CrossFit, Sports-specific, Mixed/variety)
  - "What are your primary fitness goals?" (multi-select: Build muscle, Lose fat, Improve endurance, Rehab/injury prevention, General health)
- Conversation feels natural (not form-like); agent can rephrase questions if user seems confused
- Agent confirms extracted values before finalizing: "Just to confirm, you're 5'10", 180 lbs, prefer strength training, and want to build muscle. Is that right?"

---

**FR4: Profile Extraction & Storage**
Agent shall extract structured profiles from conversation and store in federated microservices.

**Acceptance Criteria:**
- PydanticAI extracts structured data from conversation:
  ```python
  class EatingProfile(BaseModel):
      weight: float
      weight_unit: Literal["lbs", "kg"]
      height: float
      height_unit: Literal["ft_in", "cm"]
      eating_preference: Literal["omnivore", "vegetarian", "vegan", "pescatarian", "other"]

  class MovementProfile(BaseModel):
      training_preference: List[str]  # ["strength_training", "yoga"]
      goals: List[str]  # ["build_muscle", "lose_fat"]
  ```
- users_service receives profiles and delegates storage:
  - `POST /users/{user_id}/profiles/eating` → meals_service stores eating_profile
  - `POST /users/{user_id}/profiles/movement` → movements_service stores movement_profile
- users_service acts as orchestrator (hub pattern):
  - `GET /users/{user_id}/profiles` returns aggregated profiles from all services
- Derived values calculated server-side:
  - Calorie target: Harris-Benedict equation based on weight, height, age (from auth), activity level (inferred from training preference)
  - Macro split: Default 40/30/30 (protein/carbs/fat) for "build muscle" goal; adjustable in future

---

**FR5: Skip & Partial Profile Handling**
User shall be able to skip onboarding entirely or exit mid-conversation with partial profile saved.

**Acceptance Criteria:**
- "Skip for now" button always visible in chat UI (top-right corner)
- If user skips before providing any data → create empty user_profile record with `onboarding_status: skipped`
- If user exits mid-conversation → save partial profile with `onboarding_status: incomplete` + fields collected so far (nulls for missing)
- App allows access to main UI even with incomplete profile (no hard gate)
- Notification sent 24 hours after skip/incomplete: "Complete your profile to get personalized recommendations"

---

**FR6: Resume Interrupted Conversation**
User shall be able to resume incomplete onboarding from where they left off.

**Acceptance Criteria:**
- User re-opens app with `onboarding_status: incomplete` → sees "Resume Profile Setup" banner in home screen
- Tapping banner → chat UI loads with conversation history (previous questions/answers visible)
- Agent says: "Welcome back! Let's pick up where we left off. I still need to know [next question]"
- User can edit previous answers ("Actually, I'm 175 lbs, not 180") → agent updates profile
- Completing conversation updates `onboarding_status: complete`

---

**FR7: UI Personalization via Profiles**
App UI shall display personalized values derived from user profiles.

**Acceptance Criteria:**
- **Meals Dashboard:** Shows daily calorie target (e.g., "2,200 cal target") derived from eating profile
- **Meals Logging:** Shows macro progress bar (protein/carbs/fat split) based on derived targets
- **Workout Programs:** Filters available programs by training preference (e.g., hide yoga programs for strength training users)
- **Future:** Movement restrictions field → exercise substitutions (e.g., "Avoid squats due to knee injury" → suggest lunges)
- UI gracefully handles missing profile data (shows generic defaults, prompts to complete profile)

---

**FR8: Observability & Conversation Monitoring**
System shall log all conversations to Logfire for quality monitoring and debugging.

**Acceptance Criteria:**
- Every conversation logged with:
  - User ID, timestamp, conversation transcript (sanitized, no PII in plain text)
  - Extracted profile data (for accuracy validation)
  - Completion status (completed, skipped, incomplete)
  - Duration (start to finish)
- Logfire dashboard shows:
  - Completion rate (completed / total conversations)
  - Average duration
  - Common drop-off points (which question users exit on)
  - Extraction accuracy (manual spot-checks flagged for review)
- Alerts triggered for:
  - Conversation errors (API failures, extraction failures)
  - Unusually long conversations (>5 minutes, indicates confusion)
  - High skip rate (>40%, indicates UX problem)

---

### 2.2 Non-Functional Requirements

**NFR1: Performance**
- Onboarding conversation loads within 1 second on 4G network
- Agent response latency: <2 seconds per message (user types → agent responds)
- Profile extraction completes within 3 seconds of conversation end

**NFR2: Reliability**
- 99% uptime for onboarding agent service (separate from main app services)
- Conversation state persists even if user force-quits app
- Graceful degradation: If agent service unavailable, show "Onboarding temporarily unavailable, try again later" + allow skip

**NFR3: Scalability**
- System supports 100 concurrent onboarding conversations (Month 3 target: 250 users)
- PydanticAI agent deployed as serverless function (scales to zero when idle)
- Conversation history stored efficiently (no full transcript storage after profile extracted, only structured data)

**NFR4: Security**
- All conversations encrypted in transit (HTTPS/WSS for real-time chat)
- Profile data encrypted at rest (Supabase row-level security)
- No PII logged to Logfire in plain text (use user_id, not email/name)
- Conversation transcripts auto-deleted after 30 days (GDPR compliance prep)

**NFR5: Usability**
- Conversation feels natural (not robotic or form-like)
- User can complete onboarding in 1-3 minutes (avg 2 minutes)
- Mobile-first UI (optimized for thumb-typing on small screens)
- Accessibility: Screen reader compatible, high contrast mode support

**NFR6: Testability**
- Mock conversation scenarios for E2E testing (predefined user inputs → validate extraction)
- Manual test script for conversation quality review
- Logfire integration enables A/B testing of conversation prompts

---

## 3. UI Design Goals

### 3.1 Overall UX Vision

The onboarding conversation should feel like **texting a knowledgeable personal trainer** - friendly, efficient, and goal-oriented. Avoid clinical or robotic language; use casual, motivating tone.

**Design Principles:**
1. **Conversational, not form-based** - Questions feel like natural dialogue, not field labels
2. **Progressive disclosure** - One question at a time, not overwhelming
3. **Visual confirmation** - Show extracted data as cards/chips user can tap to edit
4. **Quick exit paths** - Always allow skip, never hard-gate
5. **Celebrate completion** - Confetti animation + "You're all set!" message at end

### 3.2 Key Interaction Paradigms

**Chat Interface:**
- Standard chat UI (messages on left/right like iMessage)
- Agent messages: Left-aligned, light gray bubble
- User messages: Right-aligned, blue bubble (brand color)
- Input field: Bottom sheet with text input + send button
- Typing indicator: "..." animation when agent is "thinking"

**Quick Reply Buttons:**
- For predefined options (eating preferences, training modalities), show buttons instead of forcing user to type
- Example: "What type of training do you prefer?" → [Strength] [Running] [Yoga] [Other] buttons
- User taps button → appears as user message bubble → agent responds

**Edit Previous Answers:**
- Agent confirmation message shows extracted data as editable cards:
  ```
  Agent: "Just to confirm:"
  [Card: Weight: 180 lbs] [Edit]
  [Card: Height: 5'10"] [Edit]
  [Card: Preference: Strength Training] [Edit]
  ```
- User taps "Edit" → re-opens that question for correction

**Progress Indicator:**
- Top of screen shows "2 of 5 questions" progress bar (not intrusive, just context)
- Helps user understand how long conversation will take

### 3.3 Core Screens and Views

1. **Onboarding Launch Screen**
   - Friendly mascot/illustration (AI coach character)
   - Headline: "Let's personalize your experience"
   - Subtext: "This will take about 2 minutes"
   - CTA: "Get Started" button
   - Link: "Skip for now" (bottom)

2. **Chat Conversation Screen**
   - Agent messages (questions)
   - User input (text or quick reply buttons)
   - Progress indicator (top)
   - Skip button (top-right)

3. **Confirmation Screen**
   - Shows extracted profile data as cards (editable)
   - CTA: "Looks good!" button
   - Link: "Go back to edit" (reopens chat)

4. **Completion Screen**
   - Confetti animation
   - "You're all set, [Name]!" headline
   - Summary: "Your personalized calorie target: 2,200/day"
   - CTA: "Start exploring" button → main app

5. **Resume Banner** (for incomplete profiles)
   - Persistent banner in home screen: "Complete your profile to unlock recommendations"
   - CTA: "Resume" button → reopens chat

### 3.4 Accessibility

**WCAG AA Compliance:**
- Color contrast ratio ≥4.5:1 for chat bubbles
- Touch targets ≥44px for buttons
- Screen reader labels for all interactive elements ("Agent message: What's your weight?")
- Support for system font scaling (respect user's text size preferences)

---

## 4. Technical Assumptions

### 4.1 Architecture Decision

**Agent Deployment:**
- **Option 1 (Recommended):** PydanticAI + FastAPI deployed on **Modal** (serverless, auto-scales, simple deployment)
  - Pros: No infrastructure management, pay-per-use, fast cold starts (<1s)
  - Cons: Vendor lock-in (but easy to migrate to in-cluster later)
- **Option 2:** PydanticAI + FastAPI as new microservice in Docker Compose (in-cluster)
  - Pros: Full control, consistent with existing architecture
  - Cons: More infra overhead, manual scaling management

**Decision for MVP:** Modal (Option 1) - optimize for speed of delivery, migrate to in-cluster post-validation if needed.

**Service Architecture:**
```
┌─────────────────────┐
│  Mobile App (Expo)  │
│  Chat UI            │
└──────────┬──────────┘
           │ WebSocket (real-time chat)
           ▼
┌─────────────────────┐
│  Onboarding Agent   │
│  (PydanticAI +      │
│   FastAPI on Modal) │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│  users_service      │
│  (Hub/Orchestrator) │
└──────────┬──────────┘
           │
     ┌─────┴──────┬────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│ meals_  │  │movements_│  │practices_│
│ service │  │ service  │  │ service  │
│ (eating │  │ (movement│  │ (habits) │
│ profile)│  │ profile) │  │          │
└─────────┘  └──────────┘  └──────────┘
```

### 4.2 Technology Stack

**Frontend (Mobile):**
- React Native with Expo (existing)
- TypeScript with fp-ts
- Chat UI: Custom components (or library like `react-native-gifted-chat` if time-constrained)
- WebSocket client: `socket.io-client` for real-time messaging
- Supabase Auth SDK (reuse existing auth)

**Backend (Onboarding Agent):**
- PydanticAI (structured extraction)
- FastAPI (WebSocket + REST endpoints)
- Modal (serverless deployment)
- Logfire (observability)

**Backend (Profile Storage):**
- users_service: New GraphQL mutations for profile CRUD
- meals_service: New `eating_profiles` table
- movements_service: New `movement_profiles` table
- PostgreSQL (existing databases, separate per service)

**Authentication:**
- Supabase JWT (existing) - user authenticated before onboarding starts
- Onboarding agent validates JWT on WebSocket connection

### 4.3 Storage Schema

**users_service (Hub):**
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  onboarding_status VARCHAR(20) NOT NULL, -- 'incomplete' | 'complete' | 'skipped'
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**meals_service:**
```sql
CREATE TABLE eating_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  weight DECIMAL(5,2),
  weight_unit VARCHAR(10), -- 'lbs' | 'kg'
  height DECIMAL(5,2),
  height_unit VARCHAR(10), -- 'ft_in' | 'cm'
  eating_preference VARCHAR(50), -- 'omnivore' | 'vegetarian' | 'vegan' | etc.
  calorie_target INT, -- derived value
  macro_split JSONB, -- {"protein": 40, "carbs": 30, "fat": 30}
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**movements_service:**
```sql
CREATE TABLE movement_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  training_preferences JSONB, -- ["strength_training", "yoga"]
  goals JSONB, -- ["build_muscle", "lose_fat"]
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.4 PydanticAI Configuration

**Model Selection:**
- **Primary:** OpenAI GPT-4o-mini (fast, cost-effective for extraction)
- **Fallback:** Anthropic Claude 3.5 Haiku (if OpenAI unavailable)

**Structured Output:**
```python
from pydantic import BaseModel
from pydantic_ai import Agent

class UserProfile(BaseModel):
    name: str
    eating_profile: EatingProfile
    movement_profile: MovementProfile

agent = Agent(
    'openai:gpt-4o-mini',
    result_type=UserProfile,
    system_prompt="""You are a friendly fitness coach conducting an onboarding interview.
    Ask one question at a time. Be casual and encouraging.
    Extract structured profile data from the conversation."""
)
```

**Conversation State Management:**
- Store conversation history in Redis (ephemeral, auto-expire after 7 days)
- Key: `onboarding:{user_id}:conversation`
- Value: JSON array of messages

---

## 5. Epic List

### Epic 1: Onboarding Agent Infrastructure
**Description:** Set up PydanticAI agent service on Modal with WebSocket support, conversation state management, and Logfire observability.

**Linked Requirements:** NFR1, NFR2, NFR3, NFR4, FR8

**Estimated Effort:** 6-10 hours

---

### Epic 2: Profile Storage & Federation
**Description:** Implement federated profile storage across users_service (hub), meals_service (eating profiles), and movements_service (movement profiles) with GraphQL API extensions.

**Linked Requirements:** FR4, FR7

**Estimated Effort:** 8-12 hours

---

### Epic 3: Chat UI Implementation
**Description:** Build mobile chat interface with conversation flow, quick reply buttons, edit functionality, and completion screens.

**Linked Requirements:** FR1, FR2, FR3, FR5, FR6

**Estimated Effort:** 12-16 hours

---

### Epic 4: Conversation Orchestration & Quality
**Description:** Implement conversation logic, profile extraction, confirmation flow, and resume functionality with quality assurance testing.

**Linked Requirements:** FR3, FR4, FR6, FR8

**Estimated Effort:** 8-12 hours

---

### Epic 5: UI Personalization Integration
**Description:** Connect extracted profiles to app UI (calorie targets, macro displays, program filtering) and build notification system for incomplete profiles.

**Linked Requirements:** FR7, FR5

**Estimated Effort:** 6-10 hours

---

**Total Estimated Effort:** 40-60 hours (2-3 weeks for one developer)

**Critical Path:** Epic 1 → Epic 2 → Epic 3 → Epic 4 → Epic 5

---

## 6. Epic Details with User Stories

### Epic 1: Onboarding Agent Infrastructure

**Epic Goal:** Establish serverless PydanticAI agent service with real-time chat capabilities and comprehensive observability.

---

#### Story 1.1: Modal Deployment Setup
**As a** platform engineer
**I want** PydanticAI + FastAPI agent deployed on Modal
**So that** the agent auto-scales and requires no infrastructure management

**Acceptance Criteria:**
- Modal project created with `modal setup`
- FastAPI app defined with `@app.function()` decorator
- WebSocket endpoint: `wss://[modal-url]/chat/{user_id}`
- REST endpoint: `POST /extract-profile` (for batch processing)
- Environment variables: `OPENAI_API_KEY`, `LOGFIRE_TOKEN`, `REDIS_URL`
- `modal deploy` completes successfully, returns public URL
- Health check endpoint: `GET /health` returns 200

**Implementation Notes:**
- Reference: https://modal.com/docs/guide/webhooks
- ~2-3 hours

**Story Points:** 5

---

#### Story 1.2: Conversation State Management (Redis)
**As a** developer
**I want** conversation history stored in Redis with auto-expiration
**So that** users can resume conversations and we don't store data indefinitely

**Acceptance Criteria:**
- Redis connection configured (use Upstash for serverless Redis)
- Key pattern: `onboarding:{user_id}:conversation`
- Value: JSON array of messages: `[{"role": "agent", "content": "What's your name?"}, {"role": "user", "content": "Alex"}]`
- TTL: 7 days (auto-delete after 1 week)
- Helper functions: `save_message(user_id, role, content)`, `get_conversation(user_id)`, `clear_conversation(user_id)`

**Implementation Notes:**
- Upstash Redis: https://upstash.com/docs/redis/overall/getstarted
- ~1-2 hours

**Story Points:** 3

---

#### Story 1.3: Logfire Integration
**As a** developer
**I want** all conversations logged to Logfire for monitoring and debugging
**So that** I can track completion rates, identify drop-off points, and debug extraction failures

**Acceptance Criteria:**
- Logfire SDK initialized in FastAPI app
- Events logged:
  - `onboarding.started` (user_id, timestamp)
  - `onboarding.message` (user_id, role, content_length, timestamp)
  - `onboarding.completed` (user_id, duration, extracted_profile)
  - `onboarding.skipped` (user_id, timestamp)
  - `onboarding.error` (user_id, error_type, stack_trace)
- Logfire dashboard shows:
  - Completion rate metric
  - Average duration metric
  - Drop-off funnel (which question users exit on)
- No PII logged in plain text (use user_id, not email/name)

**Implementation Notes:**
- Logfire docs: https://docs.pydantic.dev/logfire/
- ~2 hours

**Story Points:** 3

---

### Epic 2: Profile Storage & Federation

**Epic Goal:** Create federated profile storage architecture with users_service as orchestrator and domain services managing their profiles.

---

#### Story 2.1: users_service GraphQL API Extensions
**As a** backend engineer
**I want** users_service to orchestrate profile creation/retrieval across services
**So that** frontend has single API for all profile operations

**Acceptance Criteria:**
- GraphQL mutations:
  ```graphql
  mutation CreateUserProfile($input: UserProfileInput!) {
    createUserProfile(input: $input) {
      id
      userId
      name
      onboardingStatus
      eatingProfile {
        weight
        weightUnit
        calorieTarget
      }
      movementProfile {
        trainingPreferences
        goals
      }
    }
  }

  mutation UpdateOnboardingStatus($userId: ID!, $status: String!) {
    updateOnboardingStatus(userId: $userId, status: $status) {
      id
      onboardingStatus
    }
  }
  ```
- GraphQL queries:
  ```graphql
  query GetUserProfile($userId: ID!) {
    userProfile(userId: $userId) {
      id
      name
      onboardingStatus
      eatingProfile { ... }
      movementProfile { ... }
    }
  }
  ```
- users_service makes REST calls to meals_service and movements_service to fetch/store sub-profiles
- Handles partial profiles gracefully (nulls for missing fields)

**Implementation Notes:**
- Add to `users_service/app/graphql/resolvers.py`
- ~4-5 hours

**Story Points:** 8

---

#### Story 2.2: meals_service Eating Profile Storage
**As a** backend engineer
**I want** meals_service to store and serve eating profiles
**So that** eating preferences and calorie targets are managed in the appropriate domain service

**Acceptance Criteria:**
- New table: `eating_profiles` (schema in Technical Assumptions section)
- REST endpoints:
  - `POST /eating-profiles` (create)
  - `GET /eating-profiles/{user_id}` (read)
  - `PUT /eating-profiles/{user_id}` (update)
- Calorie target calculation:
  - Harris-Benedict equation: BMR based on weight, height, age
  - Activity multiplier inferred from training preference (sedentary=1.2, moderate=1.5, active=1.7)
  - Example: 180 lbs, 5'10", age 30, strength training → ~2,200 cal/day
- Macro split defaults:
  - Build muscle goal: 40% protein, 30% carbs, 30% fat
  - Lose fat goal: 35% protein, 35% carbs, 30% fat
  - General health: 30% protein, 40% carbs, 30% fat

**Implementation Notes:**
- Add to `meals_service/app/routes.py`
- ~3-4 hours

**Story Points:** 5

---

#### Story 2.3: movements_service Movement Profile Storage
**As a** backend engineer
**I want** movements_service to store training preferences and goals
**So that** workout programs can be filtered/recommended based on user profile

**Acceptance Criteria:**
- New table: `movement_profiles` (schema in Technical Assumptions section)
- REST endpoints:
  - `POST /movement-profiles` (create)
  - `GET /movement-profiles/{user_id}` (read)
  - `PUT /movement-profiles/{user_id}` (update)
- Training preferences stored as JSONB array: `["strength_training", "yoga"]`
- Goals stored as JSONB array: `["build_muscle", "improve_flexibility"]`

**Implementation Notes:**
- Add to `movements_service/app/routes.py`
- ~2-3 hours

**Story Points:** 3

---

### Epic 3: Chat UI Implementation

**Epic Goal:** Build mobile-first chat interface with progressive onboarding flow and resume functionality.

---

#### Story 3.1: Chat UI Component
**As a** mobile developer
**I want** a chat UI component for conversational onboarding
**So that** users can interact with the agent naturally

**Acceptance Criteria:**
- Chat interface with message list (scrollable, auto-scroll to latest)
- Agent messages: Left-aligned, light gray bubble, agent icon
- User messages: Right-aligned, blue bubble (brand color)
- Input field: Bottom sheet with text input + send button
- Typing indicator: "..." animation when agent is composing response
- Quick reply buttons for predefined options (eating preferences, training modalities)
- Supports keyboard dismissal on scroll
- Works on iOS and Android (React Native)

**Implementation Notes:**
- Consider `react-native-gifted-chat` library for faster implementation
- Or custom implementation with FlatList + styled components
- ~4-6 hours

**Story Points:** 8

---

#### Story 3.2: Onboarding Launch & Completion Screens
**As a** mobile developer
**I want** launch and completion screens to frame the onboarding conversation
**So that** users understand what's happening and feel motivated to complete

**Acceptance Criteria:**
- **Launch Screen:**
  - Friendly illustration (AI coach character or abstract fitness graphic)
  - Headline: "Let's personalize your experience"
  - Subtext: "This will take about 2 minutes"
  - CTA: "Get Started" button → opens chat
  - Link: "Skip for now" → creates skipped profile, goes to main app
- **Completion Screen:**
  - Confetti animation (use `react-native-confetti-cannon`)
  - "You're all set, [Name]!" headline
  - Summary card: "Your personalized calorie target: 2,200/day"
  - CTA: "Start exploring" → main app home screen

**Implementation Notes:**
- Screens: `app/(onboarding)/launch.tsx`, `app/(onboarding)/chat.tsx`, `app/(onboarding)/complete.tsx`
- ~3-4 hours

**Story Points:** 5

---

#### Story 3.3: Resume Functionality UI
**As a** user
**I want** to see a banner reminding me to complete my profile
**So that** I can easily resume the conversation I started

**Acceptance Criteria:**
- Home screen checks `onboarding_status` from user profile
- If `status === 'incomplete'`, show banner at top:
  - Text: "Complete your profile to unlock personalized recommendations"
  - CTA: "Resume" button
  - Dismissible: "X" button (but reappears on next app open until completed)
- Tapping "Resume" → opens chat UI with conversation history pre-loaded
- Agent welcomes user back: "Welcome back, [Name]! Let's pick up where we left off."
- Push notification sent 24 hours after incomplete status: "Finish setting up your profile!"

**Implementation Notes:**
- Banner component: `components/OnboardingBanner.tsx`
- Notification: Use Expo Notifications API
- ~2-3 hours

**Story Points:** 5

---

### Epic 4: Conversation Orchestration & Quality

**Epic Goal:** Implement intelligent conversation flow with profile extraction and quality assurance.

---

#### Story 4.1: Conversation Flow Logic
**As a** developer
**I want** PydanticAI agent to guide users through onboarding questions
**So that** the conversation feels natural and extracts required profile data

**Acceptance Criteria:**
- Conversation sequence:
  1. "Hi! I'm here to help you get the most out of MindMirror. What's your name?"
  2. "Great to meet you, [Name]! What would you like to set up today?" [Workouts & Movement] button
  3. (Eating questions) "Let's start with a few basics. What's your current weight?" (numeric input + unit selector)
  4. "And your height?" (numeric input + unit selector)
  5. "Do you have any eating preferences?" [Omnivore] [Vegetarian] [Vegan] [Pescatarian] [Other] buttons
  6. (Movement questions) "What type of training do you prefer?" [Strength] [Running] [Yoga] [Mixed] buttons
  7. "What are your fitness goals?" [Build muscle] [Lose fat] [Endurance] [Rehab] (multi-select)
  8. Confirmation: "Just to confirm:" [editable cards]
  9. "You're all set!" → completion screen
- Agent handles edge cases:
  - User provides invalid input ("I weigh potato") → "I didn't catch that. Could you share your weight in pounds or kilograms?"
  - User asks off-topic question ("What's the weather?") → "I'm here to help with your fitness profile. Let's get back to the questions - what's your weight?"
- Progress indicator updates after each question (1 of 7, 2 of 7, etc.)

**Implementation Notes:**
- PydanticAI agent with state machine or prompt-based flow
- ~4-5 hours

**Story Points:** 8

---

#### Story 4.2: Profile Extraction with PydanticAI
**As a** developer
**I want** structured profile data extracted from conversation
**So that** we can store profiles in database and personalize UI

**Acceptance Criteria:**
- PydanticAI `result_type=UserProfile` extracts:
  ```python
  class UserProfile(BaseModel):
      name: str
      eating_profile: EatingProfile
      movement_profile: MovementProfile
  ```
- Extraction triggered after confirmation step (user approves data)
- Validation:
  - Weight: 50-500 lbs or 20-200 kg (sanity check)
  - Height: 4'0" - 7'0" or 120-220 cm
  - Eating preference: Must be one of predefined options
  - Training preferences: At least one selected
  - Goals: At least one selected
- If extraction fails (invalid data), agent asks clarifying question: "I didn't quite get your weight. Could you confirm it's [extracted value]?"
- Successful extraction → POST to users_service GraphQL API

**Implementation Notes:**
- PydanticAI structured extraction: https://ai.pydantic.dev/structured-outputs/
- ~3-4 hours

**Story Points:** 5

---

#### Story 4.3: Conversation Quality Testing
**As a** QA engineer
**I want** manual test scripts for conversation quality assurance
**So that** we validate the agent feels natural and extracts data accurately

**Acceptance Criteria:**
- Test script covers:
  - Happy path: User answers all questions correctly → profile extracted
  - Edge cases:
    - User provides invalid input (strings instead of numbers)
    - User asks off-topic questions
    - User exits mid-conversation → conversation saved, resumable
    - User edits previous answers in confirmation screen
  - Extraction accuracy: Spot-check 20 test conversations, validate extracted profiles match user inputs (>90% accuracy)
- Manual test script doc: `docs/testing/onboarding-agent-test-script.md`
- Automated test: Mock conversation scenarios with predefined inputs, validate extraction

**Implementation Notes:**
- Playwright for automated E2E testing (simulate user typing in chat)
- ~2-3 hours

**Story Points:** 3

---

### Epic 5: UI Personalization Integration

**Epic Goal:** Connect extracted profiles to app UI for personalized experience.

---

#### Story 5.1: Meals Dashboard Personalization
**As a** user
**I want** my daily calorie target displayed on meals dashboard
**So that** I know how much I should eat

**Acceptance Criteria:**
- Meals dashboard fetches user profile: `GET /users/{user_id}/profiles`
- If `eating_profile.calorie_target` exists, display: "Daily goal: [target] cal"
- If `eating_profile.macro_split` exists, show progress bar with protein/carbs/fat breakdown
- If profile incomplete, show: "Complete your profile to see personalized targets" + "Set up now" CTA
- Updates in real-time when profile completed (WebSocket or polling)

**Implementation Notes:**
- Component: `app/(app)/meals/dashboard.tsx`
- ~2-3 hours

**Story Points:** 3

---

#### Story 5.2: Workout Program Filtering
**As a** user
**I want** workout programs filtered by my training preferences
**So that** I only see relevant programs (no yoga programs if I prefer strength training)

**Acceptance Criteria:**
- Programs list fetches user profile: `GET /users/{user_id}/profiles`
- If `movement_profile.training_preferences` exists, filter programs:
  - User prefers "strength_training" → show strength-focused programs
  - User prefers "yoga" → show yoga/flexibility programs
  - User prefers "mixed" → show all programs
- If profile incomplete, show all programs (no filtering)
- Filter toggle: "Show all programs" checkbox (in case user wants to explore)

**Implementation Notes:**
- Component: `app/(app)/programs/index.tsx`
- ~2-3 hours

**Story Points:** 3

---

#### Story 5.3: Incomplete Profile Notifications
**As a** user
**I want** a reminder notification if I skip onboarding
**So that** I'm encouraged to complete my profile later

**Acceptance Criteria:**
- When user skips onboarding (`onboarding_status: skipped`), schedule push notification for 24 hours later
- Notification text: "Finish setting up your profile to get personalized recommendations!"
- Tapping notification → opens app to onboarding chat
- Notification only sent once (not daily spam)
- User can disable in settings: "Profile setup reminders"

**Implementation Notes:**
- Expo Notifications: https://docs.expo.dev/push-notifications/overview/
- ~2 hours

**Story Points:** 2

---

## 7. Open Questions & Risks

### 7.1 Unresolved Technical Questions

**Q1: Modal vs. In-Cluster Deployment**
- **Question:** Should we deploy on Modal (serverless) or add as microservice in Docker Compose?
- **Impact:** Affects infrastructure management, scaling, and cost
- **Recommendation:** Start with Modal for speed, migrate to in-cluster post-validation if needed
- **Timeline:** Decide before Epic 1 implementation

**Q2: Chat UI Library vs. Custom Implementation**
- **Question:** Use `react-native-gifted-chat` or build custom chat UI?
- **Tradeoffs:** Library is faster (2-3 hours) but less customizable; custom is more work (6-8 hours) but full control
- **Recommendation:** Try library first, fall back to custom if customization needs arise
- **Timeline:** Decide during Epic 3 Story 3.1

**Q3: Conversation Resumption UX**
- **Question:** When user resumes, should they see full conversation history or just "where they left off"?
- **Impact:** Affects perceived conversation length and user patience
- **Recommendation:** Show last 3 messages + current question (not full history)
- **Timeline:** Decide during Epic 4 implementation

**Q4: Profile Edit Flow Post-Completion**
- **Question:** Can users edit their profile after onboarding completion? If so, how (chat or form)?
- **Impact:** Affects long-term profile maintenance
- **Recommendation:** Defer to post-MVP (use form in settings for now)
- **Timeline:** Post-Phase 1

**Q5: Multi-Vertical Onboarding Order**
- **Question:** When multi-vertical is enabled, should users choose all verticals upfront or one-at-a-time?
- **Impact:** Affects perceived conversation length
- **Recommendation:** One-at-a-time (feels more human, less overwhelming)
- **Timeline:** Phase 2 concern (deferred)

### 7.2 Project Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| Conversation feels robotic, users prefer forms | Medium | High | A/B test conversation tone; have copywriter review prompts; user test with 5 alpha users before broader rollout | Product Manager |
| Profile extraction accuracy <90% | Medium | Medium | Manual spot-checks; Logfire monitoring; implement feedback loop where users can flag incorrect extractions | ML Engineer |
| Modal deployment costs exceed budget | Low | Medium | Monitor costs weekly; set budget alerts; fallback to in-cluster deployment if needed | Platform Engineer |
| Users drop off mid-conversation (>40% skip rate) | Medium | High | Shorten conversation (reduce questions); add progress indicator; allow "save and finish later" | UX Designer |
| WebSocket connection issues on poor networks | Medium | Medium | Implement fallback to REST polling; save message history locally; retry logic for failed sends | Mobile Engineer |
| Calorie calculation inaccurate (Harris-Benedict too generic) | Low | Low | Start with simple calculation; iterate based on user feedback; consider integrating TDEE calculators post-MVP | Backend Engineer |
| Multi-language support required earlier than planned | Low | Medium | Design prompts to be translation-friendly; avoid idioms; prepare i18n structure even if English-only for MVP | Product Manager |

### 7.3 Decision Points

**Phase 1 Decision: Ship with Minimal Questions or Full Profile?**
- **Criteria:** If user testing shows >40% drop-off after 3 questions, should we reduce scope?
- **Recommendation:** Reduce to 3 essential questions (name, weight, goal) for MVP, expand post-validation
- **Rationale:** Better to have high completion rate with partial profiles than low completion with full profiles

**Phase 2 Decision: Add Agent B (Onboarding Coach) or Iterate on Agent A?**
- **Criteria:** After Phase 1 launch, prioritize tutorial agent or improve profiling agent?
- **Recommendation:** Prioritize Agent A improvements (better extraction, more domains) over Agent B
- **Rationale:** Accurate profiles drive more value than tutorial; users can learn UI through exploration

**Future Decision: Voice-Based Onboarding**
- **Criteria:** If mobile user base grows beyond 1,000 users, consider voice input
- **Recommendation:** Defer until user research validates demand
- **Rationale:** Voice is high complexity, low MVP value; typing is acceptable for 2-minute conversation

---

## 8. Next Steps

### 8.1 Immediate Actions (Pre-Development)

1. **User Research (Optional but Recommended)**
   - Conduct 5 user interviews to validate conversational onboarding hypothesis
   - Questions: "Would you prefer chat or forms for profile setup?" "How long is too long for onboarding?"
   - Timeline: 1 week

2. **Prompt Engineering Workshop**
   - Draft conversation prompts for all 7 questions
   - Review with copywriter for tone (friendly, motivating, concise)
   - A/B test variations: Formal vs. casual, short vs. detailed
   - Timeline: 2-3 days

3. **Technical Spike: Modal Deployment**
   - Deploy "Hello World" PydanticAI agent on Modal
   - Validate WebSocket latency (<2s response time)
   - Estimate costs for 250 users (Month 3 target)
   - Timeline: 4 hours

4. **Schema Validation**
   - Confirm users_service can orchestrate profile creation across services
   - Test REST calls from users_service → meals_service, movements_service
   - Timeline: 2 hours

### 8.2 Handoff Prompts

#### For Backend Engineer (Profile Storage)
**Context:** You're implementing federated profile storage with users_service as hub. meals_service and movements_service will store domain-specific profiles.

**Key Tasks:**
1. Add `eating_profiles` table to meals_service (schema in section 4.3)
2. Add `movement_profiles` table to movements_service
3. Extend users_service GraphQL API with `createUserProfile`, `getUserProfile` mutations/queries
4. Implement calorie calculation (Harris-Benedict equation) in meals_service
5. Test federation: `GET /users/{user_id}/profiles` returns aggregated data from all services

**Deliverables:**
- Alembic migrations for new tables
- GraphQL schema updates
- Postman collection for testing
- Unit tests for calorie calculation

**Timeline:** Epic 2 (8-12 hours)

---

#### For Mobile Engineer (Chat UI)
**Context:** You're building a chat-native onboarding experience in React Native with Expo.

**Key Tasks:**
1. Build chat UI component (consider `react-native-gifted-chat` or custom)
2. Implement WebSocket client for real-time messaging
3. Create launch, chat, and completion screens
4. Add resume functionality (banner + conversation history loading)
5. Integrate with onboarding agent API (Modal endpoint)

**Deliverables:**
- Chat UI component with typing indicator, quick reply buttons
- Onboarding flow screens (`app/(onboarding)/`)
- WebSocket connection management
- E2E tests for happy path (Playwright or Detox)

**Timeline:** Epic 3 (12-16 hours)

---

#### For ML/AI Engineer (PydanticAI Agent)
**Context:** You're building the conversational agent that guides users through onboarding and extracts structured profiles.

**Key Tasks:**
1. Deploy PydanticAI + FastAPI on Modal
2. Implement conversation flow (7-question sequence)
3. Configure structured extraction (`result_type=UserProfile`)
4. Set up Redis for conversation state management
5. Integrate Logfire for observability

**Deliverables:**
- Modal deployment with WebSocket endpoint
- Conversation prompt engineering
- Profile extraction with >90% accuracy (validated via spot-checks)
- Logfire dashboard for monitoring completion rates

**Timeline:** Epic 1 + Epic 4 (14-22 hours)

---

### 8.3 Success Criteria Checklist

Before launching to users, validate:
- [ ] User can complete onboarding in 1-3 minutes (timed test with 5 users)
- [ ] Profile extraction accuracy >90% (spot-check 20 test conversations)
- [ ] Skip functionality works (creates partial profile, no errors)
- [ ] Resume functionality works (conversation history loads, user can continue)
- [ ] UI displays personalized values (calorie target on meals dashboard)
- [ ] Logfire shows all expected events (started, completed, skipped, errors)
- [ ] No crashes or WebSocket disconnections during testing
- [ ] Notifications sent 24 hours after skip (test with fake user)
- [ ] Works on iOS and Android (test on real devices)
- [ ] Accessibility: Screen reader can navigate conversation (VoiceOver/TalkBack)

---

## Appendix A: Conversation Script Examples

### Example 1: Happy Path (Complete Profile)

```
Agent: Hi! I'm here to help you get the most out of MindMirror. What's your name?
User: Alex

Agent: Great to meet you, Alex! What would you like to set up today?
[Workouts & Movement] [Eating & Nutrition (Coming soon)] [Sleep (Coming soon)]
User: [taps Workouts & Movement]

Agent: Perfect! Let's start with a few basics. What's your current weight?
User: 180 [dropdown: lbs]

Agent: Got it. And your height?
User: 5 [ft] 10 [in]

Agent: Do you have any eating preferences?
[Omnivore] [Vegetarian] [Vegan] [Pescatarian]
User: [taps Omnivore]

Agent: What type of training do you prefer?
[Strength Training] [Running] [Yoga] [Mixed]
User: [taps Strength Training]

Agent: What are your fitness goals? (Select all that apply)
[Build Muscle] [Lose Fat] [Improve Endurance] [Rehab]
User: [taps Build Muscle, Improve Endurance]

Agent: Just to confirm:
[Card: Weight: 180 lbs] [Edit]
[Card: Height: 5'10"] [Edit]
[Card: Eating: Omnivore] [Edit]
[Card: Training: Strength] [Edit]
[Card: Goals: Build muscle, Endurance] [Edit]

Does this look right?
[Yes, looks good!] [Go back to edit]
User: [taps Yes, looks good!]

Agent: You're all set, Alex! 🎉
Your personalized calorie target: 2,200 cal/day
Macro split: 40% protein, 30% carbs, 30% fat

[Start Exploring] button
```

### Example 2: Skip Flow

```
Agent: Hi! I'm here to help you get the most out of MindMirror. What's your name?
User: [taps "Skip for now" in top-right]

[Dialog: "Are you sure you want to skip? It only takes 2 minutes to set up your profile."]
[Go back] [Skip anyway]
User: [taps Skip anyway]

[App navigates to main home screen]
[Banner appears: "Complete your profile to unlock personalized recommendations" | Resume button]
```

### Example 3: Resume Interrupted Conversation

```
[User opens app 24 hours later after exiting mid-conversation]
[Banner: "Complete your profile to unlock recommendations" | Resume]
User: [taps Resume]

[Chat UI loads with conversation history]
Agent: Hey Alex! 👋
Agent: Welcome back! Let's pick up where we left off.
Agent: I still need to know: What are your fitness goals?
[Build Muscle] [Lose Fat] [Improve Endurance] [Rehab]
User: [taps Build Muscle]

[Conversation continues to confirmation...]
```

---

## Appendix B: Glossary

- **Vertical:** Domain-specific area of the app (workouts, eating, sleep, mindfulness)
- **Hub Pattern:** Architecture where users_service acts as orchestrator, delegating to domain services
- **Federated Profiles:** User profile data split across multiple microservices by domain
- **Structured Extraction:** PydanticAI technique to extract typed data (Pydantic models) from natural language
- **Quick Reply Buttons:** Pre-defined option buttons in chat UI (vs. free-text input)
- **Conversation State:** Chat message history stored in Redis for resumption

---

**End of PRD**

*For questions or next steps, contact Product Manager (Mary) or submit issue to project tracker.*
