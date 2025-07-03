import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'
import { AuthProvider } from '@/features/auth/context/AuthContext'
import { ApolloProviderWrapper } from '@/services/api/apollo-provider'

export default function RootLayout() {
  return (
    <AuthProvider>
      <ApolloProviderWrapper>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(auth)" options={{ headerShown: false }} />
          <Stack.Screen name="(app)" options={{ headerShown: false }} />
        </Stack>
      </ApolloProviderWrapper>
    </AuthProvider>
  )
}
