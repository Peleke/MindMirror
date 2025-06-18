# MindMirror Bug Reports & Known Issues

## 1. Journal History Caching

**Description:**
When a new journal entry (Gratitude, Reflection, or Freeform) is successfully submitted, the `/dashboard/history` page does not automatically update to show the new entry. The user must manually refresh the page to see the latest data.

**Expected Behavior:**
The `JournalHistory` component should automatically refetch its data and display the new entry immediately after submission without requiring a manual page refresh.

**Possible Cause:**
The Apollo Client cache is not being properly invalidated or updated after the creation mutations (`createGratitudeJournalEntry`, `createReflectionJournalEntry`, `createFreeformJournalEntry`) are completed.

**Potential Solution:**
Use the `refetchQueries` option in the `useMutation` hook for each of the creation mutations. The query to refetch would be `GET_JOURNAL_ENTRIES`.

**Example:**
```javascript
const [createEntry] = useMutation(CREATE_GRATITUDE_JOURNAL_ENTRY, {
  refetchQueries: [{ query: GET_JOURNAL_ENTRIES }],
  // ... onCompleted, onError, etc.
});
```

## 2. Middleware Authentication Non-Functional

**Description:**
The middleware.ts file exists in the web directory but is currently non-functional. The middleware is supposed to handle authentication checks and admin route protection, but it's not being executed properly.

**Location:**
`/web/middleware.ts` - Currently contains Supabase authentication logic but is not active.

**Expected Behavior:**
- Protect `/admin` routes by redirecting unauthenticated users to `/admin/login`
- Handle Supabase cookie management for SSR authentication
- Validate user sessions on protected routes

**Current Status:**
The middleware file exists with the correct logic but is not being triggered by Next.js. This is likely due to incorrect file placement or configuration.

**Potential Solution:**
- Verify middleware.ts is in the correct location (root of web directory)
- Check that the config.matcher is properly configured
- Ensure Next.js is recognizing the middleware file

**Impact:**
Low priority - admin routes are not currently in use, and client-side auth is working correctly. 