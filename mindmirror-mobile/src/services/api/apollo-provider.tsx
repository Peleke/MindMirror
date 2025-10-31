import React, { useMemo, useEffect } from 'react'
import { ApolloProvider } from '@apollo/client'
import { createApolloClientWithSession, apolloClient } from './client'
import { useAuth } from '@/features/auth/context/AuthContext'

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

// Simple Apollo provider that doesn't depend on auth context
// This allows AuthProvider to use Apollo hooks without circular dependency
export function SimpleApolloProvider({ children }: ApolloProviderWrapperProps) {
  return (
    <ApolloProvider client={apolloClient}>
      {children}
    </ApolloProvider>
  )
} 