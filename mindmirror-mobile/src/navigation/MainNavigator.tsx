import React from 'react'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { DashboardScreen } from '@/features/dashboard/components/DashboardScreen'
import { JournalScreen } from '@/features/journal/components/JournalScreen'
import { ChatScreen } from '@/features/chat/components/ChatScreen'
import { ProfileScreen } from '@/features/profile/components/ProfileScreen'

export type MainTabParamList = {
  Dashboard: undefined
  Journal: undefined
  Chat: undefined
  Profile: undefined
}

const Tab = createBottomTabNavigator<MainTabParamList>()

export const MainNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#6366f1',
        tabBarInactiveTintColor: '#6b7280',
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
        }}
      />
      <Tab.Screen 
        name="Journal" 
        component={JournalScreen}
        options={{
          tabBarLabel: 'Journal',
        }}
      />
      <Tab.Screen 
        name="Chat" 
        component={ChatScreen}
        options={{
          tabBarLabel: 'Chat',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
        }}
      />
    </Tab.Navigator>
  )
} 