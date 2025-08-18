import React, { useMemo } from 'react'
import { ApolloProvider } from '@apollo/client'
import { createApolloClientWithSession } from './client'
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