import { Stack } from 'expo-router'
import { ApolloProvider } from '@apollo/client'
import { apolloClient } from '@/services/api/client'
import { StatusBar } from 'expo-status-bar'

export default function RootLayout() {
  return (
    <ApolloProvider client={apolloClient}>
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(app)" options={{ headerShown: false }} />
      </Stack>
    </ApolloProvider>
  )
}
