import { ApolloClient, InMemoryCache, createHttpLink, from, ApolloLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { onError } from '@apollo/client/link/error'
import { Session } from '@supabase/supabase-js'
import Constants from 'expo-constants'
import { createMockLink } from './mockLink'

// Environment detection
const isDevelopment = __DEV__

// More robust gateway URL loading
const RAW_GATEWAY_URL = process.env.EXPO_PUBLIC_GATEWAY_URL || Constants.expoConfig?.extra?.gatewayUrl

if (!RAW_GATEWAY_URL) {
  console.error("CRITICAL: Gateway URL is not configured. Check .env or app.json.")
}

// Normalize to ensure exactly one /graphql suffix, without duplicating it
const normalizeGatewayUrl = (url?: string | null) => {
  if (!url) return null
  const trimmed = url.replace(/\/+$/, '')
  return trimmed.endsWith('/graphql') ? trimmed : `${trimmed}/graphql`
}

const finalGatewayUrl = normalizeGatewayUrl(RAW_GATEWAY_URL) || 'http://localhost:4000/graphql'

// HTTP Link for GraphQL endpoint
const httpLink = createHttpLink({ uri: finalGatewayUrl })

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
  const mockEnabled = (process.env.EXPO_PUBLIC_MOCK_TASKS || '').toLowerCase() === 'true'

  const headerLink = setContext((_, { headers }) => {
    const nextHeaders: Record<string, string> = {
      ...(headers as Record<string, string>),
      'Content-Type': 'application/json',
    }
    if (session?.access_token) {
      nextHeaders['Authorization'] = `Bearer ${session.access_token}`
    }
    if (session?.user?.id) {
      nextHeaders['x-internal-id'] = session.user.id
    }
    return { headers: nextHeaders }
  })

  const linkChain: ApolloLink[] = [errorLink, headerLink]
  if (mockEnabled) {
    linkChain.push(createMockLink())
  }
  linkChain.push(httpLink)

  return new ApolloClient({
    link: from(linkChain),
    cache: apolloClient.cache,
    defaultOptions: apolloClient.defaultOptions,
  })
}

// Environment info for debugging
export const apolloConfig = {
  gatewayUrl: finalGatewayUrl,
  isDevelopment,
  environment: isDevelopment ? 'development' : 'production'
} 