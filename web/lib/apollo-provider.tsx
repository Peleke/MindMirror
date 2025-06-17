'use client'

import { ApolloProvider } from '@apollo/client'
import { createApolloClientWithSession } from './apollo-client'
import { useAuth } from './auth-context'
import { useMemo } from 'react'

interface ApolloProviderWrapperProps {
  children: React.ReactNode
}

export function ApolloProviderWrapper({ children }: ApolloProviderWrapperProps) {
  const { session } = useAuth()
  
  // Create Apollo client with current session
  const client = useMemo(() => {
    return createApolloClientWithSession(session)
  }, [session])

  return (
    <ApolloProvider client={client}>
      {children}
    </ApolloProvider>
  )
} 