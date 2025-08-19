import React, { createContext, useContext, useEffect, useState } from 'react'
import { Session, User } from '@supabase/supabase-js'
import { supabase } from '@/services/supabase/client'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

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
        if (event === 'SIGNED_IN') {
          console.log('✅ User signed in:', session?.user?.email)
        } else if (event === 'SIGNED_OUT') {
          console.log('❌ User signed out')
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
  }

  const value = {
    user,
    session,
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