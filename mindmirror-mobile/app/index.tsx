import { Redirect } from 'expo-router'

export default function Index() {
  // For now, redirect to auth. Later we'll add authentication logic
  return <Redirect href="/(auth)/login" />
} 