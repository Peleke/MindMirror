# Debugging: "Become a Coach" 401 User Not Found Error

**Status**: Root cause identified, fix ready to implement
**Priority**: High (blocks core user functionality)
**Branch**: `fix/users-service-assign-role-auth`
**Date**: 2025-11-05

---

## Problem Summary

When users click "Become a Coach" button in the mobile app Profile screen, the request fails with:
```
Exception occurred in UoW block: 401: User not found, rolling back session
INFO: 169.254.169.126:42916 - "POST /graphql HTTP/1.1" 401 Unauthorized
```

**Observable Pattern** (from Cloud Logs):
- Initial request from mobile app (User-Agent: "Unknown") → 401 Unauthorized
- Immediate retry with service credentials (User-Agent: "python-httpx/0.28.1") → 200 OK
- Pattern repeats for every "Become a Coach" click

---

## Root Cause Analysis

### Issue Location
`users_service/users/web/graphql/resolvers.py:904-924`

### The Problem
The `assignRoleToUser` GraphQL mutation **does NOT authenticate** the requesting user.

**Current Implementation** (BROKEN):
```python
@strawberry.mutation
async def assignRoleToUser(self, info: Info, userId: strawberry.ID, role: str, domain: str) -> bool:
    """Assigns a role to a user in a specific domain."""
    uow = await get_uow_from_info(info)  # ❌ SKIPS AUTH CHECK
    repo = UserRepository(session=uow.session)

    try:
        role_enum = RoleModel(role)
        domain_enum = DomainModel(domain)

        await repo.assign_role_to_user(
            user_id=uuid.UUID(str(userId)),
            role=role_enum,
            domain=domain_enum
        )
        await uow.commit()
        return True
    except ValueError as e:
        raise Exception(f"Invalid role or domain: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to assign role: {str(e)}")
```

**Compare to working mutations** (e.g., `requestCoaching`, `acceptCoaching`):
```python
@strawberry.mutation
async def requestCoaching(self, info: Info, clientEmail: str) -> bool:
    current_user = await get_current_user_from_info(info)  # ✅ AUTH CHECK PRESENT
    uow = await get_uow_from_info(info)
    repo = UserRepository(session=uow.session)
    # ... rest of implementation
```

### Why This Causes 401 Errors

1. **Mobile app** sends GraphQL mutation with valid JWT token
2. **Gateway** validates JWT and forwards request to users-service
3. **Users-service** receives request but `assignRoleToUser` never extracts user context
4. **Repository layer** attempts to log/audit the operation, expecting user context
5. **UoW exception handler** catches missing user and raises "401: User not found"
6. **Request fails** with 401 Unauthorized

The "python-httpx" 200 OK responses are likely internal health checks or retries with service-to-service credentials that don't require user context.

---

## Request Flow Analysis

### Successful Flow (other mutations)
```
Mobile App
  → Gateway (validates JWT, extracts user)
  → Users Service (get_current_user_from_info)
  → Repository (with user context)
  ✅ SUCCESS
```

### Broken Flow (assignRoleToUser)
```
Mobile App
  → Gateway (validates JWT, extracts user)
  → Users Service (SKIPS get_current_user_from_info)
  → Repository (missing user context)
  ❌ 401: User not found
```

---

## Proposed Fix

### 1. Add Authentication Check

**File**: `users_service/users/web/graphql/resolvers.py:904-924`

**Change**:
```python
@strawberry.mutation
async def assignRoleToUser(self, info: Info, userId: strawberry.ID, role: str, domain: str) -> bool:
    """Assigns a role to a user in a specific domain."""
    # ✅ ADD AUTH CHECK
    current_user = await get_current_user_from_info(info)

    uow = await get_uow_from_info(info)
    repo = UserRepository(session=uow.session)

    try:
        role_enum = RoleModel(role)
        domain_enum = DomainModel(domain)

        await repo.assign_role_to_user(
            user_id=uuid.UUID(str(userId)),
            role=role_enum,
            domain=domain_enum
        )
        await uow.commit()
        return True
    except ValueError as e:
        raise Exception(f"Invalid role or domain: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to assign role: {str(e)}")
```

### 2. Security Consideration (Optional Enhancement)

**Current behavior**: Any authenticated user can assign ANY role to ANY user.

**Recommended**: Add authorization check to ensure only admins or self-assignment:
```python
@strawberry.mutation
async def assignRoleToUser(self, info: Info, userId: strawberry.ID, role: str, domain: str) -> bool:
    """Assigns a role to a user in a specific domain."""
    current_user = await get_current_user_from_info(info)

    # Authorization check: users can only assign roles to themselves
    if str(current_user.id_) != str(userId):
        raise Exception("Unauthorized: You can only assign roles to yourself")

    uow = await get_uow_from_info(info)
    repo = UserRepository(session=uow.session)

    # ... rest of implementation
```

---

## Testing Strategy

### 1. Manual Testing (Production)
1. Deploy fix to staging
2. Login to mobile app
3. Navigate to Profile → "Become a Coach"
4. Verify:
   - ✅ No 401 errors in Cloud Logs
   - ✅ User successfully assigned COACH role
   - ✅ UI updates to show coach status
   - ✅ Coach features become available

### 2. Unit Tests (Add to `users_service/tests/web/test_graphql_mutations.py`)

**Test Case 1**: Authenticated user can self-assign role
```python
async def test_assign_role_to_self_authenticated():
    """Test that authenticated users can assign roles to themselves."""
    # Setup: Create user and auth context
    # Execute: Call assignRoleToUser mutation
    # Assert: Role assigned successfully, no 401 error
```

**Test Case 2**: Unauthenticated request fails
```python
async def test_assign_role_unauthenticated_fails():
    """Test that unauthenticated requests fail properly."""
    # Setup: No auth context
    # Execute: Call assignRoleToUser mutation
    # Assert: Raises "Unauthorized" exception
```

**Test Case 3**: User cannot assign role to others (if implementing authorization)
```python
async def test_assign_role_to_other_user_fails():
    """Test that users cannot assign roles to other users."""
    # Setup: Create two users, auth as user A
    # Execute: Try to assign role to user B
    # Assert: Raises "Unauthorized" exception
```

### 3. Integration Testing
- Test full flow: Mobile app → Gateway → Users service
- Verify JWT propagation through all layers
- Check audit logs for correct user attribution

---

## Related Issues to Audit

### Other Mutations Missing Auth Check

Search for mutations that skip `get_current_user_from_info(info)`:
```bash
# Find all @strawberry.mutation decorators
grep -A 10 "@strawberry.mutation" users_service/users/web/graphql/resolvers.py

# Check which ones skip auth
```

**Known safe mutations** (have auth check):
- `requestCoaching` (line 827)
- `requestCoachingByUserId` (line 847)
- `acceptCoaching` (line 868)
- `rejectCoaching` (line 886)
- `terminateCoachingForClient` (line 793)

**Mutations to audit**:
- ✅ `assignRoleToUser` (line 904) - **KNOWN BROKEN**
- ⚠️ `create_user` (line 520) - May need auth for security
- ⚠️ `update_user` (line 528) - Should verify user can only update self
- ⚠️ `delete_user` (line 544) - Should restrict to admins
- ⚠️ `remove_role_from_user` (line 692) - Similar to assignRoleToUser

---

## Deployment Plan

### Phase 1: Immediate Fix (This Issue Only)
1. ✅ Create branch: `fix/users-service-assign-role-auth`
2. Add auth check to `assignRoleToUser`
3. Add authorization check (users can only self-assign)
4. Write unit tests
5. Deploy to staging
6. Manual testing
7. Deploy to production
8. Monitor Cloud Logs for 401 errors

### Phase 2: Security Audit (Follow-up)
1. Audit all mutations in `resolvers.py`
2. Add auth/authz checks where missing
3. Document which mutations require admin vs self-service access
4. Add integration tests for auth flows

---

## Implementation Checklist

- [x] Root cause identified
- [x] Fix designed
- [x] Branch created
- [ ] Code changes applied
- [ ] Unit tests written
- [ ] Manual testing in staging
- [ ] Deploy to production
- [ ] Monitor for 401 errors
- [ ] Security audit scheduled

---

## Success Criteria

✅ **Fix is successful when**:
1. Users can click "Become a Coach" without 401 errors
2. Cloud Logs show successful POST 200 responses (no 401s)
3. Users receive COACH role in PRACTICES domain
4. Coach features unlock in mobile app
5. No security regressions (users can't escalate others' privileges)

---

## Additional Notes

### Mobile App Code Reference
**File**: `mindmirror-mobile/app/(app)/profile.tsx:530-551`

```typescript
const handleBecomeCoach = async () => {
  try {
    await assignRole({
      variables: {
        userId: userId,
        role: ROLES.COACH,
        domain: DOMAINS.PRACTICES
      }
    });
    await refetchUser();
    toast.show({
      title: "Success",
      description: "You are now a coach!",
    });
  } catch (error: any) {
    toast.show({
      title: "Error",
      description: error.message || "Failed to upgrade to coach.",
      action: "error",
    });
  }
};
```

**GraphQL Mutation**: `mindmirror-mobile/src/services/api/users.ts:131-135`
```graphql
mutation AssignRole($userId: ID!, $role: String!, $domain: String!) {
  assignRoleToUser(userId: $userId, role: $role, domain: $domain)
}
```

### Gateway Configuration
Gateway properly validates JWT and forwards requests. No changes needed to gateway.

### Cloud Logs Evidence
```
2025-11-05 18:06:01.655 EST
POST 401 127 B 48 ms Unknown https://users-service-4ik6kij34q-uk.a.run.app/graphql

2025-11-05 18:06:01.697 EST
Exception occurred in UoW block: 401: User not found, rolling back session

2025-11-05 18:06:01.702 EST
INFO: 169.254.169.126:42916 - "POST /graphql HTTP/1.1" 401 Unauthorized
```

---

**Ready to implement**: Yes
**Estimated time**: 30 minutes
**Risk level**: Low (isolated change, well-tested pattern)
