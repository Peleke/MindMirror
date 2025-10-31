# Epic 6: Onboarding Agent Infrastructure

**Epic ID:** EPIC-6
**Status:** Draft
**Priority:** P1 (Month 3 Feature - Post-Alpha Validation)
**Estimated Effort:** 6-10 hours
**Story Points:** 11

---

## Epic Goal

Establish serverless PydanticAI agent service with real-time chat capabilities, conversation state management, and comprehensive observability to power conversational onboarding.

---

## Business Value

**Problem:** New users have no personalized data in the system, leading to generic UI experiences and inability to provide tailored recommendations. Manual form-based profiling is tedious and has low completion rates.

**Solution:** Deploy AI-powered conversational agent that feels like "texting a personal trainer" - natural, quick (1-3 minutes), and extracts structured profile data for personalization.

**Impact:**
- Increases profile completion rate from ~30% (traditional forms) to target 80%+ (conversational)
- Reduces time-to-personalization from "never" (users skip forms) to <3 minutes
- Enables UI personalization (calorie targets, program filtering) immediately after signup
- Scales to 250+ users without operational overhead (serverless architecture)

---

## Linked Requirements

- **NFR1:** Performance (conversation loads <1s, agent responds <2s)
- **NFR2:** Reliability (99% uptime, state persistence)
- **NFR3:** Scalability (100 concurrent conversations)
- **NFR4:** Security (encrypted conversations, no PII in logs)
- **FR8:** Observability & Conversation Monitoring

---

## User Stories

### Story 6.1: Modal Deployment Setup
**File:** `docs/stories/6.1-modal-deployment.md`
**Points:** 5
**Estimate:** ~2-3 hours

**As a** platform engineer
**I want** PydanticAI + FastAPI agent deployed on Modal
**So that** the agent auto-scales and requires no infrastructure management

---

### Story 6.2: Conversation State Management (Redis)
**File:** `docs/stories/6.2-conversation-state-redis.md`
**Points:** 3
**Estimate:** ~1-2 hours

**As a** developer
**I want** conversation history stored in Redis with auto-expiration
**So that** users can resume conversations and we don't store data indefinitely

---

### Story 6.3: Logfire Integration
**File:** `docs/stories/6.3-logfire-integration.md`
**Points:** 3
**Estimate:** ~2 hours

**As a** developer
**I want** all conversations logged to Logfire for monitoring and debugging
**So that** I can track completion rates, identify drop-off points, and debug extraction failures

---

## Technical Assumptions

**Validated:**
- ✅ Modal supports Python FastAPI + WebSocket deployments
- ✅ PydanticAI integrates with OpenAI GPT-4o-mini (cost-effective for extraction)
- ✅ Logfire SDK works with FastAPI (Pydantic-native observability)
- ✅ Upstash Redis provides serverless Redis (no infra management)

**Dependencies:**
- OpenAI API key (existing)
- Logfire account + API token (new setup required)
- Upstash Redis account (free tier sufficient for alpha)

---

## Success Criteria

- [ ] Modal deployment completes successfully, returns public URL
- [ ] WebSocket endpoint accepts connections from mobile app
- [ ] Conversation history persists in Redis (7-day TTL)
- [ ] Logfire dashboard shows completion rate, avg duration, drop-off funnel
- [ ] No PII logged to Logfire (user_id only, not email/name)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Modal cold starts >1s (poor UX) | Medium | Medium | Use Modal "keep warm" feature; fallback to in-cluster if needed |
| Redis connection failures | Low | High | Implement retry logic; graceful degradation (conversation still works, just can't resume) |
| Logfire costs exceed budget | Low | Low | Monitor usage; set data retention to 30 days; use sampling for high-volume events |

---

## Dependencies

**Blockers:**
- None (can start immediately)

**Blocks:**
- Epic 9 (Conversation Orchestration requires deployed agent service)
- Epic 8 (Chat UI needs WebSocket endpoint URL)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-20 | v1.0 | Initial epic creation from Onboarding Agent PRD | Mary (Business Analyst) |
