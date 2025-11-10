# EPIC: Agent Service Implementation

**Status**: Planning
**Priority**: High
**Estimated Effort**: 3-4 weeks
**Dependencies**: EPIC_HMAC_Service_Auth (for production), Supabase schema migration

---

## Overview

Build a conversational AI agent service that allows users to interact with MindMirror's API via natural language. The agent will parse text input into structured data, orchestrate multi-step workflows with human-in-the-loop approval gates, and execute operations across practices and meals services.

**Primary Use Cases:**
1. **Workout Template Creation**: Parse workout descriptions → create templates → get approval → persist
2. **Program Building**: Create multiple templates → link to program → get approval → persist
3. **Meal Logging**: Parse meal descriptions → structured log entry → persist

**Future Use Cases:**
- CV-based meal parsing from images
- Nutrition tracking and recommendations
- Workout modifications via natural language

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Agent Service (New)                    │
│                                                     │
│  FastAPI + LangChain v1.x + Redis + Postgres       │
│  - create_agent pattern (2025)                     │
│  - Structured output (with_structured_output)      │
│  - Manual workflow state management                │
│  - Background task execution                       │
└─────────────────────────────────────────────────────┘
         │                              │
         ├──────────────────────────────┤
         │                              │
    ┌────▼─────┐                  ┌────▼─────┐
    │  Redis   │                  │ Postgres │
    │ (Temp    │                  │ (Schema: │
    │  State)  │                  │  agent)  │
    └──────────┘                  └──────────┘
         │
         └──────────────────────────────┐
                                        │
                  ┌─────────────────────▼──────────────┐
                  │      Downstream Services           │
                  │  - practices_service (GraphQL)     │
                  │  - meals_service (GraphQL)         │
                  │  - users_service (GraphQL)         │
                  └────────────────────────────────────┘
