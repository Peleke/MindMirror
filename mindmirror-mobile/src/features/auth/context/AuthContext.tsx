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
  const [autoEnrollState, setAutoEnrollState] = useState<'idle'|'success'|'mismatch'|'none'>('idle')

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
          // One-time autoenroll per session
          try {
            const resp = await fetch(`${process.env.EXPO_PUBLIC_WEB_BASE_URL || ''}/api/vouchers/autoenroll`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
            })
            const j = await resp.json().catch(() => ({}))
            if (j?.enrolled) {
              console.log('🎟️ Auto-enrolled via voucher')
              setAutoEnrollState('success')
            } else if (j?.reason === 'email_mismatch') {
              console.log('⚠️ Voucher email mismatch; show voucher entry modal')
              setAutoEnrollState('mismatch')
            } else {
              setAutoEnrollState('none')
            }
          } catch (e) {
            console.log('autoenroll error', e)
          }
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
      {autoEnrollState === 'success' && (
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, padding: 16 }}>
          <div style={{ backgroundColor: '#10b981', padding: 12, borderRadius: 8 }}>
            <span style={{ color: 'white' }}>You’re in! Your voucher has been applied.</span>
            <button onClick={() => setAutoEnrollState('idle')} style={{ marginLeft: 12, color: 'white', textDecorationLine: 'underline' }}>Dismiss</button>
          </div>
        </div>
      )}
      {autoEnrollState === 'mismatch' && (
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, padding: 16 }}>
          <div style={{ backgroundColor: '#f59e0b', padding: 12, borderRadius: 8 }}>
            <span style={{ color: 'white' }}>We couldn’t auto-apply your voucher. Enter your code here or use Marketplace → Redeem Voucher.</span>
            <button onClick={() => setAutoEnrollState('idle')} style={{ marginLeft: 12, color: 'white', textDecorationLine: 'underline' }}>Dismiss</button>
          </div>
        </div>
      )}
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