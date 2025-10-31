# Coding Standards

**Document:** Architecture Shard - Coding Standards
**Version:** v4.0
**Last Updated:** 2025-10-15

---

## Python Backend Standards

### Code Style

- **Formatter:** Black (line length 88)
- **Linter:** Ruff with FastAPI best practices
- **Import Order:** isort compatible (stdlib → third-party → local)
- **Async/Await:** Use async def for all I/O operations (database, HTTP calls)
- **Type Hints:** Required for all function signatures

### Patterns

- **Repository Pattern:** Separate data access from business logic
  ```python
  # Good
  class UserRepository:
      async def get_by_id(self, user_id: str) -> User | None:
          pass

  # Bad - mixing data access with business logic
  async def get_user_and_send_email(user_id: str):
      user = await db.query(...)
      await send_email(user.email)
  ```

- **Dependency Injection:** Use FastAPI dependency injection for shared resources
  ```python
  from fastapi import Depends
  from shared.auth import get_current_user

  async def endpoint(user: User = Depends(get_current_user)):
      pass
  ```

- **Error Handling:** Raise HTTPException for API errors
  ```python
  from fastapi import HTTPException, status

  if not user:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="User not found"
      )
  ```

### Testing

- **Framework:** pytest with async fixtures
- **Coverage:** 70% minimum
- **Structure:** Mirror source structure in `tests/` directory
- **Fixtures:** Use `pytest.fixture` for shared test data
  ```python
  @pytest.fixture
  async def test_db():
      async with TestDatabase() as db:
          yield db
  ```

---

## TypeScript Frontend Standards

### Code Style

- **Formatter:** Prettier (2 space indentation)
- **Linter:** ESLint with TypeScript plugin
- **Import Order:** React → third-party → local
- **Type Safety:** Strict TypeScript (`strict: true` in tsconfig)

### React Patterns

- **Functional Components:** Always use functional components with hooks
  ```typescript
  // Good
  const Component: React.FC<Props> = ({ name }) => {
    const [state, setState] = useState<string>('');
    return <div>{name}</div>;
  };

  // Bad - class components
  class Component extends React.Component<Props> {
    render() { return <div>{this.props.name}</div>; }
  }
  ```

- **Custom Hooks:** Extract reusable logic into custom hooks
  ```typescript
  function useWorkoutState(practiceId: string) {
    const [sets, setSets] = useState<Set[]>([]);
    // ... logic
    return { sets, logSet };
  }
  ```

- **Error Boundaries:** Wrap routes with error boundaries
  ```typescript
  <ErrorBoundary fallback={<ErrorScreen />}>
    <WorkoutScreen />
  </ErrorBoundary>
  ```

### GraphQL

- **Co-location:** Place queries/mutations with components
  ```typescript
  // WorkoutScreen.graphql.ts
  export const GET_WORKOUT = gql`
    query GetWorkout($id: ID!) {
      workout(id: $id) {
        id
        exercises { ... }
      }
    }
  `;
  ```

- **Type Generation:** Use GraphQL Code Generator for type safety
- **Error Handling:** Use Apollo Client's error policies
  ```typescript
  const { data, error } = useQuery(GET_WORKOUT, {
    variables: { id },
    errorPolicy: 'all', // Show partial data on error
  });
  ```

### Mobile-Specific

- **fp-ts:** Use functional programming patterns for data transformations
  ```typescript
  import { pipe } from 'fp-ts/function';
  import * as A from 'fp-ts/Array';

  const completed = pipe(
    sets,
    A.filter(s => s.completed),
    A.map(s => s.weight)
  );
  ```

- **Gluestack UI:** Use pre-built components, avoid custom styled-components
  ```typescript
  // Good
  import { Box, Button, VStack } from '@gluestack-ui/themed';

  // Bad - custom styled component
  const StyledBox = styled.View`...`;
  ```

- **Navigation:** Use Expo Router file-based routing
  ```typescript
  // app/(app)/workout/[id].tsx
  export default function WorkoutScreen() {
    const { id } = useLocalSearchParams();
  }
  ```

---

## Enhancement-Specific Standards

### Admin UI Components (Next.js)

- **Server Components:** Default to Server Components, mark Client Components with "use client"
  ```typescript
  // Server Component (default)
  async function ProgramDashboard() {
    const programs = await fetchPrograms();
    return <div>{programs.map(...)}</div>;
  }

  // Client Component (interactive)
  'use client';
  function MagicLinkForm() {
    const [email, setEmail] = useState('');
  }
  ```

- **Forms:** Use React Hook Form with Zod validation
  ```typescript
  const schema = z.object({
    email: z.string().email(),
    programId: z.string().uuid(),
  });

  const form = useForm({ resolver: zodResolver(schema) });
  ```

### Mobile Workout Components

- **Component Structure:**
  ```typescript
  interface Props {
    exerciseId: string;
    onComplete: (setData: SetData) => void;
  }

  export const SetTable: React.FC<Props> = ({ exerciseId, onComplete }) => {
    // Component logic
  };
  ```

- **Animations:** Use React Native Reanimated for smooth transitions
  ```typescript
  import Animated, { useAnimatedStyle, withSpring } from 'react-native-reanimated';

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: withSpring(isVisible ? 1 : 0),
  }));
  ```

---

## Critical Integration Rules

### Existing API Compatibility

- **Never modify existing GraphQL query/mutation signatures** (only extend with optional fields)
- **Backward compatibility:** New fields must be optional (nullable)
- **Versioning:** If breaking changes needed, create new mutation (e.g., `autoEnrollPracticesV2`)

### Database Integration

- **Validate schemas:** Before implementing features, verify database fields exist
  ```python
  # Check practice_instance.notes field exists
  assert hasattr(PracticeInstance, 'notes'), "notes field missing"
  ```

- **No schema changes:** All enhancement features use existing database fields
- **Migrations:** If schema changes required, create Alembic migration and test in staging first

### Error Handling

- **External APIs:** Wrap all external API calls in try/catch with fallback
  ```typescript
  try {
    const exercise = await fetchExercise(id);
  } catch (error) {
    console.error('Failed to fetch exercise:', error);
    return <PlaceholderCard />; // Fallback UI
  }
  ```

- **GraphQL Mutations:** Handle network errors gracefully
  ```typescript
  const [mutate] = useMutation(LOG_SET, {
    onError: (error) => {
      toast.error('Failed to save set');
      console.error(error);
    },
  });
  ```

### Logging Consistency

- **Python:** Use FastAPI logging
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f"User {user_id} logged set")
  ```

- **TypeScript:** Use console methods (error, warn, info)
  ```typescript
  console.error('GraphQL mutation failed:', error);
  console.warn('Exercise GIF not found, using placeholder');
  ```

---

## File Naming Conventions

### Python

- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`

### TypeScript

- **Files:** `kebab-case.ts`, `PascalCase.tsx` (React components)
- **Directories:** `kebab-case/`
- **Components:** `PascalCase`
- **Functions:** `camelCase`
- **Constants:** `UPPER_SNAKE_CASE`

### Examples

```
# Python
practices_service/
  practices/
    repository/
      models/
        practice_instance.py  # File: snake_case
          class PracticeInstance  # Class: PascalCase
          async def get_by_id()  # Function: snake_case

# TypeScript (Mobile)
mindmirror-mobile/
  src/features/practices/
    components/
      ExerciseCard.tsx        # Component file: PascalCase
      SetTable.tsx
      index.ts                # Barrel export

# TypeScript (Web)
web/
  src/app/admin/
    vouchers/
      create/
        page.tsx              # Next.js route: lowercase
```

---

## Documentation Standards

### Python Docstrings (Google Style)

```python
async def log_set(
    practice_id: str,
    set_number: int,
    weight: float,
    reps: int
) -> PracticeInstance:
    """Log a completed set for a workout.

    Args:
        practice_id: UUID of the practice instance
        set_number: Set number (1-indexed)
        weight: Weight in pounds
        reps: Number of repetitions

    Returns:
        Updated practice instance with logged set

    Raises:
        HTTPException: If practice instance not found
    """
    pass
```

### TypeScript JSDoc

```typescript
/**
 * Fetches exercise details including GIF URL from ExerciseDB API.
 *
 * @param exerciseId - UUID of the exercise
 * @returns Exercise data with GIF URL, or null if not found
 * @throws {Error} If API request fails after retries
 */
async function fetchExercise(exerciseId: string): Promise<Exercise | null> {
  // ...
}
```

---

## Git Commit Messages

**Format:** `<type>(<scope>): <subject>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding tests
- `docs`: Documentation
- `chore`: Maintenance tasks

**Examples:**
```
feat(admin): add magic link generator UI
fix(mobile): workout timer persists on navigation
refactor(practices): extract set table to separate component
test(e2e): add workflow test for workout completion
docs(architecture): update tech stack section
```

---

## Code Review Checklist

- [ ] Type hints/types present for all function signatures
- [ ] Tests written for new functionality (80% coverage target)
- [ ] Error handling implemented with fallback behavior
- [ ] GraphQL schema backward compatible (no breaking changes)
- [ ] Existing test suites pass (`npm test`, `pytest`)
- [ ] Linting passes (`npm run lint`, `ruff check`)
- [ ] Documentation updated (docstrings, JSDoc, README)
- [ ] No hardcoded secrets or API keys
- [ ] Mobile components use Gluestack UI primitives
- [ ] Web components follow Next.js App Router patterns
