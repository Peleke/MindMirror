# React Native GraphQL Wiring Plan

## Overview
This document outlines the steps to wire up GraphQL queries and mutations from the web app to the React Native mobile app, restoring full functionality.

## Current State

### ✅ Already Implemented:
1. **Apollo Client Setup** - Complete with authentication, error handling, and environment configuration
2. **Query Library** - All queries from web app are duplicated in `mindmirror-mobile/src/services/api/queries.ts`
3. **Mutation Library** - All mutations from web app are duplicated in `mindmirror-mobile/src/services/api/mutations.ts`
4. **Basic Chat Integration** - `chat.tsx` already imports and uses `LIST_TRADITIONS` query

### 🔧 Integration Points Needed:

#### **1. Journal Entry Creation (High Priority)**
- **Files to update:**
  - `mindmirror-mobile/app/(app)/journal/gratitude.tsx` - Wire up `CREATE_GRATITUDE_JOURNAL_ENTRY` mutation
  - `mindmirror-mobile/app/(app)/journal/reflection.tsx` - Wire up `CREATE_REFLECTION_JOURNAL_ENTRY` mutation  
  - `mindmirror-mobile/app/(app)/journal/freeform.tsx` - Wire up `CREATE_FREEFORM_JOURNAL_ENTRY` mutation

- **Current state:** All three screens have mock implementations with TODO comments
- **Web pattern:** Uses `useMutation` with proper error handling and loading states
- **Success handling:** Show success message and navigate back to home

#### **2. Journal Entry Display (High Priority)**
- **File to update:** `mindmirror-mobile/app/(app)/archive.tsx`
- **Current state:** Uses mock data array
- **Web pattern:** Uses `useQuery(GET_JOURNAL_ENTRIES)` with proper loading/error states
- **Needs:** Replace mock entries with real GraphQL data

#### **3. Chat Functionality (Medium Priority)**
- **File to update:** `mindmirror-mobile/app/(app)/chat.tsx`
- **Current state:** Has `LIST_TRADITIONS` query but chat is mocked
- **Web pattern:** Uses `useLazyQuery(ASK_QUERY)` for on-demand chat requests
- **Needs:** Replace mock AI responses with real `ASK_QUERY` calls

#### **4. Insights Generation (Medium Priority)**
- **File to update:** `mindmirror-mobile/app/(app)/insights.tsx`
- **Current state:** Both summarize and review features are mocked
- **Web patterns:** 
  - Uses `useQuery(SUMMARIZE_JOURNALS_QUERY)` for journal summaries
  - Uses `useMutation(GENERATE_REVIEW)` for performance reviews
- **Needs:** Replace mock API calls with real GraphQL operations

#### **5. Entry Existence Checks (Low Priority)**
- **Files to update:** All journal entry screens
- **Web pattern:** Uses `useQuery(JOURNAL_ENTRY_EXISTS_TODAY)` to check if user already wrote today
- **Needs:** Add existence checks before allowing new entries

#### **6. Meal Suggestions (Low Priority)**
- **File to update:** Not currently implemented in mobile
- **Web pattern:** Uses `useQuery(GET_MEAL_SUGGESTION)` 
- **Needs:** New feature implementation

#### **7. Document Upload (Low Priority)**
- **File to update:** Not currently implemented in mobile
- **Web pattern:** Uses `useMutation(UPLOAD_DOCUMENT)`
- **Needs:** New feature implementation

## Implementation Order:
1. **Journal Entry Creation** (gratitude, reflection, freeform) - Core functionality
2. **Journal Entry Display** (archive) - Core functionality  
3. **Chat Functionality** - High user value
4. **Insights Generation** - Nice-to-have features
5. **Entry Existence Checks** - UX improvement
6. **Additional Features** - Future enhancements

## Key Considerations:
- **Error Handling:** Mobile needs more robust error handling with user-friendly alerts
- **Loading States:** Already implemented in UI, just need to wire up to real operations
- **Authentication:** Apollo client already configured with Supabase session
- **Environment:** Gateway URL is configurable via environment variables
- **Offline Support:** Consider caching strategies for better mobile experience
- **Success Indicators:** Show success messages and navigate users appropriately after operations

## Web App Patterns to Follow:
- Use `useMutation` for create operations with proper error handling
- Use `useQuery` for read operations with loading states
- Use `useLazyQuery` for on-demand operations (like chat)
- Implement proper form validation before submission
- Show loading states during operations
- Display success messages and navigate users appropriately
- Handle GraphQL errors gracefully with user-friendly messages

## Files Structure:
```
mindmirror-mobile/src/services/api/
├── client.ts              # Apollo client configuration
├── apollo-provider.tsx    # Apollo provider wrapper
├── queries.ts            # All GraphQL queries
└── mutations.ts          # All GraphQL mutations
```

The foundation is solid - all the GraphQL operations are defined and the Apollo client is properly configured. The main work is replacing the mock implementations with real GraphQL calls following the patterns established in the web app. 