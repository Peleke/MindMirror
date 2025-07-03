import { useEffect } from 'react'
import { useRouter, useSegments } from 'expo-router'
import { useAuth } from '@/features/auth/context/AuthContext'

export function useAuthState() {
  const { user, loading } = useAuth()
  const segments = useSegments()
  const router = useRouter()

  useEffect(() => {
    console.log("=== AUTH STATE CHANGE ===")
    console.log("User:", user ? `Yes (${user.email})` : 'No')
    console.log("Loading:", loading)
    console.log("Segments:", segments)
    console.log("Current route:", segments.join('/'))
    
    if (loading) {
      console.log("Still loading, skipping navigation")
      return;
    }

    const inAuthGroup = segments[0] === '(auth)'
    const inAppGroup = segments[0] === '(app)'
    const atRoot = !inAuthGroup && !inAppGroup

    console.log("Route analysis:", { inAuthGroup, inAppGroup, atRoot, user: !!user })

    if (!user && !inAuthGroup) {
      console.log('🚀 Redirecting to login')
      router.replace('/(auth)/login')
    } else if (user && (inAuthGroup || atRoot)) {
      console.log('🚀 Redirecting to journal')
      router.replace('/(app)/journal')
    } else {
      console.log('✅ No redirect needed - staying on current route')
    }
    console.log("=== END AUTH STATE CHANGE ===")
  }, [user, loading, segments, router])

  return { user, loading }
} 