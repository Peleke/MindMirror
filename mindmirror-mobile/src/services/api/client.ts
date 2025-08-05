import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { onError } from '@apollo/client/link/error'
import { Session } from '@supabase/supabase-js'
import Constants from 'expo-constants'

// Environment detection
const isDevelopment = __DEV__

// More robust gateway URL loading
const GATEWAY_BASE_URL = process.env.EXPO_PUBLIC_GATEWAY_URL || Constants.expoConfig?.extra?.gatewayUrl

if (!GATEWAY_BASE_URL) {
  console.error("CRITICAL: Gateway URL is not configured. Check .env or app.json.")
}

// Ensure the final URI includes the /graphql path
const finalGatewayUrl = GATEWAY_BASE_URL 
  ? `${GATEWAY_BASE_URL.replace(/\/$/, '')}/graphql` 
  : 'http://localhost:4000/graphql'; // Fallback for local dev if nothing is set

// HTTP Link for GraphQL endpoint
const httpLink = createHttpLink({
  uri: finalGatewayUrl,
})

// Auth link to add JWT token and user ID headers
const authLink = setContext((_, { headers, session }) => {
  // Get session from context or use provided session
  const currentSession = session as Session | null

  if (!currentSession?.access_token) {
    console.warn('Apollo Client: No session or access token available')
    return { headers }
  }

  return {
    headers: {
      ...headers,
      // JWT token for authentication
      'Authorization': `Bearer ${currentSession.access_token}`,
      // Supabase user ID for internal routing
      'x-internal-id': currentSession.user?.id || '',
      // Content type for GraphQL
      'Content-Type': 'application/json',
    }
  }
})

// Error link for handling authentication and network errors
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    })
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`)
    
    // Handle authentication errors
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      console.error('Authentication failed - redirecting to login')
      // In a real app, you might want to trigger a re-authentication flow
      // For mobile, we'll handle this in the navigation
    }
  }
})

// Create Apollo Client instance
export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          // Cache policy for journal entries
          journalEntries: {
            merge(existing = [], incoming) {
              return incoming
            }
          },
          // Cache policy for traditions
          listTraditions: {
            merge(existing = [], incoming) {
              return incoming
            }
          }
        }
      }
    }
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all'
    },
    query: {
      errorPolicy: 'all'
    }
  }
})

// Helper function to create client with session context
export function createApolloClientWithSession(session: Session | null) {
  return new ApolloClient({
    link: from([
      errorLink, 
      setContext((_, { headers }) => ({
        headers: {
          ...headers,
          'Authorization': session?.access_token ? `Bearer ${session.access_token}` : '',
          'x-internal-id': session?.user?.id || '',
          'Content-Type': 'application/json',
        }
      })),
      httpLink
    ]),
    cache: apolloClient.cache,
    defaultOptions: apolloClient.defaultOptions
  })
}

// Environment info for debugging
export const apolloConfig = {
  gatewayUrl: GATEWAY_BASE_URL,
  isDevelopment,
  environment: isDevelopment ? 'development' : 'production'
} 