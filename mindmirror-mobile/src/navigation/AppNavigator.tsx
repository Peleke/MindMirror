import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'
import { LoadingScreen } from '@/components/common/Loading'
import { AuthNavigator } from './AuthNavigator'
import { MainNavigator } from './MainNavigator'
import { useAuth } from '@/features/auth/hooks/useAuth'

const Stack = createStackNavigator()

export const AppNavigator: React.FC = () => {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen text="Loading..." />
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  )
} 