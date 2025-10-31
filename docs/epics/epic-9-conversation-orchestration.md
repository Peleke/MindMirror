# Epic 9: Conversation Orchestration & Quality

**Epic ID:** EPIC-9
**Status:** Draft
**Priority:** P1 (Month 3 Feature - Post-Alpha Validation)
**Estimated Effort:** 8-12 hours
**Story Points:** 16

---

## Epic Goal

Implement intelligent conversation flow with PydanticAI-powered profile extraction, confirmation flow, and quality assurance testing to ensure >90% extraction accuracy.

---

## Business Value

**Problem:** Conversational onboarding only works if the agent feels natural and accurately extracts profile data. Poor conversation quality or extraction failures undermine user trust.

**Solution:** Use PydanticAI for structured extraction (Pydantic models from natural language), implement 7-question conversation flow with confirmation step, and validate accuracy via Logfire monitoring.

**Impact:**
- 90%+ profile extraction accuracy (user inputs correctly captured)
- Natural conversation tone (not robotic or form-like)
- Users complete onboarding in 1-3 minutes (avg 2 min)
- Foundation for future multi-vertical onboarding (eating, sleep, mindfulness)

---

## Linked Requirements

- **FR3:** Workouts/Movement Profiling Interview
- **FR4:** Profile Extraction & Storage
- **FR6:** Resume Interrupted Conversation
- **FR8:** Observability & Conversation Monitoring

---

## User Stories

### Story 9.1: Conversation Flow Logic
**File:** `docs/stories/9.1-conversation-flow-logic.md`
**Points:** 8
**Estimate:** ~4-5 hours

**As a** developer
**I want** PydanticAI agent to guide users through onboarding questions
**So that** the conversation feels natural and extracts required profile data

---

### Story 9.2: Profile Extraction with PydanticAI
**File:** `docs/stories/9.2-profile-extraction-pydantic.md`
**Points:** 5
**Estimate:** ~3-4 hours

**As a** developer
**I want** structured profile data extracted from conversation
**So that** we can store profiles in database and personalize UI

---

### Story 9.3: Conversation Quality Testing
**File:** `docs/stories/9.3-conversation-quality-testing.md`
**Points:** 3
**Estimate:** ~2-3 hours

**As a** QA engineer
**I want** manual test scripts for conversation quality assurance
**So that** we validate the agent feels natural and extracts data accurately

---

## Technical Assumptions

**PydanticAI Configuration:**
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
    system_prompt="""You are a friendly fitness coach conducting onboarding.
    Ask one question at a time. Be casual and encouraging.
    Extract structured profile data from conversation."""
)
```

**Validated:**
- ✅ PydanticAI supports structured extraction (Pydantic models as output)
- ✅ OpenAI GPT-4o-mini is cost-effective ($0.15/1M input tokens)
- ✅ Conversation state can be stored in Redis (from Epic 6)

**Dependencies:**
- Epic 6 (Modal deployment + Redis state management)
- Epic 7 (users_service profile storage API)

---

## Success Criteria

- [ ] Conversation follows 7-question sequence (name → vertical → eating → movement)
- [ ] Agent handles invalid inputs gracefully ("I didn't catch that, could you confirm your weight?")
- [ ] Profile extraction accuracy >90% (validated via 20 spot-checks)
- [ ] Users can edit previous answers in confirmation screen
- [ ] Conversation feels natural (qualitative feedback from 5 user tests)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Conversation feels robotic/stilted | Medium | High | A/B test prompts; have copywriter review; user test with 5 alpha users |
| Profile extraction accuracy <90% | Medium | Medium | Manual spot-checks; Logfire monitoring; feedback loop for flagging errors |
| Agent asks off-topic questions (hallucination) | Low | Medium | Use strict system prompt; validate extracted data against schema |

---

## Dependencies

**Blockers:**
- Epic 6 (requires deployed agent service + Redis)
- Epic 7 (requires profile storage endpoints)

**Blocks:**
- Epic 10 (UI personalization requires extracted profiles)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-20 | v1.0 | Initial epic creation from Onboarding Agent PRD | Mary (Business Analyst) |
