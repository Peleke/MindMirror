import React, { createContext, useContext, useEffect, useState } from 'react'
import { Session, User } from '@supabase/supabase-js'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { supabase } from '@/services/supabase/client'
import { apolloClient } from '@/services/api/client'
import { EXCHANGE_SUPABASE_ID_FOR_INTERNAL_ID } from '@/services/api/users'

interface AuthContextType {
  user: User | null
  session: Session | null
  internalUserId: string | null
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)
const INTERNAL_USER_ID_KEY = '@mindmirror_internal_user_id'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [internalUserId, setInternalUserId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Exchange Supabase ID for internal UUID
  const exchangeUserIds = async (supabaseId: string) => {
    try {
      console.log('🔄 Exchanging Supabase ID for internal UUID...')
      const { data, errors } = await apolloClient.query({
        query: EXCHANGE_SUPABASE_ID_FOR_INTERNAL_ID,
        variables: { supabaseId },
        fetchPolicy: 'network-only', // Always fetch fresh
      })

      if (errors || !data?.exchangeSupabaseIdForInternalId) {
        console.error('❌ Exchange failed:', errors)
        return null
      }

      const internalId = data.exchangeSupabaseIdForInternalId
      console.log('✅ Exchanged successfully, internal UUID:', internalId)

      // Cache in AsyncStorage
      await AsyncStorage.setItem(INTERNAL_USER_ID_KEY, internalId)
      setInternalUserId(internalId)

      return internalId
    } catch (error) {
      console.error('❌ Error exchanging user IDs:', error)
      return null
    }
  }

  useEffect(() => {
    console.log('AuthProvider: Initializing auth state')

    // Get initial session
    const getInitialSession = async () => {
      console.log('AuthProvider: Getting initial session')
      const { data: { session }, error } = await supabase.auth.getSession()
      if (error) {
        console.error('Error getting session:', error)
      } else {
        console.log('AuthProvider: Initial session:', session ? 'exists' : 'none')
        setSession(session)
        setUser(session?.user ?? null)

        // Try to load cached internal ID or exchange
        if (session?.user?.id) {
          const cachedId = await AsyncStorage.getItem(INTERNAL_USER_ID_KEY)
          if (cachedId) {
            console.log('📦 Loaded cached internal UUID')
            setInternalUserId(cachedId)
          } else {
            console.log('🔄 No cached UUID, exchanging...')
            await exchangeUserIds(session.user.id)
          }
        }
      }
      setLoading(false)
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('=== AUTH PROVIDER STATE CHANGE ===')
        console.log('Event:', event)
        console.log('Session:', session ? 'exists' : 'none')
        console.log('User:', session?.user?.email || 'none')

        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)

        // Handle different auth events
        if (event === 'SIGNED_IN' && session?.user?.id) {
          console.log('✅ User signed in:', session?.user?.email)
          // Exchange Supabase ID for internal UUID
          await exchangeUserIds(session.user.id)
        } else if (event === 'SIGNED_OUT') {
          console.log('❌ User signed out')
          // Clear cached internal UUID
          await AsyncStorage.removeItem(INTERNAL_USER_ID_KEY)
          setInternalUserId(null)
        } else if (event === 'TOKEN_REFRESHED') {
          console.log('🔄 Token refreshed')
        } else if (event === 'USER_UPDATED') {
          console.log('👤 User updated')
        }
        console.log('=== END AUTH PROVIDER STATE CHANGE ===')
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Error signing out:', error)
    }
    // Clear internal UUID on sign out
    await AsyncStorage.removeItem(INTERNAL_USER_ID_KEY)
    setInternalUserId(null)
  }

  const value = {
    user,
    session,
    internalUserId,
    loading,
    signOut
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 