```

**Tech Stack:**
- **Framework**: LangChain v1.x (`create_agent` pattern)
- **LLM**: OpenAI GPT-4o with structured output
- **API**: FastAPI with async/await
- **State**: Redis (temporary workflow state) + Postgres (history)
- **Auth**: JWT pass-through (MVP) → HMAC signing (production)
- **Integration**: REST/GraphQL clients extending `shared.clients.base`

---

## User Stories

### Epic-Level Stories

**US-1**: As a user, I can send a natural language message to create workout templates, and the AI will parse my input, show me a preview, and wait for my approval before creating anything.

**US-2**: As a user, I can edit the AI's interpretation either through the UI or by sending follow-up natural language messages.

**US-3**: As a user, I can create multi-template workout programs in a single conversational flow.

**US-4**: As a user, I can log meals via natural language descriptions without using forms.

**US-5**: As a developer, I can extend the agent with new capabilities by adding tools that follow the established pattern.

---

## Technical Stories

### Phase 1: Foundation (Week 1)

**TS-1.1**: Set up agent service project structure
- Create `src/agent_service/` directory
- Set up Poetry with LangChain v1.x dependencies
- Create FastAPI application skeleton
- Configure environment variables

**TS-1.2**: Create Postgres database and schema
- Add new Postgres container to `docker-compose.yml` (port 5438)
- Create Alembic migration config for agent service
- Create initial migration: `conversations`, `messages`, `workflow_history` tables
- Add schema: `agent` to Supabase (staging/production)

**TS-1.3**: Implement base service clients
- Extend `PracticesServiceClient` from `shared.clients.base`
- Extend `MealsServiceClient` from `shared.clients.base`
- Create factory functions for client initialization
- Add GraphQL mutations for create operations

**TS-1.4**: Set up Redis connection for workflow state
- Add Redis client initialization
- Create `WorkflowState` class for state management
- Implement CRUD operations for workflows in Redis
- Add 1-hour TTL for temporary workflow data

### Phase 2: LangChain Agent Core (Week 2)

**TS-2.1**: Create structured output models
- Define Pydantic models: `WorkoutTemplate`, `WorkoutParseResult`, `ProgramParseResult`, `MealLogEntry`
- Add confidence scoring fields
- Add validation rules

**TS-2.2**: Implement agent with structured output
- Create `create_mindmirror_agent` function using LangChain v1.x pattern
- Configure ChatOpenAI with `.with_structured_output()`
- Add system prompts for workout/meal parsing
- Set up agent with tools

**TS-2.3**: Build hand-crafted workflow tools
- `create_workout_template_tool`: Parse → Preview → Workflow ID
- `create_program_tool`: Multi-template → Program → Workflow ID
- `log_meal_tool`: Parse → Log entry
- `approve_workflow_tool`: Execute pending workflow

**TS-2.4**: Auto-generate CRUD tools from GraphQL schemas
- GraphQL introspection utility
- Tool generator from mutations/queries
- Dynamic tool registration
- MCP-compatible tool registry endpoint (`/tools`)

### Phase 3: API & Workflows (Week 2-3)

**TS-3.1**: Implement chat endpoints
- `POST /chat/send`: Send message, invoke agent
- `POST /chat/approve`: Approve/reject/edit workflow
- `GET /chat/history`: Retrieve conversation history
- Error handling and validation

**TS-3.2**: Implement workflow execution
- Background task execution with FastAPI `BackgroundTasks`
- Workflow state transitions
- Error recovery and retry logic
- Completion notifications

**TS-3.3**: Add conversation persistence
- Store messages in Postgres
- Store workflow history in Postgres
- Retrieve conversation context from DB
- Implement conversation pagination

**TS-3.4**: Implement streaming (optional for MVP)
- Server-Sent Events (SSE) endpoint
- Stream agent thinking process
- Stream workflow status updates
- Frontend integration hooks

### Phase 4: Authentication & Integration (Week 3)

**TS-4.1**: Implement JWT pass-through authentication
- Extract user from JWT in agent service
- Create `AuthContext` from user
- Pass JWT to downstream services via `Authorization` header
- Add `x-internal-id` header

**TS-4.2**: Add service-to-service auth layer
- Extend `create_auth_headers` for agent service identity
- Add error handling for auth failures
- Implement token refresh logic (if needed)
- Add auth context injection to tools

**TS-4.3**: Integrate with practices_service
- Test template creation flow end-to-end
- Test program creation flow end-to-end
- Add error handling for GraphQL errors
- Add retry logic for transient failures

**TS-4.4**: Integrate with meals_service
- Test meal logging flow end-to-end
- Add error handling for nutrition API failures
- Add validation for meal data

### Phase 5: Testing & Polish (Week 4)

**TS-5.1**: Unit tests
- Test structured output parsing
- Test workflow state management
- Test tool execution
- Test client methods

**TS-5.2**: Integration tests
- Test full conversation flows
- Test approval/rejection paths
- Test edit workflows
- Test error scenarios

**TS-5.3**: End-to-end tests
- Test with real LLM (OpenAI)
- Test with real services (local Docker)
- Test authentication flows
- Test concurrent workflows

**TS-5.4**: Documentation
- API documentation (OpenAPI/Swagger)
- Agent architecture docs
- Tool development guide
- Deployment guide

---

## Database Schema

### New Postgres Database: `mindmirror_agent`

**Local Docker:**
- New container: `postgres_agent` (port 5438)
- Database: `mindmirror_agent`

**Supabase (staging/production):**
- Schema: `agent` in existing Supabase database

### Tables

```sql
-- Conversations
CREATE TABLE agent.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Messages in conversations
CREATE TABLE agent.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES agent.conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    tool_calls JSONB,  -- LangChain tool invocations
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Workflow history (long-term storage)
CREATE TABLE agent.workflow_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    conversation_id UUID REFERENCES agent.conversations(id) ON DELETE SET NULL,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'pending' | 'approved' | 'rejected' | 'completed' | 'failed'
    input_data JSONB NOT NULL,
    preview_data JSONB,
    result_data JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversations_user ON agent.conversations(user_id);
CREATE INDEX idx_messages_conversation ON agent.messages(conversation_id);
CREATE INDEX idx_workflow_user ON agent.workflow_history(user_id);
CREATE INDEX idx_workflow_status ON agent.workflow_history(status);
CREATE INDEX idx_workflow_conversation ON agent.workflow_history(conversation_id);
```

---

## Configuration

### Environment Variables

```bash
# Agent Service
AGENT_SERVICE_PORT=8008
OPENAI_API_KEY=sk-...
AGENT_DATABASE_URL=postgresql+asyncpg://user:pass@postgres_agent:5432/mindmirror_agent
REDIS_URL=redis://redis:6379/2

# Downstream Services
PRACTICES_SERVICE_URL=http://practices_service:8006
MEALS_SERVICE_URL=http://meals_service:8004
USERS_SERVICE_URL=http://users_service:8007

