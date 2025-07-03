import { useAuthState } from '@/features/auth/hooks/useAuthState'

export function AuthStateHandler() {
  // This component doesn't render anything, it just uses the hook
  // to handle navigation based on auth state
  useAuthState()
  
  return null
} 