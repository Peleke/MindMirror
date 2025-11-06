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
    // Landing page can be: [] (root), ['index'], or no segments at initial load
    const onLandingPage = segments.length === 0 || segments[0] === 'index'

    console.log("Route analysis:", { inAuthGroup, inAppGroup, onLandingPage, segments: segments.join('/') || '(root)', user: !!user })

    // Redirect logic:
    // 1. Unauthenticated users can view landing page and auth routes only
    // 2. Authenticated users should be in the app
    if (!user) {
      // User not logged in - allow landing page, don't redirect from root/index
      if (inAppGroup) {
        console.log('🚀 Redirecting to login (unauthenticated trying to access app)')
        router.replace('/(auth)/login')
      } else if (onLandingPage || inAuthGroup) {
        console.log('✅ Staying on public page (landing or auth)')
      }
    } else {
      // User is logged in - only redirect from landing if they're authenticated
      // This allows unauthenticated users to stay on landing/index
      if (inAuthGroup) {
        console.log('🚀 Redirecting to journal (authenticated on auth page)')
        router.replace('/(app)/journal')
      } else if (onLandingPage) {
        // Only redirect authenticated users away from landing
        console.log('🚀 Redirecting to journal (authenticated on landing)')
        router.replace('/(app)/journal')
      } else {
        console.log('✅ Staying in app (already authenticated)')
      }
    }
    console.log("=== END AUTH STATE CHANGE ===")
  }, [user, loading, segments, router])

  return { user, loading }
} 