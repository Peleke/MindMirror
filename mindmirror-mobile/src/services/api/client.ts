import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { onError } from '@apollo/client/link/error'
import Constants from 'expo-constants'

const GATEWAY_URL = Constants.expoConfig?.extra?.gatewayUrl || 'http://localhost:4000/graphql'

const httpLink = createHttpLink({
  uri: GATEWAY_URL,
})

const authLink = setContext((_, { headers, session }) => {
  const currentSession = session

  if (!currentSession?.access_token) {
    return { headers }
  }

  return {
    headers: {
      ...headers,
      'Authorization': `Bearer ${currentSession.access_token}`,
      'x-internal-id': currentSession.user?.id || '',
      'Content-Type': 'application/json',
    }
  }
})

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    })
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`)
  }
})

export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          journalEntries: {
            merge(existing = [], incoming) {
              return incoming
            }
          },
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