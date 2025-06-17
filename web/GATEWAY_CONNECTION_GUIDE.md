# Gateway Connection Guide

## 🚀 Current Status

**Phase 2.1 COMPLETE!** ✅

Your MindMirror web app is now fully configured with:
- ✅ Apollo Client setup with JWT authentication
- ✅ GraphQL queries and mutations ready
- ✅ Dashboard with responsive navigation
- ✅ Tradition context management
- ✅ Environment detection (Docker vs Local)
- ✅ Connection testing component

## 🔌 Next Steps: Connect to Gateway

### 1. Start Your Gateway
Make sure your Hive Gateway is running on port 4000:
```bash
# In your gateway directory
npm run dev
# or
yarn dev
```

### 2. Test the Connection
1. Navigate to `/dashboard` in your web app
2. Scroll down to "Gateway Connection Test" 
3. Click "Test Gateway Connection"
4. Check the results!

### 3. Expected Connection Flow

**Success Case:**
- ✅ Connection successful
- ✅ Loads traditions from Gateway
- ✅ JWT token passed correctly
- ✅ User ID header set

**Failure Cases:**
- ❌ Network Error: Gateway not running
- ❌ GraphQL Error: Schema mismatch
- ❌ Auth Error: JWT validation failed

## 🛠 Troubleshooting

### Gateway Not Running
```
Network Error: fetch failed
```
**Solution:** Start your Gateway on port 4000

### Schema Mismatch
```
GraphQL Error: Cannot query field "listTraditions"
```
**Solution:** Make sure your Gateway schema includes the `listTraditions` query

### Authentication Issues
```
GraphQL Error: Unauthorized
```
**Solution:** Check that Gateway accepts JWT tokens in Authorization header

### Docker Environment
If running in Docker, the web app will try to connect to:
```
http://hive-gateway:4000/graphql
```
Make sure your Gateway container is named `hive-gateway`

### Local Development
In local development, connects to:
```
http://localhost:4000/graphql
```

## 📋 Required Gateway Schema

Your Gateway should support these queries/mutations:

### Queries
```graphql
type Query {
  listTraditions: [String!]!
  journalEntryExistsToday(entryType: String!): Boolean!
  journalEntries(limit: Int, offset: Int): [JournalEntry!]!
  ask(query: String!, tradition: String!): AskResponse!
  getMealSuggestion(mealType: String!, tradition: String!): MealSuggestion!
}
```

### Mutations
```graphql
type Mutation {
  createGratitudeJournalEntry(input: GratitudeEntryInput!): JournalEntry!
  createReflectionJournalEntry(input: ReflectionEntryInput!): JournalEntry!
  createFreeformJournalEntry(input: FreeformEntryInput!): JournalEntry!
  uploadDocument(fileName: String!, content: String!, tradition: String!): UploadResponse!
  generateReview(tradition: String!): ReviewResponse!
}
```

## 🔧 Environment Variables

The web app automatically detects environment:
- `NODE_ENV=production` OR `DOCKER_ENV=true` → Uses Docker Gateway URL
- Otherwise → Uses localhost Gateway URL

## 🎯 What's Ready

Once Gateway is connected, these features work immediately:
1. **Tradition Selection** - Dropdown in header
2. **Connection Testing** - Real-time Gateway health check
3. **Authentication** - JWT tokens automatically sent
4. **Navigation** - All dashboard pages ready
5. **Error Handling** - Graceful failure states

## 🚧 Coming Next (Phase 2.2)

After Gateway connection is verified:
1. **Gratitude Form** - Morning gratitude entry
2. **Chat Interface** - Real-time AI conversation  
3. **Journal History** - View past entries
4. **Document Upload** - PDF/text file processing
5. **Meal Suggestions** - AI-powered recommendations

## 🆘 Need Help?

If you run into issues:
1. Check the browser console for errors
2. Use the Connection Test component
3. Verify Gateway is responding to GraphQL queries
4. Check that JWT authentication is working

**The web app is 100% ready - just waiting for your Gateway!** 🎉 