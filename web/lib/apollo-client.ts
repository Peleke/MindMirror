import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { onError } from '@apollo/client/link/error'
import { Session } from '@supabase/supabase-js'

// Environment detection - check for Docker environment
const isDocker = process.env.NODE_ENV === 'production' || process.env.DOCKER_ENV === 'true'

// Gateway URL based on environment
const GATEWAY_URL = isDocker 
  ? 'http://localhost:4000/graphql' // Docker internal network
  : 'http://localhost:4000/graphql'    // Local development

// HTTP Link for GraphQL endpoint
const httpLink = createHttpLink({
  uri: GATEWAY_URL,
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
      window.location.href = '/login'
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
  gatewayUrl: GATEWAY_URL,
  isDocker,
  environment: process.env.NODE_ENV || 'development'
} 