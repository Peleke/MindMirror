import { useEffect } from 'react'
import { useRouter, useSegments } from 'expo-router'
import { useAuth } from '@/features/auth/context/AuthContext'

export function useAuthState() {
  const { user, loading } = useAuth()
  const segments = useSegments()
  const router = useRouter()

  useEffect(() => {
    console.log("Auth state changed:", { user: !!user, loading, segments })
    
    if (loading) return;

    const inAuthGroup = segments[0] === '(auth)'
    const inAppGroup = segments[0] === '(app)'
    const atRoot = !inAuthGroup && !inAppGroup

    console.log("Navigation logic:", { inAuthGroup, inAppGroup, atRoot, user: !!user })

    if (!user && !inAuthGroup) {
      console.log('Redirecting to login')
      router.replace('/(auth)/login')
    } else if (user && (inAuthGroup || atRoot)) {
      console.log('Redirecting to dashboard')
      router.replace('/(app)/dashboard')
    } else {
      console.log('No redirect needed')
    }
  }, [user, loading, segments, router])

  return { user, loading }
} 