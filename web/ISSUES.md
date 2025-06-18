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