# Auth (MVP: pass-through)
AUTH_MODE=jwt_passthrough  # Future: hmac

# LangChain
LANGCHAIN_TRACING_V2=true  # Optional: LangSmith
LANGCHAIN_API_KEY=...      # Optional: LangSmith
```

### Docker Compose Addition

```yaml
  postgres_agent:
    image: postgres:16-alpine
    container_name: postgres_agent
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: mindmirror_agent
    ports:
      - "5438:5432"
    volumes:
      - postgres_agent_data:/var/lib/postgresql/data

  agent_service:
    build:
      context: .
      dockerfile: src/agent_service/Dockerfile
    container_name: agent_service
    environment:
      AGENT_DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres_agent:5432/mindmirror_agent
      REDIS_URL: redis://redis:6379/2
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      PRACTICES_SERVICE_URL: http://practices_service:8006
      MEALS_SERVICE_URL: http://meals_service:8004
    ports:
      - "8008:8008"
    depends_on:
      - postgres_agent
      - redis
      - practices_service
      - meals_service

volumes:
  postgres_agent_data:
```

---

## API Specification

### Endpoints

**POST /chat/send**
```json
Request:
{
  "message": "Create a 3-day upper/lower split...",
  "conversation_id": "uuid" // optional
}

Response:
{
  "conversation_id": "uuid",
  "response": "I've created these workout templates...",
  "workflow_id": "wf_abc123", // if preview created
  "preview": { /* structured preview */ },
  "actions": ["approve", "edit", "cancel"],
  "status": "awaiting_approval" | "completed" | "error"
}
```

**POST /chat/approve**
```json
Request:
{
  "workflow_id": "wf_abc123",
  "conversation_id": "uuid",
  "action": "approve" | "reject" | "edit",
  "edit_message": "change bench press to 5 sets" // if action=edit
}

Response:
{
  "status": "executing" | "completed" | "rejected",
  "result": { /* created entities */ }
}
```

**GET /chat/history?conversation_id={uuid}&limit=50&offset=0**
```json
Response:
{
  "messages": [
    {
      "role": "user",
      "content": "...",
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "...",
      "created_at": "2025-01-15T10:00:05Z"
    }
  ],
  "total": 100,
  "has_more": true
}
```

**GET /tools** (MCP-compatible registry)
```json
Response:
{
  "tools": [
    {
      "name": "create_workout_template",
      "description": "Create a workout template...",
      "inputSchema": { /* JSON Schema */ },
      "annotations": {
        "category": "practices",
        "source": "mindmirror-agent"
      }
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "structured_output": true,
    "workflows": true,
    "streaming": false
  }
}
```

---

## Tool Patterns

### Hand-Crafted Workflow Tool Pattern

```python
@tool
async def create_workout_template(template_data: Dict[str, Any]) -> str:
    """
    Create a workout template with preview and approval.

    Args:
        template_data: {
            "name": str,
            "description": str,
            "duration_minutes": int,
            "exercises": [...]
        }

    Returns:
        Workflow ID and preview for approval
    """
    # 1. Create workflow
    workflow_id = await workflow_state.create_workflow(...)

    # 2. Generate preview
    preview = {...}

    # 3. Return for user approval
    return f"Created preview. Workflow ID: {workflow_id}\n{preview}"
```

### Auto-Generated CRUD Tool Pattern

```python
# Auto-generated from GraphQL introspection
@tool
async def list_practice_templates(user_id: str) -> str:
    """List all practice templates for a user"""
    result = await practices_client.list_templates(...)
    return json.dumps(result)
```

---

## Structured Output Strategy

### Always Force Structured Output

Per requirements, **always** use structured output for parsing user input:

```python
# 1. Define Pydantic models
class WorkoutTemplate(BaseModel):
    name: str
    description: Optional[str]
    duration_minutes: int
    exercises: List[ExerciseDetail]

class WorkoutParseResult(BaseModel):
    templates: List[WorkoutTemplate]
    program_name: Optional[str]
    confidence: float = Field(ge=0.0, le=1.0)

# 2. Create structured LLM
structured_llm = ChatOpenAI(model="gpt-4o").with_structured_output(
    WorkoutParseResult,
    method="json_schema"  # Most reliable per LangChain docs
)

# 3. Always parse before agent invocation
parse_result = await (prompt | structured_llm).ainvoke({"input": user_message})

# 4. Use confidence threshold
if parse_result.confidence < 0.7:
    # Ask for clarification
    return {"response": "I'm not sure I understood..."}
else:
    # Proceed with workflow
    workflow_id = await create_workflow(parse_result.dict())
```

### Structured Output Models

**Workout Domain:**
- `WorkoutTemplate`: Single template definition
- `ExerciseDetail`: Exercise within template
- `WorkoutParseResult`: Multi-template parse result
- `ProgramParseResult`: Program with linked templates

**Meal Domain:**
- `MealLogEntry`: Single meal log
- `FoodItem`: Individual food in meal
- `NutritionInfo`: Parsed nutrition data

**Confidence Thresholds:**
- `>= 0.9`: Auto-execute (high confidence)
- `0.7 - 0.9`: Show preview, require approval
- `< 0.7`: Ask for clarification

---

## Success Metrics

### MVP Success Criteria

1. **Functional**:
   - Users can create workout templates via chat
   - Users can create programs via chat
   - Users can log meals via chat
   - 95%+ structured output parse success rate

2. **Quality**:
   - <500ms p95 response time for parse
   - <3s p95 end-to-end workflow completion
   - Zero auth failures (pass-through works)
   - 100% test coverage for core workflows

3. **User Experience**:
   - Clear preview formatting
   - Intuitive approval flow
   - Helpful error messages
   - Edit-via-chat works seamlessly

### Future Enhancements

1. **Streaming responses** (SSE)
2. **Pub/sub notifications** (Redis)
3. **Image upload** for CV meal parsing
4. **Multi-turn conversations** with context
5. **Personalized recommendations**
6. **Voice input** support
7. **MCP server** external integration

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM parsing errors | High | Force structured output, confidence thresholds, fallback prompts |
| Auth token expiry | Medium | Implement token refresh, short-circuit retry logic |
| Downstream service failures | Medium | Retry with exponential backoff, clear error messages |
| Workflow state loss | Low | Redis persistence + Postgres backup, 1-hour TTL |
| Tool execution errors | Medium | Comprehensive error handling, workflow rollback |
| Performance (LLM latency) | Medium | Cache common parses, optimize prompts, parallel tool calls |

---

## Dependencies

### External
- OpenAI API (GPT-4o)
- LangChain v1.x (`langchain>=0.3.0`)
- FastAPI (`fastapi>=0.115.0`)
- Redis (existing)
- Postgres (new container/schema)

### Internal
- `shared.clients.base` (existing)
- `shared.auth` (existing)
- `practices_service` GraphQL API (existing)
- `meals_service` GraphQL API (existing)

---

## Acceptance Criteria

### Phase 1: Foundation
- [ ] Agent service runs locally via Docker Compose
- [ ] Postgres database created with schema
- [ ] Redis connection established
- [ ] Service clients can call practices/meals services

### Phase 2: Agent Core
- [ ] LangChain agent created with `create_agent`
- [ ] Structured output parsing works for workouts
- [ ] Structured output parsing works for meals
- [ ] Confidence scoring implemented

### Phase 3: Workflows
- [ ] Can create workout template with approval flow
- [ ] Can create program with multiple templates
- [ ] Can log meal via chat
- [ ] Background execution works

### Phase 4: Integration
- [ ] JWT pass-through authentication works
- [ ] Can create templates in practices_service
- [ ] Can create programs in practices_service
- [ ] Can log meals in meals_service

### Phase 5: Testing
- [ ] 90%+ unit test coverage
- [ ] Integration tests pass
- [ ] E2E tests pass with real services
- [ ] Documentation complete

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Foundation | Week 1 | Service skeleton, DB, clients |
| Phase 2: Agent Core | Week 2 | LangChain agent, tools, structured output |
| Phase 3: Workflows | Week 2-3 | API endpoints, workflow execution |
| Phase 4: Integration | Week 3 | Auth, service integration, testing |
| Phase 5: Polish | Week 4 | Testing, docs, deployment |

**Total: 3-4 weeks**

---

## Related EPICs

- [EPIC: HMAC Service-to-Service Authentication](./EPIC_HMAC_Service_Auth.md)
- Future: EPIC_Agent_Service_CV_Meal_Parsing
- Future: EPIC_Agent_Service_Streaming_Responses
- Future: EPIC_Agent_Service_MCP_Server
