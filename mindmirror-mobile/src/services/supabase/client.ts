import { createClient } from '@supabase/supabase-js'
import Constants from 'expo-constants'

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || Constants.expoConfig?.extra?.supabaseUrl
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || Constants.expoConfig?.extra?.supabaseAnonKey

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase configuration. Please check your environment variables.')
}

// Web-safe storage - only use AsyncStorage if available (React Native), fallback to no storage for web builds
const getStorage = () => {
  try {
    // Check if we're in React Native environment
    if (typeof window === 'undefined' && typeof global !== 'undefined') {
      // During build time - return undefined to use default web storage
      return undefined
    }
    
    // Runtime - try to import AsyncStorage for React Native
    const AsyncStorage = require('@react-native-async-storage/async-storage').default
    return AsyncStorage
  } catch {
    // Fallback for web or when AsyncStorage is not available
    return undefined
  }
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: getStorage(),
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
})

// Auth helper functions matching web implementation
export const auth = {
  signUp: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { data, error }
  },

  signIn: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    return { data, error }
  },

  signOut: async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  resetPassword: async (email: string) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email)
    return { data, error }
  },

  getSession: async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    return { session, error }
  },

  getUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  }
